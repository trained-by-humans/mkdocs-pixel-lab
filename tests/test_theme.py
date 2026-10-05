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
