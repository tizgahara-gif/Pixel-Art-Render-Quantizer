"""Internal CurveMapping storage for Palette Assignment Curve."""
from __future__ import annotations

try:
    import bpy
except ModuleNotFoundError:  # pragma: no cover - Blender-only module
    bpy = None

NODE_TREE_NAME = ".PAQ_Internal_AssignmentCurve"
NODE_NAME = ".PAQ_AssignmentCurve"


def assignment_curve_points_from_scene(scene):
    return [
        (0.0, scene.pixel_render_assignment_curve_black),
        (0.25, scene.pixel_render_assignment_curve_shadow),
        (0.5, scene.pixel_render_assignment_curve_mid),
        (0.75, scene.pixel_render_assignment_curve_light),
        (1.0, scene.pixel_render_assignment_curve_white),
    ]


def _curve_map(mapping):
    curves = getattr(mapping, "curves", None)
    if not curves:
        return None
    return curves[3] if len(curves) > 3 else curves[0]


def _reset_curve_points(curve_map, points):
    existing = list(curve_map.points)
    for point in existing[2:]:
        curve_map.points.remove(point)
    while len(curve_map.points) < 2:
        curve_map.points.new(1.0, 1.0)
    sorted_points = sorted(points, key=lambda item: item[0])
    curve_map.points[0].location = sorted_points[0]
    curve_map.points[1].location = sorted_points[-1]
    for x, y in sorted_points[1:-1]:
        curve_map.points.new(float(x), float(y))
    for point in curve_map.points:
        point.handle_type = 'AUTO'


def initialize_assignment_curve_mapping(mapping, points):
    curve_map = _curve_map(mapping)
    if curve_map is None:
        return False
    _reset_curve_points(curve_map, points)
    if hasattr(mapping, "clip_min_x"):
        mapping.clip_min_x = 0.0
        mapping.clip_min_y = 0.0
        mapping.clip_max_x = 1.0
        mapping.clip_max_y = 1.0
        mapping.use_clip = True
    if hasattr(mapping, "update"):
        mapping.update()
    return True


def get_assignment_curve_owner(scene):
    """Return the internal node that owns PAQ's CurveMapping, or None."""
    if bpy is None:
        return None
    tree = bpy.data.node_groups.get(NODE_TREE_NAME)
    created = tree is None
    if tree is None:
        tree = bpy.data.node_groups.new(NODE_TREE_NAME, 'CompositorNodeTree')
        tree.use_fake_user = True
    node = tree.nodes.get(NODE_NAME)
    if node is None:
        node = tree.nodes.new('CompositorNodeCurveRGB')
        node.name = NODE_NAME
        node.label = "PAQ Internal Assignment Curve"
        created = True
    if created and hasattr(node, "mapping"):
        initialize_assignment_curve_mapping(node.mapping, assignment_curve_points_from_scene(scene))
    return node


def get_assignment_curve_mapping(scene):
    """
    Return a Blender CurveMapping object used by PAQ Palette Assignment Curve.

    This must not modify the user's compositor node setup.
    """
    owner = get_assignment_curve_owner(scene)
    return getattr(owner, "mapping", None) if owner is not None else None


def reset_assignment_curve_mapping(scene):
    mapping = get_assignment_curve_mapping(scene)
    if mapping is None:
        return False
    return initialize_assignment_curve_mapping(
        mapping,
        [(0.0, 0.0), (0.25, 0.25), (0.5, 0.5), (0.75, 0.75), (1.0, 1.0)],
    )
