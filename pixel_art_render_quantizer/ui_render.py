try: import bpy
except ModuleNotFoundError: bpy=None
if bpy:
 class PAQ_PT_render(bpy.types.Panel):
    bl_label='Pixel Art Render Quantizer'; bl_space_type='PROPERTIES'; bl_region_type='WINDOW'; bl_context='render'
    def draw(self,context):
        s=context.scene; l=self.layout; l.prop(s,'pixel_render_mode'); l.prop(s,'pixel_render_look_palette_id',text='Look Palette'); l.operator('paq.quick_render_check'); l.operator('paq.render_quantize')
        box=l.box(); box.label(text='Output Size'); box.prop(s,'pixel_render_resolution_preset'); box.prop(s,'pixel_render_width'); box.prop(s,'pixel_render_height'); box.prop(s,'pixel_render_scale'); box.label(text=f'Final Output Size: {s.pixel_render_width*int(s.pixel_render_scale)} x {s.pixel_render_height*int(s.pixel_render_scale)}'); box.prop(s,'pixel_render_sync_blender_resolution')
        box=l.box(); box.label(text='Advanced Look'); box.prop(s,'pixel_render_gamma'); box.prop(s,'pixel_render_alpha_mode'); box.prop(s,'pixel_render_alpha_threshold'); box.prop(s,'pixel_render_dither_mode'); box.prop(s,'pixel_render_dither_strength'); box.prop(s,'pixel_render_outline_enabled')
        box=l.box(); box.label(text='Palette Manager'); box.operator('paq.duplicate_palette_as_custom'); box.operator('paq.load_gpl_palette'); box.operator('paq.export_gpl_palette'); box.operator('paq.delete_custom_palette')
        box=l.box(); box.label(text='Output'); box.prop(s,'pixel_render_output_path'); box.prop(s,'pixel_render_save_quantized_lowres'); box.prop(s,'pixel_render_save_upscaled'); box.prop(s,'pixel_render_save_lowres_source')
        l.label(text='Diagnostics: Ready' if s.pixel_render_active else 'Diagnostics: Pixel Render is inactive.')
 classes=(PAQ_PT_render,)
