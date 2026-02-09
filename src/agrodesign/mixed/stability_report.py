import pandas as pd


class StabilityReport:
    """
    Combines AMMI, Finlay-Wilkinson, and Eberhart-Russell
    into one breeder-friendly recommendation table
    """

    def __init__(self, ammi, fw, er):
        self.ammi = ammi
        self.fw = fw
        self.er = er

    # --------------------------------------------------
    # Build report
    # --------------------------------------------------
    def build(self):

        # Mean yield
        means = self.ammi.means.mean(axis=1).rename("MeanYield")

        # AMMI stability
        asv = self.ammi.stability().set_index("Genotype")["ASV"]

        # FW slope
        fw = self.fw.fit().set_index("Genotype")

        # ER stats
        er = self.er.fit().set_index("Genotype")

        report = pd.concat([means, asv, fw, er], axis=1)
        report = report.loc[:, ~report.columns.duplicated()]

        # ---- thresholds computed BEFORE recommendation ----
        self.asv_median = report["ASV"].median()
        self.s2di_median = report["S2di"].median()

        report["Recommendation"] = report.apply(self._recommend, axis=1)

        self.report = report.sort_values("MeanYield", ascending=False)
        return self.report

    # --------------------------------------------------
    # Decision logic
    # --------------------------------------------------
    def _recommend(self, row):

        stable = row["ASV"] <= self.asv_median
        wide = abs(row["bi"] - 1) < 0.1 and row["S2di"] <= self.s2di_median

        if stable and wide:
            return "Ideal genotype (widely adapted)"

        if row["bi"] > 1.1:
            return "High-input environment recommendation"

        if row["bi"] < 0.9:
            return "Stress-prone area recommendation"

        return "Specific adaptation"

    # --------------------------------------------------
    # Best genotype
    # --------------------------------------------------
    def best(self):

        if not hasattr(self, "report"):
            self.build()

        return self.report.iloc[0]
