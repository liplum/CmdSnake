import platform

sysinfo = platform.system()
from Core import *

render: IRender
if sysinfo == "Windows":
    import Windows
    import msvcrt

    getch = msvcrt.getwch
    can_get_ch = msvcrt.kbhit
    render = Windows.WinRender()
    c_left = 75
    c_right = 77
    c_down = 80
    c_up = 72

else:
    pass
from Games import *

import sys

args = sys.argv
if len(args) > 1 and args[1] == "x":
    input("Attach:")
from timers import timer

render.Initialize()
canvas = render.CreateCanvas()
game = Game(canvas.Width, canvas.Height)

rps = timer.byFps(60)
rps.reset()
c_q = ord("q")
lps = timer.byFps(20)
lps.reset()

OperationMap = {
    c_up: Operation.MoveUp,
    c_down: Operation.MoveDown,
    c_left: Operation.MoveLeft,
    c_right: Operation.MoveRight,
}

game.Initialize()
game.Speed = 5
while True:
    if can_get_ch():
        ch_num = ord(getch())
        if ch_num == 0xe0:
            ch_num = ord(getch())

        if ch_num == c_q:
            break
        elif ch_num in OperationMap:
            op = OperationMap[ch_num]
            game.AddOp(op)

    if lps.is_end:
        game.Tick()
        lps.reset()
    if rps.is_end and game.NeedRender:
        game.PaintOn(canvas)
        render.Render(canvas)
        rps.reset()
        game.ClearDirty()
