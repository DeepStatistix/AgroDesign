import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless backend

from agrodesign.analysis.anova import Anova
from agrodesign.plots import boxplot_letters


def test_boxplot_letters_runs():
    df = pd.DataFrame({
        "A": ["A1","A1","A2","A2"],
        "Yield": [10,12,18,20]
    })

    aov = Anova(df, response="Yield")
    aov.factorial(['A'])

    boxplot_letters(aov, factor="A", show=False)
