# Stacked lettering

Retro SVG lettering with solid shadow layers. Negative text tilt raises the
right end of the baseline; shadow direction is independent: 0° right, 90° down,
180° left, 270° up. Colors run from the front face toward the farthest shadow.

## Try it

<form id="stacked-text-controls" style="display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 24px;">
  <label>Title<br><input name="text" value="PIXEL LAB" maxlength="512" required></label>
  <label>Text tilt (degrees)<br><input name="tilt_angle" type="number" value="-10" step="1" required style="width: 100px;"></label>
  <label>Shadow angle (degrees)<br><input name="shadow_angle" type="number" value="90" step="1" required style="width: 100px;"></label>
  <label>Shadow thickness<br><input name="shadow_thickness" type="number" value="6" min="0.5" max="32" step="0.5" required style="width: 100px;"></label>
  <label>Shadow spacing<br><input name="shadow_spacing" type="number" value="0" min="0" max="32" step="0.5" required style="width: 100px;"></label>
  <label>Shadow colors set<br><select name="shadow_colors_set"><option value="rainbow">Rainbow</option><option value="rainbow-inverted">Rainbow inverted</option><option value="rainbow-muted">Rainbow muted</option><option value="custom">Custom array</option></select></label>
  <label>Shadow layers<br><input name="shadow_layers" type="number" min="0" max="64" step="1" placeholder="All colors" style="width: 100px;"></label>
  <label>Text color<br><input name="text_color" value="#fffbe6" style="width: 100px;"></label>
  <label>Custom colors (JSON)<br><input name="custom_colors" value='["#ffcf54", "#e88932", "#d85d79", "#7568ae"]' style="max-width: 100%; width: 340px;"></label>
  <label>Character styles (JSON, optional)<br><textarea name="character_styles" rows="3" style="max-width: 100%; width: 440px;" placeholder='[{"text_color":"#FFD166","shadow_colors_set":["#FFBE26","#E8A200"]},null]'></textarea></label>
  <button type="submit" class="header-btn">Render</button>
  <button type="button" id="stacked-text-download" class="header-btn">Download SVG</button>
</form>
<p id="stacked-text-status" role="status" aria-live="polite"></p>
<div style="background: #101410; padding: 28px;">
  <div id="stacked-text-preview" data-stacked-text='{"text_color": "#fffbe6"}'>PIXEL LAB</div>
</div>

Shadow thickness and shadow spacing use SVG units, measured along the shadow
direction. Zero spacing keeps the continuous stack; positive spacing moves
the colored copies farther apart, revealing the underlying colored layers
where they overlap. It does not cut transparent gaps through the stack.

Text color is optional: leave it empty to use the first palette color, or enter
a CSS color to override only the lettering. This preview starts with the
original cream color `#fffbe6` filled in and applied. Clear the field to use
the first palette color for the text and start shadows from the second color.
An explicit text color leaves all palette colors available for shadows.
Leave shadow layers blank to use all available shadow colors, or enter a count
to use that many. The count excludes the text face; zero shows only the text.
There is one shadow layer per available color, with no cycling or interpolation.

Downloaded SVGs keep text editable and require the chosen font to be installed
on the viewer's machine. They are not outlined logo assets.

## Per-character faces and shadows

`character_styles` accepts a nonempty array repeated across visible characters
in text order, including spaces and punctuation. When it runs out, it starts
again at the first entry; a single entry styles every character. Extra entries
are unused. Combining marks and joined emoji count as
one character (using the browser's `Intl.Segmenter`). A `null` entry inherits
the global colors. Each object can override `text_color`, `shadow_colors_set`,
or both; omitted properties inherit the global values. The same options work
in JavaScript, `data-stacked-text` JSON, and the theme's `stacked_title` YAML.

The existing palette rule applies separately to each character: an omitted,
`null`, or blank `text_color` takes the first palette color for the face and
uses the remaining colors as shadows. An explicit `text_color` uses the
entire palette for shadows. The global `shadow_layers` count must fit every
palette; leaving it unset uses each character's full available stack. Shadow
colors never cycle between layers, and the SVG bounds fit the longest stack.

For example, `character_styles: [{text_color: "gold"}, {text_color: "coral"}]`
alternates gold and coral faces for any text length. A single
`{text_color: "gold"}` entry makes every face gold while inheriting the global
shadow palette.

This reproduces the original VLM-TASKS palettes. Each array contains a face
followed by four shadows, nearest to farthest. The two S positions are
independent:

```javascript
const palettes = [
  ["#FFD166", "#FFBE26", "#E8A200", "#AB7800", "#765200"], // Gold
  ["#FF8B78", "#FF5134", "#F42200", "#B41900", "#7C1100"], // Coral
  ["#B9A0FF", "#8255FF", "#4E0FFF", "#3400C7", "#240089"], // Purple
  ["#F78CC7", "#F944A8", "#F4088A", "#B40666", "#7C0446"], // Pink
  ["#56DDEB", "#1BD9ED", "#0FB0C1", "#0B828F", "#085A62"], // Cyan
  ["#82D696", "#4FCB6C", "#33AD50", "#25803B", "#1A5829"], // Green
];

const svg = await PixelLabStackedText.render(document.querySelector("#my-title"), {
  text: "VLM-TASKS",
  font_family: "Impact",
  font_size: 80,
  font_weight: 400,
  tilt_angle: 0,
  shadow_angle: 120,
  shadow_thickness: 6,
  shadow_spacing: 3,
  shadow_layers: 4,
  text_color: null,
  character_styles: palettes.map(shadow_colors_set => ({ shadow_colors_set }))
});

svg.style.width = "960px";
svg.style.height = "auto";
```

The six palettes repeat across nine characters, giving the final SKS the
same gold, coral, and purple palettes as VLM.

To use the preview, enter your text and a nonempty character styles JSON
array in the controls above. Clear **Text color** to let each palette supply
its own face, or set `text_color` explicitly in each character's object.
Invalid arrays leave the previous preview intact. Downloaded SVGs retain
all per-character colors and definitions without needing JavaScript.

## Rainbow muted

<div style="background: #101410; padding: 28px;">
  <div id="stacked-text-muted" data-stacked-text='{"shadow_colors_set": "rainbow-muted"}'>PIXEL LAB</div>
</div>

## Rainbow inverted

The same rainbow colors in reverse order: cyan text, yellow farthest shadow.

<div style="background: #101410; padding: 28px;">
  <div id="stacked-text-inverted" data-stacked-text='{"shadow_colors_set": "rainbow-inverted"}'>PIXEL LAB</div>
</div>

## Custom solid layers

These four colors create a text face followed by three shadow layers. Add an
explicit text color to use all four palette colors as shadows.

<div style="background: #101410; padding: 28px;">
  <div id="stacked-text-custom" data-stacked-text='{"tilt_angle": -6, "shadow_angle": 65, "shadow_colors_set": ["#ffcf54", "#e88932", "#d85d79", "#7568ae"]}'>PIXEL LAB</div>
</div>
