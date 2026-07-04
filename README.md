# Pixel Art Render Quantizer

Pixel Art Render Quantizer is a Blender add-on for a v1.0 pixel-art render post-process workflow. It renders at a low pixel resolution, quantizes the result to a palette, applies alpha/outline options, upscales with nearest-neighbor filtering, and can save PNG outputs.

## Install

Copy `pixel_art_render_quantizer/` into Blender's add-ons directory and enable **Pixel Art Render Quantizer**.

## Basic Workflow

1. Open **Render Properties > Pixel Art Render Quantizer**.
2. Click **Start Pixel Render**.
3. Click **Quick Render Check**.
4. Check the generated `Pixel_Render_Check` image.
5. Click **Render & Quantize** to output PNG files.
6. Click **Stop Pixel Render** when you are finished.

Start Pixel Render keeps valid user settings from the previous session. It only fills missing or invalid values with defaults.

## Render Check Output

Quick Render Check does **not** directly overwrite Blender's `Render Result`.

The preview result is written to an Image named `Pixel_Render_Check`:

- If an Image Editor area is open, the add-on automatically displays `Pixel_Render_Check` there.
- If no Image Editor area is open, press **Open Pixel_Render_Check** in Render Properties or select `Pixel_Render_Check` manually from Blender's image list.

Render & Quantize writes the displayed result to `Pixel_Render_Quantized` and saves enabled PNG outputs to the configured output directory.

## Palette UI and Color Limits

The Palette Grid shows only color numbers and state symbols inside the grid cells. It does not show HEX color codes inside swatches.

State symbols:

- `R` = Reserved
- `X` = Quantization Disabled
- `O` = Outline Color

**Palette Color Limit** is the maximum number of quantization candidate colors. Reserved colors are not counted as candidates. For Custom / External palettes, colors with Quantization Disabled are also excluded from the candidate pool.

Built-in palettes are read-only. To change the color limit for a built-in palette, use **Change Limit (Duplicate as Custom)** and edit the duplicated Custom Palette.


## Extract Palette from Render

**Extract Palette from Render** creates a Custom Palette from the standard Blender render image before Pixel Render processing.

You can specify the number of colors to extract. The default is 16 colors. The supported range is 2 to 256 colors.

The extracted palette is saved as a Scene Custom Palette and is automatically selected as the Look Palette. It appears in the Palette Grid and is used by Quick Render Check. If the render has too few valid pixels or colors, the created palette may contain fewer colors than requested.

This feature does not pick colors from `Pixel_Render_Check`. It extracts representative colors from the normal Blender render result before Pixel Render / Palette Quantize is applied.

## Camera Frame Sync

Camera Frame Sync synchronizes Blender's Render Resolution to the Pixel Render settings.

Recommended setting: **Sync Final Output Size**.

When enabled, the Camera View frame matches the final Pixel Render output aspect ratio. During Quick Render Check, the add-on temporarily switches Blender's render resolution to the Pixel Render Size for the internal render, then restores the synchronized resolution after processing.

## v1.0 Limitations

- Individual Palette Mode stores palette assignments only.
- Per-object or individual rendering for Individual Palette Mode is not implemented.
- Object ID Mask is not implemented.
- Depth Outline is not implemented.
- Silhouette Outline is not implemented.
- Refraction handling is not implemented.
- Aseprite file loading is not implemented.

## Notes

The add-on intentionally avoids reading `Render Result.pixels` directly. Low-resolution renders are saved through a temporary PNG and reloaded as a normal Blender Image before quantization.
