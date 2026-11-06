from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Solution:
    mines_used: int
    placement_count: dict[tuple[int, int], int] | dict[int, int]
    all_placements: int

    def serialize(self) -> dict[str, Any]:
        # int() casts numpy scalars (e.g. np.int16) leaking in from the grid,
        # which json.dumps cannot encode.
        # Keys are emitted as [key, count] pairs because JSON object keys cannot
        # be tuples; tuple keys become JSON arrays.
        return {
            "mines_used": int(self.mines_used),
            "placement_count": [
                [
                    [int(component) for component in variable]
                    if isinstance(variable, tuple)
                    else int(variable),
                    int(count),
                ]
                for variable, count in self.placement_count.items()
            ],
            "all_placements": int(self.all_placements),
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
