# Theme setup

Configure the site once, then focus on writing. These guides follow the parts
of the documentation website you want to change.

| Goal | Guide |
| --- | --- |
| Set a shared palette | [Colors](colors.md) |
| Understand or override typography | [Fonts](fonts.md) |
| Replace toolbar and page-action artwork | [Icons](icons.md) |
| Set the site name, favicon, and footer | [Branding and footer](branding.md) |
| Arrange sections and pages | [Navigation](navigation.md) |
| Enable and style section anchor links | [Heading permalinks](heading-permalinks.md) |
| Enable the search index | [Search](search.md) |
| Link the repository and page sources | [Repository and page actions](repository.md) |
| Link related projects | [Related sites](related-sites.md) |
| Configure opt-in analytics | [Analytics and privacy](analytics.md) |

## Where configuration belongs

Not every setting is a theme option:

- **MkDocs settings** such as `site_name`, `nav`, and `repo_url` describe the site.
- **`theme` settings** control Pixel Lab's appearance and theme features.
- **`markdown_extensions`** enable syntax such as content tabs and heading links.
- **`plugins`** enable build-time behavior such as search and metadata generation.
- **`extra` settings** configure related-site navigation and analytics.

The [configuration reference](../reference/configuration.md) lists defaults
and links to the responsible guide.

Each guide's parameter tables show the default and its effect on that part of
the site. Main configuration is explained beside the example that enables or
defines the feature. Further customization sections cover optional changes to
its appearance, not a second copy of its setup. The Colors, Fonts, and Icons
guides focus entirely on appearance.

Color defaults match this documentation website. Shared effects are called
out, and native MkDocs settings and CSS overrides are identified separately
from Pixel Lab options.

## Component customization

Content-specific settings live with their [component guides](../components/index.md).
For example, the Content tabs guide explains [layout modes](../components/tabs.md#layout-modes)
alongside the tab syntax, then [selected-tab colors](../components/tabs.md#customization)
under Customization. Those colors are configured globally under `theme`, but
you don't have to leave the tab guide to find them.
