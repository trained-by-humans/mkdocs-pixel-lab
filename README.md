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
