"""Note 2: state-aware regional prediction from exact Hadamard constraints."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from math import comb, log, sqrt
from pathlib import Path

import numpy as np

from .corpus import download_corpus, load_corpus_file
from .matrices import SignMatrix, permuted_equivalent
from .note2 import _common_metadata, _write_csv, fixed_anchor_variants
from .robustness import audit_split, bootstrap_mean_interval, matrix_level_split

ORDERS = (24, 28)
BLOCK_SIZES = (2, 4, 8)
PRESENTATIONS = (
    "catalog",
    "permute_both_fixed_anchor",
    "permute_both_renormalized",
)
TARGETS = ("row_plus_count", "pressured_pair_agreement_count")
MODELS = ("fair_binomial", "serialized_context", "constraint_state", "state_plus_context")
STAGES = ("all", "early", "middle", "late")


@dataclass(frozen=True)
class RegionalObservation:
    """One categorical next-block target and its exact correction state."""

    target_name: str
    outcome: int
    successes_remaining: int
    positions_remaining: int
    context_code: int
    position: int
    stage: str


def encode_sign_context(context: np.ndarray) -> int:
    """Encode a one-dimensional sign context as a binary integer."""

    code = 0
    for value in context:
        code = (code << 1) | int(value == 1)
    return code


def progress_stage(position: int, order: int) -> str:
    fraction = position / order
    if fraction < 1.0 / 3.0:
        return "early"
    if fraction < 2.0 / 3.0:
        return "middle"
    return "late"


def block_starts(order: int, block_size: int, context_length: int) -> list[int]:
    """Return a broad construction-stage grid, including the terminal block."""

    starts = list(range(context_length, order - block_size + 1, block_size))
    terminal = order - block_size
    if terminal >= context_length and terminal not in starts:
        starts.append(terminal)
    return sorted(starts)


def hypergeometric_probabilities(
    successes: int,
    population: int,
    draws: int,
) -> np.ndarray:
    """Distribution of successes in draws without replacement."""

    if not 0 <= successes <= population:
        raise ValueError("success count must lie inside the population")
    if not 0 <= draws <= population:
        raise ValueError("draw count must lie inside the population")
    denominator = comb(population, draws)
    probabilities = np.zeros(draws + 1, dtype=np.float64)
    for outcome in range(draws + 1):
        if outcome <= successes and draws - outcome <= population - successes:
            probabilities[outcome] = (
                comb(successes, outcome)
                * comb(population - successes, draws - outcome)
                / denominator
            )
    return probabilities


def binomial_probabilities(draws: int) -> np.ndarray:
    return np.asarray([comb(draws, outcome) / 2**draws for outcome in range(draws + 1)])


def iter_regional_observations(
    matrix: SignMatrix,
    block_size: int,
    context_length: int,
) -> Iterator[RegionalObservation]:
    """Yield balance and most-pressured-pair targets from a completed matrix."""

    order = matrix.shape[0]
    for row_index in range(1, order):
        row = matrix[row_index]
        for position in block_starts(order, block_size, context_length):
            remaining = order - position
            prefix = row[:position]
            block = row[position : position + block_size]
            plus_remaining = order // 2 - int(np.count_nonzero(prefix == 1))
            yield RegionalObservation(
                target_name="row_plus_count",
                outcome=int(np.count_nonzero(block == 1)),
                successes_remaining=plus_remaining,
                positions_remaining=remaining,
                context_code=encode_sign_context(row[position - context_length : position]),
                position=position,
                stage=progress_stage(position, order),
            )

            if row_index < 2:
                continue
            prior_rows = matrix[1:row_index]
            prefix_products = prior_rows[:, :position] * prefix
            partial_inner_products = np.sum(prefix_products, axis=1, dtype=np.int64)
            pressured_offset = int(np.argmax(np.abs(partial_inner_products)))
            partial_inner_product = int(partial_inner_products[pressured_offset])
            prior_row = prior_rows[pressured_offset]
            product_context = (
                row[position - context_length : position]
                * prior_row[position - context_length : position]
            )
            product_block = block * prior_row[position : position + block_size]
            agreements_remaining = (remaining - partial_inner_product) // 2
            yield RegionalObservation(
                target_name="pressured_pair_agreement_count",
                outcome=int(np.count_nonzero(product_block == 1)),
                successes_remaining=agreements_remaining,
                positions_remaining=remaining,
                context_code=encode_sign_context(product_context),
                position=position,
                stage=progress_stage(position, order),
            )


@dataclass
class RegionalTables:
    block_size: int
    context_counts: dict[str, dict[int, np.ndarray]] = field(default_factory=dict)
    joint_counts: dict[str, dict[tuple[int, int, int], np.ndarray]] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        self.context_counts = {target: {} for target in TARGETS}
        self.joint_counts = {target: {} for target in TARGETS}

    def update(self, observation: RegionalObservation) -> None:
        context_table = self.context_counts[observation.target_name]
        context_counts = context_table.setdefault(
            observation.context_code,
            np.zeros(self.block_size + 1, dtype=np.int64),
        )
        context_counts[observation.outcome] += 1
        key = (
            observation.position,
            observation.successes_remaining,
            observation.context_code,
        )
        joint_table = self.joint_counts[observation.target_name]
        joint_counts = joint_table.setdefault(
            key,
            np.zeros(self.block_size + 1, dtype=np.int64),
        )
        joint_counts[observation.outcome] += 1


def fit_tables(
    matrices: Iterable[SignMatrix],
    block_size: int,
    context_length: int,
) -> RegionalTables:
    tables = RegionalTables(block_size)
    for matrix in matrices:
        for observation in iter_regional_observations(matrix, block_size, context_length):
            tables.update(observation)
    return tables


def _context_probabilities(
    counts: np.ndarray | None,
    outcomes: int,
    alpha: float,
) -> np.ndarray:
    if counts is None:
        counts = np.zeros(outcomes, dtype=np.int64)
    return (counts + alpha) / (int(np.sum(counts)) + alpha * outcomes)


def _state_context_probabilities(
    counts: np.ndarray | None,
    constraint: np.ndarray,
    prior_strength: float,
) -> np.ndarray:
    if counts is None:
        return constraint
    return (counts + prior_strength * constraint) / (int(np.sum(counts)) + prior_strength)


@dataclass
class MetricAccumulator:
    log_loss_sum: float = 0.0
    squared_error_sum: float = 0.0
    absolute_error_sum: float = 0.0
    observations: int = 0

    def update(self, outcome: int, probabilities: np.ndarray) -> None:
        probability = float(probabilities[outcome])
        if probability <= 0:
            raise ValueError("a valid held-out outcome received zero probability")
        expectation = float(probabilities @ np.arange(probabilities.size))
        error = expectation - outcome
        self.log_loss_sum -= log(probability)
        self.squared_error_sum += error * error
        self.absolute_error_sum += abs(error)
        self.observations += 1


def evaluate_tables(
    matrices: Iterable[SignMatrix],
    tables: RegionalTables,
    block_size: int,
    context_length: int,
    *,
    alpha: float,
    prior_strength: float,
) -> list[dict[str, object]]:
    accumulators = {
        (target, stage, model): MetricAccumulator()
        for target in TARGETS
        for stage in STAGES
        for model in MODELS
    }
    fair = binomial_probabilities(block_size)
    constraint_cache: dict[tuple[int, int], np.ndarray] = {}
    for matrix in matrices:
        for observation in iter_regional_observations(matrix, block_size, context_length):
            state = (observation.successes_remaining, observation.positions_remaining)
            constraint = constraint_cache.setdefault(
                state,
                hypergeometric_probabilities(*state, block_size),
            )
            context_counts = tables.context_counts[observation.target_name].get(
                observation.context_code
            )
            context = _context_probabilities(context_counts, block_size + 1, alpha)
            joint_key = (
                observation.position,
                observation.successes_remaining,
                observation.context_code,
            )
            joint_counts = tables.joint_counts[observation.target_name].get(joint_key)
            state_context = _state_context_probabilities(
                joint_counts,
                constraint,
                prior_strength,
            )
            predictions = {
                "fair_binomial": fair,
                "serialized_context": context,
                "constraint_state": constraint,
                "state_plus_context": state_context,
            }
            for stage in ("all", observation.stage):
                for model, probabilities in predictions.items():
                    accumulators[(observation.target_name, stage, model)].update(
                        observation.outcome,
                        probabilities,
                    )

    results: list[dict[str, object]] = []
    for target in TARGETS:
        for stage in STAGES:
            stage_metrics = {
                model: accumulators[(target, stage, model)] for model in MODELS
            }
            if stage_metrics["fair_binomial"].observations == 0:
                continue
            fair_loss = (
                stage_metrics["fair_binomial"].log_loss_sum
                / stage_metrics["fair_binomial"].observations
            )
            constraint_loss = (
                stage_metrics["constraint_state"].log_loss_sum
                / stage_metrics["constraint_state"].observations
            )
            for model, metric in stage_metrics.items():
                log_loss = metric.log_loss_sum / metric.observations
                results.append(
                    {
                        "target": target,
                        "stage": stage,
                        "model": model,
                        "observations": metric.observations,
                        "log_loss": log_loss,
                        "gain_over_fair": fair_loss - log_loss,
                        "gain_over_constraint": constraint_loss - log_loss,
                        "rmse_count": sqrt(metric.squared_error_sum / metric.observations),
                        "mae_count": metric.absolute_error_sum / metric.observations,
                    }
                )
    return results


def summarize(
    rows: list[dict[str, object]],
    *,
    bootstrap_seed: int,
    bootstrap_resamples: int,
) -> list[dict[str, object]]:
    keys = (
        "order",
        "block_size",
        "presentation",
        "target",
        "stage",
        "model",
    )
    grouped: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(tuple(row[key] for key in keys), []).append(row)
    rng = np.random.default_rng(bootstrap_seed)
    summary: list[dict[str, object]] = []
    for key, group in sorted(grouped.items()):
        gains_fair = np.asarray([float(row["gain_over_fair"]) for row in group])
        gains_constraint = np.asarray(
            [float(row["gain_over_constraint"]) for row in group]
        )
        fair_lower, fair_upper = bootstrap_mean_interval(
            gains_fair, rng, resamples=bootstrap_resamples
        )
        constraint_lower, constraint_upper = bootstrap_mean_interval(
            gains_constraint, rng, resamples=bootstrap_resamples
        )
        summary.append(
            {
                **dict(zip(keys, key, strict=True)),
                "repetitions": len(group),
                "mean_observations": float(
                    np.mean([int(row["observations"]) for row in group])
                ),
                "mean_log_loss": float(np.mean([float(row["log_loss"]) for row in group])),
                "mean_gain_over_fair": float(np.mean(gains_fair)),
                "gain_over_fair_ci95_lower": fair_lower,
                "gain_over_fair_ci95_upper": fair_upper,
                "mean_gain_over_constraint": float(np.mean(gains_constraint)),
                "gain_over_constraint_ci95_lower": constraint_lower,
                "gain_over_constraint_ci95_upper": constraint_upper,
                "mean_rmse_count": float(
                    np.mean([float(row["rmse_count"]) for row in group])
                ),
                "mean_mae_count": float(
                    np.mean([float(row["mae_count"]) for row in group])
                ),
            }
        )
    return summary


def run(
    *,
    orders: list[int],
    block_sizes: list[int],
    context_length: int,
    alpha: float,
    prior_strength: float,
    test_fraction: float,
    base_seed: int,
    repetitions: int,
    bootstrap_resamples: int,
    data_directory: Path,
    output: Path,
) -> None:
    if repetitions < 2:
        raise ValueError("at least two repetitions are required")
    paths = download_corpus(orders, data_directory)
    corpora = {order: load_corpus_file(paths[order], order) for order in orders}
    rows: list[dict[str, object]] = []
    split_records: list[dict[str, object]] = []

    for repetition in range(repetitions):
        seed = base_seed + repetition
        print(f"State experiment repetition {repetition + 1}/{repetitions}", flush=True)
        for order in orders:
            matrices = corpora[order]
            train_indices, test_indices = matrix_level_split(
                len(matrices), test_fraction, np.random.default_rng(seed + order)
            )
            audit = audit_split(matrices, train_indices, test_indices)
            split_records.append(
                {
                    "repetition": repetition,
                    "seed": seed,
                    "order": order,
                    "train_class_indices_zero_based": train_indices,
                    "test_class_indices_zero_based": test_indices,
                    "audit": audit,
                }
            )
            presentations: dict[str, list[SignMatrix]] = {"catalog": matrices}
            presentations["permute_both_fixed_anchor"] = fixed_anchor_variants(
                matrices, np.random.default_rng(seed + 60_000 + order)
            )["permute_both_fixed_anchor"]
            unrestricted_rng = np.random.default_rng(seed + 70_000 + order)
            presentations["permute_both_renormalized"] = [
                permuted_equivalent(matrix, unrestricted_rng) for matrix in matrices
            ]

            for presentation, represented in presentations.items():
                train = [represented[index] for index in train_indices]
                test = [represented[index] for index in test_indices]
                for block_size in block_sizes:
                    tables = fit_tables(train, block_size, context_length)
                    metrics = evaluate_tables(
                        test,
                        tables,
                        block_size,
                        context_length,
                        alpha=alpha,
                        prior_strength=prior_strength,
                    )
                    for metric in metrics:
                        rows.append(
                            {
                                "repetition": repetition,
                                "seed": seed,
                                "order": order,
                                "presentation": presentation,
                                "block_size": block_size,
                                "context_length": context_length,
                                "train_matrices": len(train),
                                "test_matrices": len(test),
                                **metric,
                            }
                        )

    _write_csv(output, rows)
    summary = summarize(
        rows,
        bootstrap_seed=base_seed + 95_000,
        bootstrap_resamples=bootstrap_resamples,
    )
    summary_path = output.with_name(f"{output.stem}_summary.csv")
    _write_csv(summary_path, summary)
    metadata = {
        **_common_metadata(),
        "experiment": "note2_state_aware_regional_prediction",
        "orders": orders,
        "block_sizes": block_sizes,
        "context_length": context_length,
        "alpha": alpha,
        "state_context_prior_strength": prior_strength,
        "test_fraction": test_fraction,
        "base_seed": base_seed,
        "repetitions": repetitions,
        "bootstrap_resamples": bootstrap_resamples,
        "presentations": list(PRESENTATIONS),
        "targets": list(TARGETS),
        "models": list(MODELS),
        "all_leakage_audits_passed": all(
            bool(record["audit"]["passed"]) for record in split_records
        ),
        "splits": split_records,
        "raw_output": str(output),
        "summary_output": str(summary_path),
    }
    metadata_path = output.with_name(f"{output.stem}_metadata.json")
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} raw rows to {output}", flush=True)
    print(f"wrote {len(summary)} summary rows to {summary_path}", flush=True)


def _parse_int_list(value: str, allowed: tuple[int, ...], label: str) -> list[int]:
    values = [int(item.strip()) for item in value.split(",") if item.strip()]
    if not values or set(values) - set(allowed):
        raise argparse.ArgumentTypeError(f"{label} must be drawn from {allowed}")
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--orders", type=lambda value: _parse_int_list(value, ORDERS, "orders"), default=list(ORDERS)
    )
    parser.add_argument(
        "--block-sizes",
        type=lambda value: _parse_int_list(value, BLOCK_SIZES, "block sizes"),
        default=list(BLOCK_SIZES),
    )
    parser.add_argument("--context-length", type=int, default=4)
    parser.add_argument("--alpha", type=float, default=0.5)
    parser.add_argument("--prior-strength", type=float, default=8.0)
    parser.add_argument("--test-fraction", type=float, default=0.2)
    parser.add_argument("--base-seed", type=int, default=20260814)
    parser.add_argument("--repetitions", type=int, default=20)
    parser.add_argument("--bootstrap-resamples", type=int, default=10_000)
    parser.add_argument("--data-directory", type=Path, default=Path("data/raw"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(
        orders=args.orders,
        block_sizes=args.block_sizes,
        context_length=args.context_length,
        alpha=args.alpha,
        prior_strength=args.prior_strength,
        test_fraction=args.test_fraction,
        base_seed=args.base_seed,
        repetitions=args.repetitions,
        bootstrap_resamples=args.bootstrap_resamples,
        data_directory=args.data_directory,
        output=args.output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
