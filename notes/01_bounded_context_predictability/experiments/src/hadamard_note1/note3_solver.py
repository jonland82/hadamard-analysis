"""Note 3: exact Hadamard completion with constraint-state branch ordering."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from itertools import product
from pathlib import Path
from typing import Sequence

import numpy as np

from .corpus import download_corpus, load_corpus_file
from .matrices import SignMatrix, require_hadamard
from .note2 import _common_metadata

POLICIES = (
    "lexicographic",
    "random_order",
    "balance_only",
    "balance_pressured_pair",
    "all_pair_product",
    "all_pair_lexicographic",
    "minimum_max_pressure",
)

GUIDED_POLICIES = ("all_pair_product", "all_pair_lexicographic")

MASK64 = (1 << 64) - 1


def sign_code(signs: Sequence[int]) -> int:
    """Encode +1 as zero and -1 as one in printed lexicographic order."""

    code = 0
    for sign in signs:
        if sign not in (-1, 1):
            raise ValueError("sign sequences must contain only -1 and +1")
        code = (code << 1) | int(sign == -1)
    return code


def _splitmix64(value: int) -> int:
    value = (value + 0x9E3779B97F4A7C15) & MASK64
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK64
    return value ^ (value >> 31)


def partial_sum_feasible(partial_sum: int, remaining: int) -> bool:
    """Return whether ``remaining`` signs can bring ``partial_sum`` to zero."""

    return abs(partial_sum) <= remaining and (remaining - partial_sum) % 2 == 0


def prefix_can_exceed(prefix: Sequence[int], lower_bound: Sequence[int]) -> bool:
    """Return whether a partial row can finish lexicographically above a row.

    The ordering uses :func:`sign_code`, so +1 precedes -1. Equality is allowed
    only while the row remains unfinished.
    """

    if len(prefix) > len(lower_bound):
        raise ValueError("prefix cannot be longer than its lower bound")
    for current, previous in zip(prefix, lower_bound, strict=False):
        current_bit = int(current == -1)
        previous_bit = int(previous == -1)
        if current_bit < previous_bit:
            return False
        if current_bit > previous_bit:
            return True
    return len(prefix) < len(lower_bound)


def _log_hypergeometric(
    successes: int,
    population: int,
    draws: int,
    outcome: int,
) -> float:
    if not (
        0 <= successes <= population
        and 0 <= draws <= population
        and 0 <= outcome <= draws
        and outcome <= successes
        and draws - outcome <= population - successes
    ):
        return -math.inf
    numerator = math.comb(successes, outcome) * math.comb(
        population - successes, draws - outcome
    )
    return math.log(numerator / math.comb(population, draws))


def canonical_seed(order: int) -> tuple[tuple[int, ...], ...]:
    """Fix the first two rows using normalization and column symmetry."""

    if order < 4 or order % 4:
        raise ValueError("exact Hadamard search requires an order divisible by four")
    first = tuple([1] * order)
    second = tuple([1] * (order // 2) + [-1] * (order // 2))
    return first, second


def _validate_seed_rows(seed_rows: Sequence[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
    if len(seed_rows) < 2:
        raise ValueError("at least the normalized first row and one nonfirst row are required")
    rows = tuple(tuple(int(value) for value in row) for row in seed_rows)
    order = len(rows[0])
    if any(len(row) != order for row in rows):
        raise ValueError("all seed rows must have the same length")
    if rows[0] != tuple([1] * order):
        raise ValueError("the first seed row must be all +1")
    if any(row[0] != 1 for row in rows):
        raise ValueError("all seed rows must begin with +1")
    if any(sum(row) != 0 for row in rows[1:]):
        raise ValueError("every nonfirst seed row must be balanced")
    for left in range(len(rows)):
        for right in range(left):
            if sum(a * b for a, b in zip(rows[left], rows[right], strict=True)) != 0:
                raise ValueError("seed rows must be pairwise orthogonal")
    return rows


@dataclass
class SearchStats:
    nodes: int = 0
    backtracks: int = 0
    dead_ends: int = 0
    candidate_evaluations: int = 0
    exact_prunes: int = 0
    symmetry_prunes: int = 0
    completed_rows: int = 0
    scoring_calls: int = 0
    scoring_seconds: float = 0.0


@dataclass(frozen=True)
class Candidate:
    block: tuple[int, ...]
    row_sum_after: int
    pair_sums_after: tuple[int, ...]
    plus_count: int
    agreement_counts: tuple[int, ...]
    max_pressure: int
    random_key: int


@dataclass
class SearchResult:
    solved: bool
    termination: str
    elapsed_seconds: float
    stats: SearchStats
    solution: tuple[tuple[int, ...], ...] | None


class SearchLimitReached(RuntimeError):
    pass


class ExactHadamardSolver:
    """Complete depth-first solver whose policies only reorder feasible children."""

    def __init__(
        self,
        *,
        policy: str,
        block_size: int,
        tie_seed: int,
        max_nodes: int | None = None,
        max_seconds: float | None = None,
    ) -> None:
        if policy not in POLICIES:
            raise ValueError(f"unknown policy {policy!r}; choose from {POLICIES}")
        if block_size < 1 or block_size > 12:
            raise ValueError("block size must lie between 1 and 12")
        if max_nodes is not None and max_nodes < 1:
            raise ValueError("max_nodes must be positive when supplied")
        if max_seconds is not None and max_seconds <= 0:
            raise ValueError("max_seconds must be positive when supplied")
        self.policy = policy
        self.block_size = block_size
        self.tie_seed = int(tie_seed) & MASK64
        self.max_nodes = max_nodes
        self.max_seconds = max_seconds
        self.stats = SearchStats()
        self._rows: list[tuple[int, ...]] = []
        self._seed_count = 0
        self._order = 0
        self._started = 0.0
        self._deadline: float | None = None
        self._blocks: dict[int, tuple[tuple[int, ...], ...]] = {}

    def solve(self, seed_rows: Sequence[Sequence[int]]) -> SearchResult:
        rows = _validate_seed_rows(seed_rows)
        self._rows = list(rows)
        self._seed_count = len(rows)
        self._order = len(rows[0])
        if len(rows) > self._order:
            raise ValueError("there cannot be more seed rows than columns")
        self.stats = SearchStats()
        self._started = time.perf_counter()
        self._deadline = (
            self._started + self.max_seconds if self.max_seconds is not None else None
        )
        termination = "exhausted"
        solved = False
        try:
            solved = self._search_matrix()
            termination = "solved" if solved else "exhausted"
        except SearchLimitReached as error:
            termination = str(error)
        elapsed = time.perf_counter() - self._started
        solution = tuple(self._rows) if solved else None
        if solution is not None:
            require_hadamard(np.asarray(solution, dtype=np.int64))
        return SearchResult(solved, termination, elapsed, self.stats, solution)

    def _check_limits(self) -> None:
        if self.max_nodes is not None and self.stats.nodes >= self.max_nodes:
            raise SearchLimitReached("node_budget")
        if self._deadline is not None and time.perf_counter() >= self._deadline:
            raise SearchLimitReached("time_budget")

    def _search_matrix(self) -> bool:
        self._check_limits()
        if len(self._rows) == self._order:
            return True
        prior_nonfirst = self._rows[1:]
        prefix = (1,)
        pair_sums = tuple(row[0] for row in prior_nonfirst)
        return self._search_row(prefix, 1, pair_sums)

    def _search_row(
        self,
        prefix: tuple[int, ...],
        row_sum: int,
        pair_sums: tuple[int, ...],
    ) -> bool:
        self._check_limits()
        if len(prefix) == self._order:
            if row_sum != 0 or any(pair_sums):
                raise AssertionError("an infeasible completed row reached the row boundary")
            self.stats.completed_rows += 1
            self._rows.append(prefix)
            if self._search_matrix():
                return True
            self._rows.pop()
            return False

        draw = min(self.block_size, self._order - len(prefix))
        candidates = self._feasible_candidates(prefix, row_sum, pair_sums, draw)
        if not candidates:
            self.stats.dead_ends += 1
            return False
        for candidate in self._ordered(
            candidates,
            position=len(prefix),
            row_sum=row_sum,
            pair_sums=pair_sums,
            draw=draw,
        ):
            self._check_limits()
            self.stats.nodes += 1
            if self._search_row(
                prefix + candidate.block,
                candidate.row_sum_after,
                candidate.pair_sums_after,
            ):
                return True
            self.stats.backtracks += 1
        self.stats.dead_ends += 1
        return False

    def _candidate_blocks(self, length: int) -> tuple[tuple[int, ...], ...]:
        return self._blocks.setdefault(
            length,
            tuple(tuple(values) for values in product((1, -1), repeat=length)),
        )

    def _feasible_candidates(
        self,
        prefix: tuple[int, ...],
        row_sum: int,
        pair_sums: tuple[int, ...],
        draw: int,
    ) -> list[Candidate]:
        position = len(prefix)
        population = self._order - position
        after_remaining = population - draw
        prior_rows = self._rows[1:]
        prefix_code = sign_code(prefix)
        feasible: list[Candidate] = []
        for block in self._candidate_blocks(draw):
            self.stats.candidate_evaluations += 1
            row_after = row_sum + sum(block)
            pair_after = tuple(
                pair_sums[index]
                + sum(
                    sign * prior_rows[index][position + offset]
                    for offset, sign in enumerate(block)
                )
                for index in range(len(prior_rows))
            )
            if not partial_sum_feasible(row_after, after_remaining) or any(
                not partial_sum_feasible(value, after_remaining) for value in pair_after
            ):
                self.stats.exact_prunes += 1
                continue
            new_prefix = prefix + block
            lower_bound = self._rows[-1] if len(self._rows) > self._seed_count else None
            if lower_bound is not None and not prefix_can_exceed(new_prefix, lower_bound):
                self.stats.symmetry_prunes += 1
                continue

            plus_count = sum(sign == 1 for sign in block)
            agreement_counts = tuple(
                sum(
                    sign == prior_row[position + offset]
                    for offset, sign in enumerate(block)
                )
                for prior_row in prior_rows
            )
            max_pressure = max((abs(row_after), *(abs(value) for value in pair_after)))
            random_key = _splitmix64(
                self.tie_seed
                ^ (len(self._rows) << 48)
                ^ (position << 40)
                ^ (prefix_code << 12)
                ^ sign_code(block)
            )
            feasible.append(
                Candidate(
                    block=block,
                    row_sum_after=row_after,
                    pair_sums_after=pair_after,
                    plus_count=plus_count,
                    agreement_counts=agreement_counts,
                    max_pressure=max_pressure,
                    random_key=random_key,
                )
            )
        return feasible

    def _ordered(
        self,
        candidates: list[Candidate],
        position: int,
        row_sum: int,
        pair_sums: tuple[int, ...],
        draw: int,
    ) -> list[Candidate]:
        if self.policy == "lexicographic":
            return candidates
        started = time.perf_counter()
        self.stats.scoring_calls += 1
        population = self._order - position
        plus_remaining = (population - row_sum) // 2
        agreement_remaining = tuple(
            (population - partial_sum) // 2 for partial_sum in pair_sums
        )
        pressured_index = (
            max(range(len(pair_sums)), key=lambda index: abs(pair_sums[index]))
            if pair_sums
            else None
        )

        def balance_score(candidate: Candidate) -> float:
            return _log_hypergeometric(
                plus_remaining, population, draw, candidate.plus_count
            )

        def pair_score(candidate: Candidate, index: int) -> float:
            return _log_hypergeometric(
                agreement_remaining[index],
                population,
                draw,
                candidate.agreement_counts[index],
            )

        if self.policy == "random_order":
            key = lambda candidate: candidate.random_key
        elif self.policy == "balance_only":
            key = lambda candidate: (-balance_score(candidate), candidate.random_key)
        elif self.policy == "balance_pressured_pair":
            key = lambda candidate: (
                -(
                    balance_score(candidate)
                    + (
                        pair_score(candidate, pressured_index)
                        if pressured_index is not None
                        else 0.0
                    )
                ),
                candidate.random_key,
            )
        elif self.policy in GUIDED_POLICIES:
            def all_pair_score(candidate: Candidate) -> float:
                return balance_score(candidate) + sum(
                    pair_score(candidate, index) for index in range(len(pair_sums))
                )

            if self.policy == "all_pair_product":
                key = lambda candidate: (-all_pair_score(candidate), candidate.random_key)
            else:
                key = lambda candidate: (-all_pair_score(candidate), sign_code(candidate.block))
        elif self.policy == "minimum_max_pressure":
            key = lambda candidate: (candidate.max_pressure, candidate.random_key)
        else:  # pragma: no cover - guarded by __init__
            raise AssertionError(f"unhandled policy {self.policy}")
        ordered = sorted(candidates, key=key)
        self.stats.scoring_seconds += time.perf_counter() - started
        return ordered


def matrix_digest(matrix: Sequence[Sequence[int]]) -> str:
    payload = "\n".join("".join("+" if value == 1 else "-" for value in row) for row in matrix)
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


@dataclass(frozen=True)
class CompletionInstance:
    instance_id: str
    order: int
    class_index: int
    presentation_seed: int
    hidden_rows: int
    seed_rows: tuple[tuple[int, ...], ...]
    target_digest: str
    seed_digest: str


def make_completion_instance(
    matrix: SignMatrix,
    *,
    class_index: int,
    hidden_rows: int,
    presentation_seed: int,
) -> CompletionInstance:
    """Create a satisfiable prefix instance; the target is not returned to the solver."""

    hadamard = require_hadamard(matrix)
    order = hadamard.shape[0]
    if not 1 <= hidden_rows <= order - 2:
        raise ValueError("hidden_rows must leave at least two completed seed rows")
    rng = np.random.default_rng(presentation_seed)
    permutation = np.concatenate(
        (np.asarray([0], dtype=np.int64), rng.permutation(np.arange(1, order)))
    )
    presented = hadamard[:, permutation]
    row_permutation = rng.permutation(np.arange(1, order))
    nonfirst = tuple(
        tuple(int(value) for value in presented[index]) for index in row_permutation
    )
    target = (tuple([1] * order), *nonfirst)
    seed_rows = target[: order - hidden_rows]
    identifier = f"d{order}-c{class_index}-h{hidden_rows}-s{presentation_seed}"
    return CompletionInstance(
        instance_id=identifier,
        order=order,
        class_index=class_index,
        presentation_seed=presentation_seed,
        hidden_rows=hidden_rows,
        seed_rows=seed_rows,
        target_digest=matrix_digest(target),
        seed_digest=matrix_digest(seed_rows),
    )


@dataclass(frozen=True)
class SearchJob:
    instance: CompletionInstance
    policy: str
    block_size: int
    tie_repetition: int
    tie_seed: int
    max_nodes: int
    max_seconds: float


def run_search_job(job: SearchJob) -> dict[str, object]:
    solver = ExactHadamardSolver(
        policy=job.policy,
        block_size=job.block_size,
        tie_seed=job.tie_seed,
        max_nodes=job.max_nodes,
        max_seconds=job.max_seconds,
    )
    result = solver.solve(job.instance.seed_rows)
    solution_digest = matrix_digest(result.solution) if result.solution is not None else ""
    verification_passed = False
    if result.solution is not None:
        require_hadamard(np.asarray(result.solution, dtype=np.int64))
        verification_passed = (
            tuple(result.solution[: len(job.instance.seed_rows)]) == job.instance.seed_rows
        )
    return {
        "instance_id": job.instance.instance_id,
        "order": job.instance.order,
        "class_index": job.instance.class_index,
        "presentation_seed": job.instance.presentation_seed,
        "hidden_rows": job.instance.hidden_rows,
        "seed_rows": len(job.instance.seed_rows),
        "seed_digest": job.instance.seed_digest,
        "target_digest": job.instance.target_digest,
        "block_size": job.block_size,
        "policy": job.policy,
        "tie_repetition": job.tie_repetition,
        "tie_seed": job.tie_seed,
        "max_nodes": job.max_nodes,
        "max_seconds": job.max_seconds,
        "solved": result.solved,
        "termination": result.termination,
        "elapsed_seconds": result.elapsed_seconds,
        **asdict(result.stats),
        "solution_digest": solution_digest,
        "verification_passed": verification_passed,
    }


def _write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("cannot write an empty result table")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1"}:
            return True
        if normalized in {"false", "0"}:
            return False
    raise ValueError(f"cannot interpret {value!r} as a Boolean")


def summarize_results(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    keys = ("order", "hidden_rows", "block_size", "policy")
    grouped: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(tuple(row[key] for key in keys), []).append(row)
    output: list[dict[str, object]] = []
    for key, group in sorted(grouped.items()):
        solved = [row for row in group if _as_bool(row["solved"])]
        nodes = np.asarray([int(row["nodes"]) for row in solved], dtype=np.float64)
        times = np.asarray(
            [float(row["elapsed_seconds"]) for row in solved], dtype=np.float64
        )
        score_fractions = np.asarray(
            [
                float(row["scoring_seconds"]) / max(float(row["elapsed_seconds"]), 1e-12)
                for row in solved
            ],
            dtype=np.float64,
        )
        output.append(
            {
                **dict(zip(keys, key, strict=True)),
                "runs": len(group),
                "solved_runs": len(solved),
                "solve_rate": len(solved) / len(group),
                "median_nodes_solved": float(np.median(nodes)) if len(nodes) else math.nan,
                "mean_nodes_solved": float(np.mean(nodes)) if len(nodes) else math.nan,
                "median_backtracks_solved": float(
                    np.median([int(row["backtracks"]) for row in solved])
                )
                if solved
                else math.nan,
                "median_seconds_solved": float(np.median(times)) if len(times) else math.nan,
                "mean_seconds_solved": float(np.mean(times)) if len(times) else math.nan,
                "median_scoring_fraction_solved": float(np.median(score_fractions))
                if len(score_fractions)
                else math.nan,
            }
        )
    return output


def paired_policy_effects(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    identity = ("instance_id", "block_size", "tie_repetition")
    by_run: dict[tuple[object, ...], dict[str, dict[str, object]]] = {}
    for row in rows:
        by_run.setdefault(tuple(row[key] for key in identity), {})[str(row["policy"])] = row
    effects: list[dict[str, object]] = []
    for key, policies in sorted(by_run.items()):
        for guided_name in GUIDED_POLICIES:
            guided = policies.get(guided_name)
            if guided is None or not _as_bool(guided["solved"]):
                continue
            for baseline_name in (
                "lexicographic",
                "random_order",
                "balance_only",
                "minimum_max_pressure",
            ):
                baseline = policies.get(baseline_name)
                if baseline is None or not _as_bool(baseline["solved"]):
                    continue
                guided_nodes = int(guided["nodes"])
                baseline_nodes = int(baseline["nodes"])
                guided_seconds = float(guided["elapsed_seconds"])
                baseline_seconds = float(baseline["elapsed_seconds"])
                effects.append(
                    {
                        "instance_id": key[0],
                        "block_size": key[1],
                        "tie_repetition": key[2],
                        "order": guided["order"],
                        "hidden_rows": guided["hidden_rows"],
                        "guided_policy": guided_name,
                        "baseline": baseline_name,
                        "guided_nodes": guided_nodes,
                        "baseline_nodes": baseline_nodes,
                        "node_ratio_guided_over_baseline": guided_nodes
                        / max(baseline_nodes, 1),
                        "node_reduction_fraction": 1.0
                        - guided_nodes / max(baseline_nodes, 1),
                        "guided_seconds": guided_seconds,
                        "baseline_seconds": baseline_seconds,
                        "time_ratio_guided_over_baseline": guided_seconds
                        / max(baseline_seconds, 1e-12),
                        "time_reduction_fraction": 1.0
                        - guided_seconds / max(baseline_seconds, 1e-12),
                    }
                )
    return effects


def summarize_paired_outcomes(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Summarize solved pairs without discarding one-sided budget failures."""

    identity = ("instance_id", "block_size", "tie_repetition")
    by_run: dict[tuple[object, ...], dict[str, dict[str, object]]] = {}
    for row in rows:
        by_run.setdefault(tuple(row[key] for key in identity), {})[str(row["policy"])] = row
    grouped: dict[tuple[object, ...], list[tuple[dict[str, object], dict[str, object]]]] = {}
    for policies in by_run.values():
        for guided_name in GUIDED_POLICIES:
            guided = policies.get(guided_name)
            if guided is None:
                continue
            for baseline_name in (
                "lexicographic",
                "random_order",
                "balance_only",
                "minimum_max_pressure",
            ):
                baseline = policies.get(baseline_name)
                if baseline is None:
                    continue
                key = (
                    guided["order"],
                    guided["hidden_rows"],
                    guided["block_size"],
                    guided_name,
                    baseline_name,
                )
                grouped.setdefault(key, []).append((guided, baseline))

    summary: list[dict[str, object]] = []
    for key, pairs in sorted(grouped.items()):
        both = [
            (guided, baseline)
            for guided, baseline in pairs
            if _as_bool(guided["solved"]) and _as_bool(baseline["solved"])
        ]
        ratios = np.asarray(
            [
                int(guided["nodes"]) / max(int(baseline["nodes"]), 1)
                for guided, baseline in both
            ],
            dtype=np.float64,
        )
        time_ratios = np.asarray(
            [
                float(guided["elapsed_seconds"])
                / max(float(baseline["elapsed_seconds"]), 1e-12)
                for guided, baseline in both
            ],
            dtype=np.float64,
        )
        summary.append(
            {
                "order": key[0],
                "hidden_rows": key[1],
                "block_size": key[2],
                "guided_policy": key[3],
                "baseline": key[4],
                "pairs": len(pairs),
                "both_solved": len(both),
                "guided_only_solved": sum(
                    _as_bool(guided["solved"]) and not _as_bool(baseline["solved"])
                    for guided, baseline in pairs
                ),
                "baseline_only_solved": sum(
                    not _as_bool(guided["solved"]) and _as_bool(baseline["solved"])
                    for guided, baseline in pairs
                ),
                "neither_solved": sum(
                    not _as_bool(guided["solved"]) and not _as_bool(baseline["solved"])
                    for guided, baseline in pairs
                ),
                "guided_node_win_rate_both_solved": float(
                    np.mean(
                        [int(guided["nodes"]) < int(baseline["nodes"]) for guided, baseline in both]
                    )
                )
                if both
                else math.nan,
                "median_node_ratio_guided_over_baseline_both_solved": float(np.median(ratios))
                if len(ratios)
                else math.nan,
                "geometric_mean_node_ratio_guided_over_baseline_both_solved": float(
                    np.exp(np.mean(np.log(ratios)))
                )
                if len(ratios)
                else math.nan,
                "median_time_ratio_guided_over_baseline_both_solved": float(np.median(time_ratios))
                if len(time_ratios)
                else math.nan,
            }
        )
    return summary


def _parse_int_list(value: str) -> list[int]:
    values = [int(item.strip()) for item in value.split(",") if item.strip()]
    if not values:
        raise argparse.ArgumentTypeError("expected a comma-separated integer list")
    return values


def _parse_policy_list(value: str) -> list[str]:
    values = [item.strip() for item in value.split(",") if item.strip()]
    if not values or set(values) - set(POLICIES):
        raise argparse.ArgumentTypeError(f"policies must be drawn from {POLICIES}")
    return values


def build_instances(
    corpora: dict[int, list[SignMatrix]],
    *,
    hidden_rows: list[int],
    instances_per_condition: int,
    base_seed: int,
) -> list[CompletionInstance]:
    instances: list[CompletionInstance] = []
    for order, matrices in sorted(corpora.items()):
        for hidden in hidden_rows:
            if hidden > order - 2:
                continue
            for repetition in range(instances_per_condition):
                class_index = repetition % len(matrices)
                presentation_seed = base_seed + order * 100_000 + hidden * 1_000 + repetition
                instances.append(
                    make_completion_instance(
                        matrices[class_index],
                        class_index=class_index,
                        hidden_rows=hidden,
                        presentation_seed=presentation_seed,
                    )
                )
    return instances


def run_experiment(
    *,
    orders: list[int],
    hidden_rows: list[int],
    block_sizes: list[int],
    policies: list[str],
    instances_per_condition: int,
    tie_repetitions: int,
    base_seed: int,
    max_nodes: int,
    max_seconds: float,
    workers: int,
    data_directory: Path,
    output: Path,
) -> None:
    if instances_per_condition < 1 or tie_repetitions < 1:
        raise ValueError("instance and tie repetition counts must be positive")
    paths = download_corpus(orders, data_directory)
    corpora = {order: load_corpus_file(paths[order], order) for order in orders}
    instances = build_instances(
        corpora,
        hidden_rows=hidden_rows,
        instances_per_condition=instances_per_condition,
        base_seed=base_seed,
    )
    jobs = [
        SearchJob(
            instance=instance,
            policy=policy,
            block_size=block_size,
            tie_repetition=tie_repetition,
            tie_seed=(
                base_seed
                + 10_000_019 * tie_repetition
                + 1_000_003 * block_size
                + instance.presentation_seed
            ),
            max_nodes=max_nodes,
            max_seconds=max_seconds,
        )
        for instance in instances
        for block_size in block_sizes
        for tie_repetition in range(tie_repetitions)
        for policy in policies
    ]
    print(
        f"running {len(jobs)} exact-search jobs across {workers} worker(s)",
        flush=True,
    )
    rows: list[dict[str, object]] = []
    if workers == 1:
        for index, job in enumerate(jobs, start=1):
            rows.append(run_search_job(job))
            if index % 10 == 0 or index == len(jobs):
                print(f"completed {index}/{len(jobs)} jobs", flush=True)
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(run_search_job, job): job for job in jobs}
            for index, future in enumerate(as_completed(futures), start=1):
                rows.append(future.result())
                if index % 10 == 0 or index == len(jobs):
                    print(f"completed {index}/{len(jobs)} jobs", flush=True)
    rows.sort(
        key=lambda row: (
            int(row["order"]),
            int(row["hidden_rows"]),
            str(row["instance_id"]),
            int(row["block_size"]),
            int(row["tie_repetition"]),
            str(row["policy"]),
        )
    )
    _write_rows(output, rows)
    summary = summarize_results(rows)
    summary_path = output.with_name(f"{output.stem}_summary.csv")
    _write_rows(summary_path, summary)
    effects = paired_policy_effects(rows)
    effects_path = output.with_name(f"{output.stem}_paired.csv")
    _write_rows(effects_path, effects)
    paired_summary = summarize_paired_outcomes(rows)
    paired_summary_path = output.with_name(f"{output.stem}_paired_summary.csv")
    _write_rows(paired_summary_path, paired_summary)
    metadata = {
        **_common_metadata(),
        "experiment": "note3_exact_hadamard_completion_branch_ordering",
        "orders": orders,
        "hidden_rows": hidden_rows,
        "block_sizes": block_sizes,
        "policies": policies,
        "instances_per_condition": instances_per_condition,
        "tie_repetitions": tie_repetitions,
        "base_seed": base_seed,
        "max_nodes": max_nodes,
        "max_seconds": max_seconds,
        "workers": workers,
        "jobs": len(jobs),
        "all_solutions_verified": all(
            not _as_bool(row["solved"]) or _as_bool(row["verification_passed"]) for row in rows
        ),
        "target_hidden_from_solver": True,
        "instance_audit": [asdict(instance) | {"seed_rows": len(instance.seed_rows)} for instance in instances],
        "raw_output": str(output),
        "summary_output": str(summary_path),
        "paired_output": str(effects_path),
        "paired_summary_output": str(paired_summary_path),
    }
    metadata_path = output.with_name(f"{output.stem}_metadata.json")
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} raw runs to {output}", flush=True)
    print(f"wrote {len(summary)} summary rows to {summary_path}", flush=True)
    print(f"wrote {len(effects)} paired effects to {effects_path}", flush=True)
    print(
        f"wrote {len(paired_summary)} paired summary rows to {paired_summary_path}",
        flush=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders", type=_parse_int_list, default=[16, 20])
    parser.add_argument("--hidden-rows", type=_parse_int_list, default=[4, 8])
    parser.add_argument("--block-sizes", type=_parse_int_list, default=[2, 4])
    parser.add_argument("--policies", type=_parse_policy_list, default=list(POLICIES))
    parser.add_argument("--instances-per-condition", type=int, default=5)
    parser.add_argument("--tie-repetitions", type=int, default=3)
    parser.add_argument("--base-seed", type=int, default=20260815)
    parser.add_argument("--max-nodes", type=int, default=1_000_000)
    parser.add_argument("--max-seconds", type=float, default=60.0)
    parser.add_argument("--workers", type=int, default=max(1, min(8, os.cpu_count() or 1)))
    parser.add_argument("--data-directory", type=Path, default=Path("data/raw"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run_experiment(
        orders=args.orders,
        hidden_rows=args.hidden_rows,
        block_sizes=args.block_sizes,
        policies=args.policies,
        instances_per_condition=args.instances_per_condition,
        tie_repetitions=args.tie_repetitions,
        base_seed=args.base_seed,
        max_nodes=args.max_nodes,
        max_seconds=args.max_seconds,
        workers=args.workers,
        data_directory=args.data_directory,
        output=args.output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
