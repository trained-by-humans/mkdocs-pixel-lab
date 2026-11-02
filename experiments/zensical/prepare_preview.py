"""Prepare a disposable Zensical 0.0.72 preview; never edit the source theme.

Run with the dedicated Zensical interpreter described in migration/zensical.md.
This experiment uses private Zensical APIs and is not a supported integration.
"""

from __future__ import annotations

import argparse
from importlib.metadata import version
from pathlib import Path
import re
import shutil

import yaml
import zensical


ROOT = Path(__file__).resolve().parents[2]
UI_COMMIT = "f2e8d027764f7f52272a7064e80c576af5f08de9"

BRIDGE = """import {mount, open, setup} from './client.js';
const button = document.querySelector('#search-toggle');
const root = new URL(base_url.replace(/\\/?$/, '/'), window.location.href);
const index = await fetch(new URL('search.json', root)).then(response => {
  if (!response.ok) throw new Error('Search index unavailable');
  return response.json();
});
for (const item of index.items) item.location = new URL(item.location, root).href;
const host = document.createElement('div');
document.body.append(host);
const shadow = host.attachShadow({mode: 'open'});
const styles = document.createElement('link');
styles.rel = 'stylesheet';
styles.href = new URL('./client.css', import.meta.url).href;
shadow.append(styles);
setup(new URL('./worker.js', import.meta.url).href, {
  highlight: false,
  navigate: url => window.location.assign(url),
});
mount(index, shadow);
button.addEventListener('click', open);
"""

METADATA_BRIDGE = """from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor
from zensical.extensions.context import ContextPreprocessor
from metadata_helpers import page_metadata

class MetadataPostprocessor(Postprocessor):
    def run(self, html):
        context = ContextPreprocessor.from_markdown(self.md)
        if context is None:
            raise RuntimeError('Zensical rendering context is missing')
        context.page.meta['pixel_lab_metadata'] = page_metadata(
            html, meta=context.page.meta, page_title=context.page.title,
            site_name=context.config.get('site_name'),
            site_description=context.config.get('site_description'),
        )
        return html

class MetadataExtension(Extension):
    def extendMarkdown(self, md):
        md.postprocessors.register(MetadataPostprocessor(md), 'pixel_lab_metadata', 0)

def makeExtension(**kwargs):
    return MetadataExtension(**kwargs)
"""


def replace_get(match: re.Match) -> str:
    obj, args = match.groups()
    parts = args.split(',', 1)
    fallback = parts[1].strip() if len(parts) > 1 else 'none'
    return f'({obj}[{parts[0].strip()}] | default({fallback}))'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture', action='store_true', help='Use the small test fixture instead of the docs')
    parser.add_argument('--ui-source', type=Path, required=True, help=f'Zensical UI checkout at {UI_COMMIT}')
    parser.add_argument('--destination', type=Path, required=True, help='Empty directory outside the repository')
    args = parser.parse_args()
    if version('zensical') != '0.0.72':
        parser.error('This experiment is pinned to Zensical 0.0.72')
    destination = args.destination.resolve()
    if destination == ROOT or ROOT in destination.parents:
        parser.error('The destination must be outside the repository')
    if destination.exists() and any(destination.iterdir()):
        parser.error('The destination must be empty')
    ui = args.ui_source.resolve()
    import subprocess
    commit = subprocess.check_output(['git', '-C', str(ui), 'rev-parse', 'HEAD'], text=True).strip()
    if commit != UI_COMMIT:
        parser.error(f'The UI checkout must be at {UI_COMMIT}')
    templates = Path(zensical.__file__).parent / 'templates'
    destination.mkdir(parents=True, exist_ok=True)
    source_config = ROOT / ('tests/fixture_site/mkdocs.yml' if args.fixture else 'mkdocs.yml')
    config = yaml.safe_load(source_config.read_text())
    shutil.copytree(source_config.parent / config.get('docs_dir', 'docs'), destination / 'docs')
    theme = destination / 'overrides'
    shutil.copytree(ROOT / 'src/mkdocs_pixel_lab', theme, ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copyfile(templates / 'sitemap.xml', theme / 'sitemap.xml')
    for file in theme.glob('*.html'):
        file.write_text(re.sub(r'([A-Za-z_][\w.]*)\.get\(([^()]*)\)', replace_get, file.read_text()))
    base = theme / 'base.html'
    text = base.read_text()
    text = text.replace('{% if metadata_title %}', '{% set brand_suffix = " — " ~ config.site_name %}{% if metadata_title %}', 1)
    text = text.replace('not metadata_title.lower().endswith((" — " ~ config.site_name).lower())', '(metadata_title | lower)[-(brand_suffix | length):] != brand_suffix | lower')
    text = text.replace('pixel_lab_metadata | default({})', 'page.meta.pixel_lab_metadata | default({})')
    text = text.replace('id="mkdocs-search-query"', 'id="legacy-disabled-search"')
    text = text.replace('</body>', '<script type="module" src="{{ \'assets/zensical-prototype/bridge.js\' | url }}"></script></body>')
    base.write_text(text)
    actions = theme / 'page_source.html'
    text = actions.read_text().replace('edit_url.split("/", 6)', '(edit_url | split("/") | list)')
    text = text.replace('parts | length == 7', 'parts | length >= 7').replace('~ parts[6]', '~ (parts[6:] | join("/"))')
    actions.write_text(text)
    assets = theme / 'assets/zensical-prototype'
    assets.mkdir()
    client = ui / 'src/assets/javascripts/components/search/client'
    for source, target in [('index.js', 'client.js'), ('index.css', 'client.css')]:
        shutil.copyfile(client / source, assets / target)
    shutil.copyfile(next((templates / 'assets/javascripts/workers').glob('search.*.min.js')), assets / 'worker.js')
    shutil.copyfile(ui / 'LICENSE', assets / 'LICENSE.txt')
    (assets / 'bridge.js').write_text(BRIDGE)
    # Extract the existing pure parser only for this disposable experiment.
    # A real implementation should move it into a shared engine-independent module.
    helpers = (ROOT / 'src/mkdocs_pixel_lab/metadata.py').read_text().split('\nclass MetadataPlugin')[0]
    helpers = helpers.replace('from mkdocs.plugins import BasePlugin, event_priority\n', '')
    (destination / 'metadata_helpers.py').write_text(helpers)
    (destination / 'metadata_bridge.py').write_text(METADATA_BRIDGE)
    config['docs_dir'] = 'docs'
    config['site_dir'] = 'site'
    config['theme'].update(name=None, custom_dir='overrides', variant='classic', font=False)
    config['plugins'] = ['search', {'exclude': {'glob': ['**/*.py', '**/*.pyc', '**/__pycache__/**', 'mkdocs_theme.yml']}}]
    config['markdown_extensions'].append('metadata_bridge')
    (destination / 'mkdocs.yml').write_text(yaml.safe_dump(config, sort_keys=False))
    print(f'Prepared {destination}; see migration/zensical.md for build instructions and limitations.')


if __name__ == '__main__':
    main()
