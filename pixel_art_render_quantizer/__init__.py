bl_info = {
    'name': 'Pixel Art Render Quantizer',
    'author': 'OpenAI',
    'version': (1, 0, 0),
    'blender': (3, 6, 0),
    'location': 'Compositor Sidebar, Render Properties, 3D Viewport Sidebar',
    'description': 'Post-render pixel art quantization, strict outline, alpha, nearest upscale, and PNG output.',
    'category': 'Render',
}

try: import bpy
except ModuleNotFoundError: bpy=None

if bpy:
    from bpy.app.handlers import persistent
    from .properties import register_properties, unregister_properties
    from . import operators_session, operators_render, operators_palette, operators_assignment, ui_compositor, ui_render, ui_viewport
    MODULE_CLASSES = (operators_session.classes + operators_render.classes + operators_palette.classes + operators_assignment.classes + ui_compositor.classes + ui_render.classes + ui_viewport.classes)
    @persistent
    def _paq_load_post(_dummy):
        for scene in bpy.data.scenes: scene.pixel_render_active = False
    def register():
        register_properties()
        for cls in MODULE_CLASSES: bpy.utils.register_class(cls)
        if _paq_load_post not in bpy.app.handlers.load_post: bpy.app.handlers.load_post.append(_paq_load_post)
    def unregister():
        if _paq_load_post in bpy.app.handlers.load_post: bpy.app.handlers.load_post.remove(_paq_load_post)
        for cls in reversed(MODULE_CLASSES): bpy.utils.unregister_class(cls)
        unregister_properties()
else:
    def register(): pass
    def unregister(): pass
