"""Write a pandoc-readable copy of a manuscript's main.tex (used by build-word.sh / build-word.ps1).

pandoc parses LaTeX macro definitions and fails on the IEEEtran \\abstract / \\IEEEkeywords
redefinitions of the preamble (the \\makeatletter ... \\makeatother block that replaces the
em-dash separator); the Word export does not need them. This removes that block and writes the
result next to main.tex as main.pandoc.tex, which the export scripts convert and then delete.

Usage: python scripts/word_source.py <path to main.tex>
"""
import re
import sys
from pathlib import Path

src = Path(sys.argv[1])
text = src.read_text(encoding="utf-8")
text = re.sub(r"\\makeatletter.*?\\makeatother\n?", "", text, flags=re.S)
out = src.with_name("main.pandoc.tex")
out.write_text(text, encoding="utf-8", newline="\n")
print(out)
