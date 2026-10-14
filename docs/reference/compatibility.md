# Compatibility

## Requirements

- Python 3.10 or newer.
- MkDocs 1.6 or newer, below 2.0.
- Pymdown Extensions 10.x and Pygments 2.19.1 or newer, below 3.0.

Installing Pixel Lab installs these Python dependencies. Required Markdown
extensions must still be enabled in `mkdocs.yml`; see the relevant
[component guide](../components/index.md).

## Theme scope

Pixel Lab uses MkDocs navigation, repository URLs, search, and Markdown
extensions. It doesn't implement Material's full feature set, icon library,
or configuration API. Use Pixel Lab's [configuration reference](configuration.md)
rather than copying Material-specific feature flags.

Current boundaries include:

- Navigation rendering supports up to three levels.
- Content-tab selection styles support up to eight tabs in a group.
- One configured palette; no runtime light/dark switch.
- No separate visible page-contents sidebar or previous/next controls.
- No built-in localization system or dedicated generated 404 template.
- Source-file view URLs are inferred for standard `github.com` URLs only;
  edit actions use MkDocs' resolved URLs for other providers too.

## JavaScript and keyboard behavior

Normal links, heading permalinks, native details, and CSS-driven tab selection
remain usable without JavaScript. Search, automatic/forced tab layouts, table
scrolling wrappers, and copy buttons use JavaScript. Without layout detection,
tab panels retain padding.

The theme provides focus styles and a skip-to-content link. Escape closes
search or navigation overlays and returns focus. Test your own palette,
custom icons, and embedded content with a keyboard and at narrow widths;
theme defaults don't guarantee the accessibility of arbitrary custom content.

For configuration and rendering problems, see [Troubleshooting](troubleshooting.md).
