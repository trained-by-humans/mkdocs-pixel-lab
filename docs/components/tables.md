# Tables

Use Markdown tables for structured comparisons and small references. MkDocs
enables Python-Markdown's table extension by default.

## Write a table

| Setting | Purpose | Default |
| --- | --- | --- |
| `show_repo` | Show the repository button | `true` |
| `show_source` | Show the page source action | `true` |
| `show_edit` | Show the page edit action | `true` |

```markdown
| Setting | Purpose | Default |
| --- | --- | --- |
| `show_repo` | Show the repository button | `true` |
| `show_source` | Show the page source action | `true` |
| `show_edit` | Show the page edit action | `true` |
```

## Wide tables

The theme's script wraps tables in a horizontal scrolling frame. The border
and shadow stay fixed while the contents scroll. On a narrow screen, try
scrolling this table sideways:

| Payload | Meaning |
| --- | --- |
| `a_long_unbroken_configuration_value_that_should_scroll_inside_the_table_instead_of_widening_the_page` | Long identifiers don't need to be shortened in the source. |

Without JavaScript, the Markdown table remains readable but doesn't receive
the script-created scrolling frame.

> [!NOTE]
>
> Images inside a table share the table frame's outer shadow. See
> [Nest components](index.md#nest-components).

## Customization

These theme settings customize all tables:

```yaml
theme:
  name: pixel-lab
  surface_alt_color: "#e8e4cf"
  surface_color: "#fffdf2"
  subtle_border_color: "rgba(16, 20, 16, 0.3)"
  border_color: "#101410"
  shadow_color: "#101410"
```

These Pixel Lab parameters belong under `theme`:

| Parameter | Default | Effect |
| --- | --- | --- |
| `surface_alt_color` | Pale khaki · `#e8e4cf` | Header row background |
| `surface_color` | Ivory · `#fffdf2` | Scrolling frame background |
| `subtle_border_color` | Near-black at 30% · `rgba(16, 20, 16, 0.3)` | Cell rules |
| `border_color` | Near-black · `#101410` | Outer frame |
| `shadow_color` | Near-black · `#101410` | Fixed pixel shadow |

See [Common attributes](../reference/configuration.md#common-attributes).

To customize the header fill for all content tables without changing other
component types, use a [custom stylesheet](index.md#load-custom-css):

```css
.main th {
  background: #e8e4cf; /* Pale khaki */
}
```

### Override an instance

Wrap only the target table, following [Scope one instance](index.md#scope-one-instance):

```markdown
<div class="instance-table" markdown="1">

| Setting | Purpose |
| --- | --- |
| `show_repo` | Show the repository button |

</div>
```

Scope the header rule to this table in the same stylesheet. It keeps working
when JavaScript adds the scrolling frame; other tables keep the component defaults:

```css
.instance-table th {
  background: #e8e4cf; /* Pale khaki */
}
```
