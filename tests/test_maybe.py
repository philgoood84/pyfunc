# Test for the maybe container
from functools import partial
from basics.maybe import _Protocol, Maybe, Just, Nothing, as_maybe
import operator as op
import pytest
from typing import Dict, Callable



def make_just[T](value: T) -> Maybe[T]:
    return Just.pure(value)

def make_nothing[T](value: T = None) -> Maybe[T]:
    return Nothing()

def test_just() -> None:
    just = make_just(2)
    assert just.value == 2

def _test_pure[T](m: _Protocol[T], value: T) -> Maybe[T]:
    return type(m).pure(value)

def _test_map[T, S](m: _Protocol[T], f: Callable[T, S]) -> Maybe[S]:
    return m.map(f)

def _test_apply[T, S](m: _Protocol[T], mf: _Protocol[Callable[T, S]]) -> Maybe[S]:
    return m.apply(mf)

def is_nothing[T](m: _Protocol[T]) -> bool:
    return m.is_nothing()

def stringify[T](value: T) -> str:
    return f"{value}"

def test_just_protocols() -> None:
    two = make_just(2)
    three = make_just(3)
    five = make_just(5)
    ten = make_just(10)
    nothing = make_nothing()
    assert two == _test_pure(two, 2)

    just_string = make_just('2')
    assert just_string == _test_map(two, stringify)
    with pytest.raises(TypeError):
        instance: Maybe[int] = two.map(lambda x: x + 'z')

    assert not is_nothing(two)

    assert two.apply(make_just(stringify)) == just_string
    assert is_nothing(two.apply(make_nothing(stringify)))

    assert two.map2(three, op.add) == five
    assert is_nothing(two.map2(nothing, op.add))

    assert two.map3(three, five, lambda x, y, z: x + y + z) == ten
    assert two.map4(three, five, ten, lambda x, y, z, a: x + y + z + a) == make_just(20)


def test_nothing_protocol() -> None:
    two = make_just(2)
    three = make_just(3)
    five = make_just(5)
    ten = make_just(10)
    nothing = make_nothing()
    assert nothing == _test_pure(nothing, 2)

    assert is_nothing(nothing)

    assert is_nothing(nothing.map(stringify))

    assert is_nothing(nothing.apply(make_just(stringify)))
    assert is_nothing(nothing.apply(make_nothing(stringify)))

    assert is_nothing(nothing.map2(two, op.add))

    assert is_nothing(two.map3(two, nothing, lambda x, y, z: x + y + z))
    assert is_nothing(two.map3(nothing, two, lambda x, y, z: x + y + z))
    assert is_nothing(nothing.map3(two, two, lambda x, y, z: x + y + z))

    assert is_nothing(nothing.map4(three, five, ten, lambda x, y, z, a: x + y + z + a))
    assert is_nothing(two.map4(nothing, five, ten, lambda x, y, z, a: x + y + z + a))
    assert is_nothing(two.map4(three, nothing, ten, lambda x, y, z, a: x + y + z + a))
    assert is_nothing(two.map4(three, five, nothing, lambda x, y, z, a: x + y + z + a))


def test_decorator_and_and_then() -> None:
    dict_test: Dict[str, int] = {'a': 12, 'b': 15}
    safe_get = as_maybe(Dict.get)
    assert safe_get(dict_test, 'a').value == 12
    assert is_nothing(safe_get(dict_test, 'c'))

    @as_maybe
    def _safe_get(key: str) -> Maybe[int]:
        return dict_test.get(key)

    key = make_just('a')
    wrong_key = make_just('c')
    nothing = make_nothing()
    assert key.and_then(_safe_get) == make_just(12)
    assert is_nothing(wrong_key.and_then(_safe_get))
    assert is_nothing(nothing.and_then(_safe_get))


    another_dict: Dict[int, str] = {12: 'a', 15: 'b'} 
    @as_maybe
    def _safe_get2(key: int) -> Maybe[str]:
        return another_dict.get(key)

    assert key.m_compose(_safe_get, _safe_get2) == key
    assert is_nothing(nothing.m_compose(_safe_get, _safe_get2))
    assert is_nothing(wrong_key.m_compose(_safe_get, _safe_get2))

    assert Just.pure(Just.pure(2)).join() == Just.pure(2)
    assert is_nothing(Just.pure(Nothing.pure()).join())
    assert is_nothing(Nothing.pure(Just.pure(2)).join())
    assert is_nothing(Nothing.pure(Nothing.pure()).join())


    assert Just.pure(dict_test).and_then2(key, safe_get) == Just.pure(12)
