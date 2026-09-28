# Pixel Lab

Pixel Lab is a vibrant, accessible theme for [MkDocs](https://www.mkdocs.org/).

## Quick start

```bash
python -m pip install mkdocs-pixel-lab
```

Use it in `mkdocs.yml`:

```yaml
theme:
  name: pixel-lab
```

## Site colors

Pixel Lab keeps its layout and neutral palette consistent while allowing a site
to set its own identity colors:

```yaml
theme:
  name: pixel-lab
  header_background: "#8315F9"
  accent_color: "#8315F9"
  accent_dark_color: "#5E0AAE"
  accent_foreground_color: "#FFFFFF"
```

`header_background` accepts any CSS background value, including a linear
gradient. `accent_color` and `accent_dark_color` are used for navigation,
links, headings, and interactive states; `accent_foreground_color` is used for
text on the header and accent-filled controls.

Pixel Lab includes responsive navigation, search, code-copy controls, heading
fragment tracking, a skip link, and styling for standard MkDocs and Pymdown
content.

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

## Development

```bash
python -m pip install -e '.[test]'
playwright install chromium
pytest
```
