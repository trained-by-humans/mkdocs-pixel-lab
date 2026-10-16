<p align="center">
  <img src="assets/pixel-lab-logo.svg" alt="Pixel Lab retro logo" width="480">
</p>

<p align="center">
  <a href="https://pypi.org/project/mkdocs-pixel-lab/"><img src="https://img.shields.io/pypi/v/mkdocs-pixel-lab?style=flat-square&amp;logo=pypi&amp;logoColor=white&amp;label=PyPI&amp;color=C48800" alt="Latest PyPI release"></a>
  <a href="https://pypi.org/project/mkdocs-pixel-lab/"><img src="https://img.shields.io/badge/Python-3.10%2B-2377C8?style=flat-square&amp;logo=python&amp;logoColor=white" alt="Python 3.10 or newer"></a>
  <a href="https://github.com/trained-by-humans/mkdocs-pixel-lab/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/mkdocs-pixel-lab?style=flat-square&amp;label=License&amp;color=287C35" alt="Apache 2.0 license"></a>
  <a href="https://www.mkdocs.org/"><img src="https://img.shields.io/badge/MkDocs-%3E%3D1.6%2C%20%3C2-7E46B6?style=flat-square" alt="MkDocs &gt;=1.6, &lt;2"></a>
</p>

<p align="center">
  A retro-inspired theme for <a href="https://www.mkdocs.org/">MkDocs</a>, with pixel borders, bold colors, and arcade-style shadows.<br>
  Built for modern documentation with responsive navigation, search, and rich Markdown components.
</p>

## Preview

<table>
  <tr>
    <td align="center"><img src="tests/snapshots/desktop.png" alt="Pixel Lab desktop documentation preview" height="480"></td>
    <td align="center"><img src="tests/snapshots/mobile.png" alt="Pixel Lab mobile documentation preview" height="480"></td>
  </tr>
  <tr>
    <td align="center">Desktop</td>
    <td align="center">Mobile</td>
  </tr>
</table>

## Demo

Visit [Pixel Lab on GitHub Pages](https://trained-by-humans.github.io/mkdocs-pixel-lab/)
to see the theme in action. The documentation site uses Pixel Lab itself and
includes examples of its components.

## Features

- A tastefully designed, retro-inspired theme with pixel-art assets, crisp borders, and playful shadows.
- Optional metadata, Git-based sitemap dates, and `robots.txt` plugins.
- Opt-in Google Analytics 4 with consent controls.

## Quick start

For an existing MkDocs project, install Pixel Lab:

```bash
python -m pip install mkdocs-pixel-lab
```

Select it in your existing `mkdocs.yml`:

```yaml
theme:
  name: pixel-lab
```

Preview your site:

```bash
mkdocs serve
```

Requires Python 3.10 or newer. Installing Pixel Lab also installs MkDocs,
Pymdown Extensions, and Pygments.

Starting a new project? Follow [Get started](docs/getting-started.md) for
environment setup, a new site, and enabling Markdown extensions.

## Documentation

- [Theme setup](docs/setup/index.md): colors, fonts, icons, branding, navigation, search, repository links, and analytics.
- [Components](docs/components/index.md): Markdown syntax, live examples, required extensions, and appearance settings.
- [Reference](docs/reference/configuration.md): configuration defaults, [bundled plugins](docs/reference/plugins.md), [compatibility](docs/reference/compatibility.md), and [troubleshooting](docs/reference/troubleshooting.md).
- [Upgrading](docs/reference/upgrading.md): migration notes and checks for existing sites.
