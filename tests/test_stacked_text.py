"""Browser coverage for optional SVG stacked lettering."""

import mimetypes
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

from mkdocs.commands.build import build
from mkdocs.config import load_config
import pytest
from playwright.sync_api import expect


FIXTURE = Path(__file__).parent / "fixture_site" / "mkdocs.yml"
ORIGIN = "https://example.invalid"


@pytest.fixture(scope="session")
def stacked_site(tmp_path_factory):
    destination = tmp_path_factory.mktemp("stacked-site")
    build(load_config(config_file=str(FIXTURE), site_dir=str(destination), strict=True))
    return destination


def serve(page, destination):
    def respond(route):
        url = urlsplit(route.request.url)
        if url.netloc != "example.invalid":
            route.abort()
            return
        path = destination / url.path.lstrip("/")
        if path.is_dir():
            path /= "index.html"
        if path.is_file():
            route.fulfill(content_type=mimetypes.guess_type(str(path))[0] or "text/plain", body=path.read_bytes())
        else:
            route.fulfill(status=404, body="Not found")
    page.route("**/*", respond)
    return page


@pytest.fixture()
def stacked_page(page, stacked_site):
    serve(page, stacked_site)
    page.goto(ORIGIN + "/guide/stacked-text/")
    expect(page.locator("#stacked-text-preview .stacked-text__svg")).to_be_visible()
    return page


def test_presets_and_solid_bands(stacked_page, tmp_path):
    page = stacked_page
    for name, count in [("preview", 12), ("muted", 11), ("inverted", 11)]:
        expect(page.locator(f"#stacked-text-{name} .stacked-text__band")).to_have_count(count)
    custom = page.locator("#stacked-text-custom")
    assert custom.locator(".stacked-text__band").evaluate_all("els => els.map(el => el.getAttribute('fill'))") == ["#7568ae", "#d85d79", "#e88932"]
    assert page.locator("#stacked-text-preview .stacked-text__band").first.get_attribute("fill") != page.locator("#stacked-text-muted .stacked-text__band").first.get_attribute("fill")
    for band in custom.locator(".stacked-text__band").all():
        assert band.locator("use").count() == 12
    expect(custom.locator(".stacked-text__face")).to_have_attribute("fill", "#ffcf54")
    expect(page.locator("#stacked-text-preview .stacked-text__face")).to_have_attribute("fill", "#fffbe6")
    expect(page.get_by_label("Text color", exact=True)).to_have_value("#fffbe6")
    expect(page.locator("#stacked-text-muted .stacked-text__face")).to_have_attribute("fill", "#dfcd72")
    expect(page.locator("#stacked-text-inverted .stacked-text__face")).to_have_attribute("fill", "#19c6cf")
    expect(page.locator(".brand__name svg")).to_have_count(0)
    ids = page.locator(".stacked-text defs text").evaluate_all("els => els.map(el => el.id)")
    assert len(ids) == len(set(ids)) == 4
    colors = page.locator("#stacked-text-preview .stacked-text__band").evaluate_all("els => els.map(el => el.getAttribute('fill'))")
    inverted = page.locator("#stacked-text-inverted .stacked-text__band").evaluate_all("els => els.map(el => el.getAttribute('fill'))")
    assert inverted == colors[::-1][:-1]
    page.set_viewport_size({"width": 1440, "height": 1100})
    page.screenshot(path=tmp_path / "stacked-text-desktop.png", full_page=True)


@pytest.mark.parametrize("spacing", [0, 3])
@pytest.mark.parametrize(("tilt", "angle"), [(-10, 90), (35, 0), (-30, 180), (15, 270), (-45, -135), (370, 425)])
@pytest.mark.parametrize("per_character", [False, True])
def test_all_directions_fit_the_viewbox(stacked_page, tilt, angle, spacing, per_character):
    page = stacked_page
    page.evaluate("""async options => {
      if (options.per_character) {
        options.character_styles = Array.from('Ag PIXEL', (_, index) => ({
          shadow_colors_set: index % 2 ? ['red', 'blue'] : ['gold', 'green', 'purple', 'black']
        }));
      }
      await PixelLabStackedText.render(document.querySelector('#stacked-text-preview'), options);
    }""", {"tilt_angle": tilt, "shadow_angle": angle, "shadow_thickness": 12, "shadow_spacing": spacing, "text": "Ag PIXEL", "per_character": per_character})
    fits = page.locator("#stacked-text-preview svg").evaluate("""svg => {
      const v = svg.viewBox.baseVal;
      return [...svg.querySelectorAll('.stacked-text__band use, .stacked-text__face')].every(use => {
        const b = use.getBBox(), m = use.transform.baseVal.consolidate().matrix;
        return [[b.x,b.y], [b.x+b.width,b.y], [b.x,b.y+b.height], [b.x+b.width,b.y+b.height]].every(([x,y]) => {
          const p = new DOMPoint(x,y).matrixTransform(m);
          return p.x >= v.x && p.y >= v.y && p.x <= v.x+v.width && p.y <= v.y+v.height;
        });
      });
    }""")
    assert fits


def test_shadow_direction_does_not_rotate_with_text(stacked_page):
    result = stacked_page.evaluate("""async () => {
      const el = document.querySelector('#stacked-text-preview');
      const positions = [];
      for (const tilt_angle of [-30, 0, 20]) {
        await PixelLabStackedText.render(el, {tilt_angle, shadow_angle:90, shadow_colors_set:['red','blue'], text_color:'#fffbe6'});
        const m = el.querySelector('.stacked-text__band use').transform.baseVal.consolidate().matrix;
        positions.push([m.e, m.f]);
      }
      return positions;
    }""")
    for x, y in result:
        assert x == pytest.approx(0, abs=1e-10)
        assert y == pytest.approx(12)


@pytest.mark.parametrize("text_color", [None, "#fffbe6"])
@pytest.mark.parametrize("colors_set", ["rainbow", "rainbow-inverted", "rainbow-muted", ["red", "green", "blue", "purple"], ["#123456"]])
def test_layer_count_uses_first_colors_without_cycling(stacked_page, colors_set, text_color):
    result = stacked_page.evaluate("""async ({colors_set, text_color}) => {
      const el = document.querySelector('#stacked-text-preview');
      const full = await PixelLabStackedText.render(el, {
        tilt_angle:0, shadow_angle:90, shadow_spacing:3, shadow_colors_set:colors_set, text_color
      });
      const colors = [...full.querySelectorAll('.stacked-text__band')].reverse().map(band => band.getAttribute('fill'));
      const height = full.viewBox.baseVal.height;
      const results = [];
      for (const shadow_layers of [null, ...new Set([0, Math.min(1, colors.length), Math.min(3, colors.length), colors.length])]) {
        const svg = await PixelLabStackedText.render(el, {
          tilt_angle:0, shadow_angle:90, shadow_spacing:3,
          shadow_colors_set:colors_set, shadow_layers, text_color
        });
        results.push({
          count: shadow_layers,
          colors: [...svg.querySelectorAll('.stacked-text__band')].reverse().map(band => band.getAttribute('fill')),
          height: svg.viewBox.baseVal.height,
          face: svg.querySelector('.stacked-text__face').getAttribute('fill')
        });
      }
      return {colors, height, results};
    }""", {"colors_set": colors_set, "text_color": text_color})
    palette_size = len(colors_set) if isinstance(colors_set, list) else 12
    assert len(result["colors"]) == palette_size - (text_color is None)
    for item in result["results"]:
        count = len(result["colors"]) if item["count"] is None else item["count"]
        assert item["colors"] == result["colors"][:count]
        expected_face = colors_set[0] if isinstance(colors_set, list) else {"rainbow": "#fff000", "rainbow-inverted": "#19c6cf", "rainbow-muted": "#dfcd72"}[colors_set]
        assert item["face"] == (text_color or expected_face)
        total_depth = len(result["colors"]) * 6 + (len(result["colors"]) - 1) * 3 if result["colors"] else 0
        selected_depth = count * 6 + (count - 1) * 3 if count else 0
        assert item["height"] == pytest.approx(result["height"] - total_depth + selected_depth)


@pytest.mark.parametrize("options", [
    {"tilt_angle": "10"}, {"shadow_angle": None}, {"shadow_thickness": 0},
    {"shadow_colors_set": []}, {"shadow_colors_set": ["not-a-color"]},
    {"shadow_colors_set": "unknown"}, {"shadow_colors_set": ["url(javascript:alert(1))"]},
    {"font_size": -1}, {"font_family": ""}, {"text": ""},
    {"shadow_spacing": -1}, {"shadow_spacing": "3"}, {"shadow_spacing": 33},
    {"shadow_layers": -1}, {"shadow_layers": 1.5}, {"shadow_layers": "2"},
    {"shadow_layers": 12}, {"shadow_layers": 13},
    {"shadow_colors_set": ["red"], "shadow_layers": 1},
    {"shadow_colors_set": ["red"], "shadow_layers": 2},
    {"shadow_colors_set": ["red", "blue"], "shadow_layers": 2},
    {"text_color": "not-a-color"}, {"text_color": 1}, {"text_color": ["red"]},
    {"text_color": "url(javascript:alert(1))"},
])
def test_invalid_automatic_options_keep_plain_text(stacked_page, options):
    result = stacked_page.evaluate("""async options => {
      const el = document.createElement('div');
      el.textContent = 'Readable fallback';
      el.dataset.stackedText = JSON.stringify(options);
      document.querySelector('main').append(el);
      await PixelLabStackedText.init(el);
      return {text: el.textContent, rendered: !!el.querySelector('svg')};
    }""", options)
    assert result == {"text": "Readable fallback", "rendered": False}


def test_text_is_safe_and_label_is_not_duplicated(stacked_page):
    page = stacked_page
    text = '<img src=x onerror="alert(1)"> & "TITLE"'
    page.evaluate("""async text => {
      const el = document.querySelector('#stacked-text-preview');
      await PixelLabStackedText.render(el, {text});
      await PixelLabStackedText.render(el, {shadow_colors_set:['red','blue']});
    }""", text)
    root = page.locator("#stacked-text-preview")
    expect(root.locator("img")).to_have_count(0)
    expect(root.locator("svg")).to_have_count(1)
    expect(root.locator(".stacked-text__label")).to_have_count(1)
    expect(root.locator(".stacked-text__label")).to_have_text(text)
    expect(root.locator("svg")).to_have_attribute("aria-hidden", "true")
    expect(root.locator("defs text")).to_have_text(text)
    assert root.aria_snapshot() == f"- text: {text}"


def test_newest_render_wins(stacked_page):
    result = stacked_page.evaluate("""async () => {
      const el = document.querySelector('#stacked-text-preview');
      const [old, current] = await Promise.all([
        PixelLabStackedText.render(el, {text:'OLD'}),
        PixelLabStackedText.render(el, {text:'NEW', shadow_colors_set:['red']})
      ]);
      return {superseded: old === null, text: el.querySelector('.stacked-text__label').textContent, bands: current.querySelectorAll('.stacked-text__band').length};
    }""")
    assert result == {"superseded": True, "text": "NEW", "bands": 0}


def test_spacing_changes_offsets_not_shadow_thickness(stacked_page, tmp_path):
    result = stacked_page.evaluate("""async () => {
      const el = document.querySelector('#stacked-text-preview');
      const result = [];
      for (const shadow_spacing of [0, 3]) {
        await PixelLabStackedText.render(el, {
          text:'PIXEL LAB', tilt_angle:0, shadow_angle:90, shadow_thickness:6,
          shadow_spacing, shadow_colors_set:['red','green','blue'], text_color:'#fffbe6'
        });
        result.push({
          height: el.querySelector('svg').viewBox.baseVal.height,
          offsets: [...el.querySelectorAll('.stacked-text__band')].map(band =>
            [...band.querySelectorAll('use')].map(use => use.transform.baseVal.consolidate().matrix.f)),
          masks: el.querySelectorAll('mask').length
        });
      }
      return result;
    }""")
    continuous, spaced = result
    assert spaced["height"] - continuous["height"] == pytest.approx(6)
    assert continuous["masks"] == 0
    assert spaced["masks"] == 0
    for band, continuous_band, offset in zip(spaced["offsets"], continuous["offsets"], [6, 3, 0]):
        assert len(band) == 12
        assert band == pytest.approx([position + offset for position in continuous_band])
    stacked_page.locator("#stacked-text-preview").screenshot(path=tmp_path / "spaced-shadows.png")


def test_spacing_reveals_the_colored_layer_underneath(stacked_page):
    pixel = stacked_page.evaluate("""async () => {
      const svg = await PixelLabStackedText.render(document.querySelector('#stacked-text-preview'), {
        text:'I', font_family:'Arial', tilt_angle:0, shadow_angle:90,
        shadow_thickness:8, shadow_spacing:6, shadow_colors_set:['#ff0000','#00ff00','#0000ff'], text_color:'#fffbe6'
      });
      const canvas = document.createElement('canvas');
      canvas.width = Math.ceil(svg.viewBox.baseVal.width);
      canvas.height = Math.ceil(svg.viewBox.baseVal.height);
      const ctx = canvas.getContext('2d');
      const img = new Image();
      img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(new XMLSerializer().serializeToString(svg));
      await img.decode();
      ctx.drawImage(img, 0, 0);
      ctx.font = '900 80px Arial';
      const metrics = ctx.measureText('I');
      const v = svg.viewBox.baseVal;
      // Halfway between the end of the first extrusion (8) and the next
      // layer's offset (14): the full green copy underneath must be visible.
      return [...ctx.getImageData(
        Math.round(metrics.width / 2 - v.x),
        Math.round(metrics.actualBoundingBoxDescent + 11 - v.y), 1, 1
      ).data];
    }""")
    assert pixel == [0, 255, 0, 255]


@pytest.mark.parametrize("text_color", [None, "", "   ", "#fffbe6", "  #fffbe6  ", "rebeccapurple"])
def test_text_color_fallback_reserves_first_palette_color(stacked_page, text_color):
    result = stacked_page.evaluate("""async text_color => {
      const svg = await PixelLabStackedText.render(document.querySelector('#stacked-text-preview'), {
        shadow_colors_set:['#123456', '#abcdef', '#ffaa00'], text_color
      });
      return {
        face: svg.querySelector('.stacked-text__face').getAttribute('fill'),
        shadows: [...svg.querySelectorAll('.stacked-text__band')].reverse().map(band => band.getAttribute('fill'))
      };
    }""", text_color)
    assert result["face"] == (text_color.strip() if text_color and text_color.strip() else "#123456")
    explicit = bool(text_color and text_color.strip())
    assert result["shadows"] == (["#123456", "#abcdef", "#ffaa00"] if explicit else ["#abcdef", "#ffaa00"])


@pytest.mark.parametrize("options", [{}, {"text_color": None}, {"text_color": ""}, {"text_color": "   "}])
def test_single_color_fallback_renders_only_text(stacked_page, options):
    result = stacked_page.evaluate("""async options => {
      const palette = ['#123456'];
      const svg = await PixelLabStackedText.render(document.querySelector('#stacked-text-preview'), {
        shadow_colors_set: palette, ...options
      });
      return {
        face: svg.querySelector('.stacked-text__face').getAttribute('fill'),
        shadows: svg.querySelectorAll('.stacked-text__band').length,
        palette
      };
    }""", options)
    assert result == {"face": "#123456", "shadows": 0, "palette": ["#123456"]}


def test_fallback_limits_layers_to_remaining_colors_without_mutating_palette(stacked_page):
    result = stacked_page.evaluate("""async () => {
      const palette = ['red', 'green', 'blue'];
      const svg = await PixelLabStackedText.render(document.querySelector('#stacked-text-preview'), {
        shadow_colors_set: palette, shadow_layers: 1
      });
      return {
        face: svg.querySelector('.stacked-text__face').getAttribute('fill'),
        shadows: [...svg.querySelectorAll('.stacked-text__band')].map(b => b.getAttribute('fill')),
        palette
      };
    }""")
    assert result == {"face": "red", "shadows": ["green"], "palette": ["red", "green", "blue"]}


def test_character_palettes_keep_repeated_letters_independent(stacked_page):
    result = stacked_page.evaluate("""async () => {
      const palettes = [
        ['#FFD166', '#FFBE26', '#E8A200', '#AB7800', '#765200'],
        ['#FF8B78', '#FF5134', '#F42200', '#B41900', '#7C1100'],
        ['#B9A0FF', '#8255FF', '#4E0FFF', '#3400C7', '#240089']
      ];
      const options = {
        text: 'VSS', shadow_layers: 4, tilt_angle: 0, shadow_angle: 120,
        character_styles: palettes.map(shadow_colors_set => ({shadow_colors_set}))
      };
      const before = JSON.stringify(options);
      const svg = await PixelLabStackedText.render(document.querySelector('#stacked-text-preview'), options);
      const spans = text => [...text.children].map(span => [span.textContent, span.getAttribute('fill')]);
      const ids = [...svg.querySelectorAll('[id]')].map(el => el.id);
      return {
        faces: spans(svg.querySelector('defs text:not([data-layer])')),
        shadows: [...svg.querySelectorAll('defs text[data-layer]')]
          .sort((a, b) => Number(a.dataset.layer) - Number(b.dataset.layer)).map(spans),
        unchanged: before === JSON.stringify(options),
        references: [...svg.querySelectorAll('use')].every(use => ids.includes(use.getAttribute('href').slice(1))),
        unique: new Set(ids).size === ids.length
      };
    }""")
    assert result["faces"] == [["V", "#FFD166"], ["S", "#FF8B78"], ["S", "#B9A0FF"]]
    assert result["shadows"] == [
        [["V", "#FFBE26"], ["S", "#FF5134"], ["S", "#8255FF"]],
        [["V", "#E8A200"], ["S", "#F42200"], ["S", "#4E0FFF"]],
        [["V", "#AB7800"], ["S", "#B41900"], ["S", "#3400C7"]],
        [["V", "#765200"], ["S", "#7C1100"], ["S", "#240089"]],
    ]
    assert result["unchanged"] and result["references"] and result["unique"]


@pytest.mark.parametrize("width", [240, 480, 960, 1500])
def test_character_spacing_and_bounds_stay_stable_when_resized(stacked_page, width):
    result = stacked_page.evaluate("""async width => {
      const svg = await PixelLabStackedText.render(document.querySelector('#stacked-text-preview'), {
        text: 'VLM-TASKS', font_family: 'Impact', font_size: 80, font_weight: 400,
        tilt_angle: 0, shadow_angle: 120, shadow_spacing: 3,
        text_color: 'white', shadow_colors_set: ['#444444', '#333333', '#222222', '#111111'],
        character_styles: ['gold', 'coral', 'purple', 'pink', 'cyan', 'green'].map(text_color => ({text_color}))
      });
      const glyph = svg.querySelector('defs text:not([data-layer])');
      const positions = () => [...glyph.children].flatMap(span => {
        const b = span.getBBox();
        return [b.x, b.width];
      });
      const before = positions();
      svg.style.width = width + 'px';
      svg.style.height = 'auto';
      const v = svg.viewBox.baseVal;
      const fits = [...svg.querySelectorAll('.stacked-text__band use, .stacked-text__face')].every(use => {
        const b = use.getBBox(), m = use.transform.baseVal.consolidate().matrix;
        return [[b.x,b.y], [b.x+b.width,b.y], [b.x,b.y+b.height], [b.x+b.width,b.y+b.height]].every(([x,y]) => {
          const p = new DOMPoint(x,y).matrixTransform(m);
          return p.x >= v.x && p.y >= v.y && p.x <= v.x+v.width && p.y <= v.y+v.height;
        });
      });
      return {before, after: positions(), fits};
    }""", width)
    assert result["after"] == pytest.approx(result["before"], abs=1e-4)
    assert result["fits"]


def test_character_styles_inherit_globals_and_allow_different_depths(stacked_page):
    result = stacked_page.evaluate("""async () => {
      const svg = await PixelLabStackedText.render(document.querySelector('#stacked-text-preview'), {
        text: 'ABCD', text_color: 'white', shadow_colors_set: ['red', 'green', 'blue'],
        character_styles: [null, {text_color: 'gold'}, {shadow_colors_set: ['cyan', 'navy']},
          {text_color: null, shadow_colors_set: ['pink', 'purple']}]
      });
      const fills = text => [...text.children].map(span => span.getAttribute('fill'));
      return {
        faces: fills(svg.querySelector('defs text:not([data-layer])')),
        shadows: [...svg.querySelectorAll('defs text[data-layer]')]
          .sort((a,b) => Number(a.dataset.layer) - Number(b.dataset.layer)).map(fills)
      };
    }""")
    assert result == {
        "faces": ["white", "gold", "white", "pink"],
        "shadows": [["red", "red", "cyan", "purple"], ["green", "green", "navy", "none"], ["blue", "blue", "none", "none"]],
    }


@pytest.mark.parametrize(("character_styles", "faces"), [
    ([{"text_color": "gold"}], ["gold"] * 9),
    ([{"text_color": "gold"}, {"text_color": "coral"}], ["gold", "coral"] * 4 + ["gold"]),
    ([None], ["white"] * 9),
])
def test_repeating_faces_keep_the_global_shadow_palette(stacked_page, character_styles, faces):
    result = stacked_page.evaluate("""async character_styles => {
      const svg = await PixelLabStackedText.render(document.querySelector('#stacked-text-preview'), {
        text: 'VLM-TASKS', text_color: 'white', shadow_colors_set: ['green', 'blue'], character_styles
      });
      const fills = text => [...text.children].map(span => span.getAttribute('fill'));
      return {
        faces: fills(svg.querySelector('defs text:not([data-layer])')),
        shadows: [...svg.querySelectorAll('defs text[data-layer]')]
          .sort((a,b) => Number(a.dataset.layer) - Number(b.dataset.layer)).map(fills)
      };
    }""", character_styles)
    assert result == {"faces": faces, "shadows": [["green"] * 9, ["blue"] * 9]}


@pytest.mark.parametrize("style_count", [1, 2, 3, 12])
def test_character_styles_repeat_or_truncate_without_mutating_input(stacked_page, style_count):
    result = stacked_page.evaluate("""async count => {
      const palettes = [['gold', 'orange', 'brown'], ['pink', 'purple'], ['cyan', 'navy', 'black']];
      const character_styles = Array.from({length: count}, (_, index) => ({shadow_colors_set: palettes[index % 3]}));
      const before = JSON.stringify(character_styles);
      const svg = await PixelLabStackedText.render(document.querySelector('#stacked-text-preview'), {
        text: 'VLM-TASKS', character_styles
      });
      const fills = text => [...text.children].map(span => span.getAttribute('fill'));
      return {
        faces: fills(svg.querySelector('defs text:not([data-layer])')),
        shadows: [...svg.querySelectorAll('defs text[data-layer]')]
          .sort((a,b) => Number(a.dataset.layer) - Number(b.dataset.layer)).map(fills),
        unchanged: before === JSON.stringify(character_styles)
      };
    }""", style_count)
    positions = [(index % style_count) % 3 for index in range(9)]
    assert result == {
        "faces": [["gold", "pink", "cyan"][index] for index in positions],
        "shadows": [
            [["orange", "purple", "navy"][index] for index in positions],
            [["brown", "none", "black"][index] for index in positions],
        ],
        "unchanged": True,
    }


@pytest.mark.parametrize("shadow_layers", [None, 0, 1])
def test_character_shadow_layer_limits_and_face_only_palettes(stacked_page, shadow_layers):
    result = stacked_page.evaluate("""async shadow_layers => {
      const options = {text: 'AB', character_styles: [
        {shadow_colors_set: ['red', 'green', 'blue']}, {shadow_colors_set: ['gold', 'purple']}
      ], shadow_layers};
      const svg = await PixelLabStackedText.render(document.querySelector('#stacked-text-preview'), options);
      const bands = svg.querySelectorAll('.stacked-text__band').length;
      const flat = await PixelLabStackedText.render(document.querySelector('#stacked-text-preview'), {
        text: 'AB', character_styles: [{shadow_colors_set:['red']}, {shadow_colors_set:['gold']}]
      });
      return {bands, flat: flat.querySelectorAll('.stacked-text__band').length};
    }""", shadow_layers)
    assert result == {"bands": 2 if shadow_layers is None else shadow_layers, "flat": 0}


def test_character_styles_use_visible_unicode_characters_and_keep_accessible_text(stacked_page):
    result = stacked_page.evaluate("""async () => {
      const text = 'e\u0301 👩‍💻S';
      const options = {
        text, text_color: 'white', shadow_colors_set: ['red', 'blue'],
        character_styles: [null, {text_color:'pink'}]
      };
      const el = document.createElement('div');
      el.textContent = text;
      el.dataset.stackedText = JSON.stringify(options);
      document.querySelector('main').append(el);
      await PixelLabStackedText.init(el);
      const svg = el.querySelector('svg');
      return {
        characters: [...svg.querySelectorAll('defs text:not([data-layer]) tspan')].map(span => span.textContent),
        faces: [...svg.querySelectorAll('defs text:not([data-layer]) tspan')].map(span => span.getAttribute('fill')),
        label: el.querySelector('.stacked-text__label').textContent,
        hidden: svg.getAttribute('aria-hidden'), labels: el.querySelectorAll('.stacked-text__label').length
      };
    }""")
    assert result == {"characters": ["e\u0301", " ", "👩‍💻", "S"], "faces": ["white", "pink", "white", "pink"], "label": "e\u0301 👩‍💻S", "hidden": "true", "labels": 1}


@pytest.mark.parametrize("options", [
    {"character_styles": "red"}, {"character_styles": {}}, {"character_styles": []},
    {"character_styles": [1, None]}, {"character_styles": [[], None]},
    {"character_styles": [{"unknown": "red"}, None]},
    {"character_styles": [{"text_color": "not-a-color"}, None]},
    {"character_styles": [{"shadow_colors_set": []}, None]},
    {"character_styles": [{"shadow_colors_set": ["not-a-color"]}, None]},
    {"character_styles": [{"shadow_colors_set": ["red"]}, None], "shadow_layers": 1},
])
def test_invalid_character_styles_keep_previous_render(stacked_page, options):
    result = stacked_page.evaluate("""async options => {
      const el = document.querySelector('#stacked-text-preview');
      await PixelLabStackedText.render(el, {text:'SS'});
      const before = el.innerHTML;
      let message;
      try { await PixelLabStackedText.render(el, options); }
      catch (error) { message = error.message; }
      return {message, unchanged: before === el.innerHTML};
    }""", options)
    assert "character_styles" in result["message"]
    assert result["unchanged"]


def test_exported_character_colors_render_without_javascript(stacked_page):
    result = stacked_page.evaluate("""async () => {
      const svg = await PixelLabStackedText.render(document.querySelector('#stacked-text-preview'), {
        text:'I I', font_family:'Arial', tilt_angle:0, shadow_angle:90,
        shadow_thickness:8, shadow_spacing:6, text_color:'#fffbe6',
        shadow_colors_set:['#ff0000','#00ff00','#0000ff'],
        character_styles: [null, null, {text_color:'#B9A0FF', shadow_colors_set:['#ff00ff','#00ffff','#ffaa00']}]
      });
      const canvas = document.createElement('canvas');
      canvas.width = Math.ceil(svg.viewBox.baseVal.width);
      canvas.height = Math.ceil(svg.viewBox.baseVal.height);
      const ctx = canvas.getContext('2d');
      const img = new Image();
      img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(new XMLSerializer().serializeToString(svg));
      await img.decode();
      ctx.drawImage(img, 0, 0);
      ctx.font = '900 80px Arial';
      const metrics = ctx.measureText('I');
      const v = svg.viewBox.baseVal;
      const sample = (x, y) => [...ctx.getImageData(Math.round(x-v.x), Math.round(y-v.y), 1, 1).data];
      const centers = [metrics.width/2, ctx.measureText('I ').width + metrics.width/2];
      return {
        faces: centers.map(x => sample(x, -metrics.actualBoundingBoxAscent/2)),
        shadows: centers.map(x => sample(x, metrics.actualBoundingBoxDescent+11))
      };
    }""")
    assert result == {"faces": [[255, 251, 230, 255], [185, 160, 255, 255]], "shadows": [[0, 255, 0, 255], [0, 255, 255, 255]]}


def test_character_preview_controls_and_svg_download(stacked_page, tmp_path):
    page = stacked_page
    page.locator('[name="text"]').fill("SS")
    page.get_by_label("Text color", exact=True).fill("")
    page.get_by_label("Character styles (JSON, optional)", exact=True).fill(
        '[{"shadow_colors_set":["gold","orange","brown"]},{"shadow_colors_set":["pink","purple"]}]'
    )
    page.get_by_role("button", name="Render", exact=True).click()
    expect(page.locator("#stacked-text-status")).to_have_text("Preview updated.")
    expect(page.locator("#stacked-text-preview .stacked-text__band")).to_have_count(2)
    with page.expect_download() as event:
        page.get_by_role("button", name="Download SVG").click()
    destination = tmp_path / event.value.suggested_filename
    event.value.save_as(destination)
    svg = ET.parse(destination).getroot()
    ns = {"s": "http://www.w3.org/2000/svg"}
    face = svg.find("s:defs/s:text", ns)
    assert [span.attrib["fill"] for span in face] == ["gold", "pink"]
    shadows = {text.attrib["data-layer"]: [span.attrib["fill"] for span in text]
               for text in svg.findall("s:defs/s:text[@data-layer]", ns)}
    assert shadows == {"0": ["orange", "purple"], "1": ["brown", "none"]}
    page.get_by_label("Character styles (JSON, optional)", exact=True).fill("[]")
    page.get_by_role("button", name="Render", exact=True).click()
    expect(page.locator("#stacked-text-status")).to_contain_text("nonempty array")
    expect(page.locator("#stacked-text-preview .stacked-text__band")).to_have_count(2)


def test_preview_controls_and_svg_download(stacked_page, tmp_path):
    page = stacked_page
    color = page.get_by_label("Text color", exact=True)
    expect(color).to_have_value("#fffbe6")
    page.locator('[name="text"]').fill("MY WEBSITE")
    page.locator('[name="shadow_colors_set"]').select_option("custom")
    page.locator('[name="custom_colors"]').fill('["#123456", "#abcdef"]')
    page.get_by_label("Shadow thickness", exact=True).fill("8")
    page.locator('[name="shadow_spacing"]').fill("3")
    page.get_by_role("button", name="Render", exact=True).click()
    expect(page.locator("#stacked-text-status")).to_have_text("Preview updated.")
    expect(page.locator("#stacked-text-preview .stacked-text__band")).to_have_count(2)
    expect(page.locator("#stacked-text-preview .stacked-text__face")).to_have_attribute("fill", "#fffbe6")
    with page.expect_download() as event:
        page.get_by_role("button", name="Download SVG").click()
    destination = tmp_path / event.value.suggested_filename
    event.value.save_as(destination)
    svg = ET.parse(destination).getroot()
    assert svg.attrib["role"] == "img"
    assert svg.find("{http://www.w3.org/2000/svg}title").text == "MY WEBSITE"
    assert not svg.attrib.get("style")
    assert not svg.findall(".//{http://www.w3.org/2000/svg}mask")
    assert svg.find(".//{http://www.w3.org/2000/svg}use[@class='stacked-text__face']").attrib["fill"] == "#fffbe6"
    page.locator('[name="custom_colors"]').fill("invalid json")
    page.get_by_role("button", name="Render", exact=True).click()
    expect(page.locator("#stacked-text-status")).not_to_have_text("Preview updated.")
    expect(page.locator("#stacked-text-preview .stacked-text__label")).to_have_text("MY WEBSITE")


def test_preview_inverted_colors_set_and_layer_count(stacked_page):
    page = stacked_page
    page.locator('[name="shadow_colors_set"]').select_option("rainbow-inverted")
    page.get_by_label("Shadow layers", exact=True).fill("3")
    page.get_by_role("button", name="Render", exact=True).click()
    expect(page.locator("#stacked-text-status")).to_have_text("Preview updated.")
    bands = page.locator("#stacked-text-preview .stacked-text__band")
    expect(bands).to_have_count(3)
    assert bands.evaluate_all("els => els.map(el => el.getAttribute('fill')).reverse()") == ["#19c6cf", "#009ee5", "#2519d8"]
    page.locator('[name="shadow_layers"]').fill("")
    page.get_by_role("button", name="Render", exact=True).click()
    expect(bands).to_have_count(12)
    page.locator('[name="shadow_layers"]').fill("13")
    page.get_by_role("button", name="Render", exact=True).click()
    expect(page.locator("#stacked-text-status")).to_contain_text("shadow_layers must be an integer between 0 and 12")
    expect(bands).to_have_count(12)
    page.locator('[name="shadow_layers"]').fill("")
    page.get_by_label("Text color", exact=True).fill("#fffbe6")
    page.get_by_role("button", name="Render", exact=True).click()
    expect(page.locator("#stacked-text-status")).to_have_text("Preview updated.")
    expect(bands).to_have_count(12)
    expect(page.locator("#stacked-text-preview .stacked-text__face")).to_have_attribute("fill", "#fffbe6")
    expect(bands.last).to_have_attribute("fill", "#19c6cf")
    page.get_by_label("Text color", exact=True).fill("")
    page.get_by_role("button", name="Render", exact=True).click()
    expect(page.locator("#stacked-text-preview .stacked-text__face")).to_have_attribute("fill", "#19c6cf")
    expect(bands).to_have_count(11)
    expect(bands.last).to_have_attribute("fill", "#009ee5")


@pytest.fixture(scope="session", params=[False, True, {"tilt_angle": 0, "shadow_angle": 180, "shadow_spacing": 3, "shadow_colors_set": ["#123456", "#abcdef"], "shadow_layers": 1, "text_color": "#fffbe6"}])
def header_site(request, tmp_path_factory):
    destination = tmp_path_factory.mktemp("stacked-header")
    config = load_config(config_file=str(FIXTURE), site_dir=str(destination), strict=True)
    config.site_name = "A long website title"
    config.theme["stacked_title"] = request.param
    config.extra["site_navigation"] = {"items": [{"title": "Example", "url": "/"}]}
    build(config)
    return destination, bool(request.param)


@pytest.mark.parametrize("width", [320, 390, 1440])
def test_header_opt_in_and_responsiveness(page, header_site, width):
    site, enabled = header_site
    serve(page, site)
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(ORIGIN)
    brand = page.get_by_role("link", name="A LONG WEBSITE TITLE", exact=True)
    expect(brand).to_be_visible()
    expect(brand.locator(".brand-trademark")).to_be_visible()
    expect(brand.locator(".stacked-text__svg")).to_have_count(1 if enabled else 0)
    if enabled:
        expect(brand.locator(".stacked-text__svg")).to_be_visible()
        box = brand.bounding_box()
        buttons = page.locator(".header-right").bounding_box()
        assert box["x"] + box["width"] <= buttons["x"] + 1
        svg = brand.locator(".stacked-text__svg").bounding_box()
        assert svg["height"] <= 40
        assert svg["y"] >= 0
        assert svg["y"] + svg["height"] <= 64
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")


def test_no_javascript_keeps_plain_title(browser, stacked_site):
    context = browser.new_context(java_script_enabled=False)
    try:
        page = serve(context.new_page(), stacked_site)
        page.goto(ORIGIN + "/guide/stacked-text/")
        expect(page.locator("#stacked-text-preview")).to_have_text("PIXEL LAB")
        expect(page.locator("#stacked-text-preview")).to_be_visible()
        expect(page.locator("#stacked-text-preview svg")).to_have_count(0)
    finally:
        context.close()
