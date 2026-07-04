# Pixel Art Render Quantizer

Blender add-on implementing a v1.0 pixel-art render post-process flow: Start Pixel Render, Quick Render Check, RGB palette quantization, reserved colors, alpha modes, Bayer 4x4 dithering, strict 1px outline cleanup, nearest upscale, and PNG output.

Install by copying `pixel_art_render_quantizer/` into Blender's add-ons directory and enabling **Pixel Art Render Quantizer**.

## Camera Frame Sync

Camera Frame Syncを有効にすると、Pixel Renderの設定に合わせてBlender本体のRender Resolutionも更新されます。

これにより、Camera Viewのカメラ枠がPixel Renderの最終出力比率と一致します。

推奨設定は Sync Final Output Size です。

Quick Render Check内部では、従来通りPixel Render Sizeで一時レンダーし、処理後にBlender本体のRender Resolutionへ戻します。
