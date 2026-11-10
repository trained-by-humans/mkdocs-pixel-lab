# Collapsible content

Use an expandable note for optional instructions, a longer explanation, or
troubleshooting details.

## Enable

```yaml
markdown_extensions:
  - admonition
  - pymdownx.details
```

`pymdownx.details` enables the collapsible `???` syntax; `admonition` also
enables regular `!!!` notes.

For non-collapsible notes with the same styling, see [Admonitions](admonitions.md).

## Closed by default

??? note "Show the configuration advice"

    Keep one `theme` block in `mkdocs.yml` and merge new options into it.

```markdown
??? note "Show the configuration advice"

    Keep one `theme` block in `mkdocs.yml` and merge new options into it.
```

## Open by default

???+ tip "Start with the defaults"

    Override only the settings your site needs.

```markdown
???+ tip "Start with the defaults"

    Override only the settings your site needs.
```

The browser's native `details` element handles opening and closing, including
keyboard activation. It works without the theme's JavaScript.

> [!NOTE]
>
> Expanded content shares the collapsible block's outer shadow. See
> [Nest components](index.md#nest-components).

## Native HTML alternative

You can also write `<details>` directly. For Markdown inside the body, enable
[`md_in_html`](customization.md#scope-selected-instances) and add `markdown`:

```html
<details markdown>
<summary>More information</summary>

This body supports **Markdown**.

</details>
```

## Layout modes

Pixel Lab chooses each expanded body's layout automatically, like
[content tabs](tabs.md#layout-modes):

- A single [code block](code-blocks.md) or [table](tables.md) fills the body **flush**.
- Prose, multiple blocks, and mixed content use a **padded** inset.
- Nested details and tabs select their layouts independently.

Flush content shares the details frame without a duplicate border or surrounding
gap. Code retains its internal padding, and wide code and tables scroll
horizontally inside the body.

???+ note "Code without an extra inset"

    ```python
    print("One code block fills the expanded body")
    ```

???+ note "A table without an extra inset"

    | Content | Layout |
    | --- | --- |
    | Single code block or table | Flush |
    | Prose or mixed content | Padded |

### Scoped layout overrides

Use `.details-padded` or `.details-flush` directly on a native `<details>`
element, or wrap selected `???` blocks using
[Scope selected instances](customization.md#scope-selected-instances):

<div class="details-padded" markdown>

???+ note "Always padded"

    ```python
    print("Keep an inset around this block")
    ```

</div>

````markdown
<div class="details-padded" markdown>

???+ note "Always padded"

    ```python
    print("Keep an inset around this block")
    ```

</div>
````

For native HTML, place the class on the element:

```html
<details class="details-flush" open>
<summary>Always flush</summary>
<pre><code>Keep code's internal padding.</code></pre>
</details>
```

> [!NOTE]
>
> - For nested details, the nearest details layout class controls the layout.
> - These classes affect only details; `.tabs-padded` and `.tabs-flush` affect only tabs.
> - `.details-padded` and `.details-flush` work with or without JavaScript.
> - Automatic layout requires JavaScript, without it details stay padded.

## Customization

Use the properties and selectors below to customize this component, following the
[Customization](customization.md) guide.

### Component properties

These CSS variables take their default values from the corresponding theme settings.

| Property | Description | Theme setting | Default |
| --- | --- | --- | --- |
| `--highlight` | Summary background | `highlight_color` | Golden yellow · `#f5c842` |
| `--surface` | Expanded body background | `surface_color` | Ivory · `#fffdf2` |
| `--border` | Frame and summary divider | `border_color` | Near-black · `#101410` |
| `--shadow` | Frame's pixel shadow | `shadow_color` | Near-black · `#101410` |

Summary and body text inherit the page's `text_color`. Set `color` on `details`
to change it locally. All detail types share these styles.

See [Colors](../setup/colors.md) for palette configuration and
[Fonts](../setup/fonts.md) for typography defaults and overrides.

### Component styles

Use these selectors to style the frame and summary. For the expanded content
inset and flush presentation, see [Layout modes](#layout-modes).

| Selector | CSS properties | Description |
| --- | --- | --- |
| `details` | `background`, `border`, `box-shadow`, `margin`, `color` | The whole collapsible block, including its frame and inherited text color |
| `details > summary` | `background`, `border-bottom`, `font-family`, `font-size`, `padding` | Summary fill, divider, typography, and inset |
