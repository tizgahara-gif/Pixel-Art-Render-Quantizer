try: import bpy
except ModuleNotFoundError: bpy=None
from .palettes_builtin import DEFAULT_PALETTE_ID
from .properties import sync_selected_palette_color

if bpy:
 class PAQ_OT_start_pixel_render(bpy.types.Operator):
    bl_idname='paq.start_pixel_render'; bl_label='Start Pixel Render'; bl_options={'REGISTER','UNDO'}
    def execute(self, context):
        s=context.scene; s.pixel_render_active=True; s.pixel_render_mode='ALL_IN_ONE'; s.pixel_render_look_palette_id=DEFAULT_PALETTE_ID; s.pixel_render_global_palette_id=DEFAULT_PALETTE_ID; s.pixel_render_background_palette_id=DEFAULT_PALETTE_ID
        s.pixel_render_width=320; s.pixel_render_height=180; s.pixel_render_scale='4'
        sync_selected_palette_color(s)
        bpy.ops.paq.update_preview_nodes()
        return {'FINISHED'}
 class PAQ_OT_stop_pixel_render(bpy.types.Operator):
    bl_idname='paq.stop_pixel_render'; bl_label='Stop Pixel Render'; bl_options={'REGISTER','UNDO'}
    def execute(self, context):
        s=context.scene; s.pixel_render_active=False
        return {'FINISHED'}
 class PAQ_OT_update_preview_nodes(bpy.types.Operator):
    bl_idname='paq.update_preview_nodes'; bl_label='Update Preview Nodes'; bl_options={'REGISTER','UNDO'}
    def execute(self, context):
        context.scene.use_nodes=True
        tree=context.scene.node_tree
        if tree and not tree.nodes.get('PAQ Preview Note'):
            node=tree.nodes.new('NodeFrame'); node.name='PAQ Preview Note'; node.label='Pixel Render preview helper only - final quantization is add-on image processing'
        return {'FINISHED'}
 class PAQ_OT_remove_preview_nodes(bpy.types.Operator):
    bl_idname='paq.remove_preview_nodes'; bl_label='Remove Preview Nodes'; bl_options={'REGISTER','UNDO'}
    def execute(self, context):
        tree=context.scene.node_tree
        if tree:
            for node in list(tree.nodes):
                if node.name.startswith('PAQ Preview'): tree.nodes.remove(node)
        return {'FINISHED'}
 classes=(PAQ_OT_start_pixel_render,PAQ_OT_stop_pixel_render,PAQ_OT_update_preview_nodes,PAQ_OT_remove_preview_nodes)
