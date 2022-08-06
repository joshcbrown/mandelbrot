import numpy as np
from numba import njit
from typing import List


class LinearInterpolator:
    def __init__(self, xs, ys):
        self.xs = np.array(xs, dtype=np.float64)
        self.ys = np.array(ys, dtype=np.float64)
        y_diffs = self.ys[1:] - self.ys[:-1]
        x_diffs = self.xs[1:] - self.xs[:-1]

        # nasty way to do this with hard coding, but it works for this application
        x_diffs = x_diffs.repeat(y_diffs.shape[1]).reshape(
            x_diffs.shape[0], y_diffs.shape[1])
        self.ms = y_diffs / x_diffs
        self.cs = self.ys[1:] - \
            (self.ms * self.xs[1:].repeat(3).reshape(self.ms.shape))

    def __call__(self, x):
        return _get_val(x, self.xs, self.ys, self.ms, self.cs)


class PaletteLinearInterpolator(LinearInterpolator):
    def __init__(self, ys, weights, splits):
        print(ys, len(ys))
        ys = list(set([tuple(x) for x in ys]))

        print(ys, len(ys))
        print(weights, len(weights))
        xs = np.linspace(0, 1, splits)
        new_ys = [[0, 0, 0]]
        for _ in range(xs.size - 2):
            idx = np.random.choice([*range(len(ys))], p=weights)
            new_ys.append(ys[idx])
        new_ys.append([0, 0, 0])
        new_ys = np.array(new_ys)
        print(xs.shape, new_ys.shape)
        super().__init__(xs, new_ys)


class RandomLinearInterpolator(LinearInterpolator):
    COLOURS = np.array([
        [255, 0, 0],
        [0, 255, 0],
        [0, 0, 255],
        [255, 255, 0],
        [255, 0, 255],
        [0, 255, 255],
        [255, 255, 255]
    ])

    def __init__(self, splits):
        xs = np.linspace(0, 1, splits)
        ys = [[0, 0, 0]]
        for _ in range(xs.size - 2):
            prev = ys[-1]
            new = prev.copy()
            changing = np.random.randint(0, 3)
            new[changing] = 0 if new[changing] == 255 else 255
            ys.append(new)
        ys.append([0, 0, 0])
        ys = np.array(ys)
        print(ys.shape)
        ys[-1] = [0, 0, 0]
        super().__init__(xs, ys)


@njit
def _get_val(x, xs, ys, ms, cs):
    if x >= xs[-1]:
        return ys[-1]
    elif x <= xs[0]:
        return ys[0]
    # not doing binary search here since it won't make a large difference to performance

    for i in range(xs.shape[0] - 1):
        if xs[i] <= x <= xs[i + 1]:
            return ms[i] * x + cs[i]

    return np.array([0, 0, 0], dtype=np.float64)
