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
from itertools import combinations
# core engines
from agrodesign.analysis.anova import Anova
from agrodesign.analysis.assumptions import Assumptions
from agrodesign.interpretation.recommendation import generate_recommendation
from agrodesign.interpretation.mixed_interpretation import interpret_mixed
# posthoc
from agrodesign.mean_separation.lsd import LSD
from agrodesign.mean_separation.tukey import TukeyHSD
from agrodesign.mean_separation.dmrt import DMRT

# plots
from agrodesign.plots.mean_plot import mean_plot
from agrodesign.plots.interaction_plot import interaction_plot
from agrodesign.plots.report_plot import report_plot
from agrodesign.interpretation.gxe_interpretation import interpret_gxe
# mixed & stability
from agrodesign.mixed.lmm import MixedModel
from agrodesign.mixed.gxe import GxEModel
from agrodesign.mixed.ammi import AMMI
from agrodesign.mixed.stability_report import StabilityReport


class Experiment:
    """
    Universal AgroDesign interface
    Automatically runs complete workflow based on chosen design
    """

    # -------------------------------------------------
    # INIT
    # -------------------------------------------------
    def __init__(self, data: pd.DataFrame, response: str):

        if response not in data.columns:
            raise ValueError(f"{response} column not found")

        self.data = data.copy()
        self.response = response

        self.mode = None
        self.params = {}


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

    # =================================================
    # MAIN EXECUTION ENGINE
    # =================================================

    def run(self, posthoc="tukey", alpha=0.05, plots=True, export=None):
        """
        Run complete agronomic analysis pipeline

        Parameters
        ----------
        posthoc : "lsd" | "tukey" | "dmrt"
        export : str or None
            "report.png", "report.pdf", or folder path
        """


        if self.mode is None:
            raise RuntimeError("No design specified")

        print("\n================ AGRODESIGN ANALYSIS ================")

        if self.mode in ["crd", "rcbd", "factorial", "split"]:
            return self._run_doe(posthoc, alpha, plots, export)

        elif self.mode == "gxe":
            return self._run_gxe(export)

        elif self.mode == "mixed":
            return self._run_mixed(export)



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

    def _run_doe(self, posthoc, alpha, plots, export=None):

        print("\n======================================================")
        print(self._design_title())
        print("Response variable:", self.response)
        print("======================================================")

        aov = Anova(self.data, self.response)

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

        # ---------- PRINT ANOVA ----------
        print("\nANOVA TABLE")
        print(table)
    
        # ---------- FIND HIGHEST EFFECT ----------
        highest = self._find_highest_significant_effect(table, alpha)
        print("\nHighest significant effect:", highest)


        # =====================================================
        # SIMPLE EFFECT ANALYSIS (if interaction significant)
        # =====================================================
        if highest and highest.count(":") >= 1:

            from agrodesign.interpretation.simple_effects import simple_effects

            factors_high = highest.replace("C(","").replace(")","").split(":")

            simple_effects(aov, factors_high, posthoc, alpha)

        # ---------- MEANS + POSTHOC ----------
        print("\n========== MEAN COMPARISON ==========")

        collected_means = {}
        effects = self._generate_effect_list(factors)

        for eff in effects:

            if isinstance(eff, list):
                effect_name = ":".join(eff)
                title = " × ".join(eff)
                factor_for_plot = eff
            else:
                effect_name = eff
                title = eff
                factor_for_plot = eff

            print(f"\nEffect: {title}")

            aov.factorial_means(eff)

            if posthoc == "lsd":
                sep = LSD(aov, effect=effect_name, alpha=alpha)
            elif posthoc == "tukey":
                sep = TukeyHSD(aov, effect=effect_name, alpha=alpha)
            elif posthoc == "dmrt":
                sep = DMRT(aov, alpha=alpha)

            means = sep.test()
            collected_means[effect_name] = means.copy()

            print(means.round(4))
            # ---- print critical value ----
            if hasattr(sep, "lsd_value"):
                print(f"LSD({alpha}) = {sep.lsd_value:.4f}")
            elif hasattr(sep, "hsd_value"):
                print(f"HSD({alpha}) = {sep.hsd_value:.4f}")
            elif hasattr(sep, "lsr"):
                print(f"DMRT({alpha}) critical ranges computed")

            if plots:
                if isinstance(eff, list) and len(eff) == 2:
                    interaction_plot(aov, eff, method=posthoc)
                else:
                    mean_plot(aov=aov, factor=factor_for_plot, method=posthoc)

        # ---------- RECOMMENDATION ----------
        from agrodesign.interpretation.hierarchy import (
            highest_significant_effect,
            filter_effects_by_hierarchy
        )
        from agrodesign.interpretation.recommendation import generate_recommendation

        print("\n========== FINAL RECOMMENDATION ==========")

        highest = highest_significant_effect(aov.anova_table, alpha)
        interpretable_means = filter_effects_by_hierarchy(collected_means, highest)

        recommendation = generate_recommendation(
            aov.anova_table,
            interpretable_means,
            self.mode.upper()
        )

        print(recommendation)

        # ---------- SIMPLE EFFECTS ----------
        if highest and highest.count(":") >= 2:
            from agrodesign.interpretation.simple_effects import simple_effects
            from agrodesign.plots.simple_effect_plot import simple_effect_plot

            factors_high = highest.replace("C(","").replace(")","").split(":")

            print("\n========== SIMPLE EFFECT ANALYSIS ==========")
            simple_effects(aov, factors_high, posthoc, alpha)

            print("\n========== CONDITIONAL INTERACTION PLOTS ==========")
            simple_effect_plot(aov, highest, posthoc, alpha)

        # ---------- ASSUMPTIONS ----------
        print("\n========== ASSUMPTIONS ==========")
        assump = Assumptions(aov)
        print("Shapiro p-value:", assump.shapiro_test())

        # ---------- REPORT ----------
        if plots:
            report_plot(
                aov,
                factors[:2] if len(factors) >= 2 else factors[0],
                save=export
            )

        return None

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

        # =====================================================
        # AUTOMATIC EFFECT ANALYSIS (ALL ORDERS)
        # =====================================================
        print("\n========== MEAN COMPARISON ==========")

        effects = self._generate_effect_list(factors)

        for eff in effects:

            # normalize name
            if isinstance(eff, list):
                effect_name = ":".join(eff)
                title = " × ".join(eff)
                factor_for_plot = eff
            else:
                effect_name = eff
                title = eff
                factor_for_plot = eff

            print(f"\nEffect: {title}")

            # ---- compute means ----
            aov.factorial_means(eff)

            # ---- run posthoc ----
            if posthoc == "lsd":
                sep = LSD(aov, effect=effect_name, alpha=alpha)
                label = "LSD"

            elif posthoc == "tukey":
                sep = TukeyHSD(aov, effect=effect_name, alpha=alpha)
                label = "HSD"

            elif posthoc == "dmrt":
                sep = DMRT(aov, alpha=alpha)
                label = "DMRT"

            else:
                raise ValueError("posthoc must be lsd/tukey/dmrt")

            means = sep.test()

            # ---- print critical value ----
            if hasattr(sep, "lsd_value"):
                print(f"LSD({alpha}) = {sep.lsd_value:.4f}")
            elif hasattr(sep, "hsd_value"):
                print(f"HSD({alpha}) = {sep.hsd_value:.4f}")
            elif hasattr(sep, "lsr"):
                print(f"DMRT({alpha}) critical ranges computed")

            print(means.round(4))
            self._recommendation(means, title)

            # ---- plots ----
            if plots:
                if isinstance(eff, list) and len(eff) == 2:
                    interaction_plot(aov, eff, method=posthoc)
                else:
                    mean_plot(aov=aov, factor=factor_for_plot, method=posthoc)

        # =====================================================
        # ASSUMPTIONS
        # =====================================================
        print("\n========== ASSUMPTIONS ==========")
        assump = Assumptions(aov)
        print("Shapiro p-value:", assump.shapiro_test())

        # =====================================================
        # FINAL REPORT
        # =====================================================
        print("\n========== SUMMARY REPORT ==========")
        savepath = None
        if export:
            if export.endswith(".png") or export.endswith(".pdf"):
                savepath = export
            else:
                savepath = export + "/agrodesign_report.png"

        report_plot(
            aov,
            factors[:2] if len(factors) >= 2 else factors[0],
            save=savepath
        )

        if savepath:
            print(f"\nReport exported to: {savepath}")

        return None

    # =================================================
    # MIXED MODEL PIPELINE
    # =================================================


    def _run_mixed(self, export=None):

        print("\nMIXED MODEL ANALYSIS")

        model = MixedModel(self.data, self.response)
        model.fit(self.params["fixed"], self.params["random"])

        summary = model.summary()
        blup = model.blup(self.params["random"])

        print("\nVariance Components")
        print(summary)

        print("\nBLUPs")
        print(blup)

        print("\nINTERPRETATION")
        print(interpret_mixed(summary, blup))

        return model


    # =================================================
    # G×E PIPELINE
    # =================================================

    def _run_gxe(self, export=None):

        print("\nG×E ANALYSIS")

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

        print("\nANOVA")
        print(anova)

        print("\nVariance Components")
        print(vc)

        print("\nHeritability:", h2)

        print("\nGenotype BLUPs")
        print(blup)

        print("\nINTERPRETATION")
        print(interpret_gxe(anova, vc, h2, blup))


    def _recommendation(self, sep_table, factor):

        # highest mean treatment
        best = sep_table.iloc[0]

        level_cols = [c for c in sep_table.columns if c not in ["Mean","Replications","Group"]]
        treatment_name = " × ".join(str(best[c]) for c in level_cols)

        rec = (
            f"\nFINAL RECOMMENDATION:\n"
            f"{factor}: {treatment_name} produced the highest mean "
            f"({best['Mean']:.3f}) and belongs to the superior statistical group '{best['Group']}'."
        )

        print(rec)
        return rec
