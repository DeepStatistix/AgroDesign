import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols


class Anova:
    """
    Generic ANOVA engine for agricultural designs
    """

    def __init__(self, data, response):
        """
        Parameters
        ----------
        data : pandas.DataFrame
            Experimental data
        response : str
            Name of response variable
        """
        self.data = data.copy()
        self.response = response
        self.model = None
        self.anova_table = None

    def crd(self, treatment):
        """
        ANOVA for Completely Randomized Design (CRD)

        Model: Y ~ Treatment
        """
        formula = f"{self.response} ~ C({treatment})"
        self.model = ols(formula, data=self.data).fit()
        self.anova_table = sm.stats.anova_lm(self.model, typ=2)

        return self._format_anova()

    def rcbd(self, treatment, block):
        """
        ANOVA for Randomized Complete Block Design (RCBD)

        Model: Y ~ Treatment + Block
        """
        formula = f"{self.response} ~ C({treatment}) + C({block})"
        self.model = ols(formula, data=self.data).fit()
        self.anova_table = sm.stats.anova_lm(self.model, typ=2)

        return self._format_anova()
    def means(self, treatment):
        """
        Compute treatment means and number of replications
        """
        if treatment not in self.data.columns:
            raise ValueError(f"{treatment} not found in data")

        means_df = (
            self.data
            .groupby(treatment)[self.response]
            .agg(
                Mean="mean",
                Replications="count"
            )
            .reset_index()
        )

        self.means_table = means_df
        return means_df
    def factorial(self, factor_a, factor_b, block=None):
        """
        ANOVA for Factorial experiment (with or without blocks)

        Model without blocks: Y ~ A * B
        Model with blocks:    Y ~ A * B + Block
        """
        if block:
            formula = (
                f"{self.response} ~ C({factor_a}) * C({factor_b}) "
                f"+ C({block})"
            )
        else:
            formula = f"{self.response} ~ C({factor_a}) * C({factor_b})"

        self.model = ols(formula, data=self.data).fit()
        self.anova_table = sm.stats.anova_lm(self.model, typ=2)

        return self._format_anova()

    def _format_anova(self):
        """
        Clean and format ANOVA table (agricultural style)
        """
        table = self.anova_table.copy()
        table = table.rename(columns={
            "sum_sq": "SS",
            "df": "DF",
            "F": "F",
            "PR(>F)": "p-value"
        })

        table["MS"] = table["SS"] / table["DF"]

        cols = ["DF", "SS", "MS", "F", "p-value"]
        # Store error terms for mean separation
        if "Residual" in table.index:
            self.error_df = table.loc["Residual", "DF"]
            self.error_ms = table.loc["Residual", "MS"]

        return table[cols]