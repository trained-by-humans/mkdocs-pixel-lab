"""Build-time page metadata from explicit fields or introductory HTML content."""

from __future__ import annotations

from collections.abc import Mapping
from html.parser import HTMLParser
from typing import Any

from mkdocs.plugins import BasePlugin, event_priority

DESCRIPTION_LENGTH = 160
_VOID_TAGS = frozenset("area base br col embed hr img input link meta param source track wbr".split())
_SKIP_TAGS = frozenset(
    "aside blockquote details dl figure figcaption footer form header nav ol pre script style svg table ul".split()
)
_SKIP_CLASSES = frozenset({"admonition", "gh-alert", "headerlink", "highlight", "tabbed-set", "toc"})


def _text(value: Any) -> str:
    """Accept text fields only and normalize whitespace without interpreting HTML."""
    return " ".join(value.split()) if isinstance(value, str) else ""


class _IntroductionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.heading = ""
        self.paragraph = ""
        self._stack: list[tuple[str, bool]] = []
        self._capture: tuple[str, int] | None = None
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        blocked = bool(self._stack and self._stack[-1][1]) or (
            tag in _SKIP_TAGS
            or bool(classes & _SKIP_CLASSES)
            or "hidden" in attributes
            or (attributes.get("aria-hidden") or "").lower() == "true"
        )
        if tag in _VOID_TAGS:
            if tag == "br" and self._capture and not blocked:
                self._parts.append(" ")
            return
        self._stack.append((tag, blocked))
        if not blocked and self._capture is None and (
            (tag == "h1" and not self.heading) or (tag == "p" and not self.paragraph)
        ):
            self._capture = (tag, len(self._stack))
            self._parts = []

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in _VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self._stack) - 1, -1, -1):
            if self._stack[index][0] != tag:
                continue
            if self._capture and self._capture[1] >= index + 1:
                capture_tag, _ = self._capture
                value = _text("".join(self._parts))
                if capture_tag == "h1":
                    self.heading = value
                else:
                    self.paragraph = value
                self._capture = None
                self._parts = []
            del self._stack[index:]
            break

    def handle_data(self, data: str) -> None:
        if self._capture and self._stack and not self._stack[-1][1]:
            self._parts.append(data)


def _excerpt(value: str) -> str:
    if len(value) <= DESCRIPTION_LENGTH:
        return value
    prefix = value[: DESCRIPTION_LENGTH - 1]
    if " " in prefix:
        prefix = prefix.rsplit(" ", 1)[0]
    return prefix.rstrip(" .,:;!?") + "…"


def page_metadata(
    html: str,
    *,
    meta: Mapping[str, Any] | None = None,
    page_title: str | None = None,
    site_name: str | None = None,
    site_description: str | None = None,
) -> dict[str, str]:
    """Derive unbranded title and description without changing page content."""
    parser = _IntroductionParser()
    parser.feed(html)
    parser.close()
    fields = meta or {}
    return {
        "title": _text(fields.get("title")) or parser.heading or _text(page_title) or _text(site_name),
        "description": _text(fields.get("description")) or _excerpt(parser.paragraph) or _text(site_description),
    }


class MetadataPlugin(BasePlugin):
    """Provide content-based page metadata without Git or sitemap changes."""

    @event_priority(-100)
    def on_page_context(self, context, *, page, config, nav):
        context["pixel_lab_metadata"] = page_metadata(
            page.content or "",
            meta=page.meta,
            page_title=page.title,
            site_name=config.site_name,
            site_description=config.site_description,
        )
        return context
