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
    def factorial(self, factors, block=None):
        """
        General factorial ANOVA (CRD or RCBD)

        Parameters
        ----------
        factors : list or tuple of str
            Factor names, e.g. ["A", "B"] or ["A", "B", "C"]
        block : str, optional
            Block factor for RCBD
        """
        if not isinstance(factors, (list, tuple)) or len(factors) < 1:
            raise ValueError("factors must be a list or tuple of factor names")

        # Validate columns
        for f in factors:
            if f not in self.data.columns:
                raise ValueError(f"Factor '{f}' not found in data")

        if block and block not in self.data.columns:
            raise ValueError(f"Block '{block}' not found in data")

        # Build factorial term: C(A) * C(B) * C(C)
        factorial_term = " * ".join([f"C({f})" for f in factors])

        if block:
            formula = f"{self.response} ~ {factorial_term} + C({block})"
        else:
            formula = f"{self.response} ~ {factorial_term}"

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
    
    def factorial_means(self, factors):
        """
        Compute means for main effects or interactions

        Parameters
        ----------
        factors : str or list/tuple of str
            "A" → main effect
            ["A","B"] → A×B
            ["A","B","C"] → A×B×C
        """
        if self.model is None:
            raise RuntimeError("Run factorial ANOVA before computing means")

        if isinstance(factors, str):
            factors = [factors]

        for f in factors:
            if f not in self.data.columns:
                raise ValueError(f"Factor '{f}' not found in data")

        means = (
            self.data
            .groupby(factors)[self.response]
            .agg(Mean="mean", Replications="count")
            .reset_index()
        )

        self.means_table = means
        return means
    
    def split_plot(self, whole_plot, sub_plot, block, sub_sub_plot=None):
        """
        Split-Plot and Split–Split Plot ANOVA (balanced designs)
        """

        factors = [block, whole_plot, sub_plot]
        if sub_sub_plot:
            factors.append(sub_sub_plot)

        safe_data, mapping = self._make_safe_columns(factors)

        R = mapping[block]
        A = mapping[whole_plot]
        B = mapping[sub_plot]

        terms = [
            f"C({R})",
            f"C({A})",
            f"C({R}):C({A})",
            f"C({B})",
            f"C({A}):C({B})"
        ]

        if sub_sub_plot:
            C_ = mapping[sub_sub_plot]
            terms += [
                f"C({R}):C({A}):C({B})",
                f"C({C_})",
                f"C({A}):C({C_})",
                f"C({B}):C({C_})",
                f"C({A}):C({B}):C({C_})"
            ]

        formula = f"{self.response} ~ " + " + ".join(terms)

        self.model = ols(formula, data=safe_data).fit()
        self.anova_table = sm.stats.anova_lm(self.model, typ=1)

        table = self._format_splitplot_anova(
            whole_plot=A,
            sub_plot=B,
            block=R,
            sub_sub_plot=mapping[sub_sub_plot] if sub_sub_plot else None
        )

        return self._restore_index(table, mapping)


 
    def _format_splitplot_anova(self, whole_plot, sub_plot, block, sub_sub_plot=None):
        """
        Format ANOVA table for Split-Plot and Split–Split Plot designs
        using correct error strata (Type-I SS).
        """
        from scipy.stats import f

        table = self.anova_table.copy()

        table = table.rename(columns={
            "sum_sq": "SS",
            "df": "DF",
            "F": "F",
            "PR(>F)": "p-value"
        })

        table["MS"] = table["SS"] / table["DF"]

        # --- WHOLE-PLOT ERROR ---
        wp_error = f"C({block}):C({whole_plot})"
        wp_factor = f"C({whole_plot})"

        if wp_error not in table.index:
            raise RuntimeError(
                f"Whole-plot error term '{wp_error}' not found in ANOVA table.\n"
                f"Available terms: {list(table.index)}"
            )

        # Correct F-test for whole-plot factor
        table.loc[wp_factor, "F"] = (
            table.loc[wp_factor, "MS"] / table.loc[wp_error, "MS"]
        )

        df1 = table.loc[wp_factor, "DF"]
        df2 = table.loc[wp_error, "DF"]

        table.loc[wp_factor, "p-value"] = 1 - f.cdf(
            table.loc[wp_factor, "F"], df1, df2
        )

        # --- SPLIT–SPLIT PLOT ---
        if sub_sub_plot:
            sp_error = f"C({block}):C({whole_plot}):C({sub_plot})"

            if sp_error not in table.index:
                raise RuntimeError(
                    f"Sub-plot error term '{sp_error}' not found in ANOVA table.\n"
                    f"Available terms: {list(table.index)}"
                )

            # Correct F-tests for B and A×B
            for term in [
                f"C({sub_plot})",
                f"C({whole_plot}):C({sub_plot})"
            ]:
                table.loc[term, "F"] = (
                    table.loc[term, "MS"] / table.loc[sp_error, "MS"]
                )

                df1 = table.loc[term, "DF"]
                df2 = table.loc[sp_error, "DF"]

                table.loc[term, "p-value"] = 1 - f.cdf(
                    table.loc[term, "F"], df1, df2
                )

            # Store correct residual error for mean separation
            if "Residual" in table.index:
                self.error_df = table.loc["Residual", "DF"]
                self.error_ms = table.loc["Residual", "MS"]

        else:
            # Classical split-plot
            if "Residual" in table.index:
                self.error_df = table.loc["Residual", "DF"]
                self.error_ms = table.loc["Residual", "MS"]

        return table[["DF", "SS", "MS", "F", "p-value"]]

    
    def _make_safe_columns(self, cols):
        """
        Create a safe internal copy of data with renamed columns
        to avoid Patsy keyword conflicts (C, I, Q, etc.)
        """
        mapping = {col: f"_F{i}" for i, col in enumerate(cols)}
        safe_data = self.data.rename(columns=mapping)
        return safe_data, mapping


    def _restore_index(self, table, mapping):
        """
        Restore original factor names in ANOVA table index
        """
        inv = {v: k for k, v in mapping.items()}

        new_index = []
        for idx in table.index:
            for safe, orig in inv.items():
                idx = idx.replace(safe, orig)
            new_index.append(idx)

        table.index = new_index
        return table

    def _cat(self, name):
        """
        Safely wrap categorical variables for Patsy formulas
        using backtick quoting (robust in notebooks)
        """
        return f'C(`{name}`)'


