import matplotlib.pyplot as plt


def fw_plot(fw, figsize=(6,6), title="Finlay-Wilkinson Regression", show=True):
    """
    Finlay-Wilkinson regression plot

    Parameters
    ----------
    fw : fitted FinlayWilkinson object
    figsize : tuple
        Figure size
    title : str
        Plot title
    show : bool
        Whether to display the plot
    """

    df = fw.results

    plt.figure(figsize=figsize)

    # Scatter plot of Bi vs MeanYield
    plt.scatter(df["MeanYield"], df["Bi"], color='blue')

    # Add labels
    for i, row in df.iterrows():
        plt.text(row["MeanYield"], row["Bi"], row["Genotype"], fontsize=9, ha='right')

    # Reference lines
    plt.axhline(y=1, color='red', linestyle='--', label='Bi = 1')
    plt.axhline(y=0.9, color='orange', linestyle=':', label='Bi = 0.9')
    plt.axhline(y=1.1, color='orange', linestyle=':', label='Bi = 1.1')

    plt.xlabel("Mean Yield")
    plt.ylabel("Regression Coefficient (Bi)")
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if show:
        plt.show()

    return plt.gcf()
