# -*- coding: utf-8 -*-
"""ROUND 2-02 style polish: Abstract + roadmap sentence; keep locked numbers."""
from pathlib import Path

p = Path(r"I:\Projects\20260810-CE-QUAL-W2\06_PAPER\drafts\P1_GMD_draft_v2.md")
t = p.read_text(encoding="utf-8")

# Soften roadmap residual "likely objections"
t = t.replace(
    "discusses conditional comparability and likely objections (Sect. 6), and concludes (Sect. 7).",
    "discusses conditional comparability and interpretation limits (Sect. 6), and concludes (Sect. 7).",
)

# Contribution openers: slightly more Methods cadence (operationalize/define/demonstrate)
old_c1 = "**Contribution 1 (variable provenance).** We show that goodness-of-fit statistics can depend materially on the provenance of the evaluated output variable, and define and operationalize a CE-QUAL-W2-specific eight-field **variable provenance record (VPR)**"
new_c1 = "**Contribution 1 (variable provenance).** We demonstrate that goodness-of-fit statistics can depend materially on the provenance of the evaluated output variable, and we define and operationalize a CE-QUAL-W2-specific eight-field **variable provenance record (VPR)**"
if old_c1 in t:
    t = t.replace(old_c1, new_c1, 1)

old_c2 = "**Contribution 2 (control-state / gated outputs).** We demonstrate, for CE-QUAL-W2 controller-gated outputs, how **control state** changes the available evaluation object and therefore requires control-state provenance in the evaluation record when diagnostic or controller-specific outputs are conditionally available."
new_c2 = "**Contribution 2 (control-state / gated outputs).** For CE-QUAL-W2 controller-gated outputs, we show how **control state** changes the available evaluation object and therefore requires control-state provenance whenever diagnostic or controller-specific outputs are conditionally available."
if old_c2 in t:
    t = t.replace(old_c2, new_c2, 1)

# Abstract: light GMD cadence polish — open with assessment object; keep all numbers
old_abs_open = "In CE-QUAL-W2 evaluation practice, the interpretation and cross-study portability of reported goodness-of-fit are conditional on adequate documentation and alignment of variable provenance, controller state, and numerical-health context. Without reconstructable provenance, cross-site comparison of those numbers cannot generally be established from the reported metric alone."
new_abs_open = "This Methods paper assesses how reported goodness-of-fit for CE-QUAL-W2 applications should be interpreted when variable provenance, controller state, and numerical-health context are incompletely documented. Without reconstructable provenance, cross-site comparison of those numbers cannot generally be established from the reported metric alone."
if old_abs_open in t:
    t = t.replace(old_abs_open, new_abs_open, 1)

old_abs_close = "We operationalize a CE-QUAL-W2-specific evaluation-object contract in which reported goodness-of-fit is accompanied by VPR, control-state provenance, NHR, and a run-card—implemented in a minimal evaluator (`w2eval`) that writes cards from existing analysis files without rerunning the model. Without those reporting elements, the direct comparability of goodness-of-fit values across CE-QUAL-W2 applications cannot generally be established from the reported metric alone."
new_abs_close = "We therefore operationalize a CE-QUAL-W2-specific evaluation-object contract in which reported goodness-of-fit is accompanied by a variable provenance record (VPR), control-state provenance, a numerical health record (NHR), and a run-card, implemented in a minimal evaluator (`w2eval`) that writes cards from archived analysis records without rerunning the model. Without those reporting elements, the direct comparability of goodness-of-fit values across CE-QUAL-W2 applications cannot generally be established from the reported metric alone."
if old_abs_close in t:
    t = t.replace(old_abs_close, new_abs_close, 1)

p.write_text(t, encoding="utf-8")
print("style polish applied")
