# Heading links

Headings organize a page, and permalinks let readers link to a specific section.
Hover or focus the link beside a section heading on this page to try it.

## Enable

Heading links come from Python-Markdown's `toc` extension, not a separate
Pixel Lab plugin:

```yaml
markdown_extensions:
  - toc:
      permalink: true
```

MkDocs enables `toc` by default, but visible permalinks are off until you set
`permalink`. This documentation site explicitly enables them. These are
Python-Markdown options under `markdown_extensions` → `toc`, not Pixel Lab
theme parameters:

| Parameter | Default | Effect |
| --- | --- | --- |
| `permalink` | `false` | Enables visible heading links; `true` uses the built-in link icon, while a string supplies a text symbol |

Omit `permalink` or set it to `false` to disable visible heading links.
Headings retain their IDs, so links to sections still work.

## Write headings

```markdown
# Page title

## A section

### A subsection
```

Use one H1 for the page title. Pixel Lab displays permalink artwork for H2–H6;
the H1 retains its ID but doesn't display a heading-permalink icon. Optional
[source/edit actions](../setup/repository.md) beside H1 are a separate feature.

The theme follows the current section in the URL fragment as you scroll,
without adding history entries. This scroll tracking uses JavaScript; the
generated heading links themselves don't require it.

## Customization

The `toc` settings below apply to heading links across the site.

With heading links enabled, `permalink: true` uses the built-in solid pixelated
link icon. To replace it with a text symbol and adjust its tooltip or position,
configure `toc` directly:

```yaml
markdown_extensions:
  - toc:
      permalink: "⚓"
      permalink_title: "Link to this section"
      permalink_leading: false
```

`permalink_title`, `permalink_leading`, and heading ID options remain under
`toc`'s control. There is no `theme.icon.permalink` setting or custom permalink
image option.

These optional appearance settings also belong under `toc`:

| Parameter | Default | Effect |
| --- | --- | --- |
| `permalink_title` | `Permanent link` | Tooltip and accessible title of each heading link |
| `permalink_leading` | `false` | Places the link after the heading; `true` moves it before the heading |

The built-in icon is a black silhouette. Its copied hover/focus shadow uses
`accent_dark_color`. This is the default dark green used on this site:

```yaml
theme:
  name: pixel-lab
  accent_dark_color: "#287c35" # Dark green
```

These Pixel Lab parameters belong under `theme`:

| Parameter | Default | Effect |
| --- | --- | --- |
| `accent_color` | Leaf green · `#4caf50` | Resting text-symbol permalink color; doesn't recolor the built-in black icon |
| `accent_dark_color` | Dark green · `#287c35` | Built-in icon's hover/focus shadow and hovered text-symbol color |

See [Common attributes](../reference/configuration.md#common-attributes) and the
[Python-Markdown TOC reference](https://python-markdown.github.io/extensions/toc/)
for extension options. Enabling `toc` doesn't add a visible page-contents
sidebar in Pixel Lab.

To customize the hover/focus shadow for all heading links without changing
navigation colors, use a [custom stylesheet](index.md#load-custom-css):

```css
.headerlink {
  --accent-dark: #287c35; /* Dark green */
}
```

### Override an instance

Wrap only the target heading, following [Scope one instance](index.md#scope-one-instance):

```markdown
<div class="instance-heading" markdown="1">

## A specific section

</div>
```

Scope the CSS variable to that heading's link in the same stylesheet. Other
heading links keep the component defaults:

```css
.instance-heading > h2 > .headerlink {
  --accent-dark: #287c35; /* Dark green */
}
```

This changes the icon's hover/focus shadow (or a text symbol's hover color),
not `toc`'s site-wide symbol, title, or positioning options.
