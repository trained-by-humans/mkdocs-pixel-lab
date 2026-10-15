# Page metadata

Use MkDocs' YAML front matter to give an individual page a browser/search
title and description. These fields don't replace its visible heading or an
explicit navigation label.

## Write metadata

```markdown
---
title: Configure your first Pixel Lab site
description: Install the theme, choose a palette, and preview your documentation.
---

# Get started
```

The theme honors `title` and `description` without an extra plugin, appending
the site name to the browser title once. Look at this page's HTML `<title>`
and `<meta name="description">` to inspect the output.

| Parameter | Default | Effect |
| --- | --- | --- |
| `title` | Not set | Overrides the browser/search title, not the visible H1 or an explicit navigation label |
| `description` | Not set | Supplies the page's description without automatic shortening |

## Site defaults

Set site-wide defaults with MkDocs' top-level `site_name` and
`site_description` in `mkdocs.yml`:

```yaml
site_name: My documentation
site_description: Guides and reference for my project.
```

| Parameter | Default | Effect |
| --- | --- | --- |
| `site_name` | Required; no default | Appended once to the browser title and used as the last title fallback |
| `site_description` | Not set | Description fallback when no page description is available |

For the header's site name, see [Branding and footer](../setup/branding.md#site-name).

## Automatic defaults

Add the bundled `pixel-lab/metadata` plugin to MkDocs' `plugins` list to
generate defaults for pages without explicit metadata:

```yaml
plugins:
  - search
  - pixel-lab/metadata
```

The plugin is enabled on this documentation website. It doesn't edit the
Markdown files.

| Parameter | Default | Effect |
| --- | --- | --- |
| `plugins` → `pixel-lab/metadata` | Not enabled | Derives missing metadata from the first H1 and introductory paragraph |

When enabled, the plugin uses this fallback order:

| Field | Fallback order |
| --- | --- |
| Title | Front-matter title → first H1 → MkDocs page title → site name |
| Description | Front-matter description → first introductory paragraph → site description |

Generated descriptions skip code, tables, alerts, lists, images, and navigation,
and are shortened at a word boundary to at most 160 characters. Explicit
descriptions aren't shortened. Blank or non-text metadata is ignored by the
plugin. If no description is available, the tag is omitted.

## Scope

Search engines may choose a different title or snippet. The plugin doesn't
change canonical URLs or sitemap dates; see
[Sitemap modification dates](../reference/plugins.md#sitemap-modification-dates)
for Git-based dates.
