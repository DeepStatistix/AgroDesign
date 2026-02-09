import pandas as pd
import numpy as np
import statsmodels.formula.api as smf


class MixedModel:
    """
    Linear Mixed Model engine for agricultural and biological experiments
    Uses statsmodels MixedLM internally but provides structured API
    """

    def __init__(self, data, response):
        self.data = data.copy()
        self.response = response
        self.model = None
        self.result = None
        self.random_terms = []
        self.fixed_terms = []

    # ------------------------------------------------------------
    # Utility: build interaction column safely
    # ------------------------------------------------------------
    def _interaction_column(self, term):
        """Create interaction column like A:B internally"""
        if ":" not in term:
            return term

        cols = term.split(":")
        new_col = "_INT_" + "_".join(cols)

        if new_col not in self.data.columns:
            self.data[new_col] = self.data[cols].astype(str).agg(":".join, axis=1)

        return new_col

    # ------------------------------------------------------------
    # Fit model
    # ------------------------------------------------------------
    def fit(self, fixed, random):
        """
        Fit Linear Mixed Model

        Parameters
        ----------
        fixed : list
            Fixed effects (e.g. ["Treatment"])
        random : list
            Random grouping factor (e.g. ["Block"])
        """

        import statsmodels.formula.api as smf

        if not isinstance(fixed, (list, tuple)):
            raise ValueError("fixed must be a list")

        if not isinstance(random, (list, tuple)) or len(random) == 0:
            raise ValueError("random must be a non-empty list")

        # Only one grouping factor for now
        group = random[0]
        self.group_name = group  # ⭐ needed for summary()

        # Build formula
        fixed_terms = " + ".join([f"C({f})" for f in fixed])
        formula = f"{self.response} ~ {fixed_terms}"

        # Fit model
        self.model = smf.mixedlm(
            formula,
            data=self.data,
            groups=self.data[group]
        )

        self.result = self.model.fit(reml=True)

        return self


    # ------------------------------------------------------------
    # Summary (variance components)
    # ------------------------------------------------------------
    def summary(self):
        """
        Return variance component table (agricultural style)
        """

        import pandas as pd
        import numpy as np

        rows = []

        # 1️⃣ Random group variance (e.g. Block)
        if self.result.cov_re is not None:
            var_group = float(self.result.cov_re.iloc[0, 0])
            rows.append([
                self.group_name,
                "Random (Group)",
                var_group,
                np.sqrt(var_group)
            ])

        # 2️⃣ Additional variance components (if present)
        if getattr(self.result, "vcomp", None) is not None:
            v = self.result.vcomp

            # case: ndarray
            if isinstance(v, (list, tuple, np.ndarray)):
                for i, val in enumerate(v):
                    rows.append([
                        f"VC{i+1}",
                        "Random",
                        float(val),
                        np.sqrt(float(val))
                    ])

            # case: dict (future safe)
            elif hasattr(v, "items"):
                for name, val in v.items():
                    rows.append([
                        name,
                        "Random",
                        float(val),
                        np.sqrt(float(val))
                    ])

        # 3️⃣ Residual variance
        rows.append([
            "Residual",
            "Error",
            float(self.result.scale),
            np.sqrt(float(self.result.scale))
        ])

        table = pd.DataFrame(
            rows,
            columns=["Effect", "Type", "Variance", "Std.Dev"]
        )

        return table


    # ------------------------------------------------------------
    # BLUP extraction for random effects
    # ------------------------------------------------------------
    def blup(self, effect):
        """
        Return BLUPs for random effect

        effect can be:
            "Block"
            ["Block"]
        """

        # -------------------------------
        # Normalize input
        # -------------------------------
        if isinstance(effect, (list, tuple)):
            effect = effect[0]

        if not hasattr(self, "result"):
            raise RuntimeError("Fit model first")

        re = self.result.random_effects

        values = []
        for level, val in re.items():

            # val may be array / series
            if hasattr(val, "values"):
                v = float(val.values[0])
            elif isinstance(val, (list, tuple, np.ndarray)):
                v = float(val[0])
            else:
                v = float(val)

            values.append([level, v])

        df = pd.DataFrame(values, columns=[effect, "BLUP"])

        # Sorting safe now
        df = df.sort_values("BLUP", ascending=False).reset_index(drop=True)

        return df

    # ------------------------------------------------------------
    # Fixed effect estimates (called BLUPs in context)
    # ------------------------------------------------------------
    def fixed_blup(self, fixed):
        """
        Return fixed effect estimates (BLUPs for fixed effects)

        fixed: list of fixed effects, e.g. ["Treatment"]
        """
        if not hasattr(self, "result"):
            raise RuntimeError("Fit model first")

        effect = fixed[0]
        levels = sorted(self.data[effect].unique())
        intercept = self.result.params['Intercept']

        blups = {}
        for level in levels:
            if level == levels[0]:  # reference level
                blups[level] = intercept
            else:
                param_name = f"C({effect})[T.{level}]"
                if param_name in self.result.params:
                    blups[level] = intercept + self.result.params[param_name]
                else:
                    blups[level] = intercept

        df = pd.DataFrame(list(blups.items()), columns=[effect, "BLUP"])
        df = df.sort_values("BLUP", ascending=False).reset_index(drop=True)

        return df


    # ------------------------------------------------------------
    # Heritability
    # ------------------------------------------------------------
    def heritability(self, genotype, replications):
        """
        Broad-sense heritability
        H² = σg² / (σg² + σe² / r)
        """

        if self.result is None:
            raise RuntimeError("Model not fitted")

        var_g = self.result.cov_re.iloc[0, 0]
        var_e = self.result.scale

        r = self.data[replications].nunique()

        H2 = var_g / (var_g + var_e / r)

        return float(H2)
