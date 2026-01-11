import pandas as pd
from agrodesign.analysis.anova import Anova


def test_means_computation():
    df = pd.DataFrame({
        "Treatment": ["T1","T1","T2","T2"],
        "Yield": [10,12,14,16]
    })

    aov = Anova(df, response="Yield")
    aov.crd("Treatment")
    means = aov.means("Treatment")

    assert means.loc[means["Treatment"] == "T1", "Mean"].values[0] == 11
    assert means.loc[means["Treatment"] == "T2", "Replications"].values[0] == 2
