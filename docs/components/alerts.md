# Alerts

Use alerts for notes with predefined titles and semantic colors.
Their bodies support Markdown. For a custom title, use an
[admonition](admonitions.md) instead.

## Enable

Enable the extension bundled with Pixel Lab:

```yaml
markdown_extensions:
  - mkdocs_pixel_lab.github_alerts
```

## Write an alert

> [!NOTE]
>
> Background information that helps explain the topic.

> [!TIP]
>
> A useful shortcut or recommendation.

> [!IMPORTANT]
>
> Something readers should know before proceeding.

> [!WARNING]
>
> A potential problem that needs attention.

> [!CAUTION]
>
> A risk of damage or an irreversible action.

```markdown
> [!TIP]
>
> A useful shortcut or recommendation.
```

The supported types are `NOTE`, `TIP`, `IMPORTANT`, `WARNING`, and `CAUTION`.

> [!NOTE]
>
> Rich content inside an alert uses the alert's outer shadow rather than adding
> its own. See [Nest components](index.md#nest-components).

## Customization

Use the properties and selectors below to customize this component, following the
[Customization](customization.md) guide.

### Component properties

These CSS variables take their default values from the corresponding theme settings.

| Property | Description | Theme setting | Default |
| --- | --- | --- | --- |
| `--alert-note` | Note rail and title | `alert_note_color` | Blue · `#2377c8` |
| `--alert-note-surface` | Note background | `alert_note_surface_color` | Pale blue · `#e4f2ff` |
| `--alert-tip` | Tip rail and title | `alert_tip_color` | Dark green · `#287c35` |
| `--alert-tip-surface` | Tip background | `alert_tip_surface_color` | Pale green · `#e7f5df` |
| `--alert-important` | Important rail and title | `alert_important_color` | Purple · `#6d28d9` |
| `--alert-important-surface` | Important background | `alert_important_surface_color` | Pale lavender · `#f0e8ff` |
| `--alert-warning` | Warning rail and title | `alert_warning_color` | Amber brown · `#a65f00` |
| `--alert-warning-surface` | Warning background | `alert_warning_surface_color` | Pale yellow · `#fff0bf` |
| `--alert-caution` | Caution rail and title | `alert_caution_color` | Dark red · `#b42318` |
| `--alert-caution-surface` | Caution background | `alert_caution_surface_color` | Pale pink · `#ffe3df` |
| `--ink` | Body text | `text_color` | Dark green-gray · `#182018` |
| `--border` | Frame, except the type-specific left rail | `border_color` | Near-black · `#101410` |
| `--shadow` | Frame's pixel shadow | `shadow_color` | Near-black · `#101410` |

Each alert type maps its colors to `--alert-color` for the rail and title, and
`--alert-surface` for the background. Override these two properties on `.gh-alert`
or a type selector such as `.gh-alert--tip` to customize the corresponding alerts.

See [Colors](../setup/colors.md) for palette configuration and
[Fonts](../setup/fonts.md) for typography defaults and overrides.

### Component styles

Use these selectors to style the alert frame, body, title, and individual types.

| Selector | CSS properties | Description |
| --- | --- | --- |
| `.gh-alert` | `background`, `border`, `border-left`, `box-shadow`, `color`, `padding`, `margin` | The alert surface, frame, rail, text, and spacing |
| `.gh-alert__title` | `color`, `font-family`, `font-size`, `text-transform`, `gap`, `margin` | Title typography, spacing, and the gap beside its icon |
| `.gh-alert--note, .gh-alert--tip, .gh-alert--important, .gh-alert--warning, .gh-alert--caution` | `--alert-color`, `--alert-surface` | Rail/title and background colors for each alert type |
