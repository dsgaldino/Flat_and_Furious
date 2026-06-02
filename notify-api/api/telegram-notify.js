/**
 * Vercel serverless — Telegram notify (fallback when workers.dev SSL fails).
 * Env: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID (Vercel project settings)
 */

const ALLOWED_ORIGIN = "https://dsgaldino.github.io";

function cors(res) {
  res.setHeader("Access-Control-Allow-Origin", ALLOWED_ORIGIN);
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
}

export default async function handler(req, res) {
  cors(res);

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }

  if (req.method === "GET") {
    const token = process.env.TELEGRAM_BOT_TOKEN;
    const chatId = process.env.TELEGRAM_CHAT_ID;
    return res.status(200).json({
      ok: true,
      service: "flat-furious-notify",
      platform: "vercel",
      telegram_configured: Boolean(token && chatId),
    });
  }

  if (req.method !== "POST") {
    return res.status(405).json({ error: "POST only" });
  }

  const token = String(process.env.TELEGRAM_BOT_TOKEN || "").trim();
  const chatId = String(process.env.TELEGRAM_CHAT_ID || "").trim();
  if (!token || !chatId) {
    return res.status(500).json({ error: "TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set in Vercel" });
  }
  if (!/^-?\d+$/.test(chatId)) {
    return res.status(500).json({ error: "TELEGRAM_CHAT_ID must be numeric (from getUpdates)" });
  }

  const body = typeof req.body === "string" ? JSON.parse(req.body) : req.body || {};
  const confirmUrl = body.confirm_url || body.url || "";
  const code = body.code || "";
  const text = [
    "Novo atleta — Flat & Furious",
    "",
    "Autorizou no Strava. Registre com:",
    'python -m flatfurious auth --code "URL"',
    "",
    confirmUrl || `code: ${code}`,
  ].join("\n");

  const tgRes = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
      text,
      disable_web_page_preview: true,
    }),
  });
  const tgData = await tgRes.json();
  if (!tgRes.ok || !tgData.ok) {
    return res.status(502).json({
      error: "Telegram API failed",
      hint: tgData?.description,
      detail: tgData,
    });
  }

  return res.status(200).json({ ok: true });
}
