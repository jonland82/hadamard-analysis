import numpy as np

from hadamard_note1.matrices import sylvester
from hadamard_note1.note2_ranking import (
    all_sign_blocks,
    rank_one_state,
    tie_aware_rank_metrics,
)


def test_all_sign_blocks_are_complete_and_unique() -> None:
    blocks = all_sign_blocks(4)

    assert blocks.shape == (16, 4)
    assert np.all((blocks == -1) | (blocks == 1))
    assert np.unique(blocks, axis=0).shape[0] == 16


def test_uniform_ties_have_random_percentile_and_top1_probability() -> None:
    metrics = tie_aware_rank_metrics(np.zeros(8), true_index=3)

    assert metrics["percentile"] == 0.5
    assert metrics["top1_probability"] == 1 / 8


def test_observed_block_is_ranked_among_exactly_feasible_candidates() -> None:
    matrix = sylvester(8)
    candidates = all_sign_blocks(2)

    ranked = rank_one_state(
        matrix,
        row_index=3,
        position=2,
        block_size=2,
        candidates=candidates,
        random_pair_offset=0,
        probability_cache={},
    )

    assert ranked is not None
    feasible_candidates, policy_metrics = ranked
    assert feasible_candidates >= 2
    assert set(policy_metrics) == {
        "random_order",
        "balance_only",
        "balance_random_pair",
        "balance_pressured_pair",
        "all_pair_product",
        "minimum_max_pressure",
    }
