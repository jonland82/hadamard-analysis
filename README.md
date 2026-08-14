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

These root documents are the current source of truth. They deliberately distinguish established facts, derived statements, empirical findings, conjectures, draft definitions, and open questions.

## Current status

- The basic Hadamard facts and exact partial-orthogonality pruning rule are established.
- Local $\varepsilon$-unpredictability is still a draft definition until the sampling distribution and traversal are fixed for each claim.
- The earlier informal "Markov result" has not yet been reconstructed from data or code.
- No experimental matrix corpus or generated results are currently included.
- The next concrete task is to assemble a small verified corpus and run Experiment A against IID and balanced-sequence controls.

## Historical context

The original handoff is preserved in [`context_initial_deprecated/`](context_initial_deprecated/). It records the initial project framing and should be treated as historical reference, not as a second set of current instructions.

The adjacent ZIP archive is the original packaged copy of that handoff.
