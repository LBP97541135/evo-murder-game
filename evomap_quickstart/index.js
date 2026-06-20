// EvoMap 本地试水脚本 —— OAuth2 + PKCE 全流程,零 SDK,只用裸 fetch。
// 改编自 EvoMap/developers/examples/quickstart(MIT)。
//
// 用法:
//   1. 在 https://evomap.ai/dev/portal 注册 test_mode 应用,
//      redirect URI 必须填 http://localhost:3000/callback
//   2. cp .env.example .env 并填好 EVOMAP_CLIENT_ID / EVOMAP_CLIENT_SECRET
//   3. npm install
//   4. npm start  → 浏览器打开 http://localhost:3000  → "Connect with EvoMap"
//
// 教学示例:PKCE verifier 暂存在内存(按 state 索引)。生产请放 session。

import express from "express";
import rateLimit from "express-rate-limit";
import crypto from "node:crypto";

const CLIENT_ID = process.env.EVOMAP_CLIENT_ID;
const CLIENT_SECRET = process.env.EVOMAP_CLIENT_SECRET; // 公共/PKCE-only 客户端可不填
const BASE = process.env.EVOMAP_BASE || "https://evomap.ai";
const REDIRECT_URI = "http://localhost:3000/callback";
// 自助 scope —— gene:read / recipe:read / reuse:query / recipe:write / openid + 身份。
// 等门户批准 recipe:publish 后,把它加到这个字符串里即可。
const SCOPE = "gene:read recipe:read reuse:query recipe:write openid profile email";
const FETCH_TIMEOUT_MS = 10_000;

const app = express();
app.use(rateLimit({ windowMs: 60_000, max: 60 }));
const pending = new Map(); // state -> code_verifier(demo)
const b64url = (buf) => buf.toString("base64url");

app.get("/", (_req, res) => {
  res.type("html").send(`
    <h1>EvoMap quickstart</h1>
    <p>Multi_Agents_Company 本地试水</p>
    <a href="/login">Connect with EvoMap →</a>
  `);
});

// 1. PKCE:构造 authorize URL,把 verifier 按 state 暂存。
app.get("/login", (_req, res) => {
  const verifier = b64url(crypto.randomBytes(32));
  const challenge = b64url(crypto.createHash("sha256").update(verifier).digest());
  const state = b64url(crypto.randomBytes(16));
  pending.set(state, verifier);
  const url =
    `${BASE}/oauth/authorize?` +
    new URLSearchParams({
      response_type: "code",
      client_id: CLIENT_ID,
      redirect_uri: REDIRECT_URI,
      scope: SCOPE,
      code_challenge: challenge,
      code_challenge_method: "S256",
      state,
    });
  res.redirect(url);
});

app.get("/callback", async (req, res, next) => {
  try {
    const { code, state } = req.query;
    const verifier = pending.get(state);
    if (!code || !verifier) return res.status(400).send("Missing code or unknown state.");
    pending.delete(state);

    // 2. 用 code 换 token(urlencoded body)
    const tokenRes = await fetch(`${BASE}/oauth/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "authorization_code",
        code: String(code),
        client_id: CLIENT_ID,
        ...(CLIENT_SECRET ? { client_secret: CLIENT_SECRET } : {}),
        redirect_uri: REDIRECT_URI,
        code_verifier: verifier,
      }),
      signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
    });
    const tokens = await tokenRes.json().catch(() => null);
    if (!tokenRes.ok || !tokens?.access_token) {
      return res
        .status(tokenRes.ok ? 502 : tokenRes.status)
        .json({ error: "token_exchange_failed", upstream: tokens });
    }

    console.log("✅ access_token 已拿到(脱敏在浏览器响应里)。完整 token 仅打印一次便于调试:");
    console.log("   access_token =", tokens.access_token);
    if (tokens.refresh_token) console.log("   refresh_token =", tokens.refresh_token);

    // 3. 用 token 调一次 API 验证打通 —— 读最近 5 条 recipe
    const apiRes = await fetch(`${BASE}/developer/oauth/recipes?limit=5`, {
      headers: { Authorization: `Bearer ${tokens.access_token}` },
      signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
    });
    const recipes = await apiRes.json().catch(() => null);
    if (!apiRes.ok) {
      return res.status(apiRes.status).json({ error: "evomap_api_error", upstream: recipes });
    }

    res.json({
      mode: CLIENT_ID.startsWith("evm_client_test_") ? "test" : "live",
      tokens: {
        ...tokens,
        access_token: "***",
        refresh_token: tokens.refresh_token ? "***" : undefined,
      },
      recipes,
    });
  } catch (err) {
    next(err);
  }
});

// 4. Webhook 接收端(可选)—— 用 raw body 做 HMAC-SHA256 验签
app.post(
  "/webhooks/evomap",
  express.raw({ type: "application/json" }),
  (req, res) => {
    if (
      !verifyWebhook(
        req.body,
        req.get("X-EvoMap-Webhook-Signature"),
        process.env.EVOMAP_WEBHOOK_SECRET
      )
    ) {
      return res.status(400).send("bad signature");
    }
    const event = JSON.parse(req.body.toString("utf8"));
    console.log("webhook received:", {
      type: event.type,
      livemode: event.livemode,
      data: event.data,
    });
    res.sendStatus(200);
  }
);

function verifyWebhook(rawBody, header, secret, toleranceSec = 300) {
  if (!secret || !header) return false;
  const parts = Object.fromEntries(
    String(header).split(",").map((p) => {
      const i = p.indexOf("=");
      return i > 0 ? [p.slice(0, i).trim(), p.slice(i + 1).trim()] : [p, ""];
    })
  );
  if (!parts.t || !parts.v1) return false;
  const body = Buffer.isBuffer(rawBody) ? rawBody.toString("utf8") : String(rawBody);
  const expected = crypto
    .createHmac("sha256", secret)
    .update(`${parts.t}.${body}`)
    .digest("hex");
  const a = Buffer.from(parts.v1, "hex");
  const b = Buffer.from(expected, "hex");
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return false;
  const skew = Math.abs(Math.floor(Date.now() / 1000) - Number(parts.t));
  return Number.isFinite(skew) && skew <= toleranceSec;
}

app.use((err, _req, res, _next) => {
  console.error("unhandled error:", err?.message || err);
  if (!res.headersSent) res.status(500).json({ error: "internal_error" });
});

if (!CLIENT_ID) {
  console.error("❌ 未设置 EVOMAP_CLIENT_ID —— 请先复制 .env.example 为 .env 并填好。");
  process.exit(1);
}
const isTest = CLIENT_ID.startsWith("evm_client_test_");
console.log(`Mode: ${isTest ? "TEST(沙箱 — 零真实副作用)" : "LIVE"}`);
app.listen(3000, () =>
  console.log("Listening on http://localhost:3000 —— 浏览器打开它,点 Connect")
);
