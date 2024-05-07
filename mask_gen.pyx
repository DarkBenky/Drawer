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
    cdef np.ndarray new_mask = color_layer.copy()
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
            new_mask[i, j, 0] = sum_r // count
            new_mask[i, j, 1] = sum_g // count
            new_mask[i, j, 2] = sum_b // count

    return new_mask



cpdef increase_contrast_cython(np.ndarray[np.uint8_t, ndim=3] color_layer, float factor):
    cdef int length = color_layer.shape[0]
    cdef int width = color_layer.shape[1]
    cdef int channels = color_layer.shape[2]
    cdef int i, j, k
    cdef float avg_intensity, adjusted_intensity

    # Calculate the average intensity of the image
    avg_intensity = 0.0
    for i in range(length):
        for j in range(width):
            for k in range(channels):
                avg_intensity += color_layer[i, j, k]
    avg_intensity /= (length * width * channels)

    # Increase the contrast by adjusting each pixel intensity
    for i in range(length):
        for j in range(width):
            for k in range(channels):
                adjusted_intensity = (color_layer[i, j, k] - avg_intensity) * factor + avg_intensity
                color_layer[i, j, k] = max(0, min(255, int(adjusted_intensity)))

    return color_layer


# TODO: Implement the following functions in Python

cpdef decrease_contrast_cython(np.ndarray[np.uint8_t, ndim=3] color_layer, int radius, float factor):
    cdef int i, j, sum_r, sum_g, sum_b, count
    cdef int length = color_layer.shape[0]
    cdef int width = color_layer.shape[1]
    cdef float contrast_factor
    

    for i in range(length):
        for j in range(width):
            sum_r = 0
            sum_g = 0
            sum_b = 0
            count = 0
            for x in range(-radius, radius):
                for y in range(-radius, radius):
                    if 0 <= i + x < length and 0 <= j + y < width:
                        sum_r += color_layer[i + x, j + y, 0]
                        sum_g += color_layer[i + x, j + y, 1]
                        sum_b += color_layer[i + x, j + y, 2]
                        count += 1
            avg_r = sum_r // count
            avg_g = sum_g // count
            avg_b = sum_b // count
            # Decrease contrast
            contrast_factor = 1.0 - factor
            color_layer[i, j, 0] = max(0, min(255, int((avg_r - 128) * contrast_factor + 128)))
            color_layer[i, j, 1] = max(0, min(255, int((avg_g - 128) * contrast_factor + 128)))
            color_layer[i, j, 2] = max(0, min(255, int((avg_b - 128) * contrast_factor + 128)))

    return color_layer

# TODO: Implement the functions in Python

cpdef edge_cython(np.ndarray[np.uint8_t, ndim=3] image, tuple edge_color, int threshold):
    cdef int height = image.shape[0]
    cdef int width = image.shape[1]
    cdef int channels = image.shape[2]
    cdef np.ndarray[np.uint8_t, ndim=3] result = image.copy()
    cdef int i, j, k
    cdef int gx, gy
    cdef int gradient

    for i in range(1, height - 1):
        for j in range(1, width - 1):
            for k in range(channels):
                gx = (image[i - 1, j + 1, k] + 2 * image[i, j + 1, k] + image[i + 1, j + 1, k]) - \
                     (image[i - 1, j - 1, k] + 2 * image[i, j - 1, k] + image[i + 1, j - 1, k])
                
                gy = (image[i + 1, j - 1, k] + 2 * image[i + 1, j, k] + image[i + 1, j + 1, k]) - \
                     (image[i - 1, j - 1, k] + 2 * image[i - 1, j, k] + image[i - 1, j + 1, k])
                
                gradient = int((gx**2 + gy**2)**0.5)
                if gradient > threshold:
                    result[i, j, :] = edge_color
    return result


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

cpdef draw_layers_cython(np.ndarray[np.npy_bool, ndim=3] layers,
                                    np.ndarray[np.uint8_t, ndim=4] colors):
    cdef np.ndarray[np.uint8_t, ndim=3] result = np.zeros((layers.shape[1],layers.shape[2],3), dtype=np.uint8)
    cdef int i
    cdef int leyers_count = layers.shape[0]
    for i in range(leyers_count):
        result[layers[i]] = colors[i, layers[i], :]
    return result

#cpdef draw_layers_cython_v2(np.ndarray[np.npy_bool, ndim=3] layers,
#                                   np.ndarray[np.uint8_t, ndim=4] colors):
#    cdef int width = layers.shape[1]
#    cdef int height = layers.shape[2]
#    cdef np.ndarray[np.uint8_t, ndim=3] result = np.zeros((width, height, 3), dtype=np.uint8)
#    cdef int i, j, k, num_layers = layers.shape[0]
#    cdef np.npy_bool[:, :] covered = np.zeros((width, height), dtype=bool)
#    
#    for i in range(num_layers):
#        for j in range(width):
#            for k in range(height):
#                if layers[i, j, k] and not covered[j, k]:
#                    result[j, k] = colors[i, j, k]
#                    covered[j, k] = True
#
#    return result

cpdef draw_layer_cython(np.ndarray[np.npy_bool, ndim=3] layers,
                        np.ndarray[np.uint8_t, ndim=4] colors,
                        current_layer : int):
    cdef np.ndarray[np.uint8_t, ndim=3] result = np.zeros((layers.shape[1],layers.shape[2],3), dtype=np.uint8)
    result[layers[current_layer]] = colors[current_layer][layers[current_layer]]
    return result