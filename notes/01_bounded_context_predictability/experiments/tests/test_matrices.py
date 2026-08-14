import numpy as np
import pytest

from hadamard_note1.corpus import parse_hex_matrix
from hadamard_note1.matrices import (
    normalize_hadamard,
    permuted_equivalent,
    random_normalized_balanced,
    random_normalized_iid,
    require_hadamard,
    sylvester,
)


@pytest.mark.parametrize("order", [1, 2, 4, 8, 16, 32])
def test_sylvester_is_exact_hadamard(order: int) -> None:
    matrix = sylvester(order)
    assert matrix.dtype == np.int64
    assert np.array_equal(matrix @ matrix.T, order * np.eye(order, dtype=np.int64))
    assert np.all(matrix[0, :] == 1)
    assert np.all(matrix[:, 0] == 1)


def test_normalization_preserves_hadamard_property() -> None:
    matrix = sylvester(8)
    matrix[[1, 5], :] *= -1
    matrix[:, [2, 6]] *= -1

    normalized = normalize_hadamard(matrix)

    require_hadamard(normalized)
    assert np.all(normalized[0, :] == 1)
    assert np.all(normalized[:, 0] == 1)


@pytest.mark.parametrize("order", [0, 3, 6, 12])
def test_sylvester_rejects_non_power_of_two(order: int) -> None:
    with pytest.raises(ValueError, match="power of two"):
        sylvester(order)


def test_verifier_rejects_nonorthogonal_sign_matrix() -> None:
    with pytest.raises(ValueError, match="does not satisfy"):
        require_hadamard(np.ones((4, 4), dtype=np.int64))


def test_parse_mckay_hex_representation() -> None:
    matrix = parse_hex_matrix("F A C 9", 4)

    require_hadamard(matrix)
    assert np.all(matrix[0, :] == 1)
    assert np.all(matrix[:, 0] == 1)


def test_permuted_equivalent_is_normalized_hadamard() -> None:
    matrix = permuted_equivalent(sylvester(16), np.random.default_rng(42))

    require_hadamard(matrix)
    assert np.all(matrix[0, :] == 1)
    assert np.all(matrix[:, 0] == 1)


def test_balanced_control_has_normalized_balanced_rows() -> None:
    matrix = random_normalized_balanced(12, np.random.default_rng(42))

    assert np.all(matrix[0, :] == 1)
    assert np.all(matrix[:, 0] == 1)
    assert np.all(np.sum(matrix[1:, :], axis=1) == 0)


def test_iid_control_is_normalized_sign_matrix() -> None:
    matrix = random_normalized_iid(12, np.random.default_rng(42))

    assert np.all((matrix == -1) | (matrix == 1))
    assert np.all(matrix[0, :] == 1)
    assert np.all(matrix[:, 0] == 1)
