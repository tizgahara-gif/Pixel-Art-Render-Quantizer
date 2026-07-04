from __future__ import annotations
from contextlib import contextmanager
import os
import tempfile

try: import bpy
except ModuleNotFoundError: bpy=None

@contextmanager
def temporary_render_resolution(scene, width, height):
    old=(
        scene.render.resolution_x,
        scene.render.resolution_y,
        scene.render.resolution_percentage,
        scene.render.use_border,
        scene.render.use_crop_to_border,
    )
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.resolution_percentage = 100
    scene.render.use_border = False
    scene.render.use_crop_to_border = False
    try:
        yield
    finally:
        (
            scene.render.resolution_x,
            scene.render.resolution_y,
            scene.render.resolution_percentage,
            scene.render.use_border,
            scene.render.use_crop_to_border,
        ) = old

def upscale_nearest(pixels,width,height,scale):
    scale=int(scale); out=[]
    for y in range(height):
        row=[]
        for x in range(width): row.extend([pixels[y*width+x]]*scale)
        for _ in range(scale): out.extend(row)
    return out, width*scale, height*scale


def render_lowres_to_pixels(scene, width, height):
    """
    Render the scene to a temporary PNG file and return (pixels, actual_w, actual_h).

    Do not read pixels directly from Blender's special Render Result image.
    Render Result may report a valid size but expose an empty pixel buffer.
    """
    if bpy is None:
        raise RuntimeError("Blender is required")

    old=(
        scene.render.resolution_x,
        scene.render.resolution_y,
        scene.render.resolution_percentage,
        scene.render.use_border,
        scene.render.use_crop_to_border,
        scene.render.filepath,
        scene.render.image_settings.file_format,
        scene.render.image_settings.color_mode,
        scene.render.image_settings.color_depth,
    )

    temp_dir=tempfile.mkdtemp(prefix="paq_render_")
    temp_path=os.path.join(temp_dir,"paq_lowres.png")
    temp_img=None

    try:
        scene.render.resolution_x=int(width)
        scene.render.resolution_y=int(height)
        scene.render.resolution_percentage=100
        scene.render.use_border=False
        scene.render.use_crop_to_border=False

        scene.render.filepath=temp_path
        scene.render.image_settings.file_format="PNG"
        scene.render.image_settings.color_mode="RGBA"
        scene.render.image_settings.color_depth="8"

        bpy.ops.render.render(write_still=True)

        if not os.path.exists(temp_path):
            raise RuntimeError(f"Temporary render file was not created: {temp_path}")

        temp_img=bpy.data.images.load(temp_path,check_existing=False)

        actual_w,actual_h=int(temp_img.size[0]),int(temp_img.size[1])
        if actual_w <= 0 or actual_h <= 0:
            raise RuntimeError(f"Temporary render image has invalid size: {actual_w}x{actual_h}")

        flat=list(temp_img.pixels[:])
        pixels=[tuple(flat[i:i+4]) for i in range(0,len(flat),4)]

        if len(pixels) != actual_w * actual_h:
            raise RuntimeError(f"Temporary render pixel count mismatch: size={actual_w}x{actual_h}, pixels={len(pixels)}")

        return pixels,actual_w,actual_h

    finally:
        (
            scene.render.resolution_x,
            scene.render.resolution_y,
            scene.render.resolution_percentage,
            scene.render.use_border,
            scene.render.use_crop_to_border,
            scene.render.filepath,
            scene.render.image_settings.file_format,
            scene.render.image_settings.color_mode,
            scene.render.image_settings.color_depth,
        ) = old

        if temp_img is not None:
            try:
                bpy.data.images.remove(temp_img)
            except Exception:
                pass

        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            os.rmdir(temp_dir)
        except Exception:
            pass


def render_standard_to_pixels(scene):
    """
    Render using the current Blender render resolution/settings and return
    (pixels, actual_w, actual_h).
    This is used only for palette extraction.
    """
    if bpy is None:
        raise RuntimeError("Blender is required")

    old = (
        scene.render.filepath,
        scene.render.image_settings.file_format,
        scene.render.image_settings.color_mode,
        scene.render.image_settings.color_depth,
    )

    temp_dir = tempfile.mkdtemp(prefix="paq_standard_render_")
    temp_path = os.path.join(temp_dir, "paq_standard.png")
    temp_img = None

    try:
        scene.render.filepath = temp_path
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        scene.render.image_settings.color_depth = "8"

        bpy.ops.render.render(write_still=True)

        if not os.path.exists(temp_path):
            raise RuntimeError(f"Temporary render file was not created: {temp_path}")

        temp_img = bpy.data.images.load(temp_path, check_existing=False)
        actual_w, actual_h = int(temp_img.size[0]), int(temp_img.size[1])
        if actual_w <= 0 or actual_h <= 0:
            raise RuntimeError(f"Temporary render image has invalid size: {actual_w}x{actual_h}")

        flat = list(temp_img.pixels[:])
        pixels = [tuple(flat[i:i + 4]) for i in range(0, len(flat), 4)]

        if len(pixels) != actual_w * actual_h:
            raise RuntimeError(f"Temporary render pixel count mismatch: size={actual_w}x{actual_h}, pixels={len(pixels)}")

        return pixels, actual_w, actual_h

    finally:
        (
            scene.render.filepath,
            scene.render.image_settings.file_format,
            scene.render.image_settings.color_mode,
            scene.render.image_settings.color_depth,
        ) = old

        if temp_img is not None:
            try:
                bpy.data.images.remove(temp_img)
            except Exception:
                pass

        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            os.rmdir(temp_dir)
        except Exception:
            pass
