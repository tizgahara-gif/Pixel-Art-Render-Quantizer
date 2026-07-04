# Pixel Art Render Quantizer

Blender add-on implementing a v1.0 pixel-art render post-process flow: Start Pixel Render, Quick Render Check, RGB palette quantization, reserved colors, alpha modes, Bayer 4x4 dithering, strict 1px outline cleanup, nearest upscale, and PNG output.

Install by copying `pixel_art_render_quantizer/` into Blender's add-ons directory and enabling **Pixel Art Render Quantizer**.

## Palette Manager notes

Palette Grid displays only the color index and state markers. HEX color codes are not shown inside swatch cells.

State markers are `R` for reserved colors, `X` for quantization-disabled colors, and `O` for the outline color.

Palette Color Limit / Usable Color Count sets the maximum number of colors used for quantization. Built-in palettes have palette-specific defaults, and Custom / External palettes can be changed individually.
