import re

# ------------------------------------------------------------
# Detect highest significant effect from ANOVA table
# ------------------------------------------------------------
def highest_significant_effect(anova_table, alpha=0.05):

    pcol = None
    for c in ["PR(>F)", "Pr>F", "p-value", "P", "p"]:
        if c in anova_table.columns:
            pcol = c
            break

    if pcol is None:
        return None

    significant = []

    for idx, row in anova_table.iterrows():

        name = str(idx)

        if "Residual" in name:
            continue

        pval = row[pcol]

        if pval is not None and pval <= alpha:
            significant.append(name)

    if not significant:
        return None

    # choose highest order interaction
    significant.sort(key=lambda x: x.count(":"), reverse=True)

    return significant[0]


# ------------------------------------------------------------
# Hierarchical filtering of effects
# ------------------------------------------------------------
def filter_effects_by_hierarchy(means_tables, highest_effect):

    if highest_effect is None:
        return means_tables

    highest_order = highest_effect.count(":")

    filtered = {}

    for effect, table in means_tables.items():

        order = effect.count(":")

        # keep only same order as highest
        if order == highest_order:
            filtered[effect] = table

    return filtered
