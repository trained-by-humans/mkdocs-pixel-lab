# Contributing

## Set up your checkout

Use Python 3.10 or newer. Clone the repository and install the theme in editable
mode with its test dependencies:

```bash
git clone https://github.com/trained-by-humans/mkdocs-pixel-lab.git
cd mkdocs-pixel-lab
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m playwright install chromium
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. On Linux,
use `python -m playwright install --with-deps chromium` if browser system
dependencies are missing. Run the remaining commands from the repository root.

### Where changes belong

- [Theme source](../src/mkdocs_pixel_lab/): templates, palette defaults, CSS,
  JavaScript, fonts, icons, and plugins.
- [Public documentation](../docs/) and [site configuration](../mkdocs.yml):
  user guides and live examples.
- [Tests](../tests/) and [fixture site](../tests/fixture_site/): automated
  checks and examples used to exercise the theme.
- [Workflows](workflows/): CI, documentation deployment, and releases.

## Check your changes

For code or behavior changes, run the full suite before submitting:

```bash
python -m pytest -q
```

The suite builds sites and runs headless Chromium checks. During development,
you can focus on a module with `python -m pytest tests/test_theme.py -q`.

For CI workflow changes, run `python -m pytest tests/test_ci_workflow.py -q`.

To check the fixture build on its own:

```bash
python -m mkdocs build --strict --config-file tests/fixture_site/mkdocs.yml
```

### Review visual changes

Check desktop and mobile layouts, keyboard navigation, focus styles, and
reduced-motion behavior. Include before-and-after screenshots with visual PRs.

Browser tests normally save screenshots to temporary directories. To update
the saved desktop and mobile review images in `tests/snapshots/`:

```bash
UPDATE_SNAPSHOTS=1 python -m pytest tests/test_theme.py -q
```

Review both images before committing them. They are review screenshots, not
automatic pixel-diff assertions.

## Preview the test fixture

```bash
python -m mkdocs serve --config-file tests/fixture_site/mkdocs.yml --watch-theme
```

The fixture exercises navigation, components, and media separately from the
published manual. Preview servers print a local URL and reload after changes.
If the port is busy, append `--dev-addr 127.0.0.1:8010` and use the printed URL.
Local previews don't collect analytics.

## Update documentation

### Documentation website

Preview the public manual locally:

```bash
python -m mkdocs serve --watch-theme
```

Build the site and run its documentation and Pages workflow checks:

```bash
python -m mkdocs build --strict
python -m pytest tests/docs -q
```

### Structure and examples

- Put site-wide settings in **Theme setup**. Put component syntax, behavior,
  and appearance in **Components**. Ordinary Markdown headings belong in
  **Text and lists**; permalink settings belong in **Theme setup**.
- Explain how to enable and use a feature beside its live example. Keep
  `README.md` focused on the overview, quick start, highlights, and guide links.
- Use **Customization** for component appearance and **Further customization**
  for optional refinements in setup guides. Keep shared appearance settings
  together; explain presentation-specific artwork beside its presentation.
- Document parameters with **Parameter / Default / Effect** tables, including
  color names and component-specific effects. Match defaults to the theme.
- When extending a configuration example, use `hl_lines` to highlight only
  the added or changed options. Keep enabling settings in the setup section.
  Features without appearance settings, such as metadata, don't need a
  Customization section.

### Styling and shared guidance

- Use the existing palette to keep new styling configurable.
- In Customization, put theme settings first, then **Component-wide overrides**,
  then **Scoped overrides**. Both CSS scopes use `extra_css`; reusable wrapper
  classes select instances. Link to
  [Customization scopes](../docs/components/index.md#customization-scopes) for
  stylesheet and `md_in_html` setup.
- Give shared guidance one home. Link to
  [Common attributes](../docs/reference/configuration.md#common-attributes)
  instead of repeating shared color, font, and icon settings.
- Explain nested shadows in the Components overview, with brief notes in
  container guides. Keep that guidance out of child-content guides such as
  media and code blocks.

## Submit a pull request

Keep changes focused. Explain what changed, why, and how you checked it.
Update the relevant guide when user-facing behavior changes, extend fixture
examples for new components, and add regression tests for behavior changes.

Keep virtual environments, generated sites, and distribution artifacts out
of commits.

## Workflow summary

### CI

[CI](workflows/ci.yml) tests Python 3.10–3.13, validates distribution artifacts,
and builds the fixture using the installed wheel.

Excluded paths: `docs/**`, `tests/docs/**`, root `mkdocs.yml`,
`.github/CONTRIBUTING.md`, and `RELEASING.md`.

| Event | Result |
| --- | --- |
| PR targeting `main` or push to `main`: all changed files are excluded | Skip |
| PR targeting `main` or push to `main`: any other file changes | Run full CI |
| Release staging calls CI | Always run full CI |

### Pages

[Pages](workflows/deploy-docs.yml) validates and builds the public manual.
Relevant inputs are `docs/**`, `tests/docs/**`, `src/mkdocs_pixel_lab/**`,
`assets/**`, `mkdocs.yml`, `pyproject.toml`, `README.md`, and the Pages workflow.

| Event | Build and validate | Deploy site |
| --- | --- | --- |
| PR or `main` push with only unrelated changes | Skip | No |
| PR with any relevant change | Run | No |
| Push to `main` with any relevant change | Run | Yes |
| Manual run from `main` | Run | Yes |
| Manual run from another branch | Run | No |

PR filters use the overall PR diff. Any `pyproject.toml` edit counts, including
version-only bumps. Deployment follows successful validation.

For initial Pages setup, select **GitHub Actions** under
**Settings → Pages → Build and deployment → Source**.

### Stage

[Stage](workflows/stage-release.yml) prepares release artifacts and verifies
their installation from TestPyPI.

| Event | Result |
| --- | --- |
| Push a `v<version>` tag matching `pyproject.toml` | Run full CI, stage GitHub Release assets, publish to TestPyPI, and verify installation |

### Release

[Release](workflows/publish-release.yml) promotes the staged artifacts to PyPI.

| Event | Result |
| --- | --- |
| Manual run from a successfully staged release tag | Verify staging and artifact checksums, then publish to PyPI |

Coordinate releases with the maintainers and follow [Releasing](../RELEASING.md)
for staging and promotion. Normal contributions don't require PyPI credentials.
