import numpy as np
import pytest

from hadamard_note1.matrices import require_hadamard, sylvester
from hadamard_note1.note3_solver import (
    POLICIES,
    ExactHadamardSolver,
    _as_bool,
    canonical_seed,
    make_completion_instance,
    partial_sum_feasible,
    prefix_can_exceed,
    sign_code,
)


def test_csv_boolean_parser_does_not_treat_false_text_as_true() -> None:
    assert _as_bool(True)
    assert _as_bool("True")
    assert not _as_bool(False)
    assert not _as_bool("False")
    with pytest.raises(ValueError):
        _as_bool("maybe")


def test_partial_sum_feasibility_checks_magnitude_and_parity() -> None:
    assert partial_sum_feasible(2, 2)
    assert partial_sum_feasible(-2, 2)
    assert partial_sum_feasible(0, 2)
    assert not partial_sum_feasible(3, 2)
    assert not partial_sum_feasible(1, 2)


def test_prefix_lower_bound_uses_plus_first_sign_code() -> None:
    lower = (1, 1, -1, -1)
    assert sign_code((1, 1, -1, -1)) < sign_code((1, -1, 1, -1))
    assert prefix_can_exceed((1,), lower)
    assert prefix_can_exceed((1, 1), lower)
    assert not prefix_can_exceed((1, 1, 1), lower)
    assert prefix_can_exceed((1, -1), lower)
    assert not prefix_can_exceed(lower, lower)


@pytest.mark.parametrize("policy", POLICIES)
def test_every_policy_constructs_an_exact_order_four_matrix(policy: str) -> None:
    result = ExactHadamardSolver(
        policy=policy,
        block_size=2,
        tie_seed=17,
        max_nodes=10_000,
        max_seconds=5,
    ).solve(canonical_seed(4))
    assert result.solved
    assert result.termination == "solved"
    require_hadamard(np.asarray(result.solution))


def test_planted_completion_hides_target_and_preserves_prefix() -> None:
    matrix = sylvester(8)
    instance = make_completion_instance(
        matrix,
        class_index=0,
        hidden_rows=3,
        presentation_seed=123,
    )
    assert len(instance.seed_rows) == 5
    result = ExactHadamardSolver(
        policy="all_pair_product",
        block_size=2,
        tie_seed=456,
        max_nodes=100_000,
        max_seconds=5,
    ).solve(instance.seed_rows)
    assert result.solved
    assert result.solution is not None
    assert result.solution[: len(instance.seed_rows)] == instance.seed_rows
    require_hadamard(np.asarray(result.solution))


def test_node_budget_is_reported_without_false_unsat_claim() -> None:
    result = ExactHadamardSolver(
        policy="random_order",
        block_size=1,
        tie_seed=5,
        max_nodes=1,
        max_seconds=5,
    ).solve(canonical_seed(8))
    assert not result.solved
    assert result.termination == "node_budget"
