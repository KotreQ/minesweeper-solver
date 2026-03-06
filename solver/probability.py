import numpy as np


def combine_frontier_solutions(
    covered_frontiers, frontiers_solutions, min_mines, max_mines
):

    frontier_count = len(frontiers_solutions)

    frontiers_lengths = np.array(
        [len(frontier) for frontier in covered_frontiers], np.uint64
    )
    frontiers_lengths_sums = np.concat(
        (np.zeros(1, np.uint64), np.cumsum(frontiers_lengths))
    )

    # {mines_used: (solutions with mines on tiles (if there are exactly as many mines used), all_solutions)}
    grid_solutions = {}

    def rec(
        idx=0,
        prev_mines_used=0,
        prev_solution=np.zeros(frontiers_lengths_sums[frontier_count], np.uint64),
        prev_all_solutions=1,
    ):

        if idx >= frontier_count:
            return

        frontier_solutions = frontiers_solutions[idx]  # solutions of specified frontier

        for mines_used in frontier_solutions:
            mine_possibilities, solution_count = frontier_solutions[mines_used]
            all_mines_used = prev_mines_used + mines_used

            if all_mines_used > max_mines:
                continue

            # multiply previous ones to keep track of solution count
            cur_solution = prev_solution * solution_count
            cur_solution[
                frontiers_lengths_sums[idx] : frontiers_lengths_sums[idx + 1]
            ] = mine_possibilities * prev_all_solutions
            cur_all_solutions = prev_all_solutions * solution_count

            rec(idx + 1, all_mines_used, cur_solution, cur_all_solutions)

            if idx == frontier_count - 1:  # when full solution completed
                if all_mines_used < min_mines:
                    continue

                if all_mines_used not in grid_solutions:
                    grid_solutions[all_mines_used] = (
                        np.zeros(frontiers_lengths_sums[frontier_count], np.uint64),
                        0,
                    )

                grid_solutions[all_mines_used] = (
                    grid_solutions[all_mines_used][0] + cur_solution,
                    grid_solutions[all_mines_used][1] + cur_all_solutions,
                )

    rec()

    return grid_solutions

