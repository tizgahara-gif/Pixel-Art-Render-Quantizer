try: import bpy
except ModuleNotFoundError: bpy=None

def pixels_to_image(name,pixels,width,height):
    if bpy is None: raise RuntimeError('Blender is required')
    img=bpy.data.images.get(name) or bpy.data.images.new(name,width,height,alpha=True)
    if img.size[0] != width or img.size[1] != height: img.scale(width,height)
    img.pixels.foreach_set([c for p in pixels for c in p]); img.update()
    return img

def show_image_in_editors(image, context):
    for area in context.screen.areas:
        if area.type == 'IMAGE_EDITOR':
            area.spaces.active.image = image
