# Text and lists

Headings, basic text, links, quotations, and lists use standard Markdown. No extra
extension is required.

## Headings

```markdown
# Page title

## A section

### A subsection
```

Use one H1 (`#`) for the page title, H2 (`##`) for sections, and H3 (`###`)
for subsections. Keep heading levels in order rather than choosing a level
for its visual size.

For site-wide anchor-link visibility and appearance, see
[Heading permalinks](../setup/heading-permalinks.md).

## Emphasis and inline code

Use **bold** for emphasis, *italics* for a term, and `inline_code` for short
identifiers. Link to a [related page](tabs.md) with descriptive text.

```markdown
Use **bold** for emphasis, *italics* for a term, and `inline_code` for short
identifiers. Link to a [related page](tabs.md) with descriptive text.
```

## Lists

- Configure the theme once.
- Write content in Markdown.
    - Keep related guidance together.
    - Show the result next to its source.

```markdown
- Configure the theme once.
- Write content in Markdown.
    - Keep related guidance together.
    - Show the result next to its source.
```

1. Install Pixel Lab.
2. Select the theme.
3. Preview the site.

```markdown
1. Install Pixel Lab.
2. Select the theme.
3. Preview the site.
```

## Quotations

> Documentation is part of the product.

```markdown
> Documentation is part of the product.
```

For predefined semantic callouts, use [Alerts](alerts.md). For a custom
title, use [Admonitions](admonitions.md).

## Customization

These theme settings customize text throughout the site:

```yaml
theme:
  name: pixel-lab
  text_color: "#182018"
  muted_text_color: "#5f665d"
  accent_color: "#4caf50"
  accent_dark_color: "#287c35"
  surface_alt_color: "#e8e4cf"
  inline_code_border_color: "rgba(40, 124, 53, 0.45)"
```

These Pixel Lab parameters belong under `theme`:

| Parameter | Default | Effect |
| --- | --- | --- |
| `text_color` | Dark green-gray · `#182018` | Body text and hovered links |
| `muted_text_color` | Gray-green · `#5f665d` | Quotation text |
| `accent_color` | Leaf green · `#4caf50` | Quotation's left rail |
| `accent_dark_color` | Dark green · `#287c35` | Link text |
| `surface_alt_color` | Pale khaki · `#e8e4cf` | Inline code background |
| `inline_code_border_color` | Dark green at 45% · `rgba(40, 124, 53, 0.45)` | Inline code border |

See [Common attributes](../reference/configuration.md#common-attributes).

To customize the rail for all ordinary quotations without changing other
component types, use a [custom stylesheet](index.md#load-custom-css):

```css
.main blockquote {
  border-left-color: #4caf50; /* Leaf green */
}
```

### Scoped overrides

Wrap each selected quotation, following [Scope selected instances](index.md#scope-selected-instances):

```markdown
<div class="instance-quote" markdown="1">

> Documentation is part of the product.

</div>
```

Scope the rail rule to `.instance-quote` in the same stylesheet. Unwrapped
quotations keep the component defaults:

```css
.instance-quote > blockquote {
  border-left-color: #4caf50; /* Leaf green */
}
```
