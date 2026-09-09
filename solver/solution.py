from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Solution:
    mines_used: int
    placement_count: dict[tuple[int, int], int] | dict[int, int]
    all_placements: int
