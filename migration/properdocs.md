# Pixel Lab → ProperDocs migration

Companion to the [successor evaluation](README.md). Assessed
2026-10-25 against Pixel Lab 0.2.0 (`d48084c`), ProperDocs 1.6.7 and Python
3.12/macOS. This guide preserves those findings; versions and tests have not
been rechecked during the editorial cleanup.

## Goal and status

Move our documentation to a maintained continuation of MkDocs while preserving
Pixel Lab's templates, plugins, configuration, authored URLs and existing MkDocs
consumers. This is the proposed first migration step before considering a
broader framework change.

ProperDocs builds our fixture and documentation, and selected API tests pass.
**Search does not work with the unchanged theme.** Its loader expects
`properdocs-search-query` / `properdocs-search-results`, while our markup and
JavaScript use `mkdocs-search-query` / `mkdocs-search-results`. A small integration
fix and compatibility CI are required before claiming supported operation.
No production dependencies, theme code or workflows were migrated by this guide.

## Benefits and limits

These benefits are documented in ProperDocs releases 1.6.5–1.6.7. Our selected
builds and tests ran on 1.6.7; we did not independently reproduce every upstream
bug.

- **Existing integrations carry forward:** supports MkDocs and ProperDocs entry
  points and old logger names. Its CLI bridges `mkdocs.*` imports; programmatic
  callers must initialize that bridge before importing our plugins or tests.
- **More reliable local development:** fixes live reload being disabled by
  default with Click newer than 8.2.1, plus serve/reload crashes when configuration
  comes from stdin. The first fix directly helps theme iteration; stdin is not
  part of our current workflow.
- **Better validation and robustness:** preserves anchor warnings in verbose
  mode and fixes crashes while parsing invalid URLs. This supports our existing
  documentation checks without adding a new rendering model.
- **A path to newer Python versions:** officially supports Python 3.14. Our own
  CI currently covers 3.10–3.13, and this evaluation tested only 3.12.
- **Dependency cleanup:** removes ProperDocs' dependency on the unmaintained
  `mergedeep` package. Our current hard dependency on MkDocs still pulls it in;
  realizing that benefit fully needs a packaging change.
- **Independent theme packaging:** the built-in MkDocs/ReadTheDocs themes are
  separate packages, neither required by Pixel Lab. Fixes to those themes'
  dark mode and dropdowns do not change our frontend.

These improvements make ProperDocs a useful maintenance step. They do not add
missing Pixel Lab UI features or resolve the confirmed search selector mismatch.

## Implementation plan

### 1. Make search work with both engines

Add an integration that connects each engine's loader to Pixel Lab's search
markup. Keep the existing UI, and preserve both input and result handling.
Changing the HTML IDs alone also affects our own JavaScript, so update and test
the complete interaction.

Verify real results on home and nested pages, project-subpath URLs, empty/no-result
queries, Escape, mobile interaction and focus return. The generated-output
experiment below confirms the cause; it is not a source fix to ship.

### 2. Add engine-specific CI and package support

- Add a ProperDocs job, initially on Python 3.12, with explicit CLI commands and
  the import bridge initialized before API tests. Keep the existing MkDocs jobs.
- Verify a normal resolver install, `pip check`, strict docs/fixture builds,
  browser search and the built wheel. Expand interpreter coverage before
  advertising support across our Python 3.10–3.13 matrix.
- Document an install path, such as an optional ProperDocs extra. Existing theme
  and plugin entry points do not need renaming. Our current mandatory MkDocs
  dependency means both engines initially remain installed.

**Gate:** installable artifacts and documented commands pass CI, including
browser behavior; a strict build alone is insufficient.

### 3. Switch documentation publishing

- Keep `mkdocs.yml`, Markdown extensions, navigation, theme options and plugin
  names. Renaming the file to `properdocs.yml` is optional.
- Use `properdocs build --strict` in the Pages build job after search and CI pass.
  Keep `site_dir: build/docs` aligned with the existing artifact upload path.
- Keep the existing Pages artifact/deploy actions. Retain `fetch-depth: 0` when
  Git-derived modification dates are enabled.
- Confirm live page/asset URLs, canonical tags, sitemap, robots policy and search
  under the GitHub Pages project subpath.

**Gate:** the deployed site preserves authored URLs and behavior. Keep the
MkDocs build/configuration available for existing consumers and rollback.

### 4. Reassess a broader migration only if needed

Identify remaining product needs and compare another framework's benefits with
its porting cost. The [Zensical migration guide](zensical.md) records
one such option; adopting ProperDocs does not require that subsequent move.

## Runtime evidence

All installations and experimental adaptations were confined to
`/private/tmp/pixel-lab-successors`. Normal project dependencies were preserved.

| Check | Result |
| --- | --- |
| ProperDocs strict build: `tests/fixture_site/mkdocs.yml` | **Pass** |
| ProperDocs strict build: repository `mkdocs.yml` | **Pass** |
| Metadata, Git last-modified, and robots tests under the ProperDocs import bridge | **67 passed** |
| Documentation tests under the same bridge | **44 passed** |
| Fixture output comparison against MkDocs | Both contain **28 files**, identical paths; only `search/main.js` differs in bytes. That difference changes DOM selectors |
| Browser smoke: unchanged MkDocs fixture | Search query `highlighting` returns **2 results**; mobile menu opens/closes with Escape; no JS errors |
| Browser smoke: unchanged ProperDocs fixture | **Fail**: search produces no results because its loader targets different element IDs |
| Browser smoke: temporary ProperDocs output with search selector names adapted | **Pass**: same 2 results, mobile interaction passes, no JS errors |

The selected 111 tests cover plugin and documentation behavior, not the full
browser suite or the complete Python support matrix. The temporary search edit
was made to generated output to confirm the cause; it is not a shippable source
fix or an upstream fix.

## Reproduce the evaluation

Run from the repository root with Python 3.12. These commands create a separate
environment and write build output under a fresh temporary directory. They
exercise the current theme, including its known search mismatch.

```sh
properdocs_preview_root="$(mktemp -d /tmp/pixel-lab-properdocs.XXXXXX)"
python3.12 -m venv "$properdocs_preview_root/venv"
"$properdocs_preview_root/venv/bin/python" -m pip install 'properdocs==1.6.7' -e '.[test]'
"$properdocs_preview_root/venv/bin/python" -m pip check

"$properdocs_preview_root/venv/bin/properdocs" build --strict \
  --config-file tests/fixture_site/mkdocs.yml \
  --site-dir "$properdocs_preview_root/fixture"
"$properdocs_preview_root/venv/bin/properdocs" build --strict \
  --config-file mkdocs.yml \
  --site-dir "$properdocs_preview_root/docs"

"$properdocs_preview_root/venv/bin/python" -c 'import properdocs.replacement; import pytest; raise SystemExit(pytest.main(["tests/test_metadata.py", "tests/test_git_lastmod.py", "tests/test_robots.py", "tests/test_documentation.py", "-q"]))'
```

Import `properdocs.replacement` **before** pytest imports the test files. Otherwise
our existing `mkdocs.*` API tests exercise the installed MkDocs engine, producing
misleading compatibility evidence. The ProperDocs CLI activates the bridge for
normal builds automatically.

### Inspect the generated site

```sh
"$properdocs_preview_root/venv/bin/python" -m http.server 8000 \
  --directory "$properdocs_preview_root/fixture"
```

Open `http://localhost:8000/` and `/guide/code/`. Check navigation, source/edit
links, components, keyboard behavior and the browser console. Searching for
`highlighting` should expose the known failure in the unchanged build.
The development command becomes `properdocs serve --config-file mkdocs.yml`
after implementing the integration; the static server above lets us inspect
exactly the output generated by the evaluation commands.

### Confirm the search mismatch in a disposable build

Stop the static server, then adapt only the temporary fixture's loader:

```sh
"$properdocs_preview_root/venv/bin/python" - "$properdocs_preview_root/fixture/search/main.js" <<'PYCODE'
from pathlib import Path
import sys

loader = Path(sys.argv[1])
source = loader.read_text()
assert 'properdocs-search-' in source, 'Expected ProperDocs 1.6.7 search loader'
loader.write_text(source.replace('properdocs-search-', 'mkdocs-search-'))
PYCODE
```

Restart the static server and hard-refresh the browser. Search again from home
and a nested page; the recorded fixture smoke returned two results for
`highlighting`, with working mobile navigation and no JavaScript exceptions.
A normal rebuild overwrites this edit. Production support must implement the
integration in source and verify it in CI.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Strict builds pass but search returns nothing | Check the loader's input/result IDs against our HTML and JavaScript; see the disposable experiment above |
| Tests pass without testing ProperDocs | Initialize `properdocs.replacement` before importing pytest/test modules and use the `properdocs` CLI explicitly |
| Both MkDocs and ProperDocs are installed | Expected with Pixel Lab's current mandatory MkDocs dependency; choose the engine through its command/bridge |
| Default theme is missing | Pixel Lab uses `theme.name: pixel-lab`; ProperDocs' separate built-in theme packages are unnecessary for this theme |
| Python 3.14 is supported upstream but unverified here | Add our own interpreter/component/browser coverage before claiming Pixel Lab support |

## Rollback

For evaluation, stop the local server and return to the existing MkDocs
environment and commands. The source files and production build configuration
remain unchanged.

After a future production cutover, revert the dependency/workflow changes and
rebuild the prior site with MkDocs. Keep output paths and authored URLs stable
so the previous artifact can be redeployed without a content migration.

## Sources

- [ProperDocs maintainer's continuation and migration statement](https://github.com/orgs/ProperDocs/discussions/33)
- [ProperDocs release notes](https://properdocs.org/about/release-notes/)
- [ProperDocs 1.6.7 release](https://github.com/ProperDocs/properdocs/releases/tag/v1.6.7)
- [ProperDocs source](https://github.com/ProperDocs/properdocs)
