#!/usr/bin/env python3
"""Bibliography sanity audit for the paper repo (c269).

Finds orphan bib entries (never cited) and dangling cite-keys (used
in .tex but missing from refs.bib). Run from repo root.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BIB = REPO / "bibliography" / "refs.bib"
TEX_ROOTS = [
    REPO / "conference" / "tex",
    REPO / "journal" / "tex",
    REPO / "supplementary" / "conference",
    REPO / "supplementary" / "journal",
]

ENTRY_RE = re.compile(r"@\w+\{([^,]+),", re.MULTILINE)


def main() -> None:
    bib_text = BIB.read_text(encoding="utf-8")
    keys_in_bib = set(ENTRY_RE.findall(bib_text))
    print(f"Bib entries: {len(keys_in_bib)}")

    tex_files: list[Path] = []
    for root in TEX_ROOTS:
        if not root.is_dir():
            continue
        for f in os.listdir(root):
            if f.endswith(".tex"):
                tex_files.append(root / f)

    cited: set[str] = set()
    for f in tex_files:
        src = f.read_text(encoding="utf-8")
        idx = 0
        while True:
            i = src.find("\\cite", idx)
            if i < 0:
                break
            j = src.find("{", i)
            if j < 0:
                break
            k = src.find("}", j)
            if k < 0:
                break
            for key in src[j + 1 : k].split(","):
                cited.add(key.strip())
            idx = k

    print(f"Distinct cite-keys referenced across {len(tex_files)} .tex files: {len(cited)}")
    orphans = sorted(keys_in_bib - cited)
    dangling = sorted(cited - keys_in_bib)
    print(f"Orphan bib entries (never cited): {len(orphans)}")
    print(f"Dangling cite-keys (no matching @entry): {len(dangling)}")
    if dangling:
        for k in dangling:
            print(f"  DANGLING  {k}")
    if orphans:
        for k in orphans:
            print(f"  ORPHAN    {k}")


if __name__ == "__main__":
    main()
