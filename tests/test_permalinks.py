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
LAYERS = {
    "link": ("heading-link", "heading-link-fill"),
    "hash": ("heading-anchor", "heading-anchor-fill"),
    "chain": ("heading-chain", "heading-chain-shadow"),
}


@pytest.fixture(
    scope="session",
    params=[
        (None, None), ("link", None), ("hash", None),
        ("chain", None), ("chain", "#abcdef"), ("chain", "transparent"),
    ],
    ids=["default", "link", "hash", "chain", "chain-custom-fill", "chain-no-fill"],
)
def permalink_site(request, tmp_path_factory):
    icon, fill_color = request.param
    destination = tmp_path_factory.mktemp("permalink-site")
    config = load_config(config_file=str(FIXTURE), site_dir=str(destination), strict=True)
    if icon is not None:
        config.theme["permalink_icon"] = icon
    if fill_color is not None:
        config.theme["permalink_fill_color"] = fill_color
    build(config)
    return destination, icon or "chain", fill_color


@pytest.fixture()
def permalink_page(page, permalink_site):
    destination, icon, fill_color = permalink_site

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
    return page, destination, icon, fill_color


def test_selectable_heading_permalinks(permalink_page):
    page, destination, icon, configured_fill = permalink_page
    outline_asset, accent_asset = LAYERS[icon]
    for name in (outline_asset, accent_asset, "heading-chain-fill"):
        svg = (destination / "assets" / "icons" / f"{name}.svg").read_text()
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
        ) == f'url("{ORIGIN}/assets/icons/{outline_asset}.svg")'
        assert anchor.evaluate(
            "e => getComputedStyle(e, '::before').maskImage"
        ) == f'url("{ORIGIN}/assets/icons/{accent_asset}.svg")'

        accent = page.locator(".tab.active").evaluate("e => getComputedStyle(e, '::before').color")
        dark = page.locator(".tab.active").evaluate("e => getComputedStyle(e).color")
        fill = anchor.locator(".headerlink__fill")
        if icon == "chain":
            expect(fill).to_have_count(1)
            expect(fill).to_have_attribute("aria-hidden", "true")
            assert fill.evaluate("e => getComputedStyle(e).maskImage") == (
                f'url("{ORIGIN}/assets/icons/heading-chain-fill.svg")'
            )
            fill_color = {
                "#abcdef": "rgb(171, 205, 239)",
                "transparent": "rgba(0, 0, 0, 0)",
            }.get(configured_fill, accent)
            expect(fill).to_have_css("background-color", fill_color)
        else:
            expect(fill).to_have_count(0)

        shadow_color = dark if icon == "chain" else accent
        shadow_opacity = "0" if icon == "chain" else "1"
        assert anchor.evaluate("e => getComputedStyle(e, '::before').backgroundColor") == shadow_color
        assert anchor.evaluate("e => getComputedStyle(e, '::before').opacity") == shadow_opacity
        anchor.hover()
        assert anchor.evaluate("e => getComputedStyle(e, '::before').backgroundColor") == dark
        assert anchor.evaluate("e => getComputedStyle(e, '::before').opacity") == "1"
        assert anchor.evaluate("e => getComputedStyle(e, '::after').backgroundColor") == "rgb(0, 0, 0)"
        if icon == "chain":
            expect(fill).to_have_css("background-color", fill_color)
        page.mouse.move(0, 0)
        assert anchor.evaluate("e => getComputedStyle(e, '::before').backgroundColor") == shadow_color
        assert anchor.evaluate("e => getComputedStyle(e, '::before').opacity") == shadow_opacity
        page.keyboard.press("Tab")
        anchor.focus()
        assert anchor.evaluate("e => getComputedStyle(e, '::before').opacity") == "1"
        if icon == "chain":
            expect(fill).to_have_css("background-color", fill_color)
            assert anchor.evaluate("e => getComputedStyle(e, '::before').backgroundColor") == dark
        page.keyboard.press("Enter")
        expect(page).to_have_url(f"{ORIGIN}{path}#{section_id}")
