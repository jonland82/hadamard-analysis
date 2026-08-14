"""Utilities for repeated, leakage-audited robustness experiments."""

from __future__ import annotations

import hashlib
from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

from .matrices import SignMatrix


def matrix_digest(matrix: SignMatrix) -> str:
    """Return a stable digest that includes shape, dtype, and matrix entries."""

    array = np.ascontiguousarray(matrix, dtype=np.int64)
    digest = hashlib.sha256()
    digest.update(str(array.shape).encode("ascii"))
    digest.update(array.dtype.str.encode("ascii"))
    digest.update(array.tobytes())
    return digest.hexdigest()


def matrix_level_split(
    matrix_count: int,
    test_fraction: float,
    rng: np.random.Generator,
) -> tuple[list[int], list[int]]:
    """Return disjoint train/test indices for a complete-matrix holdout."""

    if matrix_count < 2:
        raise ValueError("at least two matrices are required for a holdout")
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must lie between zero and one")
    permutation = rng.permutation(matrix_count)
    test_count = min(matrix_count - 1, max(1, int(round(test_fraction * matrix_count))))
    test_indices = sorted(int(index) for index in permutation[:test_count])
    train_indices = sorted(int(index) for index in permutation[test_count:])
    return train_indices, test_indices


def audit_split(
    matrices: Sequence[SignMatrix],
    train_indices: Sequence[int],
    test_indices: Sequence[int],
) -> dict[str, object]:
    """Validate class/index/hash separation and return an auditable report."""

    expected = set(range(len(matrices)))
    train = set(train_indices)
    test = set(test_indices)
    index_overlap = sorted(train & test)
    missing_indices = sorted(expected - train - test)
    unexpected_indices = sorted((train | test) - expected)
    digests = [matrix_digest(matrix) for matrix in matrices]
    train_digests = {digests[index] for index in train}
    test_digests = {digests[index] for index in test}
    digest_overlap = sorted(train_digests & test_digests)
    duplicate_source_digests = len(set(digests)) != len(digests)
    passed = not (
        index_overlap
        or missing_indices
        or unexpected_indices
        or digest_overlap
        or duplicate_source_digests
    )
    report: dict[str, object] = {
        "passed": passed,
        "train_count": len(train),
        "test_count": len(test),
        "index_overlap": index_overlap,
        "matrix_digest_overlap": digest_overlap,
        "missing_indices": missing_indices,
        "unexpected_indices": unexpected_indices,
        "duplicate_source_digests": duplicate_source_digests,
    }
    if not passed:
        raise ValueError(f"matrix-level leakage audit failed: {report}")
    return report


def bootstrap_mean_interval(
    values: NDArray[np.float64],
    rng: np.random.Generator,
    *,
    resamples: int = 10_000,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Return a percentile bootstrap interval for the mean across repetitions."""

    observations = np.asarray(values, dtype=np.float64)
    if observations.ndim != 1 or observations.size < 2:
        raise ValueError("at least two one-dimensional observations are required")
    if resamples < 1:
        raise ValueError("resamples must be positive")
    if not 0 < confidence < 1:
        raise ValueError("confidence must lie between zero and one")
    indices = rng.integers(0, observations.size, size=(resamples, observations.size))
    means = np.mean(observations[indices], axis=1)
    tail = (1.0 - confidence) / 2.0
    lower, upper = np.quantile(means, [tail, 1.0 - tail])
    return float(lower), float(upper)
