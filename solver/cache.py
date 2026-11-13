import sqlite3
from collections import defaultdict
from pathlib import Path

from .constraint import Constraint
from .solution import Solution
from .canonicalization import canonicalize_constraints
from .utils.hashing import hash_jsonable


# Resolved from this file's physical location rather than cwd or the import name,
# so every import structure (package import, direct script run, symlink) uses the
# same folder. `resolve()` also collapses symlinks to the real path.
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
CACHE_DB_NAME = "solutions.db"

SCHEMA_VERSION = 1


class CacheStorage:
    def __init__(self, directory: Path = CACHE_DIR):
        self._directory = Path(directory)
        self._directory.mkdir(parents=True, exist_ok=True)

        self._db_path = self._directory / CACHE_DB_NAME
        self._connection = sqlite3.connect(self._db_path)
        self._connection.execute("PRAGMA foreign_keys = ON")
        self.__create_schema()

    def __create_schema(self):
        version = self._connection.execute("PRAGMA user_version").fetchone()[0]
        if version != SCHEMA_VERSION:
            # The cache is regenerable, so an incompatible layout (including the
            # old single-table JSON blob schema) is simply dropped and rebuilt.
            self._connection.executescript(
                """
                DROP TABLE IF EXISTS placement_counts;
                DROP TABLE IF EXISTS solutions;
                DROP TABLE IF EXISTS solution_sets;
                """
            )
            self._connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

        # One row per cached constraint set. Kept separate from `solutions` so a
        # set that solved to zero solutions is still remembered as cached.
        # `placement_counts` is one row per (solution, canonical variable) pair;
        # variables are stored as the canonicalized integer indices produced by
        # `canonicalize_constraints`.
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS solution_sets (
                key BLOB PRIMARY KEY
            );

            CREATE TABLE IF NOT EXISTS solutions (
                key BLOB NOT NULL,
                solution_index INTEGER NOT NULL,
                mines_used INTEGER NOT NULL,
                all_placements INTEGER NOT NULL,
                PRIMARY KEY (key, solution_index),
                FOREIGN KEY (key) REFERENCES solution_sets(key) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS placement_counts (
                key BLOB NOT NULL,
                solution_index INTEGER NOT NULL,
                variable INTEGER NOT NULL,
                count INTEGER NOT NULL,
                PRIMARY KEY (key, solution_index, variable),
                FOREIGN KEY (key, solution_index) REFERENCES solutions(key, solution_index) ON DELETE CASCADE
            );
            """
        )
        self._connection.commit()

    def get(self, key: bytes) -> list[Solution] | None:
        exists = self._connection.execute(
            "SELECT 1 FROM solution_sets WHERE key = ?", (key,)
        ).fetchone()
        if exists is None:
            return None

        solution_rows = self._connection.execute(
            """
            SELECT solution_index, mines_used, all_placements
            FROM solutions
            WHERE key = ?
            ORDER BY solution_index
            """,
            (key,),
        ).fetchall()

        placements: dict[int, list[tuple[int, int]]] = defaultdict(list)
        for solution_index, variable, count in self._connection.execute(
            """
            SELECT solution_index, variable, count
            FROM placement_counts
            WHERE key = ?
            """,
            (key,),
        ):
            placements[solution_index].append((variable, count))

        return [
            Solution.deserialize(
                {
                    "mines_used": mines_used,
                    "all_placements": all_placements,
                    "placement_count": placements.get(solution_index, []),
                }
            )
            for solution_index, mines_used, all_placements in solution_rows
        ]

    def save(self, key: bytes, solutions: list[Solution]):
        with self._connection:
            self._connection.execute(
                "INSERT INTO solution_sets (key) VALUES (?) ON CONFLICT(key) DO NOTHING",
                (key,),
            )
            # Replacing the set; the cascade clears its old solutions and placements.
            self._connection.execute("DELETE FROM solutions WHERE key = ?", (key,))

            for solution_index, solution in enumerate(solutions):
                data = solution.serialize()

                self._connection.execute(
                    """
                    INSERT INTO solutions (key, solution_index, mines_used, all_placements)
                    VALUES (?, ?, ?, ?)
                    """,
                    (key, solution_index, data["mines_used"], data["all_placements"]),
                )
                self._connection.executemany(
                    """
                    INSERT INTO placement_counts
                        (key, solution_index, variable, count)
                    VALUES (?, ?, ?, ?)
                    """,
                    [
                        (key, solution_index, variable, count)
                        for variable, count in data["placement_count"]
                    ],
                )

    def close(self):
        self._connection.close()


CACHE_KEY_SIZE = 32

class MinesweeperSolutionsCache:
    def __init__(self):
        self._cache = CacheStorage()

    def get(self, constraints: list[Constraint]) -> list[Solution] | None:
        canon = canonicalize_constraints(constraints)

        cache_key = hash_jsonable(canon.cache_key, digest_size=CACHE_KEY_SIZE)

        canon_solutions = self._cache.get(cache_key)
        if canon_solutions is None:
            return None

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

        self._cache.save(cache_key, canon_solutions)
