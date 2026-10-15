# Repository link

Add a toolbar button linking to your project's repository. For links to the
current page's Markdown file, see [Source and edit links](page-actions.md).

## Repository button

Set MkDocs' top-level `repo_url` and optional `repo_name` in `mkdocs.yml`:

```yaml
repo_url: https://github.com/OWNER/REPO
repo_name: GitHub
```

| Parameter | Default | Effect |
| --- | --- | --- |
| `repo_url` | Not set | Provides the repository destination and enables the toolbar link |
| `repo_name` | Inferred from `repo_url` | Supplies the repository button's label and accessible name |

MkDocs normally infers GitHub, GitLab, or Bitbucket for the label.

## Control visibility

Show only the icon, or hide the button entirely, with these `theme` settings:

```yaml hl_lines="4"
theme:
  name: pixel-lab
  show_repo: true
  show_repo_name: false
```

| Parameter | Default | Effect |
| --- | --- | --- |
| `show_repo` | `true` | Displays the repository button when `repo_url` is available |
| `show_repo_name` | `true` | Shows the repository label; `false` keeps only the icon |

The icon-only version retains its accessible label and tooltip. See
[Navigation](navigation.md#responsive-behavior) for compact toolbar behavior.

## Further customization

Customize the button's artwork under `theme`:

| Parameter | Default | Effect |
| --- | --- | --- |
| `icon.repo` | `null` (Git branch) | Replaces the repository artwork |

See [Icons](icons.md#toolbar-icons) and
[Common attributes](../reference/configuration.md#common-attributes).
