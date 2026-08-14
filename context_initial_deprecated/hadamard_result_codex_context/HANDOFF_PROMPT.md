# Initial Prompt for a Fresh Codex Session

Use the markdown files in this context directory as the authoritative handoff for my **Hadamard Result** research project.

We are studying the relationship between:

$$
\text{global Hadamard rigidity}
\qquad\text{and}\qquad
\text{bounded local predictability},
$$

and whether the combination can improve exact Hadamard search.

Start by reading `README.md`, then follow its loading order.

Important rules:

1. Preserve the distinction between **known facts, derived results, empirical observations, conjectures, and draft definitions**.
2. Do not invent the exact earlier “Markov result”; reconstruct it only from code/data/notes if available.
3. Treat local $\varepsilon$-unpredictability as a theorem target until its probability space and proof are rigorous.
4. In exact search, statistical local information may order branches but may not prune them unless we prove an impossibility condition.
5. Use exact orthogonality, normalization, balance, symmetry, and partial-inner-product feasibility aggressively.
6. When proposing a new theorem, first try to falsify it on small Hadamard matrices.
7. When proposing an algorithmic improvement, benchmark node counts and backtracks, not only wall-clock time.
8. Keep all work suitable for eventual formal papers, reproducible experiments, public code, and an explanatory website.

For the first action, summarize the current mathematical state in no more than ten bullets, identify the single most important unresolved definition, and propose the smallest experiment that would resolve or sharpen it.
