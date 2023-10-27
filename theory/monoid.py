from typing import Protocol
from theory.semigroup import Semigroup

class Monoid[T](Semigroup, Protocol):
    def empty() -> T:
        ...


