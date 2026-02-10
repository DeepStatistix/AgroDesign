# Changelog

All notable changes to AgroDesign are documented here.

This project follows semantic versioning for reproducible research.

---

## [0.6.0] — Stable Research Release

This version is frozen for reproducible analysis and citation.

It establishes the complete statistical workflow and unified user interface.

---

### Statistical Core (validated)
- CRD, RCBD, factorial, split-plot, split–split ANOVA
- Design-aware LSD and Tukey HSD
- Automatic error-term selection
- Interaction-aware mean separation
- Mixed model (BLUP) analysis
- Multi-environment G×E analysis (AMMI, FW, ER stability)
- Assumption diagnostics (normality + homogeneity)
- Journal-ready plots and tables
- Full pytest coverage for statistical engines

---

### Phase 1 — Usability Framework
Major interface expansion introducing a universal experiment workflow.

New capabilities:
- Grouped analysis (`.by()`)
- Multi-response analysis (multiple traits)
- Nested grouped + multi-trait support
- Combined ranking (average rank decision system)
- Publication-ready export including `combined_ranking.csv`
- Snapshot vs full report printing behavior
- Automatic invalid-design detection (e.g., grouped G×E without replication)
- Consistent behavior across CRD, RCBD, factorial, split-plot, mixed model and G×E

AgroDesign now functions as a unified experimental analysis interface
rather than separate statistical tools.

---

### Reproducibility guarantee
Results produced with v0.6.0 will not change in future minor versions.
All algorithmic behavior is frozen for scientific citation.

Future versions will extend features but not modify existing calculations.
