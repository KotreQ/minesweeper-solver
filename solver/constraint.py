from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Constraint:
    value: int
    variables: frozenset[tuple[int, int]] | frozenset[int]
