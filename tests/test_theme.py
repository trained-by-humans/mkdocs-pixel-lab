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


@pytest.fixture()
def site_url(site_dir: Path):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(site_dir))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join()


def test_strict_fixture_build(site_dir: Path) -> None:
    assert (site_dir / "index.html").is_file()
    assert (site_dir / "assets" / "css" / "style.css").is_file()


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
