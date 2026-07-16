try: import bpy
except ModuleNotFoundError: bpy=None
from .i18n import tr
from .palettes_builtin import BUILTIN_PALETTES
from .properties import builtin_palette_display_name
if bpy:
 class PAQ_PT_compositor(bpy.types.Panel):
    bl_label='Pixel Render'; bl_space_type='NODE_EDITOR'; bl_region_type='UI'; bl_category='Pixel Render'
    @classmethod
    def poll(cls,context):
        space = getattr(context, "space_data", None)
        return bool(space and getattr(space, "tree_type", None) == 'CompositorNodeTree')
    def draw(self,context):
        s=context.scene
        col=self.layout.column()
        col.operator('paq.start_pixel_render', text=tr(s, 'start_pixel_render'))
        col.operator('paq.stop_pixel_render', text=tr(s, 'stop_pixel_render'))
        col.operator('paq.update_preview_nodes')
        col.operator('paq.remove_preview_nodes')
        col.label(
            text=tr(s, 'status_active') if s.pixel_render_active else tr(s, 'status_inactive'),
            icon='CHECKMARK' if s.pixel_render_active else 'CANCEL'
        )
        if s.pixel_render_active:
            col.label(text=f"{tr(s, 'mode')}: {s.pixel_render_mode}")
            palette_name = builtin_palette_display_name(s, s.pixel_render_look_palette_id) if s.pixel_render_look_palette_id in BUILTIN_PALETTES else s.pixel_render_look_palette_id
            col.label(text=f"{tr(s, 'palette')}: {palette_name}")
            col.label(text=f"{tr(s, 'pixel_size')}: {s.pixel_render_width} x {s.pixel_render_height}")
            col.label(text=f"{tr(s, 'scale')}: x{s.pixel_render_scale}")
            col.label(
                text=f"{tr(s, 'final_output')}: {s.pixel_render_width * int(s.pixel_render_scale)} x {s.pixel_render_height * int(s.pixel_render_scale)}"
            )
 classes=(PAQ_PT_compositor,)
