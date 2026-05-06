from .constraints import Constraint
from dataclasses import dataclass

from collections import defaultdict
from .unionfind import UnionFind
import numpy as np


@dataclass
class Solution:
    mines_used: int
    placement_count: dict[tuple[int, int], int]
    all_placements: int


def find_constraints_solutions(constraints: list[Constraint]):
    constraint_sets = find_disjoint_constraints(constraints)

    for constraint_set in constraint_sets:
        set_solutions = csp_bruteforce(constraint_set)


def csp_bruteforce(constraints: list[Constraint]) -> list[Solution]:
    all_indices = set()

    for c in constraints:
        all_indices.update(c.indices)
    
    all_indices = list(all_indices)
    N = len(all_indices)

    mines_left = [c.value for c in constraints]
    tiles_left = [len(c.indices) for c in constraints]

    idx_constraints = [[i for i, c in enumerate(constraints) if index in c.indices] for index in all_indices]  # which constraints are affected by indices

    cur_solution = np.zeros(N, np.bool_)

    solutions = defaultdict(lambda: np.zeros(N, np.uint64))  # {mines_used: [i: solutions_with_mines_on_i]}
    all_solutions = defaultdict(int)  # {mines_used: solution_count}

    mines_used = 0

    def csp(i):
        nonlocal mines_used
        
        if i == N:
            solutions[mines_used] += cur_solution
            all_solutions[mines_used] += 1
            return
        
        for c in idx_constraints[i]:
            tiles_left[c] -= 1

        # try True
        cur_solution[i] = True
        mines_used += 1
        for c in idx_constraints[i]:
            mines_left[c] -= 1
        
        if all(0 <= mines_left[c] <= tiles_left[c] for c in idx_constraints[i]):
            csp(i+1)
        
        # try False
        cur_solution[i] = False
        mines_used -= 1
        for c in idx_constraints[i]:
            mines_left[c] += 1
        
        if all(0 <= mines_left[c] <= tiles_left[c] for c in idx_constraints[i]):
            csp(i+1)

        for c in idx_constraints[i]:
            tiles_left[c] += 1

    csp(0)

    result = []

    for mines_used in solutions:
        solution = Solution(
            mines_used,
            {index: count for index, count in zip(all_indices, solutions[mines_used])},
            all_solutions[mines_used],
        )
        result.append(solution)

    return result


def find_disjoint_constraints(constraints: list[Constraint]) -> list[list[Constraint]]:
    uf = UnionFind()  # structure has both Constraint and tuple[int, int] index inside

    for c in constraints:
        uf.add(c)
        for index in c.indices:
            uf.add(index)
            uf.union(c, index)
    
    disjoint_sets = defaultdict(list)

    for c in constraints:
        set_id = uf.find(c)
        disjoint_sets[set_id].append(c)
    
    result = list(disjoint_sets.values())

    return result