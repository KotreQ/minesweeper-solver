def get_neighbours(x, y, w, h):
    for i in range(x - 1, x + 2):
        for j in range(y - 1, y + 2):
            if i < 0 or j < 0 or i >= w or j >= h or (i == x and j == y):
                continue
            yield i, j
