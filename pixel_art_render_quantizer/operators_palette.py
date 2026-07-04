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

def export_gpl_from_scene(scene, filepath):
    if not filepath:
        raise ValueError('GPL filepath is empty')
    if not filepath.lower().endswith('.gpl'):
        filepath += '.gpl'
    for p in scene.pixel_render_palettes:
        if p.id==scene.pixel_render_look_palette_id:
            open(filepath,'w',encoding='utf-8').write(write_gpl(p.name,[c.color[:] for c in p.colors])); return filepath
    raise ValueError('Select a custom or imported palette to export')

if bpy:
 class PAQ_OT_duplicate_palette(bpy.types.Operator):
    bl_idname='paq.duplicate_palette_as_custom'; bl_label='Duplicate as Custom'; bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        try: pal=create_custom_from_palette(context.scene, context.scene.pixel_render_look_palette_id)
        except Exception as exc: self.report({'ERROR'},str(exc)); return {'CANCELLED'}
        context.scene.pixel_render_look_palette_id=pal.id; return {'FINISHED'}
 class PAQ_OT_rename_palette(bpy.types.Operator):
    bl_idname='paq.rename_custom_palette'; bl_label='Rename Custom'; bl_options={'REGISTER','UNDO'}
    name:bpy.props.StringProperty(name='Palette Name')
    def execute(self,context):
        name=sanitize_palette_name(self.name); pals=context.scene.pixel_render_palettes
        if any(p.name==name and p.id!=context.scene.pixel_render_look_palette_id for p in pals): self.report({'ERROR'},'Duplicate palette name'); return {'CANCELLED'}
        for p in pals:
            if p.id==context.scene.pixel_render_look_palette_id and p.type!='BUILTIN': p.name=name; return {'FINISHED'}
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
 classes=(PAQ_OT_duplicate_palette,PAQ_OT_rename_palette,PAQ_OT_delete_palette,PAQ_OT_load_gpl,PAQ_OT_export_gpl)
