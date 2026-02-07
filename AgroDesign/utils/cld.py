import string
import pandas as pd


def compact_letter_display(*args):
    """
    Compact Letter Display (CLD)

    Supports BOTH:
    1) Old style: compact_letter_display(diff_matrix)
    2) New style: compact_letter_display(means, sig_matrix)

    Returns
    -------
    dict {treatment: letters}
    """

    # -------------------------------------------------
    # Detect mode
    # -------------------------------------------------
    if len(args) == 1:
        # OLD MODE (only significance matrix provided)
        sig_matrix = args[0]
        treatments = list(sig_matrix.index)
        means = pd.Series(range(len(treatments)), index=treatments)  # fake ordering

    elif len(args) == 2:
        # NEW MODE (means + significance matrix)
        means, sig_matrix = args
        treatments = list(means.index)

    else:
        raise TypeError("compact_letter_display expects 1 or 2 arguments")

    # -------------------------------------------------
    # CLD algorithm
    # -------------------------------------------------
    letters = {t: "" for t in treatments}
    alphabet = list(string.ascii_lowercase)
    groups = []

    for t in treatments:

        placed = False

        for g in groups:
            conflict = any(sig_matrix.loc[t, member] for member in g)

            if not conflict:
                g.add(t)
                placed = True
                break

        if not placed:
            groups.append(set([t]))

    # assign letters
    for i, g in enumerate(groups):
        for t in g:
            letters[t] += alphabet[i]

    return letters
