# Hadamard Analysis

This repository studies a simple tension: a Hadamard matrix is exactly organized as a whole, but a bounded local view may still reveal little about the next entry. The project asks how to measure that local information and whether it can guide an exact search without compromising completeness.

The one-sentence narrative is:

> Hadamard matrices are globally choreographed, locally hard to predict, yet potentially locally informative enough to guide an exact search.

The experiments test that sentence clause by clause:

- **Globally choreographed:** established orthogonality, balance, normalization, and exact pruning supply the theory; Experiment G measures their separate search effects.
- **Locally hard to predict:** Experiments A, C, D, and E measure conditional bias, remaining entropy, context-scale behavior, and traversal dependence.
- **Still locally informative:** Experiment B asks whether the small signal improves held-out probabilistic prediction.
- **Enough to guide exact search:** Experiment F tests whether that signal reduces first-solution search work without pruning statistically disfavored branches; Experiment G separates this gain from exact constraint gains.

## Current documentation

- [`overall_summary.md`](overall_summary.md) gives the conceptual narrative, structural theory, claim registry, search consequences, and open questions.
- [`research_program.md`](research_program.md) defines the data model, pairs each experiment with mathematical statements, and organizes the work as a sequence of short notes.

## Active note

- [`notes/01_bounded_context_predictability/`](notes/01_bounded_context_predictability/) contains the first note, its Python experiments, and the completed robustness results. The compiled workshop paper is [`note1.pdf`](notes/01_bounded_context_predictability/paper/note1.pdf).

These root documents are the current source of truth. They deliberately distinguish established facts, derived statements, empirical findings, conjectures, draft definitions, and open questions.

## Current status

- The basic Hadamard facts and exact partial-orthogonality pruning rule are established.
- Local $\varepsilon$-unpredictability is still a draft definition until the sampling distribution and traversal are fixed for each claim.
- The earlier informal "Markov result" has not yet been reconstructed from data or code.
- Note 1 now includes a verified small-order McKay corpus pipeline, fixed-context predictors, matched controls, 20 paired repetitions, bootstrap intervals, and 80 passing leakage audits.
- At the primary order-$28$, $k=8$ comparison, canonical representatives gain $0.13935$ nats over a fair coin, while permuted equivalents gain $0.03047$ and balanced rows gain $0.03033$. The paired permuted-minus-balanced interval includes zero.
- The evidence supports representation-dependent local predictability, not an equivalence-invariant local law. Whether that signal is enough to guide exact search is still untested. See [`ROBUSTNESS_RESULTS.md`](notes/01_bounded_context_predictability/ROBUSTNESS_RESULTS.md).

## Historical context

The original handoff is preserved in [`context_initial_deprecated/`](context_initial_deprecated/). It records the initial project framing and should be treated as historical reference, not as a second set of current instructions.

The adjacent ZIP archive is the original packaged copy of that handoff.
