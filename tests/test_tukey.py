import pandas as pd
from agrodesign.analysis.anova import Anova
from agrodesign.mean_separation.tukey import TukeyHSD


def test_tukey_factorial_main_effect():
    df = pd.DataFrame({
        "A": ["A1","A1","A2","A2"],
        "Yield": [10,12,18,20]
    })

    aov = Anova(df, response="Yield")
    aov.factorial(['A'])   # harmless for test

    tukey = TukeyHSD(aov, factor="A")
    result = tukey.test()

    assert "Group" in result.columns
    assert result.iloc[0]["Group"] == "a"
