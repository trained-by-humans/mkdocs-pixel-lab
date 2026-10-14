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

This is a Markdown extension, not a plugin. Enable it under
`markdown_extensions` in `mkdocs.yml`; selecting the theme doesn't enable it.

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

Each alert type has a rail/title color and a surface color. These theme
settings customize every alert of that type:

```yaml
theme:
  name: pixel-lab
  alert_tip_color: "#287c35"
  alert_tip_surface_color: "#e7f5df"
  alert_warning_color: "#a65f00"
  alert_warning_surface_color: "#fff0bf"
```

These Pixel Lab parameters belong under `theme` and apply to alerts,
not admonitions:

| Parameter | Default | Effect |
| --- | --- | --- |
| `alert_note_color` | Blue · `#2377c8` | Note rail and title |
| `alert_note_surface_color` | Pale blue · `#e4f2ff` | Note background |
| `alert_tip_color` | Dark green · `#287c35` | Tip rail and title |
| `alert_tip_surface_color` | Pale green · `#e7f5df` | Tip background |
| `alert_important_color` | Purple · `#6d28d9` | Important rail and title |
| `alert_important_surface_color` | Pale lavender · `#f0e8ff` | Important background |
| `alert_warning_color` | Amber brown · `#a65f00` | Warning rail and title |
| `alert_warning_surface_color` | Pale yellow · `#fff0bf` | Warning background |
| `alert_caution_color` | Dark red · `#b42318` | Caution rail and title |
| `alert_caution_surface_color` | Pale pink · `#ffe3df` | Caution background |

For the body text, outline, and shadow:

| Parameter | Default | Effect |
| --- | --- | --- |
| `text_color` | Dark green-gray · `#182018` | Alert body text |
| `border_color` | Near-black · `#101410` | Alert outline, except the type-specific left rail |
| `shadow_color` | Near-black · `#101410` | Alert pixel shadow |

See [Common attributes](../reference/configuration.md#common-attributes).

To customize all tip alerts through a [custom stylesheet](index.md#load-custom-css),
target their component class:

```css
.gh-alert--tip {
  --alert-color: #287c35;   /* Dark green */
  --alert-surface: #e7f5df; /* Pale green */
}
```

### Scoped overrides

Wrap each selected alert, following [Scope selected instances](index.md#scope-selected-instances):

```markdown
<div class="instance-alert" markdown="1">

> [!TIP]
>
> Keep the configuration in one place.

</div>
```

Scope the same CSS variables to `.instance-alert` in your stylesheet.
Unwrapped tip alerts keep the component defaults:

```css
.instance-alert > .gh-alert--tip {
  --alert-color: #287c35;   /* Dark green */
  --alert-surface: #e7f5df; /* Pale green */
}
```
