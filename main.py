import platform

sysinfo = platform.system()
from Core import *

render: IRender
if sysinfo == "Windows":
    import Windows
    import msvcrt

    def getch():
        ch_num = ord(msvcrt.getwch())
        if ch_num == 0xe0:
            ch_num = ord(msvcrt.getwch())
        return ch_num
    can_get_ch = msvcrt.kbhit
    render = Windows.WinRender()
    c_left = 75
    c_right = 77
    c_down = 80
    c_up = 72
    c_q = ord('q')
else:
    import Linuxs
    import curses
    render: Linuxs.LinuxRender = Linuxs.LinuxRender()


    def getch():
        try:
            return render.Screen.get_wch()
        except:
            return None


    can_get_ch = lambda: True
    c_left = curses.KEY_LEFT
    c_right = curses.KEY_RIGHT
    c_down = curses.KEY_DOWN
    c_up = curses.KEY_UP
    c_q = ord('q')

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
lps = timer.byFps(20)
lps.reset()

OperationMap = {
    c_up: Operation.MoveUp,
    c_down: Operation.MoveDown,
    c_left: Operation.MoveLeft,
    c_right: Operation.MoveRight,
}

game.Initialize()
try:
    while True:
        if can_get_ch():
            ch_num = getch()
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
finally:
    render.Dispose()
