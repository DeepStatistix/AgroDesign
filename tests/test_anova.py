import pandas as pd
from agrodesign.analysis.anova import Anova


def test_crd_anova_runs():
    df = pd.DataFrame({
        "Treatment": ["T1","T1","T2","T2","T3","T3"],
        "Yield": [10,12,15,14,18,17]
    })

    aov = Anova(df, response="Yield")
    table = aov.crd("Treatment")

    assert "Residual" in table.index
    assert table.loc["C(Treatment)", "DF"] == 2
    assert table.loc["Residual", "DF"] == 3
