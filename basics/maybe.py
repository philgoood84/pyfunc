from dataclasses import dataclass
from functools import partial, wraps
from typing import Callable, Protocol, Never, Self

type Maybe[T] = Just[T] | Nothing

class _Protocol[T](Protocol):
    """Protocol to make Maybe a functor, applicative and monad
    Only pure, map, apply, and_then needs to be written
    Other utility functions are given freely from the four cited above
    Other utility functions need to be coded specialy for Maybe
    """
    @classmethod
    def pure[T](cls, value: T) -> Maybe[T]:
        ...
    
    def with_default[T](self, default: T) -> T:
        ...

    def is_nothing(self) -> bool:
        ...
    
    def map[T, S](self, f: Callable[T, S]) -> Maybe[T]:
        ...

    def apply[T, S](self, f: Maybe[Callable[T, S]]) -> Maybe[S]:
        ...

    def map2[T, S, U](self, s: Maybe[S], f: Callable[[T, S], U]) -> Maybe[U]:
        return s.apply(self.map(lambda t: partial(f, t)))

    def map3[T, S, U, V](self, s: Maybe[S], u: Maybe[U], f: Callable[[T, S, U], V]) -> Maybe[V]:
        return u.apply(self.map2(s, lambda ts, ss: partial(f, ts, ss)))

    def map4[T, S, U, V, W](self, s: Maybe[S], u: Maybe[U], v: Maybe[V], f: Callable[[T, S, U, V], W]) -> Maybe[W]:
        return v.apply(self.map3(s, u, lambda ts, ss, us: partial(f, ts, ss, us)))

    def and_then[T, S](self, f: Callable[T, Maybe[S]]) -> Maybe[S]:
        ...

    def join[T](self) -> Maybe[T]:
        ...

    def and_then2[T, S, U](self, s: Maybe[S], f: Callable[[T, S], Maybe[U]]) -> Maybe[U]:
        return self.map2(s, f).join()

    def and_then3[T, S, U, V](self, s: Maybe[S], u: Maybe[U], f: Callable[[T, S, U], Maybe[V]]) -> Maybe[V]:
        return self.map3(s, u, f).join()

    def and_then4[T, S, U, V, W](self, s: Maybe[S], u: Maybe[U], v: Maybe[V], f: Callable[[T, S, U, V], Maybe[W]]) -> Maybe[W]:
        return self.map4(s, u, v, f).join()

    def m_compose[T, S, U](self, f1: Callable[T, Maybe[S]], f2: Callable[S, Maybe[U]]) -> Maybe[U]:
        return self.and_then(f1).and_then(f2)

    def filter[T](self, predicate: Callable[T, bool]) -> Maybe[T]:
        ...

    def unwraps[T, S](self, func: Callable[T, S], default: [S]) -> S:
        ...

    def first(self, other: Maybe[T]) -> Maybe[T]:
        ...

    def last(self, other: Maybe[T]) -> Maybe[T]:
        ...

@dataclass(frozen=True)
class Just[T](_Protocol):
    """Just class to represent the existence of something
    implements pure, is_nothing, map, apply and and_then and some
    gets the other from the protocol freely
    """
    __slots__=('value',)
    value: T

    def __str__(self) -> str:
        return f"Just({self.value})"

    @classmethod
    def pure[T](cls, value: T) -> Maybe[T]:
        return cls(value= value)

    def with_default[T](self, default: T) -> T:
        return self.value

    def _is_nothing(self) -> bool:
        return False

    def map[T, S](self, f: Callable[T, S]) -> Maybe[S]:
        return Just.pure(f(self.value))

    def apply[T, S](self, f: Maybe[Callable[T, S]]) -> Maybe[S]:
        if f.is_nothing():
            return Nothing()
        return self.map(f.value)

    def and_then[T, S](self, f: Callable[T, Maybe[S]]) -> Maybe[S]:
        return f(self.value)

    def join[T](self) -> Maybe[T]:
        match self.value:
            case Nothing() | Just():
                return self.value.join()
            case _:
                return self

    def filter[T](self, predicate: Callable[T, bool]) -> Maybe[T]:
        if predicate(self.value):
            return self
        return Nothing()

    def unwraps[T, S](self, func: Callable[T, S], default: [S]) -> S:
        return func(self.value)

    def first[T](self, other: Maybe[T]) -> Maybe[T]:
        return self

    def last[T](self, other: Maybe[T]) -> Maybe[T]:
        if other.is_nothing():
            return self
        return other

@dataclass(frozen=True)
class Nothing(_Protocol):
    """Nothing class to represent the absence of something
    implements pure, is_nothing, map, apply, and and_then and some
    gets the others from the protocol freely
    """
    __slots__=()
    def __str__(self) -> str:
        return f"Nothing"

    @classmethod
    def pure[T](cls, value: T = None) -> Maybe[T]:
        return cls()

    def with_default[T](self, default: T) -> T:
        return default

    def is_nothing(self) -> bool:
        return True

    def map[T, S](self, f: Callable[T, S]) -> Maybe[S]:
        return Nothing()

    def apply[T, S](self, f: Maybe[Callable[T, S]]) -> Maybe[S]:
        return Nothing()

    def and_then[T, S](self, f: Callable[T, Maybe[S]]) -> Maybe[S]:
        return Nothing()

    def join[T](self) -> Maybe[T]:
        return Nothing()

    def filter[T](self, predicate: Callable[T, bool]) -> Maybe[T]:
        return Nothing()

    def unwraps[T, S](self, func: Callable[T, S], default: [S]) -> S:
        return default 

    def first[T](self, other: Maybe[T]) -> Maybe[T]:
        return other

    def last[T](self, other: Maybe[T]) -> Maybe[T]:
        return other

    
def as_maybe[**T, U](func):# -> Callable[[Callable[T, U]], Callable[T, Maybe[U]]]:
    """
    Make a decorator to transform ordinary functions that may return a None into a proper Maybe
    """
    @wraps(func)
    def wrapper[**T, U](*args: T.args, **kwargs: T.kwargs) -> Maybe[U]:
        res = func(*args, **kwargs)
        match res:
            case None:
                return Nothing()
            case _:
                return Just(res)
    return wrapper


