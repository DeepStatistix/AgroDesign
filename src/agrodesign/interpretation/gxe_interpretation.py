def interpret_gxe(anova, vc, h2, blup, stability=None, mega_environments=None):
    """
    Plant breeding interpretation of MET trial
    """

    report = []
    report.append("GENOTYPE × ENVIRONMENT INTERPRETATION\n")

    # ----------------------------
    # ANOVA significance
    # ----------------------------
    if anova.loc["C(Genotype)", "p-value"] < 0.05:
        report.append("Significant genotypic differences detected indicating genetic variability.")

    if anova.loc["C(Environment)", "p-value"] < 0.05:
        report.append("Environments differed significantly indicating strong environmental influence.")

    if anova.loc["C(Genotype):C(Environment)", "p-value"] < 0.05:
        report.append("Significant G×E interaction detected indicating genotype instability across environments.")
    else:
        report.append("Non-significant G×E interaction indicating stable genotype performance.")

    # ----------------------------
    # Heritability
    # ----------------------------
    if h2 > 0.7:
        report.append(f"High heritability (H²={h2:.2f}) suggesting effective selection.")
    elif h2 > 0.4:
        report.append(f"Moderate heritability (H²={h2:.2f}).")
    else:
        report.append(f"Low heritability (H²={h2:.2f}) suggesting strong environmental influence.")

    # ----------------------------
    # Best genotype
    # ----------------------------
    best = blup.iloc[0]
    report.append(
        f"Genotype '{best['Genotype']}' showed highest predicted performance (BLUP={best['BLUP']:.3f}) and is recommended."
    )

    return "\n".join(report)
