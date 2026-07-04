"""Blender property definitions and palette data management."""
from __future__ import annotations
from .palettes_builtin import BUILTIN_PALETTES, DEFAULT_PALETTE_ID
from .utils import hex_to_rgba, luminance, new_id, sanitize_palette_name

try:
    import bpy
except ModuleNotFoundError:  # allows algorithm tests outside Blender
    bpy = None

SCALE_ITEMS = [(str(v), f"x{v}", "") for v in (1, 2, 3, 4, 5, 6, 8)]
MODE_ITEMS = [("ALL_IN_ONE", "ALL in ONE", "Single palette for entire render"), ("INDIVIDUAL", "Individual Palette Mode", "Object and background palette assignment")]
PRESET_ITEMS = [("128x128", "Sprite / Icon", "128 x 128"), ("256x256", "Character Preview", "256 x 256"), ("320x180", "16:9 Small Scene", "320 x 180"), ("426x240", "16:9 Wide Preview", "426 x 240"), ("320x240", "4:3 Retro Scene", "320 x 240"), ("640x360", "Large Pixel Render", "640 x 360")]
CAMERA_FRAME_SYNC_ITEMS = [
    ("NONE", "Do Not Sync", "Do not change Blender render resolution"),
    ("LOWRES", "Sync Pixel Render Size", "Set Blender render resolution to the low-resolution Pixel Render Size"),
    ("FINAL", "Sync Final Output Size", "Set Blender render resolution to Pixel Render Size multiplied by Scale"),
]

def _palette_enum(self, context):
    items = [(pid, name, "Built-in palette") for pid, name in [(k, k) for k in BUILTIN_PALETTES]]
    scene = getattr(context, "scene", None)
    if scene:
        for pal in scene.pixel_render_palettes:
            items.append((pal.id, pal.name, pal.type))
    return items

def pixel_render_final_size(scene):
    width = int(scene.pixel_render_width)
    height = int(scene.pixel_render_height)
    scale = int(scene.pixel_render_scale)
    return width * scale, height * scale


def sync_camera_frame_to_pixel_render(scene):
    mode = getattr(scene, "pixel_render_camera_frame_sync_mode", "NONE")

    if mode == "NONE":
        return

    width = int(scene.pixel_render_width)
    height = int(scene.pixel_render_height)
    scale = int(scene.pixel_render_scale)

    if mode == "LOWRES":
        target_w = width
        target_h = height
    elif mode == "FINAL":
        target_w = width * scale
        target_h = height * scale
    else:
        return

    scene.render.resolution_x = target_w
    scene.render.resolution_y = target_h
    scene.render.resolution_percentage = 100
    scene.render.pixel_aspect_x = 1.0
    scene.render.pixel_aspect_y = 1.0


def _sync_resolution(self, context):
    sync_camera_frame_to_pixel_render(self)

def _apply_preset(self, context):
    if self.pixel_render_resolution_preset != "CUSTOM":
        w, h = self.pixel_render_resolution_preset.split("x")
        self.pixel_render_width, self.pixel_render_height = int(w), int(h)
        _sync_resolution(self, context)

def default_reserved_indices(colors):
    if len(colors) <= 4:
        return []
    black = next((i for i, c in enumerate(colors) if tuple(round(x, 4) for x in c[:3]) == (0, 0, 0)), None)
    return [black if black is not None else min(range(len(colors)), key=lambda i: luminance(colors[i]))]

_palette_edit_syncing = False

def _scene_palette(scene, palette_id):
    for pal in scene.pixel_render_palettes:
        if pal.id == palette_id:
            return pal
    return None

def _read_selected_palette_color(scene):
    """Return the currently selected palette color without making built-ins editable."""
    from .operators_palette import clamp_selected_color_index

    palette_id = scene.pixel_render_look_palette_id
    if palette_id in BUILTIN_PALETTES:
        colors = [hex_to_rgba(h) for h in BUILTIN_PALETTES[palette_id]]
        if not colors:
            return None, 0, None
        idx = max(0, min(scene.pixel_render_selected_color_index, len(colors) - 1))
        if scene.pixel_render_selected_color_index != idx:
            scene.pixel_render_selected_color_index = idx
        reserved = set(default_reserved_indices(colors))
        return None, idx, {
            "color": colors[idx],
            "reserved": idx in reserved,
            "quantization_enabled": True,
            "use_as_outline": idx in reserved,
        }

    pal = _scene_palette(scene, palette_id)
    if pal is None:
        return None, 0, None
    idx = clamp_selected_color_index(scene, pal)
    if len(pal.colors) <= 0:
        return pal, idx, None
    color = pal.colors[idx]
    return pal, idx, {
        "color": color.color[:],
        "reserved": color.reserved,
        "quantization_enabled": color.quantization_enabled,
        "use_as_outline": color.use_as_outline,
    }

def sync_selected_palette_color(scene):
    """Copy the selected palette entry into the Scene edit properties without writing back."""
    global _palette_edit_syncing
    if _palette_edit_syncing:
        return
    try:
        pal, idx, color = _read_selected_palette_color(scene)
    except Exception:
        return
    if color is None:
        return
    _palette_edit_syncing = True
    try:
        scene.pixel_render_selected_color = color["color"]
        scene.pixel_render_selected_color_reserved = color["reserved"]
        scene.pixel_render_selected_color_quantization_enabled = color["quantization_enabled"]
        scene.pixel_render_selected_color_use_as_outline = color["use_as_outline"]
    finally:
        _palette_edit_syncing = False

def _load_selected_palette_color(self, context):
    sync_selected_palette_color(self)

def _apply_selected_palette_color(self, context):
    global _palette_edit_syncing
    if _palette_edit_syncing:
        return
    from .operators_palette import ensure_editable_palette, clamp_selected_color_index, set_outline_color
    try:
        pal = ensure_editable_palette(self)
        idx = clamp_selected_color_index(self, pal)
    except Exception:
        return
    if len(pal.colors) <= 0:
        return
    color = pal.colors[idx]
    color.color = self.pixel_render_selected_color
    color.reserved = self.pixel_render_selected_color_reserved
    color.quantization_enabled = self.pixel_render_selected_color_quantization_enabled
    set_outline_color(pal, idx, self.pixel_render_selected_color_use_as_outline)

if bpy:
    class PAQ_PaletteColor(bpy.types.PropertyGroup):
        color: bpy.props.FloatVectorProperty(name="Color", subtype="COLOR", size=4, min=0, max=1, default=(0,0,0,1))
        reserved: bpy.props.BoolProperty(name="Reserved", default=False)
        quantization_enabled: bpy.props.BoolProperty(name="Quantization Enabled", default=True)
        use_as_outline: bpy.props.BoolProperty(name="Use as Outline Color", default=False)

    class PAQ_PaletteItem(bpy.types.PropertyGroup):
        id: bpy.props.StringProperty(name="Internal ID", default="")
        name: bpy.props.StringProperty(name="Palette Name", default="Custom Palette")
        type: bpy.props.EnumProperty(items=[("BUILTIN","Built-in",""),("CUSTOM_SCENE","Custom Scene",""),("EXTERNAL_IMPORTED","External Imported","")], default="CUSTOM_SCENE")
        source_builtin_id: bpy.props.StringProperty(default="")
        colors: bpy.props.CollectionProperty(type=PAQ_PaletteColor)
        outline_index: bpy.props.IntProperty(default=0, min=0)
        usable_color_count: bpy.props.IntProperty(default=0, min=0)
        selection_mode: bpy.props.StringProperty(default="EVENLY_REDUCED")
        theme_tag: bpy.props.StringProperty(default="")
        usage_tag: bpy.props.StringProperty(default="")

    def register_properties():
        bpy.utils.register_class(PAQ_PaletteColor); bpy.utils.register_class(PAQ_PaletteItem)
        s = bpy.types.Scene
        s.pixel_render_active = bpy.props.BoolProperty(default=False, options=set())
        s.pixel_render_mode = bpy.props.EnumProperty(items=MODE_ITEMS, default="ALL_IN_ONE")
        s.pixel_render_resolution_preset = bpy.props.EnumProperty(items=PRESET_ITEMS + [("CUSTOM", "Custom", "")], default="320x180", update=_apply_preset)
        s.pixel_render_width = bpy.props.IntProperty(default=320, min=1, update=_sync_resolution)
        s.pixel_render_height = bpy.props.IntProperty(default=180, min=1, update=_sync_resolution)
        s.pixel_render_scale = bpy.props.EnumProperty(items=SCALE_ITEMS, default="4", update=_sync_resolution)
        s.pixel_render_lock_aspect = bpy.props.BoolProperty(default=True)
        s.pixel_render_camera_frame_sync_mode = bpy.props.EnumProperty(items=CAMERA_FRAME_SYNC_ITEMS, default="FINAL", update=_sync_resolution)
        s.pixel_render_look_palette_id = bpy.props.EnumProperty(items=_palette_enum, update=_load_selected_palette_color)
        s.pixel_render_global_palette_id = bpy.props.EnumProperty(items=_palette_enum)
        s.pixel_render_background_palette_id = bpy.props.EnumProperty(items=_palette_enum)
        s.pixel_render_background_collection_id = bpy.props.StringProperty(default="")
        s.pixel_render_gamma = bpy.props.FloatProperty(default=1.0, min=0.1, max=5)
        s.pixel_render_exposure = bpy.props.FloatProperty(default=0.0, min=-5, max=5)
        s.pixel_render_contrast = bpy.props.FloatProperty(default=1.0, min=0, max=4)
        s.pixel_render_saturation = bpy.props.FloatProperty(default=1.0, min=0, max=4)
        s.pixel_render_alpha_mode = bpy.props.EnumProperty(items=[("PRESERVE","Preserve Alpha",""),("SOLID_THRESHOLD","Solid Threshold",""),("DITHERED","Dithered Alpha","")], default="PRESERVE")
        s.pixel_render_alpha_threshold = bpy.props.FloatProperty(default=0.5, min=0, max=1)
        s.pixel_render_dither_mode = bpy.props.EnumProperty(items=[("NONE","None",""),("BAYER4","Bayer 4x4","")], default="NONE")
        s.pixel_render_dither_strength = bpy.props.FloatProperty(default=0.0, min=0, max=1)
        s.pixel_render_outline_enabled = bpy.props.BoolProperty(name="Strict Alpha Edge Outline", description="v1.0 outline uses alpha edges only; object silhouette/depth outlines are not implemented yet", default=False)
        s.pixel_render_outline_mode = bpy.props.EnumProperty(items=[("STRICT","Strict Alpha Edge Outline","")], default="STRICT")
        s.pixel_render_outline_color_mode = bpy.props.EnumProperty(items=[("RESERVED_DARKEST","Use Reserved Darkest Color","")], default="RESERVED_DARKEST")
        s.pixel_render_output_path = bpy.props.StringProperty(subtype="DIR_PATH", default="")
        s.pixel_render_save_lowres_source = bpy.props.BoolProperty(default=False)
        s.pixel_render_save_quantized_lowres = bpy.props.BoolProperty(default=True)
        s.pixel_render_save_upscaled = bpy.props.BoolProperty(default=True)
        s.pixel_render_palettes = bpy.props.CollectionProperty(type=PAQ_PaletteItem)
        s.pixel_render_selected_color_index = bpy.props.IntProperty(name="Selected Color Index", default=0, min=0, update=_load_selected_palette_color)
        s.pixel_render_selected_color = bpy.props.FloatVectorProperty(name="Color", subtype="COLOR", size=4, min=0, max=1, default=(0,0,0,1), update=_apply_selected_palette_color)
        s.pixel_render_selected_color_reserved = bpy.props.BoolProperty(name="Reserved", default=False, update=_apply_selected_palette_color)
        s.pixel_render_selected_color_quantization_enabled = bpy.props.BoolProperty(name="Quantization Enabled", default=True, update=_apply_selected_palette_color)
        s.pixel_render_selected_color_use_as_outline = bpy.props.BoolProperty(name="Use as Outline Color", default=False, update=_apply_selected_palette_color)
        bpy.types.Object.pixel_render_palette_override_enabled = bpy.props.BoolProperty(default=False)
        bpy.types.Object.pixel_render_palette_id = bpy.props.StringProperty(default="")

    def unregister_properties():
        scene_props = (
            'pixel_render_active', 'pixel_render_mode', 'pixel_render_resolution_preset',
            'pixel_render_width', 'pixel_render_height', 'pixel_render_scale',
            'pixel_render_lock_aspect', 'pixel_render_camera_frame_sync_mode',
            'pixel_render_look_palette_id', 'pixel_render_global_palette_id',
            'pixel_render_background_palette_id', 'pixel_render_background_collection_id',
            'pixel_render_gamma', 'pixel_render_exposure', 'pixel_render_contrast',
            'pixel_render_saturation', 'pixel_render_alpha_mode', 'pixel_render_alpha_threshold',
            'pixel_render_dither_mode', 'pixel_render_dither_strength',
            'pixel_render_outline_enabled', 'pixel_render_outline_mode',
            'pixel_render_outline_color_mode', 'pixel_render_output_path',
            'pixel_render_save_lowres_source', 'pixel_render_save_quantized_lowres',
            'pixel_render_save_upscaled', 'pixel_render_palettes',
            'pixel_render_selected_color_index', 'pixel_render_selected_color',
            'pixel_render_selected_color_reserved',
            'pixel_render_selected_color_quantization_enabled',
            'pixel_render_selected_color_use_as_outline',
        )
        for prop in scene_props:
            if hasattr(bpy.types.Scene, prop):
                delattr(bpy.types.Scene, prop)
        for prop in ('pixel_render_palette_override_enabled', 'pixel_render_palette_id'):
            if hasattr(bpy.types.Object, prop):
                delattr(bpy.types.Object, prop)
        for cls in (PAQ_PaletteItem, PAQ_PaletteColor):
            try:
                bpy.utils.unregister_class(cls)
            except RuntimeError:
                pass
