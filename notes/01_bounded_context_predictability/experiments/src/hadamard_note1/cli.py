"""Command-line entry points for Note 1 experiments."""

from __future__ import annotations

import argparse
import csv
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .corpus import SUPPORTED_ORDERS, download_corpus, load_corpus_file
from .evaluation import evaluate_context_model
from .matrices import (
    permuted_equivalent,
    random_normalized_balanced,
    random_normalized_iid,
    require_hadamard,
    sylvester,
)
from .robustness import audit_split, bootstrap_mean_interval, matrix_level_split


def _git_state() -> dict[str, object]:
    def run(*arguments: str) -> str:
        completed = subprocess.run(
            ["git", *arguments],
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    try:
        return {
            "commit": run("rev-parse", "HEAD"),
            "dirty": bool(run("status", "--porcelain")),
        }
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}


def _common_metadata() -> dict[str, object]:
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": [sys.executable, *sys.argv],
        "git": _git_state(),
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
    }


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run_smoke(max_context: int, alpha: float, output: Path) -> int:
    if max_context < 1:
        raise ValueError("max_context must be positive")

    train_orders = [4, 8, 16]
    test_orders = [32]
    train = [sylvester(order) for order in train_orders]
    test = [sylvester(order) for order in test_orders]
    for matrix in [*train, *test]:
        require_hadamard(matrix)

    rows: list[dict[str, object]] = []
    for configuration, reset in (("full_row_major", False), ("reset_at_row_boundary", True)):
        for context_length in range(1, max_context + 1):
            metrics = evaluate_context_model(
                train,
                test,
                context_length,
                alpha=alpha,
                reset_at_row_boundary=reset,
            )
            rows.append(
                {
                    "configuration": configuration,
                    "train_orders": ";".join(map(str, train_orders)),
                    "test_orders": ";".join(map(str, test_orders)),
                    **metrics,
                }
            )

    _write_csv(output, rows)
    metadata = {
        **_common_metadata(),
        "experiment": "smoke",
        "matrix_source": "generated:sylvester",
        "train_orders": train_orders,
        "test_orders": test_orders,
        "max_context": max_context,
        "alpha": alpha,
        "output": str(output),
    }
    metadata_path = output.with_name(f"{output.stem}_metadata.json")
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    print(f"wrote {len(rows)} result rows to {output}")
    print(f"wrote metadata to {metadata_path}")
    print("configuration             k  train_loss  test_loss  fair_loss  unseen")
    for row in rows:
        print(
            f"{str(row['configuration']):25} "
            f"{int(row['context_length']):2d} "
            f"{float(row['train_log_loss']):11.6f} "
            f"{float(row['test_log_loss']):10.6f} "
            f"{float(row['test_fair_log_loss']):10.6f} "
            f"{float(row['test_unseen_context_rate']):7.3f}"
        )
    return 0


def _parse_orders(value: str) -> list[int]:
    orders = [int(item.strip()) for item in value.split(",") if item.strip()]
    if not orders:
        raise argparse.ArgumentTypeError("at least one order is required")
    unsupported = sorted(set(orders) - set(SUPPORTED_ORDERS))
    if unsupported:
        raise argparse.ArgumentTypeError(
            f"unsupported orders {unsupported}; choose from {SUPPORTED_ORDERS}"
        )
    return orders


def run_corpus(
    orders: list[int],
    max_context: int,
    alpha: float,
    test_fraction: float,
    seed: int,
    data_directory: Path,
    output: Path,
    include_controls: bool,
) -> int:
    if max_context < 1:
        raise ValueError("max_context must be positive")
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must lie between zero and one")

    paths = download_corpus(orders, data_directory)
    rows: list[dict[str, object]] = []
    split_metadata: dict[str, object] = {}
    for order in orders:
        matrices = load_corpus_file(paths[order], order)
        if len(matrices) < 2:
            print(f"skipping order {order}: only one equivalence class")
            continue
        split_rng = np.random.default_rng(seed + order)
        indices = split_rng.permutation(len(matrices))
        test_count = max(1, int(round(test_fraction * len(matrices))))
        test_indices = sorted(int(index) for index in indices[:test_count])
        train_indices = sorted(int(index) for index in indices[test_count:])
        split_metadata[str(order)] = {
            "train_indices_zero_based": train_indices,
            "test_indices_zero_based": test_indices,
        }

        variants: dict[str, list[np.ndarray]] = {"hadamard": matrices}
        if include_controls:
            permutation_rng = np.random.default_rng(seed + 10_000 + order)
            balance_rng = np.random.default_rng(seed + 20_000 + order)
            iid_rng = np.random.default_rng(seed + 30_000 + order)
            variants["permuted_hadamard"] = [
                permuted_equivalent(matrix, permutation_rng) for matrix in matrices
            ]
            variants["balanced_rows"] = [
                random_normalized_balanced(order, balance_rng) for _ in matrices
            ]
            variants["iid_normalized"] = [
                random_normalized_iid(order, iid_rng) for _ in matrices
            ]

        for variant, variant_matrices in variants.items():
            train = [variant_matrices[index] for index in train_indices]
            test = [variant_matrices[index] for index in test_indices]
            for configuration, reset in (
                ("full_row_major", False),
                ("reset_at_row_boundary", True),
            ):
                for context_length in range(1, max_context + 1):
                    metrics = evaluate_context_model(
                        train,
                        test,
                        context_length,
                        alpha=alpha,
                        reset_at_row_boundary=reset,
                    )
                    rows.append(
                        {
                            "order": order,
                            "variant": variant,
                            "configuration": configuration,
                            "train_matrices": len(train),
                            "test_matrices": len(test),
                            **metrics,
                        }
                    )

    if not rows:
        raise ValueError("no selected order had enough matrices for a held-out split")
    _write_csv(output, rows)
    metadata = {
        **_common_metadata(),
        "experiment": "equivalence_class_holdout",
        "matrix_source": "Brendan McKay Hadamard equivalence-class corpus",
        "orders_requested": orders,
        "max_context": max_context,
        "alpha": alpha,
        "test_fraction": test_fraction,
        "seed": seed,
        "include_controls": include_controls,
        "splits": split_metadata,
        "output": str(output),
    }
    metadata_path = output.with_name(f"{output.stem}_metadata.json")
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    print(f"wrote {len(rows)} result rows to {output}")
    print(f"wrote metadata to {metadata_path}")
    print("order variant              configuration             k  test_loss  fair_delta  unseen")
    for row in rows:
        fair_delta = float(row["test_log_loss"]) - float(row["test_fair_log_loss"])
        print(
            f"{int(row['order']):5d} "
            f"{str(row['variant']):20} "
            f"{str(row['configuration']):25} "
            f"{int(row['context_length']):2d} "
            f"{float(row['test_log_loss']):10.6f} "
            f"{fair_delta:10.6f} "
            f"{float(row['test_unseen_context_rate']):7.3f}"
        )
    return 0


def _robustness_summary(
    rows: list[dict[str, object]],
    *,
    bootstrap_seed: int,
    bootstrap_resamples: int,
) -> list[dict[str, object]]:
    grouped: dict[tuple[int, int, str], dict[int, float]] = {}
    for row in rows:
        key = (int(row["order"]), int(row["context_length"]), str(row["variant"]))
        grouped.setdefault(key, {})[int(row["repetition"])] = float(
            row["gain_over_fair"]
        )

    summary: list[dict[str, object]] = []
    rng = np.random.default_rng(bootstrap_seed)
    for (order, context_length, variant), by_repetition in sorted(grouped.items()):
        values = np.asarray(list(by_repetition.values()), dtype=np.float64)
        lower, upper = bootstrap_mean_interval(
            values,
            rng,
            resamples=bootstrap_resamples,
        )
        summary.append(
            {
                "order": order,
                "context_length": context_length,
                "statistic": "gain_over_fair",
                "variant": variant,
                "comparator": "fair_coin",
                "repetitions": values.size,
                "mean": float(np.mean(values)),
                "standard_deviation": float(np.std(values, ddof=1)),
                "ci95_lower": lower,
                "ci95_upper": upper,
            }
        )

    contrasts = (
        ("hadamard", "permuted_hadamard"),
        ("permuted_hadamard", "balanced_rows"),
        ("hadamard", "balanced_rows"),
        ("hadamard", "iid_normalized"),
    )
    order_contexts = sorted({(key[0], key[1]) for key in grouped})
    for order, context_length in order_contexts:
        for variant, comparator in contrasts:
            left = grouped[(order, context_length, variant)]
            right = grouped[(order, context_length, comparator)]
            repetitions = sorted(set(left) & set(right))
            values = np.asarray(
                [left[repetition] - right[repetition] for repetition in repetitions],
                dtype=np.float64,
            )
            lower, upper = bootstrap_mean_interval(
                values,
                rng,
                resamples=bootstrap_resamples,
            )
            summary.append(
                {
                    "order": order,
                    "context_length": context_length,
                    "statistic": "paired_gain_difference",
                    "variant": variant,
                    "comparator": comparator,
                    "repetitions": values.size,
                    "mean": float(np.mean(values)),
                    "standard_deviation": float(np.std(values, ddof=1)),
                    "ci95_lower": lower,
                    "ci95_upper": upper,
                }
            )
    return summary


def run_robustness(
    orders: list[int],
    max_context: int,
    alpha: float,
    test_fraction: float,
    base_seed: int,
    repetitions: int,
    bootstrap_resamples: int,
    data_directory: Path,
    output: Path,
) -> int:
    """Run paired repeated holdouts for the five Note 1 robustness checks."""

    if max_context < 1:
        raise ValueError("max_context must be positive")
    if repetitions < 2:
        raise ValueError("at least two repetitions are required")
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must lie between zero and one")

    paths = download_corpus(orders, data_directory)
    corpora = {order: load_corpus_file(paths[order], order) for order in orders}
    rows: list[dict[str, object]] = []
    split_records: list[dict[str, object]] = []
    for repetition in range(repetitions):
        seed = base_seed + repetition
        print(
            f"robustness repetition {repetition + 1}/{repetitions} (seed {seed})",
            flush=True,
        )
        for order in orders:
            matrices = corpora[order]
            if len(matrices) < 2:
                print(f"skipping order {order}: only one equivalence class", flush=True)
                continue
            train_indices, test_indices = matrix_level_split(
                len(matrices),
                test_fraction,
                np.random.default_rng(seed + order),
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

            permutation_rng = np.random.default_rng(seed + 10_000 + order)
            balance_rng = np.random.default_rng(seed + 20_000 + order)
            iid_rng = np.random.default_rng(seed + 30_000 + order)
            variants: dict[str, list[np.ndarray]] = {
                "hadamard": matrices,
                "permuted_hadamard": [
                    permuted_equivalent(matrix, permutation_rng) for matrix in matrices
                ],
                "balanced_rows": [
                    random_normalized_balanced(order, balance_rng) for _ in matrices
                ],
                "iid_normalized": [
                    random_normalized_iid(order, iid_rng) for _ in matrices
                ],
            }
            for variant, variant_matrices in variants.items():
                train = [variant_matrices[index] for index in train_indices]
                test = [variant_matrices[index] for index in test_indices]
                for context_length in range(1, max_context + 1):
                    metrics = evaluate_context_model(
                        train,
                        test,
                        context_length,
                        alpha=alpha,
                        reset_at_row_boundary=True,
                    )
                    gain = float(metrics["test_fair_log_loss"]) - float(
                        metrics["test_log_loss"]
                    )
                    rows.append(
                        {
                            "repetition": repetition,
                            "seed": seed,
                            "order": order,
                            "variant": variant,
                            "configuration": "reset_at_row_boundary",
                            "train_matrices": len(train),
                            "test_matrices": len(test),
                            "gain_over_fair": gain,
                            **metrics,
                        }
                    )

    if not rows:
        raise ValueError("no selected order had enough matrices for a held-out split")
    _write_csv(output, rows)
    summary = _robustness_summary(
        rows,
        bootstrap_seed=base_seed + 90_000,
        bootstrap_resamples=bootstrap_resamples,
    )
    summary_path = output.with_name(f"{output.stem}_summary.csv")
    _write_csv(summary_path, summary)
    metadata = {
        **_common_metadata(),
        "experiment": "note1_five_robustness_checks",
        "matrix_source": "Brendan McKay Hadamard equivalence-class corpus",
        "orders_requested": orders,
        "max_context": max_context,
        "alpha": alpha,
        "test_fraction": test_fraction,
        "base_seed": base_seed,
        "repetitions": repetitions,
        "independent_equivalent_presentations_per_class": repetitions,
        "bootstrap_resamples": bootstrap_resamples,
        "confidence_interval": "paired-repetition percentile bootstrap interval for the mean",
        "configuration": "reset_at_row_boundary",
        "controls": ["fair_coin", "permuted_hadamard", "balanced_rows", "iid_normalized"],
        "leakage_policy": (
            "complete source equivalence-class representatives are assigned wholly to one split; "
            "all matched variants inherit the same source-class split"
        ),
        "all_leakage_audits_passed": all(
            bool(record["audit"]["passed"]) for record in split_records
        ),
        "splits": split_records,
        "raw_output": str(output),
        "summary_output": str(summary_path),
    }
    metadata_path = output.with_name(f"{output.stem}_metadata.json")
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} raw rows to {output}")
    print(f"wrote {len(summary)} summary rows to {summary_path}")
    print(f"wrote metadata and leakage audits to {metadata_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    smoke = subparsers.add_parser("smoke", help="run a generated Sylvester smoke experiment")
    smoke.add_argument("--max-context", type=int, default=8)
    smoke.add_argument("--alpha", type=float, default=0.5)
    smoke.add_argument("--output", type=Path, default=Path("results/smoke.csv"))
    corpus = subparsers.add_parser(
        "corpus",
        help="run matrix-level holdouts on classified equivalence representatives",
    )
    corpus.add_argument("--orders", type=_parse_orders, default=_parse_orders("16,20,24,28"))
    corpus.add_argument("--max-context", type=int, default=8)
    corpus.add_argument("--alpha", type=float, default=0.5)
    corpus.add_argument("--test-fraction", type=float, default=0.2)
    corpus.add_argument("--seed", type=int, default=20260814)
    corpus.add_argument("--data-directory", type=Path, default=Path("data/raw"))
    corpus.add_argument("--output", type=Path, default=Path("results/corpus_holdout.csv"))
    corpus.add_argument(
        "--include-controls",
        action="store_true",
        help="also evaluate independently permuted Hadamards and balanced-row controls",
    )
    robustness = subparsers.add_parser(
        "robustness",
        help="run repeated paired splits, permutations, controls, and bootstrap intervals",
    )
    robustness.add_argument(
        "--orders", type=_parse_orders, default=_parse_orders("16,20,24,28")
    )
    robustness.add_argument("--max-context", type=int, default=12)
    robustness.add_argument("--alpha", type=float, default=0.5)
    robustness.add_argument("--test-fraction", type=float, default=0.2)
    robustness.add_argument("--base-seed", type=int, default=20260814)
    robustness.add_argument("--repetitions", type=int, default=20)
    robustness.add_argument("--bootstrap-resamples", type=int, default=10_000)
    robustness.add_argument("--data-directory", type=Path, default=Path("data/raw"))
    robustness.add_argument(
        "--output", type=Path, default=Path("results/robustness_raw.csv")
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "smoke":
        return run_smoke(args.max_context, args.alpha, args.output)
    if args.command == "corpus":
        return run_corpus(
            args.orders,
            args.max_context,
            args.alpha,
            args.test_fraction,
            args.seed,
            args.data_directory,
            args.output,
            args.include_controls,
        )
    if args.command == "robustness":
        return run_robustness(
            args.orders,
            args.max_context,
            args.alpha,
            args.test_fraction,
            args.base_seed,
            args.repetitions,
            args.bootstrap_resamples,
            args.data_directory,
            args.output,
        )
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
