import pandas as pd
from statsmodels.stats.multicomp import pairwise_tukeyhsd


class TukeyHSD:
    """
    Tukey Honest Significant Difference (HSD) test
    """

    def __init__(self, anova, factor, alpha=0.05):
        if anova.model is None:
            raise RuntimeError("Run ANOVA before Tukey HSD")

        self.anova = anova
        self.factor = factor
        self.alpha = alpha
        self.data = anova.data.copy()
        self.response = anova.response

        # Handle interaction
        if isinstance(factor, tuple):
            self.factor_name = ":".join(factor)
            self.data[self.factor_name] = (
                self.data[factor[0]].astype(str) + ":" +
                self.data[factor[1]].astype(str)
            )
        else:
            self.factor_name = factor

    def test(self):
        tukey = pairwise_tukeyhsd(
            endog=self.data[self.response],
            groups=self.data[self.factor_name],
            alpha=self.alpha
        )

        results = pd.DataFrame(
            tukey.summary().data[1:],
            columns=tukey.summary().data[0]
        )

        self.pairwise = results
        return self._group_means(results)

    def _group_means(self, results):
        means = (
            self.data
            .groupby(self.factor_name)[self.response]
            .mean()
            .reset_index(name="Mean")
            .sort_values("Mean", ascending=False)
            .reset_index(drop=True)
        )

        groups = ["a"]

        for i in range(1, len(means)):
            sig = False
            for j in range(i):
                row = results[
                    ((results["group1"] == means.loc[j, self.factor_name]) &
                     (results["group2"] == means.loc[i, self.factor_name])) |
                    ((results["group1"] == means.loc[i, self.factor_name]) &
                     (results["group2"] == means.loc[j, self.factor_name]))
                ]

                if not row.empty and row["reject"].values[0]:
                    sig = True

            if sig:
                groups.append(chr(ord(groups[-1]) + 1))
            else:
                groups.append(groups[-1])

        means["Group"] = groups
        self.grouped_means = means
        return means
