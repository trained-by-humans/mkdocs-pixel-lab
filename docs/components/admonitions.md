# Admonitions

Use admonitions for callouts with custom titles and Markdown content. For
predefined titles and type-specific colors, use [Alerts](alerts.md).

## Enable

Enable Python-Markdown's admonition extension in `mkdocs.yml`:

```yaml
markdown_extensions:
  - admonition
```

## Write an admonition

!!! note "Before you start"

    Keep the configuration in one place and merge new settings into it.

```markdown
!!! note "Before you start"

    Keep the configuration in one place and merge new settings into it.
```

Indent the body four spaces. The type follows `!!!`; the quoted custom title
is optional. For example, `!!! note` without a quoted title displays Note.
Admonition types currently share the same theme styling.

For expandable notes using `???` or `???+`, see [Collapsible content](details.md).

> [!NOTE]
>
> Content inside an admonition shares its outer shadow. See
> [Nest components](index.md#nest-components) for the nesting rule.

## Customization

These theme settings customize all admonitions. Admonitions don't use the
type-specific `alert_*` colors:

```yaml
theme:
  name: pixel-lab
  highlight_color: "#f5c842"
  surface_color: "#fffdf2"
  border_color: "#101410"
  shadow_color: "#101410"
```

| Parameter | Default | Effect |
| --- | --- | --- |
| `highlight_color` | Golden yellow · `#f5c842` | Admonition title background |
| `surface_color` | Ivory · `#fffdf2` | Admonition body background |
| `text_color` | Dark green-gray · `#182018` | Admonition body text |
| `border_color` | Near-black · `#101410` | Admonition outline and title divider |
| `shadow_color` | Near-black · `#101410` | Admonition pixel shadow |

See [Common attributes](../reference/configuration.md#common-attributes).

### Component-wide overrides

To change every admonition's title fill, add this to your
[custom stylesheet](index.md#load-custom-css):

```css
.admonition > .admonition-title {
  background: #f5c842; /* Golden yellow */
}
```

### Scoped overrides

Wrap each selected admonition, following [Scope selected instances](index.md#scope-selected-instances):

```markdown
<div class="instance-admonition" markdown="1">

!!! note "Before you start"

    Keep the configuration in one place.

</div>
```

Add the scoped rule to your stylesheet:

```css
.instance-admonition > .admonition > .admonition-title {
  background: #f5c842; /* Golden yellow */
}
```
