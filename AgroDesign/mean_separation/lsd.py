import pandas as pd
import numpy as np
from scipy.stats import t


class LSD:
    """
    Least Significant Difference (LSD) test
    (design-aware: CRD, RCBD, factorial, split, split–split)
    """

    def __init__(self, anova, effect=None, alpha=0.05):
        """
        Parameters
        ----------
        anova : Anova object
            Fitted ANOVA model with means already computed
        effect : str, optional
            Effect being compared ("A", "B", "C", "A:B", etc.).
            Required for split / split–split designs.
        alpha : float
            Significance level
        """
        if not hasattr(anova, "means_table"):
            raise RuntimeError("Run means() or factorial_means() before LSD test")

        self.anova = anova
        self.alpha = alpha
        self.effect = effect
        self.means = anova.means_table.copy()

        # Identify grouping columns (all except Mean, Replications)
        self.group_cols = [
            c for c in self.means.columns
            if c not in ("Mean", "Replications")
        ]

        # Select correct error term
        self.error_df, self.error_ms = self._select_error_term()

    # ------------------------------------------------------------------
    # Error-term selection (core statistical fix)
    # ------------------------------------------------------------------
    def _select_error_term(self):
        """
        Select correct error DF and MS based on design hierarchy
        """
        # CRD / RCBD / simple factorial
        if not hasattr(self.anova, "error_terms"):
            return self.anova.error_df, self.anova.error_ms

        et = self.anova.error_terms

        # If effect not specified, fall back safely
        if self.effect is None:
            return et.get("residual", (self.anova.error_df, self.anova.error_ms))

        # ---- Main effects ----
        if ":" not in self.effect:
            if self.effect == "A":
                return et.get("whole_plot", et["residual"])
            if self.effect == "B":
                return et.get("sub_plot", et["residual"])
            return et["residual"]  # C or lower-level factor

        # ---- Two-way interactions ----
        if self.effect.count(":") == 1:
            if "B" in self.effect:
                return et.get("sub_plot", et["residual"])
            return et["residual"]

        # ---- Three-way or higher ----
        return et["residual"]

    # ------------------------------------------------------------------
    # LSD test
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Grouping letters
    # ------------------------------------------------------------------
    def _group_means(self):
        """
        Assign grouping letters using full pairwise LSD comparison
        """
        means = (
            self.means
            .sort_values("Mean", ascending=False)
            .reset_index(drop=True)
        )

        groups = ["a"]

        for i in range(1, len(means)):
            current_letter = "a"
            for j in range(i):
                diff = abs(means.loc[j, "Mean"] - means.loc[i, "Mean"])
                if diff > self.lsd_value:
                    current_letter = chr(ord(current_letter) + 1)
            groups.append(current_letter)

        means["Group"] = groups
        self.grouped_means = means
        return means
