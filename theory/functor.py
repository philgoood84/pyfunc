from typing import Callable, Protocol, Self

class Functor[T](Protocol):

    def map[T, S](self, f: Callable[T, S]) -> Self:
        ...
