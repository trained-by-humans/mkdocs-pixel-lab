# Page metadata

Use YAML front matter to give an individual page a browser/search title and
description. These fields don't replace its visible heading or an explicit
navigation label.

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

These are native page front-matter fields, not Pixel Lab theme parameters:

| Parameter | Default | Effect |
| --- | --- | --- |
| `title` | Not set | Overrides the browser/search title, not the visible H1 or an explicit navigation label |
| `description` | Not set | Supplies the page's description without automatic shortening |

## Site defaults

Use MkDocs' `site_name` and `site_description` in `mkdocs.yml` for site-wide
defaults, not in a page's front matter or the `theme` block:

```yaml
site_name: My documentation
site_description: Guides and reference for my project.
```

| Parameter | Default | Effect |
| --- | --- | --- |
| `site_name` | Required; no default | Appended once to the browser title and used as the last title fallback |
| `site_description` | Not set | Description fallback when no page description is available |

`site_name` also changes the site header; `site_description` is shared by pages
that need the same fallback.

## Automatic defaults

Enable the optional bundled metadata plugin once if pages without explicit
metadata should receive content-derived defaults:

```yaml
plugins:
  - search
  - pixel-lab/metadata
```

The plugin is enabled on this documentation website. It doesn't edit the
Markdown files.

This is an optional bundled plugin, not a `theme` setting:

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

There are no color or icon settings for metadata: it affects the document
head, not a visible content block. Search engines may choose a different title
or snippet. The plugin doesn't change canonical URLs, run Git, or set sitemap
dates; see [Bundled plugins](../reference/plugins.md) for those separate options.
