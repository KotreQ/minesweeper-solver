import json
import os
from pathlib import Path

from .constraint import Constraint
from .solution import Solution
from .canonicalization import canonicalize_constraints
from .utils.hashing import hash_jsonable


# Resolved from this file's physical location rather than cwd or the import name,
# so every import structure (package import, direct script run, symlink) uses the
# same folder. `resolve()` also collapses symlinks to the real path.
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"


class CacheStorage:
    def __init__(self, directory: Path = CACHE_DIR):
        self._directory = Path(directory)
        self._cache: dict[bytes, list[Solution]] = {}
        self._directory.mkdir(parents=True, exist_ok=True)
        self.__load_cache()

    def __contains__(self, key: bytes):
        return key in self._cache

    def __getitem__(self, key: bytes):
        return self._cache[key]

    def __setitem__(self, key: bytes, value: list[Solution]):
        self._cache[key] = value
        self.__save_cache(key)

    def __path_for(self, key: bytes) -> Path:
        return self._directory / f"{key.hex()}.json"

    def __load_cache(self):
        for path in self._directory.glob("*.json"):
            try:
                key = bytes.fromhex(path.stem)
                payload = json.loads(path.read_text(encoding="utf-8"))

                if payload.get("key") != key.hex():
                    continue

                self._cache[key] = [Solution.deserialize(item) for item in payload["solutions"]]
            except (OSError, ValueError, KeyError, TypeError):
                # Ignore corrupted or foreign files instead of failing the whole load.
                continue

    def __save_cache(self, key: bytes):
        payload = {
            "key": key.hex(),
            "solutions": [solution.serialize() for solution in self._cache[key]],
        }

        path = self.__path_for(key)
        tmp_path = path.with_name(f"{path.name}.tmp")

        tmp_path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
        os.replace(tmp_path, path)  # atomic on POSIX, avoids half-written entries


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
