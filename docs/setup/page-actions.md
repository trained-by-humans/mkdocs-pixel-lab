# Source and edit links

Add View source and Edit this page actions beside the main title. They use
MkDocs' editor URLs, without a GitHub API request or an extra plugin.

## Page source and editing

Set MkDocs' `edit_uri` to your branch and Markdown directory, alongside your
[repository URL](repository.md#repository-button):

```yaml hl_lines="2"
repo_url: https://github.com/OWNER/REPO
edit_uri: edit/main/docs/
theme:
  name: pixel-lab
```

For `docs/guide/setup.md`, MkDocs resolves the editor URL to
`https://github.com/OWNER/REPO/edit/main/docs/guide/setup.md`. Pixel Lab uses it
unchanged for Edit this page, and converts it to `blob/main/docs/guide/setup.md`
for View source. Both actions appear beside the main title by default.

MkDocs' default GitHub edit path uses `master`; specify `main` if that's your
branch. Other providers' editor URLs can power editing, but automatic file-view
URL inference is limited to standard `github.com` URLs.

| Parameter | Default | Effect |
| --- | --- | --- |
| `edit_uri` | Provider-dependent; GitHub uses `edit/master/docs/` | Resolves each Markdown page's editor URL; `""` disables it unless a template supplies the URL |
| `edit_uri_template` | Not set | Provides a custom per-page URL template instead of the ordinary edit URI |

> [!NOTE]
>
> An absolute edit URI can work without `repo_url`, but doesn't enable the
> repository toolbar button. Generated pages need a source mapping from their
> generator; Pixel Lab doesn't guess a Markdown source that doesn't exist.

## Control visibility

Choose which actions to show with the visibility settings under `theme`:

```yaml hl_lines="3 4"
theme:
  name: pixel-lab
  show_source: true
  show_edit: false
```

The example hides Edit this page. Defaults for each action are:

| Parameter | Default | Effect |
| --- | --- | --- |
| `show_source` | `true` | Displays View source when a supported file-view URL can be inferred |
| `show_edit` | `true` | Displays Edit this page when MkDocs supplies a page edit URL |

To disable MkDocs edit URLs entirely, set `edit_uri: ""` and remove any
`edit_uri_template`; this also removes the inferred source link.

## Further customization

Customize the artwork and hover shadows with these `theme` settings:

| Parameter | Default | Effect |
| --- | --- | --- |
| `icon.view` | `null` (code brackets) | Replaces the View source mask |
| `icon.edit` | `null` (pen nib) | Replaces the Edit this page mask |
| `accent_dark_color` | Dark green · `#287c35` | Source/edit hover and keyboard-focus shadows |

See [Icons](icons.md#page-icons) and
[Common attributes](../reference/configuration.md#common-attributes).

Page-action artwork scales with the heading. The links remain usable without
JavaScript; the theme's script moves them immediately after the authored H1
when JavaScript is enabled.

Heading permalinks are separate: see [Heading permalinks](heading-permalinks.md).
