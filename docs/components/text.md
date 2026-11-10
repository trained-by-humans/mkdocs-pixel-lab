# Text and lists

Headings, basic text, links, quotations, and lists use standard Markdown.
No extra extension is required.

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

Use the properties and selectors below to customize this component, following the
[Customization](customization.md) guide.

### Component properties

These CSS variables take their default values from the corresponding theme settings.

| Property | Description | Theme setting | Default |
| --- | --- | --- | --- |
| `--ink` | Body text and hovered links | `text_color` | Dark green-gray · `#182018` |
| `--muted` | Quotation text | `muted_text_color` | Gray-green · `#5f665d` |
| `--accent` | Quotation's left rail | `accent_color` | Leaf green · `#4caf50` |
| `--accent-dark` | Link text | `accent_dark_color` | Dark green · `#287c35` |
| `--surface2` | Inline code background | `surface_alt_color` | Pale khaki · `#e8e4cf` |
| `--inline-code-border` | Inline code border | `inline_code_border_color` | Dark green at 45% · `rgba(40, 124, 53, 0.45)` |
| `--border` | H2 heading divider | `border_color` | Near-black · `#101410` |

Body text inherits its font and color from the page. Set `font-family` or
`color` on a content wrapper to change those defaults locally; headings, links,
quotations, and code also have their own style rules.

See [Colors](../setup/colors.md) for palette configuration and
[Fonts](../setup/fonts.md) for typography defaults and overrides.

### Component styles

Use these selectors to style text within the page content.

| Selector | CSS properties | Description |
| --- | --- | --- |
| `.main` | `color`, `font-family`, `line-height` | Text defaults within the content column |
| `.main h1, .main h2, .main h3` | `font-family`, `font-size`, `font-weight`, `text-transform`, `margin` | Page and section heading typography and spacing |
| `.main h2` | `border-bottom`, `padding-bottom` | The divider beneath second-level headings |
| `.main p, .main li` | `max-width`, `line-height`, `margin` | Paragraph and list-item reading width, line spacing, and margins |
| `.main a, .main a:hover` | `color`, `text-decoration` | Content link appearance and hover state |
| `.main blockquote` | `border-left`, `color`, `padding-left`, `margin` | Quotation rail, text, inset, and surrounding space |
| `.main :not(pre) > code` | `background`, `border`, `font-family`, `font-size`, `padding` | Inline code fill, frame, typography, and inset |
