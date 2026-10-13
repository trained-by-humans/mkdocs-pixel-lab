"""Page actions follow MkDocs' source mapping without guessing output paths."""

from html import unescape
from io import StringIO
from pathlib import Path
import re

from mkdocs.commands.build import build
from mkdocs.config import load_config
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File
import pytest
import yaml


FIXTURE = Path(__file__).parent / "fixture_site" / "mkdocs.yml"
REPOSITORY = "https://github.com/trained-by-humans/pixel-lab-fixture"


def actions(html):
    return {
        label: unescape(url)
        for url, label in re.findall(
            r'<a class="(?:page-source|page-edit)" href="([^"]*)" aria-label="([^"]*)"', html,
        )
    }


@pytest.mark.parametrize("show_edit", [None, False])
def test_repository_settings_use_native_mkdocs_defaults(tmp_path, show_edit):
    settings = yaml.safe_load(FIXTURE.read_text())
    settings.pop("edit_uri")
    if show_edit is not None:
        settings["theme"]["show_edit"] = show_edit
    config = load_config(
        config_file=StringIO(yaml.safe_dump(settings)), config_file_path=str(FIXTURE),
        site_dir=str(tmp_path), strict=True,
    )
    assert config.edit_uri == "edit/master/docs/"
    assert config.theme["show_edit"] is (show_edit is not False)
    build(config)
    html = (tmp_path / "guide/nested/index.html").read_text()
    expected = {"View source": f"{REPOSITORY}/blob/master/docs/guide/nested.md"}
    if show_edit is not False:
        expected["Edit this page"] = f"{REPOSITORY}/edit/master/docs/guide/nested.md"
    assert actions(html) == expected


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
            "Edit this page": f"{REPOSITORY}/{edit_uri}{source}",
        }
        assert html.index('class="page-source"') < html.index("<h1") < html.index('<footer class="footer">')


@pytest.mark.parametrize("show_source", [True, False])
def test_source_icon_can_be_hidden(tmp_path, show_source):
    config = load_config(config_file=str(FIXTURE), site_dir=str(tmp_path), strict=True)
    config.theme["show_source"] = show_source
    build(config)
    html = (tmp_path / "index.html").read_text()
    assert ("View source" in actions(html)) == show_source
    assert actions(html)["Edit this page"] == f"{REPOSITORY}/edit/main/docs/index.md"
    assert ('class="page-source"' in html) == show_source


@pytest.mark.parametrize("show_source", [True, False])
@pytest.mark.parametrize("show_edit", [True, False])
@pytest.mark.parametrize("directory_urls", [True, False])
def test_edit_and_source_actions_are_independent(tmp_path, show_source, show_edit, directory_urls):
    config = load_config(
        config_file=str(FIXTURE), site_dir=str(tmp_path),
        use_directory_urls=directory_urls, strict=True,
    )
    config.theme["show_source"] = show_source
    config.theme["show_edit"] = show_edit
    build(config)
    output = "guide/nested/index.html" if directory_urls else "guide/nested.html"
    html = (tmp_path / output).read_text()
    expected = {}
    if show_source:
        expected["View source"] = f"{REPOSITORY}/blob/main/docs/guide/nested.md"
    if show_edit:
        expected["Edit this page"] = f"{REPOSITORY}/edit/main/docs/guide/nested.md"
        assert html.index('class="page-edit"') < html.index("<h1")
    assert actions(html) == expected


@pytest.mark.parametrize("repository,editor,expected", [
    ("https://gitlab.com/owner/repo", "-/edit/main/docs/", "https://gitlab.com/owner/repo/-/edit/main/docs/guide/nested.md"),
    ("https://git.example.org/owner/repo", "editor/docs/", "https://git.example.org/owner/repo/editor/docs/guide/nested.md"),
])
def test_edit_link_preserves_other_providers(tmp_path, repository, editor, expected):
    config = load_config(
        config_file=str(FIXTURE), site_dir=str(tmp_path),
        repo_url=repository, edit_uri=editor, strict=True,
    )
    build(config)
    html = (tmp_path / "guide/nested/index.html").read_text()
    assert actions(html) == {"Edit this page": expected}


def test_edit_link_preserves_custom_template_and_escaping(tmp_path):
    config = load_config(
        config_file=str(FIXTURE), site_dir=str(tmp_path), edit_uri="",
        edit_uri_template="https://editor.example.org/?file={path}&ref=release/v2",
        site_url="https://example.invalid/project/docs/", strict=True,
    )
    config.repo_url = None
    build(config)
    html = (tmp_path / "guide/nested/index.html").read_text()
    assert actions(html) == {
        "Edit this page": "https://editor.example.org/?file=guide/nested.md&ref=release/v2",
    }
    assert "?file=guide/nested.md&amp;ref=release/v2" in html


@pytest.mark.parametrize("repo_url,edit_uri", [(None, None), (REPOSITORY, "")])
@pytest.mark.parametrize("show_edit", [False, True])
def test_missing_or_disabled_links_omit_the_source_icon(tmp_path, repo_url, edit_uri, show_edit):
    config = load_config(config_file=str(FIXTURE), site_dir=str(tmp_path), strict=True)
    config.repo_url = repo_url
    config.edit_uri = edit_uri
    config.theme["show_edit"] = show_edit
    build(config)
    html = (tmp_path / "index.html").read_text()
    assert not actions(html)
    assert 'class="page-source"' not in html
    assert 'class="page-edit"' not in html


def test_other_hosts_get_native_edit_link_but_no_inferred_source(tmp_path):
    config = load_config(
        config_file=str(FIXTURE), site_dir=str(tmp_path),
        repo_url="https://gitlab.com/owner/repo", edit_uri="-/edit/main/docs/", strict=True,
    )
    build(config)
    html = (tmp_path / "guide/nested/index.html").read_text()
    assert actions(html) == {
        "Edit this page": "https://gitlab.com/owner/repo/-/edit/main/docs/guide/nested.md",
    }


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
        "Edit this page": "https://github.com/edit/blob/edit/v2/manual/guide/nested.md?plain=1&from=docs",
    }
    assert "?plain=1&amp;from=docs" in html


@pytest.mark.parametrize("source_mapping", [None, "../src/operators.py"])
@pytest.mark.parametrize("show_edit", [False, True])
def test_generated_pages_require_an_explicit_source_mapping(tmp_path, source_mapping, show_edit):
    class GeneratedPagePlugin(BasePlugin):
        def on_files(self, files, *, config):
            generated = File.generated(config, "generated.md", content="# Generated reference\n")
            generated.edit_uri = source_mapping
            files.append(generated)
            return files

    config = load_config(config_file=str(FIXTURE), site_dir=str(tmp_path), strict=True)
    config.theme["show_edit"] = show_edit
    config.plugins["fixture-generated"] = GeneratedPagePlugin()
    build(config)
    links = actions((tmp_path / "generated/index.html").read_text())
    if source_mapping is None:
        assert links == {}
    else:
        expected = {
            "View source": f"{REPOSITORY}/blob/main/src/operators.py",
        }
        if show_edit:
            expected["Edit this page"] = f"{REPOSITORY}/edit/main/src/operators.py"
        assert links == expected
