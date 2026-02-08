# TODO: Fix Missing Interaction Line Plots in result.plot()

## Plan Breakdown
1. Modify `_plot_factorial_split` method in `agrodesign/core/result.py`:
   - Remove dependency on `highest_significant_effect` for interaction plotting.
   - Loop through ANOVA table to identify all significant effects (p-value <= 0.05).
   - For each significant two-way interaction (exactly one ":"), plot `interaction_plot`.
   - For each significant three-way or higher interaction (two or more ":"), use `simple_effect_plot` to generate conditional interaction plots.
   - Keep existing boxplots for all effects.
   - Clean effect names by removing "C(" and ")" before processing.

## Progress
- [ ] Step 1: Edit `_plot_factorial_split` method to implement the changes.
