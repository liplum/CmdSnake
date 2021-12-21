class LinuxCanvas(Canvas):
    def __init__(self, width: int, height: int, buffer: CSBuffer):
        self._width = width
        self._height = height
        self._buffer: CSBuffer = buffer

    @property
    def Width(self):
        return self._width

    @property
    def Height(self):
        return self._height

    @property
    def Buffer(self) -> CSBuffer:
        return self._buffer

    def Char(self, x, y, char: str):
        pass

    def Str(self, x, y, string: str):
        pass


class LinuxRender(IRender):

    def CreateCanvas(self) -> WinCanvas:
        pass

    def Render(self, canvas: Canvas):
        if isinstance(canvas, LinuxRender):
            canvas.Buffer.SetConsoleActiveScreenBuffer()
