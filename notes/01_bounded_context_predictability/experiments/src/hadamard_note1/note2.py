"""Note 2: paired representation, traversal, and normalization ablations."""

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

from .corpus import download_corpus, load_corpus_file
from .evaluation import evaluate_sequence_model
from .matrices import SignMatrix, permuted_equivalent
from .robustness import audit_split, bootstrap_mean_interval, matrix_level_split

ORDERS = (24, 28)
TRAVERSALS = ("rows", "columns")
REGIONS = {
    "all": (False, False),
    "exclude_first_row": (True, False),
    "exclude_first_column": (False, True),
    "interior": (True, True),
}
ORDERING_VARIANTS = (
    "catalog",
    "permute_rows_fixed_anchor",
    "permute_columns_fixed_anchor",
    "permute_both_fixed_anchor",
    "permute_both_renormalized",
)


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


def fixed_anchor_variants(
    matrices: list[SignMatrix],
    rng: np.random.Generator,
) -> dict[str, list[SignMatrix]]:
    """Create paired permutations that retain the normalized first row/column."""

    row_only: list[SignMatrix] = []
    column_only: list[SignMatrix] = []
    both: list[SignMatrix] = []
    for matrix in matrices:
        order = matrix.shape[0]
        row_permutation = np.concatenate(
            (np.asarray([0], dtype=np.int64), rng.permutation(np.arange(1, order)))
        )
        column_permutation = np.concatenate(
            (np.asarray([0], dtype=np.int64), rng.permutation(np.arange(1, order)))
        )
        row_only.append(matrix[row_permutation, :].copy())
        column_only.append(matrix[:, column_permutation].copy())
        both.append(matrix[row_permutation][:, column_permutation].copy())
    return {
        "permute_rows_fixed_anchor": row_only,
        "permute_columns_fixed_anchor": column_only,
        "permute_both_fixed_anchor": both,
    }


def matrix_sequences(
    matrices: list[SignMatrix],
    traversal: str,
    *,
    exclude_first_row: bool = False,
    exclude_first_column: bool = False,
) -> np.ndarray:
    """Return pooled independent row or column sequences for a matrix collection."""

    if traversal not in TRAVERSALS:
        raise ValueError(f"unknown traversal {traversal!r}")
    stack = np.stack(matrices, axis=0)
    if exclude_first_row:
        stack = stack[:, 1:, :]
    if exclude_first_column:
        stack = stack[:, :, 1:]
    if traversal == "columns":
        stack = np.swapaxes(stack, 1, 2)
    return np.ascontiguousarray(stack.reshape(-1, stack.shape[-1]), dtype=np.int64)


def _summary(
    rows: list[dict[str, object]],
    *,
    bootstrap_seed: int,
    bootstrap_resamples: int,
) -> list[dict[str, object]]:
    grouped: dict[tuple[int, int, str, str, str], dict[int, float]] = {}
    for row in rows:
        key = (
            int(row["order"]),
            int(row["context_length"]),
            str(row["variant"]),
            str(row["traversal"]),
            str(row["region"]),
        )
        grouped.setdefault(key, {})[int(row["repetition"])] = float(
            row["gain_over_fair"]
        )

    rng = np.random.default_rng(bootstrap_seed)
    summary: list[dict[str, object]] = []

    def add_statistic(
        order: int,
        context_length: int,
        effect: str,
        left: tuple[str, str, str],
        right: tuple[str, str, str],
        values: np.ndarray,
    ) -> None:
        lower, upper = bootstrap_mean_interval(
            values,
            rng,
            resamples=bootstrap_resamples,
        )
        summary.append(
            {
                "order": order,
                "context_length": context_length,
                "statistic": "mean_gain" if effect == "gain_over_fair" else "paired_difference",
                "effect": effect,
                "left_variant": left[0],
                "left_traversal": left[1],
                "left_region": left[2],
                "right_variant": right[0],
                "right_traversal": right[1],
                "right_region": right[2],
                "repetitions": values.size,
                "mean": float(np.mean(values)),
                "standard_deviation": float(np.std(values, ddof=1)),
                "ci95_lower": lower,
                "ci95_upper": upper,
            }
        )

    for key, by_repetition in sorted(grouped.items()):
        order, context_length, variant, traversal, region = key
        values = np.asarray(list(by_repetition.values()), dtype=np.float64)
        add_statistic(
            order,
            context_length,
            "gain_over_fair",
            (variant, traversal, region),
            ("fair_coin", traversal, region),
            values,
        )

    order_contexts = sorted({(key[0], key[1]) for key in grouped})

    def add_paired(
        order: int,
        context_length: int,
        effect: str,
        left: tuple[str, str, str],
        right: tuple[str, str, str],
    ) -> None:
        left_values = grouped[(order, context_length, *left)]
        right_values = grouped[(order, context_length, *right)]
        repetitions = sorted(set(left_values) & set(right_values))
        differences = np.asarray(
            [left_values[index] - right_values[index] for index in repetitions],
            dtype=np.float64,
        )
        add_statistic(order, context_length, effect, left, right, differences)

    for order, context_length in order_contexts:
        for traversal in TRAVERSALS:
            catalog = ("catalog", traversal, "all")
            for variant in ORDERING_VARIANTS[1:]:
                add_paired(
                    order,
                    context_length,
                    f"catalog_minus_{variant}",
                    catalog,
                    (variant, traversal, "all"),
                )
            add_paired(
                order,
                context_length,
                "fixed_both_minus_renormalized_both",
                ("permute_both_fixed_anchor", traversal, "all"),
                ("permute_both_renormalized", traversal, "all"),
            )
            for region in REGIONS:
                if region == "all":
                    continue
                add_paired(
                    order,
                    context_length,
                    f"all_minus_{region}",
                    catalog,
                    ("catalog", traversal, region),
                )
        for variant in ORDERING_VARIANTS:
            add_paired(
                order,
                context_length,
                "row_minus_column_traversal",
                (variant, "rows", "all"),
                (variant, "columns", "all"),
            )
    return summary


def run(
    *,
    orders: list[int],
    max_context: int,
    alpha: float,
    test_fraction: float,
    base_seed: int,
    repetitions: int,
    bootstrap_resamples: int,
    data_directory: Path,
    output: Path,
) -> None:
    if repetitions < 2:
        raise ValueError("at least two repetitions are required")
    if max_context < 1:
        raise ValueError("max_context must be positive")

    paths = download_corpus(orders, data_directory)
    corpora = {order: load_corpus_file(paths[order], order) for order in orders}
    rows: list[dict[str, object]] = []
    split_records: list[dict[str, object]] = []

    for repetition in range(repetitions):
        seed = base_seed + repetition
        print(f"Note 2 repetition {repetition + 1}/{repetitions} (seed {seed})", flush=True)
        for order in orders:
            matrices = corpora[order]
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

            variants: dict[str, list[SignMatrix]] = {"catalog": matrices}
            variants.update(
                fixed_anchor_variants(
                    matrices,
                    np.random.default_rng(seed + 40_000 + order),
                )
            )
            unrestricted_rng = np.random.default_rng(seed + 50_000 + order)
            variants["permute_both_renormalized"] = [
                permuted_equivalent(matrix, unrestricted_rng) for matrix in matrices
            ]

            conditions: list[tuple[str, str, str]] = []
            for variant in ORDERING_VARIANTS:
                for traversal in TRAVERSALS:
                    conditions.append((variant, traversal, "all"))
            for traversal in TRAVERSALS:
                for region in REGIONS:
                    if region != "all":
                        conditions.append(("catalog", traversal, region))

            for variant, traversal, region in conditions:
                exclude_first_row, exclude_first_column = REGIONS[region]
                variant_matrices = variants[variant]
                train_matrices = [variant_matrices[index] for index in train_indices]
                test_matrices = [variant_matrices[index] for index in test_indices]
                train_sequences = matrix_sequences(
                    train_matrices,
                    traversal,
                    exclude_first_row=exclude_first_row,
                    exclude_first_column=exclude_first_column,
                )
                test_sequences = matrix_sequences(
                    test_matrices,
                    traversal,
                    exclude_first_row=exclude_first_row,
                    exclude_first_column=exclude_first_column,
                )
                for context_length in range(1, max_context + 1):
                    metrics = evaluate_sequence_model(
                        train_sequences,
                        test_sequences,
                        context_length,
                        alpha=alpha,
                        exclude_first_row=exclude_first_row,
                        exclude_first_column=exclude_first_column,
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
                            "traversal": traversal,
                            "region": region,
                            "train_matrices": len(train_matrices),
                            "test_matrices": len(test_matrices),
                            "gain_over_fair": gain,
                            **metrics,
                        }
                    )

    _write_csv(output, rows)
    summary = _summary(
        rows,
        bootstrap_seed=base_seed + 90_000,
        bootstrap_resamples=bootstrap_resamples,
    )
    summary_path = output.with_name(f"{output.stem}_summary.csv")
    _write_csv(summary_path, summary)
    metadata = {
        **_common_metadata(),
        "experiment": "note2_representation_traversal_normalization_ablation",
        "matrix_source": "Brendan McKay Hadamard equivalence-class corpus",
        "orders": orders,
        "max_context": max_context,
        "alpha": alpha,
        "test_fraction": test_fraction,
        "base_seed": base_seed,
        "repetitions": repetitions,
        "bootstrap_resamples": bootstrap_resamples,
        "traversals": list(TRAVERSALS),
        "regions": REGIONS,
        "ordering_variants": list(ORDERING_VARIANTS),
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
    print(f"wrote metadata to {metadata_path}")


def _parse_orders(value: str) -> list[int]:
    orders = [int(item.strip()) for item in value.split(",") if item.strip()]
    unsupported = sorted(set(orders) - set(ORDERS))
    if unsupported or not orders:
        raise argparse.ArgumentTypeError(f"orders must be drawn from {ORDERS}")
    return orders


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders", type=_parse_orders, default=list(ORDERS))
    parser.add_argument("--max-context", type=int, default=12)
    parser.add_argument("--alpha", type=float, default=0.5)
    parser.add_argument("--test-fraction", type=float, default=0.2)
    parser.add_argument("--base-seed", type=int, default=20260814)
    parser.add_argument("--repetitions", type=int, default=20)
    parser.add_argument("--bootstrap-resamples", type=int, default=10_000)
    parser.add_argument("--data-directory", type=Path, default=Path("data/raw"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(
        orders=args.orders,
        max_context=args.max_context,
        alpha=args.alpha,
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
