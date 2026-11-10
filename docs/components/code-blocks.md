# Code blocks

Fenced code supports syntax highlighting, emphasized lines, horizontal
scrolling, and a copy button.

## Enable

```yaml
markdown_extensions:
  - pymdownx.superfences
  - pymdownx.highlight
```

## Write a code block

```python
def greet(name):
    # A small example with syntax colors.
    return f"Hello, {name}!"

print(greet("Pixel Lab"))
```

````markdown
```python
def greet(name):
    # A small example with syntax colors.
    return f"Hello, {name}!"

print(greet("Pixel Lab"))
```
````

Set the language after the opening fence. Code keeps its whitespace and
scrolls horizontally when a line is wider than the available space.

## Emphasize lines

```{ .python hl_lines="2" }
import math
print(math.pi)
```

````markdown
```{ .python hl_lines="2" }
import math
print(math.pi)
```
````

## Copy behavior

The copy button is added by the theme's JavaScript and reports success or
failure. Without JavaScript, the code remains readable and selectable.
Clipboard access may depend on the browser and a secure context such as
HTTPS or localhost.

## Customization

Use the properties and selectors below to customize this component, following the
[Customization](customization.md) guide.

### Component properties

These CSS variables take their default values from the corresponding theme settings.

| Property | Description | Theme setting | Default |
| --- | --- | --- | --- |
| `--code` | Code block background | `code_background_color` | Near-black · `#101410` |
| `--code-text` | Default code text | `code_text_color` | Pale green · `#e9f1d8` |
| `--code-keyword` | Styled keywords | `code_keyword_color` | Light green · `#72d572` |
| `--code-string` | Styled strings | `code_string_color` | Golden yellow · `#f5cf54` |
| `--code-function` | Function names | `code_function_color` | Cyan · `#4cc4d2` |
| `--code-comment` | Comments | `code_comment_color` | Gray-green · `#7f8978` |
| `--highlight` | Emphasized-line tint and copy-button hover/focus background | `highlight_color` | Golden yellow · `#f5c842` |
| `--surface` | Copy-button background | `surface_color` | Ivory · `#fffdf2` |
| `--strong-text` | Copy-button text | `strong_text_color` | Near-black · `#101410` |
| `--accent` | Successful-copy button background | `accent_color` | Leaf green · `#4caf50` |
| `--accent-foreground` | Successful-copy button text | `accent_foreground_color` | Near-black · `#101410` |
| `--accent-dark` | Copy-button hover/focus outline | `accent_dark_color` | Dark green · `#287c35` |
| `--border` | Block and copy-button outlines | `border_color` | Near-black · `#101410` |
| `--shadow` | Block's pixel shadow | `shadow_color` | Near-black · `#101410` |

Syntax colors apply to the Pygments token classes styled by the theme, not
every possible token independently. Inline code has separate surface and border
styles; see [Text and lists](text.md#customization).

See [Colors](../setup/colors.md) for palette configuration and
[Fonts](../setup/fonts.md) for typography defaults and overrides.

### Component styles

Use these selectors to style the code area, highlighted tokens, and copy button.

| Selector | CSS properties | Description |
| --- | --- | --- |
| `pre, .highlight pre` | `background`, `color`, `font-family`, `font-size`, `padding`, `border`, `box-shadow` | The code area, its typography, inset, and frame |
| `.highlight .k, .highlight .kn, .highlight .kd` | `color` | Keyword tokens |
| `.highlight .s, .highlight .sa, .highlight .s1, .highlight .s2` | `color` | String tokens |
| `.highlight .nf, .highlight .fm` | `color` | Function-name tokens |
| `.highlight .c, .highlight .c1, .highlight .cm` | `color` | Comment tokens |
| `.highlight .hll` | `background` | The tint behind emphasized lines |
| `.code-copy` | `background`, `color`, `border`, `font-family`, `padding`, `top`, `right` | The copy button and its position inside the code block |
| `.code-copy:hover, .code-copy:focus-visible` | `background`, `outline` | Copy-button hover and keyboard-focus appearance |
| `.code-copy.is-copied` | `background`, `color` | The copy button after a successful copy |
