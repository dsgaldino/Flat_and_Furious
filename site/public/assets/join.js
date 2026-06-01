/** Shared config for Strava onboarding pages (GitHub Pages). */
const FLAT_FURIOUS_JOIN = {
  CLIENT_ID: "160663",
  SCOPE: "read,activity:read_all,profile:read_all",
  /** Optional: country code + number, no + or spaces (e.g. 31612345678). Empty = pick contact in WhatsApp. */
  ADMIN_WHATSAPP: "",
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

function whatsAppShareUrl(text) {
  const encoded = encodeURIComponent(text);
  const phone = FLAT_FURIOUS_JOIN.ADMIN_WHATSAPP;
  if (phone) {
    return `https://wa.me/${phone}?text=${encoded}`;
  }
  return `https://wa.me/?text=${encoded}`;
}
