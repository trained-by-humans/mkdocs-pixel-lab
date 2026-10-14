# Contributing

Thanks for contributing to `mkdocs-pixel-lab`.
Honestly, just the fact that you opened this page makes me happy! ^^

## Install the repository

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

## Preview the theme

### Documentation website

The public theme manual lives in `docs/` and uses the root `mkdocs.yml`.
Preview it with the editable theme installation:

```bash
python -m mkdocs serve --watch-theme
```

The console prints the local preview URL. Validate its pages, examples, and
internal links with:

```bash
python -m mkdocs build --strict
python -m pytest tests/test_documentation.py -q
```

Put site-wide configuration in Theme setup. Put page-authoring syntax,
component behavior, and component-specific customization together in
Components, even when those appearance settings live under `theme`.
Keep site-wide heading permalink configuration in Theme setup and ordinary
Markdown heading syntax in Text and lists.
Cross-link shared colors/fonts rather than duplicating their full guides.
Explain main configuration beside the example that enables or defines the
feature. Use Further customization for optional appearance refinements in
feature setup guides, and Customization in component guides. Don't repeat
feature-enabling settings or content fields there. Don't add an appearance
section to features with no appearance options, such as page metadata.
For features with multiple presentations, explain presentation-specific
artwork alongside that presentation and keep shared appearance attributes
in the final customization section.
Use Parameter / Default / Effect tables beside the relevant
instructions, with color names beside values and component-specific effects.
Link to Common attributes in the configuration reference instead of repeating
explanations of shared theme settings. Distinguish native MkDocs settings and
CSS from theme options.
Configuration defaults in Reference are checked against the theme by tests.

In visible component guides, keep theme settings first under Customization.
Use Component-wide overrides for CSS targeting all instances, and Scoped
overrides for wrapper-scoped CSS targeting selected instances.
Explain that the wrapper class can be reused for one or several instances.
Both CSS scopes use `extra_css`;
don't describe an HTML wrapper or native HTML authoring as a different styling
mechanism. Link to the Components overview for stylesheet and `md_in_html` setup.

Give common guidance one home and link to it from other pages. Document nested
shadow behavior in the Components overview, with a brief note in relevant
container guides; don't repeat it in child-content guides such as media and
code blocks. Keep component-specific settings with their component.

### Test fixture

The fixture site exercises the theme's navigation, Markdown components, and
media layouts. Preview it using the editable installation:

```bash
python -m mkdocs serve --config-file tests/fixture_site/mkdocs.yml --watch-theme
```

Open `http://127.0.0.1:8000` in a browser. The `--watch-theme` option reloads
the preview when theme templates or assets change. Check both desktop and
mobile layouts, keyboard navigation, focus styles, and reduced-motion behavior
when relevant.

If port `8000` is already in use, choose another available port with
`--dev-addr` (or `-a`). For example, to use port `8010`:

```bash
python -m mkdocs serve --config-file tests/fixture_site/mkdocs.yml --watch-theme --dev-addr 127.0.0.1:8010
```

Then open `http://127.0.0.1:8010`. Replace `8010` with your preferred available
port; keeping `127.0.0.1` limits the preview to your own machine.

Validate the static site before submitting documentation or theme changes:

```bash
python -m mkdocs build --strict --config-file tests/fixture_site/mkdocs.yml
```

The fixture is a development and test site, not a separately deployed theme
documentation portal. Local previews do not collect analytics.

## Tests

Run the full suite before submitting a change:

```bash
python -m pytest -q
```

The suite builds fixture sites and runs headless Chromium checks. Add or update
tests in `tests/` for behavior changes. While developing, run a focused module:

```bash
python -m pytest tests/test_theme.py -q
```

CI tests Python 3.10, 3.11, 3.12, and 3.13. It also builds the wheel and source
distribution, checks them with `twine check`, and strictly builds the fixture
using the wheel installed in a clean environment.

## Preview screenshots

The README uses `tests/snapshots/desktop.png` and
`tests/snapshots/mobile.png`. Normal test runs capture screenshots in temporary
directories without replacing these files.

Only refresh the committed screenshots when the visual change is intentional:

```bash
UPDATE_SNAPSHOTS=1 python -m pytest tests/test_theme.py -q
```

Review both images before including them in a pull request. These screenshots
are reviewable previews, not automatic pixel-diff assertions.

## Pull requests

Keep changes focused and describe what changed, why, and how you verified it.
Include before-and-after screenshots for visible layout or styling changes.

Theme templates, palette defaults, CSS, JavaScript, and bundled assets live in
`src/mkdocs_pixel_lab/`. Keep new styling configurable through the existing
palette instead of introducing per-component hard-coded colors. Update
`README.md` when public configuration or user-facing behavior changes, and
extend `tests/fixture_site/` when a new component needs a representative
example.

Do not commit virtual environments, generated sites, or distribution artifacts.
Coordinate version bumps, release tags, and publishing with the maintainers;
normal contributions do not require PyPI credentials.
