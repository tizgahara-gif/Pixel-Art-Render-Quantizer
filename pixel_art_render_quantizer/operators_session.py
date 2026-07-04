try: import bpy
except ModuleNotFoundError: bpy=None
from .palettes_builtin import DEFAULT_PALETTE_ID
from .properties import sync_camera_frame_to_pixel_render, sync_selected_palette_color

def get_compositor_node_tree(scene):
    scene.use_nodes = True
    tree = getattr(scene, "node_tree", None)
    if tree is None:
        return None
    return tree

def tag_redraw_all_areas(context):
    screen = getattr(context, "screen", None)
    if not screen:
        return
    for area in screen.areas:
        area.tag_redraw()

if bpy:
 class PAQ_OT_start_pixel_render(bpy.types.Operator):
    bl_idname='paq.start_pixel_render'; bl_label='Start Pixel Render'; bl_options={'REGISTER','UNDO'}
    def execute(self, context):
        s=context.scene
        if not getattr(s, "pixel_render_active", False):
            s.pixel_render_active=True
        if not getattr(s, "pixel_render_mode", None):
            s.pixel_render_mode='ALL_IN_ONE'
        if not s.pixel_render_look_palette_id:
            s.pixel_render_look_palette_id=DEFAULT_PALETTE_ID
        if not s.pixel_render_global_palette_id:
            s.pixel_render_global_palette_id=DEFAULT_PALETTE_ID
        if not s.pixel_render_background_palette_id:
            s.pixel_render_background_palette_id=DEFAULT_PALETTE_ID
        if s.pixel_render_width <= 0:
            s.pixel_render_width=320
        if s.pixel_render_height <= 0:
            s.pixel_render_height=180
        if not s.pixel_render_scale:
            s.pixel_render_scale='4'
        sync_selected_palette_color(s)
        sync_camera_frame_to_pixel_render(s)
        tag_redraw_all_areas(context)
        self.report({'INFO'}, 'Pixel Render started. Camera frame synced to Pixel Render output size.')
        return {'FINISHED'}
 class PAQ_OT_stop_pixel_render(bpy.types.Operator):
    bl_idname='paq.stop_pixel_render'; bl_label='Stop Pixel Render'; bl_options={'REGISTER','UNDO'}
    def execute(self, context):
        s=context.scene; s.pixel_render_active=False
        tag_redraw_all_areas(context)
        self.report({'INFO'}, 'Pixel Render stopped.')
        return {'FINISHED'}
 class PAQ_OT_update_preview_nodes(bpy.types.Operator):
    bl_idname='paq.update_preview_nodes'; bl_label='Update Preview Nodes'; bl_options={'REGISTER','UNDO'}
    def execute(self, context):
        tree=get_compositor_node_tree(context.scene)
        if tree is None:
            self.report({'WARNING'}, 'Compositor node tree is not available in this Blender version/context.')
            return {'CANCELLED'}
        if not tree.nodes.get('PAQ Preview Note'):
            node=tree.nodes.new('NodeFrame'); node.name='PAQ Preview Note'; node.label='Pixel Render preview helper only - final quantization is add-on image processing'
        return {'FINISHED'}
 class PAQ_OT_remove_preview_nodes(bpy.types.Operator):
    bl_idname='paq.remove_preview_nodes'; bl_label='Remove Preview Nodes'; bl_options={'REGISTER','UNDO'}
    def execute(self, context):
        tree=getattr(context.scene, "node_tree", None)
        if tree is None:
            self.report({'WARNING'}, 'Compositor node tree is not available.')
            return {'CANCELLED'}
        for node in list(tree.nodes):
            if node.name.startswith('PAQ Preview'): tree.nodes.remove(node)
        return {'FINISHED'}
 classes=(PAQ_OT_start_pixel_render,PAQ_OT_stop_pixel_render,PAQ_OT_update_preview_nodes,PAQ_OT_remove_preview_nodes)
