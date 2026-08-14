"""Traversal and bounded-context extraction."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .matrices import require_sign_matrix

SignArray = NDArray[np.int64]


@dataclass(frozen=True)
class ObservationBatch:
    """Context/target observations extracted from one or more sequences."""

    contexts: SignArray
    targets: SignArray

    def __post_init__(self) -> None:
        if self.contexts.ndim != 2:
            raise ValueError("contexts must have shape (observations, context_length)")
        if self.targets.ndim != 1:
            raise ValueError("targets must be one-dimensional")
        if self.contexts.shape[0] != self.targets.shape[0]:
            raise ValueError("contexts and targets must contain the same observations")
        if not np.all((self.contexts == -1) | (self.contexts == 1)):
            raise ValueError("contexts must contain only signs")
        if not np.all((self.targets == -1) | (self.targets == 1)):
            raise ValueError("targets must contain only signs")

    def __len__(self) -> int:
        return int(self.targets.size)

    @property
    def context_length(self) -> int:
        return int(self.contexts.shape[1])


def _observations_from_sequence(sequence: SignArray, context_length: int) -> ObservationBatch:
    if sequence.size <= context_length:
        return ObservationBatch(
            contexts=np.empty((0, context_length), dtype=np.int64),
            targets=np.empty(0, dtype=np.int64),
        )
    contexts = np.lib.stride_tricks.sliding_window_view(sequence, context_length)[:-1]
    targets = sequence[context_length:]
    return ObservationBatch(
        contexts=np.asarray(contexts, dtype=np.int64).copy(),
        targets=np.asarray(targets, dtype=np.int64).copy(),
    )


def extract_contexts(
    matrix: SignArray,
    context_length: int,
    *,
    reset_at_row_boundary: bool = False,
    exclude_first_row: bool = False,
    exclude_first_column: bool = False,
) -> ObservationBatch:
    """Extract row-major contexts with explicit normalization/boundary ablations."""

    if context_length < 1:
        raise ValueError("context_length must be at least one")
    work = require_sign_matrix(matrix, square=True)
    if exclude_first_row:
        work = work[1:, :]
    if exclude_first_column:
        work = work[:, 1:]

    if not reset_at_row_boundary:
        return _observations_from_sequence(work.reshape(-1), context_length)

    batches = [_observations_from_sequence(row, context_length) for row in work]
    nonempty = [batch for batch in batches if len(batch)]
    if not nonempty:
        return ObservationBatch(
            contexts=np.empty((0, context_length), dtype=np.int64),
            targets=np.empty(0, dtype=np.int64),
        )
    return ObservationBatch(
        contexts=np.concatenate([batch.contexts for batch in nonempty], axis=0),
        targets=np.concatenate([batch.targets for batch in nonempty], axis=0),
    )


def concatenate_batches(batches: list[ObservationBatch], context_length: int) -> ObservationBatch:
    """Concatenate batches while retaining a well-shaped empty result."""

    nonempty = [batch for batch in batches if len(batch)]
    if not nonempty:
        return ObservationBatch(
            contexts=np.empty((0, context_length), dtype=np.int64),
            targets=np.empty(0, dtype=np.int64),
        )
    if any(batch.context_length != context_length for batch in nonempty):
        raise ValueError("all batches must have the requested context length")
    return ObservationBatch(
        contexts=np.concatenate([batch.contexts for batch in nonempty], axis=0),
        targets=np.concatenate([batch.targets for batch in nonempty], axis=0),
    )
