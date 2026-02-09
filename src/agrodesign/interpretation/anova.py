def interpret_anova(anova_table, alpha=0.05):
    """
    Determine which effects truly matter scientifically
    """

    # find p column automatically
    pcol = None
    for c in ["PR(>F)", "p-value", "Pr>F", "P", "p"]:
        if c in anova_table.columns:
            pcol = c
            break

    if pcol is None:
        raise ValueError("No p-value column found")

    results = {}

    for effect, row in anova_table.iterrows():

        if str(effect).lower() in ["residual", "error"]:
            continue

        p = row[pcol]

        if p >= alpha:
            status = "ns"
        elif p >= 0.01:
            status = "sig"
        else:
            status = "hs"

        results[str(effect)] = status

    # Interaction priority rule
    interactions = [k for k in results if ":" in k and results[k] != "ns"]

    return {
        "effects": results,
        "interaction_dominant": len(interactions) > 0,
        "dominant_interactions": interactions
    }
