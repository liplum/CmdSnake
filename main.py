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

rps = timer.byFps(5)
rps.reset()
c_q = ord("q")
lps = timer.byFps(10)
lps.reset()

game.Initialize()
game.Speed = 3
while True:
    if can_get_ch():
        ch_num = ord(getch())
        if ch_num == 0xe0:
            ch_num = ord(getch())

        if ch_num == c_up:
            game.AddOp(Operation.MoveUp)
        elif ch_num == c_down:
            game.AddOp(Operation.MoveDown)
        elif ch_num == c_left:
            game.AddOp(Operation.MoveLeft)
        elif ch_num == c_right:
            game.AddOp(Operation.MoveRight)
        elif ch_num == c_q:
            break
    if lps.is_end:
        game.Tick()
        lps.reset()
    if rps.is_end and game.NeedRender:
        game.PaintOn(canvas)
        render.Render(canvas)
        rps.reset()
        game.ClearDirty()
