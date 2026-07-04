"""sRGB RGB-distance quantization and look adjustment."""
from __future__ import annotations
from .utils import hex_to_rgba

def select_usable_colors(colors, reserved_indices=(), usable_color_count=0, enabled_indices=None):
    reserved = set(reserved_indices or [])
    enabled = set(range(len(colors))) if enabled_indices is None else set(enabled_indices)
    candidates = [c for i, c in enumerate(colors) if i not in reserved and i in enabled]
    if usable_color_count and usable_color_count < len(candidates):
        if usable_color_count <= 1:
            candidates = candidates[:1]
        else:
            last = len(candidates) - 1
            candidates = [candidates[round(i * last / (usable_color_count - 1))] for i in range(usable_color_count)]
    return candidates

def clamp01(value):
    return max(0.0, min(1.0, float(value)))


def lerp(a, b, t):
    return a + (b - a) * t


def apply_look(pixel, gamma=1.0, exposure=0.0, contrast=1.0, saturation=1.0):
    r, g, b, a = pixel
    rgb = [max(0, min(1, c)) for c in (r, g, b)]
    if gamma != 1.0:
        inv = 1.0 / max(gamma, 1e-6); rgb = [c ** inv for c in rgb]
    if exposure:
        f = 2 ** exposure; rgb = [max(0, min(1, c * f)) for c in rgb]
    if contrast != 1.0:
        rgb = [max(0, min(1, (c - 0.5) * contrast + 0.5)) for c in rgb]
    if saturation != 1.0:
        lum = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
        rgb = [max(0, min(1, lum + (c - lum) * saturation)) for c in rgb]
    return (*rgb, a)


def evaluate_assignment_curve(value, points):
    """
    Evaluate a simple 5-point piecewise linear curve.

    Input points:
        [
            (0.0, black),
            (0.25, shadow),
            (0.5, mid),
            (0.75, light),
            (1.0, white),
        ]

    value: 0.0 - 1.0
    returns: 0.0 - 1.0
    """
    x = clamp01(value)

    if x <= 0.0:
        return clamp01(points[0][1])
    if x >= 1.0:
        return clamp01(points[-1][1])

    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        if x0 <= x <= x1:
            if x1 == x0:
                return clamp01(y1)
            t = (x - x0) / (x1 - x0)
            return clamp01(lerp(y0, y1, t))

    return x


def build_assignment_curve_lut_from_points(points, size=256):
    """Build a luminance remap LUT from numeric assignment curve points."""
    last = max(1, int(size) - 1)
    return [evaluate_assignment_curve(i / last, points) for i in range(int(size))]


def build_assignment_curve_lut_from_mapping(mapping, size=256):
    """Build a luminance remap LUT from a Blender CurveMapping-like object."""
    curves = getattr(mapping, "curves", None)
    if not curves:
        raise ValueError("CurveMapping has no curves")
    curve = curves[3] if len(curves) > 3 else curves[0]
    if hasattr(mapping, "update"):
        mapping.update()
    last = max(1, int(size) - 1)
    lut = []
    for i in range(int(size)):
        x = i / last
        if hasattr(mapping, "evaluate"):
            value = mapping.evaluate(curve, x)
        else:
            value = evaluate_assignment_curve(x, [(p.location[0], p.location[1]) for p in curve.points])
        lut.append(clamp01(value))
    return lut


def apply_assignment_curve_lut_to_pixel(pixel, lut, strength=1.0):
    r, g, b, a = pixel

    r = clamp01(r)
    g = clamp01(g)
    b = clamp01(b)

    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    index = max(0, min(len(lut) - 1, round(lum * (len(lut) - 1))))
    mapped_lum = clamp01(lut[index])

    strength = clamp01(strength)
    target_lum = lerp(lum, mapped_lum, strength)

    if lum <= 1e-6:
        rr = clamp01(target_lum)
        gg = clamp01(target_lum)
        bb = clamp01(target_lum)
    else:
        scale = target_lum / lum
        rr = clamp01(r * scale)
        gg = clamp01(g * scale)
        bb = clamp01(b * scale)

    return (rr, gg, bb, a)


def apply_assignment_curve_to_pixel(pixel, curve_points, strength=1.0):
    """
    Remap pixel luminance and scale RGB around that luminance.

    This affects palette matching without directly editing palette colors.
    """
    r, g, b, a = pixel

    r = clamp01(r)
    g = clamp01(g)
    b = clamp01(b)

    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    mapped_lum = evaluate_assignment_curve(lum, curve_points)

    strength = clamp01(strength)
    target_lum = lerp(lum, mapped_lum, strength)

    if lum <= 1e-6:
        rr = clamp01(target_lum)
        gg = clamp01(target_lum)
        bb = clamp01(target_lum)
    else:
        scale = target_lum / lum
        rr = clamp01(r * scale)
        gg = clamp01(g * scale)
        bb = clamp01(b * scale)

    return (rr, gg, bb, a)


def nearest_color(pixel, palette):
    r, g, b = pixel[:3]
    return min(palette, key=lambda c: (r-c[0])**2 + (g-c[1])**2 + (b-c[2])**2)

def quantize_pixels(pixels, width, height, palette_colors, reserved_indices=(), usable_color_count=0, dither_mode="NONE", dither_strength=0.0, enabled_indices=None, assignment_curve_enabled=False, assignment_curve_lut=None, assignment_curve_points=None, assignment_curve_strength=1.0, **look):
    usable = select_usable_colors(palette_colors, reserved_indices, usable_color_count, enabled_indices)
    if not usable:
        raise ValueError("Palette has no active quantization colors")
    out=[]
    from .dither import bayer4_offset
    for y in range(height):
        for x in range(width):
            p = apply_look(pixels[y*width+x], **look)
            if assignment_curve_enabled and assignment_curve_lut:
                p = apply_assignment_curve_lut_to_pixel(p, assignment_curve_lut, assignment_curve_strength)
            elif assignment_curve_enabled and assignment_curve_points:
                p = apply_assignment_curve_to_pixel(p, assignment_curve_points, assignment_curve_strength)
            if dither_mode == "BAYER4" and dither_strength:
                off = bayer4_offset(x, y) * dither_strength
                p = tuple(max(0, min(1, p[i] + off)) if i < 3 else p[i] for i in range(4))
            out.append((*nearest_color(p, usable)[:3], p[3]))
    return out
