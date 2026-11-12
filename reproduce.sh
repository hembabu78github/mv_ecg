#!/usr/bin/env bash
# Regenerates the primary results from the PTB-XL / PTB-XL+ files in ./data and runs the checks.
# Order follows REPRODUCTION_REPORT.md. Outputs are written to ./results (existing files are overwritten;
# the released copies are kept in results_as_released_v1.0.0/ for comparison).
# Not included here (long-running, see README): run_rotation.py, run_benign*.py, cost_timing.py.
set -euo pipefail
export OMP_NUM_THREADS=1
export MVECG_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for f in ptbxl_database.csv scp_statements.csv feature_description.csv 12sl_features.csv ecgdeli_features.csv unig_features.csv; do
  [ -f "$MVECG_ROOT/data/$f" ] || { echo "Missing data/$f. See README.md (Data)." >&2; exit 1; }
done

cd "$MVECG_ROOT/code"
mkdir -p ../results/ext ../results/test

python3 train_models.py                       # fit the five frozen targets on folds 1-8
python3 run_ext.py     > ../results/ext/run_ext.log 2>&1   # scenario arrays
python3 monitors.py    > ../results/ext/monitors.log 2>&1  # monitors, four batch sizes (~15 min on 2 cores)
python3 run_experiments.py --split test --B 2000           # B=2000 reproduces the released bootstrap bounds
python3 analyze.py test
python3 verify.py test                                     # independent re-computation (53 checks)
python3 verify_ext.py                                      # extended re-computation (52 checks)

cd "$MVECG_ROOT"
python3 -m pytest tests -q                                 # 23 tests

cd "$MVECG_ROOT/code"
for v in all23 notrejected strict; do
  MVECG_VARIANT=$v python3 accepted_only_rerun.py
done
echo "Done."
