from typing import Protocol

class Semigroup[T](Protocol):
    def append(lhs: T, rhs: T) -> T:
        ...

