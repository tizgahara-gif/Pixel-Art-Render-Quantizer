"""Object Index based visible target mask rendering."""
from __future__ import annotations
from contextlib import contextmanager
import os
import tempfile

try: import bpy
except ModuleNotFoundError: bpy = None

SUPPORTED_TYPES = {"MESH", "CURVE", "SURFACE", "META", "FONT"}
TEMP_PASS_INDEX = 32767


def valid_outline_target_objects(scene, view_layer=None):
    objects = []
    skipped = 0
    view_objects = list(getattr(view_layer, "objects", [])) if view_layer is not None else None
    for item in getattr(scene, "pixel_render_outline_targets", []):
        obj = getattr(item, "object", None)
        if obj is None or getattr(obj, "type", None) not in SUPPORTED_TYPES or getattr(obj, "hide_render", False):
            skipped += 1; continue
        if view_objects is not None and not any(obj is candidate for candidate in view_objects):
            skipped += 1; continue
        objects.append(obj)
    return objects, skipped


@contextmanager
def temporary_object_index_state(scene, view_layer, objects):
    old_pass_indices = {}
    assigned_objects = []
    old_use_pass = getattr(view_layer, "use_pass_object_index", None)
    old_render = (
        scene.render.resolution_x, scene.render.resolution_y,
        scene.render.resolution_percentage, scene.render.use_border,
        scene.render.use_crop_to_border, scene.render.filepath,
        scene.render.image_settings.file_format, scene.render.image_settings.color_mode,
        scene.render.image_settings.color_depth,
    )
    old_compositing = getattr(scene.render, "use_compositing", None)
    old_sequencer = getattr(scene.render, "use_sequencer", None)
    try:
        for obj in objects:
            try:
                old_pass_indices[obj] = obj.pass_index
                obj.pass_index = TEMP_PASS_INDEX
                assigned_objects.append(obj)
            except Exception:
                # Linked-library or otherwise read-only objects can reject
                # pass_index writes. Skip them rather than falling back to
                # full-image alpha outlines, which would break scope semantics.
                old_pass_indices.pop(obj, None)
        if old_use_pass is not None:
            view_layer.use_pass_object_index = True
        yield assigned_objects
    finally:
        for obj, pass_index in old_pass_indices.items():
            try: obj.pass_index = pass_index
            except Exception: pass
        if old_use_pass is not None:
            view_layer.use_pass_object_index = old_use_pass
        (scene.render.resolution_x, scene.render.resolution_y,
         scene.render.resolution_percentage, scene.render.use_border,
         scene.render.use_crop_to_border, scene.render.filepath,
         scene.render.image_settings.file_format, scene.render.image_settings.color_mode,
         scene.render.image_settings.color_depth) = old_render
        if old_compositing is not None and hasattr(scene.render, "use_compositing"):
            scene.render.use_compositing = old_compositing
        if old_sequencer is not None and hasattr(scene.render, "use_sequencer"):
            scene.render.use_sequencer = old_sequencer


def _index_pass_pixels_from_render_result(width, height):
    image = bpy.data.images.get("Render Result")
    # Blender exposes render passes through view_layers in recent versions.
    for view_layer in getattr(image, "view_layers", []):
        for render_pass in getattr(view_layer, "passes", []):
            if getattr(render_pass, "name", "") in {"IndexOB", "Object Index"}:
                data = list(render_pass.rect[:])
                step = max(1, len(data) // (int(width) * int(height)))
                return [data[i] for i in range(0, len(data), step)][:int(width)*int(height)]
    return None


def render_outline_target_mask(scene, view_layer, width, height):
    if bpy is None:
        raise RuntimeError("Blender is required")
    objects, skipped = valid_outline_target_objects(scene, view_layer)
    if not objects:
        return [False] * (int(width) * int(height)), skipped, "No valid outline target objects."

    temp_dir = tempfile.mkdtemp(prefix="paq_index_mask_")
    temp_path = os.path.join(temp_dir, "paq_index.exr")
    try:
        with temporary_object_index_state(scene, view_layer, objects) as assigned_objects:
            skipped += len(objects) - len(assigned_objects)
            if not assigned_objects:
                return [False] * (int(width) * int(height)), skipped, "No writable outline target objects; no alpha-edge fallback was used."
            scene.render.resolution_x = int(width); scene.render.resolution_y = int(height)
            scene.render.resolution_percentage = 100
            scene.render.use_border = False; scene.render.use_crop_to_border = False
            if hasattr(scene.render, "use_compositing"): scene.render.use_compositing = False
            if hasattr(scene.render, "use_sequencer"): scene.render.use_sequencer = False
            scene.render.filepath = temp_path
            scene.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
            scene.render.image_settings.color_mode = "RGBA"
            scene.render.image_settings.color_depth = "32"
            bpy.ops.render.render(write_still=True)
            values = _index_pass_pixels_from_render_result(width, height)
            if values is None:
                raise RuntimeError("Object Index pass was not available from Render Result; no alpha-edge fallback was used.")
            mask = [round(float(v)) == TEMP_PASS_INDEX for v in values]
            return mask, skipped, None
    finally:
        try:
            if os.path.exists(temp_path): os.remove(temp_path)
            os.rmdir(temp_dir)
        except Exception:
            pass
