# api/ 路 README

## 鑱岃矗
鍚庣 API 鏈嶅姟锛屽熀浜?Python FastAPI銆?
璐熻矗鎵€鏈夊悗绔€昏緫锛欰gent 绠＄悊銆丒voMap 閫氫俊銆丩LM 鎺ㄧ悊銆佹父鎴?Session銆佹暟鎹寔涔呭寲銆佸墽鏈鐞嗐€佽瘉鐗╃郴缁熴€佸墽閫忔晠浜嬨€?

## 鏈湴杩愯

浠ヤ笅鍛戒护鍧囬渶瑕佸湪椤圭洰鏍圭洰褰曟墽琛岋紝鍗冲寘鍚?`api/`銆乣web/` 鍜?`data/` 鐨勭洰褰曘€?

### 1. 鐜瑕佹眰

- Python 3.10 鍙婁互涓婏紝鎺ㄨ崘 Python 3.11銆?
- 榛樿浣跨敤 SQLite锛屾棤闇€鍗曠嫭瀹夎鏁版嵁搴撱€?
- 濡傛灉闇€瑕佽皟鐢?AI 鎺ㄧ悊鎺ュ彛锛岄渶瑕佸噯澶囧搴?Provider 鐨?API Key锛屾垨鑰呰繍琛屾湰鍦?Ollama銆?

### 2. 鍒涘缓铏氭嫙鐜

Windows PowerShell锛?

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

濡傛灉 PowerShell 绂佹鎵ц婵€娲昏剼鏈紝鍙互涓嶆縺娲荤幆澧冿紝鍚庣画鐩存帴浣跨敤锛?

```powershell
.\.venv\Scripts\python.exe
```

macOS / Linux锛?

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 瀹夎渚濊禆

寮€鍙戠幆澧冨缓璁畨瑁呭彲鏇存柊鐨勪緷璧栨竻鍗曪細

```powershell
python -m pip install --upgrade pip
python -m pip install -r api/requirements.txt
```

闇€瑕佷弗鏍煎鐜板綋鍓嶅紑鍙戠幆澧冩椂锛屼娇鐢ㄩ攣瀹氱増鏈細

```powershell
python -m pip install -r api/requirements-lock.txt
```

鏈縺娲?Windows 铏氭嫙鐜鏃讹細

```powershell
.\.venv\Scripts\python.exe -m pip install -r api/requirements.txt
```

### 4. 閰嶇疆鐜鍙橀噺

鍦ㄩ」鐩牴鐩綍鍒涘缓 `.env`銆俙api/config/settings.py` 浣跨敤 `load_dotenv()`锛?
鍥犳浠庨」鐩牴鐩綍鍚姩鏃惰鍙栫殑鏄牴鐩綍涓嬬殑 `.env`銆?

鏈€灏忛厤缃ず渚嬶細

```dotenv
# AI Provider锛歰penai / anthropic / groq / openrouter / ollama
INFERENCE_SERVICE=openai
MODEL=evomap-gemini-3.1-pro-preview
API_KEY=鏇挎崲涓哄疄闄呭瘑閽?
OPENAI_API_BASE=https://api.evomap.ai/v1
MAX_TOKENS=8192

# EvoMap锛涙殏鏃朵笉浣跨敤杩滅▼鑺傜偣鏃跺彲浠ョ暀绌?
EVOMAP_HUB_URL=https://evomap.ai
EVOMAP_NODE_ID=
EVOMAP_NODE_SECRET=

# 鏁版嵁搴擄紱DB_CONN_URL 鐣欑┖鏃朵娇鐢?SQLite
DB_CONN_URL=
SQLITE_PATH=data/murder_mystery.db

DEBUG=true
```

鍙祴璇曞仴搴锋鏌ャ€佸墽鏈鍙栫瓑涓嶈Е鍙?LLM 鐨勬帴鍙ｆ椂锛宍API_KEY` 鍙互鏆傛椂鐣欑┖銆?
璋冪敤 `/invoke`銆佹祦寮?AI銆丄gent 鎰忓浘鐢熸垚绛夋帴鍙ｆ椂蹇呴』閰嶇疆鍙敤鐨勬ā鍨嬫湇鍔°€?

浣跨敤鏈湴 Ollama 鐨勭ず渚嬶細

```dotenv
INFERENCE_SERVICE=ollama
MODEL=qwen2.5:7b
OLLAMA_URL=http://localhost:11434
API_KEY=
```

浣跨敤 PostgreSQL 鏃惰缃細

```dotenv
DB_CONN_URL=postgresql+psycopg://鐢ㄦ埛鍚?瀵嗙爜@localhost:5432/鏁版嵁搴撳悕
```

### 5. 鍚姩鍚庣

鎺ㄨ崘浠庨」鐩牴鐩綍鍚姩锛?

```powershell
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

鏈縺娲?Windows 铏氭嫙鐜鏃讹細

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

macOS / Linux 鍛戒护鐩稿悓锛?

```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

涓嶈杩涘叆 `api/` 鐩綍鍚庢墽琛?`uvicorn main:app`锛岄」鐩唴閮ㄤ娇鐢?`api.*`
缁濆瀵煎叆锛屼粠椤圭洰鏍圭洰褰曚互 `api.main:app` 鍚姩鏈€绋冲畾銆?

### 6. 楠岃瘉鏈嶅姟

鍚姩鎴愬姛鍚庤闂細

- 鍋ュ悍妫€鏌ワ細<http://localhost:8000/health>
- Swagger API 鏂囨。锛?http://localhost:8000/docs>
- OpenAPI JSON锛?http://localhost:8000/openapi.json>

PowerShell 楠岃瘉鍛戒护锛?

```powershell
Invoke-RestMethod http://localhost:8000/health
```

鎴栬€咃細

```powershell
curl.exe http://localhost:8000/health
```

### 7. 鍚屾椂鍚姩鍓嶇

鍙﹀紑涓€涓粓绔細

```bash
cd web
npm install
npm start
```

鍓嶇榛樿杩炴帴 `http://localhost:8000`锛堥€氳繃 `package.json` 鐨?`proxy` 閰嶇疆锛夈€?
`npm start` 宸叉敼涓鸿法骞冲彴鍏煎锛屾棤闇€璁剧疆鐜鍙橀噺鍗冲彲鍦?Windows/macOS/Linux 杩愯銆?

濡傞渶鑷畾涔夊悗绔湴鍧€锛?

```bash
# macOS / Linux
VITE_API_URL=http://localhost:8000 npm start

# Windows PowerShell
$env:VITE_API_URL="http://localhost:8000"; npm start
```

### 甯歌闂

#### `ModuleNotFoundError: No module named 'api'`

纭褰撳墠鐩綍鏄」鐩牴鐩綍锛屽苟浣跨敤锛?

```powershell
python -m uvicorn api.main:app --reload --port 8000
```

#### PowerShell 鏃犳硶杩愯 `Activate.ps1`

鏃犻渶淇敼绯荤粺鎵ц绛栫暐锛屽彲浠ョ洿鎺ヤ娇鐢ㄨ櫄鎷熺幆澧冧腑鐨?Python锛?

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8000
```

#### SQLite 鎶?`unable to open database file`

纭浠庨」鐩牴鐩綍鍚姩锛屽苟涓旀牴鐩綍涓嬪瓨鍦?`data/`銆傞粯璁ゆ暟鎹簱鏂囦欢涓猴細

```text
data/murder_mystery.db
```

#### `/game/create-session` 杩斿洖 `No agents registered yet`

鍒涘缓娓告垙 Session 鍓嶏紝鍚庣缂栨帓鍣ㄤ腑鑷冲皯闇€瑕佷竴涓凡娉ㄥ唽 Agent銆傚彲浠ュ厛閫氳繃
Swagger 璋冪敤 `POST /agents/register`銆傚鏋滃彧寮€鍙戦〉闈紝鍓嶇浼氶檷绾т负鏈湴娓告垙妯″紡銆?

#### AI 鎺ュ彛杩斿洖璁よ瘉鎴栨ā鍨嬮敊璇?

妫€鏌?`.env` 涓殑 `INFERENCE_SERVICE`銆乣MODEL`銆乣API_KEY` 鍜屽搴?API Base銆?
淇敼 `.env` 鍚庨渶瑕侀噸鍚悗绔繘绋嬨€?

## 鐩綍缁撴瀯

```
api/
鈹溾攢鈹€ main.py                 鈫?FastAPI 鍏ュ彛锛宎pp鍒濆鍖?+ 璺敱鎸傝浇
鈹溾攢鈹€ requirements.txt        鈫?Python 渚濊禆娓呭崟
鈹溾攢鈹€ __init__.py             鈫?鍖呮爣璁?
鈹?
鈹溾攢鈹€ config/                 鈫?閰嶇疆绠＄悊
鈹?  鈹溾攢鈹€ settings.py         鈫?.env璇诲彇锛屾墍鏈夐厤缃彉閲?
鈹?  鈹斺攢鈹€ README.md
鈹?
鈹溾攢鈹€ evomap/                 鈫?EvoMap A2A Protocol 瀹㈡埛绔?
鈹?  鈹溾攢鈹€ evomap_client.py    鈫?鍏ㄧ鐐瑰皝瑁咃紙30+鏂规硶锛?
鈹?  鈹溾攢鈹€ __init__.py
鈹?  鈹斺攢鈹€ README.md
鈹?
鈹溾攢鈹€ agents/                 鈫?澶欰gent缂栨帓绯荤粺
鈹?  鈹溾攢鈹€ agent_orchestrator.py 鈫?AgentNode + Orchestrator + 瑙掕壊妯℃澘
鈹?  鈹溾攢鈹€ __init__.py
鈹?  鈹斺攢鈹€ README.md
鈹?
鈹溾攢鈹€ llm/                    鈫?LLM 鎺ㄧ悊鏈嶅姟
鈹?  鈹溾攢鈹€ llm_service.py      鈫?涓夊眰绠￠亾 + 5涓狿rovider + 瑙掕壊Prompt
鈹?  鈹溾攢鈹€ __init__.py
鈹?  鈹斺攢鈹€ README.md
鈹?
鈹溾攢鈹€ schemas/                鈫?Pydantic 鏁版嵁妯″瀷
鈹?  鈹溾攢鈹€ invoke_types.py     鈫?鎵€鏈夎姹?鍝嶅簲妯″瀷 + SafeActor
鈹?  鈹溾攢鈹€ __init__.py
鈹?  鈹斺攢鈹€ README.md
鈹?
鈹溾攢鈹€ db/                     鈫?鏁版嵁鎸佷箙鍖?
鈹?  鈹溾攢鈹€ models.py           鈫?SQLAlchemy ORM 妯″瀷锛?5涓〃 + 杞崲鍑芥暟锛?
鈹?  鈹溾攢鈹€ database.py         鈫?杩炴帴寮曟搸 + 鍒濆鍖?+ Session
鈹?  鈹溾攢鈹€ __init__.py
鈹?  鈹斺攢鈹€ README.md
鈹?
鈹溾攢鈹€ routes/                 鈫?FastAPI 璺敱瀹氫箟
鈹?  鈹溾攢鈹€ health.py           鈫?/health 鍋ュ悍妫€鏌?
鈹?  鈹溾攢鈹€ agents.py           鈫?/agents 娉ㄥ唽/鍒楄〃/蹇冭烦/杩涘寲
鈹?  鈹溾攢鈹€ invoke.py           鈫?/invoke AI涓夊眰绠￠亾
鈹?  鈹溾攢鈹€ game.py             鈫?/game Session/骞挎挱/澶嶇洏
鈹?  鈹溾攢鈹€ memory.py           鈫?/memory 璁板綍/鍙洖/鐘舵€?
鈹?  鈹溾攢鈹€ scripts.py          鈫?/scripts 鍓ф湰CRUD锛堜繚瀛?鍒楄〃/璇︽儏/鍒犻櫎锛?
鈹?  鈹溾攢鈹€ evidence.py         鈫?/evidence 璇佺墿绯荤粺锛堝垱寤?鏌ヨ/鍑虹ず/缁勫悎/杩涘害锛?
鈹?  鈹溾攢鈹€ spoiler_stories.py  鈫?/spoiler-stories 鍓ч€忔晠浜嬬鐞?
鈹?  鈹溾攢鈹€ __init__.py
鈹?  鈹斺攢鈹€ README.md
鈹?
鈹斺攢鈹€ README.md               鈫?鏈枃浠?
```

## 褰撳墠闇€姹?
- [ ] 瀹為檯娴嬭瘯鎵€鏈?EvoMap 绔偣璋冪敤
- [ ] 瀹為檯娴嬭瘯涓夊眰 LLM 绠￠亾
- [ ] 瀹炵幇娴佸紡 SSE 杈撳嚭
- [ ] 瀹炵幇 constitution 鑷姩鏀瑰啓閫昏緫
- [ ] 娣诲姞鍥惧儚鐢熸垚璺敱锛堝ご鍍?灏侀潰/鑳屾櫙锛?
- [ ] 娣诲姞 Council 娌荤悊璺敱
- [ ] 璇佹嵁 LLM 鍙嶅簲瀵规帴锛?evidence/present 鎺ュ叆 llm_service锛?

## 杩涘害
- 鉁?椤圭洰缁撴瀯浠庢墎骞?鈫?妯″潡鍖栨媶鍒嗗畬鎴?
- 鉁?鎵€鏈?import 璺緞鏇存柊瀹屾瘯
- 鉁?main.py 鍙仛鍒濆鍖?+ 璺敱鎸傝浇
- 鉁?routes 浠?main.py 鍗曚綋鎷嗗垎涓?8 涓嫭绔嬫枃浠?
- 鉁?鏁版嵁搴撲粠 6 涓〃鎵╁睍鍒?15 涓〃锛堝惈娓告垙寮曟搸瀹屾暣鐨勮瘉鐗╃郴缁?杩涘害琛級
- 鉁?鍓ф湰 CRUD API锛堜繚瀛?鍒楄〃/璇︽儏/鍒犻櫎锛屽惈瑙掕壊/璇佺墿/灏侀潰澶勭悊锛?
- 鉁?杩愯鏃惰瘉鐗╃郴缁燂紙鍒涘缓/鏌ヨ/鏇存柊/鍑虹ず/缁勫悎/杩涘害杩借釜锛?涓鐐癸級
- 鉁?鍓ч€忔晠浜嬬鐞嗭紙CRUD + 鎵归噺鍒犻櫎锛?涓鐐癸級
- 鉁?鍏ㄩ儴鏂板绔偣闆嗘垚娴嬭瘯閫氳繃

## 鐤戦棶
- 姣忎釜瀛愮洰褰曠殑 README 涓凡鍒楀嚭鍚勮嚜鐨勫叿浣撶枒闂?
- 鏈€鍏抽敭鐨勯樆濉炵偣锛欵voMap hello 绔偣鐨勫疄闄呰繑鍥炴牸寮忛渶瑕侀獙璇?
- 璇佹嵁 /present 鐨?AI 鍙嶅簲锛氭槸鍦ㄥ悗绔唴璋冪敤 LLM锛岃繕鏄鍓嶇鐢?/invoke 鑷繁瑙﹀彂锛?
