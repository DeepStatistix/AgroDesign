import numpy as np
import pandas as pd
from statsmodels.stats.libqsturng import qsturng
from agrodesign.utils.cld import compact_letter_display


class TukeyHSD:
    """
    Tukey Honest Significant Difference (HSD) test
    (CRD, RCBD, factorial, split-plot, split–split aware)
    """

    def __init__(self, anova, effect=None, alpha=0.05):
        """
        Tukey Honest Significant Difference (design-aware)
        """

        self.anova = anova
        self.alpha = alpha
        self.effect = effect

        # -------------------------------------------------
        # AUTO-COMPUTE MEANS IF USER DIDN'T
        # -------------------------------------------------
        if not hasattr(anova, "means_table"):

            if effect is None:
                raise RuntimeError(
                    "Effect must be provided when means are not precomputed"
                )

            if isinstance(effect, str):
                factors = effect.split(":")
            else:
                factors = list(effect)

            anova.factorial_means(factors)

        # copy means
        self.means = anova.means_table.copy()

        # -------------------------------------------------
        # Detect grouping columns
        # -------------------------------------------------
        self.group_cols = [
            c for c in self.means.columns
            if c not in ("Mean", "Replications")
        ]

        # -------------------------------------------------
        # Select correct error term (CRITICAL FIX)
        # -------------------------------------------------
        self.error_df, self.error_ms = self._select_error_term()

    # ==================================================
    # Error-term selection (design-aware, safe fallback)
    # ==================================================
    def _select_error_term(self):

        if not hasattr(self.anova, "error_terms"):
            return self.anova.error_df, self.anova.error_ms

        et = self.anova.error_terms

        if self.effect is None:
            return et.get("residual", (self.anova.error_df, self.anova.error_ms))

        # main effects
        if ":" not in self.effect:
            if self.effect == "A":
                return et.get("whole_plot", et["residual"])
            if self.effect == "B":
                return et.get("sub_plot", et["residual"])
            return et["residual"]

        # interactions
        if self.effect.count(":") == 1:
            if "B" in self.effect:
                return et.get("sub_plot", et["residual"])
            return et["residual"]

        return et["residual"]

    # ==================================================
    # Tukey HSD test
    # ==================================================
    def test(self):
        """
        Perform Tukey HSD and assign grouping letters
        """
        means = (
            self.means
            .sort_values("Mean", ascending=False)
            .reset_index(drop=True)
        )

        k = len(means)
        r = means["Replications"].mean()

        # Studentized range critical value
        q_crit = qsturng(1 - self.alpha, k, self.error_df)

        # HSD value
        self.hsd_value = q_crit * np.sqrt(self.error_ms / r)

        return self._group_means(means)

    # ==================================================
    # Grouping logic
    # ==================================================
    def _group_means(self, means_df):
        """
        Compact Letter Display (CLD) grouping using Tukey HSD comparisons
        """

        # create treatment labels (supports interactions automatically)
        labels = means_df[self.group_cols].astype(str).agg(":".join, axis=1)

        means_series = pd.Series(means_df["Mean"].values, index=labels)

        treatments = list(means_series.index)
        n = len(treatments)

        # build significance matrix using Tukey HSD
        sig_matrix = pd.DataFrame(False, index=treatments, columns=treatments)

        for i in range(n):
            for j in range(n):
                if i == j:
                    continue

                diff = abs(means_series.iloc[i] - means_series.iloc[j])

                if diff > self.hsd_value:
                    sig_matrix.iloc[i, j] = True

        # generate compact letter display
        letters = compact_letter_display(means_series, sig_matrix)

        means_df["Group"] = labels.map(letters)
        self.grouped_means = means_df

        return means_df

