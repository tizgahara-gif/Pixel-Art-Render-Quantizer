try: import bpy
except ModuleNotFoundError: bpy=None
if bpy:
 class PAQ_PT_viewport(bpy.types.Panel):
    bl_label='Pixel Render'; bl_space_type='VIEW_3D'; bl_region_type='UI'; bl_category='Pixel Render'
    @classmethod
    def poll(cls,context): return bool(context.scene.pixel_render_active)
    def draw(self,context):
        s=context.scene; l=self.layout; l.label(text='Status: Active'); l.prop(s,'pixel_render_mode',text='Mode')
        if s.pixel_render_mode=='ALL_IN_ONE':
            l.label(text='Object assignment is disabled in ALL in ONE mode.'); op=l.operator('wm.context_set_enum',text='Switch to Individual Palette Mode'); op.data_path='scene.pixel_render_mode'; op.value='INDIVIDUAL'
        else:
            l.label(text=f'Selected Objects Count: {len(context.selected_objects)}'); l.prop(s,'pixel_render_global_palette_id',text='Palette'); l.operator('paq.assign_palette_to_selected'); l.operator('paq.clear_object_palette_override'); l.operator('paq.select_objects_using_palette'); l.prop(s,'pixel_render_background_palette_id',text='Background Palette'); l.operator('paq.assign_background_collection'); l.operator('paq.clear_background_assignment')
 classes=(PAQ_PT_viewport,)
