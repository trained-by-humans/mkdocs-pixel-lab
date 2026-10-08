"""Sitemap dates from the last committed change to each page's source file."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import subprocess

from mkdocs.plugins import BasePlugin, event_priority


def _git(directory: Path, *arguments: str) -> str | None:
    """Run read-only Git commands, treating missing history as unavailable."""
    try:
        result = subprocess.run(
            ["git", "--no-pager", "--literal-pathspecs", "-C", str(directory), *arguments],
            check=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip()


class GitLastModified:
    """Look up page dates in one complete repository, caching within a build."""

    def __init__(self, docs_dir: str | Path) -> None:
        self._root: Path | None = None
        self._dates: dict[Path, str | None] = {}
        root = _git(Path(docs_dir).resolve(), "rev-parse", "--show-toplevel")
        if root:
            directory = Path(root).resolve()
            # A shallow boundary can falsely report every file as newly changed.
            if _git(directory, "rev-parse", "--is-shallow-repository") == "false":
                self._root = directory

    def date_for(self, source_path: str | Path | None) -> str | None:
        """Return an ISO committer date, or None when it cannot be established."""
        if source_path is None or self._root is None:
            return None
        source = Path(source_path).resolve()
        if source in self._dates:
            return self._dates[source]
        try:
            relative = source.relative_to(self._root).as_posix()
        except ValueError:
            return None

        value = None
        # Do not reuse an old path's history for an untracked/generated file.
        if _git(self._root, "ls-files", "--error-unmatch", "--", relative) is not None:
            committed = _git(
                self._root, "log", "-1", "--follow", "--no-show-signature", "--format=%cs", "--", relative
            )
            if committed:
                try:
                    value = date.fromisoformat(committed).isoformat()
                except ValueError:
                    pass
        self._dates[source] = value
        return value


class GitLastmodPlugin(BasePlugin):
    """Opt in to Git-derived sitemap dates independently of page metadata."""

    def on_pre_build(self, *, config):
        # Refresh for every rebuild, including commits made during mkdocs serve.
        self._git_dates = GitLastModified(config.docs_dir)

    @event_priority(-100)
    def on_env(self, env, *, config, files):
        # Run before static templates, including pages skipped in dirty builds.
        for file in files.documentation_pages():
            if file.page is None:
                continue
            modified = self._git_dates.date_for(file.abs_src_path)
            file.page.pixel_lab_lastmod = modified
            # MkDocs needs a valid date for the gzip header even when the
            # sitemap omits lastmod. Never clear its internal update_date.
            if modified:
                file.page.update_date = modified
        return env
