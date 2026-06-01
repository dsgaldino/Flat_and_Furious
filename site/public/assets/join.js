/** Shared config for Strava onboarding (GitHub Pages). */
const FLAT_FURIOUS_JOIN = {
  CLIENT_ID: "160663",
  SCOPE: "read,activity:read_all,profile:read_all",
  /**
   * Cloudflare Worker URL after deploy (see docs/TELEGRAM_ONBOARDING.md).
   * Example: "https://flat-furious-notify.SEU_SUBDOMINIO.workers.dev"
   * Leave empty to only show copy / manual Telegram share.
   */
  TELEGRAM_NOTIFY_WEBHOOK: "",
};

function repoBasePath() {
  const path = window.location.pathname;
  const idx = path.lastIndexOf("/");
  if (idx <= 0) return "/";
  return path.slice(0, idx + 1);
}

function stravaCallbackUri() {
  const base = repoBasePath();
  const root = base.replace(/strava\/.*$/, "").replace(/join\.html.*$/, "");
  const normalized = root.endsWith("/") ? root : root + "/";
  return `${window.location.origin}${normalized}strava/callback.html`;
}

function stravaAuthorizeUrl() {
  const params = new URLSearchParams({
    client_id: FLAT_FURIOUS_JOIN.CLIENT_ID,
    response_type: "code",
    redirect_uri: stravaCallbackUri(),
    approval_prompt: "force",
    scope: FLAT_FURIOUS_JOIN.SCOPE,
  });
  return `https://www.strava.com/oauth/authorize?${params.toString()}`;
}

/** Fallback: open Telegram with pre-filled message (semi-auto). */
function telegramShareUrl(text) {
  return `https://t.me/share/url?url=${encodeURIComponent(text)}`;
}

/**
 * Notify admin via Cloudflare Worker (token stays on server).
 * @returns {Promise<{ok: boolean, auto: boolean, message?: string}>}
 */
async function notifyAdminTelegram(confirmUrl, code) {
  const webhook = (FLAT_FURIOUS_JOIN.TELEGRAM_NOTIFY_WEBHOOK || "").trim();
  if (!webhook) {
    return { ok: false, auto: false };
  }

  try {
    const res = await fetch(webhook, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ confirm_url: confirmUrl, code }),
    });
    if (res.ok) {
      return { ok: true, auto: true };
    }
    const err = await res.text();
    return { ok: false, auto: true, message: err };
  } catch (e) {
    return { ok: false, auto: true, message: String(e) };
  }
}
