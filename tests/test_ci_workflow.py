"""Skip expensive CI for documentation-only edits while retaining release checks."""

from fnmatch import fnmatchcase
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def ci_workflow() -> dict:
    return yaml.load(
        (ROOT / ".github/workflows/ci.yml").read_text(),
        Loader=yaml.BaseLoader,
    )


def test_ci_filters_prs_and_main_consistently(ci_workflow: dict) -> None:
    triggers = ci_workflow["on"]
    assert set(triggers) == {"pull_request", "push", "workflow_call"}
    assert triggers["pull_request"]["branches"] == triggers["push"]["branches"] == ["main"]
    assert triggers["pull_request"]["paths-ignore"] == triggers["push"]["paths-ignore"]


@pytest.mark.parametrize("event", ["pull_request", "push"])
@pytest.mark.parametrize(("changed_paths", "should_run"), [
    (["docs/index.md"], False),
    (["docs/components/cards.md", "docs/assets/component-preview.svg", "mkdocs.yml"], False),
    ([".github/CONTRIBUTING.md", "RELEASING.md"], False),
    (["docs/index.md", ".github/CONTRIBUTING.md"], False),
    (["docs/components/cards.md", "src/mkdocs_pixel_lab/assets/css/style.css"], True),
    (["docs/index.md", "tests/fixture_site/docs/guide/cards.md"], True),
    (["docs/index.md", "pyproject.toml"], True),
    (["tests/test_theme.py"], True),
    (["tests/docs/test_site.py", "tests/docs/test_workflow.py"], False),
    (["tests/docs/test_new_guide.py"], False),
    (["tests/docs/test_site.py", "tests/test_theme.py"], True),
    (["tests/test_ci_workflow.py"], True),
    (["README.md"], True),
    (["LICENSE", "THIRD_PARTY_LICENSES.md"], True),
    (["assets/pixel-lab-logo.svg"], True),
    ([".github/workflows/ci.yml"], True),
    ([".github/workflows/stage-release.yml"], True),
])
def test_ci_only_skips_when_all_changes_are_documentation(
    ci_workflow: dict, event: str, changed_paths: list[str], should_run: bool,
) -> None:
    ignored = ci_workflow["on"][event]["paths-ignore"]
    assert any(
        not any(fnmatchcase(path, pattern) for pattern in ignored)
        for path in changed_paths
    ) == should_run


def test_release_staging_always_calls_full_ci(ci_workflow: dict) -> None:
    # Trigger path filters apply to push/PR events, not reusable workflow calls.
    assert "workflow_call" in ci_workflow["on"]
    assert all("if" not in job for job in ci_workflow["jobs"].values())
    staging = yaml.load(
        (ROOT / ".github/workflows/stage-release.yml").read_text(),
        Loader=yaml.BaseLoader,
    )
    assert staging["jobs"]["ci"]["uses"] == "./.github/workflows/ci.yml"
    assert "if" not in staging["jobs"]["ci"]
    assert staging["jobs"]["stage"]["needs"] == "ci"
