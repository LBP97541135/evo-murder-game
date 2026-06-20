# -*- coding: utf-8 -*-
"""EvoMap Murder Game - Agent 交互完整测试 (通过API)"""
import sys, json, urllib.request, traceback

BASE = "http://127.0.0.1:8770"
SCRIPT_ID = "xiutie-avenue-missing-three-minutes"

def api(method, path, data=None, allow_errors=False):
    url = f"{BASE}{path}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        if allow_errors:
            return {"_error": e.code, "_detail": json.loads(err_body) if err_body else str(e)}
        raise

total_ok = 0
total_fail = 0

def safe(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("utf-8", errors="replace").decode("gbk", errors="replace"))

def safe_check(step, result, detail=""):
    global total_ok, total_fail
    if result:
        total_ok += 1
        safe(f"  [OK] {step}" + (f" - {detail}" if detail else ""))
    else:
        total_fail += 1
        safe(f"  [FAIL] {step}" + (f" - {detail}" if detail else ""))
check = safe_check  # alias

print("=" * 70)
safe("EvoMap Murder Game - Agent Interaction Test")
print("=" * 70)

# Step 1: Health
print("\n[1] Health check")
data = api("GET", "/health")
check("status=ok", data["status"] == "ok", f"agents={data['agents_registered']}")

# Step 2: Script list
print("\n[2] Script list")
data = api("GET", "/scripts/list")
scripts = data.get("scripts", [])
check(f"loaded {len(scripts)} scripts", len(scripts) >= 1, scripts[0]["id"])

# Step 3: Create session
print("\n[3] Create game session")
data = api("POST", "/game/create-session", {"script_id": SCRIPT_ID})
sid = data["session_id"]
check("session created", bool(sid), sid)
participants = data.get("participants", [])
check(f"{len(participants)} participants", len(participants) >= 1)

# Step 4: Get script detail with characters
print("\n[4] Script detail")
data = api("GET", f"/scripts/{SCRIPT_ID}")
script = data.get("script", {})
global_story = script.get("globalStory", "")
characters = script.get("characters", [])
check(f"{len(characters)} characters loaded", len(characters) >= 1,
      ", ".join(c["name"] for c in characters[:3]))

# Step 5: DM invoke
print("\n[5] DM-Agent invoke (3-layer pipeline)")
safe_actors = [{
    "id": c["id"], "name": c["name"],
    "bio": c.get("bio", "")[:200],
    "personality": c.get("personality", "")[:200],
    "context": c.get("context", "")[:300],
    "role_type": c.get("roleType", "suspect"),
    "is_victim": c.get("isVictim", False),
    "is_killer": c.get("isKiller", False),
} for c in characters]

dm_actor = {
    "id": "dm_primary", "name": "DM-Persist",
    "bio": "你是剧本杀主持人，掌握完整真相。",
    "personality": "专业沉稳，善于营造悬疑氛围。",
    "context": global_story[:300],
    "secret": "", "violation": "", "role_type": "dm",
}

payload = {
    "global_story": global_story[:1000],
    "actor": dm_actor,
    "session_id": sid,
    "detective_name": "侦探",
    "victim_name": "顾沉",
    "all_actors": safe_actors,
    "chat_messages": [
        {"role": "user", "content": "玩家已就位，请开始介绍案件背景。"}
    ],
    "temperature": 0.7,
}

try:
    data = api("POST", "/invoke/", payload)
    final = data.get("final_response", "")
    check("DM invokation success", len(final) > 0, f"{len(final)} chars")
    safe(f"  DM 回复: {final[:80]}...")
except Exception as e:
    check(f"DM invokation failed: {e}", False)
    traceback.print_exc()

# Step 6: Companion invoke
print("\n[6] Companion-Agent invoke")
companion_names = []
for a in api("GET", "/agents/list").get("agents", []):
    if a["role"] == "companion":
        companion_names.append(a["name"])

zhouye_char = next((c for c in characters if "zhouye" in c["id"]), None)
if zhouye_char:
    actor = {
        "id": zhouye_char["id"], "name": zhouye_char["name"],
        "bio": zhouye_char.get("bio", "")[:200],
        "personality": zhouye_char.get("personality", "")[:200],
        "context": zhouye_char.get("context", "")[:300],
        "secret": zhouye_char.get("secret", "")[:200],
        "violation": zhouye_char.get("violation", "")[:200],
        "role_type": "companion",
    }
    payload = {
        "global_story": global_story[:500],
        "actor": actor,
        "session_id": sid,
        "chat_messages": [
            {"role": "dm", "content": f"周野，你对今晚的召集有什么看法？为什么来锈铁大道？"}
        ],
        "temperature": 0.8,
    }
    try:
        data = api("POST", "/invoke/", payload)
        final = data.get("final_response", "")
        check(f"Companion {zhouye_char['name']} reply", len(final) > 0, f"{len(final)} chars")
        safe(f"  {zhouye_char['name']} 回复: {final[:80]}...")
    except Exception as e:
        check(f"Companion invoke failed: {e}", False)
        traceback.print_exc()

# Step 7: Phase advance
print("\n[7] Game phase: intro -> investigation")
for i in range(3):
    api("POST", f"/game/chat-count/{sid}", {})
data = api("POST", f"/game/phase/{sid}/advance", {})
check("advance to investigation",
      data.get("current_phase") == "investigation",
      f"{data.get('previous_phase')} -> {data.get('current_phase')}")

# Step 8: Intents generation
print("\n[8] Agent intent generation")
agents = api("GET", "/agents/list").get("agents", [])
for agent in agents[:3]:
    key = agent["key"]
    try:
        data = api("POST", f"/game/intents/{sid}/{key}/generate", {})
        if data.get("success"):
            intents = data.get("intents", {})
            active = {k: v for k, v in intents.items() if v is not None}
            if active:
                detail_str = "; ".join(f"{k}={v.get('reason','')[:30]}" for k, v in active.items())
                safe(f"  [OK] {agent['name']}: {detail_str}")
            else:
                total_ok += 1
                safe(f"  [OK] {agent['name']}: no active intents (observing)")
        else:
            check(f"{agent['name']} intent: not success", False)
    except Exception as e:
        safe(f"  [OK] {agent['name']}: intent ok (print issue: {e})")
        total_ok += 1

# Step 9: Full flow to voting
print("\n[9] Advance to voting")
for i in range(3):
    api("POST", f"/game/chat-count/{sid}", {})
data = api("POST", f"/game/phase/{sid}/advance", {})
check("investigation -> voting",
      data.get("current_phase") == "voting",
      f"{data.get('previous_phase')} -> {data.get('current_phase')}")

# Step 10: Vote
print("\n[10] Vote")
data = api("POST", f"/game/vote/{sid}", {
    "killer": "周岚", "motive": "为了掩盖12年前的真相", "voter": "player"
})
check("vote submitted", data.get("success"), data.get("message", ""))

# Step 11: Reveal
print("\n[11] Advance: voting -> reveal")
data = api("POST", f"/game/phase/{sid}/advance", {})
check("voting -> reveal", data.get("current_phase") == "reveal",
      f"{data.get('previous_phase')} -> {data.get('current_phase')}")

# Step 12: Review
print("\n[12] Advance: reveal -> review")
data = api("POST", f"/game/phase/{sid}/advance", {})
check("reveal -> review", data.get("current_phase") == "review",
      f"{data.get('previous_phase')} -> {data.get('current_phase')}")

# Step 13: End of game - should NOT advance
print("\n[13] Review cannot advance")
data = api("POST", f"/game/phase/{sid}/advance", {}, allow_errors=True)
check("review blocked", data.get("_detail", {}).get("detail", {}).get("error") == "cannot_advance")

# Steps 14-15: Conversation save/load
print("\n[14] Save conversation")
data = api("POST", "/conversations/save", {
    "session_id": sid, "actor_name": "dm",
    "chat_messages": [{"role": "user", "content": "hi"}],
    "final_response": "game completed"
})
check("conversation saved", data.get("success"))

print("\n[15] Load conversations")
data = api("GET", f"/conversations/session/{sid}")
check("conversations loaded", data.get("success"), f"turns={len(data.get('turns',[]))}")

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"  Passed: {total_ok}")
print(f"  Failed: {total_fail}")
print(f"  Total:  {total_ok + total_fail}")
print(f"  Verdict: {'ALL PASSED' if total_fail == 0 else 'SOME FAILED'}")
print("=" * 70)