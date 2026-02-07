import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

from agrodesign.plots.effect_plot import effect_plot
from agrodesign.analysis.assumptions import Assumptions


def report_plot(
    aov,
    effect,
    method="tukey",
    alpha=0.05,
    figsize=(10, 8),
    save=None,
    dpi=300
):
    """
    Full experiment visual report

    Panels:
    1) ANOVA significance
    2) Effect / interaction plot
    3) QQ plot
    4) Residual vs fitted
    """

    if aov.model is None:
        raise RuntimeError("Run ANOVA before report_plot()")

    fig, axes = plt.subplots(2, 2, figsize=figsize)

    ax1, ax2, ax3, ax4 = axes.flatten()

    # ---------------------------------------------------
    # PANEL 1 — ANOVA SIGNIFICANCE SUMMARY
    # ---------------------------------------------------
    table = aov.anova_table.copy()

    # detect p-value column automatically
    pcol = None
    for candidate in ["p-value", "PR(>F)", "Pr>F", "P", "p"]:
        if candidate in table.columns:
            pcol = candidate
            break

    if pcol is None:
        raise RuntimeError("ANOVA table has no p-value column")

    sig = []
    names = []

    for idx, row in table.iterrows():

        if str(idx).lower() in ["residual", "error"]:
            continue

        pval = row[pcol]

        if pval is None or np.isnan(pval):
            continue

        names.append(str(idx))
        sig.append(-np.log10(pval) if pval > 0 else 10)

    ax1.barh(names, sig)
    ax1.axvline(-np.log10(alpha), linestyle="--")
    ax1.set_xlabel("-log10(p-value)")
    ax1.set_title("ANOVA Significance")

    # ---------------------------------------------------
    # PANEL 2 — EFFECT / INTERACTION PLOT
    # ---------------------------------------------------
    effect_plot(
        aov,
        effect,
        method=method,
        alpha=alpha,
        ylabel=aov.response,
        ax=ax2,
        show=False
    )

    # ---------------------------------------------------
    # PANEL 3 — QQ PLOT
    # ---------------------------------------------------
    assump = Assumptions(aov)
    residuals = assump.residuals

    stats.probplot(residuals, plot=ax3)
    ax3.set_title("Normality (QQ Plot)")

    # ---------------------------------------------------
    # PANEL 4 — RESIDUAL vs FITTED
    # ---------------------------------------------------
    fitted = assump.fitted

    ax4.scatter(fitted, residuals)
    ax4.axhline(0, linestyle="--")
    ax4.set_xlabel("Fitted")
    ax4.set_ylabel("Residuals")
    ax4.set_title("Homoscedasticity")

    plt.tight_layout()

    # optional export
    if save is not None:
        plt.savefig(save, dpi=dpi, bbox_inches="tight")

    plt.show()
