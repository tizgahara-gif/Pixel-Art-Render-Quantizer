from __future__ import annotations
from contextlib import contextmanager

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
