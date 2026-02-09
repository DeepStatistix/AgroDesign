import matplotlib.pyplot as plt
import numpy as np

# optional imports (lazy usage)
from agrodesign.mean_separation.lsd import LSD
from agrodesign.mean_separation.tukey import TukeyHSD
from agrodesign.mean_separation.dmrt import DMRT


def mean_plot(
    means_df=None,
    *,
    aov=None,
    factor=None,
    method="tukey",
    alpha=0.05,
    mean_col="Mean",
    group_col="Group",
    se_col=None,
    kind="point",
    ylabel="Response",
    title=None,
    figsize=(6, 4),
    ax=None,
    show=True
):
    """
    Plot treatment/factor means with grouping letters.

    TWO USAGE MODES
    ----------------
    1) Classic mode:
        mean_plot(means_df)

    2) Automatic mode:
        mean_plot(aov=aov, factor="A", method="dmrt")
    """

    # ============================================================
    # AUTO MODE
    # ============================================================
    if means_df is None:
        if aov is None or factor is None:
            raise ValueError("Provide either means_df OR (aov + factor)")

        if isinstance(factor, str):
            factors = [factor]
        else:
            factors = list(factor)

        # compute means
        aov.factorial_means(factors)

        effect_name = ":".join(factors)

        if method.lower() == "lsd":
            sep = LSD(aov, effect=effect_name, alpha=alpha)
        elif method.lower() == "tukey":
            sep = TukeyHSD(aov, effect=effect_name, alpha=alpha)
        elif method.lower() == "dmrt":
            sep = DMRT(aov, effect=effect_name, alpha=alpha)
        else:
            raise ValueError("method must be lsd/tukey/dmrt")

        means_df = sep.test()

    # ============================================================
    # Prepare axis
    # ============================================================
    standalone = False
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
        standalone = True

    # ============================================================
    # Identify factor columns
    # ============================================================
    group_cols = [
        c for c in means_df.columns
        if c not in (mean_col, group_col, "Replications", se_col)
    ]

    if not group_cols:
        raise ValueError("No grouping columns found in means_df")

    labels = means_df[group_cols].astype(str).agg(":".join, axis=1)

    x = np.arange(len(means_df))
    y = means_df[mean_col].values

    # ============================================================
    # Plot means
    # ============================================================
    if kind == "bar":
        ax.bar(
            x,
            y,
            yerr=means_df[se_col] if se_col else None,
            capsize=5,
            edgecolor="black"
        )
    else:
        ax.errorbar(
            x,
            y,
            yerr=means_df[se_col] if se_col else None,
            fmt="o",
            capsize=5
        )

    # ============================================================
    # Add grouping letters (CLD compatible)
    # ============================================================
    y_range = max(y) - min(y) if len(y) > 1 else max(y)
    offset = 0.05 * y_range if y_range > 0 else 0.1

    for i, row in means_df.iterrows():
        ax.text(
            x[i],
            y[i] + offset,
            str(row[group_col]),
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold"
        )

    # ============================================================
    # Formatting
    # ============================================================
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(" × ".join(group_cols))

    if title:
        ax.set_title(title)

    # ============================================================
    # Show / Return behavior
    # ============================================================
    if standalone:
        plt.tight_layout()
        if show:
            plt.show()
            plt.close()  # Close after showing to free memory

    return ax.figure if standalone else ax
