try: import bpy
except ModuleNotFoundError: bpy=None
from .palettes_builtin import BUILTIN_PALETTES
from .properties import default_reserved_indices
from .utils import hex_to_rgba, new_id, sanitize_palette_name
from .palette_io_gpl import parse_gpl, write_gpl

def create_custom_from_builtin(scene, builtin_id):
    pal=scene.pixel_render_palettes.add(); pal.id=new_id('palette'); pal.type='CUSTOM_SCENE'; pal.source_builtin_id=builtin_id
    base=sanitize_palette_name(builtin_id+'_Custom'); names={p.name for p in scene.pixel_render_palettes if p != pal}; name=base; n=1
    while name in names: name=f'{base}_{n:03d}'; n+=1
    pal.name=name
    colors=[hex_to_rgba(h) for h in BUILTIN_PALETTES[builtin_id]]; reserved=default_reserved_indices(colors)
    for i,c in enumerate(colors):
        pc=pal.colors.add(); pc.color=c; pc.reserved=i in reserved; pc.quantization_enabled=True
    pal.usable_color_count=max(1,len(colors)-len(reserved)); pal.outline_index=reserved[0] if reserved else 0
    return pal
if bpy:
 class PAQ_OT_duplicate_palette(bpy.types.Operator):
    bl_idname='paq.duplicate_palette_as_custom'; bl_label='Duplicate as Custom'; bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        pal=create_custom_from_builtin(context.scene, context.scene.pixel_render_look_palette_id); context.scene.pixel_render_look_palette_id=pal.id; return {'FINISHED'}
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
 class PAQ_OT_load_gpl(bpy.types.Operator):
    bl_idname='paq.load_gpl_palette'; bl_label='Load .gpl'; bl_options={'REGISTER','UNDO'}
    filepath:bpy.props.StringProperty(subtype='FILE_PATH')
    def execute(self,context):
        colors=parse_gpl(open(self.filepath,encoding='utf-8').read()); pal=context.scene.pixel_render_palettes.add(); pal.id=new_id('palette'); pal.type='EXTERNAL_IMPORTED'; pal.name=sanitize_palette_name(self.filepath.rsplit('/',1)[-1].rsplit('.',1)[0])
        reserved=default_reserved_indices(colors)
        for i,c in enumerate(colors): pc=pal.colors.add(); pc.color=c; pc.reserved=i in reserved; pc.quantization_enabled=True
        pal.usable_color_count=max(1,len(colors)-len(reserved)); context.scene.pixel_render_look_palette_id=pal.id; return {'FINISHED'}
 class PAQ_OT_export_gpl(bpy.types.Operator):
    bl_idname='paq.export_gpl_palette'; bl_label='Export .gpl'; bl_options={'REGISTER','UNDO'}
    filepath:bpy.props.StringProperty(subtype='FILE_PATH')
    def execute(self,context):
        for p in context.scene.pixel_render_palettes:
            if p.id==context.scene.pixel_render_look_palette_id:
                open(self.filepath,'w',encoding='utf-8').write(write_gpl(p.name,[c.color[:] for c in p.colors])); return {'FINISHED'}
        return {'CANCELLED'}
 classes=(PAQ_OT_duplicate_palette,PAQ_OT_rename_palette,PAQ_OT_delete_palette,PAQ_OT_load_gpl,PAQ_OT_export_gpl)
