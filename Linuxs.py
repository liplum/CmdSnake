import curses

from Core import *
from Shared import *

"""
|---x--------->
| 0 1 2 3 4 5 6
y 1 2 3 4 5 6 7
| 2 3 4 5 6 7 8
v 3 4 5 6 7 8 9
"""


class LinuxCanvas(Canvas):
    def __init__(self, width: int, height: int, buffer: Buffer, dirty_marks: DirtyMarks):
        self._width = width
        self._height = height
        self.buffer: Buffer = buffer
        self.dirty_marks: DirtyMarks = dirty_marks

    @property
    def Width(self):
        return self._width

    @property
    def Height(self):
        return self._height

    def Char(self, x, y, char: str):
        self.buffer[y, x] = char
        self.dirty_marks[y] = True

    def Str(self, x, y, string: str):
        for i, char in enumerate(string):
            self.buffer[y, x + i] = char
        self.dirty_marks[y] = True


class LinuxRender(IRender):

    def OnResized(self):
        stdscr = curses.initscr()

    def Initialize(self):
        pass

    def CreateCanvas(self) -> LinuxCanvas:
        pass

    def Render(self, canvas: Canvas):
        if isinstance(canvas, LinuxCanvas):
            canvas.Buffer.SetConsoleActiveScreenBuffer()
