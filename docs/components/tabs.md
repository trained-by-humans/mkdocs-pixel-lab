# Content tabs

Use tabs for alternative instructions or related examples within a page.
These are different from the site's [primary navigation tabs](../setup/navigation.md).

## Enable

```yaml
markdown_extensions:
  - pymdownx.tabbed:
      alternate_style: true
```

`alternate_style: true` is required for the markup Pixel Lab styles.
For the highlighted examples below, also enable [Code blocks](code-blocks.md#enable).

## Write tabs

<div id="basic-tabs" markdown="1">

=== "Python"

    ```python
    print("Hello, Pixel Lab!")
    ```

=== "Shell"

    ```bash
    echo "Hello, Pixel Lab!"
    ```

</div>

````markdown
=== "Python"

    ```python
    print("Hello, Pixel Lab!")
    ```

=== "Shell"

    ```bash
    echo "Hello, Pixel Lab!"
    ```
````

Indent each panel's content four spaces. The first tab starts selected.
Tab selection uses CSS and remains usable without JavaScript.

## Layout modes

Pixel Lab chooses each panel's layout automatically:

- A single [code block](code-blocks.md) or [table](tables.md) fills the panel **flush**.
- Prose, multiple blocks, or mixed content use a **padded** inset.
- Nested tabs are evaluated independently.

> [!NOTE]
>
> Flush code and table panels use the tab group's frame. Nested content shares
> its outer shadow; see [Nest components](index.md#nest-components).

<div id="layout-tabs" markdown="1">

=== "Code only"

    ```python
    print("This panel is flush")
    ```

=== "Table only"

    | Format | Result |
    | --- | --- |
    | Code or table | Flush |
    | Mixed content | Padded |

=== "Mixed content"

    This introduction gives the panel a padded layout.

    ```python
    print("This panel keeps an inset")
    ```

</div>

Layout detection uses JavaScript. Without it, panels retain the padded
presentation.

### Scoped layout overrides

Wrap selected groups in `.tabs-padded` or `.tabs-flush`, following
[Scope selected instances](index.md#scope-selected-instances):

<div id="forced-tabs" class="tabs-padded" markdown="1">

=== "Always padded"

    ```python
    print("Keep an inset around this block")
    ```

</div>

````markdown
<div class="tabs-padded" markdown="1">

=== "Always padded"

    ```python
    print("Keep an inset around this block")
    ```

</div>
````

Use `tabs-flush` instead to remove the inset. The closest wrapper wins for
nested groups. Forced layout also relies on the theme's JavaScript.

## Customization

Tab colors are configured site-wide under `theme`, not in the tab's Markdown.
These are the default colors used by the examples on this page:

```yaml
theme:
  name: pixel-lab
  accent_color: "#4caf50"            # Leaf green
  accent_foreground_color: "#101410" # Near-black
  tab_hover_color: "#d8d3b8"         # Muted khaki
```

| Parameter | Default | Effect |
| --- | --- | --- |
| `accent_color` | Leaf green · `#4caf50` | Selected tab background |
| `accent_foreground_color` | Near-black · `#101410` | Selected tab text and marker |
| `tab_hover_color` | Muted khaki · `#d8d3b8` | Unselected tab background on hover |
| `muted_text_color` | Gray-green · `#5f665d` | Unselected tab text |
| `surface_alt_color` | Pale khaki · `#e8e4cf` | Tab-strip background |
| `surface_color` | Ivory · `#fffdf2` | Panel background |
| `border_color` | Near-black · `#101410` | Frame and label dividers |
| `shadow_color` | Near-black · `#101410` | Outer pixel shadow |

See [Common attributes](../reference/configuration.md#common-attributes).

### Component-wide overrides

To change every tab group's colors and label font, add this to your
[custom stylesheet](index.md#load-custom-css):

```css
.tabbed-set {
  --accent: #4caf50;            /* Leaf green */
  --accent-foreground: #101410; /* Near-black */
  --tab-hover: #d8d3b8;         /* Muted khaki */
}

.tabbed-labels > label {
  font-family: system-ui, sans-serif;
}
```

### Scoped overrides

Wrap each selected group, following [Scope selected instances](index.md#scope-selected-instances):

```markdown
<div class="instance-tabs" markdown="1">

=== "Python"

    Use Python for this example.

=== "Shell"

    Use a shell for this example.

</div>
```

Add the scoped rule to your stylesheet:

```css
.instance-tabs > .tabbed-set {
  --accent: #4caf50;            /* Leaf green */
  --accent-foreground: #101410; /* Near-black */
  --tab-hover: #d8d3b8;         /* Muted khaki */
}
```

For layout rather than color changes, see
[Scoped layout overrides](#scoped-layout-overrides).

## Limits

Keep groups to eight tabs or fewer; the current selection styles support the
first eight panels. Prefer separate sections when labels become hard to scan
on a small screen.
