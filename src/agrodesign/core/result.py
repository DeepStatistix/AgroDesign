class AgroResult:
    """
    Universal container for AgroDesign outputs
    Returned by Experiment.run()
    """

    def __init__(self, design, response):
        self.design = design
        self.response = response
        self.objective = "maximize"  # maximize or minimize
        self._is_direct = False  # flag for direct execution vs assignment

        # common
        self.anova = None
        self.aov = None  # store Anova object for plotting
        self.means = {}
        self.posthoc = {}
        self.hsd = {}
        self.assumptions = {}
        self.recommendation = None
        self.figures = []

        # mixed / breeding
        self.variance_components = None
        self.blups = None
        self.heritability = None
        self.stability = None
        self.mega_environments = None
        self.model = None  # store model for mixed/gxe plotting


    def summary(self):
        """Print agronomic interpretation"""
        if self.recommendation:
            print(f"\n================ AGRONOMIC INTERPRETATION ================\n\n{self.recommendation}\n\n=========================================================")
        else:
            print("No agronomic interpretation available.")

    def plot(self, save_dir=None, show=True):
        """
        Automatically generate all relevant plots based on design type

        Parameters
        ----------
        save_dir : str, optional
            Folder path to save figures (e.g., 'plots/')
        show : bool
            Whether to display plots (default True)
        """
        import matplotlib.pyplot as plt
        import warnings

        # Suppress matplotlib warnings
        warnings.filterwarnings("ignore", message="FigureCanvasAgg is non-interactive")
        plt.rcParams['figure.max_open_warning'] = 0

        # Clear existing figures
        self.figures = []

        # Detect design type and plot accordingly
        if self.design in ["CRD", "RCBD"]:
            self._plot_crd_rcbd(show=show)
        elif self.design in ["Factorial Experiment", "SPLIT"]:
            self._plot_factorial_split(show=show)
        elif self.design == "MIXED MODEL":
            self._plot_mixed(show=show)
        elif self.design == "GxE":
            self._plot_gxe(show=show)
        else:
            # Fallback: display stored figures if any
            pass

        # Save if requested
        if save_dir:
            import os
            os.makedirs(save_dir, exist_ok=True)
            for i, fig in enumerate(self.figures):
                fig.savefig(f"{save_dir}/plot_{i}.png", dpi=300, bbox_inches="tight")

        # Show if requested
        if show:
            for fig in self.figures:
                plt.figure(fig.number)
                plt.show()

    def save(self, path):
        """Save all figures to path (e.g., 'report.png')"""
        import matplotlib.pyplot as plt
        for i, fig in enumerate(self.figures):
            fig.savefig(f"{path}_{i}.png", dpi=300, bbox_inches="tight")

    def export(self, folder):
        """
        Create full publication folder with tables/, plots/, report.txt

        Parameters
        ----------
        folder : str
            Folder name to create (e.g., 'experiment_results')
        """
        import os

        # Create directories
        os.makedirs(f"{folder}/tables", exist_ok=True)
        os.makedirs(f"{folder}/plots", exist_ok=True)

        # Save ANOVA table as CSV
        if self.anova is not None:
            self.anova.to_csv(f"{folder}/tables/anova_table.csv", index=True)

        # Save means tables as CSV
        if self.means:
            for effect_name, means_df in self.means.items():
                safe_name = effect_name.replace(":", "_").replace("C(", "").replace(")", "")
                means_df.to_csv(f"{folder}/tables/means_{safe_name}.csv", index=True)

        # Save GxE specific tables
        if self.design == "GxE":
            if self.blups is not None:
                self.blups.to_csv(f"{folder}/tables/blups.csv", index=False)
            if self.stability is not None:
                self.stability.to_csv(f"{folder}/tables/stability.csv", index=False)
            if self.variance_components is not None:
                self.variance_components.to_csv(f"{folder}/tables/variance_components.csv", index=False)

            # Save stability analysis tables
            if hasattr(self, 'ammi') and self.ammi is not None:
                self.ammi.stability().to_csv(f"{folder}/tables/ammi_stability.csv", index=False)
                self.ammi.ranking().to_csv(f"{folder}/tables/ammi_ranking.csv", index=True)
            if hasattr(self, 'finlay_wilkinson') and self.finlay_wilkinson is not None:
                self.finlay_wilkinson.classify().to_csv(f"{folder}/tables/fw_regression.csv", index=False)
            if hasattr(self, 'eberhart_russell') and self.eberhart_russell is not None:
                self.eberhart_russell.classify().to_csv(f"{folder}/tables/er_stability.csv", index=False)
            if hasattr(self, 'stability_report') and self.stability_report is not None:
                self.stability_report.report.to_csv(f"{folder}/tables/stability_ranking.csv", index=True)

        # Save all figures as PNG
        if self.figures:
            for i, fig in enumerate(self.figures):
                fig.savefig(f"{folder}/plots/plot_{i}.png", dpi=300, bbox_inches="tight")

        # Save full report as TXT
        with open(f"{folder}/report.txt", "w", encoding="utf-8") as f:
            f.write(self._full_report())

    def _plot_crd_rcbd(self, show=True):
        """Plot for CRD and RCBD designs"""
        import matplotlib.pyplot as plt
        from agrodesign.plots.boxplot_letters import boxplot_letters
        from agrodesign.analysis.assumptions import Assumptions

        # Boxplot with letters (if aov available)
        if self.aov is not None:
            for effect in self.means.keys():
                if effect.count(":") == 0:
                    try:
                        fig = boxplot_letters(
                            self.aov,
                            factor=effect,
                            ylabel=self.response,
                            title=f"Boxplot for {effect}",
                            show=False
                        )
                        self.figures.append(fig)
                    except Exception as e:
                        pass

        # Residual diagnostics
        if self.aov is not None:
            try:
                assump = Assumptions(self.aov)

                # QQ plot
                fig, ax = plt.subplots(figsize=(6, 6))
                from scipy.stats import probplot
                probplot(assump.residuals, plot=ax)
                ax.set_title("QQ Plot of Residuals")
                self.figures.append(fig)

                # Residual vs fitted
                fig, ax = plt.subplots(figsize=(6, 6))
                ax.scatter(assump.fitted, assump.residuals)
                ax.axhline(y=0, color='r', linestyle='--')
                ax.set_xlabel("Fitted Values")
                ax.set_ylabel("Residuals")
                ax.set_title("Residuals vs Fitted")
                self.figures.append(fig)
            except Exception as e:
                pass

    def _plot_factorial_split(self, show=True):
        """Plot for Factorial and Split-plot designs"""
        import matplotlib.pyplot as plt
        from agrodesign.plots.mean_plot import mean_plot
        from agrodesign.plots.boxplot_letters import boxplot_letters
        from agrodesign.plots.interaction_plot import interaction_plot
        from agrodesign.plots.simple_effect_plot import simple_effect_plot
        from agrodesign.analysis.assumptions import Assumptions

        # Plot interaction plots for all two-way interactions and significant higher interactions
        if self.anova is not None and self.aov is not None:
            # Find p-column
            pcol = None
            for c in ["PR(>F)", "Pr>F", "p-value", "P", "p"]:
                if c in self.anova.columns:
                    pcol = c
                    break

            if pcol is not None:
                for idx, row in self.anova.iterrows():
                    name = str(idx)
                    if "Residual" in name or "Error" in name:
                        continue
                    # Clean the effect name
                    clean_name = name.replace("C(", "").replace(")", "")
                    colon_count = clean_name.count(":")
                    if colon_count == 1:  # Two-way interaction - plot all
                        factors = clean_name.split(":")
                        if len(factors) == 2:
                            try:
                                fig = interaction_plot(self.aov, factors, method="tukey", show=False)
                                self.figures.append(fig)
                            except Exception as e:
                                print(f"Warning: Could not generate interaction plot for {clean_name}: {e}")
                    elif colon_count >= 2:  # Three-way or higher interaction - only if significant
                        pval = row[pcol]
                        if pval is not None and pval <= 0.05:
                            try:
                                figs = simple_effect_plot(self.aov, clean_name, method="tukey", alpha=0.05, show=False)
                                self.figures.extend(figs)
                            except Exception as e:
                                pass

        # Always plot boxplots for all effects
        for effect in self.means.keys():
            # Boxplot with letters
            if self.aov is not None:
                try:
                    fig = boxplot_letters(self.aov, factor=effect, ylabel=self.response, title=f"Boxplot for {effect}", show=False)
                    self.figures.append(fig)
                except Exception as e:
                    pass

        # Always include residual diagnostics
        if self.aov is not None:
            assump = Assumptions(self.aov)
            # QQ plot
            fig, ax = plt.subplots(figsize=(6, 6))
            from scipy.stats import probplot
            probplot(assump.residuals, plot=ax)
            ax.set_title("QQ Plot of Residuals")
            self.figures.append(fig)

            # Residual vs fitted
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.scatter(assump.fitted, assump.residuals)
            ax.axhline(y=0, color='r', linestyle='--')
            ax.set_xlabel("Fitted Values")
            ax.set_ylabel("Residuals")
            ax.set_title("Residuals vs Fitted")
            self.figures.append(fig)

    def _plot_mixed(self, show=True):
        """Plot for Mixed Model designs"""
        import matplotlib.pyplot as plt
        import pandas as pd

        # BLUP bar chart
        if self.blups is not None and not self.blups.empty:
            fig, ax = plt.subplots(figsize=(8, 6))
            blups_sorted = self.blups.sort_values("BLUP", ascending=False)
            values = blups_sorted["BLUP"]
            labels = blups_sorted.iloc[:, 0]  # First column is the effect name
            ax.bar(range(len(values)), values)
            ax.set_xticks(range(len(values)))
            ax.set_xticklabels(labels, rotation=45)
            ax.set_ylabel("BLUP")
            ax.set_title("BLUP Ranking")
            plt.tight_layout()
            self.figures.append(fig)

        # Variance component pie chart
        if self.variance_components is not None and not self.variance_components.empty:
            fig, ax = plt.subplots(figsize=(6, 6))
            vc = self.variance_components
            labels = vc["Effect"]
            sizes = vc["Variance"]
            ax.pie(sizes, labels=labels, autopct='%1.1f%%')
            ax.set_title("Variance Components")
            self.figures.append(fig)

        # Residual QQ plot
        if self.model is not None and hasattr(self.model, 'result'):
            fig, ax = plt.subplots(figsize=(6, 6))
            import scipy.stats as stats
            stats.probplot(self.model.result.resid, dist="norm", plot=ax)
            ax.set_title("Residual QQ Plot")
            self.figures.append(fig)

    def _plot_gxe(self, show=True):
        """Plot for GxE designs"""
        import matplotlib.pyplot as plt
        import pandas as pd

        # Genotype BLUP ranking
        if self.blups is not None:
            fig, ax = plt.subplots(figsize=(8, 6))
            if isinstance(self.blups, pd.DataFrame):
                blups_sorted = self.blups.sort_values(by=self.blups.columns[0], ascending=False)
                values = blups_sorted[self.blups.columns[0]]
                index = blups_sorted.index
            else:
                blups_sorted = self.blups.sort_values(ascending=False)
                values = blups_sorted.values
                index = blups_sorted.index
            ax.bar(range(len(values)), values)
            ax.set_xticks(range(len(values)))
            ax.set_xticklabels(index, rotation=45)
            ax.set_ylabel("BLUP")
            ax.set_title("Genotype BLUP Ranking")
            plt.tight_layout()
            self.figures.append(fig)

        # Stability plot (variance vs mean)
        if self.blups is not None and self.variance_components is not None:
            # This would require additional computation, simplified for now
            pass

        # AMMI biplot (if available)
        try:
            from agrodesign.plots.ammi_biplot import ammi_biplot
            if hasattr(self, 'ammi') and self.ammi is not None:
                fig = ammi_biplot(self.ammi, show=False)
                self.figures.append(fig)
        except:
            pass

        # GGE biplot
        try:
            from agrodesign.plots.gge_biplot import gge_biplot
            if self.model is not None:
                fig = gge_biplot(self.model.data, self.model.genotype, self.model.environment, self.model.response, show=False)
                self.figures.append(fig)
        except:
            pass

        # Finlay-Wilkinson plot
        try:
            from agrodesign.plots.fw_plot import fw_plot
            if hasattr(self, 'finlay_wilkinson') and self.finlay_wilkinson is not None:
                fig = fw_plot(self.finlay_wilkinson, show=False)
                self.figures.append(fig)
        except:
            pass

        # Stability scatter (Eberhart-Russell)
        try:
            from agrodesign.plots.stability_scatter import stability_scatter
            if hasattr(self, 'eberhart_russell') and self.eberhart_russell is not None:
                fig = stability_scatter(self.eberhart_russell, show=False)
                self.figures.append(fig)
        except:
            pass

        # Heritability gauge (simplified)
        if self.heritability is not None:
            fig, ax = plt.subplots(figsize=(6, 6))
            h2 = self.heritability
            ax.pie([h2, 1-h2], labels=['Heritability', 'Environment'], autopct='%1.1f%%')
            ax.set_title("Heritability")
            self.figures.append(fig)

        # Stability plot (AMMI ASV vs Mean)
        if self.stability is not None and self.blups is not None:
            fig, ax = plt.subplots(figsize=(8, 6))
            # Get means from BLUPs (assuming BLUPs represent means)
            means = self.blups.set_index('Genotype')['BLUP']
            stab = self.stability.set_index('Genotype')['ASV']
            common_genos = means.index.intersection(stab.index)
            ax.scatter(stab[common_genos], means[common_genos])
            for geno in common_genos:
                ax.annotate(geno, (stab[geno], means[geno]))
            ax.set_xlabel("AMMI Stability Value (ASV)")
            ax.set_ylabel("Genotype BLUP")
            ax.set_title("Stability vs Yield")
            self.figures.append(fig)

    # -----------------------------------
    # nice printing in console
    # -----------------------------------
    @property
    def _snapshot_text(self):
        """Short scientific snapshot"""
        lines = []

        # Header
        lines.append(f"AgroResult ({self.design})")
        lines.append(f"Response: {self.response}")

        # Significant factors
        if self.anova is not None:
            pcol = None
            for c in ["PR(>F)", "Pr>F", "p-value", "P", "p"]:
                if c in self.anova.columns:
                    pcol = c
                    break

            if pcol is not None:
                sig_factors = []
                for idx, row in self.anova.iterrows():
                    name = str(idx)
                    if "Residual" in name or "Error" in name:
                        continue
                    pval = row[pcol]
                    if pval is not None and pval <= 0.05:
                        sig_factors.append(name.replace("C(", "").replace(")", ""))

                if sig_factors:
                    lines.append(f"Significant factors: {', '.join(sig_factors)}")
                else:
                    lines.append("Significant factors: None")

        # Best treatment
        if self.means:
            # Find the effect with highest significance
            best_effect = None
            best_mean = -float('inf')
            best_treatment = None

            for effect_name, means_df in self.means.items():
                if means_df.empty:
                    continue
                max_mean = means_df['Mean'].max()
                if max_mean > best_mean:
                    best_mean = max_mean
                    best_effect = effect_name
                    best_row = means_df.loc[means_df['Mean'].idxmax()]
                    if ":" in effect_name:
                        factors = effect_name.split(":")
                        best_treatment = " × ".join([str(best_row[f]) for f in factors])
                    else:
                        best_treatment = str(best_row.name)

            if best_treatment:
                lines.append(f"Best treatment: {best_treatment}")
                lines.append(f"Expected yield: {best_mean:.2f}")

        # Best BLUP for mixed models
        if self.design == "MIXED MODEL" and self.blups is not None and not self.blups.empty:
            best_blup_row = self.blups.iloc[0]
            best_level = best_blup_row.iloc[0]  # First column is the level name
            best_blup_value = best_blup_row['BLUP']
            lines.append(f"Best level: {best_level}")
            lines.append(f"BLUP: {best_blup_value:.2f}")

        # GxE specific snapshot
        if self.design == "GxE":
            if self.heritability is not None:
                lines.append(f"Heritability: {self.heritability:.2f}")
            if self.blups is not None and not self.blups.empty:
                best_geno = self.blups.iloc[0]['Genotype']
                lines.append(f"Best genotype: {best_geno}")
            if self.stability is not None and not self.stability.empty:
                most_stable = self.stability.iloc[0]['Genotype']
                lines.append(f"Most stable genotype: {most_stable}")
            if self.mega_environments is not None:
                target_env = list(self.mega_environments.keys())[0]  # Just show first one
                winner = self.mega_environments[target_env]
                lines.append(f"Target environment: {target_env}")

        return "\n".join(lines)

    def __repr__(self):
        return self._snapshot_text

    def __str__(self):
        return self._full_report()

    def _full_report(self):
        """Generate full detailed analysis report"""
        if hasattr(self, '_full_report_text') and self._full_report_text:
            report = [self._full_report_text]
        else:
            report = []

            # Header
            report.append("=" * 50)
            report.append("AGRODESIGN ANALYSIS")
            report.append("=" * 50)

            # Design info
            if self.design == "Factorial Experiment":
                report.append("\nFACTORIAL EXPERIMENT ANALYSIS")
            else:
                report.append(f"\n{self.design} ANALYSIS")

            report.append(f"Response variable: {self.response}")
            report.append("Post-hoc test: Tukey HSD (α = 0.05)")

            # ANOVA Table
            if self.anova is not None:
                report.append("\n" + "-" * 50)
                report.append("ANOVA TABLE")
                report.append("-" * 50)

                # Format ANOVA table with significance
                def safe_float(p):
                    if isinstance(p, str) and '<' in p:
                        return 0.0
                    return float(p)

                # Detect p column automatically
                pcol = None
                for c in ["PR(>F)", "Pr>F", "p-value", "P", "p"]:
                    if c in self.anova.columns:
                        pcol = c
                        break

                anova_copy = self.anova.copy()
                if pcol is not None:
                    anova_copy['Significance'] = anova_copy[pcol].apply(
                        lambda p: '***' if safe_float(p) < 0.001 else '**' if safe_float(p) < 0.01 else '*' if safe_float(p) < 0.05 else 'ns'
                    )
                    anova_copy[pcol] = anova_copy[pcol].apply(lambda p: '<0.001' if safe_float(p) < 0.001 else f'{safe_float(p):.3f}')

                    # Reorder columns
                    cols = ['DF', 'MS', 'F', pcol, 'Significance']
                    anova_display = anova_copy[cols]

                    # Convert to string with proper formatting and Source column
                    table_str = anova_display.to_string()
                    # Add Source header
                    lines = table_str.split('\n')
                    if len(lines) > 0:
                        lines[0] = 'Source' + lines[0][6:]  # Replace empty with Source
                    report.append('\n'.join(lines))
                else:
                    # If no p-value column found, just display the table as is
                    table_str = self.anova.to_string()
                    lines = table_str.split('\n')
                    if len(lines) > 0:
                        lines[0] = 'Source' + lines[0][6:]  # Replace empty with Source
                    report.append('\n'.join(lines))

            # Highest significant effect
            if self.anova is not None:
                from agrodesign.interpretation.hierarchy import highest_significant_effect
                highest = highest_significant_effect(self.anova, alpha=0.05)
                if highest:
                    report.append(f"\nHighest significant effect: {highest.replace('C(', '').replace(')', '')}")
                else:
                    report.append("\nHighest significant effect: MAIN EFFECTS")

                report.append("\nInterpretation rule:")
                if highest and ":" in highest:
                    report.append("Interaction detected → interpret interaction effects")
                else:
                    report.append("No interaction detected → interpret main effects")

            # Post-hoc critical values
            if self.hsd:
                report.append("\n" + "-" * 50)
                report.append("POST HOC TEST CRITICAL VALUES")
                report.append("-" * 50)

                for effect, hsd_val in self.hsd.items():
                    report.append(f"HSD({effect}) = {hsd_val:.4f}")

            # Mean comparison
            if self.means:
                report.append("\n" + "-" * 50)
                report.append("MEAN COMPARISON (ALL EFFECTS)")
                report.append("-" * 50)

                # Group effects by order
                main_effects = {}
                two_way = {}
                three_way = {}

                for effect_name, means_df in self.means.items():
                    order = effect_name.count(":")
                    if order == 0:
                        main_effects[effect_name] = means_df
                    elif order == 1:
                        two_way[effect_name] = means_df
                    elif order == 2:
                        three_way[effect_name] = means_df

                # Main effects
                if main_effects:
                    report.append("\nMAIN EFFECTS")
                    report.append("-" * 15)
                    for effect, df in main_effects.items():
                        report.append(f"\nFactor {effect}")
                        report.append(df[['Mean', 'Group']].to_string(index=False, float_format='%.3f'))

                # Two-way interactions
                if two_way:
                    report.append("\n\nTWO WAY INTERACTIONS")
                    report.append("-" * 20)
                    for effect, df in two_way.items():
                        factors = effect.split(":")
                        report.append(f"\n{factors[0]} × {factors[1]}")
                        # Format columns for interactions
                        cols = factors + ['Mean', 'Group']
                        report.append(df[cols].to_string(index=False, float_format='%.3f'))

                # Three-way interactions
                if three_way:
                    report.append("\n\nTHREE WAY INTERACTION")
                    report.append("-" * 20)
                    for effect, df in three_way.items():
                        factors = effect.split(":")
                        report.append(f"\n{factors[0]}   {factors[1]}   {factors[2]}   Mean   Group")
                        for _, row in df.iterrows():
                            report.append(f"{row[factors[0]]}   {row[factors[1]]}   {row[factors[2]]}   {row['Mean']:.3f}   {row['Group']}")

            # Simple effects
            if hasattr(self, 'simple_effects_text') and self.simple_effects_text:
                report.append(self.simple_effects_text)

            # Variance Components (for mixed models)
            if self.design == "MIXED MODEL" and self.variance_components is not None:
                report.append("\nVariance components:")
                report.append("-" * 32)
                for _, row in self.variance_components.iterrows():
                    effect = row["Effect"]
                    variance = row["Variance"]
                    report.append(f"{effect} (random)     {variance:.2f}")

            # BLUPs (for mixed models)
            if self.design == "MIXED MODEL" and self.blups is not None:
                report.append("\nBLUPs (Treatment effects)")
                report.append("-" * 32)
                for _, row in self.blups.iterrows():
                    level = row.iloc[0]
                    blup = row["BLUP"]
                    report.append(f"{level}    {blup:.1f}")

                # Normality test for mixed models
                p_val = self.assumptions.get("normality_p", None)
                if p_val is not None and isinstance(p_val, (int, float)):
                    report.append(f"\nNormality test (Shapiro-Wilk): p = {p_val:.2f}")
                    if p_val >= 0.05:
                        report.append("Residuals: Normally distributed")
                    else:
                        report.append("Residuals: Not normally distributed")

            # GxE specific sections
            if self.design == "GxE":
                # Heritability
                if self.heritability is not None:
                    report.append(f"\nHeritability (broad sense): {self.heritability:.2f}")

                # Genotype BLUPs
                if self.blups is not None:
                    report.append("\nGenotype BLUPs")
                    report.append("-" * 15)
                    for _, row in self.blups.iterrows():
                        report.append(f"{row['Genotype']}   {row['BLUP']:.1f}")

                # Stability (AMMI/IPCA1)
                if self.stability is not None:
                    report.append("\nStability (AMMI/IPCA1)")
                    report.append("-" * 22)
                    report.append("Most stable genotype: " + str(self.stability.iloc[0]['Genotype']))

                # Mega-environment winner
                if self.mega_environments is not None:
                    report.append("\nMega-environment winner")
                    report.append("-" * 23)
                    for env, geno in self.mega_environments.items():
                        report.append(f"{env} → {geno}")

            # Final recommendation
                if self.blups is not None and self.stability is not None:
                    best_yielding = self.blups.iloc[0]['Genotype']
                    most_stable = self.stability.iloc[0]['Genotype']
                    report.append("\nFINAL RECOMMENDATION")
                    report.append("-" * 21)
                    report.append(f"{best_yielding} is the highest yielding genotype across environments.")
                    report.append(f"{most_stable} is the most stable genotype.")

            # Stability Analysis Section
            if hasattr(self, 'ammi') and self.ammi is not None:
                report.append("\n" + "=" * 50)
                report.append("STABILITY ANALYSIS")
                report.append("=" * 50)

                # AMMI
                report.append("\nAMMI")
                report.append("-" * 4)
                stability_table = self.ammi.stability()
                report.append(stability_table.to_string(index=False))

                ranking_table = self.ammi.ranking()
                report.append("\nAMMI Ranking")
                report.append("-" * 12)
                report.append(ranking_table.to_string())

                # Finlay-Wilkinson
                report.append("\nFinlay-Wilkinson")
                report.append("-" * 16)
                fw_classify = self.finlay_wilkinson.classify()
                report.append(fw_classify.to_string(index=False))

                # Eberhart-Russell
                report.append("\nEberhart-Russell")
                report.append("-" * 16)
                er_classify = self.eberhart_russell.classify()
                report.append(er_classify.to_string(index=False))

                # Consensus Stability
                report.append("\nConsensus Stability")
                report.append("-" * 19)
                best_geno = self.stability_report.best()
                report.append(best_geno.to_string())

            # Recommendation
            if self.recommendation:
                report.append("\n" + "-" * 50)
                if self.design == "MIXED MODEL":
                    report.append("FINAL RECOMMENDATION")
                else:
                    report.append("AGRONOMIC INTERPRETATION")
                report.append("-" * 50)
                report.append(self.recommendation)

            # Assumptions (for non-mixed models)
            if self.assumptions and self.design != "MIXED MODEL":
                report.append("\n" + "-" * 50)
                report.append("ASSUMPTION CHECK")
                report.append("-" * 50)

                p_val = self.assumptions.get("normality_p", None)
                if p_val is not None and isinstance(p_val, (int, float)):
                    if p_val < 0.05:
                        status = "Not normally distributed"
                        rec = "transformation may improve model validity"
                    else:
                        status = "Normally distributed"
                        rec = "assumptions satisfied"

                    report.append(f"Shapiro-Wilk normality test: p = {p_val:.5f}")
                    report.append(f"Residuals: {status}")
                    report.append(f"Recommendation: {rec}")

                # Homogeneity of variance tests
                homogeneity = self.assumptions.get("homogeneity", [])
                if homogeneity:
                    report.append("")
                    for h in homogeneity:
                        report.append(f"Levene's test for {h['factor']}: p = {h['p-value']:.5f}, {h['homogeneous']}")


            report.append("\n" + "=" * 50)

        return "\n".join(report)
