# Related sites

Use `extra.site_navigation` to link related projects. Omit it to show no
related-site navigation. These are Pixel Lab settings in `mkdocs.yml`, not
native MkDocs `nav` entries or options under `theme`.

## Items

Define the links once. The footer and both header presentations use the same
ordered `items` list; `catalog` adds a link to the complete project directory.

```yaml
extra:
  site_navigation:
    items:
      - title: Documentation
        url: https://example.com/docs/
        active: true
      - title: API reference
        url: https://example.com/api/
    catalog:
      title: All projects
      url: https://example.com/projects/
```

Each item and the catalog need a title and URL. Mark the current project with
`active: true`; it isn't inferred from the URL. These settings belong under
`extra.site_navigation`:

| Parameter | Default | Effect |
| --- | --- | --- |
| `items` | `[]` | Ordered links used by the footer, inline header, and dropdown |
| `catalog` | Not set | Final link to all projects; required for the footer and inline header, optional in the dropdown |
| `items[].title` / `catalog.title` | Required for each link | Visible link text |
| `items[].url` / `catalog.url` | Required for each link | Link destination |
| `items[].active` | `false` | Marks a related-site item as the current project |

The default header presentation is a dropdown. The footer is independently
enabled when a catalog is configured. Merge the settings below into the same
`extra.site_navigation` block; keep the items and catalog defined above.

## Footer

Show related-site links before the theme attribution:

```yaml
extra:
  site_navigation:
    show_footer: true
    footer_size: 3
    footer_label: Projects
```

The footer requires `catalog`. `footer_size` includes that final link, so
the example displays the first two items followed by All projects. The
default size of `1` shows only the catalog. Links stack vertically on narrow
screens and don't display item icons.

| Parameter | Default | Effect |
| --- | --- | --- |
| `show_footer` | `true` | Enables the footer lane when a catalog is configured |
| `footer_size` | `1` | Maximum footer links, including the catalog link |
| `footer_label` | `Related sites` | Footer lane heading |

Set `show_footer: false` to hide these links without changing the header.
For footer-only links, also set `header_mode: none`.

## Header: inline

Place text links directly in the header instead of using a dropdown:

```yaml
extra:
  site_navigation:
    header_mode: inline
    header_size: 3
```

The header has one presentation at a time: `inline`, `dropdown` (default), or
`none`. These settings also belong under `extra.site_navigation` and don't
change footer visibility:

| Parameter | Default | Effect |
| --- | --- | --- |
| `header_mode` | `dropdown` | Selects `dropdown`, `inline`, or `none` for the header presentation |
| `header_size` | `1` | Maximum inline header links, including the catalog link; doesn't limit the dropdown |

Inline links require `catalog`. Like the footer, a size of `3` displays the
first two items plus the catalog; the default size of `1` shows only the
catalog. Inline links hide on narrow screens and don't display item icons.

## Header: dropdown

Use a toolbar button to open all configured links:

```yaml
extra:
  site_navigation:
    header_mode: dropdown
    dropdown_label: Projects
```

The dropdown appears when `items` or `catalog` provides links; an empty
configuration doesn't add a button. It shows every item, followed by the
optional catalog, regardless of `header_size` or `footer_size`.

This setting belongs under `extra.site_navigation`:

| Parameter | Default | Effect |
| --- | --- | --- |
| `dropdown_label` | `Sites` | Dropdown button text and accessible label |

Hover previews the dropdown; moving into the menu keeps it open and leaving
closes it. Click to pin it open. A second mouse click returns to hover preview,
while touch and keyboard activation toggle it. Escape or an outside click
dismisses it. Use Tab or arrow keys to navigate.

### Item icons

Each item and the catalog can specify an `icon` path relative to `docs_dir`
or an image URL. Artwork appears in the dropdown; omitted artwork gets a
themed pixel fallback.

```yaml
extra:
  site_navigation:
    items:
      - title: API
        url: https://example.com/api/
        icon: assets/api.svg
        icon_hover: assets/api.svg#icon-hover
```

`icon_hover` replaces the resting image on hover or focus and restarts on
each entry. An SVG can use `:target` with a fragment to provide animation.
Use same-origin assets or CORS-enabled URLs. Reduced-motion users retain the
static image; loading failures also leave the resting icon unchanged.

Static images use a 24 × 24 px slot. Hover-enabled images use 24 × 44 px,
including vertical breathing room; include that room in both SVG canvases.

These artwork settings belong under `extra.site_navigation`, not `theme`:

| Parameter | Default | Effect |
| --- | --- | --- |
| `items[].icon` / `catalog.icon` | Not set (pixel fallback) | Resting artwork in dropdown rows |
| `items[].icon_hover` / `catalog.icon_hover` | Not set | Alternate artwork on hover/focus, unless reduced motion is requested |

### Toolbar icons

The button's artwork is configured separately under `theme`, not
`extra.site_navigation`:

```yaml
theme:
  name: pixel-lab
  icon:
    sites: assets/icons/sites.svg
    dropdown: assets/icons/chevron.svg
```

| Parameter | Default | Effect |
| --- | --- | --- |
| `icon.sites` | `null` (pixel grid) | Related-sites toolbar button artwork |
| `icon.dropdown` | `null` (down arrow) | Toolbar dropdown arrow; hidden on compact screens |

See [Icons](icons.md) for image formats and paths. Icon settings replace
artwork; they don't enable the dropdown.

## Further customization

These appearance settings belong under `theme`. Presentation-specific labels,
limits, and icons are documented above.

| Parameter | Default | Effect |
| --- | --- | --- |
| `accent_foreground_color` | Near-black · `#101410` | Inline header links and their dividers |
| `text_color` | Dark green-gray · `#182018` | Resting dropdown link text and footer lane heading |
| `muted_text_color` | Gray-green · `#5f665d` | Resting footer links and their dividers |
| `accent_color` | Leaf green · `#4caf50` | Built-in dropdown item artwork and keyboard-focus outline |
| `highlight_color` | Golden yellow · `#f5c842` | Highlighted toolbar button background |
| `surface_color` | Ivory · `#fffdf2` | Toolbar button and dropdown background |
| `surface_alt_color` | Pale khaki · `#e8e4cf` | Active item background and part of the hovered-item color mix |
| `accent_dark_color` | Dark green · `#287c35` | Active and hovered footer/dropdown link text |
| `border_color` | Near-black · `#101410` | Button and dropdown outlines |
| `shadow_color` | Near-black · `#101410` | Dropdown and highlighted-button pixel shadows |

See [Common attributes](../reference/configuration.md#common-attributes).
