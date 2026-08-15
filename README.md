# Hadamard Analysis

**Project website:** [jonland82.github.io/hadamard-analysis](https://jonland82.github.io/hadamard-analysis/)

This repository studies how exact global organization becomes useful during local construction. A Hadamard matrix may reveal little through the last few printed entries, while the evolving balance and orthogonality state sharply constrains the composition of the region that remains. The project measures that regional information and asks whether it can guide an exact search without compromising completeness.

The one-sentence narrative is:

> Hadamard matrices reveal how global order can make local summaries predictable without making local decisions wise: the constraint state tells us what the next region should look like, but not which plausible region can belong to a complete whole.

The experiments test that sentence clause by clause:

- **Global order:** orthogonality, balance, normalization, and exact feasibility are mathematical constraints.
- **Predictable local summaries:** Note 2 derives exact remaining-inventory laws and verifies held-out next-block prediction across randomized equivalent presentations.
- **Unwise local decisions:** Note 3 shows that regional ordering can improve on random, balance-only, and pressure heuristics, yet the current greedy score loses to a strong lexicographic policy as construction depth grows.
- **The missing whole:** the next target is residual completability or branch survival beyond a structural baseline.

## Current documentation

- [`overall_summary.md`](overall_summary.md) gives the conceptual narrative, structural theory, claim registry, search consequences, and open questions.
- [`research_program.md`](research_program.md) defines the data model, pairs each experiment with mathematical statements, and organizes the work as a sequence of short notes.

## Completed notes and experiments

- [`notes/01_bounded_context_predictability/`](notes/01_bounded_context_predictability/) contains the first note, its Python experiments, and the completed robustness results. The compiled workshop paper is [`note1.pdf`](notes/01_bounded_context_predictability/paper/note1.pdf).
- [`notes/02_representation_ablation/`](notes/02_representation_ablation/) contains the completed representation diagnosis, regional prediction, and candidate-ranking study. The compiled workshop paper is [`note2.pdf`](notes/02_representation_ablation/paper/note2.pdf).
- [`notes/03_exact_search/`](notes/03_exact_search/) contains the completed controlled exact-search experiments, $2{,}070$ final run records, verification audits, and the four-page manuscript [`note3.pdf`](notes/03_exact_search/paper/note3.pdf).

These root documents are the current source of truth. They deliberately distinguish established facts, derived statements, empirical findings, conjectures, draft definitions, and open questions.

## Current status

- The basic Hadamard facts and exact partial-orthogonality pruning rule are established.
- Local $\varepsilon$-unpredictability is still a draft definition until the sampling distribution and traversal are fixed for each claim.
- The earlier informal "Markov result" has not yet been reconstructed from data or code.
- Note 1 now includes a verified small-order McKay corpus pipeline, fixed-context predictors, matched controls, 20 paired repetitions, bootstrap intervals, and 80 passing leakage audits.
- At the primary order-$28$, $k=8$ comparison, canonical representatives gain $0.13935$ nats over a fair coin, while permuted equivalents gain $0.03047$ and balanced rows gain $0.03033$. The paired permuted-minus-balanced interval includes zero.
- Note 2 adds $7{,}680$ measurements over 20 paired repetitions and 40 passing leakage audits. It shows that the representation-dependent signal lives mainly in coordinate order within rows or columns, not in the order of pooled rows or columns and not primarily in normalization anchors.
- The state-aware extension adds $11{,}520$ measurements and 40 passing leakage audits. Exact balance and partial-inner-product state predicts next-block composition under randomized equivalent representations at every tested block size and construction stage.
- At unrestricted randomized order $28$ and block size $8$, early-stage gains are $0.05724$ nats for row composition and $0.12014$ nats for the most-pressured pair's agreement count. Serialized context adds no gain beyond this state after randomization.
- The nonterminal ranking closure adds $4{,}320$ policy measurements and 40 passing audits. At unrestricted randomized order $28$, $b=8$, the all-pair score ranks observed continuations at the $84.8$th percentile early and $93.2$nd percentile in the middle, well above balance-only and minimum-pressure policies.
- Note 3 implements a complete blockwise solver with policy-independent exact pruning and independently verifies every returned matrix. Its four final result families contain $2{,}070$ runs and $1{,}952$ verified solutions.
- In the main benchmark, all-pair ordering has a lower condition-level median node count than balance-only in $11/12$ conditions and random ordering in $9/12$, but lexicographic ordering in only $1/12$.
- In the $20$-presentation $b=8$ closure, the lex-tied hybrid is competitive for four hidden rows at order $16$, but at six hidden rows it costs $6.72$ times as many paired-median nodes as lexicographic at order $16$. At order $20$, it solves $39/60$ runs versus lexicographic's $60/60$, and costs $5.51$ times as many nodes among jointly solved runs.
- In full order-$12$ construction from two seed rows, both lexicographic and the lex-tied hybrid solve all $15$ runs, but the hybrid uses $7.59$ times as many paired-median nodes and $15.21$ times as much time.
- The current SAT/CAS transfer gate is not met. The next hypothesis should predict residual completability beyond a structural policy rather than use marginal next-block likelihood as the primary branch order. AWS was not needed for Note 3.

## Historical context

The original handoff is preserved in [`context_initial_deprecated/`](context_initial_deprecated/). It records the initial project framing and should be treated as historical reference, not as a second set of current instructions.

The adjacent ZIP archive is the original packaged copy of that handoff.
