import pandas as pd
import numpy as np
from numpy.linalg import svd
from scipy.stats import f

class AMMI:
    """
    AMMI (Additive Main Effects and Multiplicative Interaction)

    Performs:
    ANOVA decomposition + PCA of interaction matrix
    """

    def __init__(self, data, genotype, environment, response):
        self.data = data.copy()
        self.g = genotype
        self.e = environment
        self.y = response

    # --------------------------------------------------
    # Fit AMMI
    # --------------------------------------------------
    def fit(self):

        # Step 1: Mean table (G×E)
        table = self.data.pivot_table(
            values=self.y,
            index=self.g,
            columns=self.e,
            aggfunc="mean"
        )

        self.means = table

        # Step 2: Remove additive effects
        grand_mean = table.values.mean()
        g_means = table.mean(axis=1)
        e_means = table.mean(axis=0)

        interaction = table.copy()

        for i in table.index:
            for j in table.columns:
                interaction.loc[i, j] = (
                    table.loc[i, j]
                    - g_means[i]
                    - e_means[j]
                    + grand_mean
                )

        self.interaction = interaction

        # Step 3: SVD
        U, S, VT = svd(interaction.values, full_matrices=False)

        self.U = U
        self.S = S
        self.VT = VT

        # IPCA scores
        self.genotype_scores = pd.DataFrame(
            U * np.sqrt(S),
            index=table.index,
            columns=[f"IPCA{i+1}" for i in range(len(S))]
        )

        self.environment_scores = pd.DataFrame(
            (VT.T * np.sqrt(S)),
            index=table.columns,
            columns=[f"IPCA{i+1}" for i in range(len(S))]
        )

        return self

    # --------------------------------------------------
    # AMMI ANOVA table
    # --------------------------------------------------

    def anova(self):

        # --- basic counts ---
        g = self.means.shape[0]
        e = self.means.shape[1]

        # replications (important!)
        r = (
            self.data
            .groupby([self.g, self.e])[self.y]
            .count()
            .mean()
        )

        Y = self.means.values
        grand = Y.mean()

        # --- Total SS ---
        SS_total = ((Y - grand)**2).sum()

        # --- Genotype SS ---
        g_means = Y.mean(axis=1, keepdims=True)
        SS_g = ((g_means - grand)**2).sum() * e

        # --- Environment SS ---
        e_means = Y.mean(axis=0, keepdims=True)
        SS_e = ((e_means - grand)**2).sum() * g

        # --- Interaction SS ---
        SS_ge = SS_total - SS_g - SS_e

        # --- Degrees of freedom ---
        df_g = g - 1
        df_e = e - 1
        df_ge = (g - 1) * (e - 1)
        df_res = g * e * (r - 1)

        # --- Residual MS ---
        # estimated from original dataset
        residual = (
            self.data
            .groupby([self.g, self.e])[self.y]
            .var()
            .mean()
        )

        MS_res = residual

        rows = []

        # -----------------------
        # Genotype
        # -----------------------
        MS_g = SS_g / df_g
        F_g = MS_g / MS_res
        p_g = 1 - f.cdf(F_g, df_g, df_res)

        rows.append(["Genotype", df_g, SS_g, MS_g, F_g, p_g])

        # -----------------------
        # Environment
        # -----------------------
        MS_e = SS_e / df_e
        F_e = MS_e / MS_res
        p_e = 1 - f.cdf(F_e, df_e, df_res)

        rows.append(["Environment", df_e, SS_e, MS_e, F_e, p_e])

        # -----------------------
        # GE interaction
        # -----------------------
        MS_ge = SS_ge / df_ge
        F_ge = MS_ge / MS_res
        p_ge = 1 - f.cdf(F_ge, df_ge, df_res)

        rows.append(["G×E", df_ge, SS_ge, MS_ge, F_ge, p_ge])

        # -----------------------
        # IPCA components (Gollob test)
        # -----------------------
        remaining_df = df_ge
        remaining_ss = SS_ge

        for k, ss in enumerate(self.S**2, start=1):

            df_ipca = g + e - 1 - 2*k
            if df_ipca <= 0:
                break

            MS_ipca = ss / df_ipca
            F_ipca = MS_ipca / MS_res
            p_ipca = 1 - f.cdf(F_ipca, df_ipca, df_res)

            rows.append([f"IPCA{k}", df_ipca, ss, MS_ipca, F_ipca, p_ipca])

            remaining_df -= df_ipca
            remaining_ss -= ss

        # -----------------------
        # Residual (AMMI)
        # -----------------------
        if remaining_df > 0:
            MS_ammi_res = remaining_ss / remaining_df
            rows.append(["Residual", remaining_df, remaining_ss, MS_ammi_res, None, None])

        table = pd.DataFrame(
            rows,
            columns=["Source", "DF", "SS", "MS", "F", "p-value"]
        )

        return table


    # --------------------------------------------------
    # AMMI Stability Value (ASV)
    # --------------------------------------------------
    def stability(self):

        ipca1 = self.genotype_scores["IPCA1"]
        ipca2 = self.genotype_scores["IPCA2"]

        w = self.S[0] / self.S[1]

        asv = np.sqrt((w * ipca1)**2 + ipca2**2)

        return pd.DataFrame({
            "Genotype": self.genotype_scores.index,
            "ASV": asv
        }).sort_values("ASV")

    # --------------------------------------------------
    # Genotype ranking (mean + stability)
    # --------------------------------------------------
    def ranking(self):

        means = self.means.mean(axis=1)
        stab = self.stability().set_index("Genotype")

        rank = pd.DataFrame({
            "MeanYield": means,
            "Stability": stab["ASV"]
        })

        rank["Rank"] = (
            rank["MeanYield"].rank(ascending=False)
            + rank["Stability"].rank()
        )

        return rank.sort_values("Rank")
