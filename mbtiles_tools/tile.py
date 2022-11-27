from dataclasses import dataclass
from typing import Any, Generator

from google.protobuf.internal.containers import RepeatedScalarFieldContainer
from PIL import Image, ImageDraw

from mbtiles_tools import vector_tile_pb2
from mbtiles_tools import render_tk


@dataclass
class MoveTo:
    dX: int
    dY: int


@dataclass
class LineTo:
    dX: int
    dY: int


@dataclass
class ClosePath:
    # no parameters
    pass


PathCommands = list[LineTo | MoveTo | ClosePath]


def geometry_to_commands(geometry: RepeatedScalarFieldContainer[int]) -> PathCommands:
    idx: int = 0
    commands: PathCommands = []
    while idx < len(geometry):
        command_value = geometry[idx]
        command_id = command_value & 0x7
        parameters_count = command_value >> 3
        idx += 1
        if command_id not in (1, 2, 7):
            raise ValueError(
                f"Command id {command_id} from value {command_value} unknown!"
            )
        if command_id == 7:
            commands.append(ClosePath())
            continue
        while parameters_count > 0:
            parameters_count -= 1
            parameter_x = (geometry[idx] >> 1) ^ (-(geometry[idx] & 1))
            parameter_y = (geometry[idx + 1] >> 1) ^ (-(geometry[idx + 1] & 1))
            # the count is for couples of parameters
            idx += 2
            if command_id == 1:
                commands.append(MoveTo(parameter_x, parameter_y))
            elif command_id == 2:
                commands.append(LineTo(parameter_x, parameter_y))
    return commands


class MBTile:
    def __init__(self, data: bytes) -> None:
        self.raw_tile = vector_tile_pb2.Tile()
        self.raw_tile.ParseFromString(data)

    def generate_draw_commands(
        self,
    ) -> Generator[tuple[str, Any, Any, PathCommands], None, None]:
        for layer in self.raw_tile.layers:
            for feature in layer.features:
                yield (
                    layer.name,
                    feature.type,
                    feature.tags,  # TODO yield tags as a dictionary, not this stuff
                    geometry_to_commands(feature.geometry),
                )

    def render_tk_styleless(self) -> None:
        """Render all layers without any style and display using Tk.
        NOTE: does not render points, only lines including area perimeters
        Quick and simple, useful for debugging.
        """
        command_sets: list[PathCommands] = []
        for layer in self.raw_tile.layers:
            for feature in layer.features:
                command_sets.append(geometry_to_commands(feature.geometry))
        render_tk.render_with_tk(command_sets)

    def get_max_extent(self) -> int:
        # TODO can extent change across layers??
        return self.raw_tile.layers[0].extent

    def render_image_styleless(self) -> Image.Image:
        """Return a PIL image object with the tile drawn without style.

        NOTE: does not render points, only lines including area perimeters
        Quick and simple, useful for debugging.
        """
        im = Image.new(
            "RGB",
            (self.raw_tile.layers[0].extent, self.raw_tile.layers[0].extent),
            (255, 255, 255),
        )
        draw = ImageDraw.Draw(im)
        command_sets: list[PathCommands] = []
        for layer in self.raw_tile.layers:
            for feature in layer.features:
                command_sets.append(geometry_to_commands(feature.geometry))

        for cmds in command_sets:
            x, y = 0, 0
            for c in cmds:
                if isinstance(c, MoveTo):
                    x += c.dX
                    y += c.dY
                if isinstance(c, LineTo):
                    nx = x + c.dX
                    ny = y + c.dY
                    draw.line((x, y, nx, ny), fill="black")
                    x, y = nx, ny
        return im
