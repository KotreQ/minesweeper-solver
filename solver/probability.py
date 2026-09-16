from collections import defaultdict

import numpy as np
import math
import random

from .solution import Solution


def calculate_probabilities(grid: np.ndarray, solutions: list[Solution], mines_left: int) -> list[float, tuple[int, int]]:
    unknown_tiles = np.argwhere((~grid["is_revealed"]) & (grid["revealed_neighbours"] == 0))
    unknown_count = unknown_tiles.shape[0]

    mines_used_prob = {}

    solutions_counts = []
    for solution in solutions:
        if solution.mines_used > mines_left:
            unknown_comb_count = 0
        else:
            unknown_comb_count = math.comb(unknown_count, mines_left - solution.mines_used)
        
        solutions_counts.append((solution, unknown_comb_count * solution.all_placements))

    solutions_count_all = sum(count for _, count in solutions_counts)
    solutions_prob = [(solution, count / solutions_count_all) for solution, count in solutions_counts]

    for solution, prob in solutions_prob:
        assert solution.mines_used not in mines_used_prob
        mines_used_prob[solution.mines_used] = prob

    variable_prob = defaultdict(float)

    for solution in solutions:
        prob_of_sol = mines_used_prob[solution.mines_used]
        for var, count in solution.placement_count.items():
            prob_of_var = count / solution.all_placements

            variable_prob[var] += prob_of_sol * prob_of_var

    if unknown_count > 0:
        if len(mines_used_prob) == 0:
            mines_used_prob[0] = 1.0

        unknown_prob = 0.0
        for mines_used, prob in mines_used_prob.items():
            prob_of_mine = (mines_left - mines_used) / unknown_count
            unknown_prob += prob_of_mine * prob

        for y, x in unknown_tiles:
            y = int(y)
            x = int(x)
            variable_prob[(y, x)] = unknown_prob

    return sorted([(prob, var) for var, prob in variable_prob.items()], key=lambda t: (t[0], random.random()))
