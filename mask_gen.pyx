# cython: profile=True
# cython: boundscheck=False
# cython: wraparound=False

import numpy as np
cimport numpy as np
from libc.math cimport pow

cpdef add_items_cython(np.ndarray[np.npy_bool, ndim=2] layers,
                       np.ndarray[np.uint8_t, ndim=3] colors,
                       np.ndarray[np.npy_bool, ndim=2] mask,
                       int layer, tuple color):

    layers |= mask
    colors[mask] = color  # Assign color to elements corresponding to the mask

    return layers, colors



cpdef draw_cython(int x, int y, int radius, tuple color, int screen_width, int screen_height):
    cdef int r_squared = <int>pow(radius, 2)
    cdef np.ndarray mask = np.zeros((screen_width, screen_height), dtype=bool)
    cdef int i, j, new_x, new_y

    for i in range(-radius, radius):
        for j in range(-radius, radius):
            if pow(i, 2) + pow(j, 2) < r_squared:
                new_x = x + i
                new_y = y + j
                if 0 <= new_x < screen_width and 0 <= new_y < screen_height:
                    mask[new_x, new_y] = True

    return mask


