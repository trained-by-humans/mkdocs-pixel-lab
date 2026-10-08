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
