import pandas as pd
import matplotlib
matplotlib.use("Agg")   # prevent GUI issues in CI

from agrodesign.analysis.anova import Anova
from agrodesign.mean_separation.lsd import LSD
from agrodesign.mean_separation.tukey import TukeyHSD
from agrodesign.mean_separation.dmrt import DMRT

from agrodesign.plots.mean_plot import mean_plot
from agrodesign.plots.boxplot_letters import boxplot_letters
from agrodesign.plots.interaction_plot import interaction_plot
from agrodesign.plots.report_plot import report_plot


# =========================================================
# DATASETS
# =========================================================

def dataset_crd():
    return pd.DataFrame({
        "Treatment": ["T1","T1","T2","T2","T3","T3"],
        "Yield": [10,11,14,13,18,17]
    })


def dataset_rcbd():
    return pd.DataFrame({
        "Block":[1,1,1,2,2,2,3,3,3],
        "Treatment":["T1","T2","T3"]*3,
        "Yield":[10,12,15,11,13,14,9,12,16]
    })


def dataset_factorial():
    return pd.DataFrame({
        "A":["A1","A1","A2","A2"]*2,
        "B":["B1","B2"]*4,
        "Yield":[10,11,14,15,18,17,20,21]
    })


def dataset_split():
    return pd.DataFrame({
        "Rep":[1,1,1,1,2,2,2,2],
        "A":["A1","A1","A1","A1","A2","A2","A2","A2"],
        "B":["B1","B1","B2","B2","B1","B1","B2","B2"],
        "Yield":[10,12,11,13,15,17,16,18]
    })


# =========================================================
# CRD PIPELINE
# =========================================================

def test_crd_full_pipeline():
    df = dataset_crd()
    aov = Anova(df, response="Yield")

    aov.crd("Treatment")
    aov.means("Treatment")

    LSD(aov).test()
    TukeyHSD(aov, effect="Treatment").test()
    DMRT(aov).test()

    mean_plot(aov=aov, factor="Treatment", show=False)
    boxplot_letters(aov, "Treatment", show=False)
    report_plot(aov, "Treatment", show=False)


# =========================================================
# RCBD PIPELINE
# =========================================================

def test_rcbd_full_pipeline():
    df = dataset_rcbd()
    aov = Anova(df, response="Yield")

    aov.rcbd("Treatment","Block")
    aov.means("Treatment")

    LSD(aov).test()
    TukeyHSD(aov, effect="Treatment").test()
    DMRT(aov).test()

    mean_plot(aov=aov, factor="Treatment", show=False)


# =========================================================
# FACTORIAL PIPELINE
# =========================================================

def test_factorial_full_pipeline():
    df = dataset_factorial()
    aov = Anova(df, response="Yield")

    aov.factorial(["A","B"])
    aov.factorial_means(["A","B"])

    LSD(aov, effect="A:B").test()
    TukeyHSD(aov, effect="A:B").test()
    DMRT(aov).test()

    interaction_plot(aov, ["A","B"], show=False)
    report_plot(aov, ["A","B"], show=False)


# =========================================================
# SPLIT PLOT PIPELINE
# =========================================================

def test_splitplot_full_pipeline():
    df = dataset_split()
    aov = Anova(df, response="Yield")

    aov.split_plot("A","B","Rep")
    aov.factorial_means(["A","B"])

    LSD(aov, effect="A:B").test()
    TukeyHSD(aov, effect="A:B").test()
    DMRT(aov).test()

    interaction_plot(aov, ["A","B"], show=False)
