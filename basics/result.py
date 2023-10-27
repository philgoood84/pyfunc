from dataclasses import dataclass
from typing import Callable

type Result[S, E] = Ok[S] | Err[E]

class _Protocol[T](Protocol):
    value: T

    @classmethod
    def pure[T, E](cls, value: T) -> Result[T, E]:
        ...

    def map[T, S, E](self, f: Callable[T, S]) -> Result[S, E]:
        ...

    def apply[T, S, E](self, rf: Result[Callable[T, S], E]) -> Result[S, E]:
        ...

    def map2[T, S, U, E](self, s: Result[S, E], f: Callable[[T, S], U]) -> Result[U, E]:
        return s.apply(self.map(lambda ts: partial(f, ts)))

    def map3[T, S, U, V, E](self, s: Result[S, E], u: Result[V, E], f: Callable[[T, S, U], V]) -> Result[V, E]:
        return u.apply(self.map2(lambda ts, ss: partial(f, ts, ss)))

    def map4[T, S, U, V, W, E](self, s: Result[S, E], u: Result[V, E], w: Result[W, E], f: Callable[[T, S, U, V], W]) -> Result[W, E]:
        return v.apply(self.map3(lambda ts, ss, us: partial(f, ts, ss, us)))

    def and_then[T, S, E](self, f: Callable[T, Result[S, E]]) -> Result[S, E]:
        ...
    
    def join[T, E](self) -> Result[T, E]:
        ...

    def m_compose[T, S, U, E](self, f1: Callable[T, Result[S, E]], f2: Callable[S, Result[U, E]]) -> Result[U, E]:
        return self.and_then(f1).and_then(f2)



@dataclass
class Ok[Success](_Protocol):
    __slots__ = ('value',)
    value: Success

    @classmethod
    def pure[Success, E](cls, value: Success) -> Result[Success, E]:
        return Ok(value= value)

    def map[Success, E](self, f: Callable[Success, T]) -> Result[T, E]:
        return Ok.pure(f(ok.value))

    def apply[Success, T, E](self, rf: Result[Callable[Success, T], E]) -> Result[T, E]:
        match rf:
            case Ok(value= f):
                return self.map(f)
            case Err():
                return rf

    def and_then[Success, T, E](self, f: Callable[Success, Result[T, E]]) -> Result[T, E]:
        return f(self.value)

    def join[Success, E](self):
        match self.value:
            case Ok() | Err():
                return self.value.join()
            case _:
                return self



class Err[Error: Exception](_Protocol):
    __slots__ = ('value',)
    value: Error

    @classmethod
    def pure[S, Error](cls, value: Error) -> Result[S, Error]:
        return Err(value)

    def map[Success, E](self, f: Callable[Success, T]) -> Result[T, E]:
        return self

    def apply[T, S, E](self, rf: Result[Callable[T, S], E]) -> Result[S, E]:
        return self

    def and_then(self, f: Callable[Success, Result[T, E]]) -> Result[T, E]:
        return self

    def join[T, Error](self):
        match self.value:
            case Ok():
                return self
            case Err():
                return self.value.join()
            case _:
                return self
