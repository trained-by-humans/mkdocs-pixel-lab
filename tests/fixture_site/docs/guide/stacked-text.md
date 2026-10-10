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
