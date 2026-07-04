"""Shared helpers."""
from __future__ import annotations
import re, uuid

_FORBIDDEN = re.compile(r'[/\\:*?"<>|]')

def new_id(prefix="paq"):
    return f"{prefix}_{uuid.uuid4().hex}"

def sanitize_palette_name(name: str) -> str:
    cleaned = _FORBIDDEN.sub("_", name.strip())
    return cleaned or "Custom Palette"

def hex_to_rgba(hex_color: str):
    text = hex_color.strip().lstrip("#")
    if len(text) != 6:
        raise ValueError(f"Invalid RGB hex color: {hex_color!r}")
    return tuple(int(text[i:i+2], 16) / 255.0 for i in (0, 2, 4)) + (1.0,)

def rgba_to_hex(color) -> str:
    r, g, b = [max(0, min(255, round(float(c) * 255))) for c in color[:3]]
    return f"#{r:02X}{g:02X}{b:02X}"

def luminance(color) -> float:
    r, g, b = color[:3]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b
