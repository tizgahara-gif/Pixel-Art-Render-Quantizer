try: import bpy
except ModuleNotFoundError: bpy=None
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
        col.operator('paq.start_pixel_render')
        col.operator('paq.stop_pixel_render')
        col.operator('paq.update_preview_nodes')
        col.operator('paq.remove_preview_nodes')
        col.label(
            text='Status: Active' if s.pixel_render_active else 'Status: Inactive',
            icon='CHECKMARK' if s.pixel_render_active else 'CANCEL'
        )
        if s.pixel_render_active:
            col.label(text=f'Mode: {s.pixel_render_mode}')
            col.label(text=f'Palette: {s.pixel_render_look_palette_id}')
            col.label(text=f'Pixel Size: {s.pixel_render_width} x {s.pixel_render_height}')
            col.label(text=f'Scale: x{s.pixel_render_scale}')
            col.label(
                text=f'Final Output: {s.pixel_render_width * int(s.pixel_render_scale)} x {s.pixel_render_height * int(s.pixel_render_scale)}'
            )
 classes=(PAQ_PT_compositor,)
