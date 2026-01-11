import pandas as pd
from agrodesign.analysis.anova import Anova
from agrodesign.mean_separation.lsd import LSD


def test_lsd_groups_created():
    df = pd.DataFrame({
        "Treatment": ["T1","T1","T2","T2","T3","T3"],
        "Yield": [10,12,15,14,18,17]
    })

    aov = Anova(df, response="Yield")
    aov.crd("Treatment")
    aov.means("Treatment")

    lsd = LSD(aov)
    result = lsd.test()

    assert "Group" in result.columns
    assert len(result["Group"].unique()) >= 2
