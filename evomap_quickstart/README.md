# EvoMap 本地试水脚本

跑通 EvoMap 开发者门户的 OAuth2 + PKCE 全流程,验证你的应用凭证能正确换 token、能调到 `/developer/oauth/recipes`。

## 一次性准备

1. **去 [evomap.ai/dev/portal](https://evomap.ai/dev/portal) 注册应用**
   - 勾选 **test mode**(client id 会以 `evm_client_test_…` 开头,零真实副作用)
   - redirect URI 必须填:`http://localhost:3000/callback`
   - 申请 scope:`gene:read` / `recipe:read` / `reuse:query` / `recipe:write` / `openid` / `profile` / `email`(都是自助即用)
   - 拿到 `client_id` 和**一次性显示**的 `client_secret`(关掉页面就再也看不到了,务必当场存好)

2. **填本地凭证**
   ```bash
   cd evomap_quickstart
   cp .env.example .env
   # 编辑 .env,把 EVOMAP_CLIENT_ID 和 EVOMAP_CLIENT_SECRET 填进去
   ```

3. **装依赖**
   ```bash
   npm install
   ```

## 跑起来

```bash
npm start
```

控制台会输出 `Mode: TEST(沙箱 ...)` 和 `Listening on http://localhost:3000`。

浏览器打开 http://localhost:3000 → 点 **Connect with EvoMap** → 走完授权 → 回到 `/callback`,页面会显示:
- token 信息(脱敏)
- 最近 5 条 recipe 的 JSON

终端里会**打印一次完整 access_token**,可以拷出来用 curl 直接调:

```bash
curl "https://evomap.ai/developer/oauth/recipes?limit=5" \
  -H "Authorization: Bearer <粘贴这里>"
```

## 解锁 recipe:publish(后续)

`recipe:publish` 不是自助,需要在门户提交开发者资格申请。批准后:

1. 编辑 `index.js`,在 `SCOPE` 常量里加上 `recipe:publish`
2. 重启 `npm start`,重新走一遍授权

代码不需要其它改动。

## 切到 Live

把门户里的应用从 test mode 切到 live(或新注册一个 live 应用),把新的 `evm_client_live_…` 凭证填进 `.env`,重启即可。**代码完全一致**。

## 注意

- `.env` 已被 `.gitignore` 屏蔽,不会进版本控制 —— 但请你自己再核对一遍
- PKCE verifier 当前放在进程内存里,生产环境必须用 session 存储
- token 是机密 —— 不要写到日志、不要贴到聊天里
