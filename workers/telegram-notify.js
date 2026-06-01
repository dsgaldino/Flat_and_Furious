/**
 * Cloudflare Worker — Strava onboarding: Telegram + optional GitHub auto-auth.
 *
 * Secrets: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
 * Optional (auto-register): STRAVA_CLIENT_SECRET, GITHUB_DISPATCH_TOKEN
 * Optional: STRAVA_CLIENT_ID (default 160663), STRAVA_REDIRECT_URI, GITHUB_REPO
 *
 * POST JSON: { "confirm_url": "...", "code": "..." }
 */

const ALLOWED_ORIGINS = new Set(["https://dsgaldino.github.io"]);

const DEFAULT_CLIENT_ID = "160663";
const DEFAULT_REDIRECT_URI =
  "https://dsgaldino.github.io/Flat_and_Furious/strava/callback.html";
const DEFAULT_GITHUB_REPO = "dsgaldino/Flat_and_Furious";

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders(request) });
    }

    if (request.method === "GET") {
      return json(
        {
          ok: true,
          service: "flat-furious-notify",
          telegram_configured: Boolean(
            env.TELEGRAM_BOT_TOKEN && env.TELEGRAM_CHAT_ID,
          ),
          strava_auto: Boolean(env.STRAVA_CLIENT_SECRET),
          github_auto: Boolean(env.GITHUB_DISPATCH_TOKEN),
        },
        200,
        request,
      );
    }

    if (request.method !== "POST") {
      return json({ error: "POST only" }, 405, request);
    }

    const token = String(env.TELEGRAM_BOT_TOKEN || "").trim();
    const chatId = String(env.TELEGRAM_CHAT_ID || "").trim();
    if (!token || !chatId) {
      return json({ error: "Worker secrets not configured" }, 500, request);
    }
    if (!/^-?\d+$/.test(chatId)) {
      return json(
        { error: "TELEGRAM_CHAT_ID must be a numeric id from getUpdates" },
        500,
        request,
      );
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: "Invalid JSON" }, 400, request);
    }

    const confirmUrl = (body.confirm_url || body.url || "").trim();
    const code = (body.code || "").trim();

    const willAutoRegister = Boolean(
      env.GITHUB_DISPATCH_TOKEN && confirmUrl,
    );

    // OAuth code is single-use: if GitHub will exchange it, do not exchange here.
    let athleteName = null;
    let exchangeError = null;
    if (env.STRAVA_CLIENT_SECRET && !willAutoRegister) {
      const exchanged = await exchangeStravaCode(code, confirmUrl, env);
      if (exchanged.ok) {
        athleteName = exchanged.name;
      } else {
        exchangeError = exchanged.error;
      }
    }

    let githubResult = null;
    if (willAutoRegister) {
      githubResult = await triggerGithubAuth(confirmUrl, env);
    }

    const text = buildTelegramMessage({
      confirmUrl,
      athleteName,
      exchangeError,
      githubResult,
      autoEnabled: Boolean(env.GITHUB_DISPATCH_TOKEN),
    });

    const tgRes = await fetch(
      `https://api.telegram.org/bot${token}/sendMessage`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: chatId,
          text,
          disable_web_page_preview: true,
        }),
      },
    );

    const tgData = await tgRes.json();
    if (!tgRes.ok || !tgData.ok) {
      const hint =
        tgData?.description === "Unauthorized"
          ? "Check TELEGRAM_BOT_TOKEN"
          : tgData?.description === "Bad Request: chat not found"
            ? "Check TELEGRAM_CHAT_ID"
            : tgData?.description;
      return json(
        { error: "Telegram API failed", hint, detail: tgData },
        502,
        request,
      );
    }

    return json(
      {
        ok: true,
        athlete: athleteName,
        github_dispatch: githubResult?.ok ?? false,
      },
      200,
      request,
    );
  },
};

function buildTelegramMessage({
  confirmUrl,
  athleteName,
  exchangeError,
  githubResult,
  autoEnabled,
}) {
  const lines = ["🚴 Flat & Furious — novo atleta", ""];

  if (athleteName) {
    lines.push(`👤 ${athleteName}`);
    lines.push("");
  } else if (exchangeError) {
    lines.push(`⚠️ Strava: ${exchangeError}`);
    lines.push("");
  }

  if (githubResult?.ok) {
    lines.push("✅ Registro automático iniciado no GitHub.");
    lines.push(
      "Em ~1–2 min o token entra em data/tokens_athletes.csv (commit no repo).",
    );
    lines.push("(O nome do atleta aparece no log do workflow.)");
    lines.push("");
    lines.push(
      "Acompanhe: GitHub → Actions → Register Strava athlete",
    );
  } else if (autoEnabled && githubResult && !githubResult.ok) {
    lines.push(
      `⚠️ GitHub Actions não disparou (${githubResult.status}). Registre manualmente:`,
    );
    lines.push("");
    lines.push(`python -m flatfurious auth --code "${confirmUrl}"`);
  } else if (!autoEnabled) {
    lines.push("Registre no PC:");
    lines.push(`python -m flatfurious auth --code "${confirmUrl}"`);
  } else {
    lines.push(`python -m flatfurious auth --code "${confirmUrl}"`);
  }

  lines.push("");
  lines.push("🔗 URL:");
  lines.push(confirmUrl);

  return lines.join("\n");
}

async function exchangeStravaCode(code, confirmUrl, env) {
  const clientSecret = String(env.STRAVA_CLIENT_SECRET || "").trim();
  if (!clientSecret) {
    return { ok: false, error: "STRAVA_CLIENT_SECRET not set" };
  }

  let authCode = code;
  if (!authCode && confirmUrl) {
    try {
      authCode = new URL(confirmUrl).searchParams.get("code") || "";
    } catch {
      authCode = "";
    }
  }
  if (!authCode) {
    return { ok: false, error: "missing code" };
  }

  const clientId = String(env.STRAVA_CLIENT_ID || DEFAULT_CLIENT_ID).trim();
  const redirectUri = String(
    env.STRAVA_REDIRECT_URI || DEFAULT_REDIRECT_URI,
  ).trim();

  const form = new URLSearchParams({
    client_id: clientId,
    client_secret: clientSecret,
    code: authCode,
    grant_type: "authorization_code",
    redirect_uri: redirectUri,
  });
  const res = await fetch("https://www.strava.com/oauth/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form.toString(),
  });

  const data = await res.json();
  if (!res.ok) {
    const msg =
      data?.message || data?.error || `HTTP ${res.status}`;
    return { ok: false, error: msg };
  }

  const athlete = data.athlete || {};
  const first = athlete.firstname || "";
  const last = athlete.lastname || "";
  const name = `${first} ${last}`.trim() || athlete.username || "Atleta";

  return { ok: true, name, data };
}

async function triggerGithubAuth(confirmUrl, env) {
  const ghToken = String(env.GITHUB_DISPATCH_TOKEN || "").trim();
  const repo = String(env.GITHUB_REPO || DEFAULT_GITHUB_REPO).trim();
  if (!ghToken) {
    return { ok: false, status: 0, reason: "no token" };
  }

  const [owner, repoName] = repo.split("/");
  if (!owner || !repoName) {
    return { ok: false, status: 0, reason: "invalid GITHUB_REPO" };
  }

  const res = await fetch(
    `https://api.github.com/repos/${owner}/${repoName}/dispatches`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${ghToken}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
        "User-Agent": "flat-furious-notify-worker",
      },
      body: JSON.stringify({
        event_type: "strava_auth",
        client_payload: { auth_code: confirmUrl },
      }),
    },
  );

  return { ok: res.ok || res.status === 204, status: res.status };
}

function corsHeaders(request) {
  const origin = request.headers.get("Origin") || "";
  const allowOrigin = ALLOWED_ORIGINS.has(origin)
    ? origin
    : ALLOWED_ORIGINS.values().next().value;
  return {
    "Access-Control-Allow-Origin": allowOrigin,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
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
