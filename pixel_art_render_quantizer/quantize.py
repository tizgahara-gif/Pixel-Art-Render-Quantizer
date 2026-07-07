"""sRGB RGB-distance quantization and look adjustment."""
from __future__ import annotations
from .utils import hex_to_rgba
import importlib.util

_HAS_NUMPY = importlib.util.find_spec("numpy") is not None

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

def _quantize_pixels_python(pixels, width, height, usable, dither_mode="NONE", dither_strength=0.0, assignment_curve_enabled=False, assignment_curve_lut=None, assignment_curve_points=None, assignment_curve_strength=1.0, **look):
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


def _quantize_pixels_numpy(pixels, width, height, usable, dither_mode="NONE", dither_strength=0.0, assignment_curve_enabled=False, assignment_curve_lut=None, assignment_curve_points=None, assignment_curve_strength=1.0, **look):
    import numpy as np

    arr = np.asarray(pixels, dtype=np.float64).reshape((int(height), int(width), 4)).copy()
    rgb = np.clip(arr[..., :3], 0.0, 1.0)

    gamma = float(look.get("gamma", 1.0))
    if gamma != 1.0:
        rgb = np.power(rgb, 1.0 / max(gamma, 1e-6))
    exposure = float(look.get("exposure", 0.0))
    if exposure:
        rgb = np.clip(rgb * (2 ** exposure), 0.0, 1.0)
    contrast = float(look.get("contrast", 1.0))
    if contrast != 1.0:
        rgb = np.clip((rgb - 0.5) * contrast + 0.5, 0.0, 1.0)
    saturation = float(look.get("saturation", 1.0))
    if saturation != 1.0:
        lum = rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
        rgb = np.clip(lum[..., None] + (rgb - lum[..., None]) * saturation, 0.0, 1.0)

    if assignment_curve_enabled and (assignment_curve_lut or assignment_curve_points):
        lut = assignment_curve_lut or build_assignment_curve_lut_from_points(assignment_curve_points, size=256)
        lut_arr = np.asarray(lut, dtype=np.float64)
        lum = np.clip(rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722, 0.0, 1.0)
        idx = np.rint(lum * (len(lut_arr) - 1)).astype(np.int64)
        mapped = np.clip(lut_arr[idx], 0.0, 1.0)
        strength = clamp01(assignment_curve_strength)
        target = lum + (mapped - lum) * strength
        scale = np.divide(target, lum, out=np.zeros_like(target), where=lum > 1e-6)
        rgb = np.where((lum <= 1e-6)[..., None], target[..., None], rgb * scale[..., None])
        rgb = np.clip(rgb, 0.0, 1.0)

    if dither_mode == "BAYER4" and dither_strength:
        from .dither import BAYER4
        bayer = (np.asarray(BAYER4, dtype=np.float64) / 15.0 - 0.5) / 8.0
        offsets = np.tile(bayer, (int(height + 3) // 4, int(width + 3) // 4))[:int(height), :int(width)]
        rgb = np.clip(rgb + offsets[..., None] * float(dither_strength), 0.0, 1.0)

    palette = np.asarray([c[:3] for c in usable], dtype=np.float64)
    flat = rgb.reshape((-1, 3))
    indices = np.argmin(np.sum((flat[:, None, :] - palette[None, :, :]) ** 2, axis=2), axis=1)
    quantized_rgb = palette[indices].reshape((int(height), int(width), 3))
    out = np.concatenate((quantized_rgb, arr[..., 3:4]), axis=2).reshape((-1, 4))
    return [tuple(float(v) for v in px) for px in out]


def quantize_pixels(pixels, width, height, palette_colors, reserved_indices=(), usable_color_count=0, dither_mode="NONE", dither_strength=0.0, enabled_indices=None, assignment_curve_enabled=False, assignment_curve_lut=None, assignment_curve_points=None, assignment_curve_strength=1.0, **look):
    usable = select_usable_colors(palette_colors, reserved_indices, usable_color_count, enabled_indices)
    if not usable:
        raise ValueError("Palette has no active quantization colors")
    if _HAS_NUMPY:
        return _quantize_pixels_numpy(pixels, width, height, usable, dither_mode, dither_strength, assignment_curve_enabled, assignment_curve_lut, assignment_curve_points, assignment_curve_strength, **look)
    return _quantize_pixels_python(pixels, width, height, usable, dither_mode, dither_strength, assignment_curve_enabled, assignment_curve_lut, assignment_curve_points, assignment_curve_strength, **look)
