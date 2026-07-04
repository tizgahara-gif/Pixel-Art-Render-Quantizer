"""Built-in palettes for Pixel Art Render Quantizer."""
from __future__ import annotations

BUILTIN_PALETTES = {
    "PAQ_RetroWarm_04": ["#1B1010", "#6B2E1E", "#C06A2C", "#F2C572"],
    "PAQ_ModernCool_04": ["#0D1117", "#1F3A4A", "#4F8FA8", "#D6EEF3"],
    "PAQ_FutureColor_04": ["#120A2A", "#00D7FF", "#FF2BD6", "#E9FF5A"],
    "PAQ_RetroWarm_08": ["#140C0C", "#3A1F16", "#6B2E1E", "#9E3F25", "#C06A2C", "#D98F45", "#F2C572", "#FFF1B8"],
    "PAQ_ModernCool_08": ["#090D12", "#111A22", "#1F3A4A", "#2F5D73", "#4F8FA8", "#78BFD0", "#A8DCE5", "#E6F7FA"],
    "PAQ_FutureColor_08": ["#09031A", "#120A2A", "#2931A8", "#007CFF", "#00D7FF", "#FF2BD6", "#FF8A00", "#E9FF5A"],
    "PAQ_RetroWarm_16": ["#100909", "#24120F", "#3A1F16", "#52271A", "#6B2E1E", "#87351F", "#9E3F25", "#B7552A", "#C06A2C", "#D27B35", "#D98F45", "#E2A458", "#F2C572", "#F7D98D", "#FFF1B8", "#FFF8D8"],
    "PAQ_ModernCool_16": ["#070A0E", "#0D1117", "#111A22", "#182733", "#1F3A4A", "#294B5C", "#2F5D73", "#3D7488", "#4F8FA8", "#63A6BC", "#78BFD0", "#94D0DC", "#A8DCE5", "#C6EAF0", "#E6F7FA", "#F7FCFD"],
    "PAQ_FutureColor_16": ["#070014", "#120A2A", "#23104D", "#2931A8", "#0057D8", "#007CFF", "#00A6FF", "#00D7FF", "#00F0B5", "#7DFF6A", "#E9FF5A", "#FFB000", "#FF8A00", "#FF4A6A", "#FF2BD6", "#FFFFFF"],
    "PAQ_RetroWarm_32": ["#080505", "#100909", "#1A0D0B", "#24120F", "#2F1812", "#3A1F16", "#472319", "#52271A", "#5E2A1C", "#6B2E1E", "#79321F", "#87351F", "#943A22", "#9E3F25", "#AA4A28", "#B7552A", "#C06A2C", "#C87530", "#D27B35", "#D6843C", "#D98F45", "#DD9A4D", "#E2A458", "#E7B05F", "#F2C572", "#F5CF80", "#F7D98D", "#FAE49F", "#FFF1B8", "#FFF4C8", "#FFF8D8", "#FFFFFF"],
    "PAQ_ModernCool_32": ["#05070A", "#070A0E", "#0A0F14", "#0D1117", "#101820", "#111A22", "#14202A", "#182733", "#1B303D", "#1F3A4A", "#254454", "#294B5C", "#2B5266", "#2F5D73", "#366A7E", "#3D7488", "#457F96", "#4F8FA8", "#5B9BB3", "#63A6BC", "#6EB4C7", "#78BFD0", "#86C8D7", "#94D0DC", "#A8DCE5", "#B7E4EA", "#C6EAF0", "#D4F0F5", "#E6F7FA", "#EFFBFC", "#F7FCFD", "#FFFFFF"],
    "PAQ_FutureColor_32": ["#03000A", "#070014", "#0C0520", "#120A2A", "#1A0D3A", "#23104D", "#2A1768", "#2931A8", "#173EC2", "#0057D8", "#006BE8", "#007CFF", "#0094FF", "#00A6FF", "#00BFFF", "#00D7FF", "#00F0B5", "#34F58A", "#7DFF6A", "#B8FF58", "#E9FF5A", "#FFF06A", "#FFB000", "#FF8A00", "#FF6A3D", "#FF4A6A", "#FF2BD6", "#C927FF", "#8B5CFF", "#B9A8FF", "#E7E0FF", "#FFFFFF"],
}

BUILTIN_PALETTE_DEFAULT_USABLE_COUNTS = {
    "PAQ_RetroWarm_04": 4,
    "PAQ_ModernCool_04": 4,
    "PAQ_FutureColor_04": 4,
    "PAQ_RetroWarm_08": 8,
    "PAQ_ModernCool_08": 8,
    "PAQ_FutureColor_08": 8,
    "PAQ_RetroWarm_16": 16,
    "PAQ_ModernCool_16": 16,
    "PAQ_FutureColor_16": 16,
    "PAQ_RetroWarm_32": 32,
    "PAQ_ModernCool_32": 32,
    "PAQ_FutureColor_32": 32,
}

def builtin_default_usable_count(palette_id, color_count=None, reserved_count=0):
    """Return the default color limit for a built-in palette.

    The configured value is the user's desired upper bound. Callers that know
    the palette size can pass it in to clamp the value to a safe range.
    """
    value = int(BUILTIN_PALETTE_DEFAULT_USABLE_COUNTS.get(palette_id, 0) or 0)
    if color_count is None:
        return max(1, value) if value else 0
    if value <= 0:
        value = int(color_count) - int(reserved_count)
    return max(1, min(int(value), int(color_count)))

DEFAULT_PALETTE_ID = "PAQ_ModernCool_32"
