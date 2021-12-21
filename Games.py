from collections import deque, namedtuple
from enum import Enum, auto
from typing import List, TypeVar, Optional, Deque, Iterator, Dict, Set, Any, Callable

import utils
from Core import *

T = TypeVar("T")
Array2D = List[List[Optional[T]]]
import random


def Gen2DArray(row, column, init: T) -> Array2D:
    return [[init for r in range(row)] for c in range(column)]


class Tickable:
    def __init__(self, game_manager: "Game"):
        self.ticks = 0
        self.GameManager: "Game" = game_manager
        self.IsActive = True

    def Tick(self):
        self.ticks += 1

    def Destroy(self):
        self.GameManager.Remove(self)
        self.IsActive = False


class GameUnit(Tickable, Painter):
    def __init__(self, game_manager: "Game", x=0, y=0):
        super().__init__(game_manager)
        self.x = x
        self.y = y

    def IsCollidedWith(self, obj: "GameUnit") -> bool:
        return obj.x == self.x and obj.y == self.y

    def OnCollided(self, obj: "GameUnit"):
        pass


class Board(Tickable, Painter):
    def __init__(self, game_manager: "Game", width, height):
        super().__init__(game_manager)
        self.Width = width
        self.Height = height
        self.Map = Gen2DArray(height, width, None)

    def PaintOn(self, canvas: Canvas):
        w = min(self.Width, canvas.Width)
        h = min(self.Height, canvas.Height)
        for j in range(h):
            canvas.Str(0, j, utils.repeat(" ", w))


class Body(GameUnit):
    pass


class Head(Body):
    pass


Point = namedtuple("Position", ["x", "y"])
Vector = namedtuple("Vector", ["x", "y"])


class Direction(Enum):
    Up = Vector(0, -1)
    Down = Vector(0, 1)
    Left = Vector(-1, 0)
    Right = Vector(1, 0)


HeadChars: Dict[Direction, str] = {
    Direction.Left: "<",
    Direction.Right: ">",
    Direction.Up: "▲",
    Direction.Down: "▼"
}

ContradictedDirections: Dict[Direction, Direction] = {
    Direction.Left: Direction.Right,
    Direction.Right: Direction.Left,
    Direction.Up: Direction.Down,
    Direction.Down: Direction.Up
}


class FoodManager(Tickable):

    def __init__(self, game_manager: "Game"):
        super().__init__(game_manager)

    def Tick(self):
        super().Tick()
        if self.ticks % 10 == 1:
            gm = self.GameManager
            xw = random.randint(0, gm.Width - 1)
            xh = random.randint(0, gm.Height - 1)
            gm.AddGameObj(Toad(gm, xw, xh))


class Food(GameUnit):

    def __init__(self, game_manager: "Game", x=0, y=0):
        super().__init__(game_manager, x, y)

    def OnEaten(self, snake: "Snake"):
        snake.AddBody()
        self.Destroy()

    def OnSpawn(self, snake: "Snake"):
        pass

    def OnCollided(self, obj: "GameUnit"):
        if isinstance(obj, Snake):
            self.OnEaten(obj)


class Toad(Food):

    def PaintOn(self, canvas: Canvas):
        canvas.Char(self.x, self.y, "X")


class Rate(Food):
    pass


class Snake(GameUnit):
    def __init__(self, game_manager: "Game", board: Board, x: int, y: int, length: int):
        super().__init__(game_manager, x, y)
        self.Head: Head = Head(game_manager, x, y)
        self.Board: Board = board
        self.Bodies: Deque[Body] = deque([Body(game_manager, x - i - 1, y) for i in range(length)])
        self._direction: Direction = Direction.Right
        lastBody = self.Bodies[-1]
        self.LastBodyPos: Point = lastBody.x, lastBody.y

    @property
    def AllParts(self) -> Iterator[Body]:
        yield self.Head
        for body in self.Bodies:
            yield body

    @property
    def HeadChar(self) -> str:
        return HeadChars[self.Direction]

    def PaintOn(self, canvas: Canvas):
        for b in self.Bodies:
            canvas.Char(b.x, b.y, "0")
        head = self.Head
        canvas.Char(head.x, head.y, self.HeadChar)

    def IsCollidedWith(self, obj: GameUnit) -> bool:
        for body in self.AllParts:
            if body.IsCollidedWith(obj):
                return True
        return False

    @property
    def Direction(self) -> Direction:
        return self._direction

    @Direction.setter
    def Direction(self, value: Direction):
        if self._direction != value and value != ContradictedDirections[self._direction]:
            self._direction = value

    def Move(self):
        dx = self.Direction.value.x
        dy = self.Direction.value.y
        head = self.Head
        ox = head.x
        oy = head.y
        lx = head.x + dx
        ly = head.y + dy
        head.x = lx
        head.y = ly
        board = self.Board
        if lx < 0:
            head.x = board.Width - 1
        elif lx > board.Width - 1:
            head.x = 0
        if ly < 0:
            head.y = board.Height - 1
        elif ly > board.Height - 1:
            head.y = 0

        self.x = head.x
        self.y = head.y
        tail = self.Bodies.pop()
        newBody = Body(self.GameManager, ox, oy)
        self.Bodies.appendleft(newBody)
        lastBody = self.Bodies[-1]
        self.LastBodyPos: Point = lastBody.x, lastBody.y

    def AddBody(self):
        x, y = self.LastBodyPos
        newBody = Body(self.GameManager, x - 1, y)
        self.Bodies.append(newBody)

    def Tick(self):
        super().Tick()
        if self.ticks % self.GameManager.Speed == 0:
            self.Move()
            self.GameManager.MarkDirty()


class Operation(Enum):
    MoveUp = auto()
    MoveDown = auto()
    MoveLeft = auto()
    MoveRight = auto()


class Game(Painter):
    def __init__(self, width, height):
        self.Width = width
        self.Height = height
        self.Tasks: Deque[Callable[[], None]] = deque()
        self.ticks = 0
        self._speed = 20
        self.dirty = True
        self.GameObjects: Set[GameUnit] = set()
        self.TickableObjects: Set[Tickable] = set()
        self.Board: Board = Board(self, width, height)
        self.Snake: Snake = Snake(self, self.Board, width // 2, height // 2, 7)
        self.OperationQueue: Deque[Operation] = deque()

    def Initialize(self):
        self.AddGameObj(self.Snake)
        self.AddTickable(self.Board)
        self.AddTickable(FoodManager(self))

    def Tick(self):
        self.ticks += 1
        self.HandleOp()
        for obj in self.TickableObjects:
            if obj.IsActive:
                obj.Tick()
        self.CheckCollide()
        self.HandleTasks()

    def HandleTasks(self):
        tasks = self.Tasks
        while len(tasks) > 0:
            task = tasks.popleft()
            task()

    def CheckCollide(self):
        allobjs = list(self.GameObjects)
        number = len(allobjs)
        max_index = number - 1
        for i in range(number):
            if i == max_index:
                break
            obj = allobjs[i]
            if not obj.IsActive:
                continue
            for j in range(i + 1, number):
                target = allobjs[j]
                if not target.IsActive:
                    continue
                if obj.IsCollidedWith(target) or target.IsCollidedWith(obj):
                    obj.OnCollided(target)
                    target.OnCollided(obj)

    @property
    def Ticks(self) -> int:
        return self.ticks

    @property
    def Speed(self) -> int:
        return self._speed

    @Speed.setter
    def Speed(self, value: int):
        self._speed = max(1, value)

    def HandleOp(self):
        queue = self.OperationQueue
        snake = self.Snake
        if len(queue) > 0:
            op = queue.pop()
            if op == Operation.MoveUp:
                snake.Direction = Direction.Up
            elif op == Operation.MoveDown:
                snake.Direction = Direction.Down
            elif op == Operation.MoveLeft:
                snake.Direction = Direction.Left
            elif op == Operation.MoveRight:
                snake.Direction = Direction.Right

    def AddOp(self, op: Operation):
        self.OperationQueue.append(op)

    def PaintOn(self, canvas: Canvas):
        self.Board.PaintOn(canvas)
        for obj in self.GameObjects:
            if obj.IsActive:
                obj.PaintOn(canvas)

    @property
    def NeedRender(self) -> bool:
        return self.dirty

    def MarkDirty(self):
        self.dirty = True

    def ClearDirty(self):
        self.dirty = False

    def AddGameObj(self, obj: GameUnit):
        def func():
            self.GameObjects.add(obj)
            self.TickableObjects.add(obj)
            obj.GameManager = self
            self.MarkDirty()

        self.Tasks.append(func)

    def AddTickable(self, obj: Tickable):
        def func():
            self.TickableObjects.add(obj)
            obj.GameManager = self
            self.MarkDirty()

        self.Tasks.append(func)

    def Remove(self, obj: Any):
        def func():
            if isinstance(obj, GameUnit):
                obj.IsActive = False
                self.GameObjects.remove(obj)
                self.TickableObjects.remove(obj)
            elif isinstance(obj, Tickable):
                obj.IsActive = False
                self.TickableObjects.remove(obj)
            self.MarkDirty()

        self.Tasks.append(func)
