import numpy as np
from numba import njit


@njit
def get_iter_counts(x_axis, y_axis, resolution, max_iters, bound):
    iteration_counts = np.zeros(resolution, dtype=np.int16)
    for i, x in enumerate(x_axis):
        for j, y in enumerate(y_axis):
            z = c = complex(x, y)
            iters = 0
            for iters in range(max_iters):
                z = z ** 2 + c
                if abs(z) > bound:
                    break
            iteration_counts[i, j] = iters
    return iteration_counts


@njit
def get_cumulative_pp(iteration_counts):
    num_iters_pp = np.zeros(iteration_counts.max() + 1, dtype=np.int32)
    for row in iteration_counts:
        for count in row:
            num_iters_pp[count] += 1
    return num_iters_pp



