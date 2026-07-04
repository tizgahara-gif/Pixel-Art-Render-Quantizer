"""Preview icons for Palette Grid color chips."""
from __future__ import annotations

import os
import struct
import tempfile
import zlib

try: import bpy
except ModuleNotFoundError: bpy=None

_preview_collection = None
_temp_icon_paths = []


def ensure_preview_collection():
    """Return the add-on preview collection used for solid-color chips."""
    global _preview_collection
    if _preview_collection is None:
        import bpy.utils.previews
        _preview_collection = bpy.utils.previews.new()
    return _preview_collection


def _safe_key_part(value):
    return ''.join(ch if ch.isalnum() or ch in '_-' else '_' for ch in str(value))


def color_icon_key(palette_id, index, rgba):
    """Build a stable icon key that changes whenever the displayed color changes."""
    r = round(float(rgba[0]), 4)
    g = round(float(rgba[1]), 4)
    b = round(float(rgba[2]), 4)
    a = round(float(rgba[3]), 4) if len(rgba) > 3 else 1.0
    return f"paq_color_{_safe_key_part(palette_id)}_{index}_{r}_{g}_{b}_{a}"


def _png_chunk(chunk_type, data):
    return (
        struct.pack('>I', len(data))
        + chunk_type
        + data
        + struct.pack('>I', zlib.crc32(chunk_type + data) & 0xffffffff)
    )


def _write_solid_png(path, rgba, size=24):
    channels = [max(0, min(255, round(float(component) * 255))) for component in rgba[:4]]
    while len(channels) < 4:
        channels.append(255)
    pixel = bytes(channels)
    raw = b''.join(b'\x00' + pixel * size for _ in range(size))
    data = b'\x89PNG\r\n\x1a\n'
    data += _png_chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0))
    data += _png_chunk(b'IDAT', zlib.compress(raw))
    data += _png_chunk(b'IEND', b'')
    with open(path, 'wb') as png_file:
        png_file.write(data)


def get_color_icon_value(palette_id, index, rgba):
    """Return a Blender preview icon id for a solid chip of the given color."""
    if bpy is None:
        return 0
    pcoll = ensure_preview_collection()
    key = color_icon_key(palette_id, index, rgba)
    if key in pcoll:
        return pcoll[key].icon_id

    fd, path = tempfile.mkstemp(prefix=f'{key}_', suffix='.png')
    os.close(fd)
    _write_solid_png(path, rgba)
    _temp_icon_paths.append(path)
    preview = pcoll.load(key, path, 'IMAGE')
    return preview.icon_id


def unregister():
    """Release preview icons and remove temporary chip images."""
    global _preview_collection
    if _preview_collection is not None:
        import bpy.utils.previews
        bpy.utils.previews.remove(_preview_collection)
        _preview_collection = None
    while _temp_icon_paths:
        path = _temp_icon_paths.pop()
        try:
            os.remove(path)
        except OSError:
            pass
