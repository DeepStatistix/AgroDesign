import pandas as pd
import numpy as np
from scipy.stats import t


class LSD:
    """
    Least Significant Difference (LSD) test
    """

    def __init__(self, anova, alpha=0.05):
        """
        Parameters
        ----------
        anova : Anova object
            Fitted ANOVA model (ANOVA + means already computed)
        alpha : float
            Significance level
        """
        if not hasattr(anova, "means_table"):
            raise RuntimeError("Run means() or factorial_means() before LSD test")

        self.anova = anova
        self.alpha = alpha
        self.means = anova.means_table.copy()

        self.error_ms = anova.error_ms
        self.error_df = anova.error_df

        # Identify grouping columns (all except Mean, Replications)
        self.group_cols = [
            c for c in self.means.columns
            if c not in ("Mean", "Replications")
        ]

    def test(self):
        """
        Perform LSD test and assign grouping letters
        """
        # Balanced-design assumption (documented)
        r = self.means["Replications"].mean()

        # t critical
        t_crit = t.ppf(1 - self.alpha / 2, self.error_df)

        # LSD value
        self.lsd_value = t_crit * np.sqrt(2 * self.error_ms / r)

        return self._group_means()

    def _group_means(self):
        """
        Assign grouping letters using full pairwise comparison
        """
        means = self.means.sort_values("Mean", ascending=False).reset_index(drop=True)

        groups = ["a"]

        for i in range(1, len(means)):
            letter = "a"
            for j in range(i):
                diff = abs(means.loc[j, "Mean"] - means.loc[i, "Mean"])
                if diff > self.lsd_value:
                    letter = chr(ord(letter) + 1)
            groups.append(letter)

        means["Group"] = groups
        self.grouped_means = means
        return means
