"""Site-navigation dropdown rendering, icons, and interaction."""

import copy
import mimetypes
import re
from pathlib import Path
from urllib.parse import urlsplit

from mkdocs.commands.build import build
from mkdocs.config import load_config
import pytest
from playwright.sync_api import expect


FIXTURE = Path(__file__).parent / "fixture_site" / "mkdocs.yml"
ORIGIN = "https://example.invalid"
NAVIGATION = {
    "dropdown_label": "Packages",
    "header_size": 2,
    "footer_size": 2,
    "items": [
        {"title": "Core", "url": "guide/nested/", "icon": "assets/pixel-lab-preview.svg"},
        {
            "title": "Supervision", "url": "https://supervision.ml-pipes.com/",
            "icon": "assets/site-navigation-hover.svg", "active": True,
            "icon_hover": "assets/site-navigation-hover.svg#icon-hover",
        },
        {"title": "Vision", "url": "https://example.org/vision/"},
    ],
    "catalog": {"title": "All packages", "url": "guide/media/"},
}


@pytest.fixture(scope="session")
def navigation_site(tmp_path_factory):
    destination = tmp_path_factory.mktemp("navigation-site")
    config = load_config(config_file=str(FIXTURE), site_dir=str(destination), strict=True)
    config.site_name = "ml-pipes-supervision"
    config.extra["site_navigation"] = copy.deepcopy(NAVIGATION)
    build(config)
    return destination


@pytest.fixture()
def navigation_page(page, navigation_site):
    def respond(route):
        url = urlsplit(route.request.url)
        if url.netloc != "example.invalid":
            route.abort()
            return
        path = navigation_site / url.path.lstrip("/")
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
    return page


@pytest.mark.parametrize(
    ("navigation", "dropdown", "inline", "footer"),
    [
        (None, False, False, False), ({}, False, False, False),
        (NAVIGATION, True, False, True),
        ({**NAVIGATION, "header_mode": "dropdown"}, True, False, True),
        ({**NAVIGATION, "header_mode": "inline"}, False, True, True),
        ({**NAVIGATION, "header_mode": "none"}, False, False, True),
        ({"items": NAVIGATION["items"]}, True, False, False),
        ({"catalog": NAVIGATION["catalog"]}, True, False, True),
        ({"header_mode": "inline", "items": NAVIGATION["items"]}, False, False, False),
        ({**NAVIGATION, "show_footer": False}, True, False, False),
        ({**NAVIGATION, "header_mode": "inline", "show_footer": False}, False, True, False),
        ({**NAVIGATION, "header_mode": "none", "show_footer": False}, False, False, False),
    ],
    ids=[
        "absent", "empty", "default-dropdown", "dropdown", "inline", "none",
        "no-catalog", "catalog-only", "inline-no-catalog", "dropdown-no-footer",
        "inline-no-footer", "none-no-footer",
    ],
)
def test_navigation_placements(tmp_path, navigation, dropdown, inline, footer):
    config = load_config(config_file=str(FIXTURE), site_dir=str(tmp_path), strict=True)
    if navigation is not None:
        config.extra["site_navigation"] = navigation
    build(config)
    html = (tmp_path / "index.html").read_text()
    assert ('id="site-toggle"' in html) is dropdown
    assert ('class="package-inline"' in html) is inline
    assert ('class="package-footer"' in html) is footer


@pytest.mark.parametrize("path", ["/", "/guide/nested/"])
def test_dropdown_items_and_icons(navigation_page, path):
    page = navigation_page
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(ORIGIN + path)
    toggle = page.get_by_role("button", name="Packages", exact=True)
    panel = page.locator("#site-panel")
    expect(panel).to_be_hidden()
    expect(toggle).to_have_attribute("aria-expanded", "false")
    toggle.click()
    expect(panel).to_be_visible()
    expect(toggle).to_have_attribute("aria-expanded", "true")
    expect(panel.locator("a")).to_have_count(4)
    expect(panel.locator(".site-panel__icon")).to_have_count(4)
    expect(panel.get_by_role("link", name="Supervision")).to_have_attribute("aria-current", "true")
    expect(panel.get_by_role("link", name="Supervision")).to_have_text("Supervision")
    expect(panel.get_by_role("link", name="Supervision").locator("img")).to_have_attribute(
        "data-hover-src", "../../assets/site-navigation-hover.svg#icon-hover" if path != "/" else "assets/site-navigation-hover.svg#icon-hover",
    )
    image = panel.get_by_role("link", name="Core").locator("img")
    expect(image).to_have_attribute("alt", "")
    assert image.evaluate("e => e.src") == ORIGIN + "/assets/pixel-lab-preview.svg"
    expect(image).to_have_js_property("complete", True)
    assert image.evaluate("e => e.naturalWidth") > 0
    expect(image).to_have_css("box-shadow", "none")
    expect(image).to_have_css("border-top-width", "0px")
    expect(panel).to_have_css("border-top-color", "rgb(18, 52, 86)")
    expect(panel).to_have_css("box-shadow", "rgb(101, 67, 33) 5px 5px 0px 0px")
    expect(panel.get_by_role("link", name="Vision").locator("svg")).to_have_count(1)
    expect(panel).to_have_css("padding", "0px")
    expect(image).to_have_css("height", "24px")
    hover_image = panel.get_by_role("link", name="Supervision").locator("img")
    expect(hover_image).to_have_css("height", "44px")
    expect(hover_image).to_have_css("margin-top", "0px")
    bounds = panel.bounding_box()
    assert bounds["width"] == pytest.approx(224)
    previous_bottom = bounds["y"] + 2
    for link in panel.locator("a").all():
        row = link.bounding_box()
        assert row["x"] == pytest.approx(bounds["x"] + 2)
        assert row["width"] == pytest.approx(bounds["width"] - 4)
        assert row["y"] == pytest.approx(previous_bottom)
        assert row["height"] == pytest.approx(46)
        expect(link).to_have_css("padding-top", "0px")
        expect(link).to_have_css("padding-bottom", "0px")
        previous_bottom = row["y"] + row["height"]
    assert previous_bottom == pytest.approx(bounds["y"] + bounds["height"] - 2)
    core = panel.get_by_role("link", name="Core")
    selected = panel.locator(".active")
    selected_color = selected.evaluate("e => getComputedStyle(e).backgroundColor")
    core.hover()
    hover_color = core.evaluate("e => getComputedStyle(e).backgroundColor")
    colors = page.evaluate("""colors => {
        const context = document.createElement('canvas').getContext('2d');
        return colors.map(color => {
            context.fillStyle = color;
            context.fillRect(0, 0, 1, 1);
            return [...context.getImageData(0, 0, 1, 1).data].slice(0, 3);
        });
    }""", [hover_color, selected_color])
    assert all(hover > active for hover, active in zip(*colors))
    selected.hover()
    expect(selected).to_have_css("background-color", selected_color)
    toggle.focus()
    page.keyboard.press("ArrowDown")
    expect(core).to_be_focused()
    expect(core).to_have_css("background-color", hover_color)
    page.keyboard.press("ArrowDown")
    expect(selected).to_be_focused()
    expect(selected).to_have_css("background-color", selected_color)
    expect(page.locator(".package-inline")).to_have_count(0)
    expect(page.locator(".package-footer a")).to_have_count(2)
    toggle.click()
    expect(panel).to_be_hidden()
    expect(toggle).to_have_attribute("aria-expanded", "false")


@pytest.mark.parametrize("width", [1440, 850, 600, 390, 320])
def test_dropdown_responsive_layout(navigation_page, width):
    page = navigation_page
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(ORIGIN)
    toggle = page.get_by_role("button", name="Packages", exact=True)
    search = page.get_by_role("button", name="SEARCH", exact=True)
    expect(toggle).to_be_visible()
    expect(search).to_be_visible()
    assert toggle.bounding_box()["height"] == pytest.approx(search.bounding_box()["height"], abs=1)
    assert toggle.bounding_box()["x"] + toggle.bounding_box()["width"] <= search.bounding_box()["x"]
    toggle.click()
    panel = page.locator("#site-panel")
    bounds = panel.bounding_box()
    assert bounds["x"] >= 0
    assert bounds["x"] + bounds["width"] <= width
    assert bounds["width"] <= 224
    assert page.locator(".header").evaluate("e => e.scrollWidth") <= width
    if width <= 600:
        expect(toggle.locator(".header-btn__label")).to_be_hidden()
    page.mouse.click(5, 500)
    expect(panel).to_be_hidden()
    expect(toggle).to_have_attribute("aria-expanded", "false")


def test_dropdown_keyboard_and_search(navigation_page):
    page = navigation_page
    page.goto(ORIGIN)
    toggle = page.get_by_role("button", name="Packages", exact=True)
    panel = page.locator("#site-panel")
    links = panel.locator("a")
    toggle.focus()
    page.keyboard.press("ArrowDown")
    expect(links.first).to_be_focused()
    page.keyboard.press("ArrowDown")
    expect(links.nth(1)).to_be_focused()
    page.keyboard.press("End")
    expect(links.last).to_be_focused()
    page.keyboard.press("Home")
    expect(links.first).to_be_focused()
    page.keyboard.press("Escape")
    expect(panel).to_be_hidden()
    expect(toggle).to_be_focused()
    page.keyboard.press("ArrowUp")
    expect(links.last).to_be_focused()
    page.get_by_role("button", name="SEARCH", exact=True).click()
    expect(panel).to_be_hidden()
    expect(page.locator("#mkdocs-search-query")).to_be_focused()
    toggle.click()
    expect(page.locator("#search-panel")).to_be_hidden()
    expect(panel).to_be_visible()
    # Tab can leave the disclosure; it is not a modal or a focus trap.
    links.last.focus()
    page.keyboard.press("Tab")
    expect(panel).to_be_hidden()
    toggle.focus()
    page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")
    expect(page).to_have_url(ORIGIN + "/guide/nested/")


def test_hover_icon_animation_replays_from_cached_asset(navigation_page):
    page = navigation_page
    fetches = []
    page.on("request", lambda request: fetches.append(request.url) if request.resource_type == "fetch" and "site-navigation-hover.svg" in request.url else None)
    page.goto(ORIGIN)
    page.get_by_role("button", name="Packages", exact=True).click()
    link = page.locator("#site-panel").get_by_role("link", name="Supervision")
    icon = link.locator("img")
    expect(icon).to_have_js_property("complete", True)
    baseline = icon.screenshot()
    previous_src = None
    for _ in range(2):
        link.hover()
        expect(icon).to_have_attribute("src", re.compile(r"^blob:.*#icon-hover$"))
        current_src = icon.get_attribute("src")
        assert current_src != previous_src
        previous_src = current_src
        page.wait_for_timeout(120)
        assert icon.screenshot() != baseline
        page.wait_for_timeout(1200)
        assert icon.screenshot() == baseline
        page.mouse.move(5, 700)
        expect(icon).to_have_attribute("src", "assets/site-navigation-hover.svg")
    assert len(fetches) == 1


def test_hover_icon_canvas_contains_entire_drop(navigation_page):
    page = navigation_page
    page.emulate_media(reduced_motion="no-preference")
    page.goto(ORIGIN + "/assets/site-navigation-hover.svg#icon-hover")
    for time in (0, 120, 530, 1120):
        bounds = page.evaluate("""time => {
            const svg = document.querySelector('svg');
            svg.getAnimations({subtree: true}).forEach(animation => {
                animation.pause();
                animation.currentTime = time;
            });
            const block = svg.querySelector('.drop');
            const box = block.getBBox();
            const matrix = svg.getCTM().inverse().multiply(block.getCTM());
            const points = [new DOMPoint(box.x, box.y),
                            new DOMPoint(box.x + box.width, box.y + box.height)]
                .map(point => point.matrixTransform(matrix));
            const view = svg.viewBox.baseVal;
            return {left: points[0].x, top: points[0].y,
                    right: points[1].x, bottom: points[1].y,
                    x: view.x, y: view.y, width: view.width, height: view.height};
        }""", time)
        assert bounds['left'] >= bounds['x']
        assert bounds['top'] >= bounds['y']
        assert bounds['right'] <= bounds['x'] + bounds['width']
        assert bounds['bottom'] <= bounds['y'] + bounds['height']
        assert bounds['width'] / bounds['height'] == pytest.approx(24 / 44)


def test_hover_icon_keyboard_and_reduced_motion(navigation_page):
    page = navigation_page
    page.goto(ORIGIN)
    toggle = page.get_by_role("button", name="Packages", exact=True)
    icon = page.locator("#site-panel .active img")
    toggle.focus()
    page.keyboard.press("ArrowDown")
    page.keyboard.press("ArrowDown")
    expect(icon).to_have_attribute("src", re.compile(r"^blob:"))
    page.keyboard.press("Escape")
    expect(icon).to_have_attribute("src", "assets/site-navigation-hover.svg")
    page.emulate_media(reduced_motion="reduce")
    toggle.click()
    page.locator("#site-panel").get_by_role("link", name="Supervision").hover()
    page.wait_for_timeout(150)
    expect(icon).to_have_attribute("src", "assets/site-navigation-hover.svg")
    page.emulate_media(reduced_motion="no-preference")
    page.mouse.move(5, 700)
    page.locator("#site-panel").get_by_role("link", name="Supervision").hover()
    expect(icon).to_have_attribute("src", re.compile(r"^blob:"))
    page.emulate_media(reduced_motion="reduce")
    expect(icon).to_have_attribute("src", "assets/site-navigation-hover.svg")


def test_hover_icon_cancelled_while_asset_loads(navigation_page):
    page = navigation_page
    page.goto(ORIGIN)
    page.get_by_role("button", name="Packages", exact=True).click()
    link = page.locator("#site-panel").get_by_role("link", name="Supervision")
    icon = link.locator("img")
    expect(icon).to_have_js_property("complete", True)
    held = []
    page.route("**/assets/site-navigation-hover.svg", lambda route: held.append(route))
    link.hover()
    page.wait_for_timeout(150)
    assert len(held) == 1
    page.mouse.move(5, 700)
    held[0].fulfill(path=str(FIXTURE.parent / "docs/assets/site-navigation-hover.svg"), content_type="image/svg+xml")
    page.wait_for_timeout(150)
    expect(icon).to_have_attribute("src", "assets/site-navigation-hover.svg")
    link.hover()
    expect(icon).to_have_attribute("src", re.compile(r"^blob:"))
    assert len(held) == 1


def test_hover_icon_fetch_failure_keeps_static_icon(navigation_page):
    page = navigation_page
    page.goto(ORIGIN)
    page.get_by_role("button", name="Packages", exact=True).click()
    link = page.locator("#site-panel").get_by_role("link", name="Supervision")
    icon = link.locator("img")
    expect(icon).to_have_js_property("complete", True)
    page.route("**/assets/site-navigation-hover.svg", lambda route: route.fulfill(status=404))
    link.hover()
    page.wait_for_timeout(150)
    expect(icon).to_have_attribute("src", "assets/site-navigation-hover.svg")
    page.get_by_role("button", name="SEARCH", exact=True).click()
    expect(page.locator("#mkdocs-search-query")).to_be_focused()
