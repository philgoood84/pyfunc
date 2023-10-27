from typing import Callable, Protocol


class Semigroup[S](Protocol):
    def append[S](self, value: S) -> S:
        ...



