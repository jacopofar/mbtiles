from mbtiles_tools.tile import geometry_to_commands, ClosePath, LineTo, MoveTo


def test_example_point():
    assert geometry_to_commands([9, 50, 34]) == [
        MoveTo(25, 17),
    ]


def test_example_multi_point():
    assert geometry_to_commands([17, 10, 14, 3, 9]) == [
        MoveTo(5, 7),
        MoveTo(-2, -5),
    ]


def test_example_linestring():
    assert geometry_to_commands([9, 4, 4, 18, 0, 16, 16, 0]) == [
        MoveTo(2, 2),
        LineTo(0, 8),
        LineTo(8, 0),
    ]


def test_example_multilinestring():
    assert geometry_to_commands([9, 4, 4, 18, 0, 16, 16, 0, 9, 17, 17, 10, 4, 8]) == [
        MoveTo(+2, +2),
        LineTo(+0, +8),
        LineTo(+8, +0),
        MoveTo(-9, -9),
        LineTo(+2, +4),
    ]


def test_example_polygon():
    assert geometry_to_commands([9, 6, 12, 18, 10, 12, 24, 44, 15]) == [
        MoveTo(3, 6),
        LineTo(5, 6),
        LineTo(12, 22),
        ClosePath(),
    ]
