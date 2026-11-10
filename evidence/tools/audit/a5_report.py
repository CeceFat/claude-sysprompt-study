"""Audit A5: mechanical quote check for files the site's own verifier never covered
(report/changelog-zh-TW.md, README.md, evidence/README.md, data/versions.js).

Every run of >= 4 English words is looked up case-sensitively in the version files, then in the
diffs/external corpus. Runs that are obviously not quotations (paths, commands, headings) are listed
separately so they can be eyeballed.

Usage: python -I a5_report.py <repo_root> <file> [<file> ...]
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import facts  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ROOT = sys.argv[1]
vs, M = facts.load(ROOT)
extra = ""
for d in ("diffs", "external", "sources"):
    p = os.path.join(ROOT, "evidence", d)
    for f in sorted(os.listdir(p)):
        t = open(os.path.join(p, f), encoding="utf-8", newline="").read()
        if d == "diffs":
            t = re.sub(r"\[-|-\]|\{\+|\+\}", "", t)
        t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
        extra += "\n" + re.sub(r"\s+", " ", t)

RUN = re.compile(r"[A-Za-z<\"'(][A-Za-z0-9'’\"<>_/().,;:!?\-—–{}\[\]%&*+=@#$]*(?:[ ][A-Za-z0-9'’\"<>_/().,;:!?\-—–{}\[\]%&*+=@#$]+){3,}")
SPLIT = re.compile(r"\s*(?:…|\.\.\.|／|\s\|\s)\s*")

for path in sys.argv[2:]:
    src = open(os.path.join(ROOT, path), encoding="utf-8", newline="").read().replace("\r\n", "\n")
    src = src.replace('\\"', '"')
    ok = ci = miss = 0
    missing, cionly = [], []
    for ln_no, line in enumerate(src.split("\n"), 1):
        for m in RUN.finditer(line):
            run = m.group(0)
            for seg in SPLIT.split(run):
                seg = seg.strip(" \"'`「」（）()，。、；:：.,;*|")
                if len(seg.split()) < 4:
                    continue
                if any(v.has(seg) for v in vs) or seg in extra:
                    ok += 1
                elif any(v.has(seg, ci=True) for v in vs) or seg.lower() in extra.lower():
                    ci += 1
                    cionly.append((ln_no, seg))
                else:
                    miss += 1
                    missing.append((ln_no, seg))
    print("=== %s: english runs found verbatim %d | case-insensitive only %d | not found %d" % (path, ok, ci, miss))
    for ln_no, seg in cionly:
        print("   CI   L%d: %s" % (ln_no, seg[:150]))
    for ln_no, seg in missing:
        print("   MISS L%d: %s" % (ln_no, seg[:150]))
