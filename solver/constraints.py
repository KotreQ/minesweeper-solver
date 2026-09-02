from dataclasses import dataclass
import numpy as np
from collections import defaultdict
from .frontier import find_edges
from .grid import get_neighbours_coords
from .unionfind import UnionFind


@dataclass(frozen=True, slots=True)
class Constraint:
    value: int
    variables: frozenset[tuple[int, int]]


def get_constraints(grid):
    constraints = []

    edge_mask = find_edges(grid)
    rows, cols = grid.shape

    mines_left = grid["value"] - grid["flagged_neighbours"]
    is_unknown = ~grid["is_revealed"] & ~grid["is_flagged"]

    y_list, x_list = np.where(edge_mask)
    for x, y in zip(x_list, y_list):
        value = mines_left[y, x]
        indices = []

        for nx, ny in get_neighbours_coords(x, y, rows, cols):
            if is_unknown[ny, nx]:
                indices.append((ny, nx))

        if len(indices) > 0:
            c = Constraint(value, frozenset(indices))
            constraints.append(c)
    
    return constraints


def sort_constraints(constraints: list[Constraint]) -> None:
    # using counting sort twice for linear-time sorting
    N = len(constraints)

    # first, sort by the length of the constraint
    temp = [None for _ in range(N)]

    counts = [0 for _ in range(9)]
    for c in constraints:
        idx = 8 - len(c.variables)
        counts[idx] += 1
    counts = np.cumsum(counts)

    for c in constraints[::-1]:
        idx = 8 - len(c.variables)
        counts[idx] -= 1
        temp[counts[idx]] = c
    
    # second, do a stable sort by the value of the constraint
    counts = [0 for _ in range(9)]
    for c in temp:
        idx = 8 - c.value
        counts[idx] += 1
    counts = np.cumsum(counts)

    for c in temp[::-1]:
        idx = 8 - c.value
        counts[idx] -= 1
        constraints[counts[idx]] = c


def find_disjoint_constraints(constraints: list[Constraint]) -> list[list[Constraint]]:
    """Divides the constraints into separate lists that can be solved independently

    Args:
        constraints (list[Constraint]): All constraints

    Returns:
        list[list[Constraint]]: Independent lists of constraints
    """
    uf = UnionFind()  # structure has both Constraint and tuple[int, int] variable index inside

    for c in constraints:
        uf.add(c)
        for variable in c.variables:
            uf.add(variable)
            uf.union(c, variable)
    
    disjoint_sets = defaultdict(list)

    for c in constraints:
        set_id = uf.find(c)
        disjoint_sets[set_id].append(c)
    
    result = list(disjoint_sets.values())

    return result


def optimize_constraints(constraints: list[Constraint]) -> list[Constraint]:
    running = True
    while running:
        running = False

        # Firstly, optimize trivial cases
        new_constraints = set()
        for constraint in constraints:
            new, is_trivial = _expand_trivial(constraint)
            if is_trivial:
                new_constraints.update(new)
                running = True
            else:
                new_constraints.add(constraint)

        constraints = list(new_constraints)

        # Sort them by length, so that always the first one is optimized by the second one
        sort_constraints(constraints)
        length = len(constraints)

        new_constraints = set()
        for i in range(length):
            a = constraints[i]
            optimized = False

            for j in range(i+1, length):
                b = constraints[j]

                new, optimized = _subset_optimization(a, b)
                if optimized:
                    new_constraints.update(new)
                    break

                new, optimized = _intersection_optimization(a, b)
                if optimized:
                    new_constraints.update(new)
                    break

            if optimized:
                running = True
            else:
                new_constraints.add(a)
                
        constraints = list(new_constraints)
    
    return constraints


def _subset_optimization(a: Constraint, b: Constraint) -> tuple[list[Constraint], bool]:
    if a.variables.issuperset(b.variables):
        new_val = a.value - b.value
        new_variables = a.variables - b.variables
        new = Constraint(new_val, new_variables)
        return [new], True
    return [], False


def _intersection_optimization(a: Constraint, b: Constraint) -> tuple[list[Constraint], bool]:
    if not a.variables.isdisjoint(b.variables):
        AmB = a.variables - b.variables
        BmA = b.variables - a.variables
        AnB = a.variables.intersection(b.variables)

        if a.value - b.value == len(AmB):
            c1 = Constraint(a.value - b.value, AmB)
            c2 = Constraint(0, BmA)
            c3 = Constraint(b.value, AnB)
            return [c1, c2, c3], True

    return [], False


def _expand_trivial(a: Constraint) -> tuple[list[Constraint], bool]:
    if a.value == 0 and len(a.variables) > 1:
        return [Constraint(0, frozenset([idx])) for idx in a.variables], True
    
    if a.value == len(a.variables) and len(a.variables) > 1:
        return [Constraint(1, frozenset([idx])) for idx in a.variables], True
    
    return [], False
