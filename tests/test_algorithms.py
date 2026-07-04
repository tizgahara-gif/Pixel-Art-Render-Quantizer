from pixel_art_render_quantizer.palettes_builtin import BUILTIN_PALETTES, BUILTIN_PALETTE_DEFAULT_USABLE_COUNTS, builtin_default_usable_count
from pixel_art_render_quantizer.properties import default_reserved_indices, pixel_render_final_size, sync_camera_frame_to_pixel_render
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



def test_builtin_default_usable_counts_match_palette_sizes():
    assert set(BUILTIN_PALETTE_DEFAULT_USABLE_COUNTS) == set(BUILTIN_PALETTES)
    for palette_id, hexes in BUILTIN_PALETTES.items():
        assert builtin_default_usable_count(palette_id, len(hexes), 1) == max(1, len(hexes) - 1)


def test_palette_for_scene_uses_builtin_default_usable_count():
    scene = SimpleNamespace(pixel_render_palettes=FakeCollection())
    colors, reserved, usable, enabled = palette_for_scene(scene, 'PAQ_ModernCool_32')
    assert len(colors) == 32
    assert usable == 31
    assert enabled == list(range(32))


def test_create_custom_from_builtin_copies_default_usable_count():
    scene = SimpleNamespace(pixel_render_palettes=FakeCollection())
    pal = create_custom_from_palette(scene, 'PAQ_ModernCool_32')
    assert pal.usable_color_count == 31

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
from pixel_art_render_quantizer.operators_palette import create_custom_from_palette, load_gpl_into_scene, ensure_editable_palette, validate_palette_rename, set_outline_color
from pixel_art_render_quantizer.operators_render import individual_mode_error, palette_for_scene


class FakeCollection(list):
    def add(self):
        item = SimpleNamespace(colors=FakeCollection())
        self.append(item)
        return item


def _color_item(color):
    return SimpleNamespace(color=color, reserved=False, quantization_enabled=True)


def test_temporary_render_resolution_restores_percentage_on_exception():
    scene = SimpleNamespace(render=SimpleNamespace(resolution_x=1920, resolution_y=1080, resolution_percentage=50, use_border=True, use_crop_to_border=True))
    with pytest.raises(RuntimeError):
        with temporary_render_resolution(scene, 320, 180):
            assert (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage) == (320, 180, 100)
            assert (scene.render.use_border, scene.render.use_crop_to_border) == (False, False)
            raise RuntimeError('boom')
    assert (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage) == (1920, 1080, 50)
    assert (scene.render.use_border, scene.render.use_crop_to_border) == (True, True)


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


def test_builtin_palette_edit_ensures_custom_palette():
    scene = SimpleNamespace(pixel_render_palettes=FakeCollection(), pixel_render_look_palette_id='PAQ_ModernCool_08')
    pal = ensure_editable_palette(scene)
    assert pal.id == scene.pixel_render_look_palette_id
    assert pal.type == 'CUSTOM_SCENE'
    assert pal.source_builtin_id == 'PAQ_ModernCool_08'
    assert 'PAQ_ModernCool_08' in pal.name


def test_rename_palette_validation_rejects_duplicate_and_sanitizes():
    scene = SimpleNamespace(pixel_render_palettes=FakeCollection())
    scene.pixel_render_palettes.extend([SimpleNamespace(id='a', name='First'), SimpleNamespace(id='b', name='Second')])
    assert validate_palette_rename(scene, 'a', 'new/name:*') == 'new_name__'
    with pytest.raises(ValueError, match='Duplicate'):
        validate_palette_rename(scene, 'a', 'Second')


def test_set_outline_color_is_exclusive_and_updates_index():
    pal = SimpleNamespace(colors=FakeCollection(), outline_index=0)
    pal.colors.extend([SimpleNamespace(use_as_outline=False), SimpleNamespace(use_as_outline=False), SimpleNamespace(use_as_outline=True)])
    set_outline_color(pal, 1, True)
    assert [c.use_as_outline for c in pal.colors] == [False, True, False]
    assert pal.outline_index == 1


def test_palette_for_scene_returns_empty_enabled_indices_for_disabled_custom_palette():
    pal = SimpleNamespace(id='custom', colors=FakeCollection(), usable_color_count=0)
    pal.colors.extend([
        SimpleNamespace(color=(1.0, 0.0, 0.0, 1.0), reserved=False, quantization_enabled=False),
        SimpleNamespace(color=(0.0, 1.0, 0.0, 1.0), reserved=False, quantization_enabled=False),
    ])
    scene = SimpleNamespace(pixel_render_palettes=FakeCollection([pal]))

    colors, reserved, usable, enabled = palette_for_scene(scene, 'custom')

    assert colors == [(1.0, 0.0, 0.0, 1.0), (0.0, 1.0, 0.0, 1.0)]
    assert reserved == []
    assert usable == 0
    assert enabled == []


def test_quantize_pixels_excludes_disabled_enabled_indices():
    colors = [hex_to_rgba('#000000'), hex_to_rgba('#FFFFFF')]
    out = quantize_pixels([(0.0, 0.0, 0.0, 1.0)], 1, 1, colors, enabled_indices=[1])
    assert out == [(1.0, 1.0, 1.0, 1.0)]


def test_quantize_pixels_combines_reserved_and_disabled_filters():
    colors = [hex_to_rgba('#000000'), hex_to_rgba('#FF0000'), hex_to_rgba('#00FF00')]
    out = quantize_pixels([(1.0, 0.0, 0.0, 1.0)], 1, 1, colors, reserved_indices=[1], enabled_indices=[1, 2])
    assert out == [(0.0, 1.0, 0.0, 1.0)]
    with pytest.raises(ValueError, match='no active quantization colors'):
        quantize_pixels([(1.0, 0.0, 0.0, 1.0)], 1, 1, colors, reserved_indices=[1], enabled_indices=[1])


def test_builtin_palette_can_be_serialized_to_gpl_text():
    from pixel_art_render_quantizer.operators_palette import gpl_text_from_scene_palette

    scene = SimpleNamespace(pixel_render_look_palette_id='PAQ_ModernCool_32', pixel_render_palettes=FakeCollection())
    text = gpl_text_from_scene_palette(scene)
    assert 'Name: PAQ_ModernCool_32' in text
    assert parse_gpl(text) == [hex_to_rgba(h) for h in BUILTIN_PALETTES['PAQ_ModernCool_32']]


def test_sync_selected_palette_color_does_not_duplicate_builtin_palette():
    from pixel_art_render_quantizer.properties import sync_selected_palette_color

    scene = SimpleNamespace(
        pixel_render_palettes=FakeCollection(),
        pixel_render_look_palette_id='PAQ_ModernCool_08',
        pixel_render_selected_color_index=1,
        pixel_render_selected_color=(0, 0, 0, 1),
        pixel_render_selected_color_reserved=False,
        pixel_render_selected_color_quantization_enabled=False,
        pixel_render_selected_color_use_as_outline=False,
    )
    sync_selected_palette_color(scene)
    assert len(scene.pixel_render_palettes) == 0
    assert scene.pixel_render_selected_color == hex_to_rgba(BUILTIN_PALETTES['PAQ_ModernCool_08'][1])
    assert scene.pixel_render_selected_color_quantization_enabled is True


def test_apply_selected_palette_reserved_only_preserves_color_value():
    from pixel_art_render_quantizer.properties import _apply_selected_palette_color, sync_selected_palette_color

    pal = SimpleNamespace(id='custom', name='Custom', type='CUSTOM_SCENE', colors=FakeCollection(), outline_index=0, usable_color_count=0)
    original = (0.25, 0.5, 0.75, 1.0)
    pal.colors.append(SimpleNamespace(color=original, reserved=False, quantization_enabled=True, use_as_outline=False))
    scene = SimpleNamespace(
        pixel_render_palettes=FakeCollection([pal]),
        pixel_render_look_palette_id='custom',
        pixel_render_selected_color_index=0,
        pixel_render_selected_color=(0, 0, 0, 1),
        pixel_render_selected_color_reserved=False,
        pixel_render_selected_color_quantization_enabled=True,
        pixel_render_selected_color_use_as_outline=False,
    )
    sync_selected_palette_color(scene)
    scene.pixel_render_selected_color_reserved = True
    _apply_selected_palette_color(scene, None)
    assert pal.colors[0].color == original
    assert pal.colors[0].reserved is True



def test_apply_selected_palette_color_preserves_builtin_edit_during_palette_switch(monkeypatch):
    from pixel_art_render_quantizer import operators_palette
    from pixel_art_render_quantizer.properties import _apply_selected_palette_color

    pal = SimpleNamespace(id='custom', name='Custom', type='CUSTOM_SCENE', colors=FakeCollection(), outline_index=0, usable_color_count=0)
    pal.colors.extend([
        SimpleNamespace(color=(0.0, 0.0, 0.0, 1.0), reserved=False, quantization_enabled=True, use_as_outline=False),
        SimpleNamespace(color=(0.1, 0.1, 0.1, 1.0), reserved=False, quantization_enabled=True, use_as_outline=False),
        SimpleNamespace(color=(0.2, 0.2, 0.2, 1.0), reserved=False, quantization_enabled=True, use_as_outline=False),
        SimpleNamespace(color=(0.3, 0.3, 0.3, 1.0), reserved=False, quantization_enabled=True, use_as_outline=False),
    ])
    edited = (1.0, 0.0, 0.0, 1.0)
    scene = SimpleNamespace(
        pixel_render_palettes=FakeCollection([pal]),
        pixel_render_look_palette_id='PAQ_ModernCool_08',
        pixel_render_selected_color_index=3,
        pixel_render_selected_color=edited,
        pixel_render_selected_color_reserved=True,
        pixel_render_selected_color_quantization_enabled=False,
        pixel_render_selected_color_use_as_outline=True,
    )

    def fake_ensure_editable_palette(scene_arg, palette_id=None):
        scene_arg.pixel_render_look_palette_id = pal.id
        scene_arg.pixel_render_selected_color = (0.3, 0.3, 0.3, 1.0)
        scene_arg.pixel_render_selected_color_reserved = False
        scene_arg.pixel_render_selected_color_quantization_enabled = True
        scene_arg.pixel_render_selected_color_use_as_outline = False
        return pal

    monkeypatch.setattr(operators_palette, 'ensure_editable_palette', fake_ensure_editable_palette)

    _apply_selected_palette_color(scene, None)

    assert scene.pixel_render_selected_color_index == 3
    assert pal.colors[3].color == edited
    assert pal.colors[3].reserved is True
    assert pal.colors[3].quantization_enabled is False
    assert pal.colors[3].use_as_outline is True
    assert scene.pixel_render_selected_color == edited
    assert scene.pixel_render_selected_color_reserved is True
    assert scene.pixel_render_selected_color_quantization_enabled is False
    assert scene.pixel_render_selected_color_use_as_outline is True


def test_apply_selected_palette_color_tags_context_areas_for_redraw():
    from pixel_art_render_quantizer.properties import _apply_selected_palette_color

    pal = SimpleNamespace(id='custom', name='Custom', type='CUSTOM_SCENE', colors=FakeCollection(), outline_index=0, usable_color_count=0)
    pal.colors.append(SimpleNamespace(color=(0.0, 0.0, 0.0, 1.0), reserved=False, quantization_enabled=True, use_as_outline=False))
    scene = SimpleNamespace(
        pixel_render_palettes=FakeCollection([pal]),
        pixel_render_look_palette_id='custom',
        pixel_render_selected_color_index=0,
        pixel_render_selected_color=(0.0, 1.0, 0.0, 1.0),
        pixel_render_selected_color_reserved=False,
        pixel_render_selected_color_quantization_enabled=True,
        pixel_render_selected_color_use_as_outline=False,
    )
    area = SimpleNamespace(redraws=0)
    area.tag_redraw = lambda: setattr(area, 'redraws', area.redraws + 1)
    context = SimpleNamespace(screen=SimpleNamespace(areas=[area]))

    _apply_selected_palette_color(scene, context)

    assert pal.colors[0].color == (0.0, 1.0, 0.0, 1.0)
    assert area.redraws == 1

def test_palette_preview_data_reads_builtin_without_scene_mutation():
    from pixel_art_render_quantizer.ui_render import palette_display_entries, palette_preview_data

    scene = SimpleNamespace(pixel_render_look_palette_id='PAQ_ModernCool_08', pixel_render_palettes=FakeCollection())
    preview = palette_preview_data(scene)
    entries = palette_display_entries(scene)

    assert preview['name'] == 'PAQ_ModernCool_08'
    assert [entry['hex'] for entry in preview['colors']] == BUILTIN_PALETTES['PAQ_ModernCool_08']
    assert [entry['hex'] for entry in entries] == BUILTIN_PALETTES['PAQ_ModernCool_08']
    assert all(entry['quantization_enabled'] for entry in preview['colors'])
    assert len(scene.pixel_render_palettes) == 0


def test_palette_preview_data_reads_custom_palette_flags():
    from pixel_art_render_quantizer.ui_render import palette_display_entries, palette_preview_data

    pal = SimpleNamespace(id='custom', name='Custom Palette', colors=FakeCollection())
    pal.colors.extend([
        SimpleNamespace(color=(0.25, 0.5, 0.75, 1.0), reserved=True, quantization_enabled=False, use_as_outline=True),
        SimpleNamespace(color=(1.0, 0.0, 0.0, 1.0), reserved=False, quantization_enabled=True, use_as_outline=False),
    ])
    scene = SimpleNamespace(pixel_render_look_palette_id='custom', pixel_render_palettes=FakeCollection([pal]))
    preview = palette_preview_data(scene)
    entries = palette_display_entries(scene)

    assert preview['name'] == 'Custom Palette'
    assert preview['colors'][0]['hex'] == '#4080BF'
    assert entries[0]['hex'] == '#4080BF'
    assert preview['colors'][0]['reserved'] is True
    assert preview['colors'][0]['quantization_enabled'] is False
    assert preview['colors'][0]['use_as_outline'] is True
    assert preview['colors'][1]['hex'] == '#FF0000'


def _sync_scene(mode='FINAL', width=320, height=240, scale='4'):
    render = SimpleNamespace(
        resolution_x=1920,
        resolution_y=1080,
        resolution_percentage=50,
        pixel_aspect_x=2.0,
        pixel_aspect_y=1.5,
    )
    return SimpleNamespace(
        pixel_render_camera_frame_sync_mode=mode,
        pixel_render_width=width,
        pixel_render_height=height,
        pixel_render_scale=scale,
        render=render,
    )


def test_pixel_render_final_size_uses_scale():
    scene = _sync_scene(width=320, height=180, scale='4')
    assert pixel_render_final_size(scene) == (1280, 720)


def test_sync_camera_frame_final_output_size_and_square_pixels():
    scene = _sync_scene(mode='FINAL', width=320, height=240, scale='4')
    sync_camera_frame_to_pixel_render(scene)
    assert (scene.render.resolution_x, scene.render.resolution_y) == (1280, 960)
    assert scene.render.resolution_percentage == 100
    assert (scene.render.pixel_aspect_x, scene.render.pixel_aspect_y) == (1.0, 1.0)


def test_sync_camera_frame_lowres_and_none_modes():
    lowres_scene = _sync_scene(mode='LOWRES', width=320, height=240, scale='4')
    sync_camera_frame_to_pixel_render(lowres_scene)
    assert (lowres_scene.render.resolution_x, lowres_scene.render.resolution_y) == (320, 240)

    none_scene = _sync_scene(mode='NONE', width=320, height=240, scale='4')
    sync_camera_frame_to_pixel_render(none_scene)
    assert (none_scene.render.resolution_x, none_scene.render.resolution_y) == (1920, 1080)
    assert (none_scene.render.pixel_aspect_x, none_scene.render.pixel_aspect_y) == (2.0, 1.5)
