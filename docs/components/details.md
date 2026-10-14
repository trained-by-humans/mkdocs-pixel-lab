# Collapsible content

Use an expandable note for optional instructions, a longer explanation, or
troubleshooting details.

## Enable

```yaml
markdown_extensions:
  - admonition
  - pymdownx.details
```

Both extensions belong under `markdown_extensions` in `mkdocs.yml`.
`pymdownx.details` enables the collapsible `???` syntax; `admonition` also
enables regular `!!!` notes. Neither is enabled just by selecting the theme.

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

This is alternative authoring syntax, not a requirement for customizing the
component or overriding an instance's appearance.

You can also write `<details><summary>Title</summary>Content</details>` directly.
Follow [Scope one instance](index.md#scope-one-instance) to enable Markdown
inside HTML, then add `markdown="1"` to the wrapper:

```html
<details markdown="1">
<summary>More information</summary>

This body supports **Markdown**.

</details>
```

## Customization

These theme settings customize all collapsible blocks. Different detail types
currently share the same styling:

```yaml
theme:
  name: pixel-lab
  highlight_color: "#f5c842"
  surface_color: "#fffdf2"
  border_color: "#101410"
  shadow_color: "#101410"
```

These Pixel Lab parameters belong under `theme`:

| Parameter | Default | Effect |
| --- | --- | --- |
| `highlight_color` | Golden yellow · `#f5c842` | Summary background |
| `surface_color` | Ivory · `#fffdf2` | Expanded body background |
| `border_color` | Near-black · `#101410` | Frame and summary divider |
| `shadow_color` | Near-black · `#101410` | Outer pixel shadow |

See [Common attributes](../reference/configuration.md#common-attributes).

To customize the summary fill for all collapsible blocks without changing
admonitions, add this to your [custom stylesheet](index.md#load-custom-css):

```css
details > summary {
  background: #f5c842; /* Golden yellow */
}
```

### Override an instance

Wrap only the target block, following [Scope one instance](index.md#scope-one-instance):

```markdown
<div class="instance-details" markdown="1">

??? note "More information"

    Keep the configuration in one place.

</div>
```

Add this scoped rule to the same stylesheet. Other collapsible blocks keep
the component defaults; you don't need to rewrite this one as native HTML:

```css
.instance-details > details > summary {
  background: #f5c842; /* Golden yellow */
}
```
