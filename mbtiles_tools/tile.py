from dataclasses import dataclass

from vector_tile_protoc import vector_tile_pb2

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


def geometry_to_commands(geometry: list[int]) -> PathCommands:
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


if __name__ == "__main__":
    t = vector_tile_pb2.Tile()
    t.ParseFromString(open("14_8609_5863.pbf", "rb").read())
    command_sets: list[PathCommands] = []
    for layer in t.layers:
        print("LAYER:")
        print("layer version", layer.version)
        print("layer name", layer.name)
        print("layer extent", layer.extent)
        for k, v in zip(layer.keys, layer.values):
            print("LAYER KEY VALUE:", k, "=>", v)
        for feature in layer.features:
            print(feature.id)
            print(feature.type)
            print(feature.tags)
            print(feature.geometry)
            command_sets.append(geometry_to_commands(feature.geometry))
            # print(geometry_to_commands(feature.geometry))
    render_tk.render_with_tk(command_sets)