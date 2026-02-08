import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.formula.api import ols


class GxEModel:
    """
    Multi-Environment Trial (Genotype × Environment)
    Linear Mixed Model

    Model:
        Y = μ + E (fixed) + G (random) + GE (random) + Block(E) (random) + e
    """

    # --------------------------------------------------
    # INIT
    # --------------------------------------------------
    def __init__(self, data, response, genotype, environment, block=None):

        self.data = data.copy()

        if response not in data.columns:
            raise ValueError(f"{response} column not found")

        self.response = response
        self.genotype = genotype
        self.environment = environment
        self.block = block

        self.result = None
        self.model = None

    # --------------------------------------------------
    # Classical ANOVA (for report)
    # --------------------------------------------------
    def anova(self):

        formula = (
            f'{self.response} ~ '
            f'C({self.genotype}) + '
            f'C({self.environment}) + '
            f'C({self.genotype}):C({self.environment})'
        )

        model = ols(formula, data=self.data).fit()
        table = sm.stats.anova_lm(model, typ=2)

        return table

    # --------------------------------------------------
    # Mixed Model Fit
    # --------------------------------------------------
    def fit(self):
        """
        BLUP model:
        Environment = fixed
        Genotype = random
        """

        import statsmodels.formula.api as smf

        formula = f"{self.response} ~ C({self.environment})"

        self.model = smf.mixedlm(
            formula=formula,
            data=self.data,
            groups=self.data[self.genotype]
        )

        self.result = self.model.fit(reml=True)
        return self.result


    # --------------------------------------------------
    # Variance Components
    # --------------------------------------------------
    def var_components(self):

        sigma_g = float(self.result.cov_re.iloc[0,0])
        sigma_e = float(self.result.scale)

        return {
            "Genotype": sigma_g,
            "Residual": sigma_e
        }


    # --------------------------------------------------
    # BLUPs (Genotype performance)
    # --------------------------------------------------
    def blup(self):
        """
        Extract genotype BLUPs (robust to statsmodels versions)
        """

        re = self.result.random_effects

        rows = []

        for level, values in re.items():

            # statsmodels <0.14 → dict
            if isinstance(values, dict):
                val = float(list(values.values())[0])

            # statsmodels ≥0.14 → ndarray / Series
            else:
                val = float(values[0])

            rows.append([level, val])

        df = pd.DataFrame(rows, columns=["Genotype", "BLUP"])
        return df.sort_values("BLUP", ascending=False).reset_index(drop=True)


    # --------------------------------------------------
    # Broad Sense Heritability
    # --------------------------------------------------
    def heritability(self):

        vc = self.var_components()

        sigma_g = vc["Genotype"]
        sigma_e = vc["Residual"]

        r = self.data.groupby(
            [self.genotype, self.environment]
        ).size().mean()

        H2 = sigma_g / (sigma_g + sigma_e / r)
        return H2


    # --------------------------------------------------
    # Stability (GE variance)
    # --------------------------------------------------
    def stability(self):
        return self.var_components()["GxE"]

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------
    def summary(self):

        vc = self.var_components()

        table = pd.DataFrame({
            "Variance Component": vc.keys(),
            "Value": vc.values()
        })

        return table
