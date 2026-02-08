from .anova import interpret_anova
from .means import interpret_means


def generate_recommendation(anova_table, means_tables, design_name):
    """
    Create agronomic recommendation based on ANOVA + mean separation
    Works for main effects AND interactions of any order
    """
    highest_effect = None
    if highest_effect:
        report.append(
            f"Interpretation restricted to {highest_effect.replace(':',' × ')} "
            f"due to significant higher-order interaction."
        )

    report = []
    report.append(f"{design_name} INTERPRETATION\n")

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
            report.append(
                "Significant effects detected in: "
                + ", ".join(sig_terms)
                + "."
            )
        else:
            report.append("No significant treatment effects detected.")

    # ------------------------------------------------------
    # 2️⃣ Interpret mean separation
    # ------------------------------------------------------
    for effect, means in means_tables.items():

        best = means.iloc[0]

        # detect factor columns automatically
        factor_cols = [
            c for c in means.columns
            if c not in ["Mean", "Replications", "Group"]
        ]

        # Build treatment combination name
        if len(factor_cols) == 1:
            level_name = str(best[factor_cols[0]])
        else:
            level_name = " × ".join(str(best[c]) for c in factor_cols)

        report.append(
            f"For {effect.replace(':',' × ')}, "
            f"'{level_name}' produced the highest yield "
            f"({best['Mean']:.3f}) and belongs to the superior group "
            f"'{best['Group']}'."
        )

    # ------------------------------------------------------
    # 3️⃣ Final agronomic recommendation
    # ------------------------------------------------------
    last_effect = list(means_tables.keys())[-1]
    last_means = means_tables[last_effect]
    best = last_means.iloc[0]

    factor_cols = [
        c for c in last_means.columns
        if c not in ["Mean", "Replications", "Group"]
    ]

    final_level = " × ".join(str(best[c]) for c in factor_cols)

    report.append(
        "\nFINAL RECOMMENDATION:\n"
        f"Adopt treatment combination {final_level} "
        f"for maximizing {best['Mean']:.3f} yield under this experiment."
    )

    return "\n".join(report)
