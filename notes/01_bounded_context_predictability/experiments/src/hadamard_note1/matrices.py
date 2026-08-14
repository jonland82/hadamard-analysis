"""Exact Hadamard-matrix construction, normalization, and verification."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

SignMatrix = NDArray[np.int64]


def _as_integer_matrix(matrix: ArrayLike) -> SignMatrix:
    array = np.asarray(matrix)
    if array.ndim != 2:
        raise ValueError(f"expected a two-dimensional matrix, got shape {array.shape}")
    if not np.issubdtype(array.dtype, np.integer):
        if not np.all(np.equal(array, np.round(array))):
            raise ValueError("matrix contains noninteger entries")
    return np.asarray(array, dtype=np.int64)


def require_sign_matrix(matrix: ArrayLike, *, square: bool = False) -> SignMatrix:
    """Return an integer sign-matrix copy or raise if entries/shape are invalid."""
    array = _as_integer_matrix(matrix)
    rows, columns = array.shape
    if square and rows != columns:
        raise ValueError(f"sign matrix must be square, got {array.shape}")
    if not np.all((array == -1) | (array == 1)):
        raise ValueError("matrix entries must all belong to {-1, +1}")
    return array.copy()


def require_hadamard(matrix: ArrayLike) -> SignMatrix:
    """Return an integer copy of ``matrix`` or raise if it is not Hadamard."""

    array = require_sign_matrix(matrix, square=True)
    rows = array.shape[0]

    gram = array @ array.T
    expected = rows * np.eye(rows, dtype=np.int64)
    if not np.array_equal(gram, expected):
        raise ValueError("matrix does not satisfy H @ H.T = d I")
    return array.copy()


def normalize_hadamard(matrix: ArrayLike) -> SignMatrix:
    """Normalize a Hadamard matrix so its first row and column are all +1."""

    array = require_hadamard(matrix)
    array *= array[:, [0]]
    array *= array[[0], :]
    normalized = require_hadamard(array)
    if not np.all(normalized[0, :] == 1) or not np.all(normalized[:, 0] == 1):
        raise AssertionError("internal error: normalization did not fix first row/column")
    return normalized


def sylvester(order: int) -> SignMatrix:
    """Construct the Sylvester Hadamard matrix of a power-of-two order."""

    if order < 1 or order & (order - 1):
        raise ValueError("Sylvester order must be a positive power of two")

    matrix = np.ones((1, 1), dtype=np.int64)
    while matrix.shape[0] < order:
        matrix = np.block([[matrix, matrix], [matrix, -matrix]])
    return normalize_hadamard(matrix)


def permuted_equivalent(matrix: ArrayLike, rng: np.random.Generator) -> SignMatrix:
    """Apply independent random row/column permutations and renormalize."""

    array = require_hadamard(matrix)
    row_permutation = rng.permutation(array.shape[0])
    column_permutation = rng.permutation(array.shape[1])
    return normalize_hadamard(array[row_permutation][:, column_permutation])


def random_normalized_balanced(order: int, rng: np.random.Generator) -> SignMatrix:
    """Generate a normalized sign matrix whose nonfirst rows are exactly balanced."""

    if order < 2 or order % 2:
        raise ValueError("balanced control order must be an even integer at least two")
    matrix = np.ones((order, order), dtype=np.int64)
    minus_count = order // 2
    candidates = np.arange(1, order)
    for row in range(1, order):
        minus_columns = rng.choice(candidates, size=minus_count, replace=False)
        matrix[row, minus_columns] = -1
    return matrix


def random_normalized_iid(order: int, rng: np.random.Generator) -> SignMatrix:
    """Generate IID interior signs with a deterministic +1 first row and column."""

    if order < 2:
        raise ValueError("IID control order must be at least two")
    matrix = np.ones((order, order), dtype=np.int64)
    matrix[1:, 1:] = rng.choice(np.asarray([-1, 1], dtype=np.int64), size=(order - 1, order - 1))
    return matrix
