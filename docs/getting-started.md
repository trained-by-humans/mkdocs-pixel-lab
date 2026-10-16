# Get started

Pixel Lab is a theme for [MkDocs](https://www.mkdocs.org/), not a separate site
generator. You need Python 3.10 or newer. Installing the theme also installs
MkDocs, Pymdown Extensions, and Pygments.

## Install

Use a virtual environment for your documentation project:

```bash
python -m venv .venv
```

=== "macOS / Linux"

    ```bash
    source .venv/bin/activate
    ```

=== "Windows PowerShell"

    ```powershell
    .venv\Scripts\Activate.ps1
    ```

Then install Pixel Lab:

```bash
python -m pip install mkdocs-pixel-lab
```

## Enable the theme

For a new site, run `mkdocs new .` in an empty project directory. For an
existing site, keep your current files and navigation.

Merge this into your site's `mkdocs.yml`:

```yaml
site_name: My documentation
theme:
  name: pixel-lab
```

## Enable rich Markdown

Enable the extensions your pages use:

```yaml
markdown_extensions:
  - admonition
  - mkdocs_pixel_lab.github_alerts
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.highlight
  - pymdownx.tabbed:
      alternate_style: true
  - md_in_html
```

Each [component guide](components/index.md) lists its required extensions and
Markdown syntax.

## Preview and build

```bash
mkdocs serve
```

Open <http://127.0.0.1:8000/>. MkDocs rebuilds the preview as you edit.

Before publishing, validate your site:

```bash
mkdocs build --strict
```

For hosting options, follow [MkDocs deployment documentation](https://www.mkdocs.org/user-guide/deploying-your-docs/).

## Next steps

- [Set up your theme](setup/index.md): appearance and site-wide behavior.
- [Explore components](components/index.md): live examples and Markdown.
- [Check compatibility](reference/compatibility.md): requirements and limitations.
- [Troubleshoot a problem](reference/troubleshooting.md): configuration and rendering fixes.

## Preview this documentation from a checkout

To preview or contribute to this website, follow the
[contributor guide](https://github.com/trained-by-humans/mkdocs-pixel-lab/blob/main/.github/CONTRIBUTING.md#documentation-website).
