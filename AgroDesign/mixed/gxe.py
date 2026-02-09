import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.formula.api import ols
from agrodesign.mixed.ammi import AMMI


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

        # Format the table to match the expected structure
        table = table.rename(columns={
            "sum_sq": "SS",
            "df": "DF",
            "F": "F",
            "PR(>F)": "p-value"
        })

        table["MS"] = table["SS"] / table["DF"]

        return table[["DF", "SS", "MS", "F", "p-value"]]

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

        # Fit AMMI for stability
        self.ammi = AMMI(self.data, self.genotype, self.environment, self.response)
        self.ammi.fit()

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
    # Stability (AMMI ASV)
    # --------------------------------------------------
    def stability(self):
        if self.ammi is None:
            raise RuntimeError("Fit the model first with .fit()")
        return self.ammi.stability()

    # --------------------------------------------------
    # Mega-environments
    # --------------------------------------------------
    def mega_environments(self):
        """
        Identify the best genotype for each environment
        """
        if self.ammi is None:
            raise RuntimeError("Fit the model first with .fit()")

        # Get mean performance per genotype per environment
        env_means = self.data.groupby([self.genotype, self.environment])[self.response].mean().unstack()

        # For each environment, find the genotype with highest mean
        winners = {}
        for env in env_means.columns:
            best_geno = env_means[env].idxmax()
            winners[env] = best_geno

        return winners

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
