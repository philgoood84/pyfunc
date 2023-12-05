from typing import Protocol
from theory.semigroup import Semigroup

class Monoid[T](Semigroup, Protocol):
    @staticmethod
    def empty() -> T:
        ...


