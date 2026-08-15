import numpy as np

from hadamard_note1.matrices import require_hadamard, sylvester
from hadamard_note1.note2 import fixed_anchor_variants, matrix_sequences


def test_fixed_anchor_variants_remain_normalized_and_hadamard() -> None:
    matrix = sylvester(8)
    variants = fixed_anchor_variants([matrix], np.random.default_rng(123))

    for variant in variants.values():
        result = require_hadamard(variant[0])
        assert np.all(result[0, :] == 1)
        assert np.all(result[:, 0] == 1)


def test_row_permutation_does_not_change_pooled_row_sequences() -> None:
    matrix = sylvester(8)
    row_variant = fixed_anchor_variants([matrix], np.random.default_rng(123))[
        "permute_rows_fixed_anchor"
    ][0]

    original = matrix_sequences([matrix], "rows")
    permuted = matrix_sequences([row_variant], "rows")

    assert sorted(map(tuple, original)) == sorted(map(tuple, permuted))


def test_column_traversal_is_row_traversal_of_transpose() -> None:
    matrix = sylvester(8)

    columns = matrix_sequences([matrix], "columns")
    transposed_rows = matrix_sequences([matrix.T.copy()], "rows")

    assert np.array_equal(columns, transposed_rows)
