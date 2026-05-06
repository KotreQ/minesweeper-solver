from .constraints import Constraint
from .unionfind import UnionFind

from collections import defaultdict


def find_disjoint_constraints(constraints: list[Constraint]) -> list[list[Constraint]]:
    uf = UnionFind()  # structure has both Constraint and tuple[int, int] index inside

    for constraint in constraints:
        uf.add(constraint)
        for index in constraint.indices:
            uf.add(index)
            uf.union(constraint, index)
    
    disjoint_sets = defaultdict(list)

    for constraint in constraints:
        set_id = uf.find(constraint)
        disjoint_sets[set_id].append(constraint)
    
    result = list(disjoint_sets.values())

    return result