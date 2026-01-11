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
    figsize=(6, 4),
    show=True
):
    """
    Boxplot with grouping letters (LSD / Tukey)

    Parameters
    ----------
    aov : Anova object
    factor : str or list/tuple of str
        "A", ["A","B"], ["A","B","C"]
    method : str
        'tukey' or 'lsd'
    """

    data = aov.data.copy()
    response = response or aov.response

    # Normalize factor input
    if isinstance(factor, str):
        factors = [factor]
    elif isinstance(factor, (list, tuple)):
        factors = list(factor)
    else:
        raise ValueError("factor must be a string or list/tuple")

    # Validate factors
    for f in factors:
        if f not in data.columns:
            raise ValueError(f"Factor '{f}' not found in data")

    # Interaction name
    factor_name = factors[0] if len(factors) == 1 else ":".join(factors)

    # Create interaction column ONLY for plotting
    if len(factors) > 1:
        data[factor_name] = (
            data[factors]
            .astype(str)
            .agg(":".join, axis=1)
        )

    # Mean separation (delegated correctly)
    if method == "tukey":
        sep = TukeyHSD(aov, factor=factors, alpha=alpha)
        means = sep.test()
    elif method == "lsd":
        aov.factorial_means(factors)
        sep = LSD(aov, alpha=alpha)
        means = sep.test()
    else:
        raise ValueError("method must be 'tukey' or 'lsd'")

    # Prepare boxplot data
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

    # Add grouping letters (correct placement)
    for i, g in enumerate(groups):
        y_max_box = max(box_data[i])
        offset = 0.03 * y_max_box

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

    plt.ylabel(ylabel)
    plt.xlabel(factor_name)
    if title:
        plt.title(title)

    plt.tight_layout()
    if show:
        plt.show()
    else:
        plt.close()
