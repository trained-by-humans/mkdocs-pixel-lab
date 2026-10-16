"""Keep documentation validation separate from privileged Pages deployment."""

from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
MAIN_ONLY = "${{ github.ref == 'refs/heads/main' && github.event_name != 'pull_request' }}"


@pytest.fixture(scope="module")
def docs_workflow() -> dict:
    # BaseLoader keeps GitHub's `on` key intact instead of treating it as a
    # YAML 1.1 boolean. Workflow scalar values are sufficient as strings here.
    return yaml.load(
        (ROOT / ".github/workflows/deploy-docs.yml").read_text(),
        Loader=yaml.BaseLoader,
    )


def test_docs_workflow_validates_prs_and_main(docs_workflow: dict) -> None:
    triggers = docs_workflow["on"]
    assert set(triggers) == {"pull_request", "push", "workflow_dispatch"}
    assert triggers["push"]["branches"] == ["main"]
    assert docs_workflow["permissions"] == {"contents": "read"}
    build = docs_workflow["jobs"]["build"]
    assert "if" not in build and "permissions" not in build
    checkout = next(step for step in build["steps"] if step.get("uses", "").startswith("actions/checkout@"))
    assert "ref" not in checkout.get("with", {})


def test_docs_workflow_tests_the_checked_out_theme(docs_workflow: dict) -> None:
    steps = docs_workflow["jobs"]["build"]["steps"]
    commands = [step["run"] for step in steps if "run" in step]
    install = "python -m pip install -e '.[test]'"
    tests = "python -m pytest tests/test_documentation.py tests/test_docs_workflow.py -q"
    build = "python -m mkdocs build --strict"
    assert commands.index(install) < commands.index(tests) < commands.index(build)
    assert commands.index(build) < commands.index("git diff --exit-code")


def test_docs_artifact_matches_the_public_site(docs_workflow: dict) -> None:
    steps = docs_workflow["jobs"]["build"]["steps"]
    upload = next(step for step in steps if step.get("uses", "").startswith("actions/upload-pages-artifact@"))
    config = yaml.safe_load((ROOT / "mkdocs.yml").read_text())
    assert upload["with"]["path"] == config["site_dir"] == "build/docs"
    assert upload["if"] == MAIN_ONLY


def test_docs_deployment_is_main_only_and_least_privileged(docs_workflow: dict) -> None:
    deploy = docs_workflow["jobs"]["deploy"]
    assert deploy["needs"] == "build"
    assert deploy["if"] == MAIN_ONLY
    assert deploy["permissions"] == {
        "contents": "read", "pages": "write", "id-token": "write",
    }
    assert deploy["environment"] == {
        "name": "github-pages", "url": "${{ steps.deployment.outputs.page_url }}",
    }
    assert all("run" not in step for step in deploy["steps"])
    assert deploy["steps"][-1]["id"] == "deployment"
    assert deploy["steps"][-1]["uses"].startswith("actions/deploy-pages@")


def test_docs_concurrency_does_not_interrupt_deployments(docs_workflow: dict) -> None:
    assert docs_workflow["concurrency"] == {
        "group": "pages-${{ github.event.pull_request.number || github.ref }}",
        "cancel-in-progress": "false",
    }
