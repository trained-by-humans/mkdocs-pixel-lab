# Colors

Set the shared palette in the `theme` block of `mkdocs.yml`. Override only the
tokens you need; omitted tokens keep their defaults.

The examples below show Pixel Lab's default colors—the same palette used on
this documentation website. Match each setting to what you see here, then
replace its value to customize your own site.

## Brand colors

```yaml
theme:
  name: pixel-lab
  header_background: "#4caf50"       # Leaf green: header background
  accent_color: "#4caf50"            # Leaf green: selected tabs and controls
  accent_dark_color: "#287c35"       # Dark green: links and active navigation
  accent_foreground_color: "#101410" # Near-black: text on accents
```

| Parameter | Default | Effect |
| --- | --- | --- |
| `header_background` | Leaf green · `#4caf50` | Header background; accepts a color or CSS background such as a gradient |
| `accent_color` | Leaf green · `#4caf50` | Selected content tabs, accent-filled controls, and navigation markers |
| `accent_dark_color` | Dark green · `#287c35` | Links, active navigation text, and icon hover shadows |
| `accent_foreground_color` | Near-black · `#101410` | Site-name text and text on accent-filled controls |
| `header_border_color` | Dark green via `var(--accent-dark)` | Header's lower border; follows `accent_dark_color` unless overridden |
| `header_shadow_color` | Dark green via `var(--accent-dark)` | Header shadow; follows `accent_dark_color` unless overridden |

Color options accept CSS colors, including `rgba()` and CSS variables. Quote
hex values so YAML doesn't treat `#` as the beginning of a comment.

## Set shared surfaces and text

```yaml
theme:
  name: pixel-lab
  background_color: "#f4f1df"  # Warm cream: page background
  surface_color: "#fffdf2"     # Ivory: panels and buttons
  surface_alt_color: "#e8e4cf" # Pale khaki: table headers and tab strips
  text_color: "#182018"        # Dark green-gray: body text
  strong_text_color: "#101410" # Near-black: control labels
  muted_text_color: "#5f665d"  # Gray-green: secondary text
  border_color: "#101410"      # Near-black: outlines
  shadow_color: "#101410"      # Near-black: pixel shadows
```

| Parameter | Default | Effect |
| --- | --- | --- |
| `background_color` | Warm cream · `#f4f1df` | Page background |
| `surface_color` | Ivory · `#fffdf2` | Buttons, panels, and component bodies |
| `surface_alt_color` | Pale khaki · `#e8e4cf` | Table headers, tab strips, and unfocused search input |
| `text_color` | Dark green-gray · `#182018` | Body text |
| `strong_text_color` | Near-black · `#101410` | Toolbar and copy-button labels |
| `muted_text_color` | Gray-green · `#5f665d` | Secondary text and unselected labels |
| `border_color` | Near-black · `#101410` | Component frames and dividers |
| `shadow_color` | Near-black · `#101410` | Offset component shadows, not the separately configured header shadow |
| `subtle_border_color` | Near-black at 30% · `rgba(16, 20, 16, 0.3)` | Table cell rules |
| `sidebar_border_color` | Near-black at 25% · `rgba(16, 20, 16, 0.25)` | Desktop sidebar divider |
| `grid_color` | Near-black at 3.5% · `rgba(16, 20, 16, 0.035)` | Background grid lines |
| `overlay_color` | Near-black at 45% · `rgba(16, 20, 16, 0.45)` | Scrim behind the mobile navigation drawer |

See [Common attributes](../reference/configuration.md#common-attributes).
Check text contrast, hover states, and keyboard focus when changing a palette.

## Customize a component

Each component guide explains exactly which shared and specific colors it uses:

| Component | Appearance settings |
| --- | --- |
| [Text and lists](../components/text.md#customization) | Text, links, quotation rails, and inline code |
| [Code blocks](../components/code-blocks.md#customization) | Code background, text, and syntax colors |
| [Alerts](../components/alerts.md#customization) | Semantic rails, titles, and backgrounds |
| [Admonitions](../components/admonitions.md#customization) | Title fill, body surface, border, and shadow |
| [Content tabs](../components/tabs.md#customization) | Selected tab, hover, labels, and panel surfaces |
| [Collapsible content](../components/details.md#customization) | Summary fill, border, and shadow |
| [Tables](../components/tables.md#customization) | Header fill, rules, border, and shadow |
| [Images and video](../components/media.md#customization) | Media surfaces, frames, and shadows |

For section-link colors, see [Heading permalinks](heading-permalinks.md#further-customization).

For every token and its default, see [Configuration](../reference/configuration.md#theme-defaults).
Pixel Lab currently has one configured palette, not a runtime light/dark switch.
