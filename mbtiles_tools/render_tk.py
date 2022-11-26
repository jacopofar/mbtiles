from tkinter import Canvas, Tk

from mbtiles_tools.tile import LineTo, MoveTo, PathCommands


class DrawMap(Canvas):
    def __init__(self, parent: Tk, command_sets: list[PathCommands]) -> None:
        super().__init__(parent)
        for cmds in command_sets:
            x, y = 0, 0
            for c in cmds:
                if isinstance(c, MoveTo):
                    x += c.dX
                    y += c.dY
                if isinstance(c, LineTo):
                    nx = x + c.dX
                    ny = y + c.dY
                    self.create_line((x / 5, y / 5, nx / 5, ny / 5))
                    x, y = nx, ny


def render_with_tk(command_sets: list[PathCommands]) -> None:
    root = Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    sketch = DrawMap(root, command_sets)
    sketch.grid(column=0, row=0, sticky="nswe")
    root.mainloop()
