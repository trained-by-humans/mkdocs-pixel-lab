"""Selectable heading permalinks keep their appearance and navigation contract."""

import mimetypes
from pathlib import Path
from urllib.parse import urlsplit

from mkdocs.commands.build import build
from mkdocs.config import load_config
import pytest
from playwright.sync_api import expect


FIXTURE = Path(__file__).parent / "fixture_site" / "mkdocs.yml"
ORIGIN = "https://example.invalid"


@pytest.fixture(scope="session", params=[None, "link", "hash"], ids=["default", "link", "hash"])
def permalink_site(request, tmp_path_factory):
    destination = tmp_path_factory.mktemp("permalink-site")
    config = load_config(config_file=str(FIXTURE), site_dir=str(destination), strict=True)
    if request.param is not None:
        config.theme["permalink_icon"] = request.param
    build(config)
    return destination, request.param or "link"


@pytest.fixture()
def permalink_page(page, permalink_site):
    destination, icon = permalink_site

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
    return page, destination, icon


def test_selectable_heading_permalinks(permalink_page):
    page, destination, icon = permalink_page
    asset = "heading-anchor" if icon == "hash" else "heading-link"
    for name in ("heading-anchor", "heading-link"):
        for suffix in ("", "-fill"):
            svg = (destination / "assets" / "icons" / f"{name}{suffix}.svg").read_text()
            assert "<path " in svg and "<image" not in svg

    for path, title_id, section_id in [
        ("/", "fixture-home", "searchable-heading"),
        ("/guide/nested/", "nested-page", "fragment-target"),
    ]:
        page.goto(ORIGIN + path)
        expect(page.locator("body")).to_have_attribute("data-permalink-icon", icon)
        expect(page.locator("main h1")).to_have_attribute("id", title_id)
        expect(page.locator("main h1 > .headerlink")).to_be_hidden()
        anchor = page.locator(f"#{section_id} > .headerlink")
        expect(anchor).to_be_visible()
        expect(anchor).to_have_attribute("href", f"#{section_id}")
        expect(anchor).to_have_attribute("title", "Permanent link")
        assert anchor.evaluate("e => e.parentElement.lastChild === e")
        expect(anchor).to_have_css("height", "14px")
        expect(anchor).to_have_css("vertical-align", "baseline")
        assert anchor.evaluate(
            "e => getComputedStyle(e, '::after').maskImage"
        ) == f'url("{ORIGIN}/assets/icons/{asset}.svg")'
        assert anchor.evaluate(
            "e => getComputedStyle(e, '::before').maskImage"
        ) == f'url("{ORIGIN}/assets/icons/{asset}-fill.svg")'

        accent = page.locator(".tab.active").evaluate("e => getComputedStyle(e, '::before').color")
        dark = page.locator(".tab.active").evaluate("e => getComputedStyle(e).color")
        assert anchor.evaluate("e => getComputedStyle(e, '::before').backgroundColor") == accent
        anchor.hover()
        assert anchor.evaluate("e => getComputedStyle(e, '::before').backgroundColor") == dark
        assert anchor.evaluate("e => getComputedStyle(e, '::after').backgroundColor") == "rgb(0, 0, 0)"
        page.mouse.move(0, 0)
        assert anchor.evaluate("e => getComputedStyle(e, '::before').backgroundColor") == accent
        anchor.focus()
        page.keyboard.press("Enter")
        expect(page).to_have_url(f"{ORIGIN}{path}#{section_id}")
