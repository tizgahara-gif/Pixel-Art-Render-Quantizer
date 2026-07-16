"""Built-in palettes for Pixel Art Render Quantizer."""
from __future__ import annotations

BUILTIN_PALETTES = {
    "PAQ_RetroWarm_04": ["#1B1010", "#6B2E1E", "#C06A2C", "#F2C572"],
    "PAQ_ModernCool_04": ["#0D1117", "#1F3A4A", "#4F8FA8", "#D6EEF3"],
    "PAQ_VerdantGold_04": ["#111A0B", "#3F6B24", "#A7C93A", "#F3D96B"],
    "PAQ_RetroWarm_08": ["#140C0C", "#3A1F16", "#6B2E1E", "#9E3F25", "#C06A2C", "#D98F45", "#F2C572", "#FFF1B8"],
    "PAQ_ModernCool_08": ["#090D12", "#111A22", "#1F3A4A", "#2F5D73", "#4F8FA8", "#78BFD0", "#A8DCE5", "#E6F7FA"],
    "PAQ_VerdantGold_08": ["#0B1007", "#1B2B10", "#31501D", "#4F7A27", "#78A632", "#A7C93A", "#D6D955", "#FFF0A0"],
    "PAQ_RetroWarm_16": ["#100909", "#24120F", "#3A1F16", "#52271A", "#6B2E1E", "#87351F", "#9E3F25", "#B7552A", "#C06A2C", "#D27B35", "#D98F45", "#E2A458", "#F2C572", "#F7D98D", "#FFF1B8", "#FFF8D8"],
    "PAQ_ModernCool_16": ["#070A0E", "#0D1117", "#111A22", "#182733", "#1F3A4A", "#294B5C", "#2F5D73", "#3D7488", "#4F8FA8", "#63A6BC", "#78BFD0", "#94D0DC", "#A8DCE5", "#C6EAF0", "#E6F7FA", "#F7FCFD"],
    "PAQ_VerdantGold_16": ["#070A05", "#0D1508", "#16230D", "#203513", "#2B4719", "#375A20", "#456E26", "#56832B", "#699830", "#7EAC34", "#95BF37", "#ACCF3D", "#C4DA49", "#D9DF5A", "#ECE778", "#FFF4B0"],
    "PAQ_RetroWarm_32": ["#080505", "#100909", "#1A0D0B", "#24120F", "#2F1812", "#3A1F16", "#472319", "#52271A", "#5E2A1C", "#6B2E1E", "#79321F", "#87351F", "#943A22", "#9E3F25", "#AA4A28", "#B7552A", "#C06A2C", "#C87530", "#D27B35", "#D6843C", "#D98F45", "#DD9A4D", "#E2A458", "#E7B05F", "#F2C572", "#F5CF80", "#F7D98D", "#FAE49F", "#FFF1B8", "#FFF4C8", "#FFF8D8", "#FFFFFF"],
    "PAQ_ModernCool_32": ["#05070A", "#070A0E", "#0A0F14", "#0D1117", "#101820", "#111A22", "#14202A", "#182733", "#1B303D", "#1F3A4A", "#254454", "#294B5C", "#2B5266", "#2F5D73", "#366A7E", "#3D7488", "#457F96", "#4F8FA8", "#5B9BB3", "#63A6BC", "#6EB4C7", "#78BFD0", "#86C8D7", "#94D0DC", "#A8DCE5", "#B7E4EA", "#C6EAF0", "#D4F0F5", "#E6F7FA", "#EFFBFC", "#F7FCFD", "#FFFFFF"],
    "PAQ_VerdantGold_32": ["#040603", "#070A05", "#0A1006", "#0D1508", "#111B0A", "#16230D", "#1B2B10", "#203513", "#263D16", "#2B4719", "#31501D", "#375A20", "#3E6423", "#456E26", "#4D7928", "#56832B", "#5F8E2E", "#699830", "#73A232", "#7EAC34", "#89B536", "#95BF37", "#A1C83A", "#ACCF3D", "#B8D542", "#C4DA49", "#CFDE50", "#D9DF5A", "#E3E368", "#ECE778", "#F5EC91", "#FFF4B0"],
}

BUILTIN_PALETTE_DISPLAY_NAMES = {
    "PAQ_RetroWarm_04": "Retro Warm 4",
    "PAQ_ModernCool_04": "Modern Cool 4",
    "PAQ_VerdantGold_04": "Verdant Gold 4",
    "PAQ_RetroWarm_08": "Retro Warm 8",
    "PAQ_ModernCool_08": "Modern Cool 8",
    "PAQ_VerdantGold_08": "Verdant Gold 8",
    "PAQ_RetroWarm_16": "Retro Warm 16",
    "PAQ_ModernCool_16": "Modern Cool 16",
    "PAQ_VerdantGold_16": "Verdant Gold 16",
    "PAQ_RetroWarm_32": "Retro Warm 32",
    "PAQ_ModernCool_32": "Modern Cool 32",
    "PAQ_VerdantGold_32": "Verdant Gold 32",
}

BUILTIN_PALETTE_DISPLAY_NAME_KEYS = {
    palette_id: f"palette_{palette_id}" for palette_id in BUILTIN_PALETTE_DISPLAY_NAMES
}

LEGACY_BUILTIN_PALETTE_MAP = {
    "PAQ_FutureColor_04": "PAQ_VerdantGold_04",
    "PAQ_FutureColor_08": "PAQ_VerdantGold_08",
    "PAQ_FutureColor_16": "PAQ_VerdantGold_16",
    "PAQ_FutureColor_32": "PAQ_VerdantGold_32",
}

BUILTIN_PALETTE_DEFAULT_USABLE_COUNTS = {
    "PAQ_RetroWarm_04": 4,
    "PAQ_ModernCool_04": 4,
    "PAQ_VerdantGold_04": 4,
    "PAQ_RetroWarm_08": 8,
    "PAQ_ModernCool_08": 8,
    "PAQ_VerdantGold_08": 8,
    "PAQ_RetroWarm_16": 16,
    "PAQ_ModernCool_16": 16,
    "PAQ_VerdantGold_16": 16,
    "PAQ_RetroWarm_32": 32,
    "PAQ_ModernCool_32": 32,
    "PAQ_VerdantGold_32": 32,
}

def builtin_default_usable_count(palette_id, color_count=None, reserved_count=0):
    """Return the built-in palette default quantization candidate limit.

    Reserved colors are not quantization candidates, so the configured default
    is clamped to the candidate count (palette size minus reserved colors).
    """
    value = int(BUILTIN_PALETTE_DEFAULT_USABLE_COUNTS.get(palette_id, 0) or 0)

    if color_count is None:
        return max(1, value) if value else 0

    candidate_count = max(1, int(color_count) - int(reserved_count))

    if value <= 0:
        value = candidate_count

    return max(1, min(int(value), candidate_count))

DEFAULT_PALETTE_ID = "PAQ_ModernCool_32"
