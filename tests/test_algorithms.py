from pixel_art_render_quantizer.palettes_builtin import BUILTIN_PALETTES
from pixel_art_render_quantizer.properties import default_reserved_indices
from pixel_art_render_quantizer.utils import hex_to_rgba, sanitize_palette_name
from pixel_art_render_quantizer.quantize import select_usable_colors, quantize_pixels
from pixel_art_render_quantizer.outline import cleanup_strict_mask
from pixel_art_render_quantizer.render_pipeline import upscale_nearest
from pixel_art_render_quantizer.palette_io_gpl import parse_gpl, write_gpl


def test_builtin_count_and_default_reservation():
    assert len(BUILTIN_PALETTES) == 12
    for name, hexes in BUILTIN_PALETTES.items():
        reserved = default_reserved_indices([hex_to_rgba(h) for h in hexes])
        assert len(reserved) == (0 if len(hexes) == 4 else 1)


def test_reserved_color_excluded_and_usable_reduced():
    colors = [hex_to_rgba(h) for h in BUILTIN_PALETTES['PAQ_ModernCool_08']]
    usable = select_usable_colors(colors, [0], 3)
    assert colors[0] not in usable
    assert len(usable) == 3
    out = quantize_pixels([(0.0,0.0,0.0,1.0)], 1, 1, colors, [0], 3)
    assert out[0][:3] != colors[0][:3]


def test_nearest_upscale():
    up,w,h=upscale_nearest([(1,0,0,1),(0,1,0,1)],2,1,2)
    assert (w,h)==(4,2)
    assert up == [(1,0,0,1),(1,0,0,1),(0,1,0,1),(0,1,0,1)]*2


def test_outline_cleanup_removes_2x2_and_branch():
    mask=[True,True,True,True]
    assert sum(cleanup_strict_mask(mask,2,2)) < 4
    branch=[False,True,False, True,True,True, False,False,False]
    cleaned=cleanup_strict_mask(branch,3,3)
    assert sum(cleaned) < sum(branch)


def test_gpl_roundtrip_and_name_sanitize():
    assert sanitize_palette_name(' bad/name:* ') == 'bad_name__'
    text=write_gpl('T',[hex_to_rgba('#000000'),hex_to_rgba('#FFFFFF')])
    assert parse_gpl(text) == [hex_to_rgba('#000000'),hex_to_rgba('#FFFFFF')]
