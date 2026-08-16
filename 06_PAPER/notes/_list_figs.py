# -*- coding: utf-8 -*-
from pathlib import Path
import re
c = Path(r"I:\Projects\20260810-CE-QUAL-W2\06_PAPER\analysis\build_research_report.py").read_text(encoding="utf-8")
names = re.findall(r'self\.figure\(\s*"([^"]+)"', c)
print(len(names))
for n in names:
    print(n)
