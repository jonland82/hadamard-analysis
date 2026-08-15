import math

import numpy as np
import pytest

from hadamard_note1.contexts import ObservationBatch, extract_contexts
from hadamard_note1.evaluation import evaluate_context_model, evaluate_sequence_model
from hadamard_note1.matrices import sylvester
from hadamard_note1.models import (
    SmoothedContextModel,
    binary_log_loss,
    empirical_conditional_entropy,
)


def test_unseen_context_uses_symmetric_prior() -> None:
    batch = ObservationBatch(
        contexts=np.asarray([[1], [1]], dtype=np.int64),
        targets=np.asarray([1, -1], dtype=np.int64),
    )
    model = SmoothedContextModel(alpha=0.5).fit(batch)

    assert model.probability_plus(np.asarray([-1], dtype=np.int64)) == pytest.approx(0.5)


def test_log_loss_matches_fair_coin_baseline() -> None:
    targets = np.asarray([-1, 1, 1, -1], dtype=np.int64)
    probabilities = np.full(targets.size, 0.5)

    assert binary_log_loss(targets, probabilities) == pytest.approx(math.log(2.0))


def test_in_sample_mle_loss_is_nonincreasing_with_context_length() -> None:
    matrix = sylvester(16)
    losses = [
        empirical_conditional_entropy(
            extract_contexts(matrix, context_length, reset_at_row_boundary=False)
        )
        for context_length in range(1, 9)
    ]

    assert all(next_loss <= loss + 1e-12 for loss, next_loss in zip(losses, losses[1:]))


def test_matrix_level_evaluation_returns_finite_metrics() -> None:
    metrics = evaluate_context_model(
        [sylvester(4), sylvester(8), sylvester(16)],
        [sylvester(32)],
        3,
        reset_at_row_boundary=True,
    )

    assert metrics["train_observations"] > 0
    assert metrics["test_observations"] > 0
    assert 0 <= metrics["test_unseen_context_rate"] <= 1
    assert math.isfinite(float(metrics["train_log_loss"]))
    assert math.isfinite(float(metrics["test_log_loss"]))


def test_sequence_evaluator_matches_matrix_row_reset() -> None:
    train = [sylvester(8), sylvester(8)]
    test = [sylvester(16)]
    matrix_metrics = evaluate_context_model(
        train,
        test,
        3,
        reset_at_row_boundary=True,
    )
    sequence_metrics = evaluate_sequence_model(
        np.concatenate(train, axis=0),
        np.concatenate(test, axis=0),
        3,
    )

    for metric in (
        "train_log_loss",
        "test_log_loss",
        "test_accuracy",
        "test_unseen_context_rate",
    ):
        assert sequence_metrics[metric] == pytest.approx(matrix_metrics[metric])
