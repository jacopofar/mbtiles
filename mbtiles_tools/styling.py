from dataclasses import dataclass
from typing import Generator

from PIL import Image, ImageColor, ImageDraw

from mbtiles_tools.tile import MBTile, PathCommands, MoveTo, LineTo


@dataclass
class LayerStyle:
    """Style data for a specific layer.
    Roughly equivalent to a CSS selector + style.
    See:
    https://docs.mapbox.com/mapbox-gl-js/style-spec/layers/
    """

    type: str
    paint: dict | None


@dataclass
class DrawStyle:
    """Style details for a specific element"""
    color: int|tuple


@dataclass
class DrawableElement:
    style: DrawStyle
    commands: PathCommands


def parse_color(color: str) -> int|tuple:
    if type(color) == dict:
        # it's an interpolation, just get the middle one
        return ImageColor.getrgb(color["stops"][0][1])
    return ImageColor.getrgb(color)

class MapBoxStyle:
    def __init__(self, style: dict):
        self.layers: dict[str, list[LayerStyle]] = {}
        self.bgcolor = "white"
        for layer in style["layers"]:
            if layer["type"] == "background":
                self.bgcolor = layer["paint"]["background-color"]
            else:
                source_layer: str = layer["source-layer"]
                if source_layer not in self.layers:
                    self.layers[source_layer] = []
                self.layers[source_layer].append(
                    LayerStyle(type=layer["type"], paint=layer.get("paint"))
                )

    def tile_to_draw_primitives(
        self, tile: MBTile
    ) -> Generator[DrawableElement, None, None]:
        for (
            layer_name,
            feature_type,
            feature_tags,
            draw_commands,
        ) in tile.generate_draw_commands():
            # here is where the style is applied, replaces the dict
            for styledef in self.layers.get(layer_name, []):
                if styledef.type == "line":
                    yield DrawableElement(
                        DrawStyle(color=parse_color(styledef.paint["line-color"])), draw_commands
                    )

    def render(self, tile: MBTile) -> Image.Image:
        extent = tile.get_max_extent()
        im = Image.new(
            "RGB",
            (extent, extent),
            self.bgcolor,
        )
        draw = ImageDraw.Draw(im)
        for de in self.tile_to_draw_primitives(tile):
            x, y = 0, 0
            for c in de.commands:
                if isinstance(c, MoveTo):
                    x += c.dX
                    y += c.dY
                if isinstance(c, LineTo):
                    nx = x + c.dX
                    ny = y + c.dY
                    draw.line((x, y, nx, ny), fill=de.style.color)
                    x, y = nx, ny
        return im
