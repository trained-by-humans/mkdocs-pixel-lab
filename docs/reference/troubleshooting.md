# Troubleshooting

Find fixes for common configuration and rendering problems. For supported
versions and theme limitations, see [Compatibility](compatibility.md).

## A component looks like plain text

Check that its Markdown extension is enabled, its indentation is correct,
and the YAML hasn't overwritten another `markdown_extensions` list. For tabs,
set `alternate_style: true`. For Markdown inside an HTML wrapper, use
`md_in_html` and `markdown="1"`.

## A custom icon looks too small or like a filled box

Artwork with internal padding occupies less of the icon slot. Source and edit
images are alpha masks: use transparent backgrounds. See [Icons](../setup/icons.md).

## Source links point at the wrong branch

Set `edit_uri` explicitly for the branch and documentation directory. MkDocs'
GitHub default uses `master`, not `main`. See [Repository and page actions](../setup/repository.md).

## Search has no results

Keep `search` in `plugins`, rebuild the site, and preview through `mkdocs serve`
instead of opening built files directly with `file://`. Search requires
JavaScript and its generated index. See [Search](../setup/search.md) for setup.

## A bundled plugin is missing

Confirm that the environment running MkDocs has the expected Pixel Lab version
installed. Use `python -m mkdocs` to select the active Python environment.
See [Bundled plugins](plugins.md) for exact plugin names.
