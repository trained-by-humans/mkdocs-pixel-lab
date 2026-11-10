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

Small tables keep their natural width. Wider tables fit the available column
and scroll horizontally inside a frame added by the theme's script. The border
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

Use the properties and selectors below to customize this component, following the
[Customization](customization.md) guide.

### Component properties

These CSS variables take their default values from the corresponding theme settings.

| Property | Description | Theme setting | Default |
| --- | --- | --- | --- |
| `--surface2` | Header background | `surface_alt_color` | Pale khaki · `#e8e4cf` |
| `--surface` | Scrolling frame background | `surface_color` | Ivory · `#fffdf2` |
| `--subtle-border` | Cell dividers | `subtle_border_color` | Near-black at 30% · `rgba(16, 20, 16, 0.3)` |
| `--border` | Scrolling frame outline | `border_color` | Near-black · `#101410` |
| `--shadow` | Scrolling frame's fixed pixel shadow | `shadow_color` | Near-black · `#101410` |

Cell text inherits the page's `text_color`. Set `color` on `table` to change it
locally.

See [Colors](../setup/colors.md) for palette configuration and
[Fonts](../setup/fonts.md) for typography defaults and overrides.

### Component styles

Use these selectors to style the table and the scrolling frame added by the
theme script. The frame keeps its border and shadow fixed while the cells scroll.

| Selector | CSS properties | Description |
| --- | --- | --- |
| `table` | `border-collapse`, `color` | The table layout and inherited cell text color |
| `.table-shell` | `margin`, `width`, `max-width` | Space around the scrolling frame and its width limits |
| `.table-scroll` | `background`, `border`, `box-shadow` | The fixed frame around the scrolling table |
| `th, td` | `border`, `padding`, `text-align` | Cell dividers, content inset, and alignment |
| `th` | `background`, `font-family`, `font-weight` | Header fill and typography |
