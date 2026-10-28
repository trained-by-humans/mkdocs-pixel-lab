# Components

Write pages with Markdown and see how Pixel Lab renders them. Each guide keeps
the component's syntax, behavior, and customization together, including
appearance options configured globally under `theme`.

| Component | What you'll find |
| --- | --- |
| [Text and lists](text.md) | Headings, emphasis, links, quotations, lists, and inline code |
| [Code blocks](code-blocks.md) | Syntax highlighting, line emphasis, copying, and code colors |
| [Alerts](alerts.md) | Predefined callout titles and type-specific colors |
| [Admonitions](admonitions.md) | Custom-titled notes and shared callout styling |
| [Content tabs](tabs.md) | Tab syntax, automatic/forced layouts, and selected-tab colors |
| [Collapsible content](details.md) | Closed/open details and summary styling |
| [Tables](tables.md) | Markdown tables, horizontal scrolling, and table surfaces |
| [Images and video](media.md) | Responsive media, borders, and shadows |
| [Page metadata](metadata.md) | Per-page titles, descriptions, and optional automatic defaults |

## Read a component guide

1. **Enable** required Markdown extensions in `mkdocs.yml`; selecting the theme
   doesn't enable them automatically.
2. **Write** the provided Markdown on a page and compare it with the live example.
3. Use **Customization** for appearance settings and CSS overrides.

If syntax stays plain text, see [Troubleshooting](../reference/troubleshooting.md#a-component-looks-like-plain-text).

Examples on this site use the default palette. YAML and CSS color snippets
show those same defaults so you can match each setting to the component you see.
Replace the values to customize your own site.

## Customization scopes

**Customization** groups the component's theme settings and CSS overrides.

See [Common attributes](../reference/configuration.md#common-attributes) for
theme settings, and the component guide for the specific mapping.

**Component-wide overrides** style all instances of a component using CSS
selectors such as `.admonition` or `.tabbed-set`, loaded through `extra_css`.

**Scoped overrides** change selected instances while leaving the component's
defaults and unselected instances unchanged. Use a wrapper class to limit
where the CSS applies. Apply the class to one or several instances.
The wrapper supplies a styling target; it doesn't replace the component's
generated HTML or its normal Markdown syntax.

### Load custom CSS

Register a stylesheet once in `mkdocs.yml`:

```yaml
extra_css:
  - stylesheets/components.css
```

Create `docs/stylesheets/components.css` and add the CSS from the relevant
component guide. Both override scopes use this stylesheet.

### Scope selected instances

The scoped examples use an HTML wrapper with `markdown="1"`. Enable
`md_in_html` alongside the component's required extensions:

```yaml
markdown_extensions:
  - md_in_html
```

Put the wrapper class around the content you want to style; reuse it wherever
the same override should apply. Class names such as `instance-tabs` are
example names you choose, not built-in theme options.

> [!TIP]
>
> Scoped CSS variables inherit into nested content. If a change should affect
> only one element, target that element's CSS property directly instead.

## Nest components

Full-width components reserve the same space for their pixel shadows, so their
frames and visible right edges align. Tables and media keep their natural size
when smaller than the column; when they reach the available width, their outer
edges align with other full-width components. Standalone Markdown images can
use the full column width, while ordinary prose keeps its reading width.

Tabs, alerts, admonitions, collapsible blocks, and tables can contain other
content. Pixel Lab removes shadows from nested styled components and media,
so only the outer container is elevated.

See [Content tabs](tabs.md#layout-modes) for flush and padded panels.
