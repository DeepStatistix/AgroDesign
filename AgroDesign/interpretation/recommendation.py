from .anova import interpret_anova
from .means import interpret_means
from .hierarchy import highest_significant_effect, filter_effects_by_hierarchy


def generate_recommendation(anova_table, means_tables, design_name):
    """
    Create agronomic recommendation based on ANOVA + mean separation
    Follows hierarchical ANOVA interpretation: recommend combinations only if interaction is significant.
    """
    highest_effect = highest_significant_effect(anova_table)
    report = []
    report.append(f"{design_name} INTERPRETATION\n")

    if highest_effect:
        report.append(
            f"Interpretation restricted to {highest_effect.replace(':',' × ')} "
            f"due to significant effect."
        )

    # ------------------------------------------------------
    # 1️⃣ Interpret ANOVA significance
    # ------------------------------------------------------
    pcol = None
    for c in ["p-value", "PR(>F)", "Pr>F", "P", "p"]:
        if c in anova_table.columns:
            pcol = c
            break

    if pcol:
        sig_terms = []
        for idx, row in anova_table.iterrows():
            if str(idx).lower() in ["residual", "error"]:
                continue
            if row[pcol] < 0.05:
                sig_terms.append(str(idx))

        if sig_terms:
            # Extract factors from contrasts like C(A) -> A
            sig_factors = [s.replace('C(', '').replace(')', '') for s in sig_terms if 'C(' in s]
            if not sig_factors:
                sig_factors = sig_terms
            report.append(
                "Significant factors : "
                + ", ".join(sig_factors)
                + "."
            )
        else:
            report.append("No significant treatment effects detected.")

    # ------------------------------------------------------
    # 2️⃣ Best combination and recommendation
    # ------------------------------------------------------
    # Filter means tables by hierarchy
    filtered_means = filter_effects_by_hierarchy(means_tables, highest_effect)

    if highest_effect and ":" in highest_effect:
        # Recommend best combination from the highest order interaction
        interaction_key = highest_effect
        if interaction_key in filtered_means:
            best_means = filtered_means[interaction_key]
            best = best_means.iloc[0]

            factor_cols = [
                c for c in best_means.columns
                if c not in ["Mean", "Replications", "Group"]
            ]

            final_level = " × ".join(str(best[c]) for c in factor_cols)

            report.append(f"Best combination    : {final_level}")
            report.append(f"Expected mean       : {best['Mean']:.2f}")
            report.append(f"Recommendation      : Adopt {final_level}")
    else:
        # No interaction significant: recommend best levels independently
        report.append("No interaction detected. Factors act independently.")
        report.append("Best levels:")

        # Find best level for each main effect
        main_effects = {k: v for k, v in filtered_means.items() if ":" not in k}
        best_levels = []
        for effect, means_df in main_effects.items():
            if hasattr(means_df, 'columns'):  # DataFrame
                best_row = means_df.iloc[0]
                factor_cols = [c for c in means_df.columns if c not in ["Mean", "Replications", "Group"]]
                if factor_cols:
                    level = str(best_row[factor_cols[0]])
                    best_levels.append(level)
            else:  # Series
                factor_cols = [idx for idx in means_df.index if idx not in ["Mean", "Replications", "Group"]]
                if factor_cols:
                    level = str(means_df[factor_cols[0]])
                    best_levels.append(level)

        if best_levels:
            report.append(", ".join(best_levels) + ".")

        # For factorial, recommend the best combination from the full means
        if "FACTORIAL" in design_name:
            # Find the highest order interaction in means_tables
            interaction_keys = [k for k in means_tables.keys() if ":" in k]
            if interaction_keys:
                highest_order = max(interaction_keys, key=lambda x: x.count(":"))
                best_means = means_tables[highest_order]
                best = best_means.iloc[0]
                factor_cols = [
                    c for c in best_means.columns
                    if c not in ["Mean", "Replications", "Group"]
                ]
                final_level = " × ".join(str(best[c]) for c in factor_cols)
                report.append(f"Best combination    : {final_level}")
                report.append(f"Expected mean       : {best['Mean']:.2f}")
                report.append(f"Recommendation      : Adopt {final_level} for maximizing yield")
        else:
            # Do NOT compute or print expected combination mean
            report.append("No specific treatment combination is statistically superior.")

    return "\n".join(report)
