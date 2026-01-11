import pandas as pd
from agrodesign.analysis.anova import Anova
from agrodesign.analysis.assumptions import Assumptions


def test_assumptions_run():
    df = pd.DataFrame({
        "Treatment": ["T1","T1","T2","T2"],
        "Yield": [10,12,14,16]
    })

    aov = Anova(df, response="Yield")
    aov.crd("Treatment")

    assump = Assumptions(aov)

    shapiro = assump.shapiro_test()
    assert "p-value" in shapiro
