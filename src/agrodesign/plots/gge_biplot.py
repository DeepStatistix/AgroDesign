import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull


def gge_biplot(data, genotype, environment, response,
               figsize=(7,7), title="GGE Biplot", show=True):
    """
    GGE Biplot (Which-won-where)

    Parameters
    ----------
    data : DataFrame
    genotype : str
    environment : str
    response : str
    """

    # -----------------------------
    # 1. Mean table
    # -----------------------------
    table = data.pivot_table(
        values=response,
        index=genotype,
        columns=environment,
        aggfunc="mean"
    )

    # -----------------------------
    # 2. Remove environment means
    # -----------------------------
    env_means = table.mean(axis=0)
    gge = table - env_means

    # -----------------------------
    # 3. SVD
    # -----------------------------
    U, S, VT = np.linalg.svd(gge.values, full_matrices=False)

    G_scores = U * np.sqrt(S)
    E_scores = (VT.T * np.sqrt(S))

    G = pd.DataFrame(G_scores[:, :2], index=table.index, columns=["PC1","PC2"])
    E = pd.DataFrame(E_scores[:, :2], index=table.columns, columns=["PC1","PC2"])

    # -----------------------------
    # 4. Convex hull (polygon)
    # -----------------------------
    hull = ConvexHull(G.values)
    hull_points = G.iloc[hull.vertices]

    # -----------------------------
    # 5. Plot
    # -----------------------------
    plt.figure(figsize=figsize)

    # axes
    plt.axhline(0, linewidth=1)
    plt.axvline(0, linewidth=1)

    # genotypes
    plt.scatter(G["PC1"], G["PC2"])
    for i in G.index:
        plt.text(G.loc[i,"PC1"], G.loc[i,"PC2"], str(i), fontsize=9)

    # environments
    plt.scatter(E["PC1"], E["PC2"], marker="^")
    for i in E.index:
        plt.text(E.loc[i,"PC1"], E.loc[i,"PC2"], str(i), fontsize=9)

    # polygon
    poly = np.append(hull.vertices, hull.vertices[0])
    plt.plot(G.iloc[poly]["PC1"], G.iloc[poly]["PC2"], linewidth=1.5)

    # rays (sector division)
    center = np.array([0,0])
    for point in hull_points.values:
        vec = point - center
        vec = vec / np.linalg.norm(vec)
        plt.plot([0, vec[0]*max(abs(G.values.flatten()))],
                 [0, vec[1]*max(abs(G.values.flatten()))],
                 linestyle="--")

    plt.title(title)
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.tight_layout()

    if show:
        plt.show()

    return plt.gcf()
