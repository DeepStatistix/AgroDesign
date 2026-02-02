import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless backend for CI

from agrodesign.analysis.anova import Anova
from agrodesign.plots.boxplot_letters import boxplot_letters


def _split_plot_data():
    """
    Helper dataset for split-plot testing
    """
    return pd.DataFrame({
        "Rep": [1,1,1,1, 2,2,2,2],
        "A": ["A1","A1","A1","A1","A2","A2","A2","A2"],
        "B": ["B1","B1","B2","B2","B1","B1","B2","B2"],
        "Yield": [10,12,11,13,15,17,16,18]
    })


# -----------------------------
# MAIN EFFECT PLOT
# -----------------------------
def test_boxplot_main_effect_runs():
    df = _split_plot_data()

    aov = Anova(df, response="Yield")
    aov.split_plot("A", "B", "Rep")

    # Should run without error
    boxplot_letters(
        aov,
        factor="A",
        method="lsd",
        show=False
    )


# -----------------------------
# SUB-PLOT FACTOR PLOT
# -----------------------------
def test_boxplot_sub_plot_runs():
    df = _split_plot_data()

    aov = Anova(df, response="Yield")
    aov.split_plot("A", "B", "Rep")

    boxplot_letters(
        aov,
        factor="B",
        method="lsd",
        show=False
    )


# -----------------------------
# INTERACTION PLOT (A × B)
# -----------------------------
def test_boxplot_interaction_runs():
    df = _split_plot_data()

    aov = Anova(df, response="Yield")
    aov.split_plot("A", "B", "Rep")

    boxplot_letters(
        aov,
        factor=["A", "B"],
        method="tukey",
        show=False
    )


# -----------------------------
# INTERACTION STRING SYNTAX
# -----------------------------
def test_boxplot_interaction_string_runs():
    df = _split_plot_data()

    aov = Anova(df, response="Yield")
    aov.split_plot("A", "B", "Rep")

    boxplot_letters(
        aov,
        factor="A:B",
        method="tukey",
        show=False
    )
