# Repository and page actions

The repository button opens the project. View source and Edit this page open
the current page's source. They use native MkDocs URLs, without a GitHub API
request or an extra plugin.

## Repository button

```yaml
repo_url: https://github.com/OWNER/REPO
repo_name: GitHub
```

These are native MkDocs settings, outside `theme`:

| Parameter | Default | Effect |
| --- | --- | --- |
| `repo_url` | Not set | Provides the repository destination and enables the toolbar link |
| `repo_name` | Inferred from `repo_url` | Supplies the repository button's label and accessible name |

`repo_url` enables the toolbar button. `repo_name` supplies its label; MkDocs
normally infers GitHub, GitLab, or Bitbucket. Hide the name, or the entire
button, independently:

```yaml
theme:
  name: pixel-lab
  show_repo: true
  show_repo_name: false
```

The icon-only version retains its accessible label and tooltip. Compact
screens always use icon-only toolbar buttons.

## Page source and editing

Configure the branch and Markdown directory explicitly:

```yaml
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

These are native MkDocs settings, outside `theme`:

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

```yaml
theme:
  name: pixel-lab
  show_source: true
  show_edit: false
```

These Pixel Lab parameters belong under `theme`. Their defaults are shown
below; the example above overrides only edit visibility:

| Parameter | Default | Effect |
| --- | --- | --- |
| `show_repo` | `true` | Displays the repository button when `repo_url` is available |
| `show_repo_name` | `true` | Shows the repository label; `false` keeps only the icon |
| `show_source` | `true` | Displays View source when a supported file-view URL can be inferred |
| `show_edit` | `true` | Displays Edit this page when MkDocs supplies a page edit URL |

`show_source` and `show_edit` both default to `true` when the relevant URLs
exist. They are independent of `show_repo`. To disable MkDocs edit URLs
entirely, set `edit_uri: ""` and remove any `edit_uri_template`; this also
removes the inferred source link.

## Further customization

Use [`theme.icon.repo`, `theme.icon.view`, and `theme.icon.edit`](icons.md).
The defaults are a Git branch, code brackets, and a pen nib respectively.

| Parameter | Default | Effect |
| --- | --- | --- |
| `icon.repo` | `null` (Git branch) | Replaces the repository artwork |
| `icon.view` | `null` (code brackets) | Replaces the View source mask |
| `icon.edit` | `null` (pen nib) | Replaces the Edit this page mask |
| `accent_dark_color` | Dark green · `#287c35` | Source/edit hover and keyboard-focus shadows |

These are Pixel Lab settings under `theme`. Null icons retain the built-in
artwork, not hide the buttons.

See [Common attributes](../reference/configuration.md#common-attributes).

Page-action artwork scales with the heading. Its hover/focus shadow uses
`accent_dark_color`. These links remain usable without JavaScript; the theme's
script moves them immediately after the authored H1 when JavaScript is enabled.

Heading permalinks are separate: see [Heading links](../components/heading-links.md).
