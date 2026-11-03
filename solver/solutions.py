from collections import defaultdict
from itertools import product
from functools import reduce
import math

from .solution import Solution
from .constraint import Constraint
from .constraints import find_disjoint_constraints, optimize_constraints
from .cache import MinesweeperSolutionsCache


csp_cache = MinesweeperSolutionsCache()


def get_max_score_variable(constraints: list[Constraint]) -> tuple[int, int] | int:
    variable_scores = defaultdict(float)

    for c in constraints:
        for var in c.variables:
            variable_scores[var] += 1.0 / len(c.variables)

    return max(variable_scores.keys(), key=lambda var: variable_scores[var])


def get_trivial_constraint_solution(constraint: Constraint) -> Solution:
    mines_used = constraint.value
    all_placements = math.comb(len(constraint.variables, constraint.value))
    var_placement_count = math.comb(len(constraint.variables)-1, constraint.value-1) if constraint.value > 0 else 0

    return Solution(
        mines_used,
        {var: var_placement_count for var in constraint.variables},
        all_placements
    )


def find_constraints_solutions(constraints: list[Constraint]) -> list[Solution]:
    """This function returns all possible solutions that would satisfy constraints

    Args:
        constraints (list[Constraint]): Constraints that have to be satisfied

    Returns:
        list[Solution]: All possible solutions with regard to mine counts
    """

    constraints = optimize_constraints(constraints)
    constraint_sets = find_disjoint_constraints(constraints)

    sets_solutions = []
    for constraint_set in constraint_sets:
        if len(constraint_set) == 1:
            solution = get_trivial_constraint_solution(constraint_set[0])
            sets_solutions.append([solution])

        else:
            # TODO: Use recursion here
            set_solutions = []
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

    for variable in a.placement_count:
        placement_count[variable] = a.placement_count[variable] + b.placement_count[variable]
    
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

    for variable, count in a.placement_count.items():
        count *= b.all_placements
        placement_count[variable] = count
    
    for variable, count in b.placement_count.items():
        count *= a.all_placements
        placement_count[variable] = count

    all_placements = a.all_placements * b.all_placements
    
    return Solution(mines_used, placement_count, all_placements)
