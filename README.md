# Pixel Lab

Pixel Lab is a vibrant, accessible theme for [MkDocs](https://www.mkdocs.org/).

## Preview

<table>
  <tr>
    <td align="center"><img src="tests/snapshots/desktop.png" alt="Pixel Lab desktop documentation preview" height="480"></td>
    <td align="center"><img src="tests/snapshots/mobile.png" alt="Pixel Lab mobile documentation preview" height="480"></td>
  </tr>
  <tr>
    <td align="center">Desktop</td>
    <td align="center">Mobile</td>
  </tr>
</table>

## Quick start

```bash
python -m pip install mkdocs-pixel-lab
```

Use it in `mkdocs.yml`:

```yaml
theme:
  name: pixel-lab
```

The snippets below show settings to merge into your existing `mkdocs.yml`.

## Everyday features

### Responsive navigation

Primary navigation tabs and the contextual section sidebar follow MkDocs'
`nav:` tree. Narrow browser windows use a menu drawer with the same links,
whether viewed on a phone or desktop. The current page and section are marked
automatically.

### Search

The toolbar search opens a compact panel backed by MkDocs' search index.
Enable the standard plugin:

```yaml
plugins:
  - search
```

### Heading links and keyboard access

Section headings (H2–H6) show a permalink icon after the title. H1 page titles
keep their IDs without an icon.

Choose `link` (the default chain-link icon) or `hash` (the `#` icon) with
`theme.permalink_icon`. Both use the accent color, dark-accent hover, and
heading-relative sizing.

The URL fragment follows the current section as you scroll, without adding
browser-history entries. Enable visible heading permalinks with:

```yaml
theme:
  name: pixel-lab
  permalink_icon: link # or hash
markdown_extensions:
  - toc:
      permalink: true
```

A skip-to-content link, visible focus styles, and labeled navigation regions
support keyboard use. Escape closes the search panel or open navigation drawer
and returns focus to its toolbar button.

### Media, tables, and nested shadows

Images and videos scale to the available content width. Wide tables scroll
inside a fixed bordered frame, keeping its pixel shadow in place. When cards,
alerts, tables, media, or code are nested inside an elevated component, inner
shadows are removed automatically so only the outer component is elevated.

### Bundled fonts

Inter and IBM Plex Mono are served with the theme. No Google Fonts request or
external font service is required.

## Rich Markdown content

### Code blocks

Syntax-highlighted code blocks include a one-click copy button with success
and failure feedback. Enable Pymdown's fenced-code and highlighting extensions:

```yaml
markdown_extensions:
  - pymdownx.superfences
  - pymdownx.highlight
```

Code and inline-code colors follow the theme palette; long blocks scroll
horizontally.

### GitHub Alerts

Enable GitHub-style Markdown alerts explicitly when a site uses them:

```yaml
markdown_extensions:
  - mkdocs_pixel_lab.github_alerts
```

The extension supports `NOTE`, `TIP`, `IMPORTANT`, `WARNING`, and `CAUTION`:

```markdown
> [!TIP]
>
> Use semantic callouts for important guidance.
```

### Content tabs and collapsible notes

Admonitions, expandable details, and content tabs use the same pixel borders
and palette as the rest of the theme. Enable the corresponding extensions:

```yaml
markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.tabbed:
      alternate_style: true
```

Content tabs are separate from the primary navigation tabs below the toolbar.

## Customize your site

### Palette

Every theme color is configured from the single `theme:` block in `mkdocs.yml`.
The default palette preserves Pixel Lab’s original appearance; override only
the tokens your site needs:

```yaml
theme:
  name: pixel-lab

  # Brand
  header_background: "#8315F9"
  accent_color: "#8315F9"
  accent_dark_color: "#5E0AAE"
  accent_foreground_color: "#FFFFFF"

  # Neutrals used by every component
  background_color: "#f4f1df"
  surface_color: "#fffdf2"
  surface_alt_color: "#e8e4cf"
  text_color: "#182018"
  muted_text_color: "#5f665d"
  border_color: "#101410"
  shadow_color: "#101410"
```

`header_background` accepts any CSS background value, including a linear
gradient. All other options accept any valid CSS color, including `rgba()` and
CSS variables.

<details>
<summary>Palette token reference</summary>

| Tokens | Used for |
| --- | --- |
| `background_color`, `surface_color`, `surface_alt_color` | Page, cards, input, and table surfaces. |
| `text_color`, `strong_text_color`, `muted_text_color` | Body, control, and secondary text. |
| `border_color`, `shadow_color`, `subtle_border_color`, `sidebar_border_color` | Component outlines, offset shadows, table rules, and navigation dividers. |
| `grid_color`, `overlay_color` | Page grid and mobile-navigation scrim. |
| `header_background`, `header_border_color`, `header_shadow_color`, `accent_color`, `accent_dark_color`, `accent_foreground_color` | Header, links, navigation, active states, and accent-filled controls. |
| `highlight_color`, `secondary_color`, `input_focus_background_color`, `inline_code_border_color`, `tab_hover_color` | Interactive controls, badges, inline code, and hover states. |
| `code_background_color`, `code_text_color`, `code_keyword_color`, `code_string_color`, `code_function_color`, `code_comment_color` | Code block and syntax-highlight colors. |
| `alert_note_color`, `alert_note_surface_color`, `alert_tip_color`, `alert_tip_surface_color`, `alert_important_color`, `alert_important_surface_color`, `alert_warning_color`, `alert_warning_surface_color`, `alert_caution_color`, `alert_caution_surface_color` | GitHub Alert rails, titles, and surfaces. |

</details>

This separation lets a site change its border and shadow independently without
having to maintain CSS overrides or edit the theme.

The analytics acceptance button uses `header_background` and
`accent_foreground_color`, matching the header background and site title
without separate color settings.

### Favicon

Pixel Lab includes a default favicon. Override it for a site-specific mark:

```yaml
theme:
  name: pixel-lab
  favicon: assets/favicon.svg
```

The custom path is relative to your documentation directory. SVG and PNG
favicons are supported.

### Footer and branding

The site title includes a decorative pixel TM badge. Its circle and letter
fill follow the title's text color; the glyph's outer and inner borders use
the light and dark theme accents. Add a short footer message with
`theme.footer_text`; the built-in Pixel
Lab and Trained-by-Humans attribution remains below any related-site links:

```yaml
theme:
  name: pixel-lab
  footer_text: Build something useful
```

## Site navigation

An optional compact navigation lane can link related documentation sites.
Configure the displayed links, active site, catalog, and independent
header/footer capacities in `extra.site_navigation`:

<details>
<summary>Site navigation configuration</summary>

```yaml
extra:
  site_navigation:
    show_header: true
    show_footer: true
    header_size: 4 # includes the catalog link
    footer_size: 7 # includes the catalog link
    footer_label: Packages
    items:
      - title: Core
        url: https://ml-pipes.com/
      - title: Supervision
        url: https://supervision.ml-pipes.com/
        active: true
      - title: Vision
        url: https://github.com/trained-by-humans/ml-pipes/tree/main/packages/vision
    catalog:
      title: All Packages →
      url: https://ml-pipes.com/PACKAGES/
```

</details>

Omit `site_navigation` to render neither lane. When it is configured,
`show_header` and `show_footer` independently control whether each lane is
rendered (both default to `true`). The header renders up to `header_size` links
and the footer up to `footer_size`; each capacity includes the catalog link. On
narrow screens, the header lane hides and the footer links stack vertically.

## Analytics and privacy

### Google Analytics 4

Analytics is off by default. Configure a GA4 Measurement ID (`G-…`, not a
Firebase API key or Google Tag Manager ID) and your privacy-notice URL to
enable the built-in opt-in prompt:

```yaml
site_url: https://ml-pipes.com/
theme:
  name: pixel-lab
extra:
  analytics:
    provider: google
    measurement_id: G-XXXXXXXXXX
    privacy_policy: https://ml-pipes.com/privacy/
```

The prompt appears automatically on the first HTTPS visit matching `site_url`.
**Allow analytics** loads the Google tag; **Decline** does not. Choices can be
changed through **Analytics settings** in the footer. Withdrawal disables
collection, attempts to clear the site's GA cookies, and reloads the page.
Set `enabled: false` under `analytics` to turn the integration off. Google is
currently the only supported analytics provider.

<details>
<summary>Google setup and data-handling notes</summary>

Missing or invalid Measurement IDs leave tracking off. Local development and
alternate-host previews do not collect visits. When browser storage is blocked,
a choice applies only to the current page. Advertising consent remains denied;
Google Signals and advertising personalization are disabled. Initial page URLs
and referrers omit query strings and fragments.

To configure a GA4 property:

1. In [Google Analytics](https://analytics.google.com/), create a GA4 property
   and a **Web** data stream for your production site.
2. Copy its Measurement ID. Related documentation sites can share an ID;
   distinguish them in reports by **Hostname**. The theme keeps GA cookies
   hostname-specific, so user counts are not deduplicated across subdomains.
3. In **Enhanced measurement → Page views → Advanced settings**, disable page
   changes based on browser history events. Heading-fragment updates are not
   separate page visits. Review the other automatic measurements you enable.
4. Publish a privacy notice and configure its URL. Review applicable consent
   requirements; this prompt is not a certification of legal compliance. Do
   not send personal information through events or page titles.
5. Deploy and verify acceptance in **Realtime**. Test denial in a fresh browser
   context; Google requests should be absent.

The Measurement ID is public, not a secret. No API key, Firebase SDK, GitHub
secret, or separate subdomain property is required. Reports describe consenting
visitors, not every visit or an individual's identity.

References: [Google tag setup](https://developers.google.com/tag-platform/gtagjs)
and [consent implementation](https://developers.google.com/tag-platform/security/guides/consent).

</details>

### Privacy links

`extra.analytics.privacy_policy` is required: a missing, empty, or whitespace-only
URL keeps analytics off. The same link appears in the consent prompt and
footer, alongside **Analytics settings** when tracking is enabled. Retaining
the URL with `enabled: false` keeps the policy link visible. Relative URLs such
as `privacy/` work from nested pages.

Publish a notice customized to your operator and data practices; Pixel Lab
does not supply a universal privacy policy. Related sites may link to one
shared notice that explicitly covers them.

### Consent across sites

By default, consent is stored per documentation site URL and Measurement ID,
including separate project paths on the same GitHub Pages hostname. To share
acceptance and rejection across a custom domain and its subdomains, configure
the same `consent_domain` and Measurement ID on every participating site:

```yaml
extra:
  analytics:
    provider: google
    measurement_id: G-XXXXXXXXXX
    consent_domain: ml-pipes.com
    privacy_policy: https://ml-pipes.com/privacy/
```

Both acceptance and rejection are shared through a consent-only cookie scoped
to that domain, with `Secure`, `SameSite=Lax`, `Path=/`, and a 180-day lifetime.
The prompt identifies the shared domain. Use this only for sites you control
under the same privacy policy, not public suffixes or shared hosting domains
such as `github.io`. Other open sites synchronize changes on focus and
periodically. Only consent is shared; GA cookies remain hostname-specific.

Unrelated or malformed domains disable analytics, and browsers reject
public-suffix cookies. No parent domain is inferred automatically. Changing
the consent scope requires a new choice; previous site-only choices are not
silently promoted to domain-wide permission.

## Development

```bash
python -m pip install -e '.[test]'
playwright install chromium
pytest
```
