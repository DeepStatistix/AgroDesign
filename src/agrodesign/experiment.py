"""
AgroDesign — Universal Experiment Interface
------------------------------------------

One object to run the entire statistical workflow automatically.

Example
-------
Experiment(df,"Yield").rcbd("Variety","Rep").analyze()
Experiment(df,"Yield").factorial(["A","B"]).analyze()
Experiment(df,"Yield").gxe("Genotype","Environment","Rep").analyze()
"""

import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations
from scipy.stats import shapiro
import sys
import inspect
# core engines
from agrodesign.analysis.anova import Anova
from agrodesign.analysis.assumptions import Assumptions
from agrodesign.interpretation.recommendation import generate_recommendation
from agrodesign.interpretation.mixed_interpretation import interpret_mixed
# posthoc
from agrodesign.mean_separation.lsd import LSD
from agrodesign.mean_separation.tukey import TukeyHSD
from agrodesign.mean_separation.dmrt import DMRT
from agrodesign.core.collection import AgroCollection

# plots
from agrodesign.plots.mean_plot import mean_plot
from agrodesign.plots.interaction_plot import interaction_plot
from agrodesign.plots.report_plot import report_plot
from agrodesign.interpretation.gxe_interpretation import interpret_gxe
# mixed & stability
from agrodesign.mixed.lmm import MixedModel
from agrodesign.mixed.gxe import GxEModel
from agrodesign.mixed.ammi import AMMI
from agrodesign.mixed.finlay_wilkinson import FinlayWilkinson
from agrodesign.mixed.eberhart_russell import EberhartRussell
from agrodesign.mixed.stability_report import StabilityReport
from agrodesign.core.result import AgroResult


class Experiment:
    """
    Universal AgroDesign interface
    Automatically runs complete workflow based on chosen design
    """

    # -------------------------------------------------
    # INIT
    # -------------------------------------------------
    def __init__(self, data: pd.DataFrame, response):

        self.data = data.copy()

        # allow single or multiple responses
        if isinstance(response, str):
            if response not in data.columns:
                raise ValueError(f"{response} column not found")
            self.responses = [response]
        else:
            for r in response:
                if r not in data.columns:
                    raise ValueError(f"{r} column not found")
            self.responses = list(response)

        self.response = self.responses[0]  # default for compatibility
        self.grouping = None
        self.mode = None
        self.params = {}


    def by(self, column):
        if column not in self.data.columns:
            raise ValueError(f"{column} column not found")
        self.grouping = column
        return self

    def _generate_effect_list(self, factors):
        effects = []

        for r in range(1, len(factors)+1):
            for comb in combinations(factors, r):
                effects.append(list(comb) if len(comb)>1 else comb[0])

        return effects

    # =================================================
    # DESIGN DEFINITIONS
    # =================================================
    def _run_posthoc(self, aov, effect, posthoc, alpha):

        if posthoc == "lsd":
            sep = LSD(aov, effect=effect, alpha=alpha)
        elif posthoc == "tukey":
            sep = TukeyHSD(aov, effect=effect, alpha=alpha)
        elif posthoc == "dmrt":
            sep = DMRT(aov, alpha=alpha)
        else:
            raise ValueError("posthoc must be lsd/tukey/dmrt")

        return sep.test()

    def crd(self, treatment):
        self.mode = "crd"
        self.params = dict(treatment=treatment)
        return self

    def rcbd(self, treatment, block):
        self.mode = "rcbd"
        self.params = dict(treatment=treatment, block=block)
        return self

    def factorial(self, factors):
        self.mode = "factorial"
        self.params = dict(factors=factors)
        return self

    def split_plot(self, whole_plot, sub_plot, block, sub_sub_plot=None):
        self.mode = "split"
        self.params = dict(
            whole_plot=whole_plot,
            sub_plot=sub_plot,
            block=block,
            sub_sub_plot=sub_sub_plot
        )
        return self

    # =================================================
    # BREEDING / MULTI ENVIRONMENT
    # =================================================

    def gxe(self, genotype, environment, rep=None):
        self.mode = "gxe"
        self.params = dict(genotype=genotype, environment=environment, rep=rep)
        return self

    def mixed(self, fixed, random):
        self.mode = "mixed"
        self.params = dict(fixed=fixed, random=random)
        return self

    def _run_single_analysis(self, data, posthoc, alpha, plots):
        """
        Run analysis on a specific dataset subset
        (internal engine for grouped analysis)
        """

        original_data = self.data
        self.data = data

        try:
            if self.mode in ["crd", "rcbd", "factorial", "split"]:
                result = self._run_doe(posthoc, alpha, plots)
            elif self.mode == "gxe":
                result = self._run_gxe()
            elif self.mode == "mixed":
                result = self._run_mixed()
            else:
                raise RuntimeError("Invalid design mode")
        finally:
            self.data = original_data

        return result


    # =================================================
    # MAIN EXECUTION ENGINE
    # =================================================

    def run(self, posthoc="tukey", alpha=0.05, plots=True):
        """
        Run complete agronomic analysis pipeline

        Parameters
        ----------
        posthoc : "lsd" | "tukey" | "dmrt"
        plots : bool
            Whether to generate plots
        """

        if self.mode is None:
            raise RuntimeError("No design specified")

        # =====================================================
        # MULTI-RESPONSE ANALYSIS
        # =====================================================
        if len(self.responses) > 1:

            multi_results = {}
            original_response = self.response

            for resp in self.responses:
                self.response = resp

                # --- grouped + multi-response ---
                if self.grouping is not None:
                    grouped = {}
                    for level, subset in self.data.groupby(self.grouping):
                        res = self._run_single_analysis(subset, posthoc, alpha, plots)
                        res.group_label = level
                        res.response = resp
                        grouped[level] = res

                    multi_results[resp] = AgroCollection(grouped, self.grouping)

                # --- multi-response only ---
                else:
                    res = self._run_single_analysis(self.data, posthoc, alpha, plots)
                    res.response = resp
                    multi_results[resp] = res

            # restore original
            self.response = original_response

            result = AgroCollection(multi_results, grouping_name="Response")

        # =====================================================
        # GROUPED ANALYSIS (.by())
        # =====================================================
        elif self.grouping is not None:

            grouped_results = {}

            for level, subset in self.data.groupby(self.grouping):
                try:
                    res = self._run_single_analysis(subset, posthoc, alpha, plots)
                except Exception as e:
                    from agrodesign.core.result import AgroResult
                    res = AgroResult("INVALID DESIGN", self.response)
                    res.recommendation = f"Analysis skipped: {str(e)}"

                res.group_label = level
                grouped_results[level] = res

            result = AgroCollection(grouped_results, self.grouping)

        # =====================================================
        # NORMAL SINGLE ANALYSIS
        # =====================================================
        else:
            result = self._run_single_analysis(self.data, posthoc, alpha, plots)

        # =====================================================
        # PRINT BEHAVIOR (unchanged)
        # ====================================================

        return result


    def _design_title(self):
            titles = {
                "crd": "COMPLETELY RANDOMIZED DESIGN ANALYSIS",
                "rcbd": "RANDOMIZED COMPLETE BLOCK DESIGN ANALYSIS",
                "factorial": "FACTORIAL EXPERIMENT ANALYSIS",
                "split": "SPLIT-PLOT EXPERIMENT ANALYSIS"
            }
            return titles.get(self.mode, "EXPERIMENT ANALYSIS")
    
    def _find_highest_significant_effect(self, table, alpha=0.05):
        """
        Return highest-order significant effect from ANOVA table
        """

        # detect p column automatically
        pcol = None
        for c in ["PR(>F)", "Pr>F", "p-value", "P", "p"]:
            if c in table.columns:
                pcol = c
                break

        if pcol is None:
            return None

        sig_effects = []

        for idx, row in table.iterrows():

            name = str(idx)

            if "Residual" in name:
                continue

            pval = row[pcol]

            if pval is not None and pval <= alpha:
                sig_effects.append(name)

        if not sig_effects:
            return None

        # choose highest order interaction
        sig_effects.sort(key=lambda x: x.count(":"), reverse=True)

        return sig_effects[0]

    # =================================================
    # DOE PIPELINE
    # =================================================

    def _run_doe(self, posthoc, alpha, plots):

        if self.mode == "factorial":
            design_name = "Factorial Experiment"
        else:
            design_name = self.mode.upper()

        result = AgroResult(design_name, self.response)
        aov = Anova(self.data, self.response)
        result.aov = aov  # Store for plotting

        # ---------- FIT MODEL ----------
        if self.mode == "crd":
            table = aov.crd(self.params["treatment"])
            factors = [self.params["treatment"]]

        elif self.mode == "rcbd":
            table = aov.rcbd(self.params["treatment"], self.params["block"])
            factors = [self.params["treatment"]]

        elif self.mode == "factorial":
            table = aov.factorial(self.params["factors"])
            factors = list(self.params["factors"])

        elif self.mode == "split":
            table = aov.split_plot(**self.params)
            factors = [self.params["whole_plot"], self.params["sub_plot"]]

        result.anova = table.copy()

        # ---------- MEANS + POSTHOC ----------
        collected_means = {}
        effects = self._generate_effect_list(factors)

        for eff in effects:

            if isinstance(eff, list):
                effect_name = ":".join(eff)
                factor_for_plot = eff
            else:
                effect_name = eff
                factor_for_plot = eff

            aov.factorial_means(eff)

            if posthoc == "lsd":
                sep = LSD(aov, effect=effect_name, alpha=alpha)
            elif posthoc == "tukey":
                sep = TukeyHSD(aov, effect=effect_name, alpha=alpha)
            elif posthoc == "dmrt":
                sep = DMRT(aov, alpha=alpha)

            means = sep.test()
            result.means[effect_name] = means.copy()
            result.posthoc[effect_name] = posthoc

            # Store HSD value if available
            if hasattr(sep, 'hsd_value'):
                result.hsd[effect_name] = sep.hsd_value

            collected_means[effect_name] = means.copy()

            if plots:
                if isinstance(eff, list) and len(eff) == 2:
                    fig = interaction_plot(aov, eff, method=posthoc, show=False)
                    result.figures.append(fig)
                    plt.close(fig)
                else:
                    fig = mean_plot(aov=aov, factor=factor_for_plot, method=posthoc, show=False)
                    result.figures.append(fig)
                    plt.close(fig)

        # ---------- RECOMMENDATION ----------
        from agrodesign.interpretation.hierarchy import (
            highest_significant_effect,
            filter_effects_by_hierarchy
        )

        from agrodesign.interpretation.recommendation import generate_recommendation

        highest = highest_significant_effect(aov.anova_table, alpha)
        interpretable_means = filter_effects_by_hierarchy(collected_means, highest)

        # For factorial recommendation, use full means to get best combination
        if self.mode == "factorial":
            full_means = collected_means
        else:
            full_means = interpretable_means

        recommendation = generate_recommendation(
            aov.anova_table,
            full_means,
            self.mode.upper()
        )

        result.recommendation = recommendation

        # ---------- SIMPLE EFFECTS ----------
        if highest and highest.count(":") >= 2:
            from agrodesign.interpretation.simple_effects import simple_effects
            from agrodesign.plots.simple_effect_plot import simple_effect_plot

            factors_high = highest.replace("C(","").replace(")","").split(":")

            result.simple_effects_text = simple_effects(aov, factors_high, posthoc, alpha)

            if plots:
                figs = simple_effect_plot(aov, highest, posthoc, alpha, show=False)
                result.figures.extend(figs)

        # ---------- ASSUMPTIONS ----------
        assump = Assumptions(aov)
        pvalue = assump.shapiro_test()
        result.assumptions["normality_p"] = pvalue["p-value"]

        # Add homogeneity tests for factorial designs
        if self.mode == "factorial":
            homogeneity_results = []
            for factor in factors:
                levene_result = assump.levene_test(factor)
                homogeneity_results.append({
                    "factor": factor,
                    "test": "Levene",
                    "statistic": levene_result["Statistic"],
                    "p-value": levene_result["p-value"],
                    "homogeneous": levene_result["Homogeneous"]
                })
            result.assumptions["homogeneity"] = homogeneity_results

        # ---------- REPORT ----------
        if plots:
            fig = report_plot(
                aov,
                factors[:2] if len(factors) >= 2 else factors[0],
                show=False
            )
            result.figures.append(fig)
            plt.close(fig)

        return result


    def interpret_anova(table):

        effects = {}

        for effect, row in table.iterrows():

            if effect.lower() in ["residual","error"]:
                continue

            p = row["PR(>F)"]

            if p >= 0.05:
                status = "ns"
            elif p >= 0.01:
                status = "sig"
            else:
                status = "hs"

            effects[effect] = status

        # interaction override rule
        interactions = [e for e in effects if ":" in e and effects[e] != "ns"]

        if interactions:
            return "interaction_dominates", interactions

        return "main_effects", effects
    # =================================================
    # MIXED MODEL PIPELINE
    # =================================================


    def _run_mixed(self):

        model = MixedModel(self.data, self.response)
        model.fit(self.params["fixed"], self.params["random"])

        summary = model.summary()
        blup = model.fixed_blup(self.params["fixed"])
        result = AgroResult("MIXED MODEL", self.response)
        result.variance_components = summary
        result.blups = blup

        interpretation = interpret_mixed(summary, blup)
        result.recommendation = interpretation

        # ---------- ASSUMPTIONS ----------
        stat, p = shapiro(model.result.resid)
        result.assumptions["normality_p"] = p

        return result


    # =================================================
    # G×E PIPELINE
    # =================================================

    def _run_gxe(self, export=None):

        gxe = GxEModel(
            self.data,
            self.response,
            self.params["genotype"],
            self.params["environment"],
            self.params.get("rep", None)
        )

        anova = gxe.anova()
        gxe.fit()
        vc = gxe.summary()
        h2 = gxe.heritability()
        blup = gxe.blup()
        stability = gxe.stability()
        mega_env = gxe.mega_environments()
        result = AgroResult("GxE", self.response)
        result.model = gxe  # Store for plotting

        result.anova = anova
        result.variance_components = vc
        result.heritability = h2
        result.blups = blup
        result.stability = stability
        result.mega_environments = mega_env
        result.recommendation = interpret_gxe(anova, vc, h2, blup, stability, mega_env)

        # ---------- STABILITY ANALYSIS ----------
        genotype = self.params["genotype"]
        environment = self.params["environment"]

        ammi = AMMI(self.data, genotype, environment, self.response).fit()
        fw = FinlayWilkinson(self.data, genotype, environment, self.response)
        fw.fit()
        er = EberhartRussell(self.data, genotype, environment, self.response)
        er.fit()
        report = StabilityReport(ammi, fw, er)
        report.build()

        result.ammi = ammi
        result.finlay_wilkinson = fw
        result.eberhart_russell = er
        result.stability_report = report
        # -------------------------------------------------
        # Check replication per G×E cell
        # -------------------------------------------------
        gen = self.params["genotype"]
        env = self.params["environment"]
        rep = self.params.get("rep")

        cell_counts = self.data.groupby([gen, env]).size()

        if (cell_counts < 2).any():
            raise ValueError(
                "G×E model requires at least 2 replications per genotype × environment "
                "within each analysis group. "
                "Grouped analysis reduced replication below requirement."
            )

        # ---------- ASSUMPTIONS ----------
        stat, p = shapiro(gxe.result.resid)
        result.assumptions["normality_p"] = p

        return result
