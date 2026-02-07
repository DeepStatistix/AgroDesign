import pandas as pd
import numpy as np
import statsmodels.formula.api as smf


class GxEModel:
    """
    Genotype × Environment mixed model (MET analysis)

    Model:
    Y = μ + Environment(fixed) + Genotype(random) +
        Genotype×Environment(random) + Block(Environment) + error
    """

    def __init__(self, data, response):
        self.data = data.copy()
        self.response = response
        self.result = None

    # --------------------------------------------------
    # Fit model
    # --------------------------------------------------
    def fit(self, genotype, environment, block):

        df = self.data.copy()

        # nested block within environment
        df["_env_block"] = df[environment].astype(str) + ":" + df[block].astype(str)

        formula = f"{self.response} ~ C({environment})"

        vc = {
            "Genotype": f"0 + C({genotype})",
            "GxE": f"0 + C({genotype}):C({environment})"
        }

        self.model = smf.mixedlm(
            formula=formula,
            data=df,
            groups=df["_env_block"],
            vc_formula=vc,
            re_formula="1"
        )

        self.result = self.model.fit(reml=True)

        self.genotype = genotype
        self.environment = environment
        self.block = block

        return self.result

    # --------------------------------------------------
    # Variance components
    # --------------------------------------------------
    def var_components(self):

        # 1️⃣ Residual
        residual = float(self.result.scale)

        # 2️⃣ Block(Environment) variance (group random effect)
        if self.result.cov_re is not None:
            block_var = float(self.result.cov_re.iloc[0, 0])
        else:
            block_var = 0.0

        # 3️⃣ Additional variance components (Genotype & G×E)
        vc_dict = {}

        try:
            names = self.model.exog_vc.names
            values = self.result.vcomp
            vc_dict = dict(zip(names, values))
        except Exception:
            # fallback for older statsmodels
            if hasattr(self.result, "vcomp"):
                for i, v in enumerate(self.result.vcomp):
                    vc_dict[f"VC{i+1}"] = float(v)

        return {
            "Block(Environment)": block_var,
            "Genotype": vc_dict.get("Genotype", 0.0),
            "GxE": vc_dict.get("GxE", 0.0),
            "Residual": residual
        }

    # --------------------------------------------------
    # BLUPs
    # --------------------------------------------------
    def blup_genotypes(self):

        re = self.result.random_effects

        rows = []
        for k, v in re.items():
            rows.append([k, list(v.values())[0]])

        return pd.DataFrame(rows, columns=["EnvBlock", "BLUP"])

    # --------------------------------------------------
    # Broad sense heritability across environments
    # --------------------------------------------------
    def heritability(self):

        vc = self.var_components()

        sigma_g = vc["Genotype"]
        sigma_ge = vc["GxE"]
        sigma_e = vc["Residual"]

        e = self.data[self.environment].nunique()
        r = self.data[self.block].nunique()

        H2 = sigma_g / (sigma_g + sigma_ge/e + sigma_e/(e*r))
        return H2

    # --------------------------------------------------
    # Stability index
    # --------------------------------------------------
    def stability(self):

        vc = self.var_components()
        return vc["GxE"]

    # --------------------------------------------------
    # Summary table
    # --------------------------------------------------
    def summary(self):

        vc = self.var_components()

        return pd.DataFrame({
            "Component": vc.keys(),
            "Variance": vc.values()
        })
