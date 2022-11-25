from tkinter import Canvas, Tk

from mbtiles_tools.tile import LineTo, MoveTo, PathCommands


class Sketchpad(Canvas):
    def __init__(self, parent: Tk, command_sets: list[PathCommands], **kwargs):
        super().__init__(parent, **kwargs)
        for cmds in command_sets:
            x, y = 0, 0
            for c in cmds:
                print(c, type(c), isinstance(c, LineTo))
                if isinstance(c, MoveTo):
                    x += c.dX
                    y += c.dY
                if isinstance(c, LineTo):
                    nx = x + c.dX
                    ny = y + c.dY
                    print((x / 5, y / 5, nx / 5, ny / 5))
                    self.create_line((x / 5, y / 5, nx / 5, ny / 5))
                    x, y = nx, ny


def render_with_tk(command_sets: list[PathCommands]) -> None:
    root = Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    sketch = Sketchpad(root, command_sets)
    sketch.grid(column=0, row=0, sticky="nswe")
    print("HELLO I AM MAINLOOP")
    root.mainloop()
