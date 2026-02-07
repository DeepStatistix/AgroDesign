import pandas as pd
import numpy as np
from scipy.stats import linregress


class FinlayWilkinson:
    """
    Finlay–Wilkinson regression stability analysis
    """

    def __init__(self, data, genotype, environment, response):
        self.data = data.copy()
        self.g = genotype
        self.e = environment
        self.y = response

    # --------------------------------------------------
    # Fit model
    # --------------------------------------------------
    def fit(self):

        # mean table
        table = self.data.pivot_table(
            values=self.y,
            index=self.g,
            columns=self.e,
            aggfunc="mean"
        )

        self.means = table

        # environmental index
        env_mean = table.mean(axis=0)
        grand_mean = env_mean.mean()
        self.env_index = env_mean - grand_mean

        results = []

        for genotype in table.index:

            y = table.loc[genotype].values
            x = self.env_index.values

            slope, intercept, r, p, stderr = linregress(x, y)

            # deviation from regression (stability)
            y_pred = intercept + slope*x
            s2di = np.sum((y - y_pred)**2) / (len(x)-2)

            results.append([
                genotype,
                table.loc[genotype].mean(),
                slope,
                s2di,
                r**2
            ])

        self.results = pd.DataFrame(
            results,
            columns=["Genotype","MeanYield","Bi","S2di","R2"]
        )

        return self.results

    # --------------------------------------------------
    # Classification
    # --------------------------------------------------
    def classify(self):

        df = self.results.copy()

        def label(row):
            if row["Bi"] > 1.1:
                return "Responsive (high-input adapted)"
            elif row["Bi"] < 0.9:
                return "Stable (stress adapted)"
            else:
                return "Widely adapted"

        df["Adaptation"] = df.apply(label, axis=1)

        return df.sort_values("MeanYield", ascending=False)
