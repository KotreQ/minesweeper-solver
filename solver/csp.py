import numpy as np
from collections import defaultdict
from .constraint import Constraint
from .solution import Solution


def csp_bruteforce(constraints: list[Constraint]) -> list[Solution]:
    """Finds all possible solutions for the specified constraints using a brute-force algorithm

    Args:
        constraints (list[Constraint]): The constraints that have to be satisfied

    Returns:
        list[Solution]: Possible solutions - each separate solution is for different number of mines used
    """
    all_variables = set()

    for c in constraints:
        all_variables.update(c.variables)
    
    all_variables = list(all_variables)
    N = len(all_variables)

    mines_left = [c.value for c in constraints]
    tiles_left = [len(c.variables) for c in constraints]

    var_constraints = [[i for i, c in enumerate(constraints) if variable in c.variables] for variable in all_variables]  # which constraints are affected by variables

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
        
        for c in var_constraints[i]:
            tiles_left[c] -= 1

        # try True
        cur_solution[i] = True
        mines_used += 1
        for c in var_constraints[i]:
            mines_left[c] -= 1
        
        if all(0 <= mines_left[c] <= tiles_left[c] for c in var_constraints[i]):
            csp(i+1)
        
        # try False
        cur_solution[i] = False
        mines_used -= 1
        for c in var_constraints[i]:
            mines_left[c] += 1
        
        if all(0 <= mines_left[c] <= tiles_left[c] for c in var_constraints[i]):
            csp(i+1)

        for c in var_constraints[i]:
            tiles_left[c] += 1

    csp(0)

    result = []

    for mines_used in solutions:
        solution = Solution(
            mines_used,
            {variable: count for variable, count in zip(all_variables, solutions[mines_used])},
            all_solutions[mines_used],
        )
        result.append(solution)

    return result
