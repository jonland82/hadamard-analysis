import numpy as np
import pytest

from hadamard_note1.contexts import extract_contexts
from hadamard_note1.matrices import sylvester


@pytest.mark.parametrize("order", [4, 8, 16, 32])
def test_row_reset_removes_exactly_the_boundary_transitions(order: int) -> None:
    matrix = sylvester(order)
    full = extract_contexts(matrix, 1, reset_at_row_boundary=False)
    reset = extract_contexts(matrix, 1, reset_at_row_boundary=True)

    assert len(full) == order * order - 1
    assert len(reset) == order * (order - 1)
    assert len(full) - len(reset) == order - 1


@pytest.mark.parametrize("order", [4, 8, 16, 32])
def test_within_row_one_step_target_is_neutral_given_supported_sign(order: int) -> None:
    batch = extract_contexts(sylvester(order), 1, reset_at_row_boundary=True)

    for sign in (-1, 1):
        targets = batch.targets[batch.contexts[:, 0] == sign]
        assert targets.size > 0
        assert np.sum(targets == 1) * 2 == targets.size


def test_contexts_do_not_cross_rows_when_reset() -> None:
    matrix = sylvester(4)
    batch = extract_contexts(matrix, 2, reset_at_row_boundary=True)

    assert len(batch) == 4 * (4 - 2)
    expected_first_context = matrix[0, :2]
    assert np.array_equal(batch.contexts[0], expected_first_context)
    assert batch.targets[0] == matrix[0, 2]


def test_exclusion_options_apply_before_traversal() -> None:
    matrix = sylvester(8)
    batch = extract_contexts(
        matrix,
        1,
        reset_at_row_boundary=True,
        exclude_first_row=True,
        exclude_first_column=True,
    )

    assert len(batch) == (8 - 1) * (8 - 2)
