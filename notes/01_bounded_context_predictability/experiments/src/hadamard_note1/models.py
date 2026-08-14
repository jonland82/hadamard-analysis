"""Finite-context predictors and evaluation metrics."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from .contexts import ObservationBatch

def encode_contexts(contexts: NDArray[np.int64]) -> NDArray[np.int64]:
    """Encode sign contexts as binary integers, preserving left-to-right order."""

    if contexts.ndim != 2:
        raise ValueError("contexts must be two-dimensional")
    context_length = contexts.shape[1]
    if context_length > 20:
        raise ValueError("dense context encoding is limited to context length 20")
    powers = np.left_shift(1, np.arange(context_length - 1, -1, -1, dtype=np.int64))
    return ((contexts == 1).astype(np.int64) @ powers).astype(np.int64)


@dataclass
class SmoothedContextModel:
    """Binary fixed-context predictor with symmetric beta smoothing."""

    alpha: float = 0.5
    plus_counts: NDArray[np.int64] = field(
        default_factory=lambda: np.empty(0, dtype=np.int64), init=False
    )
    total_counts: NDArray[np.int64] = field(
        default_factory=lambda: np.empty(0, dtype=np.int64), init=False
    )
    context_length: int = field(default=0, init=False)

    def fit(self, batch: ObservationBatch) -> "SmoothedContextModel":
        if self.alpha <= 0:
            raise ValueError("alpha must be positive for held-out prediction")
        self.context_length = batch.context_length
        codes = encode_contexts(batch.contexts)
        size = 1 << self.context_length
        self.total_counts = np.bincount(codes, minlength=size).astype(np.int64)
        self.plus_counts = np.bincount(
            codes,
            weights=(batch.targets == 1).astype(np.int64),
            minlength=size,
        ).astype(np.int64)
        return self

    def probability_plus(self, context: NDArray[np.int64]) -> float:
        if context.shape != (self.context_length,):
            raise ValueError(f"expected one context of length {self.context_length}")
        code = int(encode_contexts(context.reshape(1, -1))[0])
        plus = int(self.plus_counts[code])
        total = int(self.total_counts[code])
        return (plus + self.alpha) / (total + 2.0 * self.alpha)

    def predict_probability_plus(self, contexts: NDArray[np.int64]) -> NDArray[np.float64]:
        if contexts.shape[1] != self.context_length:
            raise ValueError(f"expected contexts of length {self.context_length}")
        codes = encode_contexts(contexts)
        plus = self.plus_counts[codes].astype(np.float64)
        total = self.total_counts[codes].astype(np.float64)
        return (plus + self.alpha) / (total + 2.0 * self.alpha)

    def unseen_rate(self, contexts: NDArray[np.int64]) -> float:
        if contexts.shape[0] == 0:
            return float("nan")
        codes = encode_contexts(contexts)
        return float(np.mean(self.total_counts[codes] == 0))

    @property
    def contexts_seen(self) -> int:
        return int(np.count_nonzero(self.total_counts))


def binary_log_loss(targets: NDArray[np.int64], probability_plus: NDArray[np.float64]) -> float:
    if targets.size == 0:
        return float("nan")
    if probability_plus.shape != targets.shape:
        raise ValueError("probabilities and targets must have the same shape")
    if np.any((probability_plus <= 0) | (probability_plus >= 1)):
        raise ValueError("probabilities must lie strictly between zero and one")
    observed = np.where(targets == 1, probability_plus, 1.0 - probability_plus)
    return float(-np.mean(np.log(observed)))


def binary_accuracy(targets: NDArray[np.int64], probability_plus: NDArray[np.float64]) -> float:
    if targets.size == 0:
        return float("nan")
    predictions = np.where(probability_plus >= 0.5, 1, -1)
    return float(np.mean(predictions == targets))


def empirical_conditional_entropy(batch: ObservationBatch) -> float:
    """Return the in-sample MLE log loss, in nats per target."""

    if len(batch) == 0:
        return float("nan")
    codes = encode_contexts(batch.contexts)
    size = 1 << batch.context_length
    totals = np.bincount(codes, minlength=size).astype(np.int64)
    plus = np.bincount(
        codes,
        weights=(batch.targets == 1).astype(np.int64),
        minlength=size,
    ).astype(np.int64)
    minus = totals - plus
    total_loss = 0.0
    for counts in (minus, plus):
        supported = counts > 0
        total_loss -= float(np.sum(counts[supported] * np.log(counts[supported] / totals[supported])))
    return total_loss / len(batch)


def empirical_biases(batch: ObservationBatch) -> tuple[float, float]:
    """Return maximum and context-frequency-weighted absolute empirical bias."""

    if len(batch) == 0:
        return float("nan"), float("nan")
    codes = encode_contexts(batch.contexts)
    size = 1 << batch.context_length
    totals = np.bincount(codes, minlength=size).astype(np.int64)
    plus = np.bincount(
        codes,
        weights=(batch.targets == 1).astype(np.int64),
        minlength=size,
    ).astype(np.int64)
    supported = totals > 0
    biases = np.abs(plus[supported] / totals[supported] - 0.5)
    maximum = float(np.max(biases))
    average = float(np.sum(biases * totals[supported]) / len(batch))
    return maximum, average
