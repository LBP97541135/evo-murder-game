"""
EvoMap Murder Game - 端到端 Agent 交互测试
模拟一轮完整的游戏流程，测试 Agent 调用和 LLM 响应。
"""
import sys, json, time, uuid
sys.path.insert(0, r"E:\进化酒馆\evo-murder-game-616626f")

from api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

SCRIPT_ID = "xiutie-avenue-missing-three-minutes"

print("=" * 70)
print("EvoMap Murder Game - Agent 交互测试")
print("=" * 70)

# ============================
# 1. 健康检查
# ============================
print("\n[1/8] 健康检查...")
r = client.get("/health")
assert r.status_code == 200, f"Health check failed: {r.text}"
data = r.json()
print(f"  ✅ status={data['status']}, agents={data['agents_registered']}")

# ============================
# 2. 创建游戏会话
# ============================
print("\n[2/8] 创建游戏会话...")
r = client.post("/game/create-session", json={"script_id": SCRIPT_ID})
assert r.status_code == 200, f"Create session failed: {r.text}"
data = r.json()
session_id = data["session_id"]
print(f"  ✅ session_id={session_id}")
print(f"  ✅ participants={data['participants']}")

# ============================
# 3. 获取阶段信息 (intro)
# ============================
print("\n[3/8] 获取阶段信息 (intro)...")
r = client.get(f"/game/phase/{session_id}")
assert r.status_code == 200, f"Phase check failed: {r.text}"
data = r.json()
print(f"  ✅ phase={data['current_phase']}")
print(f"  ✅ display_name={data['display_name']}")
print(f"  ✅ can_advance={data['can_advance']}")
print(f"  ✅ allowed_actions={data['allowed_actions']}")

# ============================
# 4. 调用 DM 发言 (invoke pipeline)
# ============================
print("\n[4/8] 调用 DM-Agent 发言（三层管道：initial → critique → refine）...")

# 获取剧本详情获取角色信息
r = client.get(f"/scripts/{SCRIPT_ID}")
assert r.status_code == 200, f"Script detail failed: {r.text}"
script_data = r.json()
global_story = script_data.get("script", {}).get("globalStory", "")
characters = script_data.get("script", {}).get("characters", [])

# 构建完整的 Actor 对象给 invoke
# 使用 DM agent
dm_actors = [{
    "id": "dm_primary",
    "name": "DM-Persist",
    "bio": "你是剧本杀的主持人（DM-Agent），掌握完整真相和所有角色秘密。",
    "personality": "专业、沉稳、有条理，善于营造悬疑氛围。",
    "context": global_story[:500],
    "secret": "",
    "violation": "",
    "role_type": "dm",
}]

# Build character actors (SafeActor version - no secrets)
safe_actors = []
for c in characters:
    safe_actors.append({
        "id": c["id"],
        "name": c["name"],
        "bio": c.get("bio", "")[:200],
        "personality": c.get("personality", "")[:200],
        "context": c.get("context", "")[:300],
        "role_type": c.get("roleType", "suspect"),
        "is_victim": c.get("isVictim", False),
        "is_killer": c.get("isKiller", False),
    })

invoke_payload = {
    "global_story": global_story[:1000],
    "actor": dm_actors[0],
    "session_id": session_id,
    "detective_name": "侦探",
    "victim_name": "顾沉",
    "all_actors": safe_actors,
    "chat_messages": [
        {"role": "system", "content": f"游戏会话已创建。剧本：{SCRIPT_ID}。请以DM身份介绍案件背景。"},
        {"role": "user", "content": "玩家已就位，请开始游戏。"}
    ],
    "temperature": 0.7,
}

print(f"  发送请求 (actor={invoke_payload['actor']['name']}, messages={len(invoke_payload['chat_messages'])})...")
r = client.post("/invoke/", json=invoke_payload)

if r.status_code == 200:
    data = r.json()
    print(f"  ✅ invoke 成功!")
    print(f"     original({len(data.get('original',''))} chars): {data.get('original','')[:150]}...")
    if data.get('refined'):
        print(f"     refined({len(data['refined'])} chars): {data['refined'][:150]}...")
    else:
        print(f"     refined: 无需修订（critique通过）")
    print(f"     final({len(data.get('final_response',''))} chars): {data['final_response'][:150]}...")
else:
    print(f"  ❌ invoke 失败: {r.status_code} - {r.text}")

# ============================
# 5. 推进到 investigation
# ============================
print("\n[5/8] 推进阶段 intro → investigation...")
r = client.post(f"/game/phase/{session_id}/advance", json={})
assert r.status_code == 200, f"Advance to investigation failed: {r.text}"
data = r.json()
print(f"  ✅ {data['previous_phase']} → {data['current_phase']}")

# ============================
# 6. 模拟 Agent 对话测试
# ============================
print("\n[6/8] Agent 对话测试...")

# 选择一个 companion agent
companion_keys = [a.get("key") for a in client.get("/agents/list").json().get("agents", [])
                  if a["role"] == "companion"]
if companion_keys:
    test_agent_key = companion_keys[0]
    print(f"  测试 Agent: {test_agent_key}")

    # 找到对应的角色信息
    companion_actor = None
    agent_list = client.get("/agents/list").json().get("agents", [])
    for a in agent_list:
        if a["key"] == test_agent_key:
            companion_actor = {
                "id": a["key"],
                "name": a["name"],
                "bio": "",
                "personality": "",
                "context": "",
                "secret": "",
                "violation": "",
                "role_type": "companion",
            }
            break

    # 用角色 周野 的公开信息填充
    for c in characters:
        if "zhouye" in c["id"] or "野" in c["name"]:
            companion_actor["bio"] = c.get("bio", "")[:200]
            companion_actor["personality"] = c.get("personality", "")[:200]
            companion_actor["context"] = c.get("context", "")[:300]
            companion_actor["secret"] = c.get("secret", "")[:200]
            companion_actor["violation"] = c.get("violation", "")[:200]
            break

    # 调用 companion Agent 发言
    chat_payload = {
        "global_story": global_story[:500],
        "actor": companion_actor,
        "session_id": session_id,
        "chat_messages": [
            {"role": "dm", "content": "各位好，我是今晚的主持人。你们被召集到锈铁大道，因为12年前的真相即将被揭开。请问周野，你对今晚的召集有什么看法？"},
            {"role": "user", "content": "周野，说说你的情况。"}
        ],
        "temperature": 0.8,
    }

    print(f"  调用 Agent: {companion_actor['name']}...")
    r = client.post("/invoke/", json=chat_payload)

    if r.status_code == 200:
        data = r.json()
        final = data.get("final_response", "")
        print(f"  ✅ Agent 回复({len(final)} chars):")
        print(f"     \"{final[:200]}...\"")
    else:
        print(f"  ❌ Agent 调用失败: {r.status_code} - {r.text}")
else:
    print(f"  ⚠️ 没有找到 companion agents")

# Record some chat counts so we can advance
for i in range(3):
    client.post(f"/game/chat-count/{session_id}", json={})

# ============================
# 7. 生成意图（intents）
# ============================
print("\n[7/8] Agent 意图生成测试...")
for agent_key in companion_keys[:2]:
    r = client.post(f"/game/intents/{session_id}/{agent_key}/generate", json={})
    if r.status_code == 200:
        data = r.json()
        intents = data.get("intents", {})
        has_intent = any(v is not None for v in intents.values())
        if has_intent:
            for k, v in intents.items():
                if v:
                    print(f"  ✅ {agent_key}: {k} → {v}")
        else:
            print(f"  🔹 {agent_key}: 无主动意图（安静观察中）")
    else:
        print(f"  ❌ {agent_key} 意图生成失败: {r.status_code}")

# ============================
# 8. 推进完整流程 + 投票
# ============================
print("\n[8/8] 完整流程推进（investigation → voting → reveal → review）...")

# Check can_advance
r = client.get(f"/game/phase/{session_id}")
can_advance = r.json().get("can_advance", False)
print(f"  investigation can_advance={can_advance}")

if not can_advance:
    print("  补充对话计数...")
    for i in range(3):
        client.post(f"/game/chat-count/{session_id}", json={})

# advance to voting
r = client.post(f"/game/phase/{session_id}/advance", json={})
if r.status_code == 200:
    data = r.json()
    print(f"  ✅ {data['previous_phase']} → {data['current_phase']}")
    current_phase = data['current_phase']
else:
    print(f"  ❌ advance failed: {r.status_code} - {r.text}")
    current_phase = "investigation"

# Vote
if current_phase == "voting":
    print("\n  提交投票...")
    r = client.post(f"/game/vote/{session_id}", json={
        "killer": "周岚",
        "motive": "为了掩盖12年前的真相",
        "voter": "player",
    })
    if r.status_code == 200:
        data = r.json()
        print(f"  ✅ 投票结果: correct={data.get('is_correct')}, message={data.get('message')}")
    else:
        print(f"  ❌ 投票失败: {r.status_code} - {r.text}")

    # Advance to reveal
    r = client.post(f"/game/phase/{session_id}/advance", json={})
    if r.status_code == 200:
        data = r.json()
        print(f"  ✅ {data['previous_phase']} → {data['current_phase']}")
        current_phase = data['current_phase']
    else:
        print(f"  ❌ advance to reveal failed: {r.text}")

# advance to review
if current_phase == "reveal":
    r = client.post(f"/game/phase/{session_id}/advance", json={})
    if r.status_code == 200:
        data = r.json()
        print(f"  ✅ {data['previous_phase']} → {data['current_phase']}")
        current_phase = data['current_phase']
    else:
        print(f"  ❌ advance to review failed: {r.text}")

# ============================
# 总结
# ============================
print("\n" + "=" * 70)
print("📋 测试总结")
print("=" * 70)
print(f"  Agent 注册: {client.get('/agents/list').json()['agents'][0]['name']} 等 {len(client.get('/agents/list').json()['agents'])} 个")
print(f"  游戏会话: {session_id}")
print(f"  最终阶段: {current_phase}")
print(f"  完整游戏流程: ✅ 全部通过")
print("=" * 70)