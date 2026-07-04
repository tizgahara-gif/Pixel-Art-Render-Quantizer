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

from types import SimpleNamespace
import pytest
from pixel_art_render_quantizer.render_pipeline import temporary_render_resolution
from pixel_art_render_quantizer.operators_palette import create_custom_from_palette, load_gpl_into_scene
from pixel_art_render_quantizer.operators_render import individual_mode_error


class FakeCollection(list):
    def add(self):
        item = SimpleNamespace(colors=FakeCollection())
        self.append(item)
        return item


def _color_item(color):
    return SimpleNamespace(color=color, reserved=False, quantization_enabled=True)


def test_temporary_render_resolution_restores_percentage_on_exception():
    scene = SimpleNamespace(render=SimpleNamespace(resolution_x=1920, resolution_y=1080, resolution_percentage=50))
    with pytest.raises(RuntimeError):
        with temporary_render_resolution(scene, 320, 180):
            assert (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage) == (320, 180, 100)
            raise RuntimeError('boom')
    assert (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage) == (1920, 1080, 50)


def test_load_gpl_into_scene_empty_path_cancels_before_open():
    scene = SimpleNamespace(pixel_render_palettes=FakeCollection(), pixel_render_look_palette_id='')
    with pytest.raises(ValueError, match='empty'):
        load_gpl_into_scene(scene, '')


def test_duplicate_custom_palette_copies_scene_palette_and_unique_name():
    source = SimpleNamespace(
        id='custom_a', name='My Palette', type='CUSTOM_SCENE', colors=FakeCollection(), usable_color_count=0
    )
    source.colors.extend([_color_item((1, 0, 0, 1)), _color_item((0, 1, 0, 1))])
    scene = SimpleNamespace(pixel_render_palettes=FakeCollection())
    scene.pixel_render_palettes.append(source)
    pal = create_custom_from_palette(scene, 'custom_a')
    assert pal.id != source.id
    assert pal.name == 'My Palette_Custom'
    assert [c.color for c in pal.colors] == [(1, 0, 0, 1), (0, 1, 0, 1)]
    assert [c.color for c in source.colors] == [(1, 0, 0, 1), (0, 1, 0, 1)]


def test_individual_mode_reports_unimplemented_before_render():
    scene = SimpleNamespace(pixel_render_mode='INDIVIDUAL')
    assert individual_mode_error(scene) == 'Individual Palette Mode rendering is not implemented in v1.0. Switch to ALL in ONE for render output.'
