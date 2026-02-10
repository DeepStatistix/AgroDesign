class AgroCollection:
    """
    Container for multiple AgroResult objects
    (grouped analysis or multi-response analysis)
    """

    def __init__(self, results, grouping_name=None):
        self.results = results  # dict: level -> AgroResult
        self.grouping_name = grouping_name

    # ---------------------------
    # Snapshot view (result)
    # ---------------------------
    def __repr__(self):

        lines = ["AgroResult (Collection)"]

        if self.grouping_name:
            levels = ", ".join(str(k) for k in self.results.keys())
            lines.append(f"Groups analysed: {len(self.results)} ({levels})")

        # find consistent best across nested results
        best_counts = {}

        for level, res in self.results.items():

            text = repr(res).split("\n")

            for line in text:
                if "Best " in line and ":" in line:
                    best = line.split(":",1)[1].strip()
                    best_counts[best] = best_counts.get(best, 0) + 1

        if best_counts:
            overall_best = max(best_counts, key=best_counts.get)
            lines.append(f"Consistent best: {overall_best}")

        # overall best across traits
        try:
            overall = self.overall_best()
            if overall:
                best, _ = overall
                lines.append(f"Overall best: {best}")
        except:
            pass

        return "\n".join(lines)

    def _extract_means(self, res):
        if not hasattr(res, "means") or not res.means:
            return None

        df = list(res.means.values())[0].copy()
        factor_cols = [c for c in df.columns if c not in ["Mean", "Group"]]

        if not factor_cols:
            return None

        if len(factor_cols) == 1:
            return df.set_index(factor_cols[0])["Mean"]

        df["__combo__"] = df[factor_cols].astype(str).agg("×".join, axis=1)
        return df.set_index("__combo__")["Mean"]


    def _collect_series(self, obj):
        """Recursively collect mean series from nested collections"""
        series_list = []

        if hasattr(obj, "results"):
            for sub in obj.results.values():
                series_list.extend(self._collect_series(sub))
        else:
            s = self._extract_means(obj)
            if s is not None:
                series_list.append(s)

        return series_list


    def overall_best(self):
        """
        Compute overall best treatment/genotype across multiple results
        using average rank across traits/groups
        """

        import pandas as pd

        ranking_tables = []

        for name, res in self.results.items():

            series_list = self._collect_series(res)

            if not series_list:
                continue

            mean_series = pd.concat(series_list, axis=1).mean(axis=1)

            ranks = mean_series.rank(ascending=False, method="average")
            ranking_tables.append(ranks)

        if not ranking_tables:
            return None

        combined = pd.concat(ranking_tables, axis=1)
        combined["AverageRank"] = combined.mean(axis=1, skipna=True)
        combined["TraitCount"] = combined.count(axis=1)
        combined = combined.sort_values(["AverageRank","TraitCount"], ascending=[True,False])
        best = combined.index[0]

        return best, combined.sort_values("AverageRank")

    # ---------------------------
    # Full report (print)
    # ---------------------------
    def __str__(self):

        parts = ["="*60, "GROUPED ANALYSIS REPORT", "="*60]

        label = self.grouping_name or "Group"
        for level, res in self.results.items():
            parts.append(f"\n### {label} = {level}")
            parts.append(str(res))


        return "\n".join(parts)

    # ---------------------------
    # Agronomic interpretation
    # ---------------------------
    def summary(self):
        """
        Print combined agronomic interpretation
        """

        print("\n================ COMBINED INTERPRETATION ================\n")

        # print individual summaries first
        for level, res in self.results.items():

            if hasattr(res, "results"):
                print(f"\n### {self.grouping_name} = {level}")
                res.summary()
            else:
                label = self.grouping_name or "Group"
                print(f"--- {label} = {level} ---")
                res.summary()


        # -------------------------------------------------
        # overall recommendation
        # -------------------------------------------------
        try:
            overall = self.overall_best()
            if overall:
                best, ranking = overall

                print("OVERALL RECOMMENDATION")
                print("--------------------------------")
                print(f"Best overall performer: {best}")

                # consistency = lowest variance rank
                import pandas as pd
                rank_cols = [c for c in ranking.columns if c not in ["AverageRank","TraitCount"]]
                rank_var = ranking[rank_cols].var(axis=1)
                most_consistent = rank_var.idxmin()

                print(f"Most consistent performer: {most_consistent}")

        except Exception as e:
            print("Warning: combined ranking export failed:", e)
        print("\n=========================================================\n")

    # ---------------------------
    # Plot all groups
    # ---------------------------
    def plot(self):

        for level, res in self.results.items():
            label = self.grouping_name or "Group"
            print(f"\n--- Plots for {label} = {level} ---")
            if hasattr(res, "plot"):
                res.plot()

    # ---------------------------
    # Export grouped folders
    # ---------------------------
    def export(self, folder):
        """
        Export grouped/multi-trait results including combined ranking
        """

        import os
        os.makedirs(folder, exist_ok=True)

        # export individual results
        for level, res in self.results.items():
            subfolder = os.path.join(folder, str(level))
            if hasattr(res, "export"):
                res.export(subfolder)

        # -----------------------------------------
        # export combined ranking
        # -----------------------------------------
        try:
            overall = self.overall_best()
            if overall:
                best, ranking = overall

                tables_dir = os.path.join(folder, "tables")
                os.makedirs(tables_dir, exist_ok=True)
                ranking = ranking.dropna()
                if ranking.empty:
                    return None

                ranking.to_csv(os.path.join(tables_dir, "combined_ranking.csv"))

                # also write summary txt
                with open(os.path.join(folder, "overall_recommendation.txt"), "w") as f:
                    f.write("OVERALL RECOMMENDATION\n")
                    f.write("----------------------\n")
                    f.write(f"Best overall performer: {best}\n")

        except Exception:
            pass
