# How AgroDesign Works

AgroDesign is not a statistics library.
It is an **experimental interpretation engine**.

Traditional statistical software asks:

> “Which statistical test do you want to run?”

AgroDesign asks:

> “What experiment did you conduct?”

You describe the experiment → AgroDesign selects the correct statistical workflow.

---

## The Core Idea

Agricultural experiments are defined by **design structure**, not statistical tests.

| Experiment type   | Correct analysis      |
| ----------------- | --------------------- |
| CRD               | One-way ANOVA         |
| RCBD              | Blocked ANOVA         |
| Factorial         | Interaction model     |
| Split-plot        | Multiple error strata |
| Mixed model       | BLUP estimation       |
| Multi-environment | Stability analysis    |

Researchers should not manually choose models —
the design determines the statistics.

---

## The Universal Workflow

Every analysis in AgroDesign follows the same pattern:

```python
result = (
    Experiment(data, response)
    .design(...)
    .run()
)
```

After running:

| Command            | Purpose                   |
| ------------------ | ------------------------- |
| `result`           | Quick decision snapshot   |
| `print(result)`    | Full statistical report   |
| `result.summary()` | Biological recommendation |
| `result.plot()`    | Visual interpretation     |
| `result.export()`  | Publication files         |

You never manually run ANOVA, post-hoc tests, or diagnostics.

---

## What `.run()` Actually Does

Internally AgroDesign performs:

1. Detect design structure
2. Build correct statistical model
3. Select appropriate error term
4. Perform ANOVA or mixed model
5. Run mean separation
6. Check assumptions
7. Apply biological interpretation rules
8. Generate recommendations

The user only provides experimental structure.

---

## Interaction Interpretation Rule

AgroDesign automatically applies standard agronomic interpretation logic:

If interaction is significant:

```
Recommend treatment combination
Ignore individual factors
```

If interaction is not significant:

```
Recommend best main factor level
```

This prevents one of the most common mistakes in agricultural papers.

---

## Snapshot vs Report

AgroDesign intentionally separates outputs:

### Snapshot (`result`)

A short scientific decision — suitable for notebooks

### Full report (`print(result)`)

Complete statistical output — suitable for publications

### Summary (`summary()`)

Plain-language agronomic recommendation — suitable for extension work

---

## Grouped Analysis

You can analyze experiments repeated across years or locations:

```python
Experiment(df,"Yield").by("Year").rcbd("Variety","Block").run()
```

AgroDesign will:

* analyze each year separately
* determine consistent best treatment
* compute overall recommendation

---

## Multi-Trait Decisions

Breeding decisions often require multiple traits:

```python
Experiment(df,["Yield","Height"]).rcbd("Variety","Block").run()
```

AgroDesign combines rankings and selects the overall best genotype.

---

## Philosophy

AgroDesign separates responsibilities:

| Role       | Responsibility            |
| ---------- | ------------------------- |
| Software   | statistics                |
| Researcher | biological interpretation |

The goal is reproducible and statistically valid agricultural conclusions.

---

AgroDesign does not replace statistical thinking.
It removes statistical implementation errors.
