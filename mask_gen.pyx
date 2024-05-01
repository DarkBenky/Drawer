# cython: profile=True
# cython: boundscheck=False
# cython: wraparound=False

import numpy as np
cimport numpy as np
from libc.math cimport pow

cpdef blur_cython(np.ndarray[np.uint8_t, ndim=3] color_layer , int radius):
    cdef int i , j , sum_r, sum_g, sum_b, count = 0 , x , y
    cdef int lenght = color_layer.shape[0]
    cdef int width = color_layer.shape[1]
    for i in range(lenght):
        for j in range(width):
            sum_r = 0
            sum_g = 0
            sum_b = 0
            count = 0
            for x in range(-radius, radius):
                for y in range(-radius, radius):
                    if 0 <= i + x < lenght and 0 <= j + y < width:
                        sum_r += color_layer[i + x, j + y, 0]
                        sum_g += color_layer[i + x, j + y, 1]
                        sum_b += color_layer[i + x, j + y, 2]
                        count += 1
            color_layer[i, j, 0] = sum_r // count
            color_layer[i, j, 1] = sum_g // count
            color_layer[i, j, 2] = sum_b // count

    return color_layer

cpdef remove_cython(np.ndarray[np.npy_bool, ndim=2] layers,
                          np.ndarray[np.uint8_t, ndim=3] colors,
                          np.ndarray[np.npy_bool, ndim=2] mask):

    layers &= ~mask
    colors[mask] = (0, 0, 0)  # Assign black color to elements corresponding to the mask

    return layers, colors

cpdef add_items_cython(np.ndarray[np.npy_bool, ndim=2] layers,
                       np.ndarray[np.uint8_t, ndim=3] colors,
                       np.ndarray[np.npy_bool, ndim=2] mask,
                       tuple color):

    layers |= mask
    colors[mask] = color  # Assign color to elements corresponding to the mask

    return layers, colors



cpdef draw_cython(int x, int y, int radius, int screen_width, int screen_height):
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

cpdef box_mask_cython(int x, int y , int size, int screen_width, int screen_height):
    cdef np.ndarray mask = np.zeros((screen_width, screen_height), dtype=bool)
    cdef int i, j, new_x, new_y

    for i in range(-size, size):
        for j in range(-size, size):
            new_x = x + i
            new_y = y + j
            if 0 <= new_x < screen_width and 0 <= new_y < screen_height:
                mask[new_x, new_y] = True

    return mask


