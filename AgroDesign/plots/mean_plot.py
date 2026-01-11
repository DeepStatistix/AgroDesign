import matplotlib.pyplot as plt
import numpy as np


def mean_plot(
    means_df,
    factor,
    mean_col="Mean",
    group_col="Group",
    se_col=None,
    kind="point",
    ylabel="Response",
    title=None,
    figsize=(6, 4)
):
    """
    Plot means with grouping letters (LSD / Tukey)

    Parameters
    ----------
    means_df : pandas.DataFrame
        Output from LSD or Tukey (must contain Mean and Group)
    factor : str
        Factor name (x-axis)
    mean_col : str
        Column name of means
    group_col : str
        Column name of grouping letters
    se_col : str, optional
        Column name of standard error
    kind : str
        'point' or 'bar'
    ylabel : str
        Y-axis label
    title : str
        Plot title
    figsize : tuple
        Figure size
    """

    x = np.arange(len(means_df))
    y = means_df[mean_col].values

    plt.figure(figsize=figsize)

    if kind == "bar":
        plt.bar(x, y, yerr=means_df[se_col] if se_col else None,
                capsize=5, edgecolor="black")
    else:
        plt.errorbar(
            x, y,
            yerr=means_df[se_col] if se_col else None,
            fmt="o",
            capsize=5
        )

    # Add grouping letters
    for i, row in means_df.iterrows():
        plt.text(
            x[i],
            y[i] + (0.05 * max(y)),
            row[group_col],
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold"
        )

    plt.xticks(x, means_df[factor])
    plt.ylabel(ylabel)
    plt.xlabel(factor)

    if title:
        plt.title(title)

    plt.tight_layout()
    plt.show()
