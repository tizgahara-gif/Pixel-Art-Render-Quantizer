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


def draw_palette_grid(layout, scene):
    entries = palette_display_entries(scene)
    layout.label(text=tr(scene, 'grid_help'))
    layout.label(text=tr(scene, 'grid_legend'))
    if not entries:
        layout.label(text=tr(scene, 'no_colors'), icon='INFO')
        return
    grid = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=True, align=True)
    for entry in entries:
        cell = grid.column(align=True)
        selected = entry['index'] == scene.pixel_render_selected_color_index
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
        op = cell.operator(
            'paq.select_palette_grid_color',
            text='',
            icon_value=get_color_icon_value(scene.pixel_render_look_palette_id, entry['index'], entry['rgba']),
        )
        op.index = entry['index']


if bpy:
 class PAQ_PT_render(bpy.types.Panel):
    bl_label='Pixel Art Render Quantizer'; bl_space_type='PROPERTIES'; bl_region_type='WINDOW'; bl_context='render'
    def draw(self,context):
        s=context.scene
        l=self.layout
        l.label(text=tr(s, 'pixel_render_active') if s.pixel_render_active else tr(s, 'pixel_render_inactive'), icon='CHECKMARK' if s.pixel_render_active else 'CANCEL')
        l.prop(s, 'pixel_render_ui_language', text=tr(s, 'ui_language'))
        row = l.row(align=True)
        if s.pixel_render_active:
            row.operator('paq.stop_pixel_render', text=tr(s, 'stop_pixel_render'), icon='PAUSE')
        else:
            row.operator('paq.start_pixel_render', text=tr(s, 'start_pixel_render'), icon='PLAY')
        l.separator()
        l.operator('paq.quick_render_check', text=tr(s, 'quick_render_check'))
        l.operator('paq.open_pixel_render_check', text=tr(s, 'open_pixel_render_check'), icon='IMAGE_DATA')
        l.operator('paq.render_quantize', text=tr(s, 'render_quantize'))
        l.separator()
        l.label(text=f"{s.pixel_render_width} x {s.pixel_render_height} / {tr(s, 'scale')} x{s.pixel_render_scale}")
        l.label(text=f"{tr(s, 'palette')}: {palette_preview_data(s)['name']}")

 class PAQ_PT_pixel_size(bpy.types.Panel):
    bl_label='Pixel Size'; bl_space_type='PROPERTIES'; bl_region_type='WINDOW'; bl_context='render'; bl_parent_id='PAQ_PT_render'
    def draw(self,context):
        s=context.scene; l=self.layout
        l.prop(s,'pixel_render_mode', text=tr(s, 'mode'))
        if s.pixel_render_mode=='INDIVIDUAL':
            l.label(text='Individual assignment data is stored, but rendering is not active in v1.0.', icon='ERROR')
        l.prop(s,'pixel_render_resolution_preset', text='Preset')
        row=l.row(align=True); row.prop(s,'pixel_render_width'); row.prop(s,'pixel_render_height')
        l.prop(s,'pixel_render_scale', text=tr(s, 'scale'))
        l.label(text=f"{tr(s, 'final_output_size')}: {s.pixel_render_width*int(s.pixel_render_scale)} x {s.pixel_render_height*int(s.pixel_render_scale)}")
        l.prop(s,'pixel_render_camera_frame_sync_mode', text=tr(s, 'camera_frame_sync'))

 class PAQ_PT_palette(bpy.types.Panel):
    bl_label='Palette'; bl_space_type='PROPERTIES'; bl_region_type='WINDOW'; bl_context='render'; bl_parent_id='PAQ_PT_render'
    def draw(self,context):
        s=context.scene; l=self.layout
        l.prop(s,'pixel_render_look_palette_id',text=tr(s, 'look_palette'))
        is_builtin = s.pixel_render_look_palette_id in BUILTIN_PALETTES
        l.label(text=f"{tr(s, 'palette_type')}: {tr(s, 'built_in') if is_builtin else tr(s, 'custom_external')}")
        if is_builtin:
            l.label(text=f"{tr(s, 'palette_color_limit')}: {palette_color_limit_display(s)}")
            l.operator('paq.set_palette_usable_color_count', text=tr(s, 'change_limit_duplicate'))
        else:
            palette = selected_palette(s)
            if palette:
                l.prop(palette, 'usable_color_count', text=tr(s, 'palette_color_limit'))
                l.label(text=tr(s, 'no_limit'))
        l.separator()
        l.label(text=tr(s, 'palette_grid'))
        draw_palette_grid(l, s)
        l.separator()
        sort_box=l.box(); sort_box.label(text=tr(s, 'sort'))
        row=sort_box.row(align=True); row.prop(s,'pixel_render_palette_sort_mode', text='')
        sort_row=sort_box.row(align=True); sort_row.enabled=not is_builtin
        sort_row.operator('paq.sort_palette_colors', text=tr(s, 'sort'), icon='SORTSIZE')
        if is_builtin:
            sort_box.label(text=tr(s, 'duplicate_to_sort'), icon='INFO')
        l.separator()
        l.label(text=tr(s, 'selected_color_detail'))
        l.label(text=f"{tr(s, 'selected_index')}: {s.pixel_render_selected_color_index:02d}")
        l.prop(s,'pixel_render_selected_color', text=tr(s, 'selected_color'))
        l.label(text=f"{tr(s, 'selected_hex')}: {rgba_to_hex(s.pixel_render_selected_color)}")
        l.prop(s,'pixel_render_selected_color_reserved')
        l.prop(s,'pixel_render_selected_color_quantization_enabled')
        l.prop(s,'pixel_render_selected_color_use_as_outline')

 class PAQ_PT_palette_extraction(bpy.types.Panel):
    bl_label='Palette Extraction'; bl_space_type='PROPERTIES'; bl_region_type='WINDOW'; bl_context='render'; bl_parent_id='PAQ_PT_render'; bl_options={'DEFAULT_CLOSED'}
    def draw(self,context):
        s=context.scene; l=self.layout
        l.label(text=tr(s, 'extract_palette_description'))
        l.label(text=tr(s, 'extract_standard_render_note'))
        l.operator('paq.extract_palette_from_render', text=tr(s, 'extract_palette_from_render'))

 class PAQ_PT_outline(bpy.types.Panel):
    bl_label='Outline'; bl_space_type='PROPERTIES'; bl_region_type='WINDOW'; bl_context='render'; bl_parent_id='PAQ_PT_render'; bl_options={'DEFAULT_CLOSED'}
    def draw(self,context):
        s=context.scene; l=self.layout
        l.prop(s,'pixel_render_outline_enabled', text=tr(s, 'enable_outline'))
        l.label(text=tr(s, 'outline_alpha_only'))
        l.label(text=tr(s, 'object_outline_not_implemented'), icon='INFO')

 class PAQ_PT_look_adjustment(bpy.types.Panel):
    bl_label='Look Adjustment'; bl_space_type='PROPERTIES'; bl_region_type='WINDOW'; bl_context='render'; bl_parent_id='PAQ_PT_render'; bl_options={'DEFAULT_CLOSED'}
    def draw(self,context):
        s=context.scene; l=self.layout
        l.prop(s,'pixel_render_gamma')
        l.prop(s,'pixel_render_alpha_mode')
        l.prop(s,'pixel_render_alpha_threshold')
        l.prop(s,'pixel_render_dither_mode')
        l.prop(s,'pixel_render_dither_strength')
        l.separator(); l.label(text=tr(s, 'palette_assignment_curve'))
        l.prop(s,'pixel_render_assignment_curve_enabled', text=tr(s, 'enable_assignment_curve'))
        if s.pixel_render_assignment_curve_enabled:
            l.prop(s,'pixel_render_assignment_curve_strength')
            l.label(text=tr(s, 'assignment_curve_help'))
            curve_owner = find_assignment_curve_owner()
            if curve_owner is not None and hasattr(curve_owner, 'mapping') and hasattr(l, 'template_curve_mapping'):
                l.template_curve_mapping(curve_owner, 'mapping', type='NONE')
                l.operator('paq.reset_assignment_curve', text=tr(s, 'reset_curve'))
            else:
                l.label(text=tr(s, 'curve_editor_not_initialized'))
                l.label(text=tr(s, 'press_initialize_curve'))
                l.operator('paq.initialize_assignment_curve', text=tr(s, 'initialize_curve'))

 class PAQ_PT_output(bpy.types.Panel):
    bl_label='Output'; bl_space_type='PROPERTIES'; bl_region_type='WINDOW'; bl_context='render'; bl_parent_id='PAQ_PT_render'; bl_options={'DEFAULT_CLOSED'}
    def draw(self,context):
        s=context.scene; l=self.layout
        l.prop(s,'pixel_render_output_path')
        l.prop(s,'pixel_render_save_quantized_lowres')
        l.prop(s,'pixel_render_save_upscaled')
        l.prop(s,'pixel_render_save_lowres_source')

 class PAQ_PT_palette_management(bpy.types.Panel):
    bl_label='Palette Management'; bl_space_type='PROPERTIES'; bl_region_type='WINDOW'; bl_context='render'; bl_parent_id='PAQ_PT_render'; bl_options={'DEFAULT_CLOSED'}
    def draw(self,context):
        s=context.scene; l=self.layout
        l.operator('paq.duplicate_palette_as_custom', text=tr(s, 'duplicate_as_custom'))
        l.operator('paq.set_palette_usable_color_count', text=tr(s, 'change_limit_duplicate'))
        l.operator('paq.rename_custom_palette', text=tr(s, 'rename_custom'))
        row=l.row(align=True); row.operator('paq.load_gpl_palette', text=tr(s, 'load_gpl')); row.operator('paq.export_gpl_palette', text=tr(s, 'export_gpl'))
        l.separator()
        l.operator('paq.delete_custom_palette', text=tr(s, 'delete_custom'), icon='ERROR')

 classes=(PAQ_PT_render,PAQ_PT_pixel_size,PAQ_PT_palette,PAQ_PT_palette_extraction,PAQ_PT_outline,PAQ_PT_look_adjustment,PAQ_PT_output,PAQ_PT_palette_management)
