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

## Palette Assignment Curve

**Palette Assignment Curve** remaps the rendered pixel luminance before nearest palette color matching. It does not edit or regenerate palette colors; it only changes which existing palette color each processed pixel is likely to be assigned to.

Enable **Palette Assignment Curve** in **Advanced Look** to adjust the five stable Value / Luminance points: **Black**, **Shadow**, **Mid**, **Light**, and **White**. Use **Curve Strength** to blend between the original luminance and the curve result, and **Reset Curve** to restore the identity curve.

Examples:

- Lowering **Shadow** makes darker regions more likely to match darker palette colors.
- Raising **Mid** makes midtones more likely to match brighter palette colors.
- Lowering **Light** helps highlights avoid jumping too quickly to near-white palette colors.

Japanese: パレット色へ割り当てる前に、明度カーブで入力色を補正します。

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
