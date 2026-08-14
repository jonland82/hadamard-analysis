# Instructions for Codex

You are continuing an active mathematical research project on Hadamard matrices.

## Primary goal

Help turn exploratory discussion into:

- precise definitions;
- correct lemmas/theorems/proofs;
- reproducible experiments;
- efficient research code;
- paper-ready LaTeX;
- clear visualizations;
- a project website.

## Research discipline

### 1. Maintain claim status

Prefix important research statements in working notes with:

```text
[KNOWN]
[DERIVED]
[EMPIRICAL]
[CONJECTURE]
[DEFINITION DRAFT]
[OPEN]
```

Do not silently upgrade status.

### 2. Never invent missing prior results

The project previously discussed a “Markov result” describing nonzero local dependence, but the exact formal statement is not included here.

If code/data revealing it is absent:

- state that it must be reconstructed;
- do not fabricate its value, bound, proof, or order.

### 3. Be strict about probability

Before writing

$$
\Pr(X_{t+1}=1\mid C_k),
$$

identify:

- what is random;
- what is conditioned on;
- how matrices are sampled;
- how positions are sampled;
- how equivalence/normalization affects the distribution.

### 4. Separate pruning from heuristics

A branch may be removed only by a logically necessary constraint if the solver is claimed to be complete.

Statistical/Markov/ML predictions should initially be used only for branch ordering.

### 5. Verify all generated matrices

Every returned candidate $H$ must satisfy, in code,

```python
set(np.unique(H)).issubset({-1, 1})
np.array_equal(H @ H.T, d * np.eye(d, dtype=int))
```

Use exact integer arithmetic for verification.

### 6. Prefer small executable experiments

When a mathematical question can be cheaply falsified for small orders, write the smallest test first.

Use tests for $d=1,2,4,8,12,\ldots$ only where matrices/data are actually available.

Do not assume existence at an order merely because $4\mid d$.

### 7. Preserve baselines

Every algorithmic improvement needs a baseline using the same:

- instance set;
- verifier;
- stopping condition;
- random seeds where relevant.

### 8. Instrument search

Record nodes, prunes, backtracks, depth, and time.

Do not report runtime alone.

### 9. Keep research outputs modular

Suggested repository layout:

```text
hadamard-result/
├── context/
│   └── these handoff files
├── src/
│   └── hadamard/
├── tests/
├── experiments/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── papers/
│   ├── local-unpredictability/
│   └── search/
├── site/
├── figures/
├── results/
└── README.md
```

### 10. For each research iteration

Produce:

1. question;
2. exact mathematical formulation;
3. smallest useful computation;
4. result;
5. interpretation;
6. claim status;
7. next falsifiable question.

## Coding style

- Python first unless there is a reason otherwise.
- Type hints for reusable modules.
- Pure functions where practical.
- Deterministic seeds.
- Unit tests for all constraint logic.
- No floating point in exact Hadamard validity checks.
- Avoid premature optimization; establish node-count improvements before low-level speed work.

## Paper generation

When a result becomes stable:

- create a minimal LaTeX theorem statement;
- include assumptions explicitly;
- write a proof independently of experimental evidence;
- add an experiment only as illustration unless the claim itself is empirical.

## Website

The eventual website should distinguish:

```text
What is a Hadamard matrix?
What is known?
What did this project observe?
What has this project proved?
Interactive small-order search demo
Experiments and figures
Papers / code / data
```

Never visually blur conjectures and theorems.
