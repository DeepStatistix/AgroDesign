import numpy as np
import pandas as pd
from statsmodels.stats.libqsturng import qsturng


class TukeyHSD:
    """
    Tukey Honest Significant Difference (HSD) test
    (CRD, RCBD, factorial, split-plot, split–split aware)
    """

    def __init__(self, anova, effect, alpha=0.05):
        """
        Parameters
        ----------
        anova : Anova object
            Fitted ANOVA model
        effect : str or list/tuple
            "A", ["A","B"], "A:B", ["A","B","C"]
        alpha : float
            Significance level
        """
        if anova.model is None:
            raise RuntimeError("Run ANOVA before Tukey HSD")

        self.anova = anova
        self.alpha = alpha

        # --------------------------------------------------
        # Normalize effect
        # --------------------------------------------------
        if isinstance(effect, str):
            if ":" in effect:
                self.factors = effect.split(":")
            else:
                self.factors = [effect]
        elif isinstance(effect, (list, tuple)):
            self.factors = list(effect)
        else:
            raise ValueError("effect must be str or list/tuple")

        self.effect = ":".join(self.factors)

        # --------------------------------------------------
        # AUTO-COMPUTE MEANS (KEY FIX)
        # --------------------------------------------------
        anova.factorial_means(self.factors)
        self.means = anova.means_table.copy()

        # --------------------------------------------------
        # Select correct error term
        # --------------------------------------------------
        self.error_df, self.error_ms = self._select_error_term()

    # ==================================================
    # Error-term selection (design-aware, safe fallback)
    # ==================================================
    def _select_error_term(self):
        """
        Select appropriate error DF and MS
        """
        # Default: residual
        df = self.anova.error_df
        ms = self.anova.error_ms

        if not hasattr(self.anova, "error_terms"):
            return df, ms

        et = self.anova.error_terms

        # Main effects
        if len(self.factors) == 1:
            if self.factors[0] == "A":
                return et.get("whole_plot", (df, ms))
            if self.factors[0] == "B":
                return et.get("sub_plot", (df, ms))
            return df, ms

        # Interactions
        if len(self.factors) >= 2:
            return et.get("residual", (df, ms))

        return df, ms

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
    def _group_means(self, means):
        """
        Assign grouping letters using Tukey logic
        """
        groups = ["a"]

        for i in range(1, len(means)):
            letter = "a"
            for j in range(i):
                diff = abs(means.loc[j, "Mean"] - means.loc[i, "Mean"])
                if diff > self.hsd_value:
                    letter = chr(ord(letter) + 1)
            groups.append(letter)

        means["Group"] = groups
        self.grouped_means = means
        return means
