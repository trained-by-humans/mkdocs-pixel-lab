document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("stacked-text-controls");
  if (!form) return;
  const preview = document.getElementById("stacked-text-preview");
  const status = document.getElementById("stacked-text-status");
  form.addEventListener("submit", async event => {
    event.preventDefault();
    try {
      const values = new FormData(form);
      await PixelLabStackedText.render(preview, {
        text: values.get("text"),
        tilt_angle: Number(values.get("tilt_angle")),
        shadow_angle: Number(values.get("shadow_angle")),
        shadow_thickness: Number(values.get("shadow_thickness")),
        shadow_spacing: Number(values.get("shadow_spacing")),
        text_color: values.get("text_color"),
        shadow_layers: values.get("shadow_layers") === "" ? null : Number(values.get("shadow_layers")),
        shadow_colors_set: values.get("shadow_colors_set") === "custom"
          ? JSON.parse(values.get("custom_colors")) : values.get("shadow_colors_set"),
      });
      status.textContent = "Preview updated.";
    } catch (error) {
      status.textContent = error.message;
    }
  });
  document.getElementById("stacked-text-download").addEventListener("click", () => {
    const svg = preview.querySelector("svg");
    if (!svg) return;
    const output = svg.cloneNode(true);
    output.removeAttribute("aria-hidden");
    output.setAttribute("role", "img");
    const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
    title.textContent = preview.querySelector(".stacked-text__label").textContent;
    output.prepend(title);
    const blob = new Blob([new XMLSerializer().serializeToString(output)], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "stacked-title.svg";
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
});
