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


@pytest.mark.parametrize("width", [1440, 390, 320])
def test_repository_precedes_packages(navigation_page, width):
    page = navigation_page
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(ORIGIN)
    page.evaluate("document.fonts.ready")
    repo = page.get_by_role("link", name="Open repository: GitHub", exact=True)
    packages = page.get_by_role("button", name="Packages", exact=True)
    search = page.get_by_role("button", name="SEARCH", exact=True)
    expect(repo).to_be_visible()
    assert repo.evaluate("element => element.nextElementSibling.classList.contains('site-switcher')")
    repo_bounds = repo.bounding_box()
    package_bounds = packages.bounding_box()
    search_bounds = search.bounding_box()
    assert repo_bounds["x"] + repo_bounds["width"] <= package_bounds["x"]
    assert package_bounds["x"] + package_bounds["width"] <= search_bounds["x"]
    assert search_bounds["x"] + search_bounds["width"] <= width - 2
    repo.focus()
    page.keyboard.press("Tab")
    expect(packages).to_be_focused()
    page.keyboard.press("Tab")
    expect(search).to_be_focused()
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


@pytest.mark.parametrize("width", [1440, 390])
def test_toolbar_shadows_follow_highlights(navigation_page, width):
    page = navigation_page
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(ORIGIN)
    header = page.locator(".header")
    expect(header).to_have_css("box-shadow", "rgb(40, 124, 53) 0px 4px 0px 0px")
    for button in header.locator(".header-btn").all():
        expect(button).to_have_css("box-shadow", "none")
        expect(button).to_have_css("border-top-width", "2px")
        expect(button).to_have_css("transform", "none")

    def expect_highlighted(button):
        expect(button).to_have_css("background-color", "rgb(245, 200, 66)")
        expect(button).to_have_css("box-shadow", "rgb(101, 67, 33) 3px 3px 0px 0px")
        expect(button).to_have_css("transform", "matrix(1, 0, 0, 1, -3, -3)")

    def expect_lifted(button, idle_bounds):
        bounds = button.bounding_box()
        assert bounds == pytest.approx({
            **idle_bounds, "x": idle_bounds["x"] - 3, "y": idle_bounds["y"] - 3,
        })

    packages = page.get_by_role("button", name="Packages", exact=True)
    package_bounds = packages.bounding_box()
    packages.hover()
    expect_highlighted(packages)
    expect_lifted(packages, package_bounds)
    panel = page.locator("#site-panel")
    panel.locator("a").first.hover()
    expect_highlighted(packages)
    expect(panel).to_have_css("box-shadow", "rgb(101, 67, 33) 5px 5px 0px 0px")
    page.mouse.move(5, 800)
    expect(packages).to_have_css("box-shadow", "none")
    expect(packages).to_have_css("transform", "none")
    packages.click()
    page.mouse.move(5, 800)
    expect_highlighted(packages)

    search = page.get_by_role("button", name="SEARCH", exact=True)
    search_bounds = search.bounding_box()
    search.hover()
    # Even when its preview is blocked, a hovered button is highlighted.
    expect(search).to_have_attribute("aria-expanded", "false")
    expect_highlighted(search)
    expect_lifted(search, search_bounds)
    search.click()
    page.locator("#mkdocs-search-query").hover()
    expect_highlighted(search)
    expect(packages).to_have_css("box-shadow", "none")
    expect(page.locator("#search-panel")).to_have_css("box-shadow", "rgb(101, 67, 33) 5px 5px 0px 0px")
    page.mouse.move(5, 800)
    expect_highlighted(search)
    search.click()
    page.mouse.move(5, 800)
    expect(search).to_have_css("box-shadow", "none")
    expect(search).to_have_css("transform", "none")

    packages.focus()
    page.keyboard.press("ArrowDown")
    page.keyboard.press("Escape")
    expect(packages).to_be_focused()
    expect(packages).to_have_attribute("aria-expanded", "false")
    expect_highlighted(packages)
    page.locator(".main h1").click()
    expect(packages).to_have_css("box-shadow", "none")

    if width == 390:
        menu = page.get_by_role("button", name="Open navigation", exact=True)
        expect(menu).to_have_css("box-shadow", "none")
        menu.hover()
        expect_highlighted(menu)
        menu.click()
        page.locator("#nav-close").hover()
        expect_highlighted(menu)
        expect(page.locator("#nav-close")).to_have_css("box-shadow", "none")
        expect(page.locator("#nav-close")).to_have_css("transform", "none")
        page.locator("#nav-close").click()
        page.locator(".main h1").click()
        expect(menu).to_have_css("box-shadow", "none")
    expect(header).to_have_css("box-shadow", "rgb(40, 124, 53) 0px 4px 0px 0px")
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


@pytest.mark.parametrize(("width", "button_id"), [
    (1440, "search-toggle"), (390, "search-toggle"),
    (1440, "site-toggle"), (390, "site-toggle"), (390, "nav-toggle"),
])
def test_lifted_toolbar_button_original_corner_remains_clickable(navigation_page, width, button_id):
    page = navigation_page
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(ORIGIN)
    button = page.locator(f"#{button_id}")
    bounds = button.bounding_box()
    x = bounds["x"] + bounds["width"] - 1
    y = bounds["y"] + bounds["height"] - 1
    # Enter the original bottom-right corner, now outside the lifted face.
    page.mouse.move(x, y)
    expect(button).to_have_css("transform", "matrix(1, 0, 0, 1, -3, -3)")
    assert button.evaluate("element => element.matches(':hover')")
    page.mouse.click(x, y)
    expect(button).to_have_attribute("aria-expanded", "true")
    if button_id == "search-toggle":
        expect(page.locator(".search-shell")).to_have_class(re.compile(r"\bis-open\b"))
        expect(page.locator("#mkdocs-search-query")).to_be_focused()
    elif button_id == "site-toggle":
        expect(page.locator(".site-switcher")).to_have_class(re.compile(r"\bis-open\b"))
    else:
        expect(page.locator("#nav-close")).to_be_visible()
        return
    # A pinned button must retain that hit area even after the mouse leaves.
    page.mouse.move(5, 800)
    page.mouse.click(x, y)
    shell = page.locator(".search-shell" if button_id == "search-toggle" else ".site-switcher")
    expect(shell).not_to_have_class(re.compile(r"\bis-open\b"))
    expect(shell).to_have_class(re.compile(r"\bis-preview\b"))


@pytest.mark.parametrize("width", [1440, 390])
def test_search_hover_bridge_and_input_activation(navigation_page, width):
    page = navigation_page
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(ORIGIN)
    toggle = page.get_by_role("button", name="SEARCH", exact=True)
    shell = page.locator(".search-shell")
    panel = page.locator("#search-panel")
    query = page.locator("#mkdocs-search-query")
    packages = page.get_by_role("button", name="Packages", exact=True)
    packages.hover()
    expect(page.locator("#site-panel")).to_be_visible()
    toggle.hover()
    expect(page.locator("#site-panel")).to_be_hidden()
    expect(panel).to_be_visible()
    expect(toggle).to_have_attribute("aria-expanded", "true")
    expect(query).not_to_be_focused()
    expect(shell).not_to_have_class(re.compile(r"\bis-open\b"))
    expect(panel).to_have_css("transform", "matrix(1, 0, 0, 1, 0, 0)")
    button_bounds = toggle.bounding_box()
    panel_bounds = panel.bounding_box()
    button_bottom = button_bounds["y"] + button_bounds["height"]
    gap = panel_bounds["y"] - button_bottom
    assert gap == pytest.approx(13)
    x = button_bounds["x"] + button_bounds["width"] / 2
    for fraction in [0.1, 0.5, 0.9]:
        page.mouse.move(x, button_bottom + gap * fraction)
        expect(panel).to_be_visible()
        expect(toggle).to_have_attribute("aria-expanded", "true")
    query.hover()
    expect(panel).to_be_visible()
    expect(query).not_to_be_focused()
    page.mouse.move(5, 800)
    expect(panel).to_be_hidden()
    expect(toggle).to_have_attribute("aria-expanded", "false")

    toggle.hover()
    query.click()
    expect(query).to_be_focused()
    expect(shell).to_have_class(re.compile(r"\bis-open\b"))
    page.mouse.move(5, 800)
    query.fill("nested")
    expect(panel).to_be_visible()
    expect(query).to_have_value("nested")
    page.keyboard.press("Escape")
    expect(panel).to_be_hidden()
    expect(toggle).to_be_focused()
    expect(toggle).to_have_attribute("aria-expanded", "false")

    # A preview can be dismissed without taking focus from the page.
    page.mouse.move(5, 800)
    page.locator(".main h1").evaluate("element => { element.tabIndex = -1; element.focus(); }")
    toggle.hover()
    expect(panel).to_be_visible()
    page.keyboard.press("Escape")
    expect(panel).to_be_hidden()
    expect(page.locator(".main h1")).to_be_focused()


@pytest.mark.parametrize("width", [1440, 390])
def test_search_second_pointer_click_returns_to_preview(navigation_page, width):
    page = navigation_page
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(ORIGIN)
    toggle = page.get_by_role("button", name="SEARCH", exact=True)
    shell = page.locator(".search-shell")
    panel = page.locator("#search-panel")
    query = page.locator("#mkdocs-search-query")
    idle_color = toggle.evaluate("element => getComputedStyle(element).backgroundColor")
    for _ in range(2):
        toggle.hover()
        expect(panel).to_be_visible()
        toggle.click()
        expect(query).to_be_focused()
        query.fill("nested")
        toggle.click()
        expect(query).not_to_be_focused()
        expect(panel).to_be_visible()
        expect(shell).to_have_class(re.compile(r"\bis-preview\b"))
        expect(shell).not_to_have_class(re.compile(r"\bis-open\b"))
        expect(toggle).to_have_attribute("aria-expanded", "true")
        query.hover()
        expect(panel).to_be_visible()
        expect(query).to_have_value("nested")
        page.mouse.move(5, 800)
        expect(panel).to_be_hidden()
        expect(toggle).to_have_attribute("aria-expanded", "false")
        expect(toggle).to_have_css("background-color", idle_color)


@pytest.mark.parametrize("width", [1440, 390])
def test_search_explicit_dismissal_and_keyboard_activation(navigation_page, width):
    page = navigation_page
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(ORIGIN)
    toggle = page.get_by_role("button", name="SEARCH", exact=True)
    panel = page.locator("#search-panel")
    query = page.locator("#mkdocs-search-query")
    toggle.click()
    expect(query).to_be_focused()
    page.keyboard.press("Escape")
    # Hover and returned keyboard focus must not immediately reopen the panel.
    expect(toggle).to_be_focused()
    expect(panel).to_be_hidden()
    expect(toggle).to_have_attribute("aria-expanded", "false")
    page.keyboard.press("Enter")
    expect(query).to_be_focused()
    expect(panel).to_be_visible()
    page.keyboard.press("Shift+Tab")
    expect(toggle).to_be_focused()
    page.keyboard.press("Enter")
    expect(panel).to_be_hidden()
    expect(toggle).to_have_attribute("aria-expanded", "false")
    page.keyboard.press("Enter")
    expect(query).to_be_focused()
    page.keyboard.press("Escape")
    page.keyboard.press("Space")
    expect(query).to_be_focused()
    toggle.click()
    expect(query).not_to_be_focused()
    expect(panel).to_be_visible()
    page.mouse.move(5, 800)
    expect(panel).to_be_hidden()
    expect(toggle).to_have_attribute("aria-expanded", "false")
    toggle.click()
    expect(query).to_be_focused()
    page.locator(".main h1").click()
    expect(panel).to_be_hidden()
    expect(toggle).to_have_attribute("aria-expanded", "false")
    toggle.click()
    expect(query).to_be_focused()
    page.keyboard.press("Tab")
    expect(panel).to_be_hidden()


@pytest.mark.browser_context_args(has_touch=True)
def test_search_touch_activation(navigation_page):
    page = navigation_page
    page.set_viewport_size({"width": 390, "height": 900})
    page.goto(ORIGIN)
    toggle = page.get_by_role("button", name="SEARCH", exact=True)
    panel = page.locator("#search-panel")
    page.locator(".search-shell").dispatch_event("pointerenter", {"pointerType": "touch"})
    expect(panel).to_be_hidden()
    toggle.tap()
    expect(page.locator("#mkdocs-search-query")).to_be_focused()
    expect(panel).to_be_visible()
    toggle.tap()
    expect(panel).to_be_hidden()


@pytest.mark.parametrize("width", [1440, 390, 320])
def test_packages_hover_bridge_and_pinning(navigation_page, width):
    page = navigation_page
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(ORIGIN)
    toggle = page.get_by_role("button", name="Packages", exact=True)
    shell = page.locator(".site-switcher")
    panel = page.locator("#site-panel")
    title = page.locator(".main h1")
    title.evaluate("element => { element.tabIndex = -1; element.focus(); }")
    idle_color = toggle.evaluate("element => getComputedStyle(element).backgroundColor")
    toggle.hover()
    expect(panel).to_be_visible()
    expect(toggle).to_have_attribute("aria-expanded", "true")
    expect(shell).to_have_class(re.compile(r"\bis-preview\b"))
    expect(title).to_be_focused()
    button_bounds = toggle.bounding_box()
    panel_bounds = panel.bounding_box()
    button_bottom = button_bounds["y"] + button_bounds["height"]
    assert panel_bounds["y"] - button_bottom == pytest.approx(13)
    x = button_bounds["x"] + button_bounds["width"] / 2
    for offset in [1, 5, 9, 12]:
        page.mouse.move(x, button_bottom + offset)
        expect(panel).to_be_visible()
        expect(toggle).to_have_attribute("aria-expanded", "true")
    panel.locator("a").first.hover()
    expect(panel).to_be_visible()
    expect(title).to_be_focused()
    expect(toggle).to_have_css("background-color", "rgb(245, 200, 66)")
    page.mouse.move(5, 800)
    expect(panel).to_be_hidden()
    expect(toggle).to_have_attribute("aria-expanded", "false")
    expect(toggle).to_have_css("background-color", idle_color)
    toggle.hover()
    page.keyboard.press("Escape")
    expect(panel).to_be_hidden()
    expect(title).to_be_focused()

    toggle.click()
    expect(shell).to_have_class(re.compile(r"\bis-open\b"))
    page.mouse.move(5, 800)
    expect(panel).to_be_visible()
    toggle.click()
    expect(panel).to_be_visible()
    expect(shell).to_have_class(re.compile(r"\bis-preview\b"))
    expect(shell).not_to_have_class(re.compile(r"\bis-open\b"))
    page.mouse.move(5, 800)
    expect(panel).to_be_hidden()
    expect(toggle).to_have_css("background-color", idle_color)
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


@pytest.mark.parametrize("width", [1440, 390])
def test_pinned_toolbar_panels_take_priority_over_hover(navigation_page, width):
    page = navigation_page
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(ORIGIN)
    packages = page.get_by_role("button", name="Packages", exact=True)
    site_panel = page.locator("#site-panel")
    search = page.get_by_role("button", name="SEARCH", exact=True)
    search_panel = page.locator("#search-panel")
    query = page.locator("#mkdocs-search-query")
    # Unpinned hover previews can replace each other.
    search.hover()
    expect(search_panel).to_be_visible()
    packages.hover()
    expect(site_panel).to_be_visible()
    expect(search_panel).to_be_hidden()
    packages.click()
    search.hover()
    expect(site_panel).to_be_visible()
    expect(packages).to_have_attribute("aria-expanded", "true")
    expect(search_panel).to_be_hidden()
    expect(search).to_have_attribute("aria-expanded", "false")
    # Explicit activation can switch away from a pinned panel.
    search.click()
    expect(query).to_be_focused()
    expect(site_panel).to_be_hidden()
    packages.hover()
    expect(search_panel).to_be_visible()
    expect(query).to_be_focused()
    expect(site_panel).to_be_hidden()
    expect(packages).to_have_attribute("aria-expanded", "false")
    packages.click()
    expect(site_panel).to_be_visible()
    expect(search_panel).to_be_hidden()
    page.keyboard.press("Escape")
    expect(site_panel).to_be_hidden()
    expect(packages).to_be_focused()


def test_packages_keyboard_preview_activation_and_dismissal(navigation_page):
    page = navigation_page
    page.goto(ORIGIN)
    toggle = page.get_by_role("button", name="Packages", exact=True)
    shell = page.locator(".site-switcher")
    panel = page.locator("#site-panel")
    for key in ["Enter", "Space"]:
        toggle.focus()
        page.keyboard.press(key)
        expect(shell).to_have_class(re.compile(r"\bis-open\b"))
        page.keyboard.press(key)
        expect(panel).to_be_hidden()
        expect(toggle).to_have_attribute("aria-expanded", "false")
    toggle.hover()
    expect(panel).to_be_visible()
    page.keyboard.press("Tab")
    expect(panel.locator("a").first).to_be_focused()
    expect(shell).to_have_class(re.compile(r"\bis-open\b"))
    page.mouse.move(5, 800)
    expect(panel).to_be_visible()
    page.keyboard.press("Escape")
    expect(panel).to_be_hidden()
    expect(toggle).to_be_focused()
    toggle.click()
    page.locator(".main h1").click()
    expect(panel).to_be_hidden()
    toggle.hover()
    panel.get_by_role("link", name="Core", exact=True).click()
    expect(page).to_have_url(ORIGIN + "/guide/nested/")


@pytest.mark.browser_context_args(has_touch=True)
def test_packages_touch_activation(navigation_page):
    page = navigation_page
    page.set_viewport_size({"width": 390, "height": 900})
    page.goto(ORIGIN)
    toggle = page.get_by_role("button", name="Packages", exact=True)
    panel = page.locator("#site-panel")
    page.locator(".site-switcher").dispatch_event("pointerenter", {"pointerType": "touch"})
    expect(panel).to_be_hidden()
    toggle.tap()
    expect(panel).to_be_visible()
    expect(page.locator(".site-switcher")).to_have_class(re.compile(r"\bis-open\b"))
    toggle.tap()
    expect(panel).to_be_hidden()
    expect(toggle).to_have_attribute("aria-expanded", "false")


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
    expect(panel).to_be_visible()
    expect(page.locator(".site-switcher")).to_have_class(re.compile(r"\bis-preview\b"))
    page.mouse.move(5, 800)
    expect(panel).to_be_hidden()
    expect(toggle).to_have_attribute("aria-expanded", "false")


@pytest.mark.parametrize("width", [1440, 851, 850, 700, 601, 600, 390, 320])
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
    for button in [page.locator(".header-btn--repo"), toggle, search]:
        label = button.locator(".header-btn__label")
        if width <= 850:
            expect(label).to_be_hidden()
            expect(button).to_have_css("width", "34px")
            expect(button).to_have_css("height", "34px")
        else:
            expect(label).to_be_visible()
    arrow = toggle.locator(".site-switcher__arrow")
    if width <= 850:
        expect(arrow).to_be_hidden()
    else:
        expect(arrow).to_be_visible()
    expect(page.locator(".brand__name")).to_have_css("white-space", "nowrap")
    assert page.locator(".brand").bounding_box()["height"] == pytest.approx(17, abs=1)
    page.mouse.click(5, 500)
    expect(panel).to_be_hidden()
    expect(toggle).to_have_attribute("aria-expanded", "false")


@pytest.mark.parametrize("width", [850, 700, 390, 320])
@pytest.mark.parametrize("repo,packages", [(False, False), (True, False), (False, True), (True, True)])
def test_compact_toolbar_does_not_depend_on_optional_buttons(navigation_page, width, repo, packages):
    page = navigation_page
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(ORIGIN)
    page.evaluate("document.fonts.ready")
    # Exercise each optional-control combination against the same built page.
    if not repo:
        page.locator(".header-btn--repo").evaluate("element => element.remove()")
    if not packages:
        page.locator(".site-switcher").evaluate("element => element.remove()")
    brand = page.locator(".brand")
    expect(brand).to_have_text("ML-PIPES-SUPERVISION")
    assert brand.bounding_box()["height"] == pytest.approx(17, abs=1)
    for label in page.locator(".header-right .header-btn__label").all():
        expect(label).to_be_hidden()
    search = page.get_by_role("button", name="SEARCH", exact=True)
    expect(search).to_be_visible()
    expect(search).to_have_attribute("title", "Search documentation")
    expect(search).to_have_css("width", "34px")
    expect(search).to_have_css("height", "34px")
    toolbar = page.locator(".header-right").bounding_box()
    brand_bounds = brand.bounding_box()
    assert brand_bounds["x"] + brand_bounds["width"] + 10 <= toolbar["x"] + 0.1
    assert toolbar["x"] + toolbar["width"] <= width - 2
    assert page.locator(".header").evaluate("element => element.scrollWidth <= element.clientWidth")
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


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
