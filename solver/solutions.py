from dataclasses import dataclass
from collections import defaultdict
from itertools import product
from functools import reduce

from .constraints import Constraint, find_disjoint_constraints
import numpy as np


@dataclass(frozen=True, slots=True)
class Solution:
    mines_used: int
    placement_count: dict[tuple[int, int], int]
    all_placements: int


def find_constraints_solutions(constraints: list[Constraint]) -> list[Solution]:
    """This function returns all possible solutions that would satisfy constraints

    Args:
        constraints (list[Constraint]): Constraints that have to be satisfied

    Returns:
        list[Solution]: All possible solutions with regard to mine counts
    """
    constraint_sets = find_disjoint_constraints(constraints)

    sets_solutions = []
    for constraint_set in constraint_sets:
        set_solutions = csp_bruteforce(constraint_set)
        sets_solutions.append(set_solutions)

    if sets_solutions:
        full_solutions = [reduce(combine_unrelated_solutions, full_solution) for full_solution in product(*sets_solutions)]
    else:
        full_solutions = []

    combined_solutions = {}  # mines_used: solution
    for s in full_solutions:
        if not s.mines_used in combined_solutions:
            combined_solutions[s.mines_used] = s
        else:
            combined_solutions[s.mines_used] = combine_related_solutions(combined_solutions[s.mines_used], s)
    
    combined_solutions = list(combined_solutions.values())
    
    return combined_solutions


def extract_sure_variables(solutions: list[Solution]) -> tuple[list, list]:
    """Extract variables that have to be either 1 or 0 in all solutions

    Args:
        solutions (list[Solution]): List of solutions to check

    Returns:
        tuple[list, list]: (list of surely false variables, list of surely true variables)
    """
    index_placements = defaultdict(int)
    all_placements = defaultdict(int)

    for solution in solutions:
        for idx, count in solution.placement_count.items():
            index_placements[idx] += count
            all_placements[idx] += solution.all_placements
    
    sure_false = []
    sure_true = []

    for idx in index_placements:
        if index_placements[idx] == 0:
            sure_false.append(idx)
        elif index_placements[idx] == all_placements[idx]:
            sure_true.append(idx)

    return sure_false, sure_true


def combine_related_solutions(a: Solution, b: Solution) -> Solution:
    """Combines solutions that use the same number of mines and on the same indices

    Args:
        a (Solution): First solution
        b (Solution): Second solution

    Returns:
        Solution: The combined solution
    """
    assert a.placement_count.keys() == b.placement_count.keys()
    assert a.mines_used == b.mines_used

    mines_used = a.mines_used
    placement_count = {}

    for index in a.placement_count:
        placement_count[index] = a.placement_count[index] + b.placement_count[index]
    
    all_placements = a.all_placements + b.all_placements

    return Solution(mines_used, placement_count, all_placements)


def combine_unrelated_solutions(a: Solution, b: Solution) -> Solution:
    """Combines solutions that don't share any indices

    Args:
        a (Solution): First solution
        b (Solution): Second solution

    Returns:
        Solution: The combined solution
    """
    assert a.placement_count.keys().isdisjoint(b.placement_count.keys())

    mines_used = a.mines_used + b.mines_used
    placement_count = {}

    for index, count in a.placement_count.items():
        count *= b.all_placements
        placement_count[index] = count
    
    for index, count in b.placement_count.items():
        count *= a.all_placements
        placement_count[index] = count

    all_placements = a.all_placements * b.all_placements
    
    return Solution(mines_used, placement_count, all_placements)


def csp_bruteforce(constraints: list[Constraint]) -> list[Solution]:
    """Finds all possible solutions for the specified constraints using a brute-force algorithm

    Args:
        constraints (list[Constraint]): The constraints that have to be satisfied

    Returns:
        list[Solution]: Possible solutions - each separate solution is for different number of mines used
    """
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
