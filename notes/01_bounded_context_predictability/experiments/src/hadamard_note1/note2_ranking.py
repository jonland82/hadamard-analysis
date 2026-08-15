"""Note 2 closure: rank nonterminal candidate blocks from constraint state."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .corpus import download_corpus, load_corpus_file
from .matrices import SignMatrix, permuted_equivalent
from .note2 import _common_metadata, _write_csv, fixed_anchor_variants
from .note2_state import (
    BLOCK_SIZES,
    ORDERS,
    PRESENTATIONS,
    block_starts,
    hypergeometric_probabilities,
    progress_stage,
)
from .robustness import audit_split, bootstrap_mean_interval, matrix_level_split

POLICIES = (
    "random_order",
    "balance_only",
    "balance_random_pair",
    "balance_pressured_pair",
    "all_pair_product",
    "minimum_max_pressure",
)
RANKING_STAGES = ("early", "middle")


def all_sign_blocks(block_size: int) -> np.ndarray:
    """Return every sign block in lexicographic binary order."""

    codes = np.arange(1 << block_size, dtype=np.int64)[:, None]
    shifts = np.arange(block_size - 1, -1, -1, dtype=np.int64)
    bits = (codes >> shifts) & 1
    return np.where(bits == 1, 1, -1).astype(np.int64)


def candidate_state_specs(
    matrix_count: int,
    order: int,
    block_size: int,
    context_length: int,
    stage: str,
) -> list[tuple[int, int, int]]:
    """List nonterminal matrix/row/position states with a prior nonfirst row."""

    if stage not in RANKING_STAGES:
        raise ValueError(f"unsupported ranking stage {stage!r}")
    positions = [
        position
        for position in block_starts(order, block_size, context_length)
        if position + block_size < order and progress_stage(position, order) == stage
    ]
    return [
        (matrix_index, row_index, position)
        for matrix_index in range(matrix_count)
        for row_index in range(2, order)
        for position in positions
    ]


def tie_aware_rank_metrics(scores: np.ndarray, true_index: int) -> dict[str, float]:
    """Return ranking metrics with uniform tie-breaking."""

    true_score = float(scores[true_index])
    greater = int(np.count_nonzero(scores > true_score + 1e-12))
    equal = int(np.count_nonzero(np.isclose(scores, true_score, rtol=0.0, atol=1e-12)))
    candidate_count = scores.size
    average_rank = 1.0 + greater + 0.5 * (equal - 1)
    return {
        "percentile": (candidate_count - average_rank + 0.5) / candidate_count,
        "reciprocal_rank": 1.0 / average_rank,
        "top_decile": float(average_rank <= max(1, int(np.ceil(candidate_count / 10)))),
        "top1_probability": (1.0 / equal) if greater == 0 else 0.0,
    }


@dataclass
class RankingAccumulator:
    states: int = 0
    feasible_candidates_sum: int = 0
    percentile_sum: float = 0.0
    reciprocal_rank_sum: float = 0.0
    top_decile_sum: float = 0.0
    top1_probability_sum: float = 0.0

    def update(self, feasible_candidates: int, metrics: dict[str, float]) -> None:
        self.states += 1
        self.feasible_candidates_sum += feasible_candidates
        self.percentile_sum += metrics["percentile"]
        self.reciprocal_rank_sum += metrics["reciprocal_rank"]
        self.top_decile_sum += metrics["top_decile"]
        self.top1_probability_sum += metrics["top1_probability"]

    def as_dict(self) -> dict[str, float | int]:
        return {
            "states": self.states,
            "mean_feasible_candidates": self.feasible_candidates_sum / self.states,
            "mean_percentile": self.percentile_sum / self.states,
            "mean_percentile_minus_random": self.percentile_sum / self.states - 0.5,
            "mean_reciprocal_rank": self.reciprocal_rank_sum / self.states,
            "top_decile_rate": self.top_decile_sum / self.states,
            "expected_top1_rate": self.top1_probability_sum / self.states,
        }


def rank_one_state(
    matrix: SignMatrix,
    row_index: int,
    position: int,
    block_size: int,
    candidates: np.ndarray,
    random_pair_offset: int,
    probability_cache: dict[tuple[int, int, int], np.ndarray],
) -> tuple[int, dict[str, dict[str, float]]] | None:
    """Rank the observed block among all immediately feasible candidates."""

    order = matrix.shape[0]
    remaining = order - position
    after_remaining = remaining - block_size
    if after_remaining <= 0:
        raise ValueError("ranking states must be nonterminal")
    row = matrix[row_index]
    prefix = row[:position]
    true_block = row[position : position + block_size]
    row_sum = int(np.sum(prefix))
    candidate_row_sums = np.sum(candidates, axis=1, dtype=np.int64)
    row_after = row_sum + candidate_row_sums
    row_feasible = np.abs(row_after) <= after_remaining

    prior_rows = matrix[1:row_index]
    partial_inner_products = prior_rows[:, :position] @ prefix
    candidate_increments = candidates @ prior_rows[:, position : position + block_size].T
    pair_after = partial_inner_products + candidate_increments
    pair_feasible = np.all(np.abs(pair_after) <= after_remaining, axis=1)
    feasible_mask = row_feasible & pair_feasible
    feasible_indices = np.flatnonzero(feasible_mask)
    if feasible_indices.size < 2:
        return None
    matches = np.flatnonzero(np.all(candidates == true_block, axis=1))
    if matches.size != 1 or not feasible_mask[int(matches[0])]:
        raise AssertionError("the observed valid block must be an exactly feasible candidate")
    true_feasible_index = int(np.flatnonzero(feasible_indices == int(matches[0]))[0])

    feasible_blocks = candidates[feasible_indices]
    feasible_row_sums = candidate_row_sums[feasible_indices]
    feasible_pair_increments = candidate_increments[feasible_indices]
    row_successes = (remaining - row_sum) // 2
    row_probabilities = probability_cache.setdefault(
        (row_successes, remaining, block_size),
        hypergeometric_probabilities(row_successes, remaining, block_size),
    )
    row_plus_counts = ((feasible_row_sums + block_size) // 2).astype(np.int64)
    balance_scores = np.log(row_probabilities[row_plus_counts])

    pair_scores = np.empty((feasible_indices.size, prior_rows.shape[0]), dtype=np.float64)
    for pair_index, partial_inner_product in enumerate(partial_inner_products):
        agreements_remaining = (remaining - int(partial_inner_product)) // 2
        probabilities = probability_cache.setdefault(
            (agreements_remaining, remaining, block_size),
            hypergeometric_probabilities(agreements_remaining, remaining, block_size),
        )
        agreement_counts = (
            (feasible_pair_increments[:, pair_index] + block_size) // 2
        ).astype(np.int64)
        pair_scores[:, pair_index] = np.log(probabilities[agreement_counts])

    random_pair_index = random_pair_offset % prior_rows.shape[0]
    pressured_pair_index = int(np.argmax(np.abs(partial_inner_products)))
    maximum_pressure = np.maximum(
        np.abs(row_after[feasible_indices]),
        np.max(np.abs(pair_after[feasible_indices]), axis=1),
    )
    policy_scores = {
        "random_order": np.zeros(feasible_indices.size, dtype=np.float64),
        "balance_only": balance_scores,
        "balance_random_pair": balance_scores + pair_scores[:, random_pair_index],
        "balance_pressured_pair": balance_scores + pair_scores[:, pressured_pair_index],
        "all_pair_product": balance_scores + np.sum(pair_scores, axis=1),
        "minimum_max_pressure": -maximum_pressure.astype(np.float64),
    }
    return feasible_indices.size, {
        policy: tie_aware_rank_metrics(scores, true_feasible_index)
        for policy, scores in policy_scores.items()
    }


def evaluate_ranking(
    matrices: list[SignMatrix],
    specs: list[tuple[int, int, int]],
    block_size: int,
    *,
    random_pair_seed: int,
) -> list[dict[str, object]]:
    candidates = all_sign_blocks(block_size)
    accumulators = {policy: RankingAccumulator() for policy in POLICIES}
    probability_cache: dict[tuple[int, int, int], np.ndarray] = {}
    skipped_forced = 0
    for spec_index, (matrix_index, row_index, position) in enumerate(specs):
        ranked = rank_one_state(
            matrices[matrix_index],
            row_index,
            position,
            block_size,
            candidates,
            random_pair_seed + 104_729 * spec_index + 101 * row_index + position,
            probability_cache,
        )
        if ranked is None:
            skipped_forced += 1
            continue
        feasible_candidates, metrics = ranked
        for policy in POLICIES:
            accumulators[policy].update(feasible_candidates, metrics[policy])
    if not accumulators["random_order"].states:
        raise ValueError("no ambiguous nonterminal states were available for ranking")
    return [
        {
            "policy": policy,
            "sampled_states": len(specs),
            "skipped_forced_states": skipped_forced,
            **accumulator.as_dict(),
        }
        for policy, accumulator in accumulators.items()
    ]


def summarize(
    rows: list[dict[str, object]],
    *,
    bootstrap_seed: int,
    bootstrap_resamples: int,
) -> list[dict[str, object]]:
    keys = ("order", "presentation", "block_size", "stage", "policy")
    grouped: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(tuple(row[key] for key in keys), []).append(row)
    rng = np.random.default_rng(bootstrap_seed)
    summary: list[dict[str, object]] = []
    for key, group in sorted(grouped.items()):
        effects = np.asarray(
            [float(row["mean_percentile_minus_random"]) for row in group]
        )
        lower, upper = bootstrap_mean_interval(
            effects, rng, resamples=bootstrap_resamples
        )
        summary.append(
            {
                **dict(zip(keys, key, strict=True)),
                "repetitions": len(group),
                "mean_states": float(np.mean([int(row["states"]) for row in group])),
                "mean_feasible_candidates": float(
                    np.mean([float(row["mean_feasible_candidates"]) for row in group])
                ),
                "mean_percentile": float(
                    np.mean([float(row["mean_percentile"]) for row in group])
                ),
                "mean_percentile_minus_random": float(np.mean(effects)),
                "percentile_effect_ci95_lower": lower,
                "percentile_effect_ci95_upper": upper,
                "mean_reciprocal_rank": float(
                    np.mean([float(row["mean_reciprocal_rank"]) for row in group])
                ),
                "mean_top_decile_rate": float(
                    np.mean([float(row["top_decile_rate"]) for row in group])
                ),
                "mean_expected_top1_rate": float(
                    np.mean([float(row["expected_top1_rate"]) for row in group])
                ),
            }
        )
    return summary


def run(
    *,
    orders: list[int],
    block_sizes: list[int],
    context_length: int,
    max_states_per_stage: int,
    test_fraction: float,
    base_seed: int,
    repetitions: int,
    bootstrap_resamples: int,
    data_directory: Path,
    output: Path,
) -> None:
    if repetitions < 2:
        raise ValueError("at least two repetitions are required")
    if max_states_per_stage < 1:
        raise ValueError("max states per stage must be positive")
    paths = download_corpus(orders, data_directory)
    corpora = {order: load_corpus_file(paths[order], order) for order in orders}
    rows: list[dict[str, object]] = []
    split_records: list[dict[str, object]] = []

    for repetition in range(repetitions):
        seed = base_seed + repetition
        print(f"Ranking repetition {repetition + 1}/{repetitions}", flush=True)
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
                matrices, np.random.default_rng(seed + 80_000 + order)
            )["permute_both_fixed_anchor"]
            unrestricted_rng = np.random.default_rng(seed + 90_000 + order)
            presentations["permute_both_renormalized"] = [
                permuted_equivalent(matrix, unrestricted_rng) for matrix in matrices
            ]
            test_presentations = {
                name: [represented[index] for index in test_indices]
                for name, represented in presentations.items()
            }

            for block_size in block_sizes:
                for stage_index, stage in enumerate(RANKING_STAGES):
                    specs = candidate_state_specs(
                        len(test_indices), order, block_size, context_length, stage
                    )
                    sample_rng = np.random.default_rng(
                        seed + 100_000 + order + 100 * block_size + stage_index
                    )
                    if len(specs) > max_states_per_stage:
                        selected = sample_rng.choice(
                            len(specs), size=max_states_per_stage, replace=False
                        )
                        specs = [specs[int(index)] for index in sorted(selected)]
                    for presentation, test_matrices in test_presentations.items():
                        metrics = evaluate_ranking(
                            test_matrices,
                            specs,
                            block_size,
                            random_pair_seed=seed + 110_000 + order,
                        )
                        for metric in metrics:
                            rows.append(
                                {
                                    "repetition": repetition,
                                    "seed": seed,
                                    "order": order,
                                    "presentation": presentation,
                                    "block_size": block_size,
                                    "stage": stage,
                                    "test_matrices": len(test_matrices),
                                    **metric,
                                }
                            )

    _write_csv(output, rows)
    summary = summarize(
        rows,
        bootstrap_seed=base_seed + 120_000,
        bootstrap_resamples=bootstrap_resamples,
    )
    summary_path = output.with_name(f"{output.stem}_summary.csv")
    _write_csv(summary_path, summary)
    metadata = {
        **_common_metadata(),
        "experiment": "note2_nonterminal_candidate_block_ranking",
        "orders": orders,
        "block_sizes": block_sizes,
        "context_length": context_length,
        "ranking_stages": list(RANKING_STAGES),
        "max_states_per_stage": max_states_per_stage,
        "policies": list(POLICIES),
        "test_fraction": test_fraction,
        "base_seed": base_seed,
        "repetitions": repetitions,
        "bootstrap_resamples": bootstrap_resamples,
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
    parser.add_argument("--max-states-per-stage", type=int, default=500)
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
        max_states_per_stage=args.max_states_per_stage,
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
