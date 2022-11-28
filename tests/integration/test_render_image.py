import pytest

from mbtiles_tools.tile import MBTile

@pytest.fixture(scope="module")
def tile_data():
    with open("tests/14_8609_5863.pbf", "rb") as fr:
        yield fr.read()

def test_render_styleless_image(tile_data):
    t = MBTile(tile_data)
    im = t.render_image_styleless()
    assert im.size == (4096, 4096)
    assert im.getcolors() == [(15928969, (255, 255, 255)), (848247, (0, 0, 0))]

def test_render_styleless_image_filter_layers(tile_data):
    t = MBTile(tile_data)
    im = t.render_image_styleless(layers=set(["building"]))
    assert im.size == (4096, 4096)
    assert im.getcolors() == [(16427687, (255, 255, 255)), (349529, (0, 0, 0))]

def test_render_styleless_image_scaled(tile_data):
    t = MBTile(tile_data)
    im2 = t.render_image_styleless(scale_factor=3)
    assert im2.size == (1366, 1366)
    assert im2.getcolors() == [(1793135, (255, 255, 255)), (72821, (0, 0, 0))]

def test_render_styleless_image_scaled_and_colorized(tile_data):
    t = MBTile(tile_data)
    im = t.render_image_styleless(scale_factor=4, colorize=True)
    im2 = t.render_image_styleless(scale_factor=4, colorize=True)
    assert im.size == (1024, 1024)
    assert im2.size == (1024, 1024)
    # different colors are present, don't enforce a specific amount
    assert len(im.getcolors()) > 5
    # same colors every time
    assert im.getcolors() == im2.getcolors()