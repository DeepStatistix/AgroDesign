# Quickstart

This guide runs your first AgroDesign analysis in under 3 minutes.

---

## 1. Install

```bash
pip install agrodesign
```

---

## 2. Create a simple dataset

We will analyze a wheat variety trial conducted using a randomized complete block design (RCBD).

```python
import pandas as pd
from agrodesign.experiment import Experiment

df = pd.DataFrame({
    "Block":["B1","B1","B1","B1",
             "B2","B2","B2","B2",
             "B3","B3","B3","B3",
             "B4","B4","B4","B4"],
    "Variety":["V1","V2","V3","V4"]*4,
    "Yield":[48,52,56,60,45,50,54,58,47,51,55,59,46,49,53,57]
})
```

---

## 3. Describe the experiment

Tell AgroDesign the experimental structure.

```python
result = Experiment(df,"Yield").rcbd("Variety","Block").run()
```

---

## 4. View the decision

```python
result
```

Example output:

```
AgroResult (RCBD)
Response: Yield
Significant factors: Variety
Best treatment: V4
Expected yield: 58.50
```

---

## 5. Get full analysis

```python
print(result)
```

Complete ANOVA and mean comparison will be displayed.

---

## 6. Biological recommendation

```python
result.summary()
```

Provides agronomic interpretation in plain language.

---

## 7. Figures

```python
result.plot()
```

Generates publication-ready plots.

---

## 8. Export report

```python
result.export("report")
```

Creates a folder containing tables and figures.

---

## What just happened?

You described the experiment — AgroDesign:

* selected the correct statistical model
* performed ANOVA
* ran mean separation
* checked assumptions
* generated recommendation

No manual statistical decisions were required.

---

## Next Steps

You can analyze other experiment types:

| Experiment        | Example                                |
| ----------------- | -------------------------------------- |
| CRD               | `.crd("Treatment")`                    |
| Factorial         | `.factorial(["A","B"])`                |
| Split-plot        | `.split_plot("Main","Sub","Block")`    |
| Mixed model       | `.mixed(fixed=[...], random=[...])`    |
| Multi-environment | `.gxe("Genotype","Environment","Rep")` |
| Multi-year        | `.by("Year")`                          |
| Multiple traits   | `Experiment(df,["Yield","Height"])`    |
