"""Black-box checks for the installed Pixel Lab theme."""

from __future__ import annotations

import functools
import http.server
import os
import re
import subprocess
import sys
import threading
from pathlib import Path

import pytest
from mkdocs.commands.build import build
from mkdocs.config import load_config
from playwright.sync_api import expect


ROOT = Path(__file__).parent
FIXTURE = ROOT / "fixture_site"
SNAPSHOTS = ROOT / "snapshots"


def capture_snapshot(page, name: str, temporary_dir: Path) -> None:
    """Capture a reviewable baseline only when explicitly requested."""
    destination = SNAPSHOTS / name if os.getenv("UPDATE_SNAPSHOTS") else temporary_dir / name
    page.screenshot(path=destination, full_page=False)
    assert destination.is_file()


@pytest.fixture(scope="session")
def site_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    destination = tmp_path_factory.mktemp("site")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "mkdocs",
            "build",
            "--strict",
            "--config-file",
            str(FIXTURE / "mkdocs.yml"),
            "--site-dir",
            str(destination),
        ],
        check=True,
    )
    return destination


@pytest.fixture(scope="session")
def edit_site_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    destination = tmp_path_factory.mktemp("edit-site")
    config = load_config(
        config_file=str(FIXTURE / "mkdocs.yml"), site_dir=str(destination), strict=True,
    )
    build(config)
    return destination


def serve_site(site_dir: Path):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(site_dir))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join()


@pytest.fixture()
def site_url(site_dir: Path):
    yield from serve_site(site_dir)


@pytest.fixture()
def edit_site_url(edit_site_dir: Path):
    yield from serve_site(edit_site_dir)


@pytest.fixture(scope="session", params=["assets/site-navigation-hover.svg#icon-hover", "assets/favicon.png"])
def custom_repo_site_dir(request, tmp_path_factory):
    destination = tmp_path_factory.mktemp("custom-repo-site")
    config = load_config(
        config_file=str(FIXTURE / "mkdocs.yml"), site_dir=str(destination), strict=True,
    )
    config.theme["icon"] = {"repo": request.param}
    build(config)
    return destination, request.param


@pytest.fixture()
def custom_repo_site_url(custom_repo_site_dir):
    destination, icon = custom_repo_site_dir
    for url in serve_site(destination):
        yield url, icon


def test_strict_fixture_build(site_dir: Path) -> None:
    assert (site_dir / "index.html").is_file()
    assert (site_dir / "assets" / "css" / "style.css").is_file()
    icon = (site_dir / "assets/icons/page-source.svg").read_text()
    assert 'shape-rendering="crispEdges"' in icon
    assert "<path " in icon and "<image" not in icon
    edit_icon = (site_dir / "assets/icons/page-edit.svg").read_text()
    assert 'shape-rendering="crispEdges"' in edit_icon
    assert 'id="edit-pixel"' in edit_icon and "<path " in edit_icon
    search_icon = (site_dir / "assets/icons/search.svg").read_text()
    assert 'id="search"' in search_icon and "<path " in search_icon


def test_page_source_icon_has_one_pixel_gap(page, site_url: str) -> None:
    page.goto(site_url)
    pixels = page.evaluate("""async () => {
        const icon = new Image();
        icon.src = new URL('assets/icons/page-source.svg', document.baseURI).href;
        await icon.decode();
        const canvas = document.createElement('canvas');
        canvas.width = canvas.height = 24;
        const context = canvas.getContext('2d');
        context.drawImage(icon, 0, 0, 24, 24);
        // Slash, transparent gap, and right bracket at their closest point.
        return [13, 14, 15].map(x => context.getImageData(x, 5, 1, 1).data[3]);
    }""")
    assert pixels == [255, 0, 255]


@pytest.mark.parametrize("width", [1440, 390, 320])
@pytest.mark.parametrize("long_title", [False, True])
def test_page_source_icon_trails_title(page, site_url: str, width: int, long_title: bool) -> None:
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(f"{site_url}/guide/nested/")
    page.evaluate("document.fonts.ready")
    title = page.locator(".main h1")
    expect(title).to_have_count(1)
    expect(title).to_have_attribute("id", "nested-page")
    if long_title:
        title.evaluate("element => { element.firstChild.textContent = 'A very long documentation title that wraps across several lines'; }")
    source = page.get_by_role("link", name="View source", exact=True)
    expect(source).to_be_visible()
    expect(source).to_have_attribute(
        "href", "https://github.com/trained-by-humans/pixel-lab-fixture/blob/main/docs/guide/nested.md",
    )
    expect(source).to_have_attribute("title", "View source on GitHub")
    assert source.text_content().strip() == ""
    expect(page.get_by_role("link", name="Edit this page", exact=True)).to_have_count(1)
    expect(page.locator(".footer .page-source")).to_have_count(0)
    assert source.evaluate("element => element.parentElement.tagName === 'H1' && element.nextElementSibling.classList.contains('page-edit')")
    font_size = title.evaluate("element => parseFloat(getComputedStyle(element).fontSize)")
    last_line = title.evaluate("""element => {
        const range = document.createRange();
        range.selectNodeContents(element.firstChild);
        const rectangle = Array.from(range.getClientRects()).at(-1);
        return {right: rectangle.right, top: rectangle.top, bottom: rectangle.bottom};
    }""")
    source_bounds = source.bounding_box()
    assert source_bounds["height"] == pytest.approx(font_size * 0.7, abs=0.1)
    assert source_bounds["width"] == pytest.approx(font_size * 0.7, abs=0.1)
    assert source_bounds["x"] == pytest.approx(last_line["right"] + 7.2, abs=1)
    assert source_bounds["y"] >= last_line["top"] - 1
    assert source_bounds["y"] + source_bounds["height"] <= last_line["bottom"] + 1
    expect(source).to_have_css("background-color", "rgba(0, 0, 0, 0)")
    expect(source).to_have_css("border-top-width", "0px")
    expect(source).to_have_css("box-shadow", "none")
    expect(source).to_have_css("vertical-align", "baseline")
    assert source.evaluate("element => getComputedStyle(element, '::before').opacity") == "0"
    source.hover()
    assert source.evaluate("element => getComputedStyle(element, '::before').opacity") == "1"
    shadow_offset = source.evaluate("""element => {
        const matrix = new DOMMatrix(getComputedStyle(element, '::before').transform);
        return [matrix.m41, matrix.m42];
    }""")
    assert shadow_offset == pytest.approx([font_size * 0.07] * 2, abs=0.01)
    assert source.bounding_box() == source_bounds
    expect(source).to_have_css("background-color", "rgba(0, 0, 0, 0)")
    page.mouse.move(0, 0)
    assert source.evaluate("element => getComputedStyle(element, '::before').opacity") == "0"
    page.keyboard.press("Tab")
    source.focus()
    expect(source).to_be_focused()
    expect(source).to_have_css("outline-style", "solid")
    assert source.evaluate("element => getComputedStyle(element, '::before').opacity") == "1"
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


@pytest.mark.parametrize("width", [1440, 390])
def test_page_source_link_works_without_javascript(browser, site_url: str, width: int) -> None:
    context = browser.new_context(java_script_enabled=False, viewport={"width": width, "height": 900})
    try:
        page = context.new_page()
        page.goto(f"{site_url}/guide/nested/")
        source = page.get_by_role("link", name="View source", exact=True)
        expect(source).to_be_visible()
        expect(source).to_have_attribute(
            "href", "https://github.com/trained-by-humans/pixel-lab-fixture/blob/main/docs/guide/nested.md",
        )
        assert source.bounding_box()["y"] == pytest.approx(page.locator(".main h1").bounding_box()["y"], abs=1)
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    finally:
        context.close()


def test_page_edit_icon_combines_supplied_pen_and_reference_line(page, edit_site_url: str) -> None:
    page.goto(edit_site_url)
    pixels = page.evaluate("""async () => {
        const icon = new Image();
        icon.src = new URL('assets/icons/page-edit.svg', document.baseURI).href;
        await icon.decode();
        const canvas = document.createElement('canvas');
        canvas.width = canvas.height = 36;
        const context = canvas.getContext('2d');
        context.drawImage(icon, 0, 0, 36, 36);
        // Sample the composite SVG's 18×18 grid at twice its native resolution.
        return Array.from({length: 18}, (_, y) =>
            Array.from({length: 18}, (_, x) =>
                context.getImageData(x * 2 + 1, y * 2 + 1, 1, 1).data[3] === 255 ? '#' : '.'
            ).join(''));
    }""")
    assert pixels == [
        "..................",
        "............###...",
        "...........##.##..",
        "............#..#..",
        ".........##..###..",
        "........####..#...",
        ".......##..##.....",
        "......##...##.....",
        ".....##...##......",
        "....##...##.......",
        "...##...##........",
        "..##...##.........",
        ".##...##..........",
        ".#...##...........",
        ".#..##........##..",
        ".####......#####..",
        "..................",
        "..................",
    ]


@pytest.mark.parametrize("width", [1440, 390, 320])
@pytest.mark.parametrize("long_title", [False, True])
def test_page_edit_icon_trails_source(page, edit_site_url: str, width: int, long_title: bool) -> None:
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(f"{edit_site_url}/guide/nested/")
    page.evaluate("document.fonts.ready")
    title = page.locator(".main h1")
    if long_title:
        title.evaluate("element => { element.firstChild.textContent = 'A very long documentation title that wraps across several lines'; }")
    expect(title).to_have_attribute("id", "nested-page")
    source = page.get_by_role("link", name="View source", exact=True)
    edit = page.get_by_role("link", name="Edit this page", exact=True)
    expect(edit).to_be_visible()
    expect(edit).to_have_attribute(
        "href", "https://github.com/trained-by-humans/pixel-lab-fixture/edit/main/docs/guide/nested.md",
    )
    expect(edit).to_have_attribute("title", "Edit this page")
    assert edit.evaluate("element => element.parentElement.tagName === 'H1' && element.previousElementSibling.classList.contains('page-source') && element.parentElement.lastChild === element")
    assert edit.text_content().strip() == ""
    font_size = title.evaluate("element => parseFloat(getComputedStyle(element).fontSize)")
    bounds = edit.bounding_box()
    assert bounds["width"] == pytest.approx(font_size * 0.7, abs=0.1)
    assert bounds["height"] == pytest.approx(font_size * 0.7, abs=0.1)
    source_bounds = source.bounding_box()
    # Either trails View source on the same line, or wraps without overlapping.
    assert bounds["y"] > source_bounds["y"] or bounds["x"] >= source_bounds["x"] + source_bounds["width"]
    expect(edit).to_have_css("background-color", "rgba(0, 0, 0, 0)")
    expect(edit).to_have_css("border-top-width", "0px")
    expect(edit).to_have_css("box-shadow", "none")
    mask = edit.evaluate("element => getComputedStyle(element, '::after').maskImage")
    assert mask.endswith('/assets/icons/page-edit.svg")')
    assert edit.evaluate("element => getComputedStyle(element, '::before').opacity") == "0"
    edit.hover()
    assert edit.evaluate("element => getComputedStyle(element, '::before').opacity") == "1"
    shadow_offset = edit.evaluate("""element => {
        const matrix = new DOMMatrix(getComputedStyle(element, '::before').transform);
        return [matrix.m41, matrix.m42];
    }""")
    assert shadow_offset == pytest.approx([font_size * 0.07] * 2, abs=0.01)
    assert edit.bounding_box() == bounds
    page.mouse.move(0, 0)
    assert edit.evaluate("element => getComputedStyle(element, '::before').opacity") == "0"
    source.focus()
    page.keyboard.press("Tab")
    expect(edit).to_be_focused()
    expect(edit).to_have_css("outline-style", "solid")
    assert edit.evaluate("element => getComputedStyle(element, '::before').opacity") == "1"
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


@pytest.mark.parametrize("width", [1440, 390, 320])
def test_page_edit_link_works_without_javascript(browser, edit_site_url: str, width: int) -> None:
    context = browser.new_context(java_script_enabled=False, viewport={"width": width, "height": 900})
    try:
        page = context.new_page()
        page.goto(f"{edit_site_url}/guide/nested/")
        source = page.get_by_role("link", name="View source", exact=True)
        edit = page.get_by_role("link", name="Edit this page", exact=True)
        expect(source).to_be_visible()
        expect(edit).to_be_visible()
        expect(edit).to_have_attribute(
            "href", "https://github.com/trained-by-humans/pixel-lab-fixture/edit/main/docs/guide/nested.md",
        )
        assert edit.bounding_box()["x"] + edit.bounding_box()["width"] <= source.bounding_box()["x"]
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    finally:
        context.close()


def test_code_highlighting_is_bundled_and_rendered(site_dir: Path) -> None:
    from importlib.metadata import requires
    from packaging.requirements import Requirement

    dependencies = [Requirement(value) for value in requires("mkdocs-pixel-lab")]
    assert any(dependency.name.lower() == "pygments" and dependency.marker is None for dependency in dependencies)
    html = (site_dir / "guide" / "code" / "index.html").read_text(encoding="utf-8")
    for token in ('class="kn"', 'class="s2"', 'class="nf"', 'class="c1"'):
        assert token in html
    assert html.count('class="hll"') == 2
    assert re.search(r'class="[^"]*\blanguage-python\b', html)
    assert re.search(r'class="[^"]*\blanguage-json\b', html)


@pytest.mark.parametrize("width", [1440, 390])
def test_code_highlighting_colors_and_line_emphasis(page, site_url: str, width: int) -> None:
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(f"{site_url}/guide/code/")
    code = page.locator(".highlight code").first
    expect(code).to_be_visible()
    for selector, variable in ((".kn", "--code-keyword"), (".s2", "--code-string"),
                               (".nf", "--code-function"), (".c1", "--code-comment")):
        assert code.locator(selector).first.evaluate("""(element, variable) => {
            const expected = document.createElement('span');
            expected.style.color = `var(${variable})`;
            element.appendChild(expected);
            const matches = getComputedStyle(element).color === getComputedStyle(expected).color;
            expected.remove();
            return matches;
        }""", variable)
    expect(code.locator(".hll")).to_have_count(2)
    for line in code.locator(".hll").all():
        assert line.evaluate("e => getComputedStyle(e).backgroundColor") != "rgba(0, 0, 0, 0)"
    geometry = code.evaluate("""element => {
        const pre = element.closest('pre');
        const bounds = element.getBoundingClientRect();
        const rows = Array.from(element.querySelectorAll('.hll')).map(line => {
            const row = line.getBoundingClientRect();
            return {top: row.top, bottom: row.bottom, height: row.height, width: row.width};
        });
        return {height: bounds.height, lineHeight: parseFloat(getComputedStyle(element).lineHeight),
                scrollWidth: pre.scrollWidth, rows};
    }""")
    first, second = geometry["rows"]
    assert second["top"] == pytest.approx(first["bottom"], abs=0.1)
    for row in geometry["rows"]:
        assert row["height"] == pytest.approx(geometry["lineHeight"], abs=0.1)
        assert row["width"] == pytest.approx(geometry["scrollWidth"], abs=1)
    expected_code = "\n".join([
        "import math", "", "def greet(name):", "    # Return a greeting.",
        '    return "Hello, " + name', 'print(greet("Pixel Lab"))',
    ]) + "\n"
    assert code.text_content() == expected_code
    assert geometry["height"] == pytest.approx(6 * geometry["lineHeight"], abs=1)
    page.evaluate("""() => {
        Object.defineProperty(navigator, 'clipboard', {configurable: true, value: {
            writeText: async text => { window.copiedCode = text; }
        }});
    }""")
    copy_button = page.get_by_role("button", name="Copy code to clipboard").first
    copy_button.click()
    expect(copy_button).to_have_text("COPIED")
    assert page.evaluate("window.copiedCode") == expected_code
    if width == 390:
        wide_block = page.locator(".language-json pre")
        assert wide_block.evaluate("e => e.scrollWidth > e.clientWidth")
        wide_block.evaluate("e => e.scrollLeft = 40")
        assert wide_block.evaluate("e => e.scrollLeft") > 0
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


def test_desktop_experience(page, site_url: str, tmp_path: Path) -> None:
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(site_url)
    expect(page).to_have_title("Home — Pixel Lab Fixture")
    expect(page.locator('link[rel="canonical"]')).to_have_attribute("href", "https://example.invalid/")
    expect(page.get_by_role("link", name="PIXEL LAB", exact=True)).to_have_attribute(
        "href", "https://github.com/trained-by-humans/mkdocs-pixel-lab"
    )
    expect(page.get_by_role("link", name="TRAINED-BY-HUMANS")).to_have_attribute(
        "href", "https://github.com/trained-by-humans"
    )

    expect(page.get_by_role("img", name="An abstract Pixel Lab data-flow diagram", exact=True)).to_be_visible()
    expect(page.locator(".gh-alert--note")).to_have_count(1)
    expect(page.locator(".gh-alert__title")).to_have_text("◆NOTE")
    expect(page.locator(".sidebar")).to_have_count(0)
    expect(page.locator("pre.highlight")).to_have_css("border-top-color", "rgb(18, 52, 86)")
    expect(page.locator("pre.highlight")).to_have_css("box-shadow", "rgb(101, 67, 33) 5px 5px 0px 0px")
    expect(page.locator("pre.highlight")).to_have_css("background-color", "rgb(16, 20, 16)")
    expect(page.locator(".admonition pre")).to_have_css("box-shadow", "none")
    expect(page.locator(".table-scroll img")).to_have_css("box-shadow", "none")
    capture_snapshot(page, "desktop.png", tmp_path)

    page.get_by_role("button", name="SEARCH").click()
    expect(page.locator("#mkdocs-search-query")).to_be_visible()
    copy_button = page.get_by_role("button", name="Copy code to clipboard").first
    copy_button.click()
    expect(copy_button).to_have_text("COPIED")


@pytest.mark.parametrize("width", [1440, 390])
def test_inline_code_optical_alignment(page, site_url: str, width: int) -> None:
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(site_url)
    inline_code = page.locator(".tabbed-content code").first
    expect(inline_code).to_be_visible()
    metrics = inline_code.evaluate("""element => {
        const style = getComputedStyle(element);
        return {fontSize: parseFloat(style.fontSize), lift: parseFloat(style.verticalAlign)};
    }""")
    assert metrics["lift"] == pytest.approx(metrics["fontSize"] * 0.04)
    for code in page.locator("pre code").all():
        expect(code).to_have_css("vertical-align", "baseline")


@pytest.mark.parametrize("width", [1440, 390])
def test_tab_content_layouts(page, site_url: str, width: int) -> None:
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(f"{site_url}/guide/tabs/")
    group = page.locator("#automatic-tabs > .tabbed-set")
    panels = group.locator(":scope > .tabbed-content > .tabbed-block")
    assert panels.count() == 4
    for index, layout in enumerate(("flush", "flush", "padded", "padded")):
        group.locator(":scope > .tabbed-labels > label").nth(index).click()
        panel = panels.nth(index)
        expect(panel).to_be_visible()
        expect(panel).to_have_attribute("data-tab-layout", layout)
        expect(panel).to_have_css("padding-left", "0px" if layout == "flush" else "20px")
        panel_box = panel.bounding_box()
        child_box = panel.locator(":scope > *").first.bounding_box()
        assert child_box["x"] - panel_box["x"] == pytest.approx(0 if layout == "flush" else 20)

    group.locator(":scope > .tabbed-labels > label").first.click()
    pre = panels.first.locator("pre")
    expect(pre).to_have_css("margin-top", "0px")
    expect(pre).to_have_css("border-top-width", "0px")
    expect(pre).to_have_css("padding-left", "20px")
    expect(pre).to_have_css("box-shadow", "none")
    expect(panels.first.get_by_role("button", name="Copy code to clipboard")).to_be_visible()

    group.locator(":scope > .tabbed-labels > label").nth(1).click()
    table_panel = panels.nth(1)
    shell = table_panel.locator(".table-shell")
    scroll = table_panel.locator(".table-scroll")
    expect(shell).to_have_css("margin-top", "0px")
    expect(scroll).to_have_css("border-top-width", "0px")
    expect(scroll).to_have_css("box-shadow", "none")
    expect(scroll).to_have_css("overflow-x", "auto")
    expect(table_panel.locator("img")).to_have_css("box-shadow", "none")
    assert shell.bounding_box()["width"] == pytest.approx(table_panel.bounding_box()["width"], abs=1)
    if width == 390:
        assert scroll.evaluate("el => el.scrollWidth > el.clientWidth")
        scroll.evaluate("el => el.scrollLeft = 100")
        assert scroll.evaluate("el => el.scrollLeft") > 0
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


def test_tab_content_overrides_and_nesting(page, site_url: str) -> None:
    page.goto(f"{site_url}/guide/tabs/")
    padded = page.locator("#padded-tabs .tabbed-block")
    expect(padded).to_have_attribute("data-tab-layout", "padded")
    expect(padded).to_have_css("padding-left", "20px")
    flush = page.locator("#flush-tabs .tabbed-block")
    expect(flush).to_have_attribute("data-tab-layout", "flush")
    expect(flush).to_have_css("padding-left", "0px")
    outer = page.locator("#nested-tabs > .tabbed-set > .tabbed-content > .tabbed-block")
    expect(outer).to_have_attribute("data-tab-layout", "padded")
    inner = outer.locator(".tabbed-block")
    expect(inner).to_have_attribute("data-tab-layout", "flush")
    expect(inner).to_have_css("padding-left", "0px")


def test_tabs_keep_padded_fallback_without_javascript(browser, site_url: str) -> None:
    context = browser.new_context(java_script_enabled=False)
    try:
        page = context.new_page()
        page.goto(f"{site_url}/guide/tabs/")
        panel = page.locator("#automatic-tabs .tabbed-block").first
        expect(panel).to_be_visible()
        expect(panel).to_have_css("padding-left", "20px")
    finally:
        context.close()


def test_trademark_glyph_uses_theme_colors(page, site_url: str) -> None:
    page.goto(site_url)
    badge = page.locator(".brand-trademark")
    glyph = badge.locator("svg")
    expect(badge).to_have_attribute("aria-hidden", "true")
    expect(badge).to_have_css("width", "16px")
    expect(badge).to_have_css("height", "16px")
    expect(badge).to_have_css("border-top-style", "solid")
    expect(badge).to_have_css("border-top-left-radius", "50%")
    expect(glyph).to_have_attribute("viewBox", "0 0 928 536")
    expect(glyph).to_have_attribute("focusable", "false")
    expect(glyph.locator("path")).to_have_count(3)
    expect(glyph.locator("image, filter")).to_have_count(0)
    circle_bounds = badge.bounding_box()
    glyph_bounds = glyph.bounding_box()
    for axis, size in (("x", "width"), ("y", "height")):
        assert glyph_bounds[axis] >= circle_bounds[axis] + 1.5
        assert glyph_bounds[axis] + glyph_bounds[size] <= circle_bounds[axis] + circle_bounds[size] - 1.5

    page.locator("html").evaluate("""element => {
        element.style.setProperty('--accent-foreground', '#abcdef');
        element.style.setProperty('--accent', '#fedcba');
        element.style.setProperty('--accent-dark', '#123456');
    }""")
    expect(badge).to_have_css("border-top-color", "rgb(171, 205, 239)")
    expect(glyph.locator(".brand-trademark__outline")).to_have_css("fill", "rgb(254, 220, 186)")
    expect(glyph.locator(".brand-trademark__rim")).to_have_css("fill", "rgb(18, 52, 86)")
    expect(glyph.locator(".brand-trademark__fill")).to_have_css("fill", "rgb(171, 205, 239)")


@pytest.mark.parametrize("width", [1440, 390, 320])
@pytest.mark.parametrize("javascript", [True, False])
def test_default_search_icon_in_toolbar(browser, site_url: str, width: int, javascript: bool) -> None:
    context = browser.new_context(java_script_enabled=javascript, viewport={"width": width, "height": 900})
    try:
        page = context.new_page()
        page.goto(f"{site_url}/guide/nested/")
        page.evaluate("document.fonts.ready")
        search = page.get_by_role("button", name="SEARCH", exact=True)
        icon = search.locator(".header-btn__icon--search")
        expect(icon).to_be_visible()
        expect(icon).to_have_attribute("aria-hidden", "true")
        assert icon.text_content() == ""
        expect(icon).to_have_css("width", "14px")
        expect(icon).to_have_css("height", "14px")
        expect(icon).to_have_css("transform", "none")
        expect(icon).to_have_css("box-shadow", "none")
        expect(icon).to_have_css("mask-image", f'url("{site_url}/assets/icons/search.svg")')
        assert icon.evaluate("element => getComputedStyle(element).backgroundColor") == (
            search.evaluate("element => getComputedStyle(element).color")
        )
        search.hover()
        expect(search).to_have_css("transform", "matrix(1, 0, 0, 1, -3, -3)")
        expect(icon).to_have_css("box-shadow", "none")
        page.locator("html").evaluate("element => element.style.setProperty('--strong-text', '#abcdef')")
        expect(icon).to_have_css("background-color", "rgb(171, 205, 239)")
        if javascript:
            search.click()
            expect(page.locator("#mkdocs-search-query")).to_be_focused()
            page.keyboard.press("Escape")
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    finally:
        context.close()


@pytest.mark.parametrize("width", [1440, 850, 600, 390, 320])
@pytest.mark.parametrize("javascript", [True, False])
def test_repository_button_in_toolbar(browser, site_url: str, width: int, javascript: bool) -> None:
    context = browser.new_context(java_script_enabled=javascript, viewport={"width": width, "height": 900})
    try:
        page = context.new_page()
        page.goto(site_url)
        page.evaluate("document.fonts.ready")
        repo = page.get_by_role("link", name="Open repository: GitHub", exact=True)
        expect(repo).to_be_visible()
        expect(repo).to_have_attribute("href", "https://github.com/trained-by-humans/pixel-lab-fixture")
        expect(repo).to_have_attribute("title", "Open repository: GitHub")
        expect(repo.locator(".header-btn__label")).to_have_text("GitHub")
        expect(repo.locator(".header-btn__icon")).to_have_attribute("aria-hidden", "true")
        expect(repo.locator(".header-btn__icon")).to_have_css("height", "14px")
        expect(repo).to_have_css("box-shadow", "none")
        expect(repo).to_have_css("transform", "none")
        label = repo.locator(".header-btn__label")
        if width <= 600:
            expect(label).to_be_hidden()
        else:
            expect(label).to_be_visible()
        bounds = repo.bounding_box()
        brand = page.locator(".brand").bounding_box()
        search = page.locator("#search-toggle").bounding_box()
        assert bounds["x"] >= brand["x"] + brand["width"]
        assert bounds["x"] + bounds["width"] <= search["x"]
        assert search["x"] + search["width"] <= width - 2
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")

        repo.hover()
        expect(repo).to_have_css("background-color", "rgb(245, 200, 66)")
        expect(repo).to_have_css("box-shadow", "rgb(101, 67, 33) 3px 3px 0px 0px")
        expect(repo).to_have_css("transform", "matrix(1, 0, 0, 1, -3, -3)")
        page.mouse.move(0, 800)
        expect(repo).to_have_css("box-shadow", "none")
        page.keyboard.press("Tab")
        repo.focus()
        expect(repo).to_be_focused()
        expect(repo).to_have_css("box-shadow", "rgb(101, 67, 33) 3px 3px 0px 0px")
        page.route("https://github.com/trained-by-humans/pixel-lab-fixture",
                   lambda route: route.fulfill(content_type="text/html", body="<h1>Repository</h1>"))
        page.keyboard.press("Enter")
        expect(page).to_have_url("https://github.com/trained-by-humans/pixel-lab-fixture")
    finally:
        context.close()


@pytest.mark.parametrize("width", [1440, 390, 320])
@pytest.mark.parametrize("javascript", [True, False])
def test_custom_repository_icon_in_toolbar(browser, custom_repo_site_url, width, javascript):
    site_url, icon_path = custom_repo_site_url
    context = browser.new_context(java_script_enabled=javascript, viewport={"width": width, "height": 900})
    try:
        page = context.new_page()
        page.goto(f"{site_url}/guide/nested/")
        page.evaluate("document.fonts.ready")
        repo = page.get_by_role("link", name="Open repository: GitHub", exact=True)
        expect(repo).to_be_visible()
        icon = repo.locator("img.header-btn__icon--repo")
        expect(icon).to_be_visible()
        expect(icon).to_have_attribute("src", "../../" + icon_path)
        expect(icon).to_have_attribute("alt", "")
        expect(icon).to_have_attribute("aria-hidden", "true")
        icon.evaluate("image => image.decode()")
        assert icon.evaluate("image => image.naturalWidth > 0")
        for dimension in ("width", "height"):
            expect(icon).to_have_css(dimension, "14px")
        expect(icon).to_have_css("background-color", "rgba(0, 0, 0, 0)")
        expect(icon).to_have_css("border-top-width", "0px")
        expect(icon).to_have_css("box-shadow", "none")
        expect(icon).to_have_css("mask-image", "none")
        expect(icon).to_have_css("margin-top", "0px")
        expect(icon).to_have_css("object-fit", "contain")
        expect(icon).to_have_css("max-width", "none")
        expect(repo).to_have_css("box-shadow", "none")
        repo.hover()
        expect(repo).to_have_css("transform", "matrix(1, 0, 0, 1, -3, -3)")
        expect(repo).to_have_css("box-shadow", "rgb(101, 67, 33) 3px 3px 0px 0px")
        expect(icon).to_have_css("box-shadow", "none")
        page.mouse.move(0, 800)
        page.keyboard.press("Tab")
        repo.focus()
        expect(repo).to_be_focused()
        expect(repo).to_have_css("box-shadow", "rgb(101, 67, 33) 3px 3px 0px 0px")
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        page.route("https://github.com/trained-by-humans/pixel-lab-fixture",
                   lambda route: route.fulfill(content_type="text/html", body="<h1>Repository</h1>"))
        page.keyboard.press("Enter")
        expect(page).to_have_url("https://github.com/trained-by-humans/pixel-lab-fixture")
    finally:
        context.close()


@pytest.mark.parametrize(("width", "gap", "inset"), [(1440, "14px", "14px"), (390, "8px", "58px")])
def test_toolbar_hover_selector(page, site_url: str, width: int, gap: str, inset: str) -> None:
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(site_url)
    expect(page.locator(".tabs")).to_have_css("column-gap", gap)
    expect(page.locator(".tabs")).to_have_css("padding-left", inset)
    active = page.locator(".tab.active")
    inactive = page.locator(".tabs .tab").filter(has_text="Guide")
    selector = "e => getComputedStyle(e, '::before').opacity"
    bounds = "e => [e.getBoundingClientRect().x, e.getBoundingClientRect().width]"
    original_bounds = page.locator(".tab").evaluate_all(f"elements => elements.map({bounds})")
    assert active.evaluate(selector) == "1"
    assert inactive.evaluate(selector) == "0"

    inactive.hover()
    assert inactive.evaluate(selector) == "0.4"
    for property_name in ("content", "color"):
        computed = f"e => getComputedStyle(e, '::before').{property_name}"
        assert inactive.evaluate(computed) == active.evaluate(computed)
    assert active.evaluate(selector) == "1"
    assert page.locator(".tab").evaluate_all(f"elements => elements.map({bounds})") == original_bounds

    page.mouse.move(0, 0)
    assert inactive.evaluate(selector) == "0"
    page.keyboard.press("Tab")
    inactive.focus()
    assert inactive.evaluate(selector) == "0.4"
    page.keyboard.press("Enter")
    expect(inactive).to_have_class("tab active")
    assert inactive.evaluate(selector) == "1"


@pytest.mark.parametrize("path", ["/", "/guide/nested/"])
def test_toolbar_start_aligns_with_website_name(page, site_url: str, path: str) -> None:
    page.goto(site_url + path)
    page.evaluate("document.fonts.ready")
    for width in (1440, 1920, 1024, 851, 850, 390):
        page.set_viewport_size({"width": width, "height": 900})
        label_left = page.locator(".tab").first.evaluate("""element => {
            const range = document.createRange();
            range.selectNodeContents(element.firstChild);
            return range.getBoundingClientRect().left;
        }""")
        brand_left = page.locator(".brand").bounding_box()["x"]
        assert label_left == pytest.approx(brand_left, abs=1)


def test_sidebar_hover_selector(page, site_url: str) -> None:
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(f"{site_url}/guide/nested/")
    active = page.locator(".sidebar .nav a.active")
    inactive = page.locator(".sidebar .nav a").filter(has_text="Media gallery")
    expect(page.locator(".sidebar")).to_have_css("padding-left", "6px")
    expect(inactive).to_have_css("padding-left", "22px")
    label_left = inactive.evaluate("""element => {
        const range = document.createRange();
        range.selectNodeContents(element.firstChild);
        return range.getBoundingClientRect().left;
    }""")
    assert label_left == pytest.approx(page.locator(".brand").bounding_box()["x"], abs=1)
    selector = "e => getComputedStyle(e, '::before').opacity"
    original_bounds = inactive.bounding_box()
    expect(inactive).to_have_css("background-color", "rgba(0, 0, 0, 0)")
    assert inactive.evaluate(selector) == "0"
    assert active.evaluate(selector) == "1"

    inactive.hover()
    assert inactive.evaluate(selector) == "0.4"
    for property_name in ("content", "color"):
        computed = f"e => getComputedStyle(e, '::before').{property_name}"
        assert inactive.evaluate(computed) == page.locator(".tab.active").evaluate(computed)
    expect(inactive).to_have_css("background-color", "rgba(0, 0, 0, 0)")
    assert inactive.bounding_box() == original_bounds
    active.hover()
    assert active.evaluate(selector) == "1"
    assert inactive.evaluate(selector) == "0"

    page.mouse.move(0, 0)
    page.keyboard.press("Tab")
    inactive.focus()
    assert inactive.evaluate(selector) == "0.4"
    page.keyboard.press("Enter")
    expect(page).to_have_url(f"{site_url}/guide/media/")
    expect(inactive).to_have_class("active")
    assert inactive.evaluate(selector) == "1"


def test_mobile_navigation_and_skip_link(page, site_url: str, tmp_path: Path) -> None:
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(site_url)
    expect(page.get_by_role("img", name="An abstract Pixel Lab data-flow diagram", exact=True)).to_be_visible()
    capture_snapshot(page, "mobile.png", tmp_path)
    page.keyboard.press("Tab")
    expect(page.locator(".skip-link")).to_be_focused()
    page.keyboard.press("Enter")
    expect(page.locator("#main-content")).to_be_focused()

    page.get_by_role("button", name="Open navigation").click()
    expect(page.locator("#mobile-nav")).to_have_class(re.compile(r"\bis-open\b"))
    page.get_by_role("link", name="Media gallery").click()
    expect(page).to_have_url(f"{site_url}/guide/media/")
    expect(page.locator(".sidebar")).to_have_count(1)
    expect(page.locator("main video")).to_be_visible()
