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

**Extract Palette from Render** creates a Custom Palette from a standard Blender render before Pixel Render quantization.

This feature does not extract colors from `Pixel_Render_Check`. It renders the current scene using the current Blender render settings, saves that render internally as a temporary PNG, reads the pixels, and extracts representative colors using a Median Cut style algorithm.

The extracted palette is added as a Scene Custom Palette and automatically assigned as the current Look Palette.

You can specify the number of colors to extract.

Default: 16 colors  
Allowed range: 2 to 256 colors

If the render contains fewer usable colors than requested, the created palette may contain fewer colors than the requested Color Count.

### 日本語

**Extract Palette from Render** は、Pixel Render処理前の通常レンダー画像からCustom Paletteを作成する機能です。

`Pixel_Render_Check` から色を拾う機能ではありません。

現在のBlenderレンダー設定で通常レンダーを実行し、一時PNGとして読み込んだ画像から代表色を抽出します。

抽出色数はユーザーが指定できます。

初期値は16色です。  
指定可能範囲は2〜256色です。

レンダー画像内の有効色が少ない場合、指定した色数より少ないPaletteが作成されることがあります。

## Palette Assignment Curve

**Palette Assignment Curve** uses an interactive curve editor.
The curve remaps rendered pixel luminance before nearest palette color matching.

It does not edit palette colors.
It changes which palette color each rendered pixel is likely to match.

Enable **Palette Assignment Curve** in **Advanced Look**, then drag the curve handles to remap luminance before palette matching. Use **Curve Strength** to blend between the original luminance and the curve result, and **Reset Curve** to restore the identity curve. The legacy **Black**, **Shadow**, **Mid**, **Light**, and **White** values remain available internally for older files and numeric fallback.

Palette Assignment Curveは、ハンドル操作できるカーブエディタで調整します。

このカーブはパレット色そのものを変更するものではありません。
レンダー画像の各ピクセルが、どのパレット色へ割り当てられるかを調整します。

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

## UI Language

The add-on UI can be switched between English and Japanese from the Render Properties panel.

This language setting affects the add-on panels and button labels.  
Some Blender internal labels and technical report messages may remain in English.

## 表示言語

Render Propertiesパネルから、アドオンUIの表示言語をEnglish / 日本語で切り替えられます。

この設定は、アドオンのパネル表示やボタン文言に適用されます。  
Blender内部の表示や一部の技術的な通知メッセージは英語のまま残る場合があります。
