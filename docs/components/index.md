# Components

Write pages with Markdown and see how Pixel Lab renders them. Each guide keeps
the component's syntax, behavior, and customization together, including
appearance options configured globally under `theme`.

| Component | What you'll find |
| --- | --- |
| [Text and lists](text.md) | Emphasis, links, quotations, lists, and inline code |
| [Code blocks](code-blocks.md) | Syntax highlighting, line emphasis, copying, and code colors |
| [Alerts](alerts.md) | Predefined callout titles and type-specific colors |
| [Admonitions](admonitions.md) | Custom-titled notes and shared callout styling |
| [Content tabs](tabs.md) | Tab syntax, automatic/forced layouts, and selected-tab colors |
| [Collapsible content](details.md) | Closed/open details and summary styling |
| [Tables](tables.md) | Markdown tables, horizontal scrolling, and table surfaces |
| [Images and video](media.md) | Responsive media, borders, and shadows |
| [Heading links](heading-links.md) | Section anchors and `toc` customization |
| [Page metadata](metadata.md) | Per-page titles, descriptions, and optional automatic defaults |

## Read a component guide

1. **Enable** any required Markdown extensions once in `mkdocs.yml`.
2. **Write** the provided Markdown on a page and compare it with the live example.
3. Use **Customization** for component defaults, or **Override an instance**
   for one occurrence. Metadata has no visible styling, so its guide covers
   fields and defaults instead.

Parameter tables sit with the settings they explain: required extensions,
content fields, and feature behavior stay with the main instructions;
optional colors and artwork stay under Customization. Both show defaults and
effects without repeating the main configuration in the appearance section.

Examples on this site use the default palette. Color snippets show those same
defaults so you can match each setting to the component you see. Replace the
values to customize your own site.

## Customization scopes

**Customization** means changing all instances of a component across
the site. To style only one component type, load CSS through `extra_css`
and use its component selector, such as `.admonition` or `.tabbed-set`.

See [Common attributes](../reference/configuration.md#common-attributes) for
theme settings, and the component guide for the specific mapping.

**Override an instance** means changing one occurrence while leaving the
component's defaults and other occurrences unchanged. Give that occurrence a
wrapper class and scope the CSS to it. The wrapper supplies a styling target;
it doesn't replace the component's generated HTML or its normal Markdown syntax.

### Load custom CSS

Register a stylesheet once in `mkdocs.yml`:

```yaml
extra_css:
  - stylesheets/components.css
```

Create `docs/stylesheets/components.css` and add the CSS from the relevant
component guide. `extra_css` is a native MkDocs setting, not `extra.css` or a
Pixel Lab theme option. Both component customization and instance overrides
use the same stylesheet.

### Scope one instance

The instance examples use an HTML wrapper with `markdown="1"`. Enable
`md_in_html` alongside the component's required extensions:

```yaml
markdown_extensions:
  - md_in_html
```

Merge this into your existing extension list rather than replacing it. Put
the wrapper class on only the target occurrence; reusing it targets multiple
occurrences. Class names such as `instance-tabs` are example names you choose,
not built-in theme options.

> [!TIP]
>
> Scoped CSS variables inherit into nested content. If a change should affect
> only one element, target that element's CSS property directly instead.

## Nest components

Tabs, alerts, admonitions, collapsible blocks, and tables can contain other
content. Pixel Lab removes shadows from nested styled components and media,
so only the outer container is elevated. Container guides highlight this
behavior where it matters; child content keeps its normal authoring syntax.

See [Content tabs](tabs.md#layout-modes) for flush and padded panels.
