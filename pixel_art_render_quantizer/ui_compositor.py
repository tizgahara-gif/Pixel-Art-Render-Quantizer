try: import bpy
except ModuleNotFoundError: bpy=None
if bpy:
 class PAQ_PT_compositor(bpy.types.Panel):
    bl_label='Pixel Render'; bl_space_type='NODE_EDITOR'; bl_region_type='UI'; bl_category='Pixel Render'
    @classmethod
    def poll(cls,context): return context.space_data.tree_type == 'CompositorNodeTree'
    def draw(self,context):
        s=context.scene; col=self.layout.column(); col.operator('paq.start_pixel_render'); col.operator('paq.stop_pixel_render'); col.operator('paq.update_preview_nodes'); col.operator('paq.remove_preview_nodes'); col.label(text='Status: Active' if s.pixel_render_active else 'Status: Inactive')
 classes=(PAQ_PT_compositor,)
