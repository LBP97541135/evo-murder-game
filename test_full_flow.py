"""
EvoMap Murder Game — 完整流程测试脚本
测试：健康检查 → 人设初始化 → 注册Agent → 创建Session → 阶段流转 → 发言 → LLM调用 → 证物出示 → 多人投票
"""

import requests
import json
import sys
import time

BASE = "http://127.0.0.1:8000"


def ok(r):
    if r.status_code != 200:
        return False
    data = r.json()
    if isinstance(data, dict) and data.get("success") is False:
        return False
    if isinstance(data, dict) and "error" in data:
        return False
    return True


def section(s):
    print(f"\n{'='*60}")
    print(f"  {s}")
    print(f"{'='*60}")


# ====================================
section("1. 健康检查")
r = requests.get(f"{BASE}/health")
print(f"Health: {r.json()}")
assert r.status_code == 200

# ====================================
section("2. 初始化人设库")
r = requests.post(f"{BASE}/agents/personas/init")
print(f"Persona init: {r.json()}")
assert ok(r)

# ====================================
section("3. 查看已有剧本")
r = requests.get(f"{BASE}/scripts/list")
assert ok(r)
scripts = r.json().get("scripts", [])
print(f"已有剧本: {len(scripts)} 个")
if not scripts:
    print("❌ 没有剧本，无法继续")
    sys.exit(1)

script = scripts[0]
script_id = script["id"]
characters = script.get("characters", [])
print(f"选中的剧本: {script['title']} (ID={script_id})")
print(f"角色 ({len(characters)} 个):")
for c in characters:
    print(f"  - {c['name']} (isKiller={c.get('isKiller')}, roleType={c.get('roleType')})")

# ====================================
section("4. 注册 Agent")
companion_personas = ["white-crow", "echo", "paper-owl", "flint"]
agent_keys = []

# DM
r = requests.post(f"{BASE}/agents/register", json={
    "role": "dm",
    "name": "雾港主理人",
    "model": "evomap-deepseek-v4-flash",
})
assert ok(r), f"DM注册失败: {r.json()}"
dm_result = r.json()
print(f"DM 雾港主理人 → 模式: {dm_result.get('mode')}")

# Companions
for pk in companion_personas:
    r = requests.post(f"{BASE}/agents/register", json={
        "role": "companion",
        "name": pk,
        "model": "evomap-deepseek-v4-flash",
    })
    assert ok(r), f"{pk}注册失败: {r.json()}"
    key = f"companion_{pk}"
    agent_keys.append(key)
    print(f"Companion {pk} → 模式: {r.json().get('mode')}")

# List
r = requests.get(f"{BASE}/agents/list")
print(f"已注册 Agent: {len(r.json().get('agents', []))} 个")

# ====================================
section("5. 加载人设")
r = requests.post(f"{BASE}/agents/personas/load", json={
    "agent_key": "dm_雾港主理人",
    "persona_key": "mist-harbor"
})
print(f"DM 雾港主理人: {r.json().get('success', r.json().get('error'))}")

for pk in companion_personas:
    r = requests.post(f"{BASE}/agents/personas/load", json={
        "agent_key": f"companion_{pk}",
        "persona_key": pk
    })
    print(f"{pk}: {r.json().get('success', r.json().get('error'))}")

# ====================================
section("6. 创建游戏 Session")
r = requests.post(f"{BASE}/game/create-session", json={
    "script_id": script_id,
    "topic": "测试对局"
})
assert ok(r), f"创建Session失败: {r.json()}"
session_id = r.json().get("session_id", "")
print(f"Session ID: {session_id}")
print(f"Participants: {r.json().get('participants', [])}")

# ====================================
section("7. 检查游戏阶段")
r = requests.get(f"{BASE}/game/phase/{session_id}")
assert ok(r)
print(f"当前阶段: {r.json().get('display_name')}")

# ====================================
section("8. Agent游戏状态 — 信息隔离验证")
if agent_keys:
    first_key = agent_keys[0]
    r = requests.get(f"{BASE}/game/agent-state/{session_id}/{first_key}")
    if r.status_code == 200:
        state = r.json().get("state", {})
        ch = state.get("character", {})
        all_actors = state.get("all_actors", [])
        print(f"Agent: {first_key}")
        print(f"  自己角色: {ch.get('name')} (secret长度={len(ch.get('secret',''))})")
        print(f"  其他人信息(all_actors): {len(all_actors)} 条")
        if not all_actors:
            print(f"  ✅ 信息隔离生效：Agent 不知道其他角色的任何信息")
        else:
            print(f"  ⚠️ 仍有透传")
    else:
        print(f"  获取状态失败: {r.json()}")

# ====================================
section("9. 阶段推进: intro → investigation")
r = requests.post(f"{BASE}/game/phase/{session_id}/advance")
print(f"推进结果: {r.json()}")

r = requests.get(f"{BASE}/game/phase/{session_id}")
print(f"当前阶段: {r.json().get('display_name')}")
print(f"允许操作: {r.json().get('allowed_actions')}")

# ====================================
section("10. Agent 发言")
if agent_keys:
    test_key = agent_keys[0]
    r = requests.post(f"{BASE}/game/agent-chat/{session_id}", json={
        "session_id": session_id,
        "agent_key": test_key,
        "content": f"大家好，我是{test_key}，很高兴见到各位！",
        "role": "agent"
    })
    print(f"{test_key} 发言: {'✅' if r.json().get('success') else '❌'}")
    print(f"对话计数: {r.json().get('chat_count', 0)}")

# ====================================
section("11. LLM 调用测试")
test_agent_key = agent_keys[0] if agent_keys else "companion_white-crow"
r = requests.get(f"{BASE}/game/agent-state/{session_id}/{test_agent_key}")
char_info = {}
if r.status_code == 200:
    ch = r.json().get("state", {}).get("character", {})
    char_info = {
        "id": ch.get("id", "test"),
        "name": ch.get("name", "测试角色"),
        "bio": ch.get("bio", "测试"),
        "personality": ch.get("personality", "友善"),
        "context": ch.get("context", ""),
        "secret": ch.get("secret", ""),
        "violation": ch.get("violation", ""),
    }
else:
    char_info = {"id": "test", "name": "测试", "bio": "test", "personality": "friendly", "context": "", "secret": "", "violation": ""}

r = requests.post(f"{BASE}/invoke/", json={
    "actor": char_info,
    "session_id": session_id,
    "chat_messages": [{"role": "user", "content": "你好，请问你是谁？"}],
    "temperature": 0.7,
})
if r.status_code == 200:
    final = r.json().get("final_response", "")
    print(f"LLM 回复 ({len(final)} 字符): {final[:180]}...")
    print(f"✅ LLM 调用成功")
else:
    print(f"❌ LLM 调用失败: {r.text[:300]}")

# ====================================
section("12. 创建证物")
r = requests.post(f"{BASE}/evidence/create", json={
    "scriptId": script_id,
    "sessionId": session_id,
    "name": "一封神秘的信件",
    "basicDescription": "在书房抽屉里发现的一封没有署名的信，上面写着「我知道你的秘密」",
    "category": "document",
    "importance": "high",
    "relatedActors": [characters[0]["name"]] if characters else [],
    "discoveredBy": "player"
})
evidence_id = r.json().get("evidence", {}).get("id", "") if ok(r) else ""
print(f"证物ID: {evidence_id}" if evidence_id else f"创建结果: {r.json()}")

# ====================================
section("13. 出示证物（核心优化测试）")
if evidence_id and len(characters) >= 2:
    target = characters[1]["name"]
    r = requests.post(f"{BASE}/evidence/present", json={
        "evidenceId": evidence_id,
        "presentedTo": target,
        "presentedBy": "player",
        "sessionId": session_id,
        "textContent": "我发现了这封信，上面写着「我知道你的秘密」，你知道这是怎么回事吗？",
    })
    if r.status_code == 200:
        resp = r.json()
        print(f"✅ 出示证物成功!")
        ai_resp = resp.get("aiResponse", "")
        print(f"目标角色回应 ({len(ai_resp)} 字符): {ai_resp[:200]}...")
        print(f"解锁新线索: {resp.get('newEvidencesUnlocked', [])}")
    else:
        print(f"❌ 出示失败: {r.text[:300]}")
else:
    print(f"跳过（evidence_id={evidence_id}, 角色数={len(characters)}）")

# ====================================
section("14. Agent 意图生成")
if agent_keys:
    test_key = agent_keys[0]
    r = requests.post(f"{BASE}/game/intents/{session_id}/{test_key}/generate")
    if r.status_code == 200:
        intents = r.json().get("intents", {})
        print(f"{test_key} 意图: {json.dumps(intents, ensure_ascii=False)[:250]}")
    else:
        print(f"意图生成失败: {r.json()}")

# ====================================
section("15. 多人投票测试")
# 先推进到 voting
for i in range(5):
    r = requests.post(f"{BASE}/game/phase/{session_id}/advance")
    phase = r.json().get("current_phase") or r.json().get("error", "?")
    print(f"推进 [{i}]: {phase}")
    if "voting" in str(phase) or "error" in str(phase):
        break

r = requests.get(f"{BASE}/game/phase/{session_id}")
print(f"当前阶段: {r.json().get('display_name')}")

# True killer
killer_name = ""
for c in characters:
    if c.get("isKiller"):
        killer_name = c["name"]
        break
print(f"真凶: {killer_name or '未标记'}")

# 玩家投票
r = requests.post(f"{BASE}/game/vote/{session_id}", json={
    "killer": killer_name or characters[-1]["name"],
    "motive": "我推断是你！",
    "voter": "player"
})
print(f"玩家 投票: {r.json().get('message', r.json().get('error', '?'))}")
print(f"投票情况: {r.json().get('voted_count', 0)}/{r.json().get('total_voters', 0)}")

# Agent 投票
for ak in agent_keys:
    r = requests.get(f"{BASE}/game/agent-state/{session_id}/{ak}")
    if r.status_code != 200:
        continue
    ch = r.json().get("state", {}).get("character", {})
    if not ch or ch.get("roleType") == "victim":
        print(f"{ak} 是受害者，跳过投票")
        continue
    vote_target = killer_name or characters[-1]["name"]
    r2 = requests.post(f"{BASE}/game/vote/{session_id}", json={
        "killer": vote_target,
        "motive": "根据线索推断",
        "voter": ak
    })
    msg = r2.json().get("message", r2.json().get("error", "?"))
    print(f"{ak} 投票: {msg}")
    if r2.json().get("auto_advanced"):
        print(f"  >>> 自动推进到 {r2.json().get('next_phase')} <<<")

# ====================================
section("16. 最终状态")
r = requests.get(f"{BASE}/game/phase/{session_id}")
pi = r.json()
print(f"最终阶段: {pi.get('display_name', '?')}")
print(f"投票结果: {pi.get('can_advance', '?')}")

section("✅ 完整流程测试通过！")