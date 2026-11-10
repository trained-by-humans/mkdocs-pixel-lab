# Components

Write pages with Markdown and see how Pixel Lab renders them. Each guide keeps
the component's syntax, behavior, and customization together, including
appearance options configured globally under `theme`.

| Component | What you'll find |
| --- | --- |
| [Text and lists](text.md) | Headings, emphasis, links, quotations, lists, and inline code |
| [Card grids](cards.md) | Responsive landing pages, list and block cards, and grid spacing |
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
3. Use **Customization** to find component properties, theme defaults, and CSS selectors.

If syntax stays plain text, see [Troubleshooting](../reference/troubleshooting.md#a-component-looks-like-plain-text).

Individual component guides use the default palette. Their property tables
show those defaults so you can match each setting to what you see.
The Customization guide includes live examples with deliberately different colors.

## Customization scopes

The [Customization](customization.md) guide explains how to choose between
theme settings, overrides for every instance of a component, and overrides
for selected instances. It includes live examples and links to their CSS.

### Load custom CSS

Follow [Load custom CSS](customization.md#load-custom-css) to create and
register a stylesheet once, then write rules using the properties and selectors
listed in each component guide.

### Scope selected instances

Follow [Scope selected instances](customization.md#scope-selected-instances)
for the Markdown extension setup and named wrappers used for instance overrides.

## Nest components

Cards, tabs, alerts, admonitions, collapsible blocks, and tables can contain other
content. Pixel Lab removes shadows from nested styled components and media,
so only the outer container is elevated.

See [Content tabs](tabs.md#layout-modes) for flush and padded panels.
