"""Audit refs.bib citations against journal+conference manuscripts."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

bib = (ROOT / "bibliography" / "refs.bib").read_text(encoding="utf-8")
keys = re.findall(r"@\w+\{(\w[\w\-]*)\s*,", bib)
print(f"Total bibtex entries: {len(keys)}")

tex_files = (
    list((ROOT / "journal" / "tex").glob("*.tex"))
    + list((ROOT / "conference" / "tex").glob("*.tex"))
    + list((ROOT / "supplementary").rglob("*.tex"))
)
cite_pat = re.compile(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])?\{([^}]+)\}")
nocite_pat = re.compile(r"\\nocite\{([^}]+)\}")
all_cited: set[str] = set()
for f in tex_files:
    txt = f.read_text(encoding="utf-8")
    for m in cite_pat.finditer(txt):
        for k in m.group(1).split(","):
            all_cited.add(k.strip())
    for m in nocite_pat.finditer(txt):
        for k in m.group(1).split(","):
            all_cited.add(k.strip())
print(f"Cited keys (journal + conference): {len(all_cited)}")
unused = sorted(set(keys) - all_cited)
print(f"\nUnused entries ({len(unused)}):")
for k in unused:
    print("  -", k)
ghost = sorted(all_cited - set(keys))
print(f"\nCited but missing from refs.bib ({len(ghost)}):")
for k in ghost:
    print("  !", k)
