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

Use the properties and selectors below to customize this component, following the
[Customization](customization.md) guide.

### Component properties

These CSS variables take their default values from the corresponding theme settings.

| Property | Description | Theme setting | Default |
| --- | --- | --- | --- |
| `--highlight` | Title background | `highlight_color` | Golden yellow · `#f5c842` |
| `--surface` | Body background | `surface_color` | Ivory · `#fffdf2` |
| `--border` | Frame and title divider | `border_color` | Near-black · `#101410` |
| `--shadow` | Frame's pixel shadow | `shadow_color` | Near-black · `#101410` |

Title and body text inherit the page's `text_color`. Set `color` on `.admonition`
to change it locally. All admonition types share these styles; they don't use the
type-specific `alert_*` colors.

See [Colors](../setup/colors.md) for palette configuration and
[Fonts](../setup/fonts.md) for typography defaults and overrides.

### Component styles

Use these selectors to style the frame, title, and body.

| Selector | CSS properties | Description |
| --- | --- | --- |
| `.admonition` | `background`, `border`, `box-shadow`, `margin`, `color` | The whole callout, including its frame and inherited text color |
| `.admonition > .admonition-title` | `background`, `border-bottom`, `font-family`, `font-size`, `padding` | Title fill, divider, typography, and inset |
| `.admonition > :not(.admonition-title)` | `margin-left`, `margin-right` | The inset around body content |
