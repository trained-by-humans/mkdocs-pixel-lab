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

## Palette

Every theme color is configured from the single `theme:` block in `mkdocs.yml`.
The default palette preserves Pixel Lab’s original appearance; override only
the tokens your site needs:

```yaml
theme:
  name: pixel-lab

  # Brand
  header_background: "#8315F9"
  accent_color: "#8315F9"
  accent_dark_color: "#5E0AAE"
  accent_foreground_color: "#FFFFFF"

  # Neutrals used by every component
  background_color: "#f4f1df"
  surface_color: "#fffdf2"
  surface_alt_color: "#e8e4cf"
  text_color: "#182018"
  muted_text_color: "#5f665d"
  border_color: "#101410"
  shadow_color: "#101410"
```

`header_background` accepts any CSS background value, including a linear
gradient. All other options accept any valid CSS color, including `rgba()` and
CSS variables.

| Tokens | Used for |
| --- | --- |
| `background_color`, `surface_color`, `surface_alt_color` | Page, cards, input, and table surfaces. |
| `text_color`, `strong_text_color`, `muted_text_color` | Body, control, and secondary text. |
| `border_color`, `shadow_color`, `subtle_border_color`, `sidebar_border_color` | Component outlines, offset shadows, table rules, and navigation dividers. |
| `grid_color`, `overlay_color` | Page grid and mobile-navigation scrim. |
| `header_background`, `accent_color`, `accent_dark_color`, `accent_foreground_color` | Header, links, navigation, active states, and accent-filled controls. |
| `highlight_color`, `secondary_color`, `input_focus_background_color`, `inline_code_border_color`, `tab_hover_color` | Interactive controls, badges, inline code, and hover states. |
| `code_background_color`, `code_text_color`, `code_keyword_color`, `code_string_color`, `code_function_color`, `code_comment_color` | Code block and syntax-highlight colors. |
| `alert_note_color`, `alert_note_surface_color`, `alert_tip_color`, `alert_tip_surface_color`, `alert_important_color`, `alert_important_surface_color`, `alert_warning_color`, `alert_warning_surface_color`, `alert_caution_color`, `alert_caution_surface_color` | GitHub Alert rails, titles, and surfaces. |

This separation lets a site change its border and shadow independently without
having to maintain CSS overrides or edit the theme.

## GitHub Alerts

Enable GitHub-style Markdown alerts explicitly when a site uses them:

```yaml
markdown_extensions:
  - mkdocs_pixel_lab.github_alerts
```

The extension supports `NOTE`, `TIP`, `IMPORTANT`, `WARNING`, and `CAUTION`:

```markdown
> [!TIP]
>
> Use semantic callouts for important guidance.
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
