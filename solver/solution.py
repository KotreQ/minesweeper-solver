from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Solution:
    mines_used: int
    placement_count: dict[tuple[int, int], int] | dict[int, int]
    all_placements: int

    def serialize(self) -> dict[str, Any]:
        # Keys are emitted as [key, count] pairs because JSON object keys cannot
        # be tuples; tuple keys become JSON arrays.
        return {
            "mines_used": self.mines_used,
            "placement_count": [
                [list(variable) if isinstance(variable, tuple) else variable, count]
                for variable, count in self.placement_count.items()
            ],
            "all_placements": self.all_placements,
        }

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> "Solution":
        placement_count = {
            tuple(variable) if isinstance(variable, list) else variable: count
            for variable, count in data["placement_count"]
        }

        return cls(
            data["mines_used"],
            placement_count,
            data["all_placements"],
        )
