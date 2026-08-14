# Robustness Results

## Status

**[EMPIRICAL]** The five planned robustness checks are complete for the fixed McKay catalog through order $28$. These results are sufficient to draft Note 1, subject to the scope limitations below.

The resulting workshop manuscript is available as [`paper/note1.pdf`](paper/note1.pdf), with source in [`paper/note1.tex`](paper/note1.tex).

The principal conclusion is:

> Bounded-context predictability is substantial in canonical Hadamard representatives, but nearly all of the gain relative to simple controls disappears under equivalence-preserving row and column permutations.

This is evidence for representation-dependent local structure, not an equivalence-invariant local law of Hadamard matrices.

## Design

The experiment used orders

$$
d\in\{16,20,24,28\},
$$

context lengths

$$
k=1,2,\ldots,12,
$$

and $20$ paired repetitions. Each repetition used a fresh class-level $80/20$ split and fresh random controls. The primary traversal was row-major with contexts reset at row boundaries. The model used symmetric smoothing with $\alpha=1/2$.

For every source equivalence-class representative, the matched variants were:

- the normalized catalog representative;
- an independently row/column-permuted and renormalized equivalent matrix;
- a normalized matrix with independently sampled balanced rows;
- a normalized matrix with IID interior signs.

All variants inherited the same source-class train/test assignment within a repetition. The reported 95% intervals are percentile bootstrap intervals for the mean across the $20$ paired randomized repetitions.

## Primary comparison

Define held-out gain over the fair-coin predictor by

$$
G_k=\log 2-L_k,
$$

where $L_k$ is held-out log loss in nats per predicted sign. The prespecified pilot comparison was the row-reset traversal at $k=8$.

| Order | Variant | Mean $G_8$ | 95% interval |
|---:|---|---:|---:|
| 24 | Canonical Hadamard | $0.16573$ | $[0.15743,0.17388]$ |
| 24 | Permuted equivalent | $0.03344$ | $[0.03248,0.03431]$ |
| 24 | Balanced rows | $0.03257$ | $[0.03109,0.03396]$ |
| 24 | Normalized IID | $0.01696$ | $[0.01602,0.01793]$ |
| 28 | Canonical Hadamard | $0.13935$ | $[0.13850,0.14014]$ |
| 28 | Permuted equivalent | $0.03047$ | $[0.03030,0.03064]$ |
| 28 | Balanced rows | $0.03033$ | $[0.03006,0.03060]$ |
| 28 | Normalized IID | $0.01903$ | $[0.01888,0.01918]$ |

The paired contrasts make the interpretation direct:

| Order | Paired contrast at $k=8$ | Mean difference | 95% interval |
|---:|---|---:|---:|
| 24 | Canonical minus permuted | $0.13228$ | $[0.12394,0.14077]$ |
| 28 | Canonical minus permuted | $0.10888$ | $[0.10804,0.10968]$ |
| 24 | Permuted minus balanced | $0.00087$ | $[-0.00083,0.00268]$ |
| 28 | Permuted minus balanced | $0.00014$ | $[-0.00024,0.00052]$ |

Thus the canonical-representation effect is large and stable, while no practically meaningful Hadamard-specific residual beyond balance is detected after permutation.

## Verdict on the five checks

### 1. Repeated splits and permutations

The canonical-minus-permuted contrast remains positive across the repeated class splits at orders $24$ and $28$. Its paired interval excludes zero by a wide margin at $k=8$. Each source matrix receives $20$ independently randomized equivalent presentations across the full run.

### 2. Context-length sweep

At $k=1$, both canonical and permuted Hadamards have exactly zero gain over the fair-coin baseline under the row-reset sampling rule. At orders $24$ and $28$, the canonical-minus-permuted interval is positive for every $k=2,\ldots,12$ and the gap generally grows with $k$.

At order $28$, where unseen-context rates remain negligible through $k=12$, the mean canonical gain rises from $0$ at $k=1$ to $0.24624$ at $k=12$. The permuted and balanced gains track one another, peaking near $0.033$ and then flattening. The $k=8$ comparison remains the clean primary result because it was selected before this extended sweep and retains adequate context support at both principal orders.

### 3. Order sweep

The representation effect appears at every tested order, but orders $16$ and $20$ contain only $5$ and $3$ source equivalence classes. Their splits hold out only one class, and high-$k$ unseen-context rates exceed $80\%$. They are useful diagnostics but should not support population-level claims.

Orders $24$ and $28$, with $60$ and $487$ classes, support the main empirical statement. The result is therefore a same-order, within-catalog generalization claim, not a held-out-order or held-out-family claim.

### 4. Leakage audit

All $80$ order-by-repetition audits passed. For each split, the runner verifies:

- disjoint and exhaustive source-class indices;
- no identical normalized matrix digest on both sides;
- no duplicate matrix digests in the source order;
- inheritance of the same source-class split by every matched variant.

The source catalog supplies one representative per declared equivalence class. The experiment never splits positions or rows from the same source class across training and test sets.

### 5. Matched controls

The fair-coin, normalized-IID, balanced-row, and permuted-equivalent controls all use the same split and estimator as the canonical condition. At $k=8$, the permuted-minus-balanced paired intervals include zero at both principal orders.

At order $28$, isolated differences below $0.001$ nats appear at $k=10$ and $k=11$, without multiple-comparison correction and without consistent replication across context lengths or order $24$. These do not support a practically meaningful invariant residual.

## Consequence for the project narrative

The evidence now separates the one-sentence narrative into four claims:

- global choreography is exact;
- one-step row-local prediction is exactly neutral under the stated sampling rule;
- longer canonical contexts carry substantial transferable information, but that information is predominantly representation-dependent;
- usefulness for exact search remains untested.

The natural Note 1 theorem--experiment arc is therefore a representation-dependence result. A later search note can ask whether the canonical coordinate convention that creates the signal is also the convention used by an exact solver.

## Scope limitations

- The intervals quantify randomized split/control variation for this fixed catalog; they are not confidence intervals over all Hadamard matrices or construction families.
- The catalog representative-selection procedure may be the source of the canonical sequential regularity.
- The extended context sweep is exploratory and is not corrected for simultaneous testing over $k$.
- No held-out-order, held-out-family, asymptotic, or search-performance conclusion follows.

## Reproducible artifacts

- [`robustness_raw.csv`](experiments/results/robustness_raw.csv) contains all $3{,}840$ held-out evaluations.
- [`robustness_raw_summary.csv`](experiments/results/robustness_raw_summary.csv) contains variant means and paired contrasts with bootstrap intervals.
- [`robustness_raw_metadata.json`](experiments/results/robustness_raw_metadata.json) records the command, environment, all splits, and all leakage audits.

The original two-seed pipeline check remains in [`PILOT_RESULTS.md`](PILOT_RESULTS.md) for provenance.
