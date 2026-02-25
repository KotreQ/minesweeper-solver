import numpy as np


def solve_csp(covered_frontier, revealed_frontier, values, flagged_nieghbours):
    solution_len = len(covered_frontier)
    cur_solution = np.zeros(solution_len, np.bool_)

    tile_constraints = [
        [] for _ in range(solution_len)
    ]  # which constraints affect a specific tile

    constraints_len = len(revealed_frontier)
    mines_left = np.zeros(constraints_len, np.int8)
    tiles_free = np.zeros(constraints_len, np.int8)

    for i in range(constraints_len):
        x, y = revealed_frontier[i]

        mines_left[i] = values[y, x] - flagged_nieghbours[y, x]

        for j in range(solution_len):
            nx, ny = covered_frontier[j]
            if abs(nx - x) <= 1 and abs(ny - y) <= 1:
                tile_constraints[j].append(i)
                tiles_free[i] += 1

    solution_sum = np.zeros(solution_len, np.uint64)
    all_solutions = 0

    def rec(idx):
        nonlocal solution_sum, all_solutions

        if idx == solution_len:
            solution_sum += cur_solution
            all_solutions += 1
            return

        for c in tile_constraints[idx]:
            tiles_free[c] -= 1

        # try True
        cur_solution[idx] = True
        for c in tile_constraints[idx]:
            mines_left[c] -= 1

        if all(0 <= mines_left[c] <= tiles_free[c] for c in tile_constraints[idx]):
            rec(idx + 1)

        # try False
        cur_solution[idx] = False
        for c in tile_constraints[idx]:
            mines_left[c] += 1

        if all(0 <= mines_left[c] <= tiles_free[c] for c in tile_constraints[idx]):
            rec(idx + 1)

        for c in tile_constraints[idx]:
            tiles_free[c] += 1

    rec(0)

    return solution_sum, all_solutions
