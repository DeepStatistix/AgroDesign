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
            Fitted ANOVA model
        alpha : float
            Significance level
        """
        if not hasattr(anova, "means_table"):
            raise RuntimeError("Run means() before LSD test")

        self.anova = anova
        self.alpha = alpha

        self.means = anova.means_table.copy()
        self.error_ms = anova.error_ms
        self.error_df = anova.error_df

    def test(self):
        """
        Perform LSD test
        """
        # Average replications
        r = self.means["Replications"].mean()

        # t critical
        t_crit = t.ppf(1 - self.alpha / 2, self.error_df)

        # LSD value
        lsd = t_crit * np.sqrt(2 * self.error_ms / r)

        self.lsd_value = lsd

        # Pairwise comparisons
        comparisons = []

        for i in range(len(self.means)):
            for j in range(i + 1, len(self.means)):
                m1 = self.means.loc[i, "Mean"]
                m2 = self.means.loc[j, "Mean"]

                diff = abs(m1 - m2)
                sig = "Yes" if diff > lsd else "No"

                comparisons.append({
                    "Treatment 1": self.means.loc[i, self.means.columns[0]],
                    "Treatment 2": self.means.loc[j, self.means.columns[0]],
                    "Mean Diff": diff,
                    "Significant": sig
                })

        self.comparisons = pd.DataFrame(comparisons)

        return self._group_means()

    def _group_means(self):
        """
        Assign grouping letters (a, b, c...)
        """
        means = self.means.sort_values("Mean", ascending=False).reset_index(drop=True)
        groups = []
        current_group = "a"

        for i in range(len(means)):
            if i == 0:
                groups.append(current_group)
            else:
                diff = abs(means.loc[i - 1, "Mean"] - means.loc[i, "Mean"])
                if diff <= self.lsd_value:
                    groups.append(current_group)
                else:
                    current_group = chr(ord(current_group) + 1)
                    groups.append(current_group)

        means["Group"] = groups
        self.grouped_means = means

        return means
