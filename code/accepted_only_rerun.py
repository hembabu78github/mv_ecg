"""Accepted-only monitor, recalibrated.  Run from mv_ecg/code on a machine that has the PTB-XL+ data
and has produced results/ext/scen_fold9.npz, scen_fold10.npz, scen_meta.pkl and results/models/*.pkl (run_ext.py).
Run on the supplied PTB-XL/PTB-XL+ data: variant all23 reproduces the MR rows of results/ext/monitor_det.csv (n=200) exactly;
run it first as a sanity check before the other variants.

Usage: MVECG_VARIANT=strict python accepted_only_rerun.py   (variants: all23, notrejected, strict)
  all23        : 23 label-free relations (current primary)  -> reproduction check
  notrejected  : drop the 6 lead dropouts the cardiologist rejected as invariances (II, III, aVF, V2, V3, V4)
  strict       : also drop the 'conditional' relations (NOISE x2, ST elevation, lead dropouts I, aVL, V1, V5, V6)
Check the operator names printed below against review/clinician_verdicts_deidentified.csv (not in the public repo)."""
import os, sys, re
variant = os.environ.get("MVECG_VARIANT", "notrejected")
import monitors as M                      # imports arrays; defines LF, run(), batch_stats()
names = M.ops
REJ = {f"MASK_LEAD_{l}" for l in ("II", "III", "aVF", "V2", "V3", "V4")}
COND = {"NOISE_x2", "ST_ELEV_+0.15mV_2LEADS", "MASK_LEAD_I", "MASK_LEAD_aVL", "MASK_LEAD_V1", "MASK_LEAD_V5", "MASK_LEAD_V6"}
print([ (j, n) for j, n in enumerate(names)])
drop = set() if variant == "all23" else REJ if variant == "notrejected" else REJ | COND
missing = [d for d in drop if d not in names]; assert not missing, f"operator names not found: {missing}"
M.LF = [j for j, o in enumerate(names) if not o.startswith("TERRITORY") and o not in drop]
print(variant, "relations used:", len(M.LF))
M.OUT = M.OUT + f"/accepted_{variant}"; os.makedirs(M.OUT, exist_ok=True)
import pandas as pd
D, F = M.run(200, 500)                   # recalibrates thresholds on fold-9 clean null (inside run) and evaluates on fold 10
D.to_csv(f"{M.OUT}/monitor_det.csv", index=False); F.to_csv(f"{M.OUT}/monitor_fa.csv", index=False)
mr = D[D.monitor == "MR"]
print("MR detection by group (mean over scenario-model cells):\n", mr.groupby("group").det.mean().round(3))
print("MR detected pairs (det>=0.5) among F1-F9 x 5 models:", int((mr[mr.family.str.match(r'^F[1-9]$')].det >= .5).sum()), "of 45")
fa = F[(F.monitor == "MR") & (F.scenario == "clean")]
print("MR clean false-alarm rate:\n", fa.groupby("pop").rate.mean().round(3))
