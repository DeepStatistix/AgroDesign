import numpy as np

def interpret_mixed(summary_table, blup_table):
    """
    Scientific interpretation of mixed model
    """

    report = []
    report.append("MIXED MODEL INTERPRETATION\n")

    # ----------------------------------
    # Variance components
    # ----------------------------------
    var_random = summary_table.loc[summary_table["Type"].str.contains("Random"), "Variance"].sum()
    var_error = summary_table.loc[summary_table["Type"] == "Error", "Variance"].sum()

    if var_random > var_error:
        report.append("Random effect variance exceeds residual variance indicating strong environmental heterogeneity.")
    else:
        report.append("Residual variance exceeds random variance indicating relatively uniform experimental conditions.")

    precision = var_error / (var_error + var_random)

    if precision < 0.3:
        report.append("The experiment showed high precision.")
    elif precision < 0.6:
        report.append("The experiment showed moderate precision.")
    else:
        report.append("The experiment showed low precision.")

    # ----------------------------------
    # BLUP ranking
    # ----------------------------------
    best = blup_table.iloc[0]
    worst = blup_table.iloc[-1]

    report.append(
        f"Level '{best.iloc[0]}' had the highest predicted performance (BLUP = {best['BLUP']:.3f})."
    )

    report.append(
        f"Level '{worst.iloc[0]}' showed the lowest performance (BLUP = {worst['BLUP']:.3f})."
    )

    return "\n".join(report)
