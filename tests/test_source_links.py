"""Source icons follow MkDocs' source mapping without guessing output paths."""

from html import unescape
from pathlib import Path
import re

from mkdocs.commands.build import build
from mkdocs.config import load_config
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File
import pytest


FIXTURE = Path(__file__).parent / "fixture_site" / "mkdocs.yml"
REPOSITORY = "https://github.com/trained-by-humans/pixel-lab-fixture"


def actions(html):
    return {
        label: unescape(url)
        for url, label in re.findall(
            r'<a class="page-source" href="([^"]*)" aria-label="([^"]*)"', html,
        )
    }


@pytest.mark.parametrize("edit_uri", ["edit/main/docs/", "blob/main/docs/", "edit/release/v2/manual/"])
@pytest.mark.parametrize("directory_urls", [True, False])
def test_source_uses_markdown_paths(tmp_path, edit_uri, directory_urls):
    config = load_config(
        config_file=str(FIXTURE), site_dir=str(tmp_path),
        edit_uri=edit_uri, use_directory_urls=directory_urls, strict=True,
    )
    build(config)
    suffix = edit_uri.split("/", 1)[1]
    for output, source in [
        ("index.html", "index.md"),
        ("guide/nested/index.html" if directory_urls else "guide/nested.html", "guide/nested.md"),
    ]:
        html = (tmp_path / output).read_text()
        assert actions(html) == {
            "View source": f"{REPOSITORY}/blob/{suffix}{source}",
        }
        assert "Edit this page" not in html
        assert html.index('class="page-source"') < html.index("<h1") < html.index('<footer class="footer">')


@pytest.mark.parametrize("show_source", [True, False])
def test_source_icon_can_be_hidden(tmp_path, show_source):
    config = load_config(config_file=str(FIXTURE), site_dir=str(tmp_path), strict=True)
    config.theme["show_source"] = show_source
    build(config)
    html = (tmp_path / "index.html").read_text()
    assert ("View source" in actions(html)) == show_source
    assert "Edit this page" not in html
    assert ('class="page-source"' in html) == show_source


@pytest.mark.parametrize("repo_url,edit_uri", [(None, None), (REPOSITORY, "")])
def test_missing_or_disabled_links_omit_the_source_icon(tmp_path, repo_url, edit_uri):
    config = load_config(config_file=str(FIXTURE), site_dir=str(tmp_path), strict=True)
    config.repo_url = repo_url
    config.edit_uri = edit_uri
    build(config)
    html = (tmp_path / "index.html").read_text()
    assert not actions(html)
    assert 'class="page-source"' not in html


def test_other_hosts_do_not_get_an_inferred_source_or_edit_link(tmp_path):
    config = load_config(
        config_file=str(FIXTURE), site_dir=str(tmp_path),
        repo_url="https://gitlab.com/owner/repo", edit_uri="-/edit/main/docs/", strict=True,
    )
    build(config)
    html = (tmp_path / "guide/nested/index.html").read_text()
    assert actions(html) == {}
    assert "Edit this page" not in html


def test_native_uri_template_and_url_escaping(tmp_path):
    config = load_config(
        config_file=str(FIXTURE), site_dir=str(tmp_path), edit_uri="",
        edit_uri_template="https://github.com/edit/blob/edit/v2/manual/{path}?plain=1&from=docs",
        strict=True,
    )
    build(config)
    html = (tmp_path / "guide/nested/index.html").read_text()
    assert actions(html) == {
        "View source": "https://github.com/edit/blob/blob/v2/manual/guide/nested.md?plain=1&from=docs",
    }
    assert "?plain=1&amp;from=docs" in html


@pytest.mark.parametrize("source_mapping", [None, "../src/operators.py"])
def test_generated_pages_require_an_explicit_source_mapping(tmp_path, source_mapping):
    class GeneratedPagePlugin(BasePlugin):
        def on_files(self, files, *, config):
            generated = File.generated(config, "generated.md", content="# Generated reference\n")
            generated.edit_uri = source_mapping
            files.append(generated)
            return files

    config = load_config(config_file=str(FIXTURE), site_dir=str(tmp_path), strict=True)
    config.plugins["fixture-generated"] = GeneratedPagePlugin()
    build(config)
    links = actions((tmp_path / "generated/index.html").read_text())
    if source_mapping is None:
        assert links == {}
    else:
        assert links == {
            "View source": f"{REPOSITORY}/blob/main/src/operators.py",
        }
