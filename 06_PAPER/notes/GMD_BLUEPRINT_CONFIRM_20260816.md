# GMD blueprint confirmation — Cursor judgment (2026-08-16)

**Advisor chat:** https://chatgpt.com/c/6a812957-b108-83ea-b941-617f36744d76  
**Raw log:** `chatgpt_briefs/gmd_blueprint_confirm_raw.md`  
**Conversation status:** **Succeeded** (existing literature-architecture thread reused; web search ON; no login/CAPTCHA; no attachments).

---

## Verdict on advisor Q1–Q4

| Q | Advisor | Cursor | Decision |
|---|---|---|---|
| 1 Venue | **KEEP** Methods for assessment; soft fallback Model evaluation if draft drifts; do **not** switch to EMS now | Agree. Assessment object = evaluation workflow; Almeida is the contrasting *model evaluation* precedent | **Adopt KEEP** |
| 2 Structure | Keep §2–§4; three surgical edits (rename §2; reorder §3 internals; rename/nest 5.5 SOD); add Discussion “Scope and limitations” | Agree; none of these change the locked spine | **Adopt surgical edits** |
| 3 Contribution strength | C1/C4 keep; soften C2 “confounder”; C3 “reported skill”→“evaluation statistics”; rewrite one-sentence argument (too binary vs conditional comparability) | Agree — strongest overclaim was the argument sentence, not VPR/NHR per se | **Adopt softens** |
| 4 ≤7 checklist | Title/version + cover letter; claim–evidence matrix; W5 coding; repro package; JSON regen; figure boundary captions; claim-language audit | All actionable and within hard constraints; Zenodo DOI still **do not invent** | **Adopt as pre-sub queue** |

---

## Adopt / veto detail

### Adopt (applied or queued)

1. **KEEP GMD Methods for assessment of models** as primary venue/type.  
2. Soften **one-sentence argument** to conditional portability wording (not “not a portable skill quantity unless…”).  
3. Soften **C2**: confounder → **evaluation ambiguity**.  
4. Soften **C3**: reported skill → **reported evaluation statistics**.  
5. Rename §2 → **Evidence taxonomy and interpretation rules**; note §3 internal order 3.1–3.7; rename §5.5 and nest SOD as magnitude-only sub-result.  
6. Title/version compliance: working title must eventually carry **exact CE-QUAL-W2 version/release scope** (primary executable/audit is v4.5.5; v5.0 beta inventory remains in corpus — state multi-release scope accurately; do not invent a single fake version). Cover-letter manuscript-type sentence queued (not drafted here).

### Soft-adopt (no full rewrite this pass)

- Discussion labelled **Scope and limitations** consolidating hard boundaries — already present as limits prose; heading rename can wait until Discussion polish.  
- Figure caption boundary language — apply when caption pass runs (checklist item 6).  
- Full claim–evidence matrix freeze — already partially encoded in blueprint Table §4; expand as separate note before submission polish.

### Veto / defer

- **Do not switch to EMS** as primary.  
- **Do not** invent Zenodo DOI.  
- **Do not** expand SOD into a calibration/validation claim.  
- Advisor “Fig. 1 should distinguish evaluation record…” — interpret as **run-card / evaluation-record figure** (current Fig. 7), not renumber SciencePlots files this pass; keep figure numbers frozen unless a dedicated caption pass renames.

---

## Files touched this turn

| File | Change |
|---|---|
| `notes/chatgpt_briefs/gmd_blueprint_confirm_raw.md` | New — raw advisor extract |
| `notes/GMD_BLUEPRINT_CONFIRM_20260816.md` | This judgment |
| `drafts/P1_MERGED_BLUEPRINT.md` | Small wording / structure-label tweaks |
| `drafts/P1_GMD_draft_v2.md` | Matching C2/C3/argument/§2/§5.5 softens |
| `notes/chatgpt_briefs/conversation_links.md` | Append this follow-up |

**No commit.**
