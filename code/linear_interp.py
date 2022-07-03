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
        x_diffs = x_diffs.repeat(y_diffs.shape[1]).reshape(x_diffs.shape[0], y_diffs.shape[1])
        self.ms = y_diffs / x_diffs
        self.cs = self.ys[1:] - (self.ms * self.xs[1:].repeat(3).reshape(self.ms.shape))

    def __call__(self, x):
        return _get_val(x, self.xs, self.ys, self.ms, self.cs)


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
    def __init__(self, size, repeats):
        xs = np.concatenate([[0], np.cumsum([2 ** -i for i in range(1, size - 1)]), [1]])
        diffs = np.diff(xs)
        xs = np.concatenate([xs[:-1].repeat(repeats), xs[-1:]])
        for i in range(1, repeats):
            changing = xs[np.arange(xs.size) % repeats == i]
            xs[np.arange(xs.size) % repeats == i] = changing + i * diffs / repeats
        # xs[np.arange(xs.size) % 2 == 1] = xs[np.arange(xs.size) % 2 == 1] + diffs / 2
        # COLOURS = RandomLinearInterpolator.COLOURS
        # PALETTE = np.array([COLOURS[np.random.randint(0, COLOURS.shape[0])] for _ in range(np.random.randint(3, COLOURS.shape[0]))])
        # ys = np.concatenate([np.concatenate([PALETTE] * (xs.size // PALETTE.shape[0])), PALETTE[:xs.size % PALETTE.shape[0]]])
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
