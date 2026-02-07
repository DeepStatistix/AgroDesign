import pandas as pd
import numpy as np
from statsmodels.stats.libqsturng import qsturng
from agrodesign.utils.cld import compact_letter_display


class DMRT:
    """
    Duncan Multiple Range Test (design-aware, CLD compatible)
    """

    def __init__(self, anova, effect=None, alpha=0.05):
        """
        Parameters
        ----------
        anova : Anova object
            Fitted ANOVA model with means computed
        effect : str
            "A", "B", "A:B", etc (needed for split-plot error selection)
        alpha : float
        """
        if not hasattr(anova, "means_table"):
            raise RuntimeError("Run means() or factorial_means() before DMRT")

        self.anova = anova
        self.alpha = alpha
        self.effect = effect
        self.means = anova.means_table.copy()

        self.group_cols = [
            c for c in self.means.columns
            if c not in ("Mean", "Replications")
        ]

        self.error_df, self.error_ms = self._select_error_term()

    # --------------------------------------------------
    # Select correct error term (same logic as LSD)
    # --------------------------------------------------
    def _select_error_term(self):

        if not hasattr(self.anova, "error_terms"):
            return self.anova.error_df, self.anova.error_ms

        et = self.anova.error_terms

        if self.effect is None:
            return et.get("residual", (self.anova.error_df, self.anova.error_ms))

        if ":" not in self.effect:
            if self.effect == "A":
                return et.get("whole_plot", et["residual"])
            if self.effect == "B":
                return et.get("sub_plot", et["residual"])
            return et["residual"]

        if self.effect.count(":") == 1:
            if "B" in self.effect:
                return et.get("sub_plot", et["residual"])
            return et["residual"]

        return et["residual"]

    # --------------------------------------------------
    # Test
    # --------------------------------------------------
    def test(self):

        means = (
            self.means
            .sort_values("Mean", ascending=False)
            .reset_index(drop=True)
        )

        k = len(means)
        r = means["Replications"].mean()
        se = np.sqrt(self.error_ms / r)

        # treatment labels (supports interactions automatically)
        labels = means[self.group_cols].astype(str).agg(":".join, axis=1)

        # Precompute LSR values
        lsr = {}
        for p in range(2, k + 1):
            q = qsturng(1 - self.alpha, p, self.error_df)
            lsr[p] = q * se

        # --- significance matrix (LABELED) ---
        sig = pd.DataFrame(False, index=labels, columns=labels)

        for i in range(k):
            for j in range(i + 1, k):
                r_range = abs(i - j) + 1
                diff = abs(means.loc[i, "Mean"] - means.loc[j, "Mean"])

                if diff > lsr[r_range]:
                    sig.iloc[i, j] = True
                    sig.iloc[j, i] = True

        # Compact Letter Display
        letters = compact_letter_display(sig)

        means["Group"] = labels.map(letters)
        self.grouped_means = means
        return means
