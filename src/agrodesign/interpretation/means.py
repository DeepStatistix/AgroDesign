import pandas as pd

def interpret_means(means: pd.DataFrame):
    """
    Interpret mean separation results (LSD/Tukey/DMRT CLD)

    Returns agronomic interpretation dictionary
    """

    if "Group" not in means.columns:
        raise ValueError("Means table must contain 'Group' column")

    means = means.sort_values("Mean", ascending=False).reset_index(drop=True)

    # ---------------- Best treatment ----------------
    best = means.iloc[0]
    best_letters = set(str(best["Group"]))

    # Treatments statistically equal to best
    equal_mask = means["Group"].apply(lambda g: len(set(str(g)) & best_letters) > 0)
    competitive = means[equal_mask]

    # ---------------- Worst treatment ----------------
    worst = means.iloc[-1]

    # % improvement
    if worst["Mean"] == 0:
        gain = None
    else:
        gain = (best["Mean"] - worst["Mean"]) / worst["Mean"] * 100

    return {
        "best_row": best,
        "competitive_rows": competitive,
        "worst_row": worst,
        "gain_percent": gain,
        "n_superior": len(competitive)
    }
