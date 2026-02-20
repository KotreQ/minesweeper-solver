from collections import deque

import numpy as np


def generate_frontier(uncovered):
    padded = np.pad(uncovered, 1, "edge")

    rows, cols = uncovered.shape

    max_pool = np.zeros_like(uncovered, np.bool_)
    min_pool = np.ones_like(uncovered, np.bool_)

    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            shifted = padded[1 + dy : 1 + dy + rows, 1 + dx : 1 + dx + cols]
            max_pool = np.maximum(max_pool, shifted)
            min_pool = np.minimum(min_pool, shifted)

    border_mask = max_pool != min_pool

    revealed_frontier = border_mask & uncovered
    covered_frontier = border_mask & ~uncovered

    revealed_frontier = flood_fill_sort(revealed_frontier)
    covered_frontier = flood_fill_sort(covered_frontier)

    return revealed_frontier, covered_frontier


def flood_fill_sort(arr):
    rows, cols = arr.shape
    result = []

    visited = np.zeros_like(arr, np.bool_)

    NEIGHBOURS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for y in range(rows):
        for x in range(cols):
            if not arr[y][x] or visited[y][x]:
                continue

            q = deque()
            q.append((x, y))
            visited[y, x] = True

            while q:
                # TODO: Change algorithm to DFS and push neighbours in specific order based on previous direction
                x, y = q.popleft()
                result.append((x, y))

                for dx, dy in NEIGHBOURS:
                    nx = x + dx
                    ny = y + dy

                    if 0 <= nx < cols and 0 <= ny < rows:
                        if arr[ny, nx] and not visited[ny][nx]:
                            visited[ny, nx] = True
                            q.append((nx, ny))

    return result
