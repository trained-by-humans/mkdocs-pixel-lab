# Heading permalinks

Headings organize a page, and permalinks let readers link to a specific section.
Hover or focus the link beside a section heading on this page to try it.

## Enable

Enable permalinks through Python-Markdown's `toc` extension:

```yaml
markdown_extensions:
  - toc:
      permalink: true
```

MkDocs enables `toc` by default, but visible permalinks are off until you set
`permalink`.

| Parameter | Default | Effect |
| --- | --- | --- |
| `permalink` | `false` | Enables visible heading links; `true` uses the built-in link icon, while a string supplies a text symbol |

Headings retain their IDs even when visible permalinks are disabled.

## Use heading permalinks

Pixel Lab displays permalink artwork for H2–H6; the H1 retains its ID but
doesn't display a heading-permalink icon. Optional
[source/edit actions](repository.md) beside H1 are a separate feature.
For ordinary Markdown heading syntax, see [Text and lists](../components/text.md#headings).

The theme follows the current section in the URL fragment as you scroll,
without adding history entries. This scroll tracking uses JavaScript; the
generated heading links themselves don't require it.

## Further customization

To replace the built-in icon with a text symbol or adjust the tooltip and
position, configure `toc`:

```yaml
markdown_extensions:
  - toc:
      permalink: "⚓"
      permalink_title: "Link to this section"
      permalink_leading: false
```

| Parameter | Default | Effect |
| --- | --- | --- |
| `permalink_title` | `Permanent link` | Tooltip and accessible title of each heading link |
| `permalink_leading` | `false` | Places the link after the heading; `true` moves it before the heading |

> [!NOTE]
>
> There is no `theme.icon.permalink` setting or custom permalink image option.

To change the built-in icon's hover/focus shadow:

```yaml
theme:
  name: pixel-lab
  accent_dark_color: "#287c35" # Dark green
```

| Parameter | Default | Effect |
| --- | --- | --- |
| `accent_color` | Leaf green · `#4caf50` | Resting text-symbol permalink color; doesn't recolor the built-in black icon |
| `accent_dark_color` | Dark green · `#287c35` | Built-in icon's hover/focus shadow and hovered text-symbol color |

See [Common attributes](../reference/configuration.md#common-attributes).
For more extension options, use the
[Python-Markdown TOC reference](https://python-markdown.github.io/extensions/toc/).

### Component-wide overrides

To customize the hover/focus shadow for all heading links without changing
navigation colors, use a [custom stylesheet](../components/index.md#load-custom-css):

```css
.headerlink {
  --accent-dark: #287c35; /* Dark green */
}
```

### Scoped overrides

Wrap each selected heading, following [Scope selected instances](../components/index.md#scope-selected-instances):

```markdown
<div class="instance-heading" markdown="1">

## A specific section

</div>
```

Add the scoped rule to your stylesheet:

```css
.instance-heading > h2 > .headerlink {
  --accent-dark: #287c35; /* Dark green */
}
```
