# -*- coding: utf-8 -*-
from pathlib import Path
p = Path(r"I:\Projects\20260810-CE-QUAL-W2\06_PAPER\report\report.md")
raw = p.read_bytes()
# try utf-8 then gbk
for enc in ("utf-8", "utf-8-sig", "gbk"):
    try:
        t = raw.decode(enc)
        print("decoded", enc, "len", len(t))
        break
    except Exception as e:
        print(enc, e)
else:
    raise SystemExit("decode fail")
lines = t.splitlines()
for i, l in enumerate(lines[:8]):
    print(i, l[:80])
# insert note after first bullet-like header lines
note = "（ROUND 2：过程细节见本报告；投稿向论文 `06_PAPER/drafts/P1_GMD_draft_v2.md` 已剥离本地路径与协作元叙述）"
if "ROUND 2" not in lines[2] if len(lines) > 2 else True:
    # find generation time line
    for i, l in enumerate(lines):
        if "2026-08-16" in l and ("生成" in l or "Generate" in l or "18:09" in l):
            if "ROUND 2" not in l:
                lines[i] = l.rstrip() + " " + note
            break
    else:
        # insert after title
        lines.insert(2, "- " + note)
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("updated")
