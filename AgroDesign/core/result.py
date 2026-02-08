class AgroResult:
    """
    Universal container for AgroDesign outputs
    Returned by Experiment.run()
    """

    def __init__(self, design, response):
        self.design = design
        self.response = response
        self.objective = "maximize"  # maximize or minimize

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
        self.model = None  # store model for mixed/gxe plotting

    def summary(self):
        """Print full report and agronomic interpretation"""
        # Full report as before
        print(self._full_report())

        # Agronomic interpretation
        print("\n" + "=" * 32 + " AGRONOMIC INTERPRETATION " + "=" * 32)

        if self.anova is None:
            print("No ANOVA results available.")
            return

        alpha = 0.05

        # Find p-column
        pcol = None
        for c in ["PR(>F)", "Pr>F", "p-value", "P", "p"]:
            if c in self.anova.columns:
                pcol = c
                break

        if pcol is None:
            print("No p-value column found in ANOVA.")
            return

        # Interpret ANOVA
        significant_effects = []
        for idx, row in self.anova.iterrows():
            name = str(idx)
            if "Residual" in name or "Error" in name:
                continue
            pval = row[pcol]
            if pval is not None and pval <= alpha:
                significant_effects.append(name)

        if significant_effects:
            print("Significant differences among treatments were detected.")
        else:
            print("No significant treatment differences were observed.")

        # Significant main factors
        main_factors = [eff.replace('C(', '').replace(')', '') for eff in significant_effects if ":" not in eff]
        for factor in main_factors:
            if factor in self.means:
                means_df = self.means[factor]
                if self.objective == "maximize":
                    best_row = means_df.loc[means_df['Mean'].idxmax()]
                    worst_row = means_df.loc[means_df['Mean'].idxmin()]
                    gain = (best_row['Mean'] - worst_row['Mean']) / worst_row['Mean'] * 100
                else:  # minimize
                    best_row = means_df.loc[means_df['Mean'].idxmin()]
                    worst_row = means_df.loc[means_df['Mean'].idxmax()]
                    gain = (worst_row['Mean'] - best_row['Mean']) / worst_row['Mean'] * 100

                print(f"Factor {factor} significantly affected {self.response}.")
                print(f"Level {best_row.name} produced {gain:.1f}% {'higher' if self.objective == 'maximize' else 'lower'} {self.response} than {worst_row.name}.")

        # Interaction rule
        from agrodesign.interpretation.hierarchy import highest_significant_effect
        highest = highest_significant_effect(self.anova, alpha=alpha)
        if highest and ":" in highest:
            print("Interaction present — interpret combinations.")
        else:
            print("No interaction — main effects interpreted independently.")

        # Best treatment combination
        if highest and highest in self.means:
            means_df = self.means[highest]
            best_row = means_df.loc[means_df['Mean'].idxmax()]
            factors = highest.split(":")
            combo = " × ".join([str(best_row[f]) for f in factors])
            print(f"The combination {combo} consistently produced the highest {self.response}.")

            # Practical implication
            print(f"Farmers should adopt {combo} under tested conditions.")

            # Expected improvement vs worst
            worst_row = means_df.loc[means_df['Mean'].idxmin()]
            if self.objective == "maximize":
                improvement = (best_row['Mean'] - worst_row['Mean']) / worst_row['Mean'] * 100
                print(f"Expected improvement: {improvement:.1f}% increase in {self.response} compared to the worst treatment.")
            else:
                improvement = (worst_row['Mean'] - best_row['Mean']) / worst_row['Mean'] * 100
                print(f"Expected improvement: {improvement:.1f}% decrease in {self.response} compared to the worst treatment.")
        elif main_factors:
            # If no interaction, use main effects for best combo
            best_levels = {}
            for factor in main_factors:
                if factor in self.means:
                    means_df = self.means[factor]
                    if self.objective == "maximize":
                        best_level = means_df.loc[means_df['Mean'].idxmax()].name
                    else:
                        best_level = means_df.loc[means_df['Mean'].idxmin()].name
                    best_levels[factor] = best_level
            if best_levels:
                combo = " × ".join([f"{f}={best_levels[f]}" for f in best_levels])
                print(f"The combination {combo} consistently produced the highest {self.response}.")
                print(f"Farmers should adopt {combo} under tested conditions.")

                # Improvement: need to find overall best and worst means
                # For simplicity, use the best main effect mean as proxy
                best_mean = max([self.means[f]['Mean'].max() for f in main_factors if f in self.means])
                worst_mean = min([self.means[f]['Mean'].min() for f in main_factors if f in self.means])
                if self.objective == "maximize":
                    improvement = (best_mean - worst_mean) / worst_mean * 100
                    print(f"Expected improvement: {improvement:.1f}% increase in {self.response} compared to the worst treatment.")
                else:
                    improvement = (worst_mean - best_mean) / worst_mean * 100
                    print(f"Expected improvement: {improvement:.1f}% decrease in {self.response} compared to the worst treatment.")

        print("=" * 65)

    def plot(self, save=None, show=True):
        """
        Automatically generate all relevant plots based on design type

        Parameters
        ----------
        save : str, optional
            Folder path to save figures (e.g., 'plots/')
        show : bool
            Whether to display plots (default True)
        """
        import matplotlib.pyplot as plt

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
        if save:
            import os
            os.makedirs(save, exist_ok=True)
            for i, fig in enumerate(self.figures):
                fig.savefig(f"{save}/plot_{i}.png", dpi=300, bbox_inches="tight")

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
                        print(f"Warning: Could not generate boxplot for {effect}: {e}")

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
                print(f"Warning: Could not generate residual diagnostics: {e}")

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
                                print(f"Warning: Could not generate simple effect plots for {clean_name}: {e}")

        # Always plot boxplots for all effects
        for effect in self.means.keys():
            # Boxplot with letters
            if self.aov is not None:
                try:
                    fig = boxplot_letters(self.aov, factor=effect, ylabel=self.response, title=f"Boxplot for {effect}", show=False)
                    self.figures.append(fig)
                except Exception as e:
                    print(f"Warning: Could not generate boxplot for {effect}: {e}")

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

        # BLUP bar chart
        if self.blups is not None:
            fig, ax = plt.subplots(figsize=(8, 6))
            blups = self.blups.reset_index()
            ax.bar(blups.iloc[:, 0], blups.iloc[:, 1])
            ax.set_xlabel(blups.columns[0])
            ax.set_ylabel("BLUP")
            ax.set_title("Genotype BLUPs")
            plt.xticks(rotation=45)
            plt.tight_layout()
            self.figures.append(fig)

        # Variance component pie chart
        if self.variance_components is not None:
            fig, ax = plt.subplots(figsize=(6, 6))
            vc = self.variance_components
            if isinstance(vc, dict):
                labels = list(vc.keys())
                sizes = list(vc.values())
            else:
                # Assume it's a DataFrame or Series
                labels = vc.index.tolist()
                sizes = vc.values.tolist()
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

        # Genotype BLUP ranking
        if self.blups is not None:
            fig, ax = plt.subplots(figsize=(8, 6))
            blups = self.blups.sort_values(ascending=False)
            ax.bar(range(len(blups)), blups.values)
            ax.set_xticks(range(len(blups)))
            ax.set_xticklabels(blups.index, rotation=45)
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
            if self.model is not None:
                fig = ammi_biplot(self.model, show=False)
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

    # -----------------------------------
    # nice printing in console
    # -----------------------------------
    def __repr__(self):
        return self._full_report()

    def _full_report(self):
        """Generate full detailed analysis report"""
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

            anova_copy = self.anova.copy()
            anova_copy['Significance'] = anova_copy['p-value'].apply(
                lambda p: '***' if safe_float(p) < 0.001 else '**' if safe_float(p) < 0.01 else '*' if safe_float(p) < 0.05 else 'ns'
            )
            anova_copy['p-value'] = anova_copy['p-value'].apply(lambda p: '<0.001' if safe_float(p) < 0.001 else f'{safe_float(p):.3f}')

            # Reorder columns
            cols = ['DF', 'MS', 'F', 'p-value', 'Significance']
            anova_display = anova_copy[cols]

            # Convert to string with proper formatting and Source column
            table_str = anova_display.to_string()
            # Add Source header
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

        # Assumptions
        if self.assumptions:
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

        # Final recommendation
        if self.recommendation:
            report.append("\n" + "-" * 50)
            report.append("FINAL AGRONOMIC RECOMMENDATION")
            report.append("-" * 50)
            report.append(self.recommendation.strip())

        report.append("\n" + "=" * 50)

        return "\n".join(report)
