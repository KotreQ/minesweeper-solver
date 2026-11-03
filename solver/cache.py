from .constraint import Constraint
from .solution import Solution
from .canonicalization import canonicalize_constraints
from .utils.hashing import hash_jsonable


class CacheStorage:
    def __init__(self):
        self._cache: dict[bytes, list[Solution]] = {}

    def __contains__(self, key: bytes):
        return key in self._cache

    def __getitem__(self, key: bytes):
        return self._cache[key]

    def __setitem__(self, key: bytes, value: list[Solution]):
        self._cache[key] = value


CACHE_KEY_SIZE = 32

class MinesweeperSolutionsCache:
    def __init__(self):
        self._cache = CacheStorage()

    def get(self, constraints: list[Constraint]) -> list[Solution] | None:
        canon = canonicalize_constraints(constraints)

        cache_key = hash_jsonable(canon.cache_key, digest_size=CACHE_KEY_SIZE)

        if cache_key not in self._cache:
            return None

        canon_solutions = self._cache[cache_key]

        solutions = []
        for canon_solution in canon_solutions:
            solution = Solution(
                canon_solution.mines_used,
                {canon.canon2var[canon_var]: placement_count for canon_var, placement_count in canon_solution.placement_count.items()},
                canon_solution.all_placements
            )
            solutions.append(solution)

        return solutions

    def save(self, constraints: list[Constraint], solutions: list[Solution]):
        canon = canonicalize_constraints(constraints)

        cache_key = hash_jsonable(canon.cache_key, digest_size=CACHE_KEY_SIZE)

        canon_solutions = []
        for solution in solutions:
            canon_solution = Solution(
                solution.mines_used,
                {canon.var2canon[var]: placement_count for var, placement_count in solution.placement_count.items()},
                solution.all_placements
            )
            canon_solutions.append(canon_solution)

        self._cache[cache_key] = canon_solutions
