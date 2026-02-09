import pandas as pd
from itertools import product

from agrodesign.analysis.anova import Anova
from agrodesign.mean_separation.lsd import LSD
from agrodesign.mean_separation.tukey import TukeyHSD
from agrodesign.mean_separation.dmrt import DMRT


def simple_effects(aov, effect_factors, method="tukey", alpha=0.05):
    """
    Perform simple effect analysis when interaction is significant.

    Example:
        interaction A×B×C significant

    Analyze:
        A at each (B,C)
        B at each (A,C)
        C at each (A,B)

    Returns:
        str: Formatted report text
    """

    df = aov.data.copy()
    response = aov.response

    report_lines = []
    report_lines.append("\n========= SIMPLE EFFECT ANALYSIS =========")

    for target in effect_factors:

        conditioning = [f for f in effect_factors if f != target]

        report_lines.append(f"\n--- Effect of {target} within {' × '.join(conditioning)} ---")

        # unique combinations of conditioning factors
        levels = [df[c].unique() for c in conditioning]

        for comb in product(*levels):

            subset = df.copy()

            label = []
            for c, val in zip(conditioning, comb):
                subset = subset[subset[c] == val]
                label.append(f"{c}={val}")

            if subset.empty:
                continue

            report_lines.append("\nCondition: " + ", ".join(label))

            sub_aov = Anova(subset, response)
            sub_aov.factorial([target])

            sub_aov.factorial_means(target)

            effect_name = target

            if method == "lsd":
                sep = LSD(sub_aov, effect=effect_name, alpha=alpha)
            elif method == "tukey":
                sep = TukeyHSD(sub_aov, effect=effect_name, alpha=alpha)
            else:
                sep = DMRT(sub_aov, alpha=alpha)

            means = sep.test()
            report_lines.append(means.round(4).to_string())

    return "\n".join(report_lines)
