try: import bpy
except ModuleNotFoundError: bpy=None
try:
    from bpy_extras.io_utils import ImportHelper, ExportHelper
except ModuleNotFoundError:
    ImportHelper = ExportHelper = object
import os
from .palettes_builtin import BUILTIN_PALETTES
from .properties import default_reserved_indices
from .utils import hex_to_rgba, new_id, sanitize_palette_name
from .palette_io_gpl import parse_gpl, write_gpl

def _unique_palette_name(scene, base, exclude=None):
    base=sanitize_palette_name(base) or 'Palette_Custom'
    names={p.name for p in scene.pixel_render_palettes if p is not exclude}
    name=base; n=1
    while name in names:
        name=f'{base}_{n:03d}'; n+=1
    return name

def _palette_colors(scene, palette_id):
    if palette_id in BUILTIN_PALETTES:
        return [hex_to_rgba(h) for h in BUILTIN_PALETTES[palette_id]], palette_id
    for p in scene.pixel_render_palettes:
        if p.id==palette_id:
            return [c.color[:] for c in p.colors], p.name
    raise ValueError('Select a valid palette')

def create_custom_from_palette(scene, palette_id):
    colors, source_name = _palette_colors(scene, palette_id)
    pal=scene.pixel_render_palettes.add(); pal.id=new_id('palette'); pal.type='CUSTOM_SCENE'; pal.source_builtin_id=palette_id if palette_id in BUILTIN_PALETTES else ''
    pal.name=_unique_palette_name(scene, f'{source_name}_Custom', exclude=pal)
    reserved=default_reserved_indices(colors)
    for i,c in enumerate(colors):
        pc=pal.colors.add(); pc.color=c; pc.reserved=i in reserved; pc.quantization_enabled=True
    pal.usable_color_count=max(1,len(colors)-len(reserved)); pal.outline_index=reserved[0] if reserved else 0
    return pal

def create_custom_from_builtin(scene, builtin_id):
    return create_custom_from_palette(scene, builtin_id)

def load_gpl_into_scene(scene, filepath):
    if not filepath:
        raise ValueError('GPL filepath is empty')
    if not os.path.exists(filepath):
        raise FileNotFoundError(filepath)
    colors=parse_gpl(open(filepath,encoding='utf-8').read())
    pal=scene.pixel_render_palettes.add(); pal.id=new_id('palette'); pal.type='EXTERNAL_IMPORTED'; pal.name=_unique_palette_name(scene, os.path.splitext(os.path.basename(filepath))[0], exclude=pal)
    reserved=default_reserved_indices(colors)
    for i,c in enumerate(colors): pc=pal.colors.add(); pc.color=c; pc.reserved=i in reserved; pc.quantization_enabled=True
    pal.usable_color_count=max(1,len(colors)-len(reserved)); pal.outline_index=reserved[0] if reserved else 0; scene.pixel_render_look_palette_id=pal.id
    return pal


def find_scene_palette(scene, palette_id):
    for p in scene.pixel_render_palettes:
        if p.id == palette_id:
            return p
    return None

def validate_palette_rename(scene, palette_id, name):
    name = sanitize_palette_name(name)
    if not name:
        raise ValueError('Palette name is empty')
    if any(p.name == name and p.id != palette_id for p in scene.pixel_render_palettes):
        raise ValueError('Duplicate palette name')
    return name

def ensure_editable_palette(scene, palette_id=None):
    palette_id = palette_id or scene.pixel_render_look_palette_id
    if palette_id in BUILTIN_PALETTES:
        pal = create_custom_from_palette(scene, palette_id)
        scene.pixel_render_look_palette_id = pal.id
        return pal
    pal = find_scene_palette(scene, palette_id)
    if pal is None:
        raise ValueError('Select a custom or imported palette')
    return pal

def clamp_selected_color_index(scene, pal):
    count = len(pal.colors)
    if count <= 0:
        scene.pixel_render_selected_color_index = 0
        return 0
    idx = max(0, min(scene.pixel_render_selected_color_index, count - 1))
    scene.pixel_render_selected_color_index = idx
    return idx

def set_outline_color(pal, index, enabled):
    if enabled:
        for i, color in enumerate(pal.colors):
            color.use_as_outline = i == index
        pal.outline_index = index
    else:
        pal.colors[index].use_as_outline = False

def gpl_text_from_scene_palette(scene):
    palette_id = scene.pixel_render_look_palette_id
    if palette_id in BUILTIN_PALETTES:
        return write_gpl(palette_id, [hex_to_rgba(h) for h in BUILTIN_PALETTES[palette_id]])
    for p in scene.pixel_render_palettes:
        if p.id == palette_id:
            return write_gpl(p.name, [c.color[:] for c in p.colors])
    raise ValueError('Select a valid palette to export')

def export_gpl_from_scene(scene, filepath):
    if not filepath:
        raise ValueError('GPL filepath is empty')
    if not filepath.lower().endswith('.gpl'):
        filepath += '.gpl'
    open(filepath,'w',encoding='utf-8').write(gpl_text_from_scene_palette(scene)); return filepath

if bpy:
 class PAQ_OT_select_palette_grid_color(bpy.types.Operator):
    bl_idname='paq.select_palette_grid_color'; bl_label='Select Palette Color'; bl_options={'REGISTER','UNDO'}
    index:bpy.props.IntProperty(default=0, min=0)
    def execute(self,context):
        scene=context.scene
        scene.pixel_render_selected_color_index=self.index
        from .properties import sync_selected_palette_color
        sync_selected_palette_color(scene)
        return {'FINISHED'}
 class PAQ_OT_duplicate_palette(bpy.types.Operator):
    bl_idname='paq.duplicate_palette_as_custom'; bl_label='Duplicate as Custom'; bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        try: pal=create_custom_from_palette(context.scene, context.scene.pixel_render_look_palette_id)
        except Exception as exc: self.report({'ERROR'},str(exc)); return {'CANCELLED'}
        context.scene.pixel_render_look_palette_id=pal.id; return {'FINISHED'}
 class PAQ_OT_rename_palette(bpy.types.Operator):
    bl_idname='paq.rename_custom_palette'; bl_label='Rename Custom'; bl_options={'REGISTER','UNDO'}
    name:bpy.props.StringProperty(name='Palette Name')
    def invoke(self,context,event):
        pid=context.scene.pixel_render_look_palette_id
        if pid in BUILTIN_PALETTES:
            self.report({'ERROR'},'Built-in palettes are read-only. Duplicate as Custom first.')
            return {'CANCELLED'}
        pal=find_scene_palette(context.scene,pid)
        if not pal:
            self.report({'ERROR'},'Select a custom palette')
            return {'CANCELLED'}
        self.name=pal.name
        return context.window_manager.invoke_props_dialog(self)
    def execute(self,context):
        pid=context.scene.pixel_render_look_palette_id
        if pid in BUILTIN_PALETTES:
            self.report({'ERROR'},'Built-in palettes are read-only. Duplicate as Custom first.')
            return {'CANCELLED'}
        try: name=validate_palette_rename(context.scene,pid,self.name)
        except ValueError as exc: self.report({'ERROR'},str(exc)); return {'CANCELLED'}
        pal=find_scene_palette(context.scene,pid)
        if pal and pal.type!='BUILTIN': pal.name=name; return {'FINISHED'}
        self.report({'ERROR'},'Select a custom palette'); return {'CANCELLED'}
 class PAQ_OT_delete_palette(bpy.types.Operator):
    bl_idname='paq.delete_custom_palette'; bl_label='Delete Custom'; bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        pals=context.scene.pixel_render_palettes
        for i,p in enumerate(pals):
            if p.id==context.scene.pixel_render_look_palette_id: pals.remove(i); context.scene.pixel_render_look_palette_id='PAQ_ModernCool_32'; return {'FINISHED'}
        return {'CANCELLED'}
 class PAQ_OT_load_gpl(bpy.types.Operator, ImportHelper):
    bl_idname='paq.load_gpl_palette'; bl_label='Load .gpl'; bl_options={'REGISTER','UNDO'}
    filename_ext='.gpl'; filter_glob:bpy.props.StringProperty(default='*.gpl', options={'HIDDEN'}); filepath:bpy.props.StringProperty(subtype='FILE_PATH')
    def invoke(self,context,event): context.window_manager.fileselect_add(self); return {'RUNNING_MODAL'}
    def execute(self,context):
        try: load_gpl_into_scene(context.scene, self.filepath)
        except Exception as exc: self.report({'ERROR'},f'Failed to load .gpl: {exc}'); return {'CANCELLED'}
        return {'FINISHED'}
 class PAQ_OT_export_gpl(bpy.types.Operator, ExportHelper):
    bl_idname='paq.export_gpl_palette'; bl_label='Export .gpl'; bl_options={'REGISTER','UNDO'}
    filename_ext='.gpl'; filter_glob:bpy.props.StringProperty(default='*.gpl', options={'HIDDEN'}); filepath:bpy.props.StringProperty(subtype='FILE_PATH')
    def invoke(self,context,event): context.window_manager.fileselect_add(self); return {'RUNNING_MODAL'}
    def execute(self,context):
        try: export_gpl_from_scene(context.scene, self.filepath)
        except Exception as exc: self.report({'ERROR'},f'Failed to export .gpl: {exc}'); return {'CANCELLED'}
        return {'FINISHED'}
 classes=(PAQ_OT_select_palette_grid_color,PAQ_OT_duplicate_palette,PAQ_OT_rename_palette,PAQ_OT_delete_palette,PAQ_OT_load_gpl,PAQ_OT_export_gpl)
