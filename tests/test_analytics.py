"""GA4 is optional, production-only, and must not load before visitor consent."""

from __future__ import annotations

import mimetypes
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from mkdocs.commands.build import build
from mkdocs.config import load_config
from playwright.sync_api import expect


FIXTURE = Path(__file__).parent / "fixture_site" / "mkdocs.yml"
ORIGIN = "https://docs.example.invalid"
MEASUREMENT_ID = "G-TEST123456"
PREFERENCE_KEY = f"pixel-lab-analytics:{MEASUREMENT_ID}:{ORIGIN}/"
ANALYTICS = {
    "provider": "google",
    "measurement_id": MEASUREMENT_ID,
    "privacy_policy": "/privacy/",
}


@pytest.fixture(scope="session")
def analytics_site(tmp_path_factory):
    destination = tmp_path_factory.mktemp("analytics-site")
    config = load_config(
        config_file=str(FIXTURE),
        site_dir=str(destination),
        site_url=f"{ORIGIN}/",
        extra={"analytics": ANALYTICS},
    )
    build(config)
    return destination


@pytest.fixture()
def analytics_browser(page, analytics_site):
    """Serve the built fixture at a pretend production origin; mock all Google IO."""
    google_requests = []

    def respond(route):
        url = urlsplit(route.request.url)
        if url.hostname in {"www.googletagmanager.com", "www.google-analytics.com"}:
            google_requests.append(route.request.url)
            route.fulfill(status=200, content_type="application/javascript", body="")
        elif url.hostname in {"docs.example.invalid", "preview.example.invalid", "localhost"}:
            path = analytics_site / url.path.lstrip("/")
            if path.is_dir():
                path = path / "index.html"
            if path.is_file():
                route.fulfill(
                    status=200,
                    content_type=mimetypes.guess_type(str(path))[0] or "text/plain",
                    body=path.read_bytes(),
                )
            else:
                route.fulfill(status=404, body="Not found")
        else:
            route.abort()

    page.route("**/*", respond)
    return page, google_requests


@pytest.fixture()
def consent_sites(page, tmp_path):
    """Build multiple sites and mock their HTTPS hosts in one browser context."""
    sites = {}
    google_requests = []

    def add_site(url, consent_domain=None, measurement_id=MEASUREMENT_ID):
        analytics = {**ANALYTICS, "measurement_id": measurement_id}
        if consent_domain is not None:
            analytics["consent_domain"] = consent_domain
        destination = tmp_path / str(len(sites))
        config = load_config(
            config_file=str(FIXTURE), site_dir=str(destination), site_url=url,
            extra={"analytics": analytics},
        )
        build(config)
        sites[url] = destination

    def respond(route):
        url = urlsplit(route.request.url)
        if url.hostname in {"www.googletagmanager.com", "www.google-analytics.com"}:
            google_requests.append(route.request.url)
            route.fulfill(status=200, content_type="application/javascript", body="")
            return
        for origin, destination in sites.items():
            root = urlsplit(origin)
            if url.scheme != root.scheme or url.netloc != root.netloc or not url.path.startswith(root.path):
                continue
            path = destination / url.path[len(root.path):]
            if path.is_dir():
                path /= "index.html"
            if path.is_file():
                route.fulfill(
                    status=200, content_type=mimetypes.guess_type(str(path))[0] or "text/plain",
                    body=path.read_bytes(),
                )
            else:
                route.fulfill(status=404, body="Not found")
            return
        route.abort()

    page.context.route("**/*", respond)
    return add_site, google_requests


@pytest.mark.parametrize("analytics", [None, {}, {**ANALYTICS, "enabled": False}, {"provider": "other"}, {"provider": "google"}, {"provider": "google", "measurement_id": MEASUREMENT_ID}])
def test_unconfigured_or_disabled_analytics(tmp_path, analytics):
    extra = {} if analytics is None else {"analytics": analytics}
    config = load_config(
        config_file=str(FIXTURE), site_dir=str(tmp_path), extra=extra,
    )
    build(config)
    html = (tmp_path / "index.html").read_text()
    assert 'id="analytics-consent"' not in html
    assert 'id="analytics-settings"' not in html
    assert 'src="assets/js/analytics.js"' not in html


def test_rejection_and_later_acceptance(analytics_browser):
    page, google_requests = analytics_browser
    page.goto(ORIGIN)
    expect(page.get_by_role("region", name="Analytics preferences")).to_be_visible()
    expect(page.locator("#analytics-consent").get_by_role("link", name="Privacy policy")).to_have_attribute("href", "/privacy/")
    expect(page.locator(".footer .privacy-policy")).to_have_attribute("href", "/privacy/")
    assert google_requests == []
    assert page.evaluate("typeof window.gtag") == "undefined"

    page.get_by_role("button", name="Decline", exact=True).click()
    page.reload()
    expect(page.locator("#analytics-consent")).to_be_hidden()
    assert google_requests == []
    assert page.evaluate("key => localStorage.getItem(key)", PREFERENCE_KEY) == "denied"
    expect(page.locator(".footer .privacy-policy")).to_be_visible()

    page.get_by_role("button", name="Analytics settings").click()
    expect(page.get_by_role("button", name="Allow analytics", exact=True)).to_be_focused()
    page.get_by_role("button", name="Allow analytics", exact=True).click()
    page.wait_for_load_state("networkidle")
    assert len(google_requests) == 1
    assert google_requests[0].endswith(f"gtag/js?id={MEASUREMENT_ID}")


def test_acceptance_config_persistence_and_withdrawal(analytics_browser):
    page, google_requests = analytics_browser
    page.goto(f"{ORIGIN}/?private-value=secret#section")
    page.get_by_role("button", name="Allow analytics", exact=True).click()
    page.wait_for_load_state("networkidle")
    commands = page.evaluate("window.dataLayer.map(command => Array.from(command))")
    assert commands[0][0:2] == ["consent", "default"]
    assert set(commands[0][2].values()) == {"denied"}
    assert commands[1] == ["consent", "update", {"analytics_storage": "granted"}]
    assert commands[-1][0:2] == ["config", MEASUREMENT_ID]
    options = commands[-1][2]
    assert options["page_location"] == f"{ORIGIN}/"
    assert options["allow_google_signals"] is False
    assert options["allow_ad_personalization_signals"] is False
    assert options["cookie_domain"] == "docs.example.invalid"
    assert len(google_requests) == 1

    page.reload()
    page.wait_for_load_state("networkidle")
    expect(page.locator("#analytics-consent")).to_be_hidden()
    assert len(google_requests) == 2
    page.evaluate("document.cookie = '_ga=test; Path=/'; document.cookie = '_ga_TEST123456=test; Path=/';")
    page.get_by_role("button", name="Analytics settings").click()
    expect(page.get_by_role("button", name="Decline", exact=True)).to_be_focused()
    with page.expect_navigation():
        page.get_by_role("button", name="Decline", exact=True).click()
    expect(page.locator("#analytics-consent")).to_be_hidden()
    assert len(google_requests) == 2
    assert page.evaluate("typeof window.gtag") == "undefined"
    assert "_ga" not in page.evaluate("document.cookie")


@pytest.mark.parametrize("origin", ["http://localhost", "https://preview.example.invalid"])
def test_local_and_alternate_host_previews_are_disabled(analytics_browser, origin):
    page, google_requests = analytics_browser
    page.goto(origin)
    expect(page.locator("#analytics-consent")).to_be_hidden()
    expect(page.locator("#analytics-settings")).to_be_hidden()
    assert google_requests == []
    assert page.evaluate("typeof window.gtag") == "undefined"


@pytest.mark.parametrize("measurement_id", ["UA-12345-1", "GTM-12345", "G-XXXXXXXXXX<script>"])
def test_invalid_measurement_ids_fail_closed(analytics_browser, analytics_site, measurement_id):
    page, google_requests = analytics_browser
    html = (analytics_site / "index.html").read_text().replace(MEASUREMENT_ID, measurement_id)
    page.route(f"{ORIGIN}/", lambda route: route.fulfill(content_type="text/html", body=html))
    page.goto(ORIGIN)
    expect(page.locator("#analytics-consent")).to_be_hidden()
    expect(page.locator("#analytics-settings")).to_be_hidden()
    assert google_requests == []
    assert page.evaluate("typeof window.gtag") == "undefined"


def test_storage_unavailable_still_requires_opt_in(analytics_browser):
    page, google_requests = analytics_browser
    page.add_init_script("""
        Storage.prototype.getItem = () => { throw new Error('Storage blocked'); };
        Storage.prototype.setItem = () => { throw new Error('Storage blocked'); };
    """)
    page.goto(ORIGIN)
    expect(page.locator("#analytics-consent")).to_be_visible()
    assert google_requests == []
    page.get_by_role("button", name="Allow analytics", exact=True).click()
    page.wait_for_load_state("networkidle")
    assert len(google_requests) == 1
    page.reload()
    expect(page.locator("#analytics-consent")).to_be_visible()
    assert len(google_requests) == 1

    page.get_by_role("button", name="Allow analytics", exact=True).click()
    page.wait_for_load_state("networkidle")
    assert len(google_requests) == 2
    page.get_by_role("button", name="Analytics settings").click()
    with page.expect_navigation():
        page.get_by_role("button", name="Decline", exact=True).click()
    assert page.evaluate("typeof window.gtag") == "undefined"
    assert len(google_requests) == 2


def test_consent_banner_fits_mobile(analytics_browser):
    page, _ = analytics_browser
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(ORIGIN)
    banner = page.locator("#analytics-consent").bounding_box()
    assert banner is not None
    assert banner["x"] >= 0
    assert banner["x"] + banner["width"] <= 390
    assert banner["y"] >= 0
    assert banner["y"] + banner["height"] <= 844
    expect(page.locator(".analytics-consent__actions button")).to_have_text(["Allow analytics", "Decline"])
    for name in ["Allow analytics", "Decline"]:
        expect(page.get_by_role("button", name=name, exact=True)).to_be_visible()


@pytest.mark.parametrize("width", [1280, 390, 280])
def test_consent_actions_right_aligned(analytics_browser, width):
    page, google_requests = analytics_browser
    page.set_viewport_size({"width": width, "height": 844})
    page.goto(ORIGIN)
    actions = page.locator(".analytics-consent__actions")
    expect(actions).to_have_css("justify-content", "flex-end")
    expect(actions.locator("button")).to_have_text(["Allow analytics", "Decline"])
    group = actions.bounding_box()
    allow = page.get_by_role("button", name="Allow analytics", exact=True).bounding_box()
    decline = page.get_by_role("button", name="Decline", exact=True).bounding_box()
    assert group is not None and allow is not None and decline is not None
    assert decline["x"] + decline["width"] == pytest.approx(group["x"] + group["width"], abs=1)
    for button in [allow, decline]:
        assert button["x"] >= group["x"]
        assert button["x"] + button["width"] <= group["x"] + group["width"] + 1
    if allow["y"] == decline["y"]:
        assert allow["x"] + allow["width"] < decline["x"]
    else:
        assert allow["y"] + allow["height"] < decline["y"]
    assert not google_requests


def test_accept_button_uses_theme_palette(analytics_browser):
    page, _ = analytics_browser
    page.goto(ORIGIN)
    expect(page.locator(".analytics-consent__actions button")).to_have_text(["Allow analytics", "Decline"])
    accept = page.get_by_role("button", name="Allow analytics", exact=True)
    decline = page.get_by_role("button", name="Decline", exact=True)
    expect(accept).to_have_css("background-color", "rgb(76, 175, 80)")
    expect(accept).to_have_css("color", "rgb(16, 20, 16)")
    expect(decline).to_have_css("background-color", "rgb(232, 228, 207)")
    for property_name in ["font-size", "padding", "border-width"]:
        assert accept.evaluate("(el, property) => getComputedStyle(el).getPropertyValue(property)", property_name) == decline.evaluate(
            "(el, property) => getComputedStyle(el).getPropertyValue(property)", property_name
        )
    accept.hover()
    expect(accept).to_have_css("background-color", "rgb(76, 175, 80)")
    expect(accept).to_have_css("color", "rgb(16, 20, 16)")
    page.evaluate("""
        const palette = document.documentElement.style;
        palette.setProperty('--header-background', '#8315F9');
        palette.setProperty('--accent-foreground', '#FFFFFF');
    """)
    expect(accept).to_have_css("background-color", "rgb(131, 21, 249)")
    expect(accept).to_have_css("color", "rgb(255, 255, 255)")
    expect(page.locator('.header')).to_have_css("background-color", "rgb(131, 21, 249)")
    expect(page.locator('.brand')).to_have_css("color", "rgb(255, 255, 255)")
    page.evaluate("document.documentElement.style.setProperty('--header-background', 'linear-gradient(105deg, #111F68 0%, #042AFF 45%, #76FFD6 100%)')")
    accept.hover()
    assert accept.evaluate("el => getComputedStyle(el).backgroundImage") == page.locator('.header').evaluate(
        "el => getComputedStyle(el).backgroundImage"
    )
    expect(accept).to_have_css("color", "rgb(255, 255, 255)")
    expect(decline).to_have_css("background-color", "rgb(232, 228, 207)")


@pytest.mark.parametrize("choice", ["Allow analytics", "Decline"])
def test_default_consent_isolated_by_github_pages_project(page, consent_sites, choice):
    add_site, google_requests = consent_sites
    first = "https://owner.github.io/project-a/"
    second = "https://owner.github.io/project-b/"
    add_site(first)
    add_site(second)
    page.goto(first)
    page.get_by_role("button", name=choice, exact=True).click()
    page.wait_for_load_state("networkidle")
    count = len(google_requests)
    page.goto(second)
    expect(page.locator("#analytics-consent")).to_be_visible()
    assert len(google_requests) == count
    assert page.evaluate("typeof window.gtag") == "undefined"
    assert not page.context.cookies()
    page.goto(first)
    expect(page.locator("#analytics-consent")).to_be_hidden()
    page.wait_for_load_state("networkidle")
    assert len(google_requests) == count + (choice == "Allow analytics")


@pytest.mark.parametrize("choice", ["Allow analytics", "Decline"])
def test_domain_consent_shared_in_both_directions(page, consent_sites, choice):
    add_site, google_requests = consent_sites
    root = "https://example.invalid/"
    child = "https://docs.example.invalid/"
    add_site(root, "example.invalid")
    add_site(child, "example.invalid")
    page.goto(root)
    expect(page.locator("#analytics-consent")).to_contain_text("example.invalid and its subdomains")
    page.get_by_role("button", name=choice, exact=True).click()
    page.wait_for_load_state("networkidle")
    cookie, = page.context.cookies()
    assert cookie["name"] == f"pixel-lab-analytics-{MEASUREMENT_ID}"
    assert cookie["value"] == ("granted" if choice == "Allow analytics" else "denied")
    assert cookie["domain"] == ".example.invalid"
    assert cookie["path"] == "/"
    assert cookie["secure"] is True
    assert cookie["sameSite"] == "Lax"
    assert cookie["expires"] - page.evaluate("Date.now() / 1000") == pytest.approx(15552000, abs=5)
    assert page.evaluate("localStorage.length") == 0
    page.goto(child)
    expect(page.locator("#analytics-consent")).to_be_hidden()
    page.wait_for_load_state("networkidle")
    assert len(google_requests) == (2 if choice == "Allow analytics" else 0)
    if choice == "Allow analytics":
        assert page.evaluate("window.dataLayer.at(-1)[2].cookie_domain") == "docs.example.invalid"
        page.evaluate("document.cookie = '_ga=test; Path=/'; document.cookie = '_ga_TEST123456=test; Path=/';")
    page.get_by_role("button", name="Analytics settings").click()
    reverse = "Decline" if choice == "Allow analytics" else "Allow analytics"
    if choice == "Allow analytics":
        with page.expect_navigation():
            page.get_by_role("button", name=reverse, exact=True).click()
        assert "_ga=" not in page.evaluate("document.cookie")
    else:
        page.get_by_role("button", name=reverse, exact=True).click()
    page.wait_for_load_state("networkidle")
    count = len(google_requests)
    page.goto(root)
    expect(page.locator("#analytics-consent")).to_be_hidden()
    page.wait_for_load_state("networkidle")
    assert len(google_requests) == count + (reverse == "Allow analytics")
    assert page.evaluate("typeof window.gtag") == ("function" if reverse == "Allow analytics" else "undefined")


@pytest.mark.parametrize("domain", ["unrelated.invalid", "example..invalid", "-example.invalid", "example.invalid; Path=/", "invalid", "github.io"])
def test_invalid_shared_domains_disable_analytics(page, consent_sites, domain):
    add_site, google_requests = consent_sites
    url = "https://owner.github.io/project/" if domain == "github.io" else f"{ORIGIN}/"
    add_site(url, domain)
    page.goto(url)
    expect(page.locator("#analytics-consent")).to_be_hidden()
    expect(page.locator("#analytics-settings")).to_be_hidden()
    assert not google_requests
    assert not page.context.cookies()


def test_shared_consent_isolated_by_measurement_id(page, consent_sites):
    add_site, google_requests = consent_sites
    add_site("https://example.invalid/", "example.invalid")
    add_site(f"{ORIGIN}/", "example.invalid", "G-ANOTHER123")
    page.goto("https://example.invalid/")
    page.get_by_role("button", name="Allow analytics", exact=True).click()
    page.wait_for_load_state("networkidle")
    page.goto(ORIGIN)
    expect(page.locator("#analytics-consent")).to_be_visible()
    assert len(google_requests) == 1


def test_shared_consent_does_not_promote_old_local_choices(page, consent_sites):
    add_site, google_requests = consent_sites
    add_site(f"{ORIGIN}/", "example.invalid")
    page.add_init_script(f"localStorage.setItem('{PREFERENCE_KEY}', 'granted'); localStorage.setItem('pixel-lab-analytics:{MEASUREMENT_ID}', 'granted');")
    page.goto(ORIGIN)
    expect(page.locator("#analytics-consent")).to_be_visible()
    assert not google_requests


def test_shared_cookie_storage_blocked_requires_new_choice(page, consent_sites):
    add_site, google_requests = consent_sites
    add_site(f"{ORIGIN}/", "example.invalid")
    page.add_init_script("""
        Object.defineProperty(Document.prototype, 'cookie', {
            get: () => '',
            set: () => { throw new Error('Cookies blocked'); },
            configurable: true,
        });
    """)
    page.goto(ORIGIN)
    expect(page.locator("#analytics-consent")).to_be_visible()
    assert not google_requests
    page.get_by_role("button", name="Allow analytics", exact=True).click()
    page.wait_for_load_state("networkidle")
    assert len(google_requests) == 1
    page.reload()
    expect(page.locator("#analytics-consent")).to_be_visible()
    assert len(google_requests) == 1


    page.get_by_role("button", name="Allow analytics", exact=True).click()
    page.wait_for_load_state("networkidle")
    assert len(google_requests) == 2
    page.get_by_role("button", name="Analytics settings").click()
    with page.expect_navigation():
        page.get_by_role("button", name="Decline", exact=True).click()
    assert page.evaluate("typeof window.gtag") == "undefined"
    assert len(google_requests) == 2


def test_old_hostname_only_preferences_not_reused_for_project_sites(analytics_browser):
    page, google_requests = analytics_browser
    page.add_init_script(f"localStorage.setItem('pixel-lab-analytics:{MEASUREMENT_ID}', 'granted');")
    page.goto(ORIGIN)
    expect(page.locator("#analytics-consent")).to_be_visible()
    assert not google_requests


@pytest.mark.parametrize("value", ["invalid", "true"])
def test_unknown_cookie_values_do_not_grant_consent(page, consent_sites, value):
    add_site, google_requests = consent_sites
    add_site(f"{ORIGIN}/", "example.invalid")
    page.context.add_cookies([{
        "name": f"pixel-lab-analytics-{MEASUREMENT_ID}", "value": value,
        "domain": ".example.invalid", "path": "/", "secure": True, "sameSite": "Lax",
    }])
    page.goto(ORIGIN)
    expect(page.locator("#analytics-consent")).to_be_visible()
    assert not google_requests


def test_domain_withdrawal_synchronizes_open_subdomain_pages(page, consent_sites):
    add_site, google_requests = consent_sites
    add_site("https://example.invalid/", "example.invalid")
    add_site(f"{ORIGIN}/", "example.invalid")
    page.goto("https://example.invalid/")
    page.get_by_role("button", name="Allow analytics", exact=True).click()
    page.wait_for_load_state("networkidle")
    page.evaluate("document.cookie = '_ga=root; Path=/';")
    sibling = page.context.new_page()
    sibling.goto(ORIGIN)
    sibling.wait_for_load_state("networkidle")
    assert len(google_requests) == 2
    sibling.get_by_role("button", name="Analytics settings").click()
    with page.expect_navigation(timeout=10000):
        with sibling.expect_navigation():
            sibling.get_by_role("button", name="Decline", exact=True).click()
    expect(page.locator("#analytics-consent")).to_be_hidden()
    assert page.evaluate("typeof window.gtag") == "undefined"
    assert "_ga=" not in page.evaluate("document.cookie")
    assert len(google_requests) == 2
    sibling.close()
