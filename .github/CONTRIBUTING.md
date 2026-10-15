# Contributing

Thanks for contributing to `mkdocs-pixel-lab`.

## Development setup

Clone the repository, create and activate a Python 3.10+ virtual environment,
then install the theme in editable mode with its test dependencies:

```bash
git clone https://github.com/trained-by-humans/mkdocs-pixel-lab.git
cd mkdocs-pixel-lab
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m playwright install chromium
```

On Windows PowerShell, activate the environment with
`.venv\Scripts\Activate.ps1` instead. On Linux, Chromium may also need system
dependencies; use `python -m playwright install --with-deps chromium`.

Run the commands below from the repository root.

## Repository layout

| What to change | Location |
| --- | --- |
| Templates, palette defaults, CSS, JavaScript, and bundled assets | [`src/mkdocs_pixel_lab/`](../src/mkdocs_pixel_lab/) |
| Public documentation and site configuration | [`docs/`](../docs/) and [`mkdocs.yml`](../mkdocs.yml) |
| Automated tests | [`tests/`](../tests/) |
| Representative component examples | [`tests/fixture_site/`](../tests/fixture_site/) |
| README screenshots | [`tests/snapshots/`](../tests/snapshots/) |
| CI, documentation deployment, and releases | [`workflows/`](workflows/) |

## Local preview

The commands below print the local preview URL and reload when theme templates
or assets change. Check desktop and mobile layouts, keyboard navigation,
focus styles, and reduced-motion behavior when relevant. Local previews
don't collect analytics.

If the default port is busy, append `--dev-addr 127.0.0.1:8010` to either
command and open `http://127.0.0.1:8010`. Choose another available port if
needed; `127.0.0.1` keeps the preview local to your machine.

### Documentation website

The public theme manual lives in `docs/` and uses the root `mkdocs.yml`.

```bash
python -m mkdocs serve --watch-theme
```

### Test fixture

The fixture site exercises the theme's navigation, Markdown components, and
media layouts. It is a development and test site, not the published manual.

```bash
python -m mkdocs serve --config-file tests/fixture_site/mkdocs.yml --watch-theme
```

## Validation

Run the full suite before submitting a change:

```bash
python -m pytest -q
```

The suite builds documentation and fixture sites and runs headless Chromium
checks. Add or update tests for behavior changes. While developing, run a
focused module:

```bash
python -m pytest tests/test_theme.py -q
```

### Documentation checks

Validate the manual's pages, examples, internal links, and deployment workflow:

```bash
python -m mkdocs build --strict
python -m pytest tests/test_documentation.py tests/test_docs_workflow.py -q
```

### Fixture build

Validate the component fixture separately:

```bash
python -m mkdocs build --strict --config-file tests/fixture_site/mkdocs.yml
```

CI tests Python 3.10, 3.11, 3.12, and 3.13. It also builds the wheel and source
distribution, checks them with `twine check`, and strictly builds the fixture
using the wheel installed in a clean environment.

### Preview screenshots

The README uses `tests/snapshots/desktop.png` and
`tests/snapshots/mobile.png`. Normal test runs capture screenshots in temporary
directories without replacing these files.

Only refresh the committed screenshots when the visual change is intentional:

```bash
UPDATE_SNAPSHOTS=1 python -m pytest tests/test_theme.py -q
```

Review both images before including them in a pull request. These screenshots
are reviewable previews, not automatic pixel-diff assertions.

## Documentation guidelines

### Organize guides

- Keep site-wide configuration in **Theme setup**, including heading permalinks.
- Keep Markdown syntax, component behavior, and component-specific appearance
  in **Components**, even when appearance settings live under `theme`.
  Ordinary Markdown heading syntax belongs in **Text and lists**.
- Explain main configuration beside the example that enables or defines the
  feature. Use **Further customization** for optional appearance refinements
  in setup guides, and **Customization** in component guides.
- Don't repeat feature-enabling settings or content fields in customization
  sections. Features without appearance options, such as metadata, don't need
  an appearance section.
- For features with multiple presentations, explain presentation-specific
  artwork alongside that presentation. Keep common appearance attributes in
  the final customization section.

### Configuration examples

- Use **Parameter / Default / Effect** tables beside the relevant instructions,
  with color names beside values and component-specific effects.
- Keep configuration defaults aligned with the theme; tests check Reference
  against the implementation.
- Introduce MkDocs settings and CSS through their use and configuration path.
  Reserve explicit "not a theme option" contrasts for meaningful limitations.
- When an example builds on an earlier snippet, use `hl_lines` to highlight
  added or changed options and leave repeated context unhighlighted.

### CSS overrides

Keep theme settings first under Customization, followed by **Component-wide
overrides** for CSS targeting all instances and **Scoped overrides** for
selected instances. Wrapper classes can be reused for one or several instances.

Both CSS scopes use `extra_css`; an HTML wrapper supplies a styling target,
not a different styling mechanism. Link to the
[Components overview](../docs/components/index.md#customization-scopes) for
stylesheet and `md_in_html` setup.

### Shared guidance

Give common guidance one home and link to it elsewhere, keeping only the
brief context needed locally. Keep component-specific settings with their
component.

Link to [Common attributes](../docs/reference/configuration.md#common-attributes)
for shared theme settings rather than repeating explanations of colors,
fonts, and icons.

Document nested-shadow behavior in the Components overview. Keep a brief note
in relevant container guides, not in child-content guides such as media and
code blocks.

## Pull requests

Keep changes focused and describe what changed, why, and how you verified it.
Include before-and-after screenshots for visible layout or styling changes.

Keep new styling configurable through the existing palette instead of
introducing per-component hard-coded colors. Update the relevant guide when
public configuration or user-facing behavior changes, and extend the fixture
when a new component needs a representative example. Keep `README.md` focused
on the overview, quick start, and guide links.

Do not commit virtual environments, generated sites, or distribution artifacts.

## Publishing

### GitHub Pages

[deploy-docs.yml](workflows/deploy-docs.yml) validates documentation on pull
requests and pushes to `main`. After validation, main-branch runs publish
`build/docs` to GitHub Pages. You can also run the workflow manually from `main`.
Pull requests and manual runs on other branches validate without deploying.

For the initial repository setup, select **GitHub Actions** under
**Settings → Pages → Build and deployment → Source**.

### Package releases

Coordinate version bumps, release tags, and publishing with the maintainers;
normal contributions do not require PyPI credentials.
