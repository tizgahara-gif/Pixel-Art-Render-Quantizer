from __future__ import annotations
try: import bpy
except ModuleNotFoundError: bpy = None

from .outline_mask import SUPPORTED_TYPES
from .outline_processing import clamp_outline_palette_color_index, palette_rgba_entries

if bpy:
    class PAQ_OT_add_selected_outline_targets(bpy.types.Operator):
        bl_idname = 'paq.add_selected_outline_targets'; bl_label = 'Add Selected Objects'; bl_options = {'REGISTER', 'UNDO'}
        def execute(self, context):
            scene = context.scene
            registered = {item.object for item in scene.pixel_render_outline_targets if item.object is not None}
            added = unsupported = duplicate = 0
            for obj in context.selected_objects:
                if obj.type not in SUPPORTED_TYPES:
                    unsupported += 1; continue
                if obj in registered:
                    duplicate += 1; continue
                item = scene.pixel_render_outline_targets.add(); item.object = obj
                registered.add(obj); added += 1
            if added:
                scene.pixel_render_outline_target_index = len(scene.pixel_render_outline_targets) - 1
                self.report({'INFO'}, f'Added {added} outline target(s).')
                if unsupported or duplicate: self.report({'WARNING'}, f'Skipped {unsupported} unsupported and {duplicate} duplicate object(s).')
                return {'FINISHED'}
            self.report({'WARNING'}, 'No addable selected outline targets.')
            return {'CANCELLED'}

    class PAQ_OT_remove_outline_target(bpy.types.Operator):
        bl_idname = 'paq.remove_outline_target'; bl_label = 'Remove Outline Target'; bl_options = {'REGISTER', 'UNDO'}
        def execute(self, context):
            scene = context.scene; targets = scene.pixel_render_outline_targets
            if not targets: self.report({'WARNING'}, 'No outline targets to remove.'); return {'CANCELLED'}
            index = max(0, min(scene.pixel_render_outline_target_index, len(targets)-1))
            targets.remove(index); scene.pixel_render_outline_target_index = max(0, min(index, len(targets)-1))
            return {'FINISHED'}

    class PAQ_OT_clear_outline_targets(bpy.types.Operator):
        bl_idname = 'paq.clear_outline_targets'; bl_label = 'Clear Outline Targets'; bl_options = {'REGISTER', 'UNDO'}
        def invoke(self, context, event): return context.window_manager.invoke_confirm(self, event)
        def execute(self, context):
            context.scene.pixel_render_outline_targets.clear(); context.scene.pixel_render_outline_target_index = 0
            self.report({'INFO'}, 'Cleared all outline targets.')
            return {'FINISHED'}

    class PAQ_OT_remove_invalid_outline_targets(bpy.types.Operator):
        bl_idname = 'paq.remove_invalid_outline_targets'; bl_label = 'Remove Invalid Targets'; bl_options = {'REGISTER', 'UNDO'}
        def execute(self, context):
            targets = context.scene.pixel_render_outline_targets; removed = 0
            for index in range(len(targets)-1, -1, -1):
                obj = targets[index].object
                if obj is None or obj.type not in SUPPORTED_TYPES:
                    targets.remove(index); removed += 1
            context.scene.pixel_render_outline_target_index = max(0, min(context.scene.pixel_render_outline_target_index, len(targets)-1))
            self.report({'INFO'}, f'Removed {removed} invalid outline target(s).')
            return {'FINISHED'}

    class PAQ_OT_select_outline_palette_color(bpy.types.Operator):
        bl_idname = 'paq.select_outline_palette_color'; bl_label = 'Select Outline Palette Color'; bl_options = {'REGISTER', 'UNDO'}
        index: bpy.props.IntProperty(default=0, min=0)
        def execute(self, context):
            colors = palette_rgba_entries(context.scene)
            if not colors: self.report({'WARNING'}, 'Selected palette has no colors.'); return {'CANCELLED'}
            context.scene.pixel_render_outline_palette_color_index = max(0, min(self.index, len(colors)-1))
            clamp_outline_palette_color_index(context.scene, colors)
            return {'FINISHED'}

    classes=(PAQ_OT_add_selected_outline_targets, PAQ_OT_remove_outline_target, PAQ_OT_clear_outline_targets, PAQ_OT_remove_invalid_outline_targets, PAQ_OT_select_outline_palette_color)
else:
    classes=()
