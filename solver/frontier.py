from collections import deque

import numpy as np

from .neighbours import get_neighbours_coords


def find_edges(mask):
    padded = np.pad(mask, 1, "edge")

    rows, cols = mask.shape

    max_pool = np.zeros_like(mask, np.bool_)
    min_pool = np.ones_like(mask, np.bool_)

    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            shifted = padded[1 + dy : 1 + dy + rows, 1 + dx : 1 + dx + cols]
            max_pool = np.maximum(max_pool, shifted)
            min_pool = np.minimum(min_pool, shifted)

    border_mask = max_pool != min_pool

    ones_edge = border_mask & mask
    zeros_edge = border_mask & ~mask

    return ones_edge, zeros_edge


def generate_frontiers(
    revealed: np.ndarray[np.bool_], flagged: np.ndarray[np.bool_]
) -> list[tuple[list[tuple[int, int]], list[tuple[int, int]]]]:
    """Returns all frontiers on map

    Args:
        revealed (np.ndarray[np.bool_]): Boolean mask of revealed tiles
        flagged (np.ndarray[np.bool_]): Boolean mask of flagged tiles

    Returns:
        list[tuple[list[tuple[int, int]], list[tuple[int, int]]]]: A list of frontiers structured like: [(revealed_frontier, covered_frontier), ...] where each frontier is a list of coordinates
    """
    revealed_frontiers_mask, covered_frontiers_mask = find_edges(revealed)
    covered_frontiers_mask &= ~flagged

    height, width = revealed.shape

    visited = np.zeros((height, width), np.bool_)
    walkable = revealed_frontiers_mask | covered_frontiers_mask

    frontiers = []

    for y in range(height):
        for x in range(width):
            if not walkable[y, x] or visited[y, x]:
                continue

            q = deque()
            q.append((x, y))
            visited[y, x] = True

            revealed_frontier = []
            covered_frontier = []

            while q:
                x, y = q.popleft()

                if revealed[y, x]:
                    revealed_frontier.append((x, y))
                else:
                    covered_frontier.append((x, y))

                for nx, ny in get_neighbours_coords(x, y, height, width):
                    if visited[ny, nx]:
                        continue

                    if (
                        revealed[y, x]
                        and covered_frontiers_mask[ny, nx]
                        or not revealed[y, x]
                        and revealed_frontiers_mask[ny, nx]
                    ):  # ensure switch between revealed and covered at each step
                        visited[ny, nx] = True
                        q.append((nx, ny))

            if len(covered_frontier) > 0:  # skip frontiers with empty covered lists
                frontiers.append((revealed_frontier, covered_frontier))

    return frontiers
