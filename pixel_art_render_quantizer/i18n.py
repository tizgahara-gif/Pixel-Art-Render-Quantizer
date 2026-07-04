"""Add-on-local UI translation helpers."""
from __future__ import annotations

LANGUAGE_ITEMS = [
    ("EN", "English", "Display add-on UI in English"),
    ("JA", "日本語", "アドオンUIを日本語で表示します"),
]

_TRANSLATIONS = {
    "pixel_render_title": {"EN": "Pixel Art Render Quantizer", "JA": "ピクセルアート・レンダー量子化"},
    "ui_language": {"EN": "UI Language", "JA": "表示言語"},
    "pixel_render_active": {"EN": "Pixel Render: Active", "JA": "Pixel Render: 有効"},
    "pixel_render_inactive": {"EN": "Pixel Render: Inactive", "JA": "Pixel Render: 無効"},
    "status_active": {"EN": "Status: Active", "JA": "状態: 有効"},
    "status_inactive": {"EN": "Status: Inactive", "JA": "状態: 無効"},
    "start_pixel_render": {"EN": "Start Pixel Render", "JA": "Pixel Renderを開始"},
    "stop_pixel_render": {"EN": "Stop Pixel Render", "JA": "Pixel Renderを停止"},
    "quick_render_check": {"EN": "Quick Render Check", "JA": "クイックレンダー確認"},
    "open_pixel_render_check": {"EN": "Open Pixel_Render_Check", "JA": "Pixel_Render_Checkを開く"},
    "render_quantize": {"EN": "Render & Quantize", "JA": "レンダーして量子化"},
    "mode": {"EN": "Mode", "JA": "モード"},
    "palette": {"EN": "Palette", "JA": "パレット"},
    "pixel_size": {"EN": "Pixel Size", "JA": "ピクセルサイズ"},
    "scale": {"EN": "Scale", "JA": "倍率"},
    "final_output": {"EN": "Final Output", "JA": "最終出力"},
    "output_size": {"EN": "Output Size", "JA": "出力サイズ"},
    "final_output_size": {"EN": "Final Output Size", "JA": "最終出力サイズ"},
    "camera_frame_sync": {"EN": "Camera Frame Sync", "JA": "カメラ枠同期"},
    "advanced_look": {"EN": "Advanced Look", "JA": "詳細ルック調整"},
    "strict_alpha_edge_outline": {"EN": "Strict Alpha Edge Outline", "JA": "厳密アルファ境界アウトライン"},
    "outline_alpha_only": {"EN": "v1.0 outline uses alpha edges only.", "JA": "v1.0のアウトラインはアルファ境界のみを使用します。"},
    "object_outline_not_implemented": {"EN": "Object silhouette/depth outlines are not implemented yet.", "JA": "オブジェクトシルエット/深度アウトラインは未実装です。"},
    "palette_assignment_curve": {"EN": "Palette Assignment Curve", "JA": "パレット割り当てカーブ"},
    "enable_assignment_curve": {"EN": "Enable Assignment Curve", "JA": "割り当てカーブを有効化"},
    "reset_curve": {"EN": "Reset Curve", "JA": "カーブをリセット"},
    "assignment_curve_help": {"EN": "Remaps luminance before nearest palette color matching.", "JA": "最近傍パレット色へ割り当てる前に明度を再マップします。"},
    "palette_manager": {"EN": "Palette Manager", "JA": "パレット管理"},
    "current_palette": {"EN": "Current Palette", "JA": "現在のパレット"},
    "look_palette": {"EN": "Look Palette", "JA": "ルックパレット"},
    "palette_type": {"EN": "Palette Type", "JA": "パレット種別"},
    "built_in": {"EN": "Built-in", "JA": "内蔵"},
    "custom_external": {"EN": "Custom / External", "JA": "カスタム / 外部"},
    "palette_color_limit": {"EN": "Palette Color Limit", "JA": "パレット使用色数上限"},
    "reserved_not_counted": {"EN": "Reserved colors are not counted.", "JA": "Reserved色は候補数に含まれません。"},
    "disabled_not_counted": {"EN": "Disabled colors are not counted for custom/external palettes.", "JA": "カスタム/外部パレットではDisabled色も候補数に含まれません。"},
    "change_limit_duplicate": {"EN": "Change Limit (Duplicate as Custom)", "JA": "上限変更（カスタムとして複製）"},
    "no_limit": {"EN": "0 = No limit", "JA": "0 = 制限なし"},
    "palette_grid": {"EN": "Palette Grid", "JA": "パレットグリッド"},
    "grid_help": {"EN": "Click a color chip to select it. Edit the selected color below.", "JA": "色チップをクリックして選択し、下部で選択色を編集します。"},
    "grid_chip_help": {"EN": "The chip color is the actual palette color. ▶ marks the selected cell.", "JA": "色チップの色が実際のパレット色です。▶ が選択中セルです。"},
    "grid_legend": {"EN": "R: Reserved / X: Disabled / O: Outline", "JA": "R: 予約色 / X: 無効 / O: アウトライン"},
    "no_colors": {"EN": "No colors in the selected palette.", "JA": "選択中のパレットに色がありません。"},
    "selected_color_detail": {"EN": "Selected Color Detail", "JA": "選択色の詳細"},
    "edit_selected_cell": {"EN": "Edit the selected palette cell here.", "JA": "選択中のパレットセルをここで編集します。"},
    "selected_hex": {"EN": "Selected HEX", "JA": "選択色HEX"},
    "selected_color": {"EN": "Selected Color", "JA": "選択色"},
    "palette_operations": {"EN": "Palette Operations", "JA": "パレット操作"},
    "extract_palette_from_render": {"EN": "Extract Palette from Render", "JA": "レンダー結果からパレット抽出"},
    "duplicate_as_custom": {"EN": "Duplicate as Custom", "JA": "カスタムとして複製"},
    "rename_custom": {"EN": "Rename Custom", "JA": "カスタム名を変更"},
    "load_gpl": {"EN": "Load .gpl", "JA": ".gplを読み込み"},
    "export_gpl": {"EN": "Export .gpl", "JA": ".gplを書き出し"},
    "delete_custom": {"EN": "Delete Custom", "JA": "カスタムを削除"},
    "output": {"EN": "Output", "JA": "出力"},
    "diagnostics_ready": {"EN": "Diagnostics: Ready", "JA": "診断: 準備完了"},
    "diagnostics_inactive": {"EN": "Diagnostics: Pixel Render is inactive.", "JA": "診断: Pixel Renderは無効です。"},
    "background_palette": {"EN": "Background Palette", "JA": "背景パレット"},
}


def tr(scene_or_language, key: str) -> str:
    """Translate a UI key using a Scene or language code."""
    if isinstance(scene_or_language, str):
        language = scene_or_language
    else:
        language = getattr(scene_or_language, "pixel_render_ui_language", "EN")
    table = _TRANSLATIONS.get(key)
    if not table:
        return key
    return table.get(language) or table.get("EN") or key
