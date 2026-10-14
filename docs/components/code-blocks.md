# Code blocks

Fenced code supports syntax highlighting, emphasized lines, horizontal
scrolling, and a copy button.

## Enable

```yaml
markdown_extensions:
  - pymdownx.superfences
  - pymdownx.highlight
```

Pymdown Extensions and Pygments are installed with Pixel Lab. The extensions
still need to be enabled in your MkDocs configuration.

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

These theme settings customize all code blocks:

```yaml
theme:
  name: pixel-lab
  code_background_color: "#101410"
  code_text_color: "#e9f1d8"
  code_keyword_color: "#72d572"
  code_string_color: "#f5cf54"
  code_function_color: "#4cc4d2"
  code_comment_color: "#7f8978"
  highlight_color: "#f5c842"
```

These Pixel Lab parameters belong under `theme`:

| Parameter | Default | Effect |
| --- | --- | --- |
| `code_background_color` | Near-black · `#101410` | Code block background |
| `code_text_color` | Pale green · `#e9f1d8` | Default code text |
| `code_keyword_color` | Light green · `#72d572` | Styled keyword token classes |
| `code_string_color` | Golden yellow · `#f5cf54` | Styled string token classes |
| `code_function_color` | Cyan · `#4cc4d2` | Function names |
| `code_comment_color` | Gray-green · `#7f8978` | Comments |
| `highlight_color` | Golden yellow · `#f5c842` | Emphasized-line tint and copy-button hover/focus fill |
| `surface_color` | Ivory · `#fffdf2` | Copy-button background |
| `strong_text_color` | Near-black · `#101410` | Copy-button text |
| `accent_color` | Leaf green · `#4caf50` | Successful-copy button background |
| `accent_foreground_color` | Near-black · `#101410` | Successful-copy button text |
| `accent_dark_color` | Dark green · `#287c35` | Copy-button hover/focus outline |
| `border_color` | Near-black · `#101410` | Block and copy-button outlines |
| `shadow_color` | Near-black · `#101410` | Block's pixel shadow |

Syntax colors apply to the Pygments token classes styled by the theme, not
every possible token independently.

Inline code has separate surface/border styling: see [Text and lists](text.md#customization).
See [Common attributes](../reference/configuration.md#common-attributes).

To customize all highlighted code blocks without changing other component
types, use their selector in a [custom stylesheet](index.md#load-custom-css):

```css
.highlight {
  --code: #101410;      /* Near-black */
  --code-text: #e9f1d8; /* Pale green */
}
```

### Override an instance

Wrap only the target code block, following [Scope one instance](index.md#scope-one-instance):

````markdown
<div class="instance-code" markdown="1">

```python
print("Hello, Pixel Lab!")
```

</div>
````

Scope the CSS variables to this highlighted block in the same stylesheet.
Other code blocks keep the component defaults:

```css
.instance-code > .highlight {
  --code: #101410;      /* Near-black */
  --code-text: #e9f1d8; /* Pale green */
}
```
