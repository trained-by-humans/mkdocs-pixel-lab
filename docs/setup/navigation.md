# Navigation

Use MkDocs' `nav` tree to define the site structure. Top-level entries become
primary navigation tabs; pages inside the active section appear in the sidebar.

## Configure navigation

```yaml
nav:
  - Home: index.md
  - Guide:
      - Overview: guide/index.md
      - Installation: guide/installation.md
      - Usage: guide/usage.md
```

Navigation paths are relative to `docs_dir`. Labels in `nav` can differ from
the page's visible heading.

This is a native MkDocs setting at the top level of `mkdocs.yml`, not under
`theme`:

| Parameter | Default | Effect |
| --- | --- | --- |
| `nav` | Inferred from documentation files | Defines primary sections, sidebar pages, and drawer links |

Omit `nav` to let MkDocs discover pages automatically, or set it explicitly
to control their order, labels, and grouping.

- Use [Related sites](related-sites.md) for links to other projects, not pages
  in the current documentation.
- Primary navigation tabs are different from [content tabs](../components/tabs.md).

See [MkDocs: configure pages and navigation](https://www.mkdocs.org/user-guide/writing-your-docs/#configure-pages-and-navigation)
for the underlying `nav` behavior.

## Responsive behavior

Narrow screens use a navigation drawer with the same section and page links.
The active page is marked automatically. A skip-to-content link and visible
focus styles support keyboard use; Escape closes the drawer and returns focus
to its toolbar button.

Keep hierarchies shallow: Pixel Lab currently renders up to three navigation
levels. It doesn't provide a separate visible on-page table of contents or
previous/next page controls.

## Further customization

These Pixel Lab parameters belong under `theme`:

| Parameter | Default | Effect |
| --- | --- | --- |
| `icon.menu` | `null` (built-in menu) | Replaces the mobile drawer's open icon |
| `icon.close` | `null` (built-in close) | Replaces the mobile drawer's close icon |
| `accent_dark_color` | Dark green · `#287c35` | Active navigation text and mobile active-page rail |
| `accent_color` | Leaf green · `#4caf50` | Primary-navigation markers |
| `surface_color` | Ivory · `#fffdf2` | Primary navigation, desktop active-page fill, and drawer background |
| `surface_alt_color` | Pale khaki · `#e8e4cf` | Mobile active-page fill |
| `border_color` | Near-black · `#101410` | Primary-navigation divider, active-page outline, and drawer frame |
| `shadow_color` | Near-black · `#101410` | Desktop active-page shadow |
| `sidebar_border_color` | Near-black at 25% · `rgba(16, 20, 16, 0.25)` | Desktop sidebar divider |
| `overlay_color` | Near-black at 45% · `rgba(16, 20, 16, 0.45)` | Scrim behind the open mobile drawer |

See [Common attributes](../reference/configuration.md#common-attributes) and
[Icons](icons.md) for supported image paths.
