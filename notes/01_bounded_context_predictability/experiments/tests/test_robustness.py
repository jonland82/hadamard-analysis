import numpy as np
import pytest

from hadamard_note1.matrices import sylvester
from hadamard_note1.robustness import (
    audit_split,
    bootstrap_mean_interval,
    matrix_level_split,
)


def test_matrix_level_split_is_disjoint_and_exhaustive() -> None:
    train, test = matrix_level_split(10, 0.2, np.random.default_rng(123))

    assert len(train) == 8
    assert len(test) == 2
    assert set(train).isdisjoint(test)
    assert set(train) | set(test) == set(range(10))


def test_audit_split_passes_for_distinct_matrices() -> None:
    matrices = [sylvester(4), -sylvester(4)]

    report = audit_split(matrices, [0], [1])

    assert report["passed"] is True
    assert report["index_overlap"] == []
    assert report["matrix_digest_overlap"] == []


def test_audit_split_rejects_duplicate_matrix_across_sides() -> None:
    matrix = sylvester(4)

    with pytest.raises(ValueError, match="leakage audit failed"):
        audit_split([matrix, matrix.copy()], [0], [1])


def test_bootstrap_interval_contains_constant_mean() -> None:
    values = np.full(10, 0.125, dtype=np.float64)

    lower, upper = bootstrap_mean_interval(
        values,
        np.random.default_rng(123),
        resamples=100,
    )

    assert lower == pytest.approx(0.125)
    assert upper == pytest.approx(0.125)
