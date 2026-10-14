"""Configurable UI artwork preserves controls, default icons, and link behavior."""

import mimetypes
from pathlib import Path
import re
from urllib.parse import urlsplit

from mkdocs.commands.build import build
from mkdocs.config import load_config
from playwright.sync_api import expect
import pytest


FIXTURE = Path(__file__).parent / "fixture_site" / "mkdocs.yml"
ORIGIN = "https://example.invalid"
ICONS = {
    "repo": "assets/icons/repository.svg",
    "search": "assets/icons/heading-link.svg",
    "menu": "assets/icons/repository.svg",
    "close": "assets/icons/page-edit.svg",
    "sites": "assets/icons/page-source.svg",
    "dropdown": "assets/icons/heading-link.svg",
    "view": "assets/icons/page-edit.svg",
    "edit": "assets/icons/page-source.svg",
}


@pytest.fixture(scope="session", params=["svg", "png"])
def custom_icons_site(request, tmp_path_factory):
    destination = tmp_path_factory.mktemp("custom-icons-site")
    icons = ICONS if request.param == "svg" else dict.fromkeys(ICONS, "assets/favicon.png")
    config = load_config(config_file=str(FIXTURE), site_dir=str(destination), strict=True)
    config.theme["icon"] = icons
    config.extra["site_navigation"] = {
        "dropdown_label": "Packages",
        "items": [{"title": "Guide", "url": "guide/nested/"}],
    }
    build(config)
    return destination, icons


@pytest.fixture(params=[True, False], ids=["javascript", "no-javascript"])
def custom_icons_page(request, browser, custom_icons_site):
    destination, icons = custom_icons_site
    context = browser.new_context(java_script_enabled=request.param)
    page = context.new_page()

    def respond(route):
        url = urlsplit(route.request.url)
        if url.netloc != "example.invalid":
            route.abort()
            return
        path = destination / url.path.lstrip("/")
        if path.is_dir():
            path /= "index.html"
        if path.is_file():
            route.fulfill(
                content_type=mimetypes.guess_type(str(path))[0] or "text/plain",
                body=path.read_bytes(),
            )
        else:
            route.fulfill(status=404, body="Not found")

    page.route("**/*", respond)
    yield page, icons, request.param
    context.close()


@pytest.mark.parametrize("width", [1440, 851, 850, 700, 390, 320])
def test_custom_toolbar_icons_keep_controls_and_layout(custom_icons_page, width):
    page, icons, javascript = custom_icons_page
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(ORIGIN + "/guide/nested/")
    page.evaluate("document.fonts.ready")
    controls = {
        "repo": ".header-btn--repo",
        "search": "#search-toggle",
        "menu": "#nav-toggle",
        "close": "#nav-close",
        "sites": "#site-toggle",
        "dropdown": "#site-toggle",
    }
    for key, selector in controls.items():
        image = page.locator(f'{selector} img[src="../../{icons[key]}"]')
        if key in ("sites", "dropdown") and icons["sites"] == icons["dropdown"]:
            image = image.nth(0 if key == "sites" else 1)
        expect(image).to_have_count(1)
        expect(image).to_have_attribute("alt", "")
        expect(image).to_have_attribute("aria-hidden", "true")
        if key == "close" or (key == "menu" and width > 850) or (key == "dropdown" and width <= 850):
            expect(image).to_be_hidden()
            continue
        expect(image).to_be_visible()
        image.evaluate("image => image.decode()")
        assert image.evaluate("image => image.naturalWidth > 0")
        for dimension in ("height", "width"):
            expect(image).to_have_css(dimension, "14px")
        expect(image).to_have_css("box-shadow", "none")
        expect(image).to_have_css("border-top-width", "0px")
        expect(image).to_have_css("background-color", "rgba(0, 0, 0, 0)")
        expect(image).to_have_css("max-width", "none")
    # Toolbar customization must not replace the dropdown rows' fallback artwork.
    expect(page.locator("#site-panel .site-panel__icon")).to_have_count(1)
    assert page.locator("#site-panel .site-panel__icon").evaluate("element => element.tagName") == "svg"
    repo = page.locator(".header-btn--repo")
    packages = page.locator("#site-toggle")
    search = page.locator("#search-toggle")
    expect(repo).to_have_attribute("aria-label", "Open repository: GitHub")
    expect(packages).to_have_attribute("aria-label", "Packages")
    expect(search).to_have_attribute("aria-label", "SEARCH")
    expect(search.locator(".header-btn__icon--search")).to_have_count(0)
    repo_bounds, package_bounds, search_bounds = (element.bounding_box() for element in (repo, packages, search))
    assert repo_bounds["x"] + repo_bounds["width"] <= package_bounds["x"]
    assert package_bounds["x"] + package_bounds["width"] <= search_bounds["x"]
    assert search_bounds["x"] + search_bounds["width"] <= width - 2
    search.hover()
    expect(search).to_have_css("transform", "matrix(1, 0, 0, 1, -3, -3)")
    page.mouse.move(0, 800)
    if javascript:
        packages.hover()
        expect(page.locator("#site-panel")).to_be_visible()
        bounds = packages.bounding_box()
        assert page.locator("#site-panel").bounding_box()["y"] - bounds["y"] - bounds["height"] == pytest.approx(13)
        search.click()
        expect(page.locator("#site-panel")).to_be_hidden()
        expect(page.locator("#mkdocs-search-query")).to_be_focused()
        page.keyboard.press("Escape")
        if width <= 850:
            page.locator("#nav-toggle").click()
            expect(page.locator("#nav-close img")).to_be_visible()
            page.locator("#nav-close").click()
            expect(page.locator("#mobile-nav")).not_to_have_class(re.compile(r"\bis-open\b"))
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


@pytest.mark.parametrize("width", [1440, 390])
def test_custom_page_icons_keep_masks_and_navigation(custom_icons_page, width):
    page, icons, javascript = custom_icons_page
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(ORIGIN + "/guide/nested/")
    page.evaluate("document.fonts.ready")
    expect(page.locator("body")).to_have_attribute("data-permalink-style", "icon")
    expect(page.locator(".main h1")).to_have_attribute("id", "nested-page")
    expect(page.locator(".main h1 > .headerlink")).to_be_hidden()
    for key, selector, href in [
        ("view", ".page-source", "https://github.com/trained-by-humans/pixel-lab-fixture/blob/main/docs/guide/nested.md"),
        ("edit", ".page-edit", "https://github.com/trained-by-humans/pixel-lab-fixture/edit/main/docs/guide/nested.md"),
    ]:
        anchor = page.locator(selector)
        expect(anchor).to_be_visible()
        expect(anchor).to_have_attribute("href", href)
        expected_mask = f'url("{ORIGIN}/{icons[key]}")'
        for pseudo in ("::before", "::after"):
            assert anchor.evaluate("(element, pseudo) => getComputedStyle(element, pseudo).maskImage", pseudo) == expected_mask
        assert anchor.evaluate("element => getComputedStyle(element, '::before').opacity") == "0"
        bounds = anchor.bounding_box()
        anchor.hover()
        assert anchor.evaluate("element => getComputedStyle(element, '::before').opacity") == "1"
        assert anchor.bounding_box() == bounds
        page.mouse.move(0, 0)
        page.keyboard.press("Tab")
        anchor.focus()
        assert anchor.evaluate("element => getComputedStyle(element, '::before').opacity") == "1"
        page.locator(".main h1").click()
    page.locator("#fragment-target > .headerlink").click()
    expect(page).to_have_url(ORIGIN + "/guide/nested/#fragment-target")
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


@pytest.mark.parametrize("icons", [None, {}, dict.fromkeys(ICONS), dict.fromkeys(ICONS, ""), dict.fromkeys(ICONS, "  ")])
def test_unset_icons_keep_defaults(tmp_path, icons):
    config = load_config(config_file=str(FIXTURE), site_dir=str(tmp_path), strict=True)
    config.theme["icon"] = icons
    build(config)
    html = (tmp_path / "index.html").read_text()
    assert 'data-permalink-style="icon"' in html
    assert 'class="hamburger"' in html
    assert '<span class="header-btn__icon header-btn__icon--search" aria-hidden="true"></span>' in html
    assert "header-btn__icon--custom" not in html
    assert "--page-action-mask:" not in html


def test_custom_icons_do_not_enable_disabled_features(tmp_path):
    config = load_config(config_file=str(FIXTURE), site_dir=str(tmp_path), strict=True)
    config.theme["icon"] = ICONS
    config.theme["show_repo"] = False
    config.theme["show_source"] = False
    config.theme["show_edit"] = False
    config.mdx_configs["toc"]["permalink"] = False
    build(config)
    html = (tmp_path / "index.html").read_text()
    assert 'class="header-btn header-btn--repo"' not in html
    assert 'class="page-source"' not in html
    assert 'class="page-edit"' not in html
    assert 'class="headerlink"' not in html


def test_mask_urls_are_safe_css_strings_and_keep_queries(tmp_path):
    config = load_config(config_file=str(FIXTURE), site_dir=str(tmp_path), strict=True)
    path = """https://icons.example.org/a\\'";color:red;/*</style><script>alert(1)</script>.svg?x=1&y=2"""
    config.theme["icon"] = dict.fromkeys(("view", "edit"), path)
    build(config)
    html = (tmp_path / "guide/nested/index.html").read_text()
    style = re.search(r'<style id="pixel-lab-icons">(.*?)</style>', html, re.S)[1]
    assert "</style>" not in style and "<script>alert(1)" not in html
    for encoded in ("%5C", "%27", "%22", "%3C", "%3E"):
        assert encoded in style
    assert "?x=1&y=2" in style
    assert "&amp;" not in style
