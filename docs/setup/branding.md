# Branding and footer

## Site name

Set the MkDocs site name:

```yaml
site_name: My documentation
```

Pixel Lab displays it in the header with a decorative pixel TM badge. On
compact screens the name stays on one line and truncates when space runs out.

This is a native MkDocs setting, outside `theme`:

| Parameter | Default | Effect |
| --- | --- | --- |
| `site_name` (MkDocs) | Required; no default | Header name and site-wide browser-title branding |

## Favicon

The theme includes a favicon. Replace it with an SVG or PNG inside your docs
directory:

```yaml
theme:
  name: pixel-lab
  favicon: assets/favicon.svg
```

For this example, put the file at `docs/assets/favicon.svg`. The path is
relative to `docs_dir`, not the repository root.

This Pixel Lab parameter belongs under `theme`:

| Parameter | Default | Effect |
| --- | --- | --- |
| `favicon` | `assets/favicon.png` | Browser tab icon; custom paths are relative to `docs_dir` |

## Footer

```yaml
theme:
  name: pixel-lab
  footer_text: Build something useful
```

This Pixel Lab parameter belongs under `theme`:

| Parameter | Default | Effect |
| --- | --- | --- |
| `footer_text` | `""` | Optional text before the built-in attribution |

Your text appears before the built-in Pixel Lab and Trained-by-Humans
attribution. [Related-site links](related-sites.md) and a configured
[privacy link](analytics.md#privacy-link) can also appear in the footer.

## Further customization

Use [Colors](colors.md) for header, background, text, and border tokens, and
[Fonts](fonts.md) for typography. The TM artwork follows the header text and
accent colors; it isn't controlled by `theme.icon`.

These Pixel Lab parameters belong under `theme`:

| Parameter | Default | Effect |
| --- | --- | --- |
| `header_background` | Leaf green · `#4caf50` | Header fill |
| `accent_foreground_color` | Near-black · `#101410` | Header site name and TM text |
| `accent_color` | Leaf green · `#4caf50` | TM artwork accent |
| `accent_dark_color` | Dark green · `#287c35` | TM artwork's darker accent |
| `border_color` | Near-black · `#101410` | Footer's top divider |
| `muted_text_color` | Gray-green · `#5f665d` | Footer attribution text |

See [Common attributes](../reference/configuration.md#common-attributes).
