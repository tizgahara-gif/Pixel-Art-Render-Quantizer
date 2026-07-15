"""Outline color resolution, mask dilation, and compositing."""
from __future__ import annotations
import importlib.util

from .palettes_builtin import BUILTIN_PALETTES
from .properties import default_reserved_indices
from .utils import hex_to_rgba, luminance

_HAS_NUMPY = importlib.util.find_spec("numpy") is not None


def palette_rgba_entries(scene):
    palette_id = scene.pixel_render_look_palette_id
    if palette_id in BUILTIN_PALETTES:
        return [hex_to_rgba(hex_value) for hex_value in BUILTIN_PALETTES[palette_id]]
    for palette in scene.pixel_render_palettes:
        if palette.id == palette_id:
            return [tuple(color.color) for color in palette.colors]
    return []


def clamp_outline_palette_color_index(scene, colors=None):
    colors = palette_rgba_entries(scene) if colors is None else colors
    max_index = max(0, len(colors) - 1)
    index = max(0, min(int(getattr(scene, "pixel_render_outline_palette_color_index", 0)), max_index))
    if getattr(scene, "pixel_render_outline_palette_color_index", 0) != index:
        scene.pixel_render_outline_palette_color_index = index
    return index


def resolve_reserved_darkest_color(scene):
    colors = palette_rgba_entries(scene)
    if not colors:
        return (0.0, 0.0, 0.0, 1.0)
    reserved = default_reserved_indices(colors)
    index = reserved[0] if reserved else min(range(len(colors)), key=lambda i: luminance(colors[i]))
    return tuple(colors[index])


def resolve_outline_palette_color(scene):
    colors = palette_rgba_entries(scene)
    if not colors:
        return resolve_reserved_darkest_color(scene)
    return tuple(colors[clamp_outline_palette_color_index(scene, colors)])


def resolve_outline_rgba(scene):
    mode = getattr(scene, "pixel_render_outline_color_mode", "RESERVED_DARKEST")
    if mode == "RESERVED_DARKEST":
        return resolve_reserved_darkest_color(scene)
    if mode == "PALETTE_COLOR":
        return resolve_outline_palette_color(scene)
    if mode == "CUSTOM_COLOR":
        return tuple(scene.pixel_render_outline_custom_color)
    return (0.0, 0.0, 0.0, 1.0)


def outline_mask_from_object_mask(mask, width, height, thickness):
    thickness = max(0, int(thickness))
    if thickness <= 0:
        return [False] * (int(width) * int(height))
    if _HAS_NUMPY:
        import numpy as np
        base = np.asarray(mask, dtype=bool).reshape((int(height), int(width)))
        dilated = base.copy()
        for _ in range(thickness):
            grown = dilated.copy()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    src_y0=max(0,-dy); src_y1=int(height)-max(0,dy)
                    src_x0=max(0,-dx); src_x1=int(width)-max(0,dx)
                    dst_y0=max(0,dy); dst_y1=int(height)-max(0,-dy)
                    dst_x0=max(0,dx); dst_x1=int(width)-max(0,-dx)
                    grown[dst_y0:dst_y1, dst_x0:dst_x1] |= dilated[src_y0:src_y1, src_x0:src_x1]
            dilated = grown
        return (dilated & ~base).reshape(-1).astype(bool).tolist()
    w = int(width); h = int(height)
    base = [bool(v) for v in mask]
    dilated = base[:]
    for _ in range(thickness):
        grown = dilated[:]
        for y in range(h):
            for x in range(w):
                if not dilated[y*w+x]:
                    continue
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h:
                            grown[ny*w+nx] = True
        dilated = grown
    return [d and not b for d, b in zip(dilated, base)]


def composite_outline_mask(pixels, mask, outline_color):
    out = list(pixels)
    rgba = tuple(outline_color)
    for i, enabled in enumerate(mask):
        if enabled:
            out[i] = rgba
    return out
