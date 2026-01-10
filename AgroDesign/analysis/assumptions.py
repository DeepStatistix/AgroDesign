import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import shapiro, levene, bartlett, probplot


class Assumptions:
    """
    Assumption checks for ANOVA models
    """

    def __init__(self, anova):
        if anova.model is None:
            raise RuntimeError("Run ANOVA before checking assumptions")

        self.anova = anova
        self.residuals = anova.model.resid
        self.fitted = anova.model.fittedvalues
        self.data = anova.data
        self.response = anova.response

    # ----------------------------
    # 1. Normality
    # ----------------------------
    def shapiro_test(self):
        """
        Shapiro–Wilk test for normality of residuals
        """
        stat, p = shapiro(self.residuals)
        return {
            "Test": "Shapiro-Wilk",
            "Statistic": stat,
            "p-value": p,
            "Normal": "Yes" if p > 0.05 else "No"
        }

    def qq_plot(self):
        """
        QQ plot of residuals
        """
        probplot(self.residuals, plot=plt)
        plt.title("QQ Plot of Residuals")
        plt.show()

    # ----------------------------
    # 2. Homogeneity of Variance
    # ----------------------------
    def levene_test(self, group):
        """
        Levene's test for homogeneity of variances
        """
        groups = [
            grp[self.response].values
            for _, grp in self.data.groupby(group)
        ]

        stat, p = levene(*groups)
        return {
            "Test": "Levene",
            "Statistic": stat,
            "p-value": p,
            "Homogeneous": "Yes" if p > 0.05 else "No"
        }

    def bartlett_test(self, group):
        """
        Bartlett's test for homogeneity of variances
        (Use only if normality holds)
        """
        groups = [
            grp[self.response].values
            for _, grp in self.data.groupby(group)
        ]

        stat, p = bartlett(*groups)
        return {
            "Test": "Bartlett",
            "Statistic": stat,
            "p-value": p,
            "Homogeneous": "Yes" if p > 0.05 else "No"
        }
