"""Matrix-level training and held-out evaluation."""

from __future__ import annotations

from collections.abc import Sequence
from math import log

import numpy as np
from numpy.typing import NDArray

from .contexts import ObservationBatch, concatenate_batches, extract_contexts
from .models import (
    SmoothedContextModel,
    binary_accuracy,
    binary_log_loss,
    empirical_biases,
    empirical_conditional_entropy,
)


def _extract_many(
    matrices: Sequence[NDArray[np.int64]],
    context_length: int,
    **extraction_options: bool,
) -> ObservationBatch:
    return concatenate_batches(
        [
            extract_contexts(matrix, context_length, **extraction_options)
            for matrix in matrices
        ],
        context_length,
    )


def _constant_probabilities(size: int, probability_plus: float) -> NDArray[np.float64]:
    return np.full(size, probability_plus, dtype=np.float64)


def _evaluate_batches(
    train: ObservationBatch,
    test: ObservationBatch,
    context_length: int,
    *,
    alpha: float,
    reset_at_row_boundary: bool,
    exclude_first_row: bool,
    exclude_first_column: bool,
) -> dict[str, float | int | bool]:
    if len(train) == 0 or len(test) == 0:
        raise ValueError("both training and test splits must produce observations")

    model = SmoothedContextModel(alpha=alpha).fit(train)
    train_probabilities = model.predict_probability_plus(train.contexts)
    test_probabilities = model.predict_probability_plus(test.contexts)

    marginal_plus = (int(np.sum(train.targets == 1)) + alpha) / (len(train) + 2 * alpha)
    test_marginal = _constant_probabilities(len(test), marginal_plus)
    test_fair = _constant_probabilities(len(test), 0.5)
    train_eps_max, train_eps_avg = empirical_biases(train)
    test_eps_max, test_eps_avg = empirical_biases(test)

    return {
        "context_length": context_length,
        "alpha": alpha,
        "reset_at_row_boundary": reset_at_row_boundary,
        "exclude_first_row": exclude_first_row,
        "exclude_first_column": exclude_first_column,
        "train_observations": len(train),
        "test_observations": len(test),
        "contexts_seen": model.contexts_seen,
        "test_unseen_context_rate": model.unseen_rate(test.contexts),
        "train_log_loss": binary_log_loss(train.targets, train_probabilities),
        "test_log_loss": binary_log_loss(test.targets, test_probabilities),
        "test_fair_log_loss": binary_log_loss(test.targets, test_fair),
        "test_marginal_log_loss": binary_log_loss(test.targets, test_marginal),
        "train_accuracy": binary_accuracy(train.targets, train_probabilities),
        "test_accuracy": binary_accuracy(test.targets, test_probabilities),
        "train_mle_log_loss": empirical_conditional_entropy(train),
        "train_epsilon_max": train_eps_max,
        "train_epsilon_avg": train_eps_avg,
        "test_epsilon_max": test_eps_max,
        "test_epsilon_avg": test_eps_avg,
        "fair_log_loss_constant": log(2.0),
    }


def evaluate_context_model(
    train_matrices: Sequence[NDArray[np.int64]],
    test_matrices: Sequence[NDArray[np.int64]],
    context_length: int,
    *,
    alpha: float = 0.5,
    reset_at_row_boundary: bool = False,
    exclude_first_row: bool = False,
    exclude_first_column: bool = False,
) -> dict[str, float | int | bool]:
    """Fit one context model and return training/held-out metrics."""

    options = {
        "reset_at_row_boundary": reset_at_row_boundary,
        "exclude_first_row": exclude_first_row,
        "exclude_first_column": exclude_first_column,
    }
    train = _extract_many(train_matrices, context_length, **options)
    test = _extract_many(test_matrices, context_length, **options)
    return _evaluate_batches(
        train,
        test,
        context_length,
        alpha=alpha,
        **options,
    )


def _batch_from_sequences(
    sequences: NDArray[np.int64],
    context_length: int,
) -> ObservationBatch:
    if sequences.ndim != 2:
        raise ValueError("sequences must have shape (sequence_count, sequence_length)")
    if not np.all((sequences == -1) | (sequences == 1)):
        raise ValueError("sequences must contain only signs")
    if sequences.shape[1] <= context_length:
        raise ValueError("sequence length must exceed context length")
    windows = np.lib.stride_tricks.sliding_window_view(
        sequences,
        context_length + 1,
        axis=1,
    )
    return ObservationBatch(
        contexts=np.asarray(windows[..., :-1].reshape(-1, context_length), dtype=np.int64),
        targets=np.asarray(windows[..., -1].reshape(-1), dtype=np.int64),
    )


def evaluate_sequence_model(
    train_sequences: NDArray[np.int64],
    test_sequences: NDArray[np.int64],
    context_length: int,
    *,
    alpha: float = 0.5,
    exclude_first_row: bool = False,
    exclude_first_column: bool = False,
) -> dict[str, float | int | bool]:
    """Evaluate already-oriented independent sequences without per-matrix extraction."""

    train = _batch_from_sequences(train_sequences, context_length)
    test = _batch_from_sequences(test_sequences, context_length)
    return _evaluate_batches(
        train,
        test,
        context_length,
        alpha=alpha,
        reset_at_row_boundary=True,
        exclude_first_row=exclude_first_row,
        exclude_first_column=exclude_first_column,
    )
