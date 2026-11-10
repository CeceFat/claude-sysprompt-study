"""Audit check: how much of a version comes from each of two candidate parents.

For each (target, parent A, parent B) it prints
  * the share of the target's words in lines found verbatim in A, in B, only in A, only in B, in both;
  * the same shares when a line also counts if it is a minor edit (similarity >= 0.8) of a parent line;
  * which XML blocks the target shares with each parent.
These are the numbers behind findings F-48, F-56 and F-68 ("skeleton" claims) in
report/audit-2026-11-10-zh-TW.md.

Usage: python -I c_parents.py <repo_root>
"""
import difflib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import facts  # noqa: E402

vs, M = facts.load(sys.argv[1])
L = facts.by_label(vs)

CASES = [
    ("O5@260724", "O4.8@260528", "F5@260609"),      # F-48
    ("O5.5@260922", "O5@260724", "F5.1@260901"),    # F-68
    ("S5.5@260928", "S5@260630", "O5.5@260922"),    # F-56
    ("H5.5@261007", "S5.5@260928", "O5.5@260922"),  # checked, no finding
    ("F5.2@261109", "F5.1@261030", "O5.5@261027"),  # round 4
]
INNER = {"user", "response", "rationale", "example", "bad_response", "good_response"}


def best(line, other):
    b = 0.0
    for o in other.lines:
        # a ratio of 0.8 is impossible when one line is less than half as long as the other
        if min(len(o), len(line)) * 2 < max(len(o), len(line)):
            continue
        r = difflib.SequenceMatcher(None, line, o, autojunk=False).ratio()
        if r > b:
            b = r
    return b


def blocks(v):
    return [t for t in re.findall(r"<([a-z_]+)>", v.text) if t not in INNER]


def shares(t, a, b, near):
    w = {"A": 0, "B": 0, "AB": 0, "none": 0}
    for l in t.lines:
        ina = l in a.lineset or (near and best(l, a) >= 0.8)
        inb = l in b.lineset or (near and best(l, b) >= 0.8)
        w["AB" if ina and inb else "A" if ina else "B" if inb else "none"] += len(l.split())
    return {k: 100.0 * x / t.words for k, x in w.items()}


for tl, al, bl in CASES:
    t, a, b = L[tl], L[al], L[bl]
    print("=== %s (%d words)   A = %s   B = %s" % (tl, t.words, al, bl))
    for near, name in ((False, "verbatim"), (True, "verbatim or minor edit")):
        s = shares(t, a, b, near)
        print("  %-24s in A %5.1f%% | in B %5.1f%% | only A %5.1f%% | only B %5.1f%% | both %5.1f%% | neither %5.1f%%"
              % (name, s["A"] + s["AB"], s["B"] + s["AB"], s["A"], s["B"], s["AB"], s["none"]))
    bt, ba, bb = set(blocks(t)), set(blocks(a)), set(blocks(b))
    print("  blocks: target has %d" % len(bt))
    print("    vs A: A-only %s | target-only %s" % (sorted(ba - bt), sorted(bt - ba)))
    print("    vs B: B-only %s | target-only %s" % (sorted(bb - bt), sorted(bt - bb)))
    print()
