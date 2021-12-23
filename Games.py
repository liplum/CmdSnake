from collections import deque, namedtuple
from enum import Enum, auto
from typing import List, TypeVar, Deque, Iterator, Dict, Set, Any, Callable

import utils
from Core import *

T = TypeVar("T")
Array2D = List[List[Optional[T]]]
import random
from events import event


def Gen2DArray(row, column, init: T) -> Array2D:
    return [[init for r in range(row)] for c in range(column)]


class Tickable:
    def __init__(self, game_manager: "Game"):
        self.ticks = 0
        self.GameManager: "Game" = game_manager
        self._onRemoved = event()
        self._onAdded = event()
        self.IsActive = True

    def Initialize(self):
        self.IsActive = True
        self.GameManager.AddTickable(self)
        self.OnRemoved(self)

    def Tick(self):
        self.ticks += 1

    def Destroy(self):
        self.GameManager.Remove(self)
        self.IsActive = False
        self.OnRemoved(self)

    @property
    def OnRemoved(self):
        """
        Para 1:tickable object

        :return: event(Tickable)
        """
        return self._onRemoved

    @property
    def OnAdded(self):
        """
        Para 1:tickable object

        :return: event(Tickable)
        """
        return self._onAdded


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


AllDirections = (
    Direction.Left,
    Direction.Right,
    Direction.Up,
    Direction.Down
)

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
        if self.ticks % 20 == 1:
            gm = self.GameManager
            xw = random.randint(0, gm.Width - 1)
            xh = random.randint(0, gm.Height - 1)
            food = None
            t = random.randint(0, 100)
            if 0 <= t < 5:
                mm = random.randint(1, 10)
                cdm = random.randint(20, 100)
                food = Bird(gm, xw, xh,changeDireM=cdm,moveM=mm)
            elif t < 15:
                rate_motivation = random.randint(1, 50)
                food = Rate(gm, xw, xh, motivation=rate_motivation)
            else:
                ok = random.randint(0, 3)
                if ok == 0:
                    food = Toad(gm, xw, xh)
            if food:
                food.Initialize()
                gm.AddGameObj(food)


class Food(GameUnit):

    def __init__(self, game_manager: "Game", bonus, x=0, y=0):
        super().__init__(game_manager, x, y)
        self.Bonus = bonus
        self.viewer = Viewer()

    def OnEaten(self, snake: "Snake"):
        pass

    def OnSpawn(self, snake: "Snake"):
        pass

    def OnCollided(self, obj: "GameUnit"):
        if isinstance(obj, Snake):
            if obj.Head.IsCollidedWith(self):
                obj.Score += self.Bonus
                self.OnEaten(obj)
                self.Destroy()


class Toad(Food):

    def __init__(self, game_manager: "Game", x=0, y=0):
        super().__init__(game_manager, 3, x, y)

    def PaintOn(self, canvas: Canvas):
        v = self.viewer
        v.Bind(canvas)
        v.X = self.x
        v.Y = self.y
        v.Width = 1
        v.Height = 1
        v.Char(0, 0, "X")

    def OnEaten(self, snake: "Snake"):
        snake.AddBody()


class Rate(Food):

    def __init__(self, game_manager: "Game", x=0, y=0, motivation=10):
        super().__init__(game_manager, 5, x, y)
        self.Motivation = motivation

    def PaintOn(self, canvas: Canvas):
        v = self.viewer
        v.Bind(canvas)
        v.X = self.x
        v.Y = self.y
        v.Width = 1
        v.Height = 1
        v.Char(0, 0, "L")

    def Tick(self):
        super().Tick()
        rt = random.randint(1, self.Motivation)
        if self.ticks % rt == 0:
            dire = random.choice(AllDirections).value
            self.x += dire.x
            self.y += dire.y
            x = self.x
            y = self.y
            gm = self.GameManager
            if x < 0 or x > gm.Width or y < 0 or y > gm.Height:
                self.Destroy()
            self.GameManager.MarkDirty()

    def OnEaten(self, snake: "Snake"):
        snake.AddBody()
        snake.AddBody()


class Bird(Food):
    """
    ^-^
    """

    def __init__(self, game_manager: "Game", x=0, y=0, changeDireM=20, moveM=5):
        super().__init__(game_manager, 10, x, y)
        self.Direction = Direction.Right.value
        self.ChangeDireM = changeDireM
        self.MoveM = moveM

    def PaintOn(self, canvas: Canvas):
        v = self.viewer
        v.Bind(canvas)
        v.X = self.x
        v.Y = self.y
        v.Width = 3
        v.Height = 1
        v.Str(0, 0, "^-^")

    def RandomDirection(self):
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        self.Direction = Vector(dx, dy)

    def Tick(self):
        super().Tick()
        rt = random.randint(1, self.ChangeDireM)
        if self.ticks % rt == 0:
            self.RandomDirection()
        mt = random.randint(1, self.MoveM)
        if self.ticks % mt == 0:
            dire = self.Direction
            self.x += dire.x
            self.y += dire.y
            x = self.x
            y = self.y
            gm = self.GameManager
            if x < 0 or x > gm.Width or y < 0 or y > gm.Height:
                self.Destroy()
            self.GameManager.MarkDirty()

    def OnEaten(self, snake: "Snake"):
        snake.AddBody()
        snake.AddBody()
        snake.AddBody()


class Snake(GameUnit):
    def __init__(self, game_manager: "Game", board: Board, x: int, y: int, length: int):
        super().__init__(game_manager, x, y)
        self.Head: Head = Head(game_manager, x, y)
        self.Board: Board = board
        self.Bodies: Deque[Body] = deque([Body(game_manager, x - i - 1, y) for i in range(length)])
        self._direction: Direction = Direction.Right
        lastBody = self.Bodies[-1]
        self.LastBodyPos: Point = lastBody.x, lastBody.y
        self.Score = 0
        self._speed = 5
        self.viewer = Viewer()

    @property
    def AllParts(self) -> Iterator[Body]:
        yield self.Head
        for body in self.Bodies:
            yield body

    @property
    def HeadChar(self) -> str:
        return HeadChars[self.Direction]

    def PaintOn(self, canvas: Canvas):
        v = self.viewer
        v.Bind(canvas)
        v.X = 0
        v.Y = 0
        v.Width = canvas.Width
        v.Height = canvas.Height
        for b in self.Bodies:
            v.Char(b.x, b.y, "0")
        head = self.Head
        v.Char(head.x, head.y, self.HeadChar)

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
        score = self.Score
        if 0 < score < 10:
            self.Speed = 5
        elif score < 30:
            self.Speed = 4
        elif score < 40:
            self.Speed = 3
        elif score < 50:
            self.Speed = 2
        else:
            self.Speed = 1

        if self.ticks % self.Speed == 0:
            self.Move()
            self.GameManager.MarkDirty()

    @property
    def Speed(self) -> int:
        return self._speed

    @Speed.setter
    def Speed(self, value: int):
        self._speed = max(1, value)


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
        self.dirty = True
        self.GameObjects: Set[GameUnit] = set()
        self.TickableObjects: Set[Tickable] = set()
        self.Board: Board = Board(self, width, height)
        self.Snake: Snake = Snake(self, self.Board, width // 2, height // 2, 7)
        self.OperationQueue: Deque[Operation] = deque()
        self.Snake.Initialize()

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
