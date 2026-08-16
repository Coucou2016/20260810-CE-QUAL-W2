# -*- coding: utf-8 -*-
"""Audit P1 draft key numbers against analysis JSON."""
import json
import pathlib
import re

root = pathlib.Path(r"I:\Projects\20260810-CE-QUAL-W2\06_PAPER")
w3 = json.loads((root / "analysis/w3_tdgta_off_metrics.json").read_text(encoding="utf-8"))
w5 = json.loads((root / "analysis/w5_lit_audit_summary.json").read_text(encoding="utf-8"))
nhr = json.loads((root / "analysis/nhr_dlt_scan.json").read_text(encoding="utf-8"))
w4 = json.loads((root / "analysis/w4_cciw_vs_dart.json").read_text(encoding="utf-8"))
w7 = json.loads((root / "analysis/w7_columbia_sod_vs_almeida.json").read_text(encoding="utf-8"))
draft_path = root / "drafts/P1_GMD_draft_v2.md"
if not draft_path.exists():
    draft_path = root / "drafts/P1_GMD_draft_v1.md"
draft_raw = draft_path.read_text(encoding="utf-8")
# Normalize Unicode minus / en-dash so ASCII token searches match the draft.
draft = draft_raw.replace("\u2212", "-").replace("\u2013", "-").replace("\u2014", "-")

checks = []


def chk(name, ok, expected, note=""):
    checks.append({"name": name, "ok": bool(ok), "expected": expected, "note": note})


by = {}
for m in w3["metrics"]:
    by[(m.get("run"), m.get("caliber"))] = m

for cal, nse, r2 in [("A", -2.8044, 0.5082), ("B", 0.5, 0.5332), ("C", -2.7516, 0.5512)]:
    m = by[("ON", cal)]
    chk(f"ON {cal} NSE", abs(m["nse"] - nse) < 1e-4, nse, f"json={m['nse']}")
    chk(f"ON {cal} R2", abs(m["r2"] - r2) < 1e-4, r2, f"json={m['r2']}")
    token = "+0.5000" if cal == "B" else str(nse)
    chk(f"draft mentions ON {cal} NSE token", token in draft or str(nse) in draft, token)

mb = by[("ON", "B")]
chk("ON B sim_max", abs(mb["sim_max"] - 120.09) < 1e-6, 120.09, f"json={mb['sim_max']}")
off_b = by[("OFF", "B")]
chk(
    "OFF B absent",
    off_b.get("status") == "file_absent" or off_b.get("available") is False,
    "file_absent",
    str(off_b.get("status")),
)

chk("W5 VPR yes", w5["counts"]["vpr_reconstruct"]["yes"] == 2, 2)
chk("W5 VPR pct", abs(w5["counts"]["vpr_reconstruct_yes_pct"] - 5.3) < 1e-9, 5.3)
chk(
    "W5 only_r2 pct of r2",
    abs(w5["counts"]["only_r2_not_nse_pct_of_r2_true"] - 81.8) < 1e-9,
    81.8,
)
chk("draft has 2/38 or 2 of 38", ("2/38" in draft) or ("2 of 38" in draft), True)

counts = {}
for j in nhr["jobs"]:
    if j.get("dltinter") == "ON":
        counts[j["dltmax_window_30_40"]] = j["neg_surface_thickness_count"]
chk("NHR ON 20", counts.get(20) == 5, 5)
chk("NHR ON 50", counts.get(50) == 4, 4)
chk("NHR ON 100", counts.get(100) == 1, 1)
chk("NHR ON 200", counts.get(200) == 5, 5)
chk("draft 5/4/1/5", "5/4/1/5" in draft, True)

off_counts = {}
for j in nhr["jobs"]:
    if j.get("dltinter") == "OFF":
        off_counts[j["dltmax_window_30_40"]] = j["neg_surface_thickness_count"]
chk("NHR OFF all zero", all(v == 0 for v in off_counts.values()) and len(off_counts) == 4, "0/0/0/0")


def find_lib(o):
    if isinstance(o, dict):
        if o.get("n") == 17805 and "match_rate_abs_le_0p051" in o:
            return o
        for vv in o.values():
            r = find_lib(vv)
            if r:
                return r
    elif isinstance(o, list):
        for i in o:
            r = find_lib(i)
            if r:
                return r
    return None


lib = find_lib(w4)
chk("DART n=17805", lib is not None and lib["n"] == 17805, 17805)
chk("DART mae", lib is not None and abs(lib["mae"] - 0.026537) < 1e-6, 0.026537)
chk(
    "DART match_rate",
    lib is not None and abs(lib["match_rate_abs_le_0p051"] - 0.994945) < 1e-6,
    0.994945,
)
chk("draft DART mae 0.026537", "0.026537" in draft, True)
chk("draft match 0.994945", "0.994945" in draft, True)
chk("OOS computed_nse false", w4["out_of_sample"]["computed_nse"] is False, False)

sp = w4["spill_comparison_2011"]
chk("QGT vs DART r", abs(sp["qgt_vs_dart_spill_kcfs"]["r"] - 0.868638) < 1e-6, 0.868638)
realloc = sp["spill_realloc_days"]
chk("realloc mean dart", abs(realloc["mean_dart_spill_kcfs"] - 173.8573) < 1e-4, 173.8573)
chk("realloc mean tdgta", abs(realloc["mean_tdgta_spill_kcfs"] - 39.2308) < 1e-4, 39.2308)
chk("realloc r", abs(realloc["r"] - (-0.596447)) < 1e-6, -0.596447)
chk("draft spill means", ("173.8573" in draft) and ("39.2308" in draft), True)

sod = w7.get("columbia_wet_instantaneous") or w7.get("wet_instantaneous") or {}
# tolerate alternate keys
if not sod:
    for k, v in w7.items():
        if isinstance(v, dict) and v.get("n") == 1081 and "frac_in_0.5_3.0" in v:
            sod = v
            break
chk("SOD n", sod.get("n") == 1081, 1081, str(sod.get("n")))
chk("SOD mean", abs(sod.get("mean", 0) - 0.8762) < 1e-4, 0.8762)
chk("SOD frac", abs(sod.get("frac_in_0.5_3.0", 0) - 0.8955) < 1e-4, 0.8955)
chk("draft SOD 0.8955", "0.8955" in draft, True)

# Affirmative forbidden wording only. Allowed: "we do not claim..." and
# "drops two sentences: that the physical TDG variable is deleted...".
bad_delete = False
for m in re.finditer(r".{0,120}physical (TDG )?variable (was |is )?deleted.{0,40}", draft):
    chunk = re.sub(r"[*_`]", "", m.group(0).lower())
    if any(
        x in chunk
        for x in ("not claim", "do not", "dont", "drops", "drop ", "refused", "downgrad")
    ):
        continue
    bad_delete = True
    print("DEBUG bad_delete chunk:", chunk[:200])
chk("no affirmative 'physical variable deleted'", not bad_delete, "absent")
chk("forbidden absent: 减小时间步更不稳", "减小时间步更不稳" not in draft_raw, "absent")

chk("draft DeGray 0.9027/-0.5855", ("0.9027" in draft) and ("-0.5855" in draft), True)
chk("draft Columbia 0.6505/-1.4821", ("0.6505" in draft) and ("-1.4821" in draft), True)

n_pass = sum(1 for c in checks if c["ok"])
n_fail = sum(1 for c in checks if not c["ok"])
print(f"PASS={n_pass} FAIL={n_fail} TOTAL={len(checks)}")
for c in checks:
    if not c["ok"]:
        print("FAIL", c)

lines = [
    "# P1 number audit 20260816",
    "",
    f"Authority: `06_PAPER/analysis/*.json`. Draft: `{draft_path.relative_to(root).as_posix()}`.",
    "",
    f"Checks: {len(checks)}; **PASS={n_pass}**; **FAIL={n_fail}**.",
    "",
    "| Check | OK | Expected | Note |",
    "|---|---|---|---|",
]
for c in checks:
    lines.append(
        f"| {c['name']} | {'PASS' if c['ok'] else 'FAIL'} | {c['expected']} | {c['note']} |"
    )
lines += [
    "",
    "Script: `06_PAPER/notes/_audit_p1_numbers_20260816.py`. No W2 rerun. No unit tests in repo.",
]
out = root / "notes/P1_number_audit_20260816.md"
out.write_text("\n".join(lines), encoding="utf-8")
print("wrote", out)
