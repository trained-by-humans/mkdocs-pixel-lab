# Fonts

Pixel Lab bundles **Inter** for body text and **IBM Plex Mono** for headings,
navigation, controls, and code. Font files are served from your site; the theme
doesn't request Google Fonts or another external font service.

## Use the defaults

No configuration is required. Font fallbacks are `system-ui, sans-serif` for
body text and `monospace` for IBM Plex Mono.

## Override typography with CSS

There is currently no `theme.font` option. Use MkDocs' `extra_css` setting for
a deliberate CSS override:

```yaml
extra_css:
  - stylesheets/fonts.css
```

This is a native MkDocs setting, not a Pixel Lab font option:

| Parameter | Default | Effect |
| --- | --- | --- |
| `extra_css` | `[]` | Loads your stylesheet after the theme CSS so you can override font declarations |

Create `docs/stylesheets/fonts.css`:

```css
body {
  font-family: system-ui, sans-serif;
}

h1, h2, h3 {
  font-family: ui-monospace, monospace;
}
```

These are CSS selectors and properties, not `theme` parameters. Defaults
below describe the bundled typography before applying the override above:

| Parameter | Default | Effect |
| --- | --- | --- |
| `body` → `font-family` | `Inter, system-ui, sans-serif` | Body text and other content that inherits its font |
| `h1, h2, h3` → `font-family` | `"IBM Plex Mono", monospace` | Page title and section headings |
| `.tabbed-labels > label` → `font-family` | `"IBM Plex Mono", monospace` | Content-tab labels without changing body text |
| `code` and `pre` → `font-family` | `"IBM Plex Mono", monospace` | Inline code and fenced code blocks |

This example changes body text and headings only. Components with their own
font declarations keep IBM Plex Mono; override their selectors explicitly if
needed. See [Content tabs](../components/tabs.md#customization) for a tab-label
example.

If you supply another font, host its files yourself and define `@font-face` in
the same stylesheet. Check its license and test long titles and narrow screens.
