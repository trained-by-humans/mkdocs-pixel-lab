"""The toolbar repository link is independent of per-page actions."""

from html import unescape
from pathlib import Path
import re

from mkdocs.commands.build import build
from mkdocs.config import load_config
import pytest


FIXTURE = Path(__file__).parent / "fixture_site" / "mkdocs.yml"
REPOSITORY = "https://github.com/trained-by-humans/pixel-lab-fixture"


@pytest.mark.parametrize("repo_url,show_repo,edit_uri,show_actions", [
    (REPOSITORY, None, "edit/main/docs/", True),
    (REPOSITORY, None, "", False),
    (REPOSITORY, True, "", True),
    (REPOSITORY, False, "edit/main/docs/", True),
    (None, None, None, True),
    ("", True, "", True),
    (None, True, "https://github.com/owner/repo/edit/main/docs/", True),
])
def test_repository_button_visibility(tmp_path, repo_url, show_repo, edit_uri, show_actions):
    config = load_config(config_file=str(FIXTURE), site_dir=str(tmp_path), strict=True)
    config.repo_url = repo_url
    config.edit_uri = edit_uri
    config.theme["show_source"] = show_actions
    config.theme["show_edit"] = show_actions
    assert config.theme["show_repo"] is True
    if show_repo is not None:
        config.theme["show_repo"] = show_repo
    build(config)
    for path in ("index.html", "guide/nested/index.html"):
        html = (tmp_path / path).read_text()
        enabled = bool(repo_url) and show_repo is not False
        assert html.count('class="header-btn header-btn--repo"') == int(enabled)
        if enabled:
            assert f'href="{repo_url}" aria-label="Open repository:' in html
            assert html.index('class="header-btn header-btn--repo"') < html.index('id="search-toggle"')
        if repo_url and edit_uri and show_actions:
            assert 'class="page-edit"' in html
        if not repo_url and edit_uri and show_actions:
            # A standalone absolute edit URI does not create a toolbar repo link.
            assert 'class="page-edit"' in html
            assert 'class="page-source"' in html
    assert (tmp_path / "assets/icons/repository.svg").is_file()


@pytest.mark.parametrize("repo_url,repo_name,label", [
    ("https://github.com/owner/repo", "GitHub", "GitHub"),
    ("https://gitlab.com/owner/repo", "GitLab", "GitLab"),
    ("https://bitbucket.org/owner/repo", "Bitbucket", "Bitbucket"),
    ("https://git.example.org/owner/repo", None, "Repository"),
    ('https://git.example.org/?project=repo&ref=main', 'My "code" & docs', 'My "code" & docs'),
])
def test_repository_button_supports_providers_and_custom_labels(tmp_path, repo_url, repo_name, label):
    config = load_config(
        config_file=str(FIXTURE), site_dir=str(tmp_path), repo_url=repo_url, strict=True,
    )
    config.repo_name = repo_name
    build(config)
    html = (tmp_path / "index.html").read_text()
    link = re.search(
        r'<a class="header-btn header-btn--repo" href="([^"]*)" aria-label="([^"]*)" title="([^"]*)">(.*?)</a>',
        html, re.S,
    )
    assert link is not None
    assert unescape(link[1]) == repo_url
    assert unescape(link[2]) == f"Open repository: {label}"
    assert link[3] == link[2]
    label_match = re.search(r'<span class="header-btn__label">([^<]*)</span>', link[4])
    assert label_match is not None
    assert unescape(label_match[1]) == label
