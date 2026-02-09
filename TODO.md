# TODO: Implement AgroDesign Behaviors

## 1. Modify Experiment.run() for console/library mode detection
- [ ] Import sys in experiment.py
- [ ] Set self.verbose = sys.stdout.isatty() in run()
- [ ] Change print(result._full_report()) to self._print(result._full_report()) in _run_doe

## 2. Modify AgroResult.__repr__ for short snapshot
- [ ] Change __repr__ to return short scientific snapshot
- [ ] Include design, response, significant factors, best treatment, expected yield

## 3. Update AgroResult.plot() for save_dir
- [ ] Change save parameter to save_dir
- [ ] If save_dir provided, save plots there without showing

## 4. Add AgroResult.export() method
- [ ] Create export(folder) to make tables/, plots/, report.txt
- [ ] Save ANOVA table as CSV
- [ ] Save means tables as CSV
- [ ] Save all figures as PNG
- [ ] Save full report as TXT

## 5. Test behaviors
- [ ] Test console mode: run() prints full report
- [ ] Test library mode: result = run() silent, result shows short snapshot
- [ ] Test result.summary() for agronomic interpretation
- [ ] Test result.plot() and result.plot(save_dir="plots")
- [ ] Test result.export("folder")
