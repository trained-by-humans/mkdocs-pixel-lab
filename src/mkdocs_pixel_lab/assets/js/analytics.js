(() => {
  const config = document.currentScript;
  const measurementId = config?.dataset.measurementId;
  if (!/^G-[A-Z0-9]+$/.test(measurementId ?? "")) return;

  // Never collect from mkdocs serve, forks, or previews on another hostname.
  let site;
  try {
    site = new URL(config.dataset.siteUrl);
  } catch {
    return;
  }
  if (site.protocol !== "https:" || window.location.protocol !== "https:" ||
      window.location.hostname !== site.hostname) return;
  if (["localhost", "127.0.0.1", "[::1]"].includes(site.hostname) ||
      site.hostname.endsWith(".localhost")) return;

  const banner = document.querySelector("#analytics-consent");
  const settings = document.querySelector("#analytics-settings");
  const accept = document.querySelector("#analytics-accept");
  const decline = document.querySelector("#analytics-decline");
  if (!banner || !settings || !accept || !decline) return;

  // Sharing is explicit: never guess a registrable domain on a multi-tenant host.
  const consentDomain = (config.dataset.consentDomain ?? "").trim().toLowerCase().replace(/^\./, "");
  if (consentDomain && (
    consentDomain.length > 253 || !consentDomain.includes(".") ||
    consentDomain.split(".").some(label => !/^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/.test(label)) ||
    consentDomain === "github.io" ||
    !(site.hostname === consentDomain || site.hostname.endsWith(`.${consentDomain}`))
  )) return;

  const preferenceKey = `pixel-lab-analytics:${measurementId}:${site.origin}${site.pathname}`;
  const cookieName = `pixel-lab-analytics-${measurementId}`;
  const validChoice = (value) => ["granted", "denied"].includes(value) ? value : null;
  const readPreference = () => {
    try {
      if (consentDomain) {
        const cookie = document.cookie.split(";").map(value => value.trim())
          .find(value => value.startsWith(`${cookieName}=`));
        return validChoice(cookie?.slice(cookieName.length + 1));
      }
      return validChoice(window.localStorage.getItem(preferenceKey));
    } catch {
      return null; // Blocked storage never implies consent.
    }
  };
  const savePreference = (choice) => {
    try {
      if (consentDomain) {
        document.cookie = `${cookieName}=${choice}; Domain=${consentDomain}; Path=/; Max-Age=15552000; Secure; SameSite=Lax`;
      } else {
        window.localStorage.setItem(preferenceKey, choice);
      }
    } catch {
      // The choice still applies to this page when it cannot be persisted.
    }
  };
  let started = false;
  let preference = readPreference();
  let savedPreference = preference;

  const startAnalytics = () => {
    if (started) return;
    started = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag("consent", "default", {
      analytics_storage: "denied",
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied",
    });
    window.gtag("consent", "update", { analytics_storage: "granted" });
    window.gtag("js", new Date());
    // Documentation headings update the URL fragment; do not count them as pages.
    const cleanUrl = (value) => {
      try {
        const url = new URL(value);
        return `${url.origin}${url.pathname}`;
      } catch {
        return "";
      }
    };
    window.gtag("config", measurementId, {
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
      page_location: cleanUrl(window.location.href),
      page_referrer: cleanUrl(document.referrer),
      cookie_domain: window.location.hostname,
    });
    const tag = document.createElement("script");
    tag.async = true;
    tag.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(measurementId)}`;
    document.head.appendChild(tag);
  };

  const applyPreference = (choice) => {
    preference = choice;
    banner.hidden = choice !== null;
    if (choice === "granted") startAnalytics();
    else if (started) {
      // Disable collection immediately and unload the previously accepted tag.
      window[`ga-disable-${measurementId}`] = true;
      window.gtag("consent", "update", { analytics_storage: "denied" });
      try {
        for (const name of ["_ga", `_ga_${measurementId.slice(2)}`]) {
          document.cookie = `${name}=; Max-Age=0; Path=/`;
          document.cookie = `${name}=; Max-Age=0; Path=/; Domain=${window.location.hostname}`;
        }
      } catch {
        // Unload the tag even if the browser refuses cookie access.
      }
      window.location.reload();
    }
  };
  const choose = (choice) => {
    savePreference(choice);
    savedPreference = readPreference();
    applyPreference(choice);
    settings.focus({ preventScroll: true });
  };
  const syncPreference = () => {
    const choice = readPreference();
    if (choice === savedPreference) return;
    savedPreference = choice;
    applyPreference(choice);
  };

  accept.addEventListener("click", () => choose("granted"));
  decline.addEventListener("click", () => choose("denied"));
  settings.addEventListener("click", () => {
    syncPreference();
    banner.hidden = false;
    (preference === "granted" ? decline : accept).focus({ preventScroll: true });
  });
  // Cookies have no broadly supported change event; synchronize open sites too.
  if (consentDomain) window.setInterval(syncPreference, 2000);
  else window.addEventListener("storage", (event) => {
    if (event.key === preferenceKey || event.key === null) syncPreference();
  });
  window.addEventListener("focus", syncPreference);
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) syncPreference();
  });
  settings.hidden = false;
  if (preference === "granted") startAnalytics();
  else if (preference !== "denied") banner.hidden = false;
})();
