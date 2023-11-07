from functools import partial
from typing import Callable, Protocol, Self
from theory.functor import Functor

class Applicative[T](Functor, Protocol):
    @classmethod
    def pure[T](cls, value: T) -> Self:
        ...

    def apply[T, S, E](self, f: Self) -> Self:
        ...

    def map2[T, S, U](self, s: Self, f: Callable[[T, S], U]) -> Self:
        return s.apply(self.map(lambda ts: partial(f, ts)))
