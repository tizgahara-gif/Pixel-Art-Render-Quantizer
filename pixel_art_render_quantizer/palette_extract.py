from __future__ import annotations



def _clamp01(value):
    return max(0.0, min(1.0, float(value)))


def _channel_range(colors, channel):
    values = [color[channel] for color in colors]
    return max(values) - min(values)


def _split_box(colors):
    ranges = [_channel_range(colors, i) for i in range(3)]
    channel = max(range(3), key=lambda i: ranges[i])
    sorted_colors = sorted(colors, key=lambda color: color[channel])
    mid = len(sorted_colors) // 2
    return sorted_colors[:mid], sorted_colors[mid:]


def _average_color(colors):
    count = len(colors)
    r = sum(color[0] for color in colors) / count
    g = sum(color[1] for color in colors) / count
    b = sum(color[2] for color in colors) / count
    return (r, g, b, 1.0)


def _luminance(color):
    return 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]


def _sample_evenly(colors, max_samples):
    if len(colors) <= max_samples:
        return colors
    step = len(colors) / float(max_samples)
    return [colors[int(i * step)] for i in range(max_samples)]


def extract_palette_median_cut(pixels, target_count, alpha_threshold=0.05, max_samples=20000):
    """
    Extract representative RGBA colors from rendered pixels.

    Args:
        pixels: list of RGBA tuples, each channel 0.0 - 1.0
        target_count: number of colors to extract, from 2 to 256
        alpha_threshold: pixels with alpha <= threshold are ignored
        max_samples: maximum sampled pixels for performance

    Returns:
        list[tuple[float, float, float, float]]
    """
    target_count = int(target_count)
    if target_count < 2:
        raise ValueError('Color Count must be at least 2.')
    if target_count > 256:
        raise ValueError('Color Count must be 256 or less.')
    if max_samples <= 0:
        raise ValueError('max_samples must be greater than zero')

    colors = []
    for pixel in pixels:
        if len(pixel) < 4:
            continue
        if float(pixel[3]) <= alpha_threshold:
            continue
        colors.append((_clamp01(pixel[0]), _clamp01(pixel[1]), _clamp01(pixel[2])))

    if not colors:
        raise ValueError('No opaque pixels found in render')

    colors = _sample_evenly(colors, int(max_samples))
    boxes = [colors]

    while len(boxes) < target_count:
        split_index = None
        split_score = -1.0
        for index, box in enumerate(boxes):
            if len(box) < 2:
                continue
            score = max(_channel_range(box, channel) for channel in range(3))
            if score > split_score:
                split_index = index
                split_score = score
        if split_index is None:
            break
        box = boxes.pop(split_index)
        left, right = _split_box(box)
        if left:
            boxes.append(left)
        if right:
            boxes.append(right)
        if len(boxes) == 0:
            break

    palette = [_average_color(box) for box in boxes if box]
    palette.sort(key=_luminance)
    return palette[:target_count]
