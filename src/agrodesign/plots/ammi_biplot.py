import matplotlib.pyplot as plt


def ammi_biplot(ammi, pc1=1, pc2=2, figsize=(6,6), title="AMMI Biplot", show=True):
    """
    AMMI Biplot (IPCA scores)

    Parameters
    ----------
    ammi : fitted AMMI object
    pc1, pc2 : int
        principal components to plot
    """

    g_scores = ammi.genotype_scores
    e_scores = ammi.environment_scores

    xg = g_scores[f"IPCA{pc1}"]
    yg = g_scores[f"IPCA{pc2}"]

    xe = e_scores[f"IPCA{pc1}"]
    ye = e_scores[f"IPCA{pc2}"]

    plt.figure(figsize=figsize)

    # --- origin lines ---
    plt.axhline(0, linewidth=1)
    plt.axvline(0, linewidth=1)

    # --- genotypes ---
    plt.scatter(xg, yg, marker="o")
    for label, x, y in zip(g_scores.index, xg, yg):
        plt.text(x, y, str(label), fontsize=9, ha="right")

    # --- environments ---
    plt.scatter(xe, ye, marker="^")
    for label, x, y in zip(e_scores.index, xe, ye):
        plt.text(x, y, str(label), fontsize=9, ha="left")

    plt.xlabel(f"IPCA{pc1}")
    plt.ylabel(f"IPCA{pc2}")
    plt.title(title)

    plt.tight_layout()

    if show:
        plt.show()

    return plt.gcf()
