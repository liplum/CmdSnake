import calendar
import math
import os
import platform
import sys
import time
from datetime import datetime
from importlib import reload
from io import StringIO
from threading import RLock
from types import ModuleType
from typing import Dict, List, Tuple, Optional, TypeVar, Callable, Any, NoReturn, Collection, Iterable

system_type = platform.system()

clear_screen = None

T = TypeVar('T')
TK = TypeVar('TK')
TV = TypeVar('TV')


def all_file(folder) -> Iterable[str]:
    for root, ds, fs in os.walk(folder):
        for f in fs:
            yield f


def all_file_with_extension(folder, extension: str) -> Iterable[Tuple[str, str]]:
    """
    :return: (file name without extension , file name)
    """
    for root, ds, fs in os.walk(folder):
        for f in fs:
            n, e = os.path.splitext(f)
            if e == extension:
                yield n, f


def it_all_modules() -> Iterable[Tuple[str, ModuleType]]:
    for name, val in sys.modules.items():
        if isinstance(val, ModuleType):
            yield val.__name__, val


def all_modules() -> List[Tuple[str, ModuleType]]:
    return [t for t in it_all_modules()]


def get_module_by(name: str) -> Optional[ModuleType]:
    g = sys.modules
    if name in g:
        m = g[name]
        if isinstance(m, ModuleType):
            return m
    return None


def reload_module(module_name: str) -> bool:
    m = get_module_by(module_name)
    if m:
        reload(m)
        return True
    else:
        return False


def reload_all_modules():
    for name, module in all_modules():
        try:
            reload(module)
        except:
            pass


def nearest_prefect_square(num: int) -> int:
    return round(math.sqrt(num)) ** 2


def nearest_int_square_root(num: int) -> int:
    return round(math.sqrt(num))


def fill_2d_array(row: int, column: int, filler: Optional[T] = 0) -> List[List[Any]]:
    return [[filler for i in range(column)] for j in range(row)]


def gen_2d_array(row: int, column: int, getter: Callable[[], T]) -> List[List[Any]]:
    return [[getter() for i in range(column)] for j in range(row)]


def gen_2d_arrayX(row: int, column: int, gen: Callable[[int, int], T]) -> List[List[Any]]:
    return [[gen(j, i) for i in range(column)] for j in range(row)]


def find(li: [T], predicate: Callable[[T], bool]) -> Optional[T]:
    for item in li:
        if predicate(item):
            return item
    return None


def split_parent_path(path: str) -> List[str]:
    """
    "/p1\\p2\\p3/p4.txt" => ['/', '/p1', '/p1\\p2', '/p1\\p2\\p3', '/p1\\p2\\p3/p4.txt']
    """
    parent = path
    stack = [path]
    while True:
        if parent == "/" or parent == "\\" or parent == "":
            break
        parent, sub = os.path.split(parent)
        stack.append(parent)
    return stack[::-1]


def split_path(path: str) -> List[str]:
    """
    "/p1\\p2\\p3/p4.txt" => ['p1', 'p2', 'p3', 'p4.txt']
    """
    parent = path
    stack = []
    while True:
        if parent == "/" or parent == "\\" or parent == "":
            break
        parent, sub = os.path.split(parent)
        stack.append(sub)
    return stack[::-1]


def get_executed_path() -> Tuple[str, str]:
    """
    Gets the path of executed file(is always __file__)
    :return: (dir_path,file_path)
    """
    return os.path.split(os.path.abspath(sys.argv[0]))


def get(dic: Dict[TK, TV], key: TK) -> TV:
    if key in dic:
        return dic[key]
    else:
        return None


def get_at(li: List[T], index: int) -> T:
    if len(li) > index:
        return li[index]
    else:
        return None


def multiget(dic: Dict[TK, List[TV]], key: TK) -> List[TV]:
    if key in dic:
        li = dic[key]
        if isinstance(li, list):
            return li
        else:
            li = []
            dic[key] = li
            return li
    else:
        li = []
        dic[key] = li
        return li


def get_not_none_one(*args):
    """
    :param args:all selections
    :return: the first not none one otherwise None
    """
    for arg in args:
        if arg is not None:
            return arg
    return None


def not_none(*args) -> bool:
    for arg in args:
        if arg is None:
            return False
    return True


def all_none(*args) -> bool:
    for arg in args:
        if arg is not None:
            return False
    return True


def clear_screen_win():
    os.system("cls")


def clear_screen_linux():
    os.system("clear")


def lock(lock: RLock, func, *args, **kwargs):
    lock.acquire()
    _return = func(*args, **kwargs)
    lock.release()
    return _return


def get_cur_time_milisecs() -> int:
    return get_milisecs(time.time())


def get_milisecs(time) -> int:
    return int(round(time * 1000))


class clock:
    def __init__(self, tps: int):
        self.tps = tps
        self.interval = 1000 / tps
        self.last = None

    def delay(self):
        if self.last is None:
            self.last = get_cur_time_milisecs()
            return
        else:
            cur = get_cur_time_milisecs()
            real_interval = self.last - cur
            sleep_time = real_interval - self.interval
            self.last = cur
            if sleep_time > 0:
                time.sleep(float(sleep_time) / 1000)


def separate(text: str, separator: str, number: int = None, allow_emptychar: bool = True) -> List[str]:
    """

    :param text:
    :param separator:the character used to be separate.
    :param number:the max separation count.
    :param allow_emptychar:If true,it skips the empty char.Otherwise the item which result contains can be a empty char.
    :return:
    """
    if len(separator) > 1:
        raise ValueError(f"separator length is {len(separator)},it needs 1")
    total_len = len(text)
    if number is None or number < 0:
        number = total_len
    res = []
    temp = StringIO()
    char_count = 0
    finished = False
    if allow_emptychar:
        for char in text:
            if number <= 0:
                finished = True
                break
            char_count += 1
            if char == separator:
                cur = temp.getvalue()
                res.append(cur)
                number -= 1
                temp.close()

                temp = StringIO()
            else:
                temp.write(char)

        if not finished:
            cur = temp.getvalue()
            res.append(cur)
        else:
            rest_len = total_len - char_count
            if rest_len > 0:
                res.append(text[-rest_len:])

    else:  # not allow empty char
        for char in text:
            if number <= 0:
                finished = True
                break
            char_count += 1
            if char == separator:
                cur = temp.getvalue()
                if len(cur) > 0:
                    res.append(cur)
                    number -= 1
                    temp.close()
                    temp = StringIO()
            else:
                temp.write(char)

        cur = temp.getvalue()
        if not finished:
            if len(cur) > 0:
                res.append(cur)
        else:
            rest_len = total_len - char_count
            if rest_len > 0:
                res.append(text[-rest_len:])

    temp.close()
    return res


def compose(seq: Collection, connector: str = ",", pretreat=str, end: str = "") -> str:
    with StringIO() as temp:
        c = 0
        max_len = len(seq)
        if pretreat is None:
            for item in seq:
                c += 1
                temp.write(item)
                if c < max_len:
                    temp.write(connector)
        else:
            for item in seq:
                c += 1
                res = pretreat(item)
                if not isinstance(res, str):
                    res = str(res)
                temp.write(res)
                if c < max_len:
                    temp.write(connector)
        temp.write(end)
        return temp.getvalue()


def chain(seq: Iterable[str]) -> str:
    with StringIO() as res:
        for ch in seq:
            res.write(ch)
        return res.getvalue()


def get_mid(a: int, b: int) -> int:
    return int((a + b) / 2)


def find_range(sequential: [], item, offset: int = 0) -> Tuple[int, int]:
    seql = len(sequential)
    rest = seql - offset
    if rest < 0:
        raise ValueError(f"offset is {offset} and greater than whole's length")
    if rest == 1:
        return offset, offset
    else:
        lefti = offset
        righti = seql - 1
        if item <= sequential[lefti]:
            return lefti, lefti
        if item >= sequential[righti]:
            return righti, righti

        while lefti < righti:
            midi = get_mid(lefti, righti)
            mid = sequential[midi]
            if item < mid:
                righti = midi
            elif item > mid:
                lefti = midi
            else:
                return midi, midi
            if lefti + 1 == righti:
                return lefti, righti


def addmultidic(dic: Dict, key, item) -> Dict:
    li = get(dic, key)
    if isinstance(li, list):
        li.append(item)
    else:
        dic[key] = [item]
    return dic


def fill(text: str, repeated: str, count: int, max_char_num: Optional[int] = None) -> str:
    repeatedl = len(repeated)
    if repeatedl == 0:
        raise ValueError("repeated cannot be an empty string.")
    textl = len(text)
    if max_char_num is not None and textl >= max_char_num:
        return text

    with StringIO() as s:
        s.write(text)
        total = textl
        if max_char_num is not None:
            restl = max_char_num - textl
            restc = min(count, restl // repeatedl)
        else:
            restc = count
        while restc > 0:
            s.write(repeated)
            total += repeatedl
            restc -= 1

        return s.getvalue()


def repeatIO(IO, repeated: str, times: int) -> NoReturn:
    if times <= 0:
        return
    for i in range(times):
        IO.write(repeated)


def repeat(repeated: str, times: int) -> str:
    if times <= 0:
        return ''
    with StringIO() as s:
        for i in range(times):
            s.write(repeated)
        return s.getvalue()


def is_in(item, li: Collection, equals: Optional[Callable[[Any, Any], bool]] = None) -> bool:
    if equals:
        for i in li:
            if equals(item, i) and equals(i, item):
                return True
        return False
    else:
        for i in li:
            if item == i and i == item:
                return True
        return False


def fillto(text: str, repeated: str, max_char_num: int) -> str:
    repeatedl = len(repeated)
    if repeatedl == 0:
        raise ValueError("repeated cannot be an empty string.")
    textl = len(text)
    if textl >= max_char_num:
        return text
    with StringIO() as s:
        s.write(text)
        total = textl
        restl = max_char_num - textl
        restc = restl // repeatedl
        surplus = restl % repeatedl

        while restc > 0:
            s.write(repeated)
            total += repeatedl
            restc -= 1

        if surplus > 0:
            s.write(repeated[0:surplus])

        return s.getvalue()


def split_strip(s: str, by: str) -> List[str]:
    parts = s.split(by)
    res = []
    for p in parts:
        res.append(p.strip())
    return res


def local_to_utc(dt: datetime):
    secs = time.mktime(dt.timetuple())
    return time.gmtime(secs)


def to_seconds(dt: datetime):
    secs = time.mktime(dt.timetuple())
    return calendar.timegm(time.gmtime(secs))


def now_milisecs() -> int:
    return int(round(time.time() * 1000))


if system_type == "Windows":
    clear_screen = clear_screen_win
elif system_type == "Linux":
    clear_screen = clear_screen_linux
