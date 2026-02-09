import matplotlib.pyplot as plt
import numpy as np

from agrodesign.mean_separation.lsd import LSD
from agrodesign.mean_separation.tukey import TukeyHSD
from agrodesign.mean_separation.dmrt import DMRT


def interaction_plot(
    aov,
    factors,
    method="tukey",
    alpha=0.05,
    ylabel="Response",
    title=None,
    figsize=(6, 4),
    ax=None,
    show=True
):
    """
    Agronomy-style interaction plot with grouping letters
    AXIS-AWARE VERSION (works inside report_plot)

    Parameters
    ----------
    aov : Anova object
    factors : list/tuple length 2 → ["A","B"]
    method : "lsd", "tukey", "dmrt"
    """

    if not isinstance(factors, (list, tuple)) or len(factors) != 2:
        raise ValueError("factors must be ['A','B']")

    A, B = factors
    response = aov.response

    # ============================================================
    # Prepare axis
    # ============================================================
    standalone = False
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
        standalone = True

    # ============================================================
    # Compute means
    # ============================================================
    aov.factorial_means([A, B])

    effect_name = f"{A}:{B}"

    if method.lower() == "lsd":
        sep = LSD(aov, effect=effect_name, alpha=alpha)
    elif method.lower() == "tukey":
        sep = TukeyHSD(aov, effect=effect_name, alpha=alpha)
    elif method.lower() == "dmrt":
        sep = DMRT(aov, effect=effect_name, alpha=alpha)
    else:
        raise ValueError("method must be 'lsd', 'tukey', or 'dmrt'")

    means = sep.test()

    # ============================================================
    # Structure data
    # ============================================================
    A_levels = list(dict.fromkeys(means[A]))
    B_levels = list(dict.fromkeys(means[B]))

    markers = ["o", "s", "^", "D", "v", "P", "X", "*"]

    ymax = max(means["Mean"])
    offset = 0.05 * ymax if ymax != 0 else 0.1

    # ============================================================
    # Plot each B level as line
    # ============================================================
    for i, b in enumerate(B_levels):

        y_vals = []
        letters = []

        for a in A_levels:
            row = means[(means[A] == a) & (means[B] == b)]
            if row.empty:
                y_vals.append(np.nan)
                letters.append("")
            else:
                y_vals.append(row["Mean"].values[0])
                letters.append(str(row["Group"].values[0]))

        x = np.arange(len(A_levels))

        ax.plot(
            x,
            y_vals,
            marker=markers[i % len(markers)],
            linewidth=1.8,
            label=f"{B} = {b}"
        )

        # letters
        for xi, yi, lab in zip(x, y_vals, letters):
            if np.isnan(yi) or lab == "":
                continue
            ax.text(
                xi,
                yi + offset,
                lab,
                ha="center",
                va="bottom",
                fontsize=11,
                fontweight="bold"
            )

    # ============================================================
    # Formatting
    # ============================================================
    ax.set_xticks(np.arange(len(A_levels)))
    ax.set_xticklabels(A_levels)
    ax.set_xlabel(A)
    ax.set_ylabel(ylabel)

    if title:
        ax.set_title(title)
    else:
        ax.set_title(f"Interaction: {A} × {B}")

    ax.legend(frameon=False)

    if standalone:
        plt.tight_layout()
        if show:
            plt.show()
        # Do not close the figure when show=False to allow later display

    return ax.figure if standalone else ax
