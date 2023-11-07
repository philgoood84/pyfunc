# Test for the result container
from functools import partial
from basics.result import _Protocol, Result, Ok, Err, as_result
import operator as op
import pytest
from typing import Dict, Callable


def make_ok[T, E](value: T) -> Result[T, E]:
    return Ok.pure(value)

def make_err[T, E](error: E) -> Result[T, E]:
    return Err.pure(error)

def test_ok() -> None:
    ok = make_ok(2)
    assert ok.value == 2

def _test_pure[T, E](m: _Protocol[T], value: T) -> Result[T, E]:
    return type(m).pure(value)

def _test_map[T, S, E](m: _Protocol[T], f: Callable[T, S]) -> Result[S, E]:
    return m.map(f)

def _test_apply[T, S, E](m: _Protocol[T], mf: _Protocol[Callable[T, S]]) -> Result[S, E]:
    return m.apply(mf)

def is_err[T, E](m: _Protocol[T]) -> bool:
    return m.is_err()

def stringify[T](value: T) -> str:
    return f"{value}"

def test_ok_protocols() -> None:
    two = make_ok(2)
    three = make_ok(3)
    five = make_ok(5)
    ten = make_ok(10)
    err = make_err(ZeroDivisionError)
    assert two == _test_pure(two, 2)

    ok_string = make_ok('2')
    assert ok_string == _test_map(two, stringify)
    with pytest.raises(TypeError):
        instance: Result[int] = two.map(lambda x: x + 'z')

    assert not is_err(two)

    assert two.apply(make_ok(stringify)) == ok_string
    assert is_err(two.apply(make_err(stringify)))

    assert two.map2(three, op.add) == five
    assert is_err(two.map2(err, op.add))

    assert two.map3(three, five, lambda x, y, z: x + y + z) == ten
    assert two.map4(three, five, ten, lambda x, y, z, a: x + y + z + a) == make_ok(20)


def test_err_protocol() -> None:
    two = make_ok(2)
    three = make_ok(3)
    five = make_ok(5)
    ten = make_ok(10)
    err = make_err(ZeroDivisionError)
    assert err == _test_pure(err, ZeroDivisionError)

    assert is_err(err)

    assert is_err(err.map(stringify))

    assert is_err(err.apply(make_ok(stringify)))
    assert is_err(err.apply(make_err(stringify)))

    assert is_err(err.map2(two, op.add))

    assert is_err(two.map3(two, err, lambda x, y, z: x + y + z))
    assert is_err(two.map3(err, two, lambda x, y, z: x + y + z))
    assert is_err(err.map3(two, two, lambda x, y, z: x + y + z))

    assert is_err(err.map4(three, five, ten, lambda x, y, z, a: x + y + z + a))
    assert is_err(two.map4(err, five, ten, lambda x, y, z, a: x + y + z + a))
    assert is_err(two.map4(three, err, ten, lambda x, y, z, a: x + y + z + a))
    assert is_err(two.map4(three, five, err, lambda x, y, z, a: x + y + z + a))


def test_decorator_and_and_then() -> None:
    dict_test: Dict[str, int] = {'a': 12, 'b': 15}
    safe_get = as_result(ZeroDivisionError)(Dict.get)
    assert safe_get(dict_test, 'a').value == 12
    assert is_err(safe_get(dict_test, 'c'))

    @as_result
    def _safe_get(key: str) -> Result[int]:
        return dict_test.get(key)

    key = make_ok('a')
    wrong_key = make_ok('c')
    err = make_err()
    assert key.and_then(_safe_get) == make_ok(12)
    assert is_err(wrong_key.and_then(_safe_get))
    assert is_err(err.and_then(_safe_get))


    another_dict: Dict[int, str] = {12: 'a', 15: 'b'} 
    @as_result
    def _safe_get2(key: int) -> Result[str]:
        return another_dict.get(key)

    assert key.m_compose(_safe_get, _safe_get2) == key
    assert is_err(err.m_compose(_safe_get, _safe_get2))
    assert is_err(wrong_key.m_compose(_safe_get, _safe_get2))

    assert Ok.pure(Ok.pure(2)).join() == Ok.pure(2)
    assert is_err(Ok.pure(Err.pure()).join())
    assert is_err(Err.pure(Ok.pure(2)).join())
    assert is_err(Err.pure(Err.pure()).join())


    assert Ok.pure(dict_test).and_then2(key, safe_get) == Ok.pure(12)
