import matplotlib.pyplot as plt
import numpy as np


def mean_plot(
    means_df,
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
        Output from LSD or Tukey
    mean_col : str
        Column name of means
    group_col : str
        Column name of grouping letters
    se_col : str, optional
        Column name of standard error
    kind : str
        'point' or 'bar'
    """

    # Identify grouping columns automatically
    group_cols = [
        c for c in means_df.columns
        if c not in (mean_col, group_col, "Replications", se_col)
    ]

    if not group_cols:
        raise ValueError("No grouping columns found in means_df")

    # Build x-axis labels
    labels = means_df[group_cols].astype(str).agg(":".join, axis=1)

    x = np.arange(len(means_df))
    y = means_df[mean_col].values

    plt.figure(figsize=figsize)

    if kind == "bar":
        plt.bar(
            x,
            y,
            yerr=means_df[se_col] if se_col else None,
            capsize=5,
            edgecolor="black"
        )
    else:
        plt.errorbar(
            x,
            y,
            yerr=means_df[se_col] if se_col else None,
            fmt="o",
            capsize=5
        )

    # Add grouping letters (per-mean placement)
    for i, row in means_df.iterrows():
        offset = 0.03 * y[i]
        plt.text(
            x[i],
            y[i] + offset,
            row[group_col],
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold"
        )

    plt.xticks(x, labels, rotation=45)
    plt.ylabel(ylabel)
    plt.xlabel(" × ".join(group_cols))

    if title:
        plt.title(title)

    plt.tight_layout()
    plt.show()
