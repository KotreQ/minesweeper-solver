from collections import defaultdict
from dataclasses import dataclass
import pynauty
from .constraints import Constraint


@dataclass(frozen=True, slots=True)
class CanonicalizedConstraintVariables:
    cache_key: tuple
    var2canon: dict[tuple[int, int], int]
    canon2var: dict[int, tuple[int, int]]


def canonicalize_constraints(constraints: list[Constraint]) -> CanonicalizedConstraintVariables:
    # create an array "vertices": list of (arbitrary_constraint_id, constraint_value) or (variable_position, None)
    vertices = []
    for constraint_id, constraint in enumerate(constraints):
        vertices.append((constraint_id, constraint.value))

    all_variables = set()
    for constraint in constraints:
        all_variables.update(constraint.variables)

    for variable in all_variables:
        vertices.append((variable, None))

    # create an array "edges": list of tuples of the keys in "vertices" array
    edges = []
    for constraint_id, constraint in enumerate(constraints):
        for variable in constraint.variables:
            edges.append((constraint_id, variable))

    # run the pynauty canonicalization algorithm
    temp2old = [old_id for old_id, _ in vertices]
    old2temp = {old_id: temp for temp, old_id in enumerate(temp2old)}
    n = len(temp2old)

    adjacency = {i: [] for i in range(n)}
    for old_u, old_v in edges:
        u = old2temp[old_u]
        v = old2temp[old_v]

        adjacency[u].append(v)
        adjacency[v].append(u)

    color_classes = defaultdict[set]
    for temp, (_, label) in enumerate(vertices):
        color_classes[label].add(temp)

    graph = pynauty.Graph(
        number_of_vertices=n,
        directed=False,
        adjacency_dict=adjacency,
        vertex_coloring=list(color_classes.values())
    )

    canon_order = tuple(pynauty.canon_label(graph))

    if sorted(canon_order) != list(range(n)):
        raise RuntimeError("pynauty returned an invalid canonical labeling")

    canon2old = [temp2old[temp] for temp in canon_order]
    old2canon = {var: canon for canon, var in enumerate(canon2old)}

    canon_colors = tuple(vertices[temp][1] for temp in canon_order)
    canon_edges = tuple(sorted(
        (
        min(old2canon[old_u], old2canon[old_v]),
        max(old2canon[old_u], old2canon[old_v])
        ) for old_u, old_v in edges
    ))
    cache_key = (canon_colors, canon_edges)

    var2canon = {
        variable: old2canon[variable] for variable in all_variables
    }
    canon2var = {
        canon: var for var, canon in var2canon.items()
    }

    return CanonicalizedConstraintVariables(cache_key, var2canon, canon2var)