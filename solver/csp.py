import numpy as np


def solve_csp(
    covered_frontier: list[tuple[int, int]],
    revealed_frontier: list[tuple[int, int]],
    values: np.ndarray[np.int8],
    flagged_nieghbours: np.ndarray[np.uint8],
) -> dict[int, tuple[np.ndarray, int]]:
    """Solves CSP for a specified frontier

    Args:
        covered_frontier (list[tuple[int, int]]): coordinates of covered tiles
        revealed_frontier (list[tuple[int, int]]): coordinates of revealed tiles
        values (np.ndarray[np.int8]): array of tiles' values
        flagged_nieghbours (np.ndarray[np.uint8]): array of tiles' flagged neighbours counts

    Returns:
        dict[int, tuple[np.ndarray, int]]: for each number of mines used: (number of solutions with mine present at each tile, number of all solutions)
    """
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

    solutions = {}

    mines_used = 0

    def rec(idx):
        nonlocal solutions, mines_used

        if idx == solution_len:
            if mines_used not in solutions:
                solutions[mines_used] = (np.zeros(solution_len, np.uint64), 0)

            solutions[mines_used] = (
                solutions[mines_used][0] + cur_solution,
                solutions[mines_used][1] + 1,
            )
            return

        for c in tile_constraints[idx]:
            tiles_free[c] -= 1

        # try True
        cur_solution[idx] = True
        mines_used += 1
        for c in tile_constraints[idx]:
            mines_left[c] -= 1

        if all(0 <= mines_left[c] <= tiles_free[c] for c in tile_constraints[idx]):
            rec(idx + 1)

        # try False
        cur_solution[idx] = False
        mines_used -= 1
        for c in tile_constraints[idx]:
            mines_left[c] += 1

        if all(0 <= mines_left[c] <= tiles_free[c] for c in tile_constraints[idx]):
            rec(idx + 1)

        for c in tile_constraints[idx]:
            tiles_free[c] += 1

    rec(0)

    return solutions
