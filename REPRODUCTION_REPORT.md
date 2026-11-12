# Reproduction report (run on the supplied PTB-XL, PTB-XL+ and cardiologist-verdict files; 2 CPU cores, same pinned package versions)

| Step | Command | Outcome |
|---|---|---|
| Cohort | `build_dataset()` | 11,603 records (2,532 MI), 2,065 inputs (782 + 531 + 748 + 4), fold 10 = 1,168 records / 256 MI / 1,057 patients; record set identical to `cohort_ids.csv` |
| Models and scenario arrays | `train_models.py`, `run_ext.py` | regenerated (`results/models`, `results/ext/scen_*.npz`) |
| Monitors, all four batch sizes | `monitors.py` (15 min) | `monitor_det.csv` (6,400 rows) and `monitor_fa.csv` (2,000 rows) **identical** to the released files (max abs difference 0.0) |
| Primary test split | `run_experiments.py --split test --B 2000`, `analyze.py test` | `fault_ops`, `fault_summary`, `perf`, `benign`, `clean_mr`, `benign_ops`, `fault_summary_gated`, `benign_gated` **identical** to the released files. (A first run with the default B=1000 gave the same detections and point estimates but different bootstrap bounds: use B=2000.) |
| Independent re-computation | `verify.py test` | ALL CHECKS PASSED (53 checks) |
| Extended re-computation | `verify_ext.py` | ALL CHECKS PASSED (52 checks) |
| Unit tests | `pytest tests` | 23 passed |
| Accepted-only recalibrated monitor (new) | `accepted_only_rerun.py`, variants `all23`, `notrejected` (17 relations), `strict` (10 relations) | `all23` reproduces the released MR rows exactly. Results in `results/ext/accepted_*` and the table below |

## Accepted-only recalibrated metamorphic monitor (n = 200, mean over scenario-model cells, %)
| Variant | Relations | Development | Held-out | Active unit | Joint | F1 / F2 (dormant units) | Clean false alarm | Healthy-subgroup false alarm |
|---|---|---|---|---|---|---|---|---|
| all23 (primary) | 23 | 44.1 | 58.8 | 72.8 | 100 | 100 / 100 | 5.6 | 26.7 |
| notrejected | 17 | 42.6 | 57.4 | 72.5 | 100 | 100 / 100 | 4.8 | 26.1 |
| strict | 10 | 42.3 | 58.2 | 72.7 | 100 | 100 / 100 | 5.2 | 26.1 |

The cardiologist verdicts used are in `review/clinician_verdicts_deidentified.csv` (rejected: lead dropouts II, III, aVF, V2, V3, V4; conditional: noise x2, ST elevation, unrelated-lead masking, lead dropouts I, aVL, V1, V5, V6). The two territory operators need the true label and are excluded in all variants.

## Not re-run
Ten-fold rotation (`run_rotation.py`), benign retraining on 100 replicates (`run_benign*.py`), cost/timing, decision metrics and abstention scripts were not re-run; their released CSVs are included unchanged in `results/ext`. The released outputs of the first group of scripts were regenerated and matched exactly, so these are expected to reproduce but have not been checked.

## Notes
- Raw PTB-XL / PTB-XL+ files are not copied here (public on PhysioNet). Place them in `data/` (`ptbxl_database.csv`, `scp_statements.csv`, `feature_description.csv`, `12sl_features.csv`, `ecgdeli_features.csv`, `unig_features.csv`).
- `results_as_released_v1.0.0/` holds the files as shipped in tag v1.0.0 for comparison.
