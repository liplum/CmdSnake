from typing import Optional

import numpy as np
import win32con
import win32console
from win32console import PyConsoleScreenBufferType, PyCOORDType

import utils
from Core import *
from Shared import *

XY = PyCOORDType
CSBuffer = PyConsoleScreenBufferType

"""
|---x--------->
| 0 1 2 3 4 5 6
y 1 2 3 4 5 6 7
| 2 3 4 5 6 7 8
v 3 4 5 6 7 8 9
"""


class WinCanvas(Canvas):
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


class WinRender(IRender):

    def __init__(self):
        super().__init__()
        self.CharMatrix: Optional[ndarray] = None
        self.DirtyMarks: Optional[ndarray] = None
        self.buffer: Optional[CSBuffer] = None
        self.width: int = 0
        self.height: int = 0
        self.NeedRegen = True

    def Initialize(self):
        pass

    def RegenBuffer(self):
        self.buffer = win32console.CreateConsoleScreenBuffer(
            DesiredAccess=win32con.GENERIC_READ | win32con.GENERIC_WRITE,
            ShareMode=0, SecurityAttributes=None, Flags=1)
        buf = self.buffer
        buf.SetConsoleActiveScreenBuffer()
        info = buf.GetConsoleScreenBufferInfo()
        size = info["Size"]
        self.width = size.X
        self.height = size.Y
        size = self.height, self.width
        heights = self.height,
        if not self.CharMatrix or self.CharMatrix.shape != size:
            self.CharMatrix = np.full(size, " ", dtype=str)
        if not self.DirtyMarks or self.DirtyMarks.shape != heights:
            self.DirtyMarks = np.full(heights, False, dtype=bool)
        self.NeedRegen = False

    def OnResized(self):
        self.NeedRegen = True

    def CreateCanvas(self) -> WinCanvas:
        if self.NeedRegen:
            self.RegenBuffer()
        return WinCanvas(self.width, self.height, self.CharMatrix, self.DirtyMarks)

    def Render(self, canvas: Canvas):
        if isinstance(canvas, WinCanvas):
            cm = self.CharMatrix
            buf = self.buffer
            dm = self.DirtyMarks
            for i, dirty in enumerate(dm):
                if dirty:
                    line = utils.chain(Iterate2DRow(cm, i))
                    buf.WriteConsoleOutputCharacter(
                        line, XY(0, i)
                    )
                    dm[i] = False

    def Dispose(self):
        pass
