# Bundled plugins

Pixel Lab includes three optional build-time plugins. They require no
additional package, and none is automatically enabled by selecting the theme.
Keep `search` in the plugin list if your site uses search.

## Page metadata

```yaml
plugins:
  - search
  - pixel-lab/metadata
```

Generates browser/search title and description defaults from page content
when explicit front matter is absent. See [Page metadata](../components/metadata.md)
for front-matter fields, site defaults, and fallback rules.

It doesn't use Git or change sitemap dates.

## Sitemap modification dates

```yaml
site_url: https://example.com/docs/
plugins:
  - search
  - pixel-lab/git-lastmod
```

Sets each Markdown page's sitemap `lastmod` from its last committed Git change.
MkDocs still generates `sitemap.xml` and `sitemap.xml.gz` using `site_url`.

Git and complete repository history are required. In GitHub Actions, use a
checkout with full history:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

Dates use committer timestamps. Unrelated commits and rebuilds don't change
them; local uncommitted edits and front-matter dates don't override them.
Renamed files use their history.

Untracked or generated pages, files outside the documentation repository,
missing history, and shallow clones omit `lastmod` rather than pretending
the page changed today. Without this plugin, MkDocs' normal sitemap dates are
preserved and Pixel Lab doesn't run Git commands.

## Robots.txt

```yaml
site_url: https://example.com/
plugins:
  - search
  - pixel-lab/robots
```

Generates a permissive `robots.txt` with a sitemap URL derived from `site_url`:

```text
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

To customize the rules, add `docs/robots.txt`. Your file takes priority and
is copied unchanged. Without `site_url`, the generated sitemap directive is
omitted. Without the plugin, Pixel Lab doesn't generate `robots.txt`.

Crawlers consult robots rules at the domain root. For project-path hosting,
such as `example.com/project/`, the hosting owner must incorporate these rules
at `example.com/robots.txt`. Robots rules aren't access control.

## Markdown extensions are separate

`mkdocs_pixel_lab.github_alerts` is a Markdown extension, not a plugin. Add it
under `markdown_extensions`, as shown in [Alerts](../components/alerts.md).
Likewise, `toc` and Pymdown Extensions belong under `markdown_extensions`.
