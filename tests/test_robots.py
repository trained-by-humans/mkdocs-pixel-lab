"""Static robots output, correct sitemap URLs, and site-owned crawl rules."""

from pathlib import Path

from mkdocs.commands.build import build
from mkdocs.config import load_config
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File
import pytest


FIXTURE = Path(__file__).parent / "fixture_site" / "mkdocs.yml"


def site_config(directory, *, site_url="https://example.invalid/", plugins=None):
    docs = directory / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "index.md").write_text("# Robots fixture\n\nA public introduction.\n", encoding="utf-8")
    config = load_config(
        config_file=str(FIXTURE), docs_dir=str(docs), site_dir=str(directory / "site"),
        nav=[{"Home": "index.md"}], site_name="Robots Site", site_url=site_url,
        plugins=plugins if plugins is not None else ["search", "pixel-lab/robots"], strict=True,
    )
    # load_config ignores None overrides, so explicitly clear the fixture URL.
    if site_url is None:
        config.site_url = None
    return config


@pytest.mark.parametrize("site_url, sitemap", [
    ("https://ml-pipes.com/", "https://ml-pipes.com/sitemap.xml"),
    ("https://supervision.ml-pipes.com/", "https://supervision.ml-pipes.com/sitemap.xml"),
    ("https://ultralytics.ml-pipes.com/", "https://ultralytics.ml-pipes.com/sitemap.xml"),
    ("https://example.invalid", "https://example.invalid/sitemap.xml"),
    ("https://example.invalid/project/", "https://example.invalid/project/sitemap.xml"),
    ("https://example.invalid/project", "https://example.invalid/project/sitemap.xml"),
])
def test_generated_robots_uses_site_sitemap_url(tmp_path, site_url, sitemap):
    build(site_config(tmp_path, site_url=site_url))
    content = (tmp_path / "site/robots.txt").read_text(encoding="utf-8")
    assert content == f"User-agent: *\nAllow: /\n\nSitemap: {sitemap}\n"
    assert "{{" not in content
    assert (tmp_path / "site/sitemap.xml").is_file()
    assert (tmp_path / "site/sitemap.xml.gz").is_file()


def test_missing_site_url_does_not_emit_an_invalid_sitemap(tmp_path):
    build(site_config(tmp_path, site_url=None))
    assert (tmp_path / "site/robots.txt").read_text(encoding="utf-8") == "User-agent: *\nAllow: /\n"


def test_existing_robots_is_copied_unchanged(tmp_path):
    config = site_config(tmp_path)
    content = b"# Custom crawl policy\r\nUser-agent: *\r\nDisallow: /drafts/\r\n"
    (tmp_path / "docs/robots.txt").write_bytes(content)
    build(config)
    assert (tmp_path / "site/robots.txt").read_bytes() == content


def test_another_plugins_robots_file_takes_priority(tmp_path):
    content = "User-agent: *\nDisallow: /\n"

    class ExistingRobotsPlugin(BasePlugin):
        def on_files(self, files, *, config):
            files.append(File.generated(config, "robots.txt", content=content))
            return files

    config = site_config(tmp_path)
    config.plugins["fixture-robots"] = ExistingRobotsPlugin()
    build(config)
    assert (tmp_path / "site/robots.txt").read_text(encoding="utf-8") == content


def test_robots_generation_is_opt_in(tmp_path):
    build(site_config(tmp_path, plugins=["search"]))
    assert not (tmp_path / "site/robots.txt").exists()


def test_robots_plugin_does_not_run_git(tmp_path, monkeypatch):
    def unexpected_git(*args):
        pytest.fail("The robots-only plugin must not run Git commands")

    monkeypatch.setattr("mkdocs_pixel_lab.git_lastmod._git", unexpected_git)
    build(site_config(tmp_path))
    assert (tmp_path / "site/robots.txt").is_file()


def test_robots_works_alongside_metadata_and_git_dates(tmp_path):
    build(site_config(tmp_path, plugins=[
        "search", "pixel-lab/metadata", "pixel-lab/git-lastmod", "pixel-lab/robots",
    ]))
    assert (tmp_path / "site/robots.txt").read_text(encoding="utf-8") == (
        "User-agent: *\nAllow: /\n\nSitemap: https://example.invalid/sitemap.xml\n"
    )
    html = (tmp_path / "site/index.html").read_text(encoding="utf-8")
    assert "<title>Robots fixture — Robots Site</title>" in html
    assert 'content="A public introduction."' in html
    assert "<lastmod>" not in (tmp_path / "site/sitemap.xml").read_text(encoding="utf-8")


def test_rebuild_uses_the_current_site_url(tmp_path):
    config = site_config(tmp_path)
    build(config)
    config.site_url = "https://new.example.invalid/docs/"
    build(config)
    assert (tmp_path / "site/robots.txt").read_text(encoding="utf-8") == (
        "User-agent: *\nAllow: /\n\nSitemap: https://new.example.invalid/docs/sitemap.xml\n"
    )
