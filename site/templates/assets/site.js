/** Shared site utilities — nav, paths, Strava onboarding. */
const FLAT_FURIOUS_JOIN = {
  CLIENT_ID: "160663",
  SCOPE: "read,activity:read_all,profile:read_all",
  TELEGRAM_NOTIFY_WEBHOOK: "https://flat-furious-notify.dsgaldino.workers.dev",
};

function siteRoot() {
  const path = window.location.pathname;
  const archiveIdx = path.indexOf("/archive/");
  if (archiveIdx !== -1) {
    return path.slice(0, archiveIdx + 1);
  }
  const stravaIdx = path.indexOf("/strava/");
  if (stravaIdx !== -1) {
    return path.slice(0, stravaIdx + 1);
  }
  const idx = path.lastIndexOf("/");
  if (idx <= 0) return "/";
  return path.slice(0, idx + 1);
}

function assetPath(name) {
  const root = siteRoot();
  return `${root}assets/${name}`;
}

function pagePath(page) {
  const root = siteRoot();
  return `${root}${page}`;
}

function initSiteNav(activePage) {
  const root = siteRoot();
  const header = document.getElementById("site-header");
  if (!header) return;

  const pages = [
    { id: "home", label: "In\u00edcio", href: pagePath("index.html") },
    { id: "reports", label: "Relat\u00f3rios", href: pagePath("archive/") },
    { id: "join", label: "Entrar no grupo", href: pagePath("join.html") },
  ];

  const navLinks = pages
    .map(
      (p) =>
        `<a href="${p.href}" class="${p.id === activePage ? "active" : ""}">${p.label}</a>`
    )
    .join("");

  header.innerHTML = `
    <div class="site-header-inner">
      <a class="site-brand" href="${pagePath("index.html")}">
        <img class="site-brand-logo" src="${assetPath("logo-primary.svg")}" alt="Flat and Furious" width="88" height="88">
        <p class="site-brand-title">Flat &amp; Furious</p>
        <p class="site-brand-sub">Enschede</p>
        <div class="site-brand-flags">
          <img src="${assetPath("flags-br-nl.svg")}" alt="Brasil e Pa\u00edses Baixos" width="56" height="20">
        </div>
      </a>
      <p class="site-tagline">Private Club &middot; Cycling</p>
      <nav class="site-nav" aria-label="Principal">${navLinks}</nav>
    </div>`;
}

function initSiteFooter() {
  const footer = document.getElementById("site-footer");
  if (!footer) return;

  footer.innerHTML = `
    <div class="site-footer-inner">
      <img class="wave-divider" src="${assetPath("waves.svg")}" alt="" width="200" height="24">
      <div class="site-footer-gelato">
        <img src="${assetPath("icon-gelato.svg")}" alt="" width="24" height="24">
        <span>Toda pedalada termina no Paulinho</span>
      </div>
      <div class="site-footer-flags">
        <img src="${assetPath("flags-br-nl.svg")}" alt="Brasil e Pa\u00edses Baixos" width="56" height="20">
      </div>
      <p>Enschede, Overijssel &middot; Netherlands</p>
      <p><a href="${pagePath("join.html")}">Entrar no grupo</a> &middot; <a href="${pagePath("archive/")}">Relat\u00f3rios</a></p>
      <p class="muted">Dados via Strava</p>
    </div>`;
}

function stravaCallbackUri() {
  const root = siteRoot();
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

function telegramShareUrl(text) {
  return `https://t.me/share/url?url=${encodeURIComponent(text)}`;
}

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

function copyWhatsApp() {
  const el = document.getElementById("whatsapp-text");
  if (!el) return;
  navigator.clipboard.writeText(el.innerText).then(function () {
    const btn = document.querySelector(".copy-btn");
    if (btn) {
      const orig = btn.textContent;
      btn.textContent = "Copiado!";
      setTimeout(function () {
        btn.textContent = orig;
      }, 2000);
    }
  });
}

document.addEventListener("DOMContentLoaded", function () {
  const body = document.body;
  const active = body.dataset.activePage;
  if (active) {
    initSiteNav(active);
    initSiteFooter();
  }
});
