import matplotlib.pyplot as plt
import numpy as np
from agrodesign.mean_separation.tukey import TukeyHSD
from agrodesign.mean_separation.lsd import LSD


def boxplot_letters(
    aov,
    factor,
    method="tukey",
    response=None,
    ylabel="Response",
    title=None,
    alpha=0.05,
    figsize=(6, 4)
):
    """
    Boxplot with grouping letters (LSD / Tukey)

    Parameters
    ----------
    aov : Anova object
    factor : str or tuple
        'A', 'B', or ('A','B')
    method : str
        'tukey' or 'lsd'
    """

    data = aov.data.copy()
    response = response or aov.response

    # Handle interaction internally
    if isinstance(factor, tuple):
        factor_name = ":".join(factor)
        data[factor_name] = (
            data[factor[0]].astype(str) + ":" +
            data[factor[1]].astype(str)
        )
    else:
        factor_name = factor

    # Mean separation
    if method == "tukey":
        sep = TukeyHSD(aov, factor=factor, alpha=alpha)
        means = sep.test()
    elif method == "lsd":
        aov.means(factor_name)
        sep = LSD(aov, alpha=alpha)
        means = sep.test()
    else:
        raise ValueError("method must be 'tukey' or 'lsd'")

    # Boxplot data
    groups = data[factor_name].unique()
    box_data = [data[data[factor_name] == g][response] for g in groups]

    plt.figure(figsize=figsize)
    bp = plt.boxplot(
        box_data,
        tick_labels=groups,
        patch_artist=True,
        showmeans=True
    )

    for box in bp["boxes"]:
        box.set(facecolor="lightgray", edgecolor="black")

    
    for i, g in enumerate(groups):
        y_max_box = max(box_data[i])          # top of THIS box
        offset = 0.03 * y_max_box             # small relative offset

        letter = means.loc[means[factor_name] == g, "Group"].values
        if len(letter):
            plt.text(
                i + 1,
                y_max_box + offset,
                letter[0],
                ha="center",
                va="bottom",
                fontsize=12,
                fontweight="bold"
            )

