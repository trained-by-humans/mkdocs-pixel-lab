"""One built-in heading-link icon plus Python-Markdown's native TOC options."""

import mimetypes
from pathlib import Path
from urllib.parse import urlsplit

from mkdocs.commands.build import build
from mkdocs.config import load_config
import pytest
from playwright.sync_api import expect


FIXTURE = Path(__file__).parent / "fixture_site" / "mkdocs.yml"
ORIGIN = "https://example.invalid"


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


@pytest.fixture(scope="session")
def permalink_site(tmp_path_factory):
    destination = tmp_path_factory.mktemp("permalink-site")
    config = load_config(config_file=str(FIXTURE), site_dir=str(destination), strict=True)
    build(config)
    return destination


@pytest.fixture(params=[True, False], ids=["javascript", "no-javascript"])
def permalink_page(request, browser, permalink_site):
    context = browser.new_context(java_script_enabled=request.param)
    page = context.new_page()
    route_site(page, permalink_site)
    yield page
    context.close()


def test_only_one_built_in_permalink_asset_and_no_theme_options(permalink_site):
    assets = permalink_site / "assets" / "icons"
    assert sorted(path.name for path in assets.glob("heading-*.svg")) == ["heading-link.svg"]
    svg = (assets / "heading-link.svg").read_text()
    assert 'id="link-solid"' in svg and "<polygon " in svg and "<image" not in svg
    config = load_config(config_file=str(FIXTURE))
    assert "permalink" not in config.theme["icon"]
    assert "permalink_icon" not in config.theme
    assert "permalink_fill_color" not in config.theme


@pytest.mark.parametrize("width", [1440, 390])
def test_default_heading_permalinks(permalink_page, width):
    page = permalink_page
    page.set_viewport_size({"width": width, "height": 900})
    for path, title_id, section_id in [
        ("/", "fixture-home", "searchable-heading"),
        ("/guide/nested/", "nested-page", "fragment-target"),
    ]:
        page.goto(ORIGIN + path)
        page.evaluate("document.fonts.ready")
        expect(page.locator("body")).to_have_attribute("data-permalink-style", "icon")
        expect(page.locator("main h1")).to_have_attribute("id", title_id)
        expect(page.locator("main h1 > .headerlink")).to_be_hidden()
        anchor = page.locator(f"#{section_id} > .headerlink")
        expect(anchor).to_be_visible()
        expect(anchor).to_have_attribute("href", f"#{section_id}")
        expect(anchor).to_have_attribute("title", "Permanent link")
        assert anchor.evaluate("element => element.parentElement.lastChild === element")
        expect(anchor).to_have_css("height", "14px")
        expect(anchor).to_have_css("width", "14px")
        expect(anchor).to_have_css("vertical-align", "baseline")
        expect(anchor).to_have_css("overflow", "visible")
        expect(anchor.locator("*")).to_have_count(0)
        for pseudo in ("::before", "::after"):
            assert anchor.evaluate(
                "(element, pseudo) => getComputedStyle(element, pseudo).maskImage", pseudo,
            ) == f'url("{ORIGIN}/assets/icons/heading-link.svg")'
        assert anchor.evaluate("element => getComputedStyle(element, '::after').backgroundColor") == "rgb(0, 0, 0)"
        dark = page.locator(".tab.active").evaluate("element => getComputedStyle(element).color")
        assert anchor.evaluate("element => getComputedStyle(element, '::before').backgroundColor") == dark
        assert anchor.evaluate("element => getComputedStyle(element, '::before').opacity") == "0"
        bounds = anchor.bounding_box()
        anchor.hover()
        assert anchor.evaluate("element => getComputedStyle(element, '::before').opacity") == "1"
        assert anchor.bounding_box() == bounds
        offset = anchor.evaluate("""element => {
            const matrix = new DOMMatrix(getComputedStyle(element, '::before').transform);
            return [matrix.m41, matrix.m42];
        }""")
        assert offset == pytest.approx([1.4, 1.4], abs=0.01)
        page.mouse.move(0, 0)
        assert anchor.evaluate("element => getComputedStyle(element, '::before').opacity") == "0"
        page.keyboard.press("Tab")
        anchor.focus()
        assert anchor.evaluate("element => getComputedStyle(element, '::before').opacity") == "1"
        page.keyboard.press("Enter")
        expect(page).to_have_url(f"{ORIGIN}{path}#{section_id}")


@pytest.mark.parametrize("width", [1440, 390])
def test_permalink_aligns_to_heading_baseline(permalink_page, width):
    page = permalink_page
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(ORIGIN + "/guide/nested/")
    page.evaluate("document.fonts.ready")
    page.evaluate("""() => {
        const original = document.querySelector('#fragment-target > .headerlink');
        const footer = document.querySelector('.main .footer');
        for (let level = 2; level <= 6; level++) {
            const heading = document.createElement('h' + level);
            heading.id = 'alignment-h' + level;
            heading.textContent = level === 2
                ? 'A longer heading that wraps across multiple lines on smaller screens'
                : 'Heading level ' + level;
            const link = original.cloneNode(true);
            link.href = '#' + heading.id;
            heading.append(link);
            footer.before(heading);
        }
    }""")
    for level in range(2, 7):
        heading = page.locator(f"#alignment-h{level}")
        anchor = heading.locator(".headerlink")
        expect(anchor).to_be_visible()
        expect(anchor).to_have_css("overflow", "visible")
        metrics = heading.evaluate("""heading => {
            const anchor = heading.querySelector('.headerlink');
            const marker = document.createElement('span');
            marker.style.cssText = 'display:inline-block;width:0;height:0;vertical-align:baseline';
            heading.append(marker);
            const bounds = anchor.getBoundingClientRect();
            const metrics = {
                baselineOffset: bounds.bottom - marker.getBoundingClientRect().top,
                height: bounds.height,
                fontSize: parseFloat(getComputedStyle(heading).fontSize),
            };
            marker.remove();
            return metrics;
        }""")
        assert metrics["baselineOffset"] == pytest.approx(0, abs=0.1)
        assert metrics["height"] == pytest.approx(metrics["fontSize"] * 0.7, abs=0.1)
        anchor.hover()
        assert anchor.evaluate("element => getComputedStyle(element, '::before').opacity") == "1"
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


@pytest.fixture(
    scope="session",
    params=[
        ({"permalink": "⚓", "permalink_title": "Link to this section"}, "text", True),
        ({"permalink": "¶", "permalink_title": ""}, "text", True),
        ({"permalink": "Link here", "permalink_leading": True, "separator": "_", "anchorlink": True}, "text", True),
        ({"permalink": "#", "permalink_leading": "false"}, "text", True),
        ({"permalink": True, "permalink_leading": True}, "icon", True),
        ({"permalink": "true", "permalink_leading": "true"}, "icon", True),
        ({"permalink": "ON"}, "icon", True),
        ({"permalink": False}, "icon", False),
        ({}, "icon", False),
        ({"permalink": "false"}, "icon", False),
        ({"permalink": ""}, "text", True),
        ({"permalink": None}, "icon", False),
    ],
    ids=[
        "symbol", "explicit-paragraph-symbol", "leading-text-and-heading-links",
        "trailing-symbol", "leading-default-icon", "string-true", "string-on",
        "disabled", "omitted", "string-false", "empty-symbol", "null",
    ],
)
def toc_permalink_site(request, tmp_path_factory):
    options, mode, enabled = request.param
    destination = tmp_path_factory.mktemp("toc-permalink-site")
    config = load_config(config_file=str(FIXTURE), site_dir=str(destination), strict=True)
    config.mdx_configs["toc"] = options
    build(config)
    return destination, options, mode, enabled


@pytest.fixture(params=[True, False], ids=["javascript", "no-javascript"])
def toc_permalink_page(request, browser, toc_permalink_site):
    destination, options, mode, enabled = toc_permalink_site
    context = browser.new_context(java_script_enabled=request.param)
    page = context.new_page()
    route_site(page, destination)
    yield page, options, mode, enabled
    context.close()


def test_toc_permalink_configuration_is_respected(toc_permalink_page):
    page, options, mode, enabled = toc_permalink_page
    page.set_viewport_size({"width": 390, "height": 900})
    page.goto(ORIGIN + "/guide/nested/")
    page.evaluate("document.fonts.ready")
    expect(page.locator("body")).to_have_attribute("data-permalink-style", mode)
    separator = options.get("separator", "-")
    section_id = f"fragment{separator}target"
    heading = page.locator(f"#{section_id}")
    expect(heading).to_be_visible()
    expect(page.locator("main h1")).to_have_attribute("id", f"nested{separator}page")
    anchor = heading.locator(".headerlink")
    if not enabled:
        expect(page.locator(".main .headerlink")).to_have_count(0)
        return
    if options.get("permalink") == "":
        # TOC emits an empty anchor for an empty symbol; do not replace it with the icon.
        expect(anchor).to_have_count(1)
        expect(anchor).to_have_text("")
        expect(anchor).to_have_css("width", "0px")
        assert anchor.evaluate("element => getComputedStyle(element, '::after').content") == "none"
        return

    expect(page.locator("main h1 > .headerlink")).to_be_hidden()
    expect(anchor).to_be_visible()
    expect(anchor).to_have_attribute("href", f"#{section_id}")
    expect(anchor.locator("*")).to_have_count(0)
    title = options.get("permalink_title", "Permanent link")
    assert anchor.get_attribute("title") == (title or None)
    leading = options.get("permalink_leading", False) in (True, "true")
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
        for pseudo in ("::before", "::after"):
            assert anchor.evaluate(
                "(element, pseudo) => getComputedStyle(element, pseudo).content", pseudo,
            ) == "none"
        text_bounds = anchor.evaluate("""element => {
            const range = document.createRange();
            range.selectNodeContents(element);
            const {x, width} = range.getBoundingClientRect();
            return {x, width};
        }""")
        bounds = anchor.bounding_box()
        assert text_bounds["x"] == pytest.approx(bounds["x"], abs=1)
        assert text_bounds["width"] == pytest.approx(bounds["width"], abs=1)
    else:
        expect(anchor).to_have_css("height", "14px")
        assert anchor.evaluate("element => getComputedStyle(element, '::after').maskImage") == (
            f'url("{ORIGIN}/assets/icons/heading-link.svg")'
        )
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
    assert 'data-permalink-style="text"' in html
    assert 'data-permalink-leading="true"' in html
    assert '<h2 id="fragment_target"><a class="section-link custom-link" href="#fragment_target" title="Section URL">⚓</a>Fragment target</h2>' in html
