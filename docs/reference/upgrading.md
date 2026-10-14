# Upgrading

Upgrade in your documentation environment, then build and preview before
publishing:

```bash
python -m pip install --upgrade mkdocs-pixel-lab
python -m mkdocs build --strict
python -m mkdocs serve
```

Check [release notes](https://github.com/trained-by-humans/mkdocs-pixel-lab/releases)
for the version you're adopting. Projects with pinned dependencies should
update their pin or lockfile through their normal workflow.

## Moving to 0.2

### Heading permalinks

Use Python-Markdown's `toc` configuration:

```yaml
markdown_extensions:
  - toc:
      permalink: true
```

Remove the obsolete `theme.permalink_icon` and `theme.permalink_fill_color`
settings. There is one built-in link icon; use `toc.permalink` for a text-symbol
replacement or to disable permalinks. See [Heading permalinks](../setup/heading-permalinks.md).

### Page and repository actions

`repo_url` controls the repository button. Available page source and edit
actions are shown by default; choose `show_repo`, `show_source`, and
`show_edit` independently if your site should hide any of them. Use
`show_repo_name: false` for an icon-only repository button.

Check that `edit_uri` names the correct branch and Markdown directory. See
[Repository and page actions](../setup/repository.md) and [Icons](../setup/icons.md).

### Related-site navigation

Use `extra.site_navigation.header_mode` with `dropdown`, `inline`, or `none`
instead of the previous `show_header` / `show_dropdown` flags. Header modes
don't render together; `show_footer` remains independent. See [Related sites](../setup/related-sites.md).

## Preview checklist

- Verify navigation and toolbar actions on desktop and a narrow screen.
- Check source/edit URLs against the deployed branch.
- Try keyboard focus, Escape, search, and content tabs.
- Review custom colors and icons for contrast and sizing.
- Recheck any CSS or template overrides against the current theme.
