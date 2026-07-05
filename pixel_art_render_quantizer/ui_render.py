try: import bpy
except ModuleNotFoundError: bpy=None

from .palettes_builtin import BUILTIN_PALETTES, builtin_default_usable_count
from .properties import default_reserved_indices
from .utils import hex_to_rgba, rgba_to_hex
from .curve_mapping_store import find_assignment_curve_owner
from .i18n import tr
from .palette_preview_icons import get_color_icon_value


def palette_display_entries(scene):
    """Return display-only entries for the selected look palette grid."""
    palette_id = scene.pixel_render_look_palette_id
    if palette_id in BUILTIN_PALETTES:
        rgba_colors = [hex_to_rgba(hex_value) for hex_value in BUILTIN_PALETTES[palette_id]]
        reserved_indices = set(default_reserved_indices(rgba_colors))
        return [
                {
                    'index': index,
                    'hex': hex_value,
                    'rgba': rgba_colors[index],
                    'reserved': index in reserved_indices,
                    'quantization_enabled': True,
                    'use_as_outline': index in reserved_indices,
                    'color_item': None,
                }
                for index, hex_value in enumerate(BUILTIN_PALETTES[palette_id])
            ]

    for palette in scene.pixel_render_palettes:
        if palette.id == palette_id:
            return [
                    {
                        'index': index,
                        'hex': rgba_to_hex(color.color),
                        'rgba': color.color[:],
                        'reserved': color.reserved,
                        'quantization_enabled': color.quantization_enabled,
                        'use_as_outline': color.use_as_outline,
                        'color_item': color,
                    }
                    for index, color in enumerate(palette.colors)
                ]

    return []



def palette_preview_data(scene):
    """Return display-only palette preview data for the selected look palette."""
    palette_id = scene.pixel_render_look_palette_id
    name = palette_id or 'None'
    if palette_id not in BUILTIN_PALETTES:
        for palette in scene.pixel_render_palettes:
            if palette.id == palette_id:
                name = palette.name
                break
    return {'name': name, 'colors': palette_display_entries(scene)}

def draw_palette_color_swatch(row, entry):
    """Draw a non-editable color chip without opening Blender's color picker."""
    try:
        row.template_node_socket(color=entry['rgba'])
    except Exception:
        pass


def draw_palette_preview(box, scene):
    preview = palette_preview_data(scene)
    colors = preview['colors']
    box.separator()
    box.label(text='Palette Preview')
    box.label(text=f"Palette: {preview['name']}")
    box.label(text=f"Colors: {len(colors)}")
    for entry in colors:
        row = box.row(align=True)
        row.label(text=f"{entry['index']:02d}")
        draw_palette_color_swatch(row, entry)
        if entry['reserved']:
            row.label(text='Reserved')
        if not entry['quantization_enabled']:
            row.label(text='Disabled')
        if entry['use_as_outline']:
            row.label(text='Outline')


def selected_palette(scene):
    palette_id = scene.pixel_render_look_palette_id
    for palette in scene.pixel_render_palettes:
        if palette.id == palette_id:
            return palette
    return None

def palette_color_limit_display(scene):
    palette_id = scene.pixel_render_look_palette_id
    if palette_id in BUILTIN_PALETTES:
        colors = [hex_to_rgba(hex_value) for hex_value in BUILTIN_PALETTES[palette_id]]
        reserved = default_reserved_indices(colors)
        return builtin_default_usable_count(palette_id, len(colors), len(reserved))
    palette = selected_palette(scene)
    return palette.usable_color_count if palette else 0


if bpy:
 class PAQ_PT_render(bpy.types.Panel):
    bl_label='Pixel Art Render Quantizer'; bl_space_type='PROPERTIES'; bl_region_type='WINDOW'; bl_context='render'
    def draw(self,context):
        s=context.scene
        l=self.layout
        status_box = l.box()
        status_box.label(
            text=tr(s, 'pixel_render_active') if s.pixel_render_active else tr(s, 'pixel_render_inactive'),
            icon='CHECKMARK' if s.pixel_render_active else 'CANCEL'
        )

        status_box.prop(s, 'pixel_render_ui_language', text=tr(s, 'ui_language'))

        if s.pixel_render_active:
            status_box.label(text=f"{tr(s, 'mode')}: {s.pixel_render_mode}")
            status_box.label(text=f"{tr(s, 'look_palette')}: {s.pixel_render_look_palette_id}")
            status_box.label(
                text=f"{tr(s, 'pixel_size')}: {s.pixel_render_width} x {s.pixel_render_height}  {tr(s, 'scale')}: x{s.pixel_render_scale}"
            )
            status_box.label(
                text=f"{tr(s, 'final_output')}: {s.pixel_render_width * int(s.pixel_render_scale)} x {s.pixel_render_height * int(s.pixel_render_scale)}"
            )

        row = l.row(align=True)
        if s.pixel_render_active:
            row.operator('paq.stop_pixel_render', text=tr(s, 'stop_pixel_render'), icon='PAUSE')
        else:
            row.operator('paq.start_pixel_render', text=tr(s, 'start_pixel_render'), icon='PLAY')

        l.prop(s,'pixel_render_mode');
        if s.pixel_render_mode=='INDIVIDUAL': l.label(text='Individual assignment data is stored, but rendering is not active in v1.0.', icon='ERROR')
        l.prop(s,'pixel_render_look_palette_id',text=tr(s, 'look_palette')); l.operator('paq.quick_render_check', text=tr(s, 'quick_render_check')); l.operator('paq.open_pixel_render_check', text=tr(s, 'open_pixel_render_check'), icon='IMAGE_DATA'); l.operator('paq.render_quantize', text=tr(s, 'render_quantize'))
        box=l.box(); box.label(text=tr(s, 'output_size')); box.prop(s,'pixel_render_resolution_preset'); box.prop(s,'pixel_render_width'); box.prop(s,'pixel_render_height'); box.prop(s,'pixel_render_scale'); box.label(text=f"{tr(s, 'final_output_size')}: {s.pixel_render_width*int(s.pixel_render_scale)} x {s.pixel_render_height*int(s.pixel_render_scale)}"); box.prop(s,'pixel_render_camera_frame_sync_mode', text=tr(s, 'camera_frame_sync'))
        box=l.box(); box.label(text=tr(s, 'advanced_look')); box.prop(s,'pixel_render_gamma'); box.prop(s,'pixel_render_alpha_mode'); box.prop(s,'pixel_render_alpha_threshold'); box.prop(s,'pixel_render_dither_mode'); box.prop(s,'pixel_render_dither_strength'); box.prop(s,'pixel_render_outline_enabled', text=tr(s, 'strict_alpha_edge_outline')); box.label(text=tr(s, 'outline_alpha_only')); box.label(text=tr(s, 'object_outline_not_implemented')); box.separator(); box.label(text=tr(s, 'palette_assignment_curve')); box.prop(s,'pixel_render_assignment_curve_enabled', text=tr(s, 'enable_assignment_curve'));
        if s.pixel_render_assignment_curve_enabled:
            box.prop(s,'pixel_render_assignment_curve_strength'); box.label(text=tr(s, 'assignment_curve_help'));
            curve_owner = find_assignment_curve_owner()
            if curve_owner is not None and hasattr(curve_owner, 'mapping') and hasattr(box, 'template_curve_mapping'):
                box.template_curve_mapping(curve_owner, 'mapping', type='NONE')
                box.operator('paq.reset_assignment_curve', text=tr(s, 'reset_curve'))
            else:
                box.label(text=tr(s, 'curve_editor_not_initialized'))
                box.label(text=tr(s, 'press_initialize_curve'))
                box.operator('paq.initialize_assignment_curve', text=tr(s, 'initialize_curve'))
        box=l.box(); box.label(text=tr(s, 'palette_manager'))
        box.label(text=tr(s, 'current_palette'))
        box.prop(s,'pixel_render_look_palette_id',text=tr(s, 'look_palette'))
        is_builtin = s.pixel_render_look_palette_id in BUILTIN_PALETTES
        palette_type = tr(s, 'built_in') if is_builtin else tr(s, 'custom_external')
        box.label(text=f"{tr(s, 'palette_type')}: {palette_type}")
        limit_row = box.row(align=True)
        limit_row.label(text=f"{tr(s, 'palette_color_limit')}: {palette_color_limit_display(s)}")
        box.label(text=tr(s, 'reserved_not_counted'))
        box.label(text=tr(s, 'disabled_not_counted'))
        if is_builtin:
            box.operator('paq.set_palette_usable_color_count', text=tr(s, 'change_limit_duplicate'))
        else:
            palette = selected_palette(s)
            if palette:
                box.prop(palette, 'usable_color_count', text=tr(s, 'palette_color_limit'))
                box.label(text=tr(s, 'no_limit'))
        box.separator()
        box.label(text=tr(s, 'palette_grid'))
        entries = palette_display_entries(s)
        box.label(text=tr(s, 'grid_help'))
        box.label(text=tr(s, 'grid_index_above_chip_help'))
        box.label(text=tr(s, 'grid_chip_help'))
        box.label(text=tr(s, 'grid_legend'))
        if entries:
            columns = 4 if len(entries) <= 4 else 8
            grid = box.grid_flow(row_major=True, columns=columns, even_columns=True, even_rows=True, align=True)
            for entry in entries:
                cell = grid.column(align=True)
                selected = entry['index'] == s.pixel_render_selected_color_index
                label = f"{entry['index']:02d}"
                if entry['reserved']:
                    label += ' R'
                if not entry['quantization_enabled']:
                    label += ' X'
                if entry['use_as_outline']:
                    label += ' O'
                if selected:
                    label = f'▶ {label}'
                cell.label(text=label)
                icon_value = get_color_icon_value(
                    s.pixel_render_look_palette_id,
                    entry['index'],
                    entry['rgba'],
                )
                op = cell.operator(
                    'paq.select_palette_grid_color',
                    text='',
                    icon_value=icon_value,
                )
                op.index = entry['index']
        else:
            box.label(text=tr(s, 'no_colors'), icon='INFO')
        box.separator()
        box.label(text=tr(s, 'selected_color_detail'))
        box.label(text=tr(s, 'edit_selected_cell'))
        box.label(text=f"{tr(s, 'selected_hex')}: {rgba_to_hex(s.pixel_render_selected_color)}")
        box.prop(s,'pixel_render_selected_color_index'); box.prop(s,'pixel_render_selected_color', text=tr(s, 'selected_color')); box.prop(s,'pixel_render_selected_color_reserved'); box.prop(s,'pixel_render_selected_color_quantization_enabled'); box.prop(s,'pixel_render_selected_color_use_as_outline')
        box.separator()
        box.label(text=tr(s, 'palette_operations'))
        box.operator('paq.extract_palette_from_render', text=tr(s, 'extract_palette_from_render')); box.operator('paq.duplicate_palette_as_custom', text=tr(s, 'duplicate_as_custom')); box.operator('paq.rename_custom_palette', text=tr(s, 'rename_custom')); box.operator('paq.load_gpl_palette', text=tr(s, 'load_gpl')); box.operator('paq.export_gpl_palette', text=tr(s, 'export_gpl')); box.operator('paq.delete_custom_palette', text=tr(s, 'delete_custom'))
        box=l.box(); box.label(text=tr(s, 'output')); box.prop(s,'pixel_render_output_path'); box.prop(s,'pixel_render_save_quantized_lowres'); box.prop(s,'pixel_render_save_upscaled'); box.prop(s,'pixel_render_save_lowres_source')
        l.label(text=tr(s, 'diagnostics_ready') if s.pixel_render_active else tr(s, 'diagnostics_inactive'))
 classes=(PAQ_PT_render,)
