import numpy as np
from numba import njit


@njit
def get_iter_counts(x_axis, y_axis, resolution, max_iters, bound):
    iteration_counts = np.zeros(resolution, dtype=np.float64)
    for i, x in enumerate(x_axis):
        for j, y in enumerate(y_axis):
            z = c = complex(x, y)
            iters = 0
            for iters in range(max_iters + 1):
                z = z ** 2 + c
                if abs(z) > bound:
                    break
            if iters < max_iters:
                iters = iters + 1 - np.log(np.log(abs(z)) / np.log(2)) / np.log(2)
            iteration_counts[i][j] = iters
    return iteration_counts
