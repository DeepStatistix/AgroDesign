# AgroDesign

**AgroDesign** is a unified analysis framework for agricultural experiments.

Instead of manually choosing statistical tests, you describe the experiment —
AgroDesign automatically performs the correct analysis and produces biological recommendations.

It converts experimental data directly into **decisions, reports, figures, and publication-ready outputs**.

---

## Install

```bash
pip install agrodesign
```

---

## 5-Minute Example

Randomized Complete Block Design (variety trial)

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

result = Experiment(df,"Yield").rcbd("Variety","Block").run()

result
```

Output:

```
AgroResult (RCBD)
Response: Yield
Significant factors: Variety
Best treatment: V4
Expected yield: 58.50
```

---

## What can you do next?

```python
print(result)      # Full scientific report
result.summary()   # Agronomic recommendation
result.plot()      # Publication figures
result.export("report")  # Tables + plots folder
```

---

## Universal Workflow

All analyses follow the same pattern:

```python
result = (
    Experiment(data, response)
    .design(...)
    .run()
)
```

| Command         | Meaning                         |
| --------------- | ------------------------------- |
| `result`        | Decision snapshot               |
| `print(result)` | Scientific statistical report   |
| `summary()`     | Farmer/agronomic recommendation |
| `plot()`        | Visualization                   |
| `export()`      | Publication files               |

---

## Supported Experimental Designs

| Category         | Designs                           |
| ---------------- | --------------------------------- |
| Field trials     | CRD, RCBD                         |
| Input studies    | Factorial, Split-plot             |
| Random variation | Mixed models (BLUP)               |
| Breeding trials  | Multi-environment (G×E stability) |
| Multi-year data  | `.by("Year")` grouped analysis    |
| Multiple traits  | Automatic combined ranking        |

---

## Example Analyses

### Factorial experiment

```python
Experiment(df,"Yield").factorial(["Nitrogen","Spacing"]).run()
```

### Mixed model (adjusted performance)

```python
Experiment(df,"Yield").mixed(fixed=["Treatment"], random=["Block"]).run()
```

### Multi-environment trial (stability)

```python
Experiment(df,"Yield").gxe("Genotype","Environment","Rep").run()
```

### Multi-year experiment

```python
Experiment(df,"Yield").by("Year").rcbd("Variety","Block").run()
```

### Multi-trait selection

```python
Experiment(df,["Yield","Height"]).rcbd("Variety","Block").run()
```

---

## What AgroDesign Handles Automatically

* Correct ANOVA model construction
* Error-term selection
* Mean separation (LSD, Tukey, DMRT)
* Interaction interpretation rules
* Mixed-model BLUP ranking
* G×E stability analysis (AMMI, GGE, FW, ER)
* Assumption diagnostics
* Publication-ready plots

No manual statistical decisions required.

---

## Philosophy

Traditional workflow:

```
Choose model → run statistics → interpret biology
```

AgroDesign workflow:

```
Describe experiment → AgroDesign chooses statistics → interpret biology
```

---

## Citation

If you use AgroDesign in academic work:

**AgroDesign v0.6.0 — Stable Research Release**
[https://github.com/DeepStatistix/AgroDesign](https://github.com/DeepStatistix/AgroDesign)

(DOI will be added via Zenodo)

---

## License

Apache-2.0 open-source license

---

## Author

Aqib Gul
DeepStatistix
