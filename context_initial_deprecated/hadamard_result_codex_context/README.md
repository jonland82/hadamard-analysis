# Hadamard Result — Codex Research Handoff

This directory is the initial context bundle for continuing the **Hadamard Result** research project in Codex.

## Project objective

Study whether the strong **global constraints** of a Hadamard matrix can be combined with measurable **local structure** to:

1. characterize how predictable a Hadamard matrix is from bounded local context;
2. formalize a notion of **local $\varepsilon$-unpredictability** compatible with weak Markov-style dependence;
3. exploit exact global constraints plus any valid local information to improve brute-force / backtracking construction;
4. turn the resulting mathematics into formal papers, reproducible experiments, code, and eventually an explanatory website.

A Hadamard matrix of order $d$ is

$$
H\in\{-1,+1\}^{d\times d},
\qquad
HH^\top=dI_d.
$$

Thus distinct rows (and columns) are orthogonal.

---

## Recommended loading order for Codex

Read these files in order:

1. `PROJECT_CONTEXT.md` — mathematical setup, terminology, and status of claims.
2. `RESULTS_AND_CONJECTURES.md` — results, draft theorems, and unresolved definitions.
3. `ALGORITHMS.md` — brute-force baseline and exact constraint-guided search.
4. `EXPERIMENTS.md` — empirical program for local predictability and search speedups.
5. `PAPER_ROADMAP.md` — how to turn the project into formal papers.
6. `CODEX_INSTRUCTIONS.md` — research behavior expected from Codex.
7. `RESEARCH_LOG_TEMPLATE.md` — format for recording future work.

## Critical epistemic rule

Do **not** silently promote an observation, empirical pattern, heuristic, conjecture, or draft theorem into a proved theorem.

Every substantive claim should be tagged as one of:

- **KNOWN** — standard established Hadamard fact.
- **DERIVED** — proved within this project with a complete argument.
- **EMPIRICAL** — observed computationally.
- **CONJECTURE** — plausible but unproved.
- **DEFINITION DRAFT** — a proposed formalization still being refined.
- **OPEN** — unresolved.

The most important current mathematical issue is that “probability of the next entry” is meaningless until a probability space / sampling procedure is specified. This must be resolved before a rigorous local-unpredictability theorem is stated.

## Immediate next move

The cleanest next research cycle is:

$$
\text{define probability space}
\to
\text{measure local bias}
\to
\text{prove or falsify a bound}
\to
\text{use only certified information in search}.
$$

The algorithmic work can proceed in parallel because the global orthogonality constraints already give exact pruning rules.
