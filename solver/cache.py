from .constraint import Constraint
from .solution import Solution
from .csp import csp_bruteforce
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


class CspCacheManager:
    def __init__(self):
        self._cache = CacheStorage()

    def get_solutions(self, constraints: list[Constraint]) -> list[Solution]:
        canon = canonicalize_constraints(constraints)

        cache_key = hash_jsonable(canon.cache_key, digest_size=32).hex()

        if cache_key not in self._cache:
            canon_constraints = []
            for constraint in constraints:
                canon_vars = frozenset(canon.var2canon[var] for var in constraint.variables)
                canon_constraint = Constraint(constraint.value, canon_vars)
                canon_constraints.append(canon_constraint)

            canon_solutions = csp_bruteforce(canon_constraints)

            self._cache[cache_key] = canon_solutions

        else:
            canon_solutions = self._cache[cache_key]

        solutions = []
        for canon_solution in canon_solutions:
            solution = Solution(
                canon_solution.mines_used,
                {
                    canon.canon2var[canon_var]: placement_count
                    for canon_var, placement_count in canon_solution.placement_count.items()
                },
                canon_solution.all_placements
            )
            solutions.append(solution)

        return solutions