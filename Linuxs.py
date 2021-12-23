import curses
import os
from curses import window
from typing import Optional, Tuple
from typing import Iterable

import numpy as np

import utils
from Core import *
from Shared import *

"""
|---x--------->
| 0 1 2 3 4 5 6
y 1 2 3 4 5 6 7
| 2 3 4 5 6 7 8
v 3 4 5 6 7 8 9
"""


def GetWinsize() -> Tuple[int, int]:
    return os.get_terminal_size()


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
        if 0 <= x < self.Width and 0 <= y < self.Height:
            self.buffer[y, x] = char
            self.dirty_marks[y] = True

    def Str(self, x, y, string: Iterable[str]):
        width = self.Width
        height = self.Height
        buffer = self.buffer
        marks = self.dirty_marks
        for i, char in enumerate(string):
            nx = x + i
            if 0 <= nx < width and 0 <= y < height:
                buffer[y, nx] = char
        if 0 <= y < height:
            marks[y] = True

    def Color(self, x: int, y: int, color):
        pass

    def Colors(self, x1: int, x2: int, y1: int, y2: int, color):
        pass


class LinuxRender(IRender):

    def __init__(self):
        self.CharMatrix: Optional[ndarray] = None
        self.DirtyMarks: Optional[ndarray] = None
        self.Screen: Optional[window] = None
        self.NeedRegen = True
        self.width: int = 0
        self.height: int = 0

    def RegenScreen(self):
        scr = curses.initscr()
        self.Screen = scr
        curses.noecho()
        curses.cbreak()
        scr.keypad(True)
        scr.nodelay(True)
        scr.clear()
        size = GetWinsize()
        print(size)
        self.width = size.columns
        self.height = size.lines
        size = self.height, self.width
        heights = self.height,
        if not self.CharMatrix or self.CharMatrix.shape != size:
            self.CharMatrix = np.full(size, " ", dtype=str)
        if not self.DirtyMarks or self.DirtyMarks.shape != heights:
            self.DirtyMarks = np.full(heights, False, dtype=bool)
        self.NeedRegen = False

    def OnResized(self):
        self.NeedRegen = True

    def Initialize(self):
        pass

    def CreateCanvas(self) -> LinuxCanvas:
        if self.NeedRegen:
            self.RegenScreen()
        return LinuxCanvas(self.width, self.height, self.CharMatrix, self.DirtyMarks)

    def Render(self, canvas: Canvas):
        if isinstance(canvas, LinuxCanvas):
            cm = self.CharMatrix
            screen = self.Screen
            dm = self.DirtyMarks
            for i, dirty in enumerate(dm):
                if dirty:
                    line = utils.chain(Iterate2DRow(cm, i))
                    try:
                        screen.addstr(i, 0, line)
                    except:
                        pass
                    dm[i] = False
            screen.refresh()

    def Dispose(self):
        curses.endwin()
