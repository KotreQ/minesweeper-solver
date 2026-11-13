from dataclasses import dataclass
from typing import Any


# A single placement row: (variable, count). `variable` is always the
# canonicalized integer index of the variable.
PlacementRow = tuple[int, int]


@dataclass(frozen=True, slots=True)
class Solution:
    mines_used: int
    placement_count: dict[tuple[int, int], int] | dict[int, int]
    all_placements: int

    def serialize(self) -> dict[str, Any]:
        # Only canonicalized solutions (integer indices, see cache.py) may be
        # serialized. int() also casts numpy scalars (e.g. np.int16) leaking in
        # from the grid.
        placement_count = []
        for variable, count in self.placement_count.items():
            if isinstance(variable, tuple):
                raise TypeError(
                    "Solution.serialize() requires canonicalized integer variables, "
                    f"got {variable!r}"
                )
            placement_count.append((int(variable), int(count)))

        return {
            "mines_used": int(self.mines_used),
            "all_placements": int(self.all_placements),
            "placement_count": placement_count,
        }

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> "Solution":
        placement_count = {
            variable: count for variable, count in data["placement_count"]
        }

        return cls(
            data["mines_used"],
            placement_count,
            data["all_placements"],
        )
