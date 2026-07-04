try: import bpy
except ModuleNotFoundError: bpy=None
from .palettes_builtin import BUILTIN_PALETTES
from .utils import hex_to_rgba, luminance
from .properties import default_reserved_indices
from .quantize import quantize_pixels
from .alpha import apply_alpha
from .outline import apply_outline
from .render_pipeline import render_lowres_to_pixels, upscale_nearest
from .image_output import pixels_to_image, show_image_in_editors

def palette_for_scene(scene, palette_id):
    if palette_id in BUILTIN_PALETTES:
        colors=[hex_to_rgba(h) for h in BUILTIN_PALETTES[palette_id]]; reserved=default_reserved_indices(colors); return colors, reserved, max(1,len(colors)-len(reserved)), list(range(len(colors)))
    for p in scene.pixel_render_palettes:
        if p.id==palette_id:
            return [c.color[:] for c in p.colors], [i for i,c in enumerate(p.colors) if c.reserved], p.usable_color_count, [i for i,c in enumerate(p.colors) if c.quantization_enabled]
    raise ValueError('No valid palette selected')

def individual_mode_error(scene):
    if getattr(scene, 'pixel_render_mode', 'ALL_IN_ONE') == 'INDIVIDUAL':
        return 'Individual Palette Mode rendering is not implemented in v1.0. Switch to ALL in ONE for render output.'
    return None

def count_unique_rgb(pixels):
    return len({(round(p[0],6),round(p[1],6),round(p[2],6)) for p in pixels})

def process_pixels(scene, pixels, w, h):
    colors,reserved,usable,enabled=palette_for_scene(scene, scene.pixel_render_look_palette_id)
    q=quantize_pixels(pixels,w,h,colors,reserved,usable,scene.pixel_render_dither_mode,scene.pixel_render_dither_strength,enabled_indices=enabled,gamma=scene.pixel_render_gamma,exposure=scene.pixel_render_exposure,contrast=scene.pixel_render_contrast,saturation=scene.pixel_render_saturation)
    q=apply_alpha(q,w,h,scene.pixel_render_alpha_mode,scene.pixel_render_alpha_threshold)
    if scene.pixel_render_outline_enabled:
        oi=reserved[0] if reserved else min(range(len(colors)), key=lambda i:luminance(colors[i])); q=apply_outline(q,w,h,colors[oi])
    return q
if bpy:
 class _RenderBase:
    def _run(self,context,save=False):
        s=context.scene
        if not s.pixel_render_active: self.report({'ERROR'},'Pixel Render is inactive'); return {'CANCELLED'}
        mode_error=individual_mode_error(s)
        if mode_error: self.report({'ERROR'},mode_error); return {'CANCELLED'}
        if save and not s.pixel_render_output_path: self.report({'ERROR'},'Output path is not set'); return {'CANCELLED'}
        requested_w,requested_h=s.pixel_render_width,s.pixel_render_height
        try:
            pixels,actual_w,actual_h=render_lowres_to_pixels(s,requested_w,requested_h)
        except Exception as exc:
            self.report({'ERROR'},f'Low-resolution render failed: {exc}')
            return {'CANCELLED'}
        if (actual_w,actual_h) != (requested_w,requested_h):
            self.report({'WARNING'},f'Rendered size differs from Pixel Render Size: requested={requested_w}x{requested_h}, actual={actual_w}x{actual_h}. Using actual size.')
        try:
            low=process_pixels(s,pixels,actual_w,actual_h)
        except ValueError as exc:
            self.report({'ERROR'},str(exc))
            return {'CANCELLED'}
        unique_count=count_unique_rgb(low)
        self.report({'INFO'},f'Palette applied: {s.pixel_render_look_palette_id}, unique RGB colors={unique_count}')
        up,uw,uh=upscale_nearest(low,actual_w,actual_h,int(s.pixel_render_scale))
        out=pixels_to_image('Pixel_Render_Check' if not save else 'Pixel_Render_Quantized',up,uw,uh); show_image_in_editors(out,context)
        if save:
            import os
            base=bpy.path.abspath(s.pixel_render_output_path); os.makedirs(base,exist_ok=True)
            if s.pixel_render_save_upscaled: out.filepath_raw=os.path.join(base,'pixel_render_upscaled.png'); out.file_format='PNG'; out.save()
            if s.pixel_render_save_quantized_lowres:
                lowimg=pixels_to_image('Pixel_Render_Lowres_Quantized',low,actual_w,actual_h); lowimg.filepath_raw=os.path.join(base,'pixel_render_lowres_quantized.png'); lowimg.file_format='PNG'; lowimg.save()
        return {'FINISHED'}
 class PAQ_OT_quick_render_check(bpy.types.Operator,_RenderBase):
    bl_idname='paq.quick_render_check'; bl_label='Quick Render Check'; bl_options={'REGISTER'}
    def execute(self,context): return self._run(context,False)
 class PAQ_OT_render_quantize(bpy.types.Operator,_RenderBase):
    bl_idname='paq.render_quantize'; bl_label='Render & Quantize'; bl_options={'REGISTER'}
    def execute(self,context): return self._run(context,True)
 classes=(PAQ_OT_quick_render_check,PAQ_OT_render_quantize)
