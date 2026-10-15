# Search

Pixel Lab's toolbar search uses the standard MkDocs search index.

## Enable search

MkDocs includes its `search` plugin by default. If you specify a `plugins`
list, include it explicitly to keep the search index:

```yaml
plugins:
  - search
```

No hosted search service or API key is required.

| Parameter | Default | Effect |
| --- | --- | --- |
| `plugins` → `search` | Enabled by MkDocs unless you replace the plugin list | Builds the index used by the search panel |

See [MkDocs search configuration](https://www.mkdocs.org/user-guide/configuration/#search)
for index options. Search needs JavaScript to load and query the index.
If it returns no results, see [Troubleshooting](../reference/troubleshooting.md#search-has-no-results).

## Use the search panel

Hover over Search to preview the panel. Move into the input without the panel
closing, then click or focus the input to start searching. Leaving an inactive
preview closes it. Escape dismisses active search and returns focus to the
button.

Try the Search button on this website: search for `tabs`, `palette`, or
`repository`.

For compact toolbar behavior, see [Navigation](navigation.md#responsive-behavior).

## Further customization

To change the highlighted button and focused input backgrounds:

```yaml
theme:
  name: pixel-lab
  highlight_color: "#f5c842"
  input_focus_background_color: "#ffffff"
```

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

See [Icons](icons.md#toolbar-icons) and
[Common attributes](../reference/configuration.md#common-attributes).
