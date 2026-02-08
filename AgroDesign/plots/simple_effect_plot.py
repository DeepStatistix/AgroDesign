import matplotlib.pyplot as plt
from itertools import product
from agrodesign.analysis.anova import Anova
from agrodesign.plots.interaction_plot import interaction_plot


def simple_effect_plot(aov, highest_effect, method="tukey", alpha=0.05, show=True):
    """
    Automatically plots conditional interaction plots
    when higher-order interaction is significant.

    Example:
    A×B×C significant →
    Plot A×B within each C
    """

    factors = highest_effect.split(":")
    target_pair = factors[:2]
    conditioning = factors[2:]

    if len(conditioning) == 0:
        return []

    data = aov.data

    cond_levels = [
        sorted(data[c].unique()) for c in conditioning
    ]

    figs = []

    for combo in product(*cond_levels):

        subset = data.copy()
        title_parts = []

        for c, lvl in zip(conditioning, combo):
            subset = subset[subset[c] == lvl]
            title_parts.append(f"{c} = {lvl}")

        if subset.empty:
            continue

        sub_aov = Anova(subset, aov.response)
        sub_aov.factorial(target_pair)

        fig = interaction_plot(
            sub_aov,
            target_pair,
            method=method,
            alpha=alpha,
            title=f"{target_pair[0]} × {target_pair[1]} at " + ", ".join(title_parts),
            show=show
        )
        figs.append(fig)

    return figs
