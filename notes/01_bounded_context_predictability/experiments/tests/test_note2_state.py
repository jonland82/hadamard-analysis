from math import comb

import numpy as np

from hadamard_note1.matrices import sylvester
from hadamard_note1.note2_state import (
    block_starts,
    hypergeometric_probabilities,
    iter_regional_observations,
)


def test_hypergeometric_distribution_has_correct_mass_and_mean() -> None:
    probabilities = hypergeometric_probabilities(successes=7, population=12, draws=4)

    assert probabilities.shape == (5,)
    assert np.isclose(np.sum(probabilities), 1.0)
    assert np.isclose(probabilities @ np.arange(5), 4 * 7 / 12)
    assert np.isclose(probabilities[2], comb(7, 2) * comb(5, 2) / comb(12, 4))


def test_terminal_block_targets_are_forced_by_constraint_state() -> None:
    matrix = sylvester(8)
    observations = list(iter_regional_observations(matrix, block_size=2, context_length=2))
    terminal = [observation for observation in observations if observation.position == 6]

    assert terminal
    for observation in terminal:
        probabilities = hypergeometric_probabilities(
            observation.successes_remaining,
            observation.positions_remaining,
            2,
        )
        assert probabilities[observation.outcome] == 1.0


def test_block_grid_includes_terminal_state_without_duplicates() -> None:
    starts = block_starts(order=28, block_size=8, context_length=4)

    assert starts == [4, 12, 20]
    assert len(starts) == len(set(starts))
