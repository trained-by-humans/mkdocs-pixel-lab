"""Optional public-crawling defaults, with site-owned robots.txt taking priority."""

from urllib.parse import urljoin

from mkdocs.plugins import BasePlugin, event_priority
from mkdocs.structure.files import File


class RobotsPlugin(BasePlugin):
    """Generate robots.txt from site_url without replacing an existing file."""

    @event_priority(-100)
    def on_files(self, files, *, config):
        if files.get_file_from_path("robots.txt") is None:
            content = "User-agent: *\nAllow: /\n"
            if config.site_url:
                content += f"\nSitemap: {urljoin(config.site_url, 'sitemap.xml')}\n"
            files.append(File.generated(config, "robots.txt", content=content))
        return files
