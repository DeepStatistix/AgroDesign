import pandas as pd
from statsmodels.stats.multicomp import pairwise_tukeyhsd


class TukeyHSD:
    """
    Tukey Honest Significant Difference (HSD) test
    """

    def __init__(self, anova, factor, alpha=0.05):
        """
        Parameters
        ----------
        anova : Anova object
            Fitted ANOVA model
        factor : str or list/tuple of str
            "A" → main effect
            ["A","B"] → A×B
            ["A","B","C"] → A×B×C
        alpha : float
            Significance level
        """
        if anova.model is None:
            raise RuntimeError("Run ANOVA before Tukey HSD")

        self.anova = anova
        self.alpha = alpha
        self.data = anova.data.copy()
        self.response = anova.response

        # Normalize factor input
        if isinstance(factor, str):
            self.factors = [factor]
        elif isinstance(factor, (list, tuple)):
            self.factors = list(factor)
        else:
            raise ValueError("factor must be a string or list/tuple of strings")

        # Validate columns
        for f in self.factors:
            if f not in self.data.columns:
                raise ValueError(f"Factor '{f}' not found in data")

        # Create interaction factor internally
        if len(self.factors) == 1:
            self.factor_name = self.factors[0]
        else:
            self.factor_name = ":".join(self.factors)
            self.data[self.factor_name] = (
                self.data[self.factors]
                .astype(str)
                .agg(":".join, axis=1)
            )

    def test(self):
        """
        Perform Tukey HSD test and assign grouping letters
        """
        tukey = pairwise_tukeyhsd(
            endog=self.data[self.response],
            groups=self.data[self.factor_name],
            alpha=self.alpha
        )

        self.pairwise = pd.DataFrame(
            tukey.summary().data[1:],
            columns=tukey.summary().data[0]
        )

        return self._group_means()

    def _group_means(self):
        """
        Assign grouping letters using full Tukey pairwise logic
        """
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
            letter = "a"
            for j in range(i):
                row = self.pairwise[
                    (
                        (self.pairwise["group1"] == means.loc[j, self.factor_name]) &
                        (self.pairwise["group2"] == means.loc[i, self.factor_name])
                    ) |
                    (
                        (self.pairwise["group1"] == means.loc[i, self.factor_name]) &
                        (self.pairwise["group2"] == means.loc[j, self.factor_name])
                    )
                ]

                if not row.empty and row["reject"].values[0]:
                    letter = chr(ord(letter) + 1)

            groups.append(letter)

        means["Group"] = groups
        self.grouped_means = means
        return means
