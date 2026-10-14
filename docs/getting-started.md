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

Select the theme in `mkdocs.yml`:

```yaml
site_name: My documentation
theme:
  name: pixel-lab
```

## Enable rich Markdown

These extensions power the examples on this website. Enable only the ones
your pages use:

```yaml
plugins:
  - search
markdown_extensions:
  - admonition
  - mkdocs_pixel_lab.github_alerts
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.highlight
  - pymdownx.tabbed:
      alternate_style: true
  - md_in_html
  - toc:
      permalink: true
```

Merge snippets into your existing configuration: use one `theme` block, one
`plugins` list, and one `markdown_extensions` list. When specifying plugins,
keep `search` if you want the built-in search index.

The [component guides](components/index.md) explain which extensions each
component needs and how to write its Markdown.

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
Pixel Lab doesn't require a special hosting service.

## Next steps

- [Set up your theme](setup/index.md): appearance and site-wide behavior.
- [Explore components](components/index.md): live examples and Markdown.
- [Check compatibility](reference/compatibility.md): requirements and limitations.
- [Troubleshoot a problem](reference/troubleshooting.md): configuration and rendering fixes.

## Preview this documentation from a checkout

To work on the theme's own website, run these commands from the repository
root instead of creating another MkDocs project:

```bash
python -m pip install -e .
python -m mkdocs serve --watch-theme
```

The root `mkdocs.yml` builds this website. The separate
`tests/fixture_site/mkdocs.yml` remains a test fixture.
