# Paper Roadmap

The project can plausibly split into two papers rather than forcing mathematics and search engineering into one claim.

---

# Paper A — Global Rigidity and Local Predictability in Hadamard Matrices

## Candidate thesis

Hadamard matrices satisfy exact global orthogonality while bounded local context may provide only limited predictive information under a carefully defined ensemble.

## Minimum publishable structure

### 1. Introduction

Motivate the distinction between:

- deterministic global constraint;
- local statistical predictability.

Avoid calling Hadamard matrices “random.”

### 2. Definitions

Define:

- Hadamard matrix;
- normalization;
- equivalence notion;
- probability space;
- traversal;
- $k$-local context;
- $\varepsilon_k^{\max}$;
- $\varepsilon_k^{\mathrm{avg}}$;
- conditional entropy / mutual information.

### 3. Established structural facts

State only what is needed:

$$
HH^\top=dI,
$$

balance after normalization, and symmetries.

### 4. Main theorem

Do not write this section until a theorem is actually proved.

Desired shape:

$$
\varepsilon(d,k)\le f(d,k)
$$

for a clearly specified ensemble/family.

### 5. Empirical study

Measure local bias across:

- $d$;
- $k$;
- row/column traversals;
- inequivalent matrices/families.

### 6. Discussion

Explain how weak local dependence can coexist with exact global structure.

---

# Paper B — Constraint-Guided Search for Hadamard Matrices

## Candidate thesis

Exact partial orthogonality constraints give safe pruning, while weak local predictive models can be used as branch-ordering heuristics without sacrificing completeness.

### 1. Baseline enumeration

Start from raw

$$
2^{d^2}
$$

candidate matrices.

### 2. Symmetry and balance reductions

Normalize first row/column and enumerate balanced candidate rows.

### 3. Exact partial pruning

Use

$$
|S_{ij}(k)|\le d-k.
$$

### 4. Heuristic branch ordering

Use a local predictor only to decide search order.

### 5. Completeness proposition

Prove that branch ordering leaves the set of explored feasible branches unchanged if both branches remain available.

### 6. Benchmarking

Report node counts, backtracks, and runtime.

### 7. Ablations

Attribute each improvement to the correct source.

---

# What would make the work genuinely stronger

The strongest result would not merely be “Markov prediction speeds up search.”

A more mathematically interesting chain is:

$$
\text{global orthogonality}
\Rightarrow
\text{provable restriction on local conditional distributions}
\Rightarrow
\text{certified search consequence}.
$$

A weaker but still coherent contribution is:

$$
\text{new empirical local statistic}
+
\text{complete exact solver}
+
\text{measured heuristic speedup}.
$$

These should be described differently in a paper.

---

# Writing rules

- Give every theorem an explicit probability model.
- Separate theorem from experiment.
- Give exact constants where available.
- Never use “novel” in the manuscript without a literature search.
- Cite established Hadamard enumeration/search literature before novelty claims.
- Prefer small propositions with airtight proofs over broad philosophical claims.
- Include code and exact seeds for experimental claims.
