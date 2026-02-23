import numpy as np


class Constraint:
    def __init__(self, solution_arr, filled_mask, used_mask, target_val):
        # Mutable values
        self.__solution_arr = solution_arr  # currently tested solution
        self.__filled_mask = filled_mask  # which indices of solution are locked

        # Immutable values
        self.__used_mask = used_mask  # which indices do affect this constraint
        self.__values_count = np.sum(self.__used_mask)
        self.__target_val = target_val  # the target amount of True values

    def check(self) -> bool:
        mask_locked = self.__filled_mask & self.__used_mask

        values_locked = np.sum(mask_locked)
        values_free = self.__values_count - values_locked

        solution = self.__solution_arr & mask_locked
        current_val = np.sum(solution)

        if current_val > self.__target_val:
            return False

        if current_val + values_free < self.__target_val:
            return False

        return True


def solve_csp(covered_frontier, revealed_frontier, values, flagged_nieghbours):
    solution_len = len(covered_frontier)
    cur_solution = np.zeros(solution_len, np.bool_)
    cur_filled_mask = np.zeros(solution_len, np.bool_)

    constraints = []
    for x, y in revealed_frontier:
        mines_left = values[y, x] - flagged_nieghbours[y, x]

        neighbour_mask = [
            abs(nx - x) <= 1 and abs(ny - y) <= 1 for nx, ny in covered_frontier
        ]
        neighbour_mask = np.array(neighbour_mask, np.bool_)

        constraint = Constraint(
            cur_solution, cur_filled_mask, neighbour_mask, mines_left
        )
        constraints.append(constraint)

    solution_sum = np.zeros(solution_len, np.uint64)
    all_solutions = 0

    def rec(idx):
        nonlocal solution_sum, all_solutions

        if idx == solution_len:
            solution_sum += cur_solution
            all_solutions += 1
            return

        cur_filled_mask[idx] = True

        # try False
        cur_solution[idx] = False
        if all(c.check() for c in constraints):
            rec(idx + 1)

        # try True
        cur_solution[idx] = True
        if all(c.check() for c in constraints):
            rec(idx + 1)

        cur_filled_mask[idx] = False
    
    rec(0)

    return solution_sum, all_solutions
