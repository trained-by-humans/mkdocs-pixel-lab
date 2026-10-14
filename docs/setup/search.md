# Search

Pixel Lab's toolbar search uses the standard MkDocs search index.

## Enable search

MkDocs includes `search` by default. If you specify a `plugins` list, include
it explicitly to keep the search index:

```yaml
plugins:
  - search
```

When adding other plugins, keep `search` in the list. No hosted search service
or API key is required.

This is a native MkDocs plugin, not a Pixel Lab `theme` option:

| Parameter | Default | Effect |
| --- | --- | --- |
| `plugins` → `search` | Enabled by MkDocs unless you replace the plugin list | Builds the index used by the search panel |

See [MkDocs search configuration](https://www.mkdocs.org/user-guide/configuration/#search)
for index options. Search needs JavaScript to load and query the index.

## Use the search panel

Hover over Search to preview the panel. Move into the input without the panel
closing, then click or focus the input to start searching. Leaving an inactive
preview closes it. Escape dismisses active search and returns focus to the
button.

Try the Search button on this website: search for `tabs`, `palette`, or
`repository`.

## Further customization

Replace its artwork with [`theme.icon.search`](icons.md). The
`highlight_color` controls highlighted toolbar buttons, and
`input_focus_background_color` sets the focused input background:

```yaml
theme:
  name: pixel-lab
  highlight_color: "#f5c842"
  input_focus_background_color: "#ffffff"
```

These Pixel Lab parameters belong under `theme`:

| Parameter | Default | Effect |
| --- | --- | --- |
| `icon.search` | `null` (built-in magnifying glass) | Replaces the toolbar search artwork, not the search behavior |
| `highlight_color` | Golden yellow · `#f5c842` | Highlighted search-button background |
| `input_focus_background_color` | White · `#ffffff` | Focused search-input background |
| `surface_color` | Ivory · `#fffdf2` | Toolbar button and search-panel background |
| `surface_alt_color` | Pale khaki · `#e8e4cf` | Unfocused search-input background |
| `accent_color` | Leaf green · `#4caf50` | Focused search-input outline |
| `accent_dark_color` | Dark green · `#287c35` | Search result links |
| `muted_text_color` | Gray-green · `#5f665d` | Search result excerpts |
| `border_color` | Near-black · `#101410` | Button, panel, and input outlines |
| `shadow_color` | Near-black · `#101410` | Panel shadow and highlighted button's pop-out shadow |

See [Common attributes](../reference/configuration.md#common-attributes).

Toolbar buttons reduce to icons at 850px and below while retaining accessible
labels and tooltips. Their highlight, lift, and shadow follow the same styling
as the other toolbar actions.
