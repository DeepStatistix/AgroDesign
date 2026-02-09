import matplotlib.pyplot as plt


def stability_scatter(er, figsize=(6,6), title="Eberhart-Russell Stability Scatter", show=True):
    """
    Eberhart-Russell stability scatter plot (bi vs S2di)

    Parameters
    ----------
    er : fitted EberhartRussell object
    figsize : tuple
        Figure size
    title : str
        Plot title
    show : bool
        Whether to display the plot
    """

    df = er.results

    plt.figure(figsize=figsize)

    # Scatter plot of bi vs S2di
    plt.scatter(df["bi"], df["S2di"], color='green')

    # Add labels
    for i, row in df.iterrows():
        plt.text(row["bi"], row["S2di"], row["Genotype"], fontsize=9, ha='right')

    # Reference lines
    plt.axvline(x=1, color='red', linestyle='--', label='bi = 1')
    plt.axhline(y=df["S2di"].median(), color='orange', linestyle=':', label='Median S2di')

    plt.xlabel("Regression Coefficient (bi)")
    plt.ylabel("Deviation Mean Square (S2di)")
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if show:
        plt.show()
    else:
        plt.close()

    return plt.gcf()
