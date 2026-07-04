"""sRGB RGB-distance quantization and look adjustment."""
from __future__ import annotations
from .utils import hex_to_rgba

def select_usable_colors(colors, reserved_indices=(), usable_color_count=0, enabled_indices=None):
    reserved = set(reserved_indices or [])
    enabled = set(range(len(colors))) if enabled_indices is None else set(enabled_indices)
    candidates = [c for i, c in enumerate(colors) if i not in reserved and i in enabled]
    if usable_color_count and usable_color_count < len(candidates):
        if usable_color_count <= 1:
            candidates = candidates[:1]
        else:
            last = len(candidates) - 1
            candidates = [candidates[round(i * last / (usable_color_count - 1))] for i in range(usable_color_count)]
    return candidates

def apply_look(pixel, gamma=1.0, exposure=0.0, contrast=1.0, saturation=1.0):
    r, g, b, a = pixel
    rgb = [max(0, min(1, c)) for c in (r, g, b)]
    if gamma != 1.0:
        inv = 1.0 / max(gamma, 1e-6); rgb = [c ** inv for c in rgb]
    if exposure:
        f = 2 ** exposure; rgb = [max(0, min(1, c * f)) for c in rgb]
    if contrast != 1.0:
        rgb = [max(0, min(1, (c - 0.5) * contrast + 0.5)) for c in rgb]
    if saturation != 1.0:
        lum = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
        rgb = [max(0, min(1, lum + (c - lum) * saturation)) for c in rgb]
    return (*rgb, a)

def nearest_color(pixel, palette):
    r, g, b = pixel[:3]
    return min(palette, key=lambda c: (r-c[0])**2 + (g-c[1])**2 + (b-c[2])**2)

def quantize_pixels(pixels, width, height, palette_colors, reserved_indices=(), usable_color_count=0, dither_mode="NONE", dither_strength=0.0, **look):
    usable = select_usable_colors(palette_colors, reserved_indices, usable_color_count)
    if not usable:
        raise ValueError("Palette has no active quantization colors")
    out=[]
    from .dither import bayer4_offset
    for y in range(height):
        for x in range(width):
            p = apply_look(pixels[y*width+x], **look)
            if dither_mode == "BAYER4" and dither_strength:
                off = bayer4_offset(x, y) * dither_strength
                p = tuple(max(0, min(1, p[i] + off)) if i < 3 else p[i] for i in range(4))
            out.append((*nearest_color(p, usable)[:3], p[3]))
    return out
