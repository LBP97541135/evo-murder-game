# web/ 鐩綍 README

## 鑱岃矗

`web/` 鏄繘鍖栭厭棣嗙殑涓诲墠绔簲鐢紝鍩轰簬 React 18銆乀ypeScript銆?
Mantine UI 7銆丷eact Router 7 鍜?Create React App銆?

褰撳墠鐗堟湰鏄殫榛戝伐涓氬墽鍦洪鏍肩殑闈欐€佸彲浜や簰鍘熷瀷锛岃鐩栧墽鏈€夋嫨銆佹父鎴忚垶鍙般€?
Agent 闃靛鍜屼釜浜哄姪鎵嬪洓鏉′富瑕佺敤鎴疯矾寰勩€傝瑙夋柟鍚戝弬鑰?`figma-make/`锛?
浣嗕富搴旂敤缁х画浣跨敤 Mantine锛屼笉鐩存帴澶嶇敤鍙傝€冨伐绋嬬殑 Tailwind 鍜?Radix 缁勪欢銆?

## 鐩綍缁撴瀯

```text
web/
鈹溾攢鈹€ figma-make/             # 鐙珛鐨?Figma Make/Vite 瑙嗚鍙傝€冨伐绋?
鈹溾攢鈹€ public/                 # CRA 闈欐€佽祫婧愪笌 HTML 鍏ュ彛
鈹溾攢鈹€ src/
鈹?  鈹溾攢鈹€ api/                # 鍚庣 API 璋冪敤灏佽
鈹?  鈹溾攢鈹€ components/         # 鍙鐢ㄤ笟鍔＄粍浠堕鐣欑洰褰?
鈹?  鈹溾攢鈹€ constants/          # 甯搁噺棰勭暀鐩綍
鈹?  鈹溾攢鈹€ pages/              # 鍥涗釜涓婚〉闈笌鍏变韩 StudioShell
鈹?  鈹溾攢鈹€ providers/          # constate 鍏ㄥ眬鐘舵€?
鈹?  鈹溾攢鈹€ types/              # TypeScript 绫诲瀷
鈹?  鈹溾攢鈹€ utils/              # 宸ュ叿鍑芥暟棰勭暀鐩綍
鈹?  鈹溾攢鈹€ App.tsx             # Mantine 涓婚銆丳rovider 鍜岃矾鐢?
鈹?  鈹溾攢鈹€ index.tsx           # React 鍏ュ彛鍙?Mantine 鍩虹鏍峰紡鍏ュ彛
鈹?  鈹斺攢鈹€ styles.css          # 鍏ㄥ眬瀛椾綋銆佽儗鏅€佸崱鐗囧拰姘涘洿鏍峰紡
鈹溾攢鈹€ package.json
鈹斺攢鈹€ tsconfig.json
```

## 鍚姩涓庢瀯寤?

```bash
cd web
npm install
npm start
```

寮€鍙戞湇鍔″櫒榛樿鍦板潃涓?`http://localhost:3000`锛屽墠绔?API 閫氳繃 `package.json`
鐨?`proxy` 浠ｇ悊鍒?`http://localhost:8000`銆俙npm start` 鏃犻渶棰濆鐜鍙橀噺锛?
璺ㄥ钩鍙帮紙Windows/macOS/Linux锛夌洿鎺ヨ繍琛屻€?

濡傞渶鑷畾涔夊悗绔湴鍧€锛?

```bash
# macOS / Linux
VITE_API_URL=http://localhost:8000 npm start

# Windows PowerShell
$env:VITE_API_URL="http://localhost:8000"; npm start
```

鐢熶骇鏋勫缓锛?

```powershell
cd web
npm run build
```

## 搴旂敤鍏ュ彛

- `src/index.tsx` 蹇呴』瀵煎叆 `@mantine/core/styles.css`銆傜己灏戣鍏ュ彛鏃讹紝
  Mantine 缁勪欢鍙細淇濈暀涓嶅畬鏁寸殑鍩虹澶栬銆?
- `src/App.tsx` 鍒涘缓鏆楄壊 Mantine 涓婚锛屽畾涔夌孩鑹插己璋冭壊銆佹鏂囧拰鏍囬瀛椾綋锛?
  骞舵寕杞?Agent銆丼cript銆丼ession銆丮ystery 鍥涘眰 Provider銆?
- `src/styles.css` 鎻愪緵鏆楄壊娓愬彉銆佺綉鏍肩汗鐞嗐€佺幓鐠冭儗鏅€佸伐涓氬崱鐗囥€?
  Hero 鍜岀瓑瀹芥爣绛剧瓑璺ㄩ〉闈㈡牱寮忋€?
- 鍏ㄥ眬瀛椾綋浠?Google Fonts 鍔犺浇锛涚绾跨幆澧冧細鍥為€€鍒?Georgia 鍜?monospace銆?

## 椤甸潰璺敱

| 璺敱 | 椤甸潰 | 褰撳墠鑳藉姏 |
|------|------|----------|
| `/` | 閲嶅畾鍚?| 鑷姩璺宠浆鍒?`/library` |
| `/library` | 鍓ф湰搴?| 鎼滅储銆侀鏉愪笌闅惧害绛涢€夈€佹帹鑽愭祦銆佽鎯呭拰 Agent 閫傞厤 |
| `/play/:id` | 娓告垙涓荤晫闈?| 妯″紡鍒囨崲銆佸満鏅垶鍙般€佺帺瀹朵簰鍔ㄣ€丏M 鑺傚鍜屽鐩?|
| `/agents` | Agent 骞垮満 | 闄帺/DM 鍒囨崲銆佹悳绱㈢瓫閫夈€佽鎯呫€侀樀瀹逛笌鎿嶄綔鍏ュ彛 |
| `/evolution` | 涓汉鍔╂墜 | 鐢ㄦ埛鐢诲儚銆佸亸濂芥爣绛俱€佹帹鑽愩€佹父鐜╂€荤粨鍜屽紑灞€寤鸿 |

椤甸潰缁嗚妭瑙?[src/pages/README.md](src/pages/README.md)銆?

## 瑙嗚瑙勮寖

- 鑳屾櫙浠ラ粦绾€佺偔鐏板拰鏃х焊鑹蹭负涓伙紝绾㈣壊鍙敤浜庡叧閿姸鎬佸拰涓昏鎿嶄綔銆?
- 鏍囬浣跨敤 `Cinzel Decorative`锛屾鏂囦娇鐢?`Crimson Pro`锛?
  鏁版嵁鏍囩浣跨敤 `JetBrains Mono`銆?
- 椤甸潰浣跨敤缁熶竴鐨?`StudioShell`銆丠ero銆佺粺璁￠潰鏉垮拰宸ヤ笟鍗＄墖銆?
- 鍗＄墖寮鸿皟杈规銆佸唴楂樺厜銆佹繁闃村奖鍜岃交搴︽瘺鐜荤拑锛屼笉浣跨敤绾壊骞抽摵銆?
- 妗岄潰绔彁渚涘畬鏁撮《閮ㄥ鑸紱绐勫睆閫氳繃椤甸潰鍐呭鑸繚鎸佷富瑕佽矾鐢卞彲杈俱€?

## 鏁版嵁鐘舵€?

褰撳墠鍥涗釜椤甸潰涓昏浣跨敤缁勪欢鍐呭畾涔夌殑婕旂ず鏁版嵁锛岀敤浜庨獙璇佷俊鎭灦鏋勫拰瑙嗚璁捐銆?
`src/api/`銆乣src/providers/` 鍜岀被鍨嬪眰浠嶇劧淇濈暀锛屼絾鏂扮増椤甸潰灏氭湭鍏ㄩ儴鎺ュ叆鐪熷疄 API銆?
鍥犳鎸夐挳銆佺瓫閫夊拰闈㈡澘鍒囨崲鍙互浜や簰锛屾敞鍐屻€佸尮閰嶃€佽亰澶╁拰鎸佷箙鍖栫瓑涓氬姟娴佺▼浠嶉渶鍚庣画瀵规帴銆?

## 鍙傝€冨伐绋?

`figma-make/` 鏄嫭绔?Vite 宸ョ▼锛屽彧鎵挎媴瑙嗚鍙傝€冨拰璁捐婧簮锛?

- 涓嶅湪 `src/` 鍐咃紝涓嶄細琚?CRA 鍜?TypeScript 涓诲伐绋嬫壂鎻忋€?
- 鏈夎嚜宸辩殑 `package.json`銆佸叆鍙ｃ€佹牱寮忓拰缁勪欢渚濊禆銆?
- 涓嶅簲浠庝富搴旂敤鐩存帴 import 鍏朵腑鐨勬簮鐮併€?
- 淇敼鍙傝€冨伐绋嬫椂锛屽簲鍦?`figma-make/` 鍐呭崟鐙畨瑁呬緷璧栧拰杩愯銆?

## 褰撳墠杩涘害

- [x] 淇 Mantine 鍏ㄥ眬鏍峰紡鍏ュ彛
- [x] 寤虹珛鏆楅粦宸ヤ笟鍓у満涓婚鍜屽叏灞€鏍峰紡
- [x] 寤虹珛鍥涗釜涓昏矾鐢卞強鍏变韩甯冨眬澹?
- [x] 瀹屾垚鍓ф湰搴撻潤鎬佷氦浜掑師鍨?
- [x] 瀹屾垚娓告垙鑸炲彴闈欐€佷氦浜掑師鍨?
- [x] 瀹屾垚 Agent 骞垮満闈欐€佷氦浜掑師鍨?
- [x] 瀹屾垚涓汉鍔╂墜闈欐€佷氦浜掑師鍨?
- [x] 灏?Figma Make 宸ョ▼闅旂鍒颁富搴旂敤婧愮爜鐩綍涔嬪
- [x] 澧炲姞娴忚鍣ㄥ吋瀹圭洰鏍囧拰 Windows 鍚姩鑴氭湰
- [x] 涓诲簲鐢ㄧ敓浜ф瀯寤洪€氳繃
- [ ] 灏嗛〉闈㈡紨绀烘暟鎹浛鎹负鍚庣鏁版嵁
- [ ] 瀹屾垚鑱婂ぉ銆佸尮閰嶃€佹敹钘忋€侀個璇峰拰澶嶇洏鎸佷箙鍖?
- [ ] 琛ュ厖椤甸潰绾ф祴璇曚笌绉诲姩绔瑙夊洖褰?

## 宸茬煡闄愬埗

- `npm start` 宸叉敼涓鸿法骞冲彴鍏煎锛堢洿鎺?`react-scripts start`锛夛紝涓嶅啀渚濊禆 Windows 涓撶敤璇硶
- 澶栭儴灏侀潰鍥剧墖鍜?Google Fonts 闇€瑕佺綉缁滆闂?
- `figma-make/` 鏈畨瑁呬緷璧栨椂鏃犳硶鐩存帴鎵ц `npm run dev` 鎴?`npm run build`
