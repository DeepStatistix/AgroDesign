import numpy as np

def interpret_mixed(summary_table, blup_table):
    """
    Agronomic interpretation of mixed model
    """

    # Get random effect name
    random_effect = summary_table.loc[summary_table["Type"].str.contains("Random"), "Effect"].iloc[0]

    # BLUP ranking
    best = blup_table.iloc[0]
    worst = blup_table.iloc[-1]

    best_level = best.iloc[0]
    worst_level = worst.iloc[0]
    best_blup = best['BLUP']
    worst_blup = worst['BLUP']

    # Calculate improvement percentage
    if abs(worst_blup) > 0:
        percentage = round((best_blup - worst_blup) / abs(worst_blup) * 100)
    else:
        percentage = 0

    report = f"After adjusting for {random_effect.lower()}-to-{random_effect.lower()} variability,\ntreatment {best_level} consistently produced superior yield.\n\nFarmers should adopt treatment {best_level} across environments.\n\nExpected improvement: +{percentage}% compared to {worst_level}"

    return report
