from typing import Callable, List
import operator

def network4[T](_list: List[T], key: Callable[[T, T], bool] = operator.le) -> None:
    if key(_list[0], _list[2]):
        _list[0], _list[2] = _list[2], _list[0]
    if key(_list[1], _list[3]):
        _list[1], _list[3] = _list[3], _list[1]
    if key(_list[0], _list[1]):
        _list[0], _list[1] = _list[1], _list[0]
    if key(_list[2], _list[3]):
        _list[2], _list[3] = _list[3], _list[2]
    if key(_list[1], _list[2]):
        _list[1], _list[2] = _list[2], _list[1]

def networked4[T](_list: List[T], key: Callable[[T, T], bool] = operator.le) -> List[T]:
    _copy = _list.copy()
    network4(_copy, key)
    return _copy
