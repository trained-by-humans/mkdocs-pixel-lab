"""Real Git history and sitemap integration, without build-date fallbacks."""

from __future__ import annotations

import gzip
import os
from pathlib import Path
import subprocess
from xml.etree import ElementTree

from mkdocs.commands.build import build
from mkdocs.config import load_config
from mkdocs.plugins import BasePlugin, event_priority
from mkdocs.structure.files import File
import pytest

from mkdocs_pixel_lab.git_lastmod import GitLastModified


FIXTURE = Path(__file__).parent / "fixture_site" / "mkdocs.yml"
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def git(directory, *arguments, committed=None, authored=None):
    env = os.environ.copy()
    if committed:
        env["GIT_COMMITTER_DATE"] = f"{committed}T12:00:00+00:00"
        env["GIT_AUTHOR_DATE"] = f"{authored or committed}T12:00:00+00:00"
    return subprocess.run(
        [
            "git", "-C", str(directory),
            "-c", "user.name=Fixture Author", "-c", "user.email=fixture@example.invalid",
            "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *arguments,
        ],
        check=True, capture_output=True, text=True, env=env,
    ).stdout.strip()


def commit(directory, path, content, committed, *, authored=None):
    destination = directory / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
    git(directory, "add", "--", path)
    git(directory, "commit", "-qm", f"Update {path}", committed=committed, authored=authored)
    return destination


@pytest.fixture
def repository(tmp_path):
    git(tmp_path, "init", "-q")
    commit(tmp_path, "docs/index.md", "# Home\n\nAn introduction.\n", "2021-02-03")
    return tmp_path


def test_dates_belong_to_each_file_not_the_latest_repository_commit(repository):
    guide = commit(repository, "docs/guide.md", "# Guide\n", "2022-03-04", authored="2020-01-01")
    commit(repository, "README.md", "Unrelated change.\n", "2023-04-05")
    dates = GitLastModified(repository / "docs")
    assert dates.date_for(repository / "docs/index.md") == "2021-02-03"
    assert dates.date_for(guide) == "2022-03-04"


def test_uncommitted_edits_keep_the_last_committed_date(repository):
    source = repository / "docs/index.md"
    source.write_text("# Uncommitted update\n", encoding="utf-8")
    assert GitLastModified(repository / "docs").date_for(source) == "2021-02-03"


def test_renamed_source_uses_its_git_history(repository):
    git(repository, "mv", "docs/index.md", "docs/renamed.md")
    git(repository, "commit", "-qm", "Rename source", committed="2022-05-06")
    assert GitLastModified(repository / "docs").date_for(repository / "docs/renamed.md") == "2022-05-06"


def test_paths_are_literal_not_git_wildcards(repository):
    source = commit(repository, "docs/guide[1] with spaces.md", "# Literal\n", "2022-01-02")
    commit(repository, "docs/guide1 with spaces.md", "# Other file\n", "2023-01-02")
    assert GitLastModified(repository / "docs").date_for(source) == "2022-01-02"


def test_untracked_generated_and_outside_sources_have_no_date(repository):
    untracked = repository / "docs/untracked.md"
    untracked.write_text("# Untracked\n", encoding="utf-8")
    dates = GitLastModified(repository / "docs")
    assert dates.date_for(untracked) is None
    assert dates.date_for(None) is None
    assert dates.date_for(repository.parent / "outside.md") is None
    git(repository, "rm", "--cached", "docs/index.md")
    assert GitLastModified(repository / "docs").date_for(repository / "docs/index.md") is None


def test_non_repository_and_empty_history_have_no_date(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    source = docs / "index.md"
    source.write_text("# Page\n", encoding="utf-8")
    assert GitLastModified(docs).date_for(source) is None
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "docs/index.md")
    assert GitLastModified(docs).date_for(source) is None


@pytest.mark.parametrize("failure", [FileNotFoundError(), subprocess.TimeoutExpired("git", 10)])
def test_unavailable_git_does_not_break_the_build(tmp_path, monkeypatch, failure):
    def unavailable(*args, **kwargs):
        raise failure

    monkeypatch.setattr("mkdocs_pixel_lab.git_lastmod.subprocess.run", unavailable)
    assert GitLastModified(tmp_path).date_for(tmp_path / "index.md") is None


def test_shallow_clone_omits_potentially_inaccurate_dates(repository):
    commit(repository, "README.md", "Latest unrelated commit.\n", "2023-01-02")
    clone = repository / "shallow-clone"
    git(repository, "clone", "--depth=1", repository.as_uri(), str(clone))
    assert git(clone, "rev-parse", "--is-shallow-repository") == "true"
    assert GitLastModified(clone / "docs").date_for(clone / "docs/index.md") is None


def test_cache_is_per_build(repository, monkeypatch):
    from mkdocs_pixel_lab import git_lastmod

    source = repository / "docs/index.md"
    dates = GitLastModified(repository / "docs")
    assert dates.date_for(source) == "2021-02-03"
    original = git_lastmod._git
    calls = []

    def recorded(*args):
        calls.append(args)
        return original(*args)

    monkeypatch.setattr(git_lastmod, "_git", recorded)
    assert dates.date_for(source) == "2021-02-03"
    assert calls == []
    commit(repository, "docs/index.md", "# Updated\n", "2024-06-07")
    assert GitLastModified(repository / "docs").date_for(source) == "2024-06-07"


def site_config(directory, nav, *, plugins=None):
    return load_config(
        config_file=str(FIXTURE), docs_dir=str(directory / "docs"), site_dir=str(directory / "site"),
        nav=nav, plugins=plugins if plugins is not None else ["search", "pixel-lab/git-lastmod"],
        site_name="Git Dates",
        site_url="https://example.invalid/docs/", strict=True,
    )


def sitemap_dates(directory):
    xml = (directory / "site/sitemap.xml").read_bytes()
    with gzip.open(directory / "site/sitemap.xml.gz", "rb") as compressed:
        assert compressed.read() == xml
    return {
        url.findtext(f"{SITEMAP_NS}loc"): url.findtext(f"{SITEMAP_NS}lastmod")
        for url in ElementTree.fromstring(xml).findall(f"{SITEMAP_NS}url")
    }


def test_sitemap_uses_git_dates_and_refreshes_between_builds(repository):
    commit(repository, "docs/guide.md", "# Guide\n", "2022-03-04")
    (repository / "docs/new.md").write_text("# New untracked page\n", encoding="utf-8")
    config = site_config(repository, [{"Home": "index.md"}, {"Guide": "guide.md"}, {"New": "new.md"}])
    build(config)
    expected = {
        "https://example.invalid/docs/": "2021-02-03",
        "https://example.invalid/docs/guide/": "2022-03-04",
        "https://example.invalid/docs/new/": None,
    }
    assert sitemap_dates(repository) == expected
    commit(repository, "README.md", "Unrelated build trigger.\n", "2024-01-02")
    build(config)
    assert sitemap_dates(repository) == expected
    commit(repository, "docs/guide.md", "---\ndate_modified: 1999-01-01\n---\n\n# Updated guide\n", "2025-02-03")
    build(config)
    expected["https://example.invalid/docs/guide/"] = "2025-02-03"
    assert sitemap_dates(repository) == expected


def test_sitemap_without_git_history_omits_lastmod(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("# Page\n\nIntroduction.\n", encoding="utf-8")
    build(site_config(tmp_path, [{"Home": "index.md"}]))
    assert sitemap_dates(tmp_path) == {"https://example.invalid/docs/": None}


def test_sitemap_from_shallow_clone_omits_lastmod(repository):
    clone = repository / "shallow-clone"
    git(repository, "clone", "--depth=1", repository.as_uri(), str(clone))
    build(site_config(clone, [{"Home": "index.md"}]))
    assert sitemap_dates(clone) == {"https://example.invalid/docs/": None}


def test_generated_pages_keep_canonical_urls_without_dates(repository):
    class GeneratedPagePlugin(BasePlugin):
        def on_files(self, files, *, config):
            files.append(File.generated(config, "generated.md", content="# Generated page\n"))
            return files

    config = site_config(repository, [{"Home": "index.md"}, {"Generated": "generated.md"}])
    config.plugins["fixture-generated"] = GeneratedPagePlugin()
    build(config)
    assert sitemap_dates(repository) == {
        "https://example.invalid/docs/": "2021-02-03",
        "https://example.invalid/docs/generated/": None,
    }


def test_without_git_plugin_sitemap_preserves_mkdocs_defaults(repository):
    from mkdocs.utils import get_build_date

    config = site_config(repository, [{"Home": "index.md"}], plugins=["search"])
    build(config)
    assert sitemap_dates(repository) == {"https://example.invalid/docs/": get_build_date()}


@pytest.mark.parametrize("plugins", [
    ["search"],
    ["search", "pixel-lab/metadata"],
    ["search", "pixel-lab/git-lastmod"],
    ["search", "pixel-lab/metadata", "pixel-lab/git-lastmod"],
    ["search", "pixel-lab/git-lastmod", "pixel-lab/metadata"],
])
def test_plugins_work_independently_and_in_either_order(repository, plugins):
    from mkdocs.utils import get_build_date

    class PageAudit(BasePlugin):
        @event_priority(-200)
        def on_page_context(self, context, *, page, config, nav):
            assert ("pixel_lab_metadata" in context) == ("pixel-lab/metadata" in plugins)
            assert hasattr(page, "pixel_lab_lastmod") == ("pixel-lab/git-lastmod" in plugins)
            if "pixel-lab/metadata" in plugins:
                assert context["pixel_lab_metadata"] == {"title": "Home", "description": "An introduction."}
            return context

    config = site_config(repository, [{"Navigation label": "index.md"}], plugins=plugins)
    config.plugins["fixture-page-audit"] = PageAudit()
    build(config)
    expected = "2021-02-03" if "pixel-lab/git-lastmod" in plugins else get_build_date()
    assert sitemap_dates(repository) == {"https://example.invalid/docs/": expected}
