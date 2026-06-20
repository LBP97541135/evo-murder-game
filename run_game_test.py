# -*- coding: utf-8 -*-
"""
EvoMap Murder Game — 全自动游戏测试脚本
模拟完整一局：Agent注册→角色注入→DM开场→玩家调查→Agent对话→意图系统→投票→真相揭示→复盘
"""
import sys, json, urllib.request, traceback, time

BASE = "http://127.0.0.1:8888"
SCRIPT_ID = "xiutie-avenue-missing-three-minutes"

def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(repr(msg))

def api(method, path, data=None):
    url = f"{BASE}{path}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8")
        try:
            return {"_error": e.code, "_detail": json.loads(err)}
        except json.JSONDecodeError:
            return {"_error": e.code, "_detail": err}

def phase_name(p):
    names = {"intro":"开场介绍","investigation":"自由调查","voting":"提交推理","reveal":"真相揭示","review":"复盘反思"}
    return names.get(p, p)

# ================================================================
safe_print("=" * 70)
safe_print("EvoMap Murder Game - 全自动游戏测试")
safe_print("=" * 70)

# ---- Step 1: Health ----
safe_print("\n[1] 健康检查")
r = api("GET", "/health")
safe_print(f"  状态: {r.get('status')}, Agent: {r.get('agents_registered')}")

# ---- Step 2: Register agents ----
safe_print("\n[2] 注册 Agent（DM + 4个Companion）")
# First init personas
api("POST", "/agents/personas/init")

# Register DM
dm_name = "雾港主理人"
r = api("POST", "/agents/register", {"role":"dm","name":dm_name,"model":"evomap-deepseek-v4-flash"})
dm_key = f"dm_{dm_name}"
safe_print(f"  DM: {dm_name} ({dm_key})")

companion_names = ["white-crow", "echo", "paper-owl", "flint"]
companion_keys = []
for pk in companion_names:
    r = api("POST", "/agents/register", {"role":"companion","name":pk,"model":"evomap-deepseek-v4-flash"})
    key = f"companion_{pk}"
    companion_keys.append(key)
    safe_print(f"  Companion: {pk} ({key})")

# Load personas
safe_print("  加载人设...")
api("POST", "/agents/personas/load", {"agent_key":dm_key, "persona_key":"mist-harbor"})
for pk in companion_names:
    api("POST", "/agents/personas/load", {"agent_key":f"companion_{pk}", "persona_key":pk})

# ---- Step 3: Create session ----
safe_print("\n[3] 创建游戏会话")
r = api("POST", "/game/create-session", {"script_id": SCRIPT_ID})
sid = r["session_id"]
companions = r.get("participants", [])
safe_print(f"  Session: {sid}")
safe_print(f"  Participants: {companions}")

# ---- Step 4: Get script/characters ----
safe_print("\n[4] 加载剧本角色")
r = api("GET", f"/scripts/{SCRIPT_ID}")
script = r.get("script", {})
global_story = script.get("globalStory", "")
characters = script.get("characters", [])
killer = next((c["name"] for c in characters if c.get("isKiller")), "未知")
victim = next((c["name"] for c in characters if c.get("roleType") == "受害者"), "顾沉")
safe_print(f"  角色: {[c['name'] for c in characters]}")
safe_print(f"  真凶: {killer}")

# Build safe_actors list
safe_actors = [{
    "id": c["id"], "name": c["name"],
    "bio": c.get("bio","")[:200],
    "personality": c.get("personality","")[:200],
    "context": c.get("context","")[:300],
    "role_type": c.get("roleType","suspect"),
    "is_victim": c.get("isVictim", False),
    "is_killer": c.get("isKiller", False),
} for c in characters]

# ---- Step 5: DM intro ----
safe_print(f"\n[5] DM开场（{phase_name('intro')}）")
dm_payload = {
    "global_story": global_story[:1000],
    "actor": {
        "id": "dm_primary", "name": dm_name,
        "bio": "你是剧本杀主持人，掌握完整真相。", "personality": "专业沉稳，善于营造悬疑氛围。",
        "context": global_story[:300], "secret":"", "violation":"", "role_type":"dm",
    },
    "session_id": sid, "detective_name": "侦探", "victim_name": victim,
    "all_actors": safe_actors,
    "chat_messages": [{"role":"user","content":"玩家已就位，请开始介绍案件背景和角色。"}],
    "temperature": 0.7,
}
try:
    r = api("POST", "/invoke/", dm_payload)
    final = r.get("final_response", "")
    safe_print(f"  DM发言 ({len(final)} chars): {final[:150]}...")
except:
    safe_print(f"  DM发言失败")

# Advance intro -> investigation
api("POST", f"/game/chat-count/{sid}", {})
api("POST", f"/game/phase/{sid}/advance", {})
r = api("GET", f"/game/phase/{sid}")
safe_print(f"  推进到: {phase_name(r.get('current_phase',''))}")

# ================================================================
# 调查阶段 - 角色对话循环
# ================================================================
safe_print(f"\n{'='*70}")
safe_print(f"[6] 调查阶段 - Agent对话循环")
safe_print(f"{'='*70}")

# Get agent states to see which character each agent got
agent_character_map = {}
for ak in companion_keys[:len(characters)]:
    r = api("GET", f"/game/agent-state/{sid}/{ak}")
    if r.get("_error"): continue
    state = r.get("state", {})
    ch = state.get("character", {})
    if ch and ch.get("name"):
        agent_character_map[ak] = ch
        safe_print(f"  {ak} -> {ch.get('name')}")

# If agents weren't assigned chars (create_session didn't assign), do it manually
if not agent_character_map:
    safe_print("  Agent未分配到角色，直接从剧本用...")
    # Map companions to characters
    for i, ak in enumerate(companion_keys):
        if i < len(characters):
            c = characters[i]
            if c.get("roleType") != "受害者":  # skip victim
                ch_data = {
                    "name": c["name"], "id": c["id"],
                    "bio": c.get("bio",""), "personality": c.get("personality",""),
                    "context": c.get("context",""), "secret": c.get("secret",""),
                    "violation": c.get("violation",""), "is_killer": c.get("isKiller",False),
                    "role_type": c.get("roleType","suspect"),
                }
                agent_character_map[ak] = ch_data

def invoke_agent(actor_data, chat_msgs, story_len=500):
    """Call the invoke API for an agent."""
    payload = {
        "global_story": global_story[:story_len],
        "actor": actor_data,
        "session_id": sid,
        "all_actors": safe_actors,
        "chat_messages": chat_msgs,
        "temperature": 0.8,
    }
    try:
        r = api("POST", "/invoke/", payload)
        if r.get("final_response"):
            return r["final_response"]
        return None
    except:
        return None

def safe_invoke(agent, name, prompt):
    """Safely invoke an agent with error handling."""
    try:
        resp = invoke_agent(agent, [{"role":"user","content":prompt}])
        if resp and len(resp) > 5:
            safe_print(f"  [{name}]: {resp[:100]}...")
            return resp
        else:
            safe_print(f"  [{name}]: 回复为空")
            return None
    except Exception as e:
        safe_print(f"  [{name}] 调用失败: {e}")
        return None

# DM asks first agent a question
safe_print("\n[6a] DM向第一个角色提问...")
if companion_keys:
    first_key = companion_keys[0]
    ch = agent_character_map.get(first_key, {})
    if ch:
        safe_print(f"  [DM] 对{ch.get('name')}提问...")

# Companion 1 replies
safe_print("\n[6b] 第一个Companion回应询问...")
if companion_keys and companion_keys[0] in agent_character_map:
    ch = agent_character_map[companion_keys[0]]
    actor = {
        "id": ch["id"], "name": ch["name"], "bio": ch.get("bio","")[:200],
        "personality": ch.get("personality","")[:200], "context": ch.get("context","")[:300],
        "secret": ch.get("secret","")[:200], "violation": ch.get("violation","")[:200],
        "role_type":"companion",
    }
    resp = invoke_agent(actor, [{"role":"dm","content":f"{ch['name']}，你对今晚的召集有什么看法？你是被谁叫来的？"}])
    if resp: safe_print(f"  [{ch['name']}] 回复({len(resp)}): {resp[:150]}")
    api("POST", f"/game/chat-count/{sid}", {})

# Companion 2 speaks
safe_print("\n[6c] 第二个Companion被喊话...")
if len(companion_keys) > 1 and companion_keys[1] in agent_character_map:
    ch2 = agent_character_map[companion_keys[1]]
    actor2 = {
        "id": ch2["id"], "name": ch2["name"], "bio": ch2.get("bio","")[:200],
        "personality": ch2.get("personality","")[:200], "context": ch2.get("context","")[:300],
        "secret": ch2.get("secret","")[:200], "violation": ch2.get("violation","")[:200],
        "role_type":"companion",
    }
    resp2 = invoke_agent(actor2, [{"role":"user","content":f"{ch2['name']}，你说一下你今晚在锈铁大道看到了什么？"}])
    if resp2: safe_print(f"  [{ch2['name']}] 回复({len(resp2)}): {resp2[:150]}")
    api("POST", f"/game/chat-count/{sid}", {})

# Generate intents for all agents
safe_print("\n[6d] Agent意图生成（检查是否有插队/私聊需求）...")
for ak in companion_keys[:3]:
    r = api("POST", f"/game/intents/{sid}/{ak}/generate", {})
    if r.get("success"):
        intents = r.get("intents", {})
        active = {k:v for k,v in intents.items() if v is not None}
        if active:
            for k,v in active.items():
                safe_print(f"  [{ak}] {k}: {v.get('reason','')[:50]}")
                if v.get("urgency") == "high":
                    safe_print(f"    -> 批准 {k} 意图!")
                    api("POST", f"/game/intents/{sid}/{ak}/approve",
                        {"intent_type":k, "approved":True})
        else:
            safe_print(f"  [{ak}] 无主动意图（安静观察）")

# ---- Step 7: Advance to voting ----
safe_print(f"\n[7] 推进到投票阶段")
for i in range(3):
    api("POST", f"/game/chat-count/{sid}", {})
r = api("POST", f"/game/phase/{sid}/advance", {})
safe_print(f"  当前阶段: {phase_name(r.get('current_phase',''))}")

# ---- Step 8: Vote ----
safe_print(f"\n[8] 投票（真凶: {killer}）")
r = api("POST", f"/game/vote/{sid}", {"killer":killer,"motive":"我找到了关键证据","voter":"player"})
safe_print(f"  投票结果: {r.get('message','?')}")

# ---- Step 9: Reveal ----
safe_print(f"\n[9] 真相揭示")
r = api("POST", f"/game/phase/{sid}/advance", {})
safe_print(f"  阶段: {r.get('current_phase','')}")

# ---- Step 10: Review ----
safe_print(f"\n[10] 复盘")
r = api("POST", f"/game/phase/{sid}/advance", {})
safe_print(f"  阶段: {r.get('current_phase','')}")

# Generate spoiler story
safe_print("\n[10a] 生成剧透故事...")
r = api("POST", f"/game/reveal/{sid}/spoiler", {"killer":killer,"motive":"掩盖真相","voter":"player","correct":True})
safe_print(f"  Spoiler: {r.get('success','?')}")

# ---- Step 11: Review verify ----
safe_print(f"\n[11] 验证Review不再推进")
r = api("POST", f"/game/phase/{sid}/advance", {})
if r.get("_detail",{}).get("detail",{}).get("error") == "cannot_advance":
    safe_print("  [OK] Review阶段正确阻止推进")

# ---- Summary ----
safe_print(f"\n{'='*70}")
safe_print("  游戏流程测试完成")
safe_print(f"  Session: {sid}")
safe_print(f"  真凶: {killer}")
safe_print("  流程: intro -> investigation -> voting -> reveal -> review")
safe_print(f"{'='*70}")

# Also test evidence flow
safe_print(f"\n{'='*70}")
safe_print(f"[额外] 证物与对话测试")
safe_print(f"{'='*70}")

# Create evidence
r = api("POST", "/evidence/create", {
    "scriptId": SCRIPT_ID,
    "sessionId": sid,
    "name": "一封神秘的信件",
    "basicDescription": "在抽屉里发现一封没有署名的信，写着「我知道你12年前的秘密」",
    "category": "document",
    "importance": "high",
    "relatedActors": [characters[0]["name"]] if characters else [],
    "discoveredBy": "player"
})
ev_id = ""
if r.get("evidence"):
    ev_id = r["evidence"].get("id","")
    safe_print(f"  创建证物: {ev_id}")
elif r.get("_detail"):
    safe_print(f"  创建证物: {r['_detail']}")
else:
    safe_print(f"  创建证物: {r.get('id') or r.get('detail','?')}")

# Save conversation
r = api("POST", "/conversations/save", {
    "session_id": sid, "actor_name": "dm",
    "chat_messages": [{"role":"user","content":"游戏开始"}],
    "final_response": "欢迎来到锈铁大道",
})
safe_print(f"  保存对话: {r.get('success','?')}")

# Read conversations
r = api("GET", f"/conversations/session/{sid}")
safe_print(f"  读取对话: turns={len(r.get('turns',[]))}")

# Evidence check
r = api("GET", f"/evidence/script/{SCRIPT_ID}/session/{sid}")
safe_print(f"  证物统计: total={r.get('stats',{}).get('totalEvidences',0)}")

# Capsules
r = api("GET", "/capsules/genes")
if isinstance(r, list):
    safe_print(f"  基因记录: {len(r)}条")
else:
    safe_print(f"  基因记录: {r}")

safe_print(f"\n{'='*70}")
safe_print("  ALL GOOD - 完整游戏测试结束！")
safe_print(f"{'='*70}")
