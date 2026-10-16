# Configuration

Merge snippets into your site's `mkdocs.yml`. Don't create duplicate `theme`,
`plugins`, or `markdown_extensions` keys: YAML doesn't merge them for you.

## Configuration map

| Configuration | Owner | Guide |
| --- | --- | --- |
| `site_name` | MkDocs | [Branding](../setup/branding.md#site-name) |
| `site_description` | MkDocs | [Page metadata](../components/metadata.md#site-defaults) |
| `site_url` | MkDocs | [MkDocs site URL](https://www.mkdocs.org/user-guide/configuration/#site_url); also used by [analytics](../setup/analytics.md#enable-ga4) and [sitemap plugins](plugins.md) |
| `nav` | MkDocs | [Navigation](../setup/navigation.md) |
| `repo_url`, `repo_name` | MkDocs | [Repository link](../setup/repository.md) |
| `edit_uri`, `edit_uri_template` | MkDocs | [Source and edit links](../setup/page-actions.md) |
| `theme` palette, visibility flags, icons, favicon, footer | Pixel Lab | [Theme setup](../setup/index.md) |
| `plugins: [search]` | MkDocs | [Search](../setup/search.md) |
| `plugins: [pixel-lab/metadata]` | Bundled plugin | [Page metadata](../components/metadata.md) |
| `pixel-lab/git-lastmod`, `pixel-lab/robots` | Bundled plugins | [Bundled plugins](plugins.md) |
| `markdown_extensions` | Python-Markdown and extensions | [Components](../components/index.md) |
| `markdown_extensions` → `toc.permalink` | Python-Markdown | [Heading permalinks](../setup/heading-permalinks.md) |
| `extra.site_navigation` | Pixel Lab | [Related sites](../setup/related-sites.md) |
| `extra.analytics` | Pixel Lab | [Analytics and privacy](../setup/analytics.md) |
| `extra_css` | MkDocs | [Load custom CSS](../components/index.md#load-custom-css) and [Fonts](../setup/fonts.md#override-typography-with-css) |
| `extra_javascript` | MkDocs | [MkDocs JavaScript configuration](https://www.mkdocs.org/user-guide/configuration/#extra_javascript) |

## Common attributes

Theme attributes apply site-wide. Palette tokens such as `accent_color`,
`surface_color`, and `shadow_color` are reused by multiple components; each
guide's parameter table describes their effect on that component.

See [Colors](../setup/colors.md), [Fonts](../setup/fonts.md), and
[Icons](../setup/icons.md) for the common appearance settings, and
[Theme defaults](#theme-defaults) for every theme attribute and its default.

There is no built-in per-page theme palette. Use
[component-wide or scoped overrides](../components/index.md#customization-scopes)
when you need a narrower styling scope.

## Theme defaults

This is the complete default theme configuration. You don't need to copy it:
start with `name: pixel-lab` and override only the settings you want to change.

```yaml
theme:
  name: pixel-lab
  favicon: assets/favicon.png
  footer_text: ""
  show_repo: true
  show_repo_name: true
  show_source: true
  show_edit: true
  icon:
    repo: null
    search: null
    menu: null
    close: null
    sites: null
    dropdown: null
    view: null
    edit: null
  background_color: "#f4f1df"
  surface_color: "#fffdf2"
  surface_alt_color: "#e8e4cf"
  text_color: "#182018"
  strong_text_color: "#101410"
  muted_text_color: "#5f665d"
  border_color: "#101410"
  shadow_color: "#101410"
  subtle_border_color: "rgba(16, 20, 16, 0.3)"
  sidebar_border_color: "rgba(16, 20, 16, 0.25)"
  grid_color: "rgba(16, 20, 16, 0.035)"
  overlay_color: "rgba(16, 20, 16, 0.45)"
  header_background: "#4caf50"
  header_border_color: "var(--accent-dark)"
  header_shadow_color: "var(--accent-dark)"
  accent_color: "#4caf50"
  accent_dark_color: "#287c35"
  accent_foreground_color: "#101410"
  highlight_color: "#f5c842"
  secondary_color: "#e88932"
  input_focus_background_color: "#ffffff"
  inline_code_border_color: "rgba(40, 124, 53, 0.45)"
  tab_hover_color: "#d8d3b8"
  code_background_color: "#101410"
  code_text_color: "#e9f1d8"
  code_keyword_color: "#72d572"
  code_string_color: "#f5cf54"
  code_function_color: "#4cc4d2"
  code_comment_color: "#7f8978"
  alert_note_color: "#2377c8"
  alert_note_surface_color: "#e4f2ff"
  alert_tip_color: "#287c35"
  alert_tip_surface_color: "#e7f5df"
  alert_important_color: "#6d28d9"
  alert_important_surface_color: "#f0e8ff"
  alert_warning_color: "#a65f00"
  alert_warning_surface_color: "#fff0bf"
  alert_caution_color: "#b42318"
  alert_caution_surface_color: "#ffe3df"
```

`true` visibility flags don't create missing URLs. For example, `show_repo`
still needs `repo_url`, and source/edit actions need a resolved page edit URL.
Null icon values retain the defaults.

## Component appearance

For a token's effect on an individual component, read that component's
Customization section:

- [Text and lists](../components/text.md#customization)
- [Code blocks](../components/code-blocks.md#customization)
- [Alerts](../components/alerts.md#customization)
- [Admonitions](../components/admonitions.md#customization)
- [Content tabs](../components/tabs.md#customization)
- [Collapsible content](../components/details.md#customization)
- [Tables](../components/tables.md#customization)
- [Images and video](../components/media.md#customization)

[Customization scopes](../components/index.md#customization-scopes) explains
component-wide and scoped CSS overrides.

For the full set of native settings, use the
[MkDocs configuration reference](https://www.mkdocs.org/user-guide/configuration/).
