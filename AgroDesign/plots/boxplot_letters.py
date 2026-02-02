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

    Works for:
    - CRD / RCBD
    - Factorial
    - Split plot
    - Split–split plot

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

    # -----------------------------
    # Normalize factor input
    # -----------------------------
    if isinstance(factor, str):
        factors = factor.split(":")
        effect = factor
    elif isinstance(factor, (list, tuple)):
        factors = list(factor)
        effect = ":".join(factors)
    else:
        raise ValueError("factor must be a string or list/tuple")

    # Validate factors
    for f in factors:
        if f not in data.columns:
            raise ValueError(f"Factor '{f}' not found in data")

    # -----------------------------
    # Create interaction column ONLY for plotting
    # -----------------------------
    if len(factors) > 1:
        data[effect] = (
            data[factors]
            .astype(str)
            .agg(":".join, axis=1)
        )
    else:
        effect = factors[0]

    # -----------------------------
    # Mean separation (design-aware)
    # -----------------------------
    aov.factorial_means(factors)

    if method == "tukey":
        sep = TukeyHSD(aov, effect=effect, alpha=alpha)
        means = sep.test()
    elif method == "lsd":
        sep = LSD(aov, effect=effect, alpha=alpha)
        means = sep.test()
    else:
        raise ValueError("method must be 'tukey' or 'lsd'")

    # -----------------------------
    # Prepare boxplot data
    # (ORDER MUST MATCH means table)
    # -----------------------------
    # ---------------------------------
    # Build group labels safely
    # ---------------------------------
    if len(factors) == 1:
        group_labels = means[factors[0]].astype(str).values
    else:
        group_labels = (
            means[factors]
            .astype(str)
            .agg(":".join, axis=1)
            .values
        )

    # ---------------------------------
    # Boxplot data
    # ---------------------------------
    box_data = [
        data[data[effect].astype(str) == g][response]
        for g in group_labels
    ]


    # -----------------------------
    # Plot
    # -----------------------------
    plt.figure(figsize=figsize)

    bp = plt.boxplot(
        box_data,
        tick_labels=group_labels,
        patch_artist=True,
        showmeans=True
    )

    for box in bp["boxes"]:
        box.set(facecolor="lightgray", edgecolor="black")

    # -----------------------------
    # Add grouping letters (just above each box)
    # -----------------------------
    y_range = max(means["Mean"]) - min(means["Mean"])
    offset = 0.05 * y_range if y_range > 0 else 0.05

    for i, g in enumerate(group_labels):
        y_max_box = max(box_data[i])
        if len(factors) == 1:
            letter = means.loc[
                means[factors[0]].astype(str) == g, "Group"
            ].values[0]
        else:
            mask = (
                means[factors]
                .astype(str)
                .agg(":".join, axis=1) == g
            )
            letter = means.loc[mask, "Group"].values[0]

        plt.text(
            i + 1,
            y_max_box + offset,
            letter,
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold"
        )

    plt.ylabel(ylabel)
    plt.xlabel(effect)
    if title:
        plt.title(title)

    plt.tight_layout()
    if show:
        plt.show()
    else:
        plt.close()
