import numpy as np


DCT_BLOCK_SIZE  = 8
BIT_TARGET_COEFF  = (4, 4)


JPEG_QUANTIZATION_LUMINANCE  = np.array(
    [
        [ 8,  6,  5,  8, 12, 20, 26, 31],
        [ 6,  6,  7, 10, 13, 29, 30, 28],
        [ 7,  7,  8, 12, 20, 29, 35, 28],
        [ 7,  9, 11, 15, 26, 44, 40, 31],
        [ 9, 11, 19, 28, 34, 55, 52, 39],
        [12, 18, 28, 32, 41, 52, 57, 46],
        [25, 32, 39, 44, 52, 61, 60, 51],
        [36, 46, 48, 49, 56, 50, 52, 50],
    ],
    dtype=np.float64,
)


JPEG_QUANTIZATION_CHROMINANCE = np.array(
    [
        [ 9,  9, 12, 24, 50, 50, 50, 50],
        [ 9, 11, 13, 33, 50, 50, 50, 50],
        [12, 13, 28, 50, 50, 50, 50, 50],
        [24, 33, 50, 50, 50, 50, 50, 50],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [50, 50, 50, 50, 50, 50, 50, 50],
    ],
    dtype=np.float64,
)


def build_dct_basis_matrix(size):
    row_indices = np.arange(0, size).reshape(size, 1)
    col_indices = np.arange(size)
    scaling_factors = np.where(row_indices == 0, np.sqrt(1 / size), np.sqrt(2 / size))
    angles = np.pi * (2 * col_indices + 1) * row_indices / (2 * size)
    return scaling_factors * np.cos(angles)


DCT_MATRIX = build_dct_basis_matrix(DCT_BLOCK_SIZE)
