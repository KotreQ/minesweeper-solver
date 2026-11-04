from collections import defaultdict
from itertools import product
from functools import reduce
import math

from .solution import Solution
from .constraint import Constraint
from .constraints import find_disjoint_constraints, lock_constraints_variable, optimize_constraints
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
    all_placements = math.comb(len(constraint.variables), constraint.value)
    var_placement_count = math.comb(len(constraint.variables) - 1, constraint.value - 1) if constraint.value > 0 else 0

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
        # Trivial case
        if len(constraint_set) == 1:
            solution = get_trivial_constraint_solution(constraint_set[0])
            sets_solutions.append([solution])

        # Non-trivial case
        else:
            set_solutions = csp_cache.get(constraint_set)

            # If case is in cache
            if set_solutions is not None:
                sets_solutions.append(set_solutions)
            
            # If case is not in cache, solve and save
            else:
                set_solutions = []

                locked_var = get_max_score_variable(constraint_set)

                constraintsA, successA = lock_constraints_variable(constraint_set, locked_var, True)
                constraintsB, successB = lock_constraints_variable(constraint_set, locked_var, False)

                if successA:
                    subsolutionsA = find_constraints_solutions(constraintsA)
                    for solution in subsolutionsA:
                        mines_used = solution.mines_used + 1
                        all_placements = solution.all_placements
                        placement_count = solution.placement_count.copy()
                        placement_count[locked_var] = all_placements
                        set_solutions.append(Solution(mines_used, placement_count, all_placements))

                if successB:
                    subsolutionsB = find_constraints_solutions(constraintsB)
                    for solution in subsolutionsB:
                        mines_used = solution.mines_used
                        all_placements = solution.all_placements
                        placement_count = solution.placement_count.copy()
                        placement_count[locked_var] = 0
                        set_solutions.append(Solution(mines_used, placement_count, all_placements))

                # group solutions by mines used
                grouped_solutions = defaultdict(list)
                for s in set_solutions:
                    grouped_solutions[s.mines_used].append(s)
                set_solutions = [
                    reduce(combine_related_solutions, solutions)
                    for solutions in grouped_solutions.values()
                ]

                # save to cache
                csp_cache.save(constraint_set, set_solutions)

                sets_solutions.append(set_solutions)

    # combine solutions of sets into solutions of all constraints
    if sets_solutions:
        full_solutions = [reduce(combine_unrelated_solutions, full_solution) for full_solution in product(*sets_solutions)]
    else:
        full_solutions = []

    # group solutions by mines used
    grouped_solutions = defaultdict(list)
    for s in full_solutions:
        grouped_solutions[s.mines_used].append(s)
    combined_solutions = [
        reduce(combine_related_solutions, solutions)
        for solutions in grouped_solutions.values()
    ]

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
