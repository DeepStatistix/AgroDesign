import pandas as pd
import numpy as np
from scipy.stats import t, f, linregress


class EberhartRussell:
    """
    Eberhart–Russell stability analysis (1966)
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

        table = self.data.pivot_table(
            values=self.y,
            index=self.g,
            columns=self.e,
            aggfunc="mean"
        )

        self.means = table

        env_mean = table.mean(axis=0)
        grand_mean = env_mean.mean()
        env_index = env_mean - grand_mean

        results = []

        e = len(env_index)

        for genotype in table.index:

            y = table.loc[genotype].values
            x = env_index.values

            slope, intercept, r, p, stderr = linregress(x, y)

            # predicted
            yhat = intercept + slope*x

            # deviation mean square
            s2di = np.sum((y - yhat)**2) / (e - 2)

            # standard error of slope
            se_b = stderr

            # t-test (bi = 1)
            t_b = (slope - 1) / se_b
            p_b = 2*(1 - t.cdf(abs(t_b), df=e-2))

            results.append([
                genotype,
                table.loc[genotype].mean(),
                slope,
                s2di,
                t_b,
                p_b,
                r**2
            ])

        self.results = pd.DataFrame(
            results,
            columns=[
                "Genotype",
                "MeanYield",
                "bi",
                "S2di",
                "t(bi=1)",
                "p(bi=1)",
                "R2"
            ]
        )

        return self.results

    # --------------------------------------------------
    # Classification
    # --------------------------------------------------
    def classify(self):

        df = self.results.copy()

        def interpret(row):

            if row["p(bi=1)"] > 0.05 and row["S2di"] < df["S2di"].median():
                return "Widely adapted (stable)"

            if row["bi"] > 1 and row["p(bi=1)"] < 0.05:
                return "High-input responsive"

            if row["bi"] < 1 and row["p(bi=1)"] < 0.05:
                return "Stress tolerant"

            return "Unstable"

        df["Adaptation"] = df.apply(interpret, axis=1)

        return df.sort_values("MeanYield", ascending=False)
