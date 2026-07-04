try: import bpy
except ModuleNotFoundError: bpy=None

from .palettes_builtin import BUILTIN_PALETTES, builtin_default_usable_count
from .properties import default_reserved_indices
from .utils import hex_to_rgba, rgba_to_hex


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
    """Draw a read-only color chip when Blender exposes a suitable UI helper."""
    color_item = entry.get('color_item')
    if color_item is not None:
        swatch = row.row(align=True)
        swatch.enabled = False
        swatch.prop(color_item, 'color', text='')
        return
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
            text='Pixel Render: Active' if s.pixel_render_active else 'Pixel Render: Inactive',
            icon='CHECKMARK' if s.pixel_render_active else 'CANCEL'
        )

        if s.pixel_render_active:
            status_box.label(text=f'Mode: {s.pixel_render_mode}')
            status_box.label(text=f'Look Palette: {s.pixel_render_look_palette_id}')
            status_box.label(
                text=f'Pixel Size: {s.pixel_render_width} x {s.pixel_render_height}  Scale: x{s.pixel_render_scale}'
            )
            status_box.label(
                text=f'Final Output: {s.pixel_render_width * int(s.pixel_render_scale)} x {s.pixel_render_height * int(s.pixel_render_scale)}'
            )

        row = l.row(align=True)
        if s.pixel_render_active:
            row.operator('paq.stop_pixel_render', text='Stop Pixel Render', icon='PAUSE')
        else:
            row.operator('paq.start_pixel_render', text='Start Pixel Render', icon='PLAY')

        l.prop(s,'pixel_render_mode');
        if s.pixel_render_mode=='INDIVIDUAL': l.label(text='Individual assignment data is stored, but rendering is not active in v1.0.', icon='ERROR')
        l.prop(s,'pixel_render_look_palette_id',text='Look Palette'); l.operator('paq.quick_render_check'); l.operator('paq.open_pixel_render_check', text='Open Pixel_Render_Check', icon='IMAGE_DATA'); l.operator('paq.render_quantize')
        box=l.box(); box.label(text='Output Size'); box.prop(s,'pixel_render_resolution_preset'); box.prop(s,'pixel_render_width'); box.prop(s,'pixel_render_height'); box.prop(s,'pixel_render_scale'); box.label(text=f'Final Output Size: {s.pixel_render_width*int(s.pixel_render_scale)} x {s.pixel_render_height*int(s.pixel_render_scale)}'); box.prop(s,'pixel_render_camera_frame_sync_mode', text='Camera Frame Sync')
        box=l.box(); box.label(text='Advanced Look'); box.prop(s,'pixel_render_gamma'); box.prop(s,'pixel_render_alpha_mode'); box.prop(s,'pixel_render_alpha_threshold'); box.prop(s,'pixel_render_dither_mode'); box.prop(s,'pixel_render_dither_strength'); box.prop(s,'pixel_render_outline_enabled', text='Strict Alpha Edge Outline'); box.label(text='v1.0 outline uses alpha edges only.'); box.label(text='Object silhouette/depth outlines are not implemented yet.'); box.separator(); box.label(text='Palette Assignment Curve'); box.prop(s,'pixel_render_assignment_curve_enabled', text='Enable Assignment Curve');
        if s.pixel_render_assignment_curve_enabled:
            box.prop(s,'pixel_render_assignment_curve_strength'); box.label(text='Curve Points'); box.prop(s,'pixel_render_assignment_curve_black'); box.prop(s,'pixel_render_assignment_curve_shadow'); box.prop(s,'pixel_render_assignment_curve_mid'); box.prop(s,'pixel_render_assignment_curve_light'); box.prop(s,'pixel_render_assignment_curve_white'); box.operator('paq.reset_assignment_curve', text='Reset Curve'); box.label(text='Remaps luminance before nearest palette color matching.')
        box=l.box(); box.label(text='Palette Manager')
        box.label(text='Current Palette')
        box.prop(s,'pixel_render_look_palette_id',text='Look Palette')
        is_builtin = s.pixel_render_look_palette_id in BUILTIN_PALETTES
        palette_type = 'Built-in' if is_builtin else 'Custom / External'
        box.label(text=f'Palette Type: {palette_type}')
        limit_row = box.row(align=True)
        limit_row.label(text=f'Palette Color Limit: {palette_color_limit_display(s)}')
        box.label(text='Reserved colors are not counted.')
        box.label(text='Disabled colors are not counted for custom/external palettes.')
        if is_builtin:
            box.operator('paq.set_palette_usable_color_count', text='Change Limit (Duplicate as Custom)')
        else:
            palette = selected_palette(s)
            if palette:
                box.prop(palette, 'usable_color_count', text='Palette Color Limit')
                box.label(text='0 = No limit')
        box.separator()
        box.label(text='Palette Grid')
        entries = palette_display_entries(s)
        box.label(text='Click a cell to select it. Edit its color below.')
        box.label(text='Color chip shows palette color. ▶ marks the selected cell.')
        box.label(text='R: Reserved / X: Disabled / O: Outline')
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
                chip = cell.row(align=True)
                draw_palette_color_swatch(chip, entry)
                display_label = label
                if selected:
                    display_label = f'▶ {display_label}'
                op = cell.operator('paq.select_palette_grid_color', text=display_label)
                op.index = entry['index']
        else:
            box.label(text='No colors in the selected palette.', icon='INFO')
        box.separator()
        box.label(text='Selected Color Detail')
        box.label(text='Edit the selected palette cell here.')
        box.label(text=f'Selected HEX: {rgba_to_hex(s.pixel_render_selected_color)}')
        box.prop(s,'pixel_render_selected_color_index'); box.prop(s,'pixel_render_selected_color', text='Selected Color'); box.prop(s,'pixel_render_selected_color_reserved'); box.prop(s,'pixel_render_selected_color_quantization_enabled'); box.prop(s,'pixel_render_selected_color_use_as_outline')
        box.separator()
        box.label(text='Palette Operations')
        box.operator('paq.extract_palette_from_render', text='Extract Palette from Render'); box.operator('paq.duplicate_palette_as_custom'); box.operator('paq.rename_custom_palette'); box.operator('paq.load_gpl_palette'); box.operator('paq.export_gpl_palette'); box.operator('paq.delete_custom_palette')
        box=l.box(); box.label(text='Output'); box.prop(s,'pixel_render_output_path'); box.prop(s,'pixel_render_save_quantized_lowres'); box.prop(s,'pixel_render_save_upscaled'); box.prop(s,'pixel_render_save_lowres_source')
        l.label(text='Diagnostics: Ready' if s.pixel_render_active else 'Diagnostics: Pixel Render is inactive.')
 classes=(PAQ_PT_render,)
