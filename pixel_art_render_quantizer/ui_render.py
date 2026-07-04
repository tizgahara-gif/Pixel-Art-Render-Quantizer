try: import bpy
except ModuleNotFoundError: bpy=None

from .palettes_builtin import BUILTIN_PALETTES
from .properties import default_reserved_indices
from .utils import hex_to_rgba, rgba_to_hex


def palette_preview_data(scene):
    """Return display-only palette preview data for the selected look palette."""
    palette_id = scene.pixel_render_look_palette_id
    if palette_id in BUILTIN_PALETTES:
        rgba_colors = [hex_to_rgba(hex_value) for hex_value in BUILTIN_PALETTES[palette_id]]
        reserved_indices = set(default_reserved_indices(rgba_colors))
        return {
            'name': palette_id,
            'colors': [
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
            ],
        }

    for palette in scene.pixel_render_palettes:
        if palette.id == palette_id:
            return {
                'name': palette.name,
                'colors': [
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
                ],
            }

    return {'name': palette_id or 'None', 'colors': []}


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
        row.label(text=entry['hex'])
        if entry['reserved']:
            row.label(text='Reserved')
        if not entry['quantization_enabled']:
            row.label(text='Disabled')
        if entry['use_as_outline']:
            row.label(text='Outline')


if bpy:
 class PAQ_PT_render(bpy.types.Panel):
    bl_label='Pixel Art Render Quantizer'; bl_space_type='PROPERTIES'; bl_region_type='WINDOW'; bl_context='render'
    def draw(self,context):
        s=context.scene
        l=self.layout; l.prop(s,'pixel_render_mode');
        if s.pixel_render_mode=='INDIVIDUAL': l.label(text='Individual assignment data is stored, but rendering is not active in v1.0.', icon='ERROR')
        l.prop(s,'pixel_render_look_palette_id',text='Look Palette'); l.operator('paq.quick_render_check'); l.operator('paq.render_quantize')
        box=l.box(); box.label(text='Output Size'); box.prop(s,'pixel_render_resolution_preset'); box.prop(s,'pixel_render_width'); box.prop(s,'pixel_render_height'); box.prop(s,'pixel_render_scale'); box.label(text=f'Final Output Size: {s.pixel_render_width*int(s.pixel_render_scale)} x {s.pixel_render_height*int(s.pixel_render_scale)}'); box.prop(s,'pixel_render_sync_blender_resolution')
        box=l.box(); box.label(text='Advanced Look'); box.prop(s,'pixel_render_gamma'); box.prop(s,'pixel_render_alpha_mode'); box.prop(s,'pixel_render_alpha_threshold'); box.prop(s,'pixel_render_dither_mode'); box.prop(s,'pixel_render_dither_strength'); box.prop(s,'pixel_render_outline_enabled', text='Strict Alpha Edge Outline'); box.label(text='v1.0 outline uses alpha edges only.'); box.label(text='Object silhouette/depth outlines are not implemented yet.')
        box=l.box(); box.label(text='Palette Manager'); box.operator('paq.duplicate_palette_as_custom'); box.operator('paq.rename_custom_palette'); box.operator('paq.load_gpl_palette'); box.operator('paq.export_gpl_palette'); box.operator('paq.delete_custom_palette')
        box.prop(s,'pixel_render_selected_color_index'); box.prop(s,'pixel_render_selected_color'); box.prop(s,'pixel_render_selected_color_reserved'); box.prop(s,'pixel_render_selected_color_quantization_enabled'); box.prop(s,'pixel_render_selected_color_use_as_outline')
        draw_palette_preview(box, s)
        box=l.box(); box.label(text='Output'); box.prop(s,'pixel_render_output_path'); box.prop(s,'pixel_render_save_quantized_lowres'); box.prop(s,'pixel_render_save_upscaled'); box.prop(s,'pixel_render_save_lowres_source')
        l.label(text='Diagnostics: Ready' if s.pixel_render_active else 'Diagnostics: Pixel Render is inactive.')
 classes=(PAQ_PT_render,)
