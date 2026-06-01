/**
 * Cloudflare Worker — notifies admin on Telegram when an athlete authorizes Strava.
 *
 * Deploy: wrangler deploy (set secrets TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
 * Then set FLAT_FURIOUS_JOIN.TELEGRAM_NOTIFY_WEBHOOK in site/public/assets/join.js
 *
 * POST JSON: { "confirm_url": "...", "code": "..." }
 */

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: corsHeaders(request),
      });
    }

    if (request.method !== "POST") {
      return json({ error: "POST only" }, 405, request);
    }

    const token = env.TELEGRAM_BOT_TOKEN;
    const chatId = env.TELEGRAM_CHAT_ID;
    if (!token || !chatId) {
      return json({ error: "Worker secrets not configured" }, 500, request);
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: "Invalid JSON" }, 400, request);
    }

    const confirmUrl = body.confirm_url || body.url || "";
    const code = body.code || "";
    const text = [
      "🚴 Novo atleta — Flat & Furious",
      "",
      "Autorizou no Strava. Registre com:",
      "`python -m flatfurious auth --code \"URL\"`",
      "",
      confirmUrl || `(code: ${code})`,
    ].join("\n");

    const tgUrl = `https://api.telegram.org/bot${token}/sendMessage`;
    const tgRes = await fetch(tgUrl, {
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
      return json({ error: "Telegram API failed", detail: tgData }, 502, request);
    }

    return json({ ok: true }, 200, request);
  },
};

function corsHeaders(request) {
  const origin = request.headers.get("Origin") || "*";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

function json(data, status, request) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders(request),
    },
  });
}
