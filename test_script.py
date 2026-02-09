import pandas as pd
from agrodesign.experiment import Experiment

df = pd.DataFrame({
    "Rep": [1]*8 + [2]*8 + [3]*8,
    "A": ["A1","A1","A1","A1","A2","A2","A2","A2"] * 3,
    "B": ["B1","B1","B2","B2","B1","B1","B2","B2"] * 3,
    "C": ["C1","C2","C1","C2","C1","C2","C1","C2"] * 3,
    "Yield": [
        10,12,11,13,15,17,16,18,
        11,13,12,14,16,18,17,19,
        12,14,13,15,17,19,18,20
    ]
})

result = Experiment(df, "Yield").factorial(["A", "B", "C"]).run()
print(result)
