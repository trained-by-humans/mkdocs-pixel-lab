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

<div id="basic-tabs" markdown>

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

<div id="layout-tabs" markdown>

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
[Scope selected instances](customization.md#scope-selected-instances):

<div id="forced-tabs" class="tabs-padded" markdown>

=== "Always padded"

    ```python
    print("Keep an inset around this block")
    ```

</div>

````markdown
<div class="tabs-padded" markdown>

=== "Always padded"

    ```python
    print("Keep an inset around this block")
    ```

</div>
````

Use `tabs-flush` instead to remove the inset. The closest wrapper wins for
nested groups. Forced layout also relies on the theme's JavaScript.

## Customization

Use the properties and selectors below to customize this component, following the
[Customization](customization.md) guide.

### Component properties

These CSS variables take their default values from the corresponding theme settings.

| Property | Description | Theme setting | Default |
| --- | --- | --- | --- |
| `--accent` | Selected tab background | `accent_color` | Leaf green · `#4caf50` |
| `--accent-foreground` | Selected tab text and marker | `accent_foreground_color` | Near-black · `#101410` |
| `--tab-hover` | Unselected tab background on hover | `tab_hover_color` | Muted khaki · `#d8d3b8` |
| `--muted` | Unselected tab text | `muted_text_color` | Gray-green · `#5f665d` |
| `--surface2` | Tab-strip background | `surface_alt_color` | Pale khaki · `#e8e4cf` |
| `--surface` | Panel background | `surface_color` | Ivory · `#fffdf2` |
| `--border` | Frame and label dividers | `border_color` | Near-black · `#101410` |
| `--shadow` | Frame's pixel shadow | `shadow_color` | Near-black · `#101410` |

Panel text inherits the page's `text_color`. To change it for a tab group,
set `color` on `.tabbed-set`. See [Colors](../setup/colors.md) for palette
configuration and [Fonts](../setup/fonts.md) for typography defaults and overrides.

### Component styles

Use these selectors to style the frame, labels, and panels in your custom CSS.
The variables above control the selection and hover colors.

| Selector | CSS properties | Description |
| --- | --- | --- |
| `.tabbed-set` | `background`, `border`, `box-shadow`, `margin`, `color` | The whole tab group, including its frame and panel text |
| `.tabbed-labels` | `background`, `border-bottom` | The strip behind the labels and its divider above the panel |
| `.tabbed-labels > label` | `font-family`, `font-size`, `font-weight`, `text-transform`, `padding`, `border-right` | Label typography, spacing, and dividers |
| `.tabbed-content > .tabbed-block` | `padding` | The content inset in padded panels; see [Layout modes](#layout-modes) for flush panels |

## Limits

Keep groups to eight tabs or fewer; the current selection styles support the
first eight panels. Prefer separate sections when labels become hard to scan
on a small screen.
