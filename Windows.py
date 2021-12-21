from typing import Optional

import numpy as np
import win32con
import win32console
from numpy import ndarray
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
        self.char_matrix: Optional[ndarray] = None
        self.dirty_marks: Optional[ndarray] = None
        self.buffer: Optional[CSBuffer] = None
        self.width: int = 0
        self.height: int = 0
        self.need_update = True

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
        if not self.char_matrix or self.char_matrix.shape != size:
            self.char_matrix = np.full(size, " ", dtype=str)
        if not self.dirty_marks or self.dirty_marks.shape != heights:
            self.dirty_marks = np.full(heights, False, dtype=bool)
        self.need_update = False

    def OnResized(self):
        self.need_update = True

    def CreateCanvas(self) -> WinCanvas:
        if self.need_update:
            self.RegenBuffer()
        return WinCanvas(self.width, self.height, self.char_matrix, self.dirty_marks)

    def Render(self, canvas: Canvas):
        if isinstance(canvas, WinCanvas):
            char_matrix = self.char_matrix
            buf = self.buffer
            dirty_marks = self.dirty_marks
            for i, dirty in enumerate(dirty_marks):
                if dirty:
                    strings = utils.chain(Iterate2DRow(char_matrix, i))
                    buf.WriteConsoleOutputCharacter(
                        strings, XY(0, i)
                    )
                    dirty_marks[i] = False
