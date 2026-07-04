try: import bpy
except ModuleNotFoundError: bpy=None
if bpy:
 class PAQ_OT_assign_selected(bpy.types.Operator):
    bl_idname='paq.assign_palette_to_selected'; bl_label='Assign to Selected'; bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        pid=context.scene.pixel_render_global_palette_id
        for o in context.selected_objects: o.pixel_render_palette_override_enabled=True; o.pixel_render_palette_id=pid
        return {'FINISHED'}
 class PAQ_OT_clear_override(bpy.types.Operator):
    bl_idname='paq.clear_object_palette_override'; bl_label='Clear Object Override'; bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        for o in context.selected_objects: o.pixel_render_palette_override_enabled=False; o.pixel_render_palette_id=''
        return {'FINISHED'}
 class PAQ_OT_assign_bg_collection(bpy.types.Operator):
    bl_idname='paq.assign_background_collection'; bl_label='Assign Selected Collection as Background'; bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        col=context.collection; context.scene.pixel_render_background_collection_id=col.name if col else ''; return {'FINISHED'}
 class PAQ_OT_clear_bg(bpy.types.Operator):
    bl_idname='paq.clear_background_assignment'; bl_label='Clear Background Assignment'; bl_options={'REGISTER','UNDO'}
    def execute(self,context): context.scene.pixel_render_background_collection_id=''; return {'FINISHED'}
 class PAQ_OT_select_using_palette(bpy.types.Operator):
    bl_idname='paq.select_objects_using_palette'; bl_label='Select Objects Using This Palette'; bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        pid=context.scene.pixel_render_global_palette_id
        for o in context.scene.objects: o.select_set(o.pixel_render_palette_override_enabled and o.pixel_render_palette_id==pid)
        return {'FINISHED'}
 classes=(PAQ_OT_assign_selected,PAQ_OT_clear_override,PAQ_OT_assign_bg_collection,PAQ_OT_clear_bg,PAQ_OT_select_using_palette)
