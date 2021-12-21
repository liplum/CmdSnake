from typing import Iterable

from numpy import ndarray

Buffer = ndarray
DirtyMarks = ndarray


def Iterate2DRow(array2D: ndarray, row_index: int) -> Iterable:
    column = array2D.shape[1]
    for j in range(column):
        yield array2D[row_index, j]


def Iterate2DColumn(array2D: ndarray, column_index: int) -> Iterable:
    row = array2D.shape[0]
    for j in range(row):
        yield array2D[i, column_index]