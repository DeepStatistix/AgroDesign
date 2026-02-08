import pandas as pd
import numpy as np
from scipy.stats import t
from agrodesign.utils.cld import compact_letter_display

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
    
    def critical_value(self):
        return self.lsd_value

    # ------------------------------------------------------------------
    # Grouping letters
    # ------------------------------------------------------------------
    def _group_means(self):
        """
        Compact Letter Display (CLD) grouping using LSD pairwise comparisons
        """

        # sort by descending mean
        means_df = (
            self.means
            .sort_values("Mean", ascending=False)
            .reset_index(drop=True)
        )

        # create treatment labels (supports interactions automatically)
        labels = means_df[self.group_cols].astype(str).agg(":".join, axis=1)

        means_series = pd.Series(means_df["Mean"].values, index=labels)

        treatments = list(means_series.index)
        n = len(treatments)

        # build significance matrix
        sig_matrix = pd.DataFrame(False, index=treatments, columns=treatments)

        for i in range(n):
            for j in range(n):
                if i == j:
                    continue

                diff = abs(means_series.iloc[i] - means_series.iloc[j])

                if diff > self.lsd_value:
                    sig_matrix.iloc[i, j] = True

        # generate compact letter display
        letters = compact_letter_display(means_series, sig_matrix)

        means_df["Group"] = labels.map(letters)
        self.grouped_means = means_df

        return means_df
