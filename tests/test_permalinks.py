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
    route_site(page, destination)
    return page, destination, icon, fill_color


def route_site(page, destination):
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


@pytest.fixture(
    scope="session",
    params=[
        ({"permalink": "⚓", "permalink_title": "Link to this section"}, None, "text"),
        ({"permalink": "¶", "permalink_title": ""}, None, "text"),
        ({"permalink": "Link here", "permalink_leading": True, "separator": "_", "anchorlink": True}, None, "text"),
        ({"permalink": True, "permalink_leading": True}, None, "chain"),
        ({"permalink": "⚓", "permalink_leading": "false"}, "assets/icons/repository.svg", "custom"),
        ({"permalink": False}, "assets/icons/repository.svg", "custom"),
        ({}, "assets/icons/repository.svg", "custom"),
        ({"permalink": "true"}, None, "chain"),
        ({"permalink": "false"}, "assets/icons/repository.svg", "custom"),
    ],
    ids=[
        "symbol", "explicit-paragraph-symbol", "leading-text-and-heading-links",
        "leading-default-icon", "explicit-image-override", "disabled-with-image",
        "omitted-with-image", "string-true", "string-false-with-image",
    ],
)
def toc_permalink_site(request, tmp_path_factory):
    options, custom_icon, mode = request.param
    destination = tmp_path_factory.mktemp("toc-permalink-site")
    config = load_config(config_file=str(FIXTURE), site_dir=str(destination), strict=True)
    config.mdx_configs["toc"] = options
    if custom_icon:
        config.theme["icon"] = {"permalink": custom_icon}
    build(config)
    return destination, options, custom_icon, mode


@pytest.fixture(params=[True, False], ids=["javascript", "no-javascript"])
def toc_permalink_page(request, browser, toc_permalink_site):
    destination, options, custom_icon, mode = toc_permalink_site
    context = browser.new_context(java_script_enabled=request.param)
    page = context.new_page()
    route_site(page, destination)
    yield page, options, custom_icon, mode, request.param
    context.close()


def test_toc_permalink_configuration_is_respected(toc_permalink_page):
    page, options, custom_icon, mode, javascript = toc_permalink_page
    page.set_viewport_size({"width": 390, "height": 900})
    page.goto(ORIGIN + "/guide/nested/")
    expect(page.locator("body")).to_have_attribute("data-permalink-icon", mode)
    separator = options.get("separator", "-")
    section_id = f"fragment{separator}target"
    heading = page.locator(f"#{section_id}")
    expect(heading).to_be_visible()
    expect(page.locator("main h1")).to_have_attribute("id", f"nested{separator}page")
    anchor = heading.locator(".headerlink")
    if options.get("permalink", False) in (False, "false"):
        expect(page.locator(".main .headerlink")).to_have_count(0)
        expect(page.locator(".headerlink__fill")).to_have_count(0)
        return

    expect(page.locator("main h1 > .headerlink")).to_be_hidden()
    expect(anchor).to_be_visible()
    expect(anchor).to_have_attribute("href", f"#{section_id}")
    title = options.get("permalink_title", "Permanent link")
    assert anchor.get_attribute("title") == (title or None)
    leading = options.get("permalink_leading", False) is True
    if leading:
        assert anchor.evaluate("element => element.parentElement.firstChild === element")
        expect(anchor).to_have_css("margin-left", "0px")
        expect(anchor).to_have_css("margin-right", "7.2px")
    else:
        assert anchor.evaluate("element => element.parentElement.lastChild === element")
        expect(anchor).to_have_css("margin-left", "7.2px")
        expect(anchor).to_have_css("margin-right", "0px")

    if mode == "text":
        expect(anchor).to_have_text(options["permalink"])
        expect(anchor).to_have_css("text-indent", "0px")
        expect(anchor).to_have_css("overflow", "visible")
        expect(page.locator(".headerlink__fill")).to_have_count(0)
        for pseudo in ("::before", "::after"):
            assert anchor.evaluate("(element, pseudo) => getComputedStyle(element, pseudo).content", pseudo) == "none"
        # Confirm the symbol's glyphs occupy its visible box, not hidden indented text.
        text_bounds = anchor.evaluate("""element => {
            const range = document.createRange();
            range.selectNodeContents(element);
            const {x, width} = range.getBoundingClientRect();
            return {x, width};
        }""")
        bounds = anchor.bounding_box()
        assert text_bounds["x"] == pytest.approx(bounds["x"], abs=1)
        assert text_bounds["width"] == pytest.approx(bounds["width"], abs=1)
    elif mode == "custom":
        assert anchor.evaluate("element => getComputedStyle(element, '::after').maskImage") == (
            f'url("{ORIGIN}/{custom_icon}")'
        )
        expect(page.locator(".headerlink__fill")).to_have_count(0)
    else:
        expect(anchor).to_have_css("height", "14px")
        expect(anchor.locator(".headerlink__fill")).to_have_count(1 if javascript else 0)

    if options.get("anchorlink"):
        expect(heading.locator(".toclink")).to_have_text("Fragment target")
        expect(heading.locator(".toclink")).to_have_attribute("href", f"#{section_id}")
    anchor.focus()
    page.keyboard.press("Enter")
    expect(page).to_have_url(ORIGIN + f"/guide/nested/#{section_id}")
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


@pytest.mark.parametrize("extension", ["toc", "markdown.extensions.toc", "markdown.extensions.toc:TocExtension"])
def test_toc_extension_names_and_custom_permalink_classes(tmp_path, extension):
    config = load_config(config_file=str(FIXTURE), site_dir=str(tmp_path), strict=True)
    config.markdown_extensions = [name for name in config.markdown_extensions if name != "toc"] + [extension]
    config.mdx_configs.pop("toc", None)
    config.mdx_configs[extension] = {
        "permalink": "⚓", "permalink_class": "section-link custom-link",
        "permalink_title": "Section URL", "permalink_leading": True, "separator": "_",
    }
    build(config)
    html = (tmp_path / "guide/nested/index.html").read_text()
    assert 'data-permalink-icon="text"' in html
    assert 'data-permalink-leading="true"' in html
    assert '<h2 id="fragment_target"><a class="section-link custom-link" href="#fragment_target" title="Section URL">⚓</a>Fragment target</h2>' in html
