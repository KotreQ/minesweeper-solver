import numpy as np
from collections import defaultdict, deque
from .frontier import find_edges
from .grid import get_neighbours_coords
from .unionfind import UnionFind
from .constraint import Constraint


def get_constraints(grid):
    constraints = []

    edge_mask = find_edges(grid)
    rows, cols = grid.shape

    mines_left = grid["value"] - grid["flagged_neighbours"]
    is_unknown = ~grid["is_revealed"] & ~grid["is_flagged"]

    for y, x in np.argwhere(edge_mask):
        # int() strips the numpy scalar type (int8 - uint8 promotes to int16),
        # which would otherwise leak into Constraint/Solution.
        value = int(mines_left[y, x])
        indices = []

        for nx, ny in get_neighbours_coords(x, y, rows, cols):
            if is_unknown[ny, nx]:
                indices.append((ny, nx))

        if len(indices) > 0:
            c = Constraint(value, frozenset(indices))
            constraints.append(c)
    
    return constraints


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


def lock_constraints_variable(constraints: list[Constraint], variable: int | tuple[int, int], value: bool) -> tuple[list[Constraint], bool]:
    """Generates new constraints list, assuming a specified variable has a specific value

    Args:
        constraints (list[Constraint]): Original constraints
        variable (int | tuple[int, int]): Index of variable to be locked
        value (bool): Assumed value of the variable

    Returns:
        tuple[list[Constraint], bool]: _description_
    """

    new_constraints = []

    for c in constraints:
        if variable in c.variables:
            new_value = c.value - 1 if value else c.value
            new_variables = c.variables.difference([variable])
            if new_value < 0 or new_value > len(new_variables):
                return [], False

            if len(new_variables) > 0:
                new_constraint = Constraint(new_value, new_variables)
                new_constraints.append(new_constraint)

        else:
            new_constraints.append(c)

    return new_constraints, True


def optimize_constraints(constraints: list[Constraint]) -> tuple[list[Constraint], bool]:
    """Optimized the constraints using intersection rules

    Args:
        constraints (list[Constraint]): The constraints to optimize

    Returns:
        tuple[list[Constraint], bool]: (constraints, sat) -> Optimized constraints and are they satisfiable
    """

    constraints = _expand_trivial_constraints(constraints)
    constraints_set = set(constraints)

    pair_queue = deque()
    is_retired = [False for _ in range(len(constraints))]

    var_constraints_index = defaultdict(set)  # var -> [constraint indices]

    def update_queue(i: int):
        intersecting_constraints = set()
        for var in constraints[i].variables:
            intersecting_constraints.update(var_constraints_index[var])

            var_constraints_index[var].add(i)

            for j in intersecting_constraints:
                pair_queue.append((i, j))

    def remove_from_index(i: int):
        constraint = constraints[i]
        for var in constraint.variables:
            var_constraints_index[var].remove(i)

    for i in range(len(constraints)):
        update_queue(i)
        
    while len(pair_queue) > 0:
        a, b = pair_queue.popleft()

        if is_retired[a] or is_retired[b]:
            continue

        new, sat = _constraint_optimization(constraints[a], constraints[b])
        if not sat:  # if any optimization is unsatisfiable, the initial constraints were too
            return [], False

        if len(new) > 0:
            new = _expand_trivial_constraints(new)
            if constraints[a] not in new:
                is_retired[a] = True
                remove_from_index(a)
            if constraints[b] not in new:
                is_retired[b] = True
                remove_from_index(b)
            
            new_count = 0
            for c in new:
                if c not in constraints_set:
                    new_count += 1
                    constraints_set.add(c)
                    constraints.append(c)
                    is_retired.append(False)

            for i in range(len(constraints) - new_count, len(constraints)):
                update_queue(i)

    new_constraints = [c for c, was_optimized in zip(constraints, is_retired) if not was_optimized]

    return new_constraints, True


def _constraint_optimization(a: Constraint, b: Constraint) -> tuple[list[Constraint], bool]:
    X = a.variables - b.variables
    Y = b.variables - a.variables
    Z = a.variables & b.variables

    if len(Z) == 0:  # constraints are disjoint
        return [], True  # [], sat

    # calculate lower and upper bounds for intersection
    low_z = max(0, a.value - len(X), b.value - len(Y))
    high_z = min(len(Z), a.value, b.value)

    if low_z == high_z:  # if optimized
        z_val = low_z
        new = [
            Constraint(z_val, Z),
            Constraint(a.value - z_val, X),
            Constraint(b.value - z_val, Y)
        ]
        return new, True  # optimized constraints, sat
    
    elif low_z < high_z:  # if not optimized
        return [], True  # [], sat

    else:  # if contradictory
        return [], False  # [], unsat


def _expand_trivial_constraints(constraints: list[Constraint]):
    expanded = set()
    for constraint in constraints:
        new, optimized = _expand_trivial(constraint)
        if optimized:
            expanded.update(new)
        else:
            expanded.add(constraint)
    return list(expanded)

def _expand_trivial(a: Constraint) -> tuple[list[Constraint], bool]:
    if a.value == 0 and len(a.variables) > 1:
        return [Constraint(0, frozenset([idx])) for idx in a.variables], True
    
    if a.value == len(a.variables) and len(a.variables) > 1:
        return [Constraint(1, frozenset([idx])) for idx in a.variables], True
    
    return [], False
