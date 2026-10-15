# Icons

Replace individual toolbar or page-action icons with image files. Values are
paths relative to `docs_dir` or image URLs, not Material icon-library names.

```yaml
theme:
  name: pixel-lab
  icon:
    repo: assets/icons/repo.svg
    search: assets/icons/search.svg
    menu: assets/icons/menu.svg
    close: assets/icons/close.svg
    sites: assets/icons/sites.svg
    dropdown: assets/icons/chevron.svg
    view: assets/icons/source.svg
    edit: assets/icons/edit.svg
```

For example, `assets/icons/edit.svg` belongs at
`docs/assets/icons/edit.svg`. Use only the keys you want to replace.

Set icons under `theme.icon`. A `null` value keeps the built-in artwork.

## Toolbar icons

| Parameter | Default | Effect |
| --- | --- | --- |
| `icon.repo` | `null` (Git branch) | Replaces the [repository button](repository.md#repository-button) artwork |
| `icon.search` | `null` (magnifying glass) | Replaces the [search button](search.md#use-the-search-panel) artwork |
| `icon.menu` | `null` (menu) | Replaces the [mobile navigation](navigation.md#responsive-behavior) open icon |
| `icon.close` | `null` (close) | Replaces the [mobile navigation](navigation.md#responsive-behavior) close icon |
| `icon.sites` | `null` (pixel grid) | Replaces the [related-sites button](related-sites.md#header-dropdown) artwork |
| `icon.dropdown` | `null` (down arrow) | Replaces the [dropdown arrow](related-sites.md#toolbar-icons); remains omitted on compact screens |

SVG is recommended; PNG and other browser-supported image formats also work.
Toolbar artwork preserves its original colors and fits a 14 × 14 px slot.

> [!TIP]
>
> Internal padding in an image makes its visible artwork look smaller.

The button—not the artwork—provides the background, highlight, lift, and
shadow. Changing an icon doesn't enable its feature or change its accessible
label.

## Page icons

| Parameter | Default | Effect |
| --- | --- | --- |
| `icon.view` | `null` (code brackets) | Replaces the View source artwork beside the title |
| `icon.edit` | `null` (pen nib) | Replaces the Edit this page artwork beside the title |

Configure destinations and visibility in [Source and edit links](page-actions.md).

Source and edit icons use the image's alpha channel as a mask. Use artwork
with a transparent background: an opaque white rectangle becomes a filled
rectangle, not empty space. Custom icons receive a black silhouette and a
matching `accent_dark_color` hover/focus shadow, rather than the original
image colors.

Remote mask images must allow cross-origin loading (CORS). Local assets avoid
that dependency. These image and mask styles work without JavaScript.

For sizing or mask problems, see [Troubleshooting](../reference/troubleshooting.md#a-custom-icon-looks-too-small-or-like-a-filled-box).

## Other artwork

- [Heading permalinks](heading-permalinks.md#further-customization) use the built-in
  link icon or Python-Markdown's `toc.permalink` text, not `theme.icon`.
- [Related-site items](related-sites.md#item-icons) use their own `icon` and
  `icon_hover` properties.
- The site-name/TM artwork and navigation markers aren't `theme.icon` options.
