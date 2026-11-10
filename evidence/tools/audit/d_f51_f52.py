"""Line-by-line ledger of Fable 5.1 (2026-10-30) -> Fable 5.2 (2026-11-09).

Every line of 5.2 is classified K (identical line exists in 5.1), E (edited: best 5.1 line has
similarity >= 0.6) or N (no 5.1 counterpart); every 5.1 line that is neither kept nor the source
of an edit is D (dropped). For N lines the script reports where else the line exists verbatim
(provenance); for D lines, which other models' latest entries still carry it (fate).

Usage: python -I -B d_f51_f52.py <repo_root> [summary|ledger|dropped|blocks]
"""
import difflib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import facts  # noqa: E402

vs, M = facts.load(sys.argv[1])
MODE = sys.argv[2] if len(sys.argv) > 2 else "summary"
L = facts.by_label(vs)
A, B = L["F5.1@261030"], L["F5.2@261109"]
A0 = L["F5.1@260901"]
OTHERS = [v for v in vs if v.label not in (A.label, B.label, A0.label)]
LATEST = {}
for v in vs:
    if v.date < B.date and v.model != "Fable 5.1":
        LATEST[v.model] = v
INNER = {"user", "response", "rationale", "example", "bad_response", "good_response"}


def sections(v):
    """[(section, line)] for content lines, plus tag lines as their own entries."""
    out, stack = [], []
    for raw in v.text.split("\n"):
        s = raw.strip()
        if not s:
            continue
        m = re.fullmatch(r"<(/?)([a-z_]+)>", s)
        if m and m.group(2) not in INNER:
            if m.group(1):
                if stack and stack[-1] == m.group(2):
                    stack.pop()
            else:
                stack.append(m.group(2))
            out.append((m.group(2), s, True))
        else:
            out.append((stack[-1] if stack else "-", s, False))
    return out


def ratio(a, b):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def wdiff(a, b):
    ta, tb = a.split(), b.split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes():
        if op == "equal":
            seg = ta[i1:i2]
            out.append(" ".join(seg) if len(seg) <= 14 else " ".join(seg[:6]) + " […] " + " ".join(seg[-6:]))
        else:
            if i2 > i1:
                out.append("[-" + " ".join(ta[i1:i2]) + "-]")
            if j2 > j1:
                out.append("{+" + " ".join(tb[j1:j2]) + "+}")
    return " ".join(out)


SA, SB = sections(A), sections(B)
a_lines = [s for _, s, _ in SA]
a_set = set(a_lines)
b_all = set(s for _, s, _ in SB)
used = {}
rows = []
for sec, s, is_tag in SB:
    w = len(s.split())
    if s in a_set:
        rows.append(("K", sec, s, w, None, None))
        continue
    best_i, best_r = -1, 0.0
    for i, t in enumerate(a_lines):
        if t in used or t in b_all:
            continue
        r = ratio(s, t)
        if r > best_r:
            best_i, best_r = i, r
    if best_r >= 0.6:
        used[a_lines[best_i]] = s
        rows.append(("E", sec, s, w, a_lines[best_i], best_r))
    else:
        rows.append(("N", sec, s, w, None, best_r))
b_set = set(s for _, s, _ in SB)
dropped = [(sec, s, tag) for sec, s, tag in SA if s not in b_set and s not in used]


def first_seen(s):
    hit = [v for v in vs if v.label != B.label and s in v.lineset]
    return hit[0].label if hit else None


def carried_by(s):
    return [m for m, v in LATEST.items() if s in v.lineset]


def nearest_any(s):
    best = (0.0, None, None)
    for v in vs:
        if v.label == B.label:
            continue
        for t in v.lines:
            if min(len(s), len(t)) * 2 < max(len(s), len(t)):
                continue
            r = ratio(s, t)
            if r > best[0]:
                best = (r, v.label, t)
    return best


def words(xs):
    return sum(len(x.split()) for x in xs)


if MODE == "summary":
    k = [r for r in rows if r[0] == "K"]
    e = [r for r in rows if r[0] == "E"]
    n = [r for r in rows if r[0] == "N"]
    print("A = %s: %d lines, %d words | B = %s: %d lines, %d words" % (A.label, len(SA), A.words, B.label, len(SB), B.words))
    print("B side: kept %d lines / %d w (%.1f%%) | edited %d / %d w (%.1f%%) | no 5.1 counterpart %d / %d w (%.1f%%)" % (
        len(k), sum(r[3] for r in k), 100.0 * sum(r[3] for r in k) / B.words, len(e), sum(r[3] for r in e), 100.0 * sum(r[3] for r in e) / B.words,
        len(n), sum(r[3] for r in n), 100.0 * sum(r[3] for r in n) / B.words))
    ea = words(r[4] for r in e)
    print("A side: kept %d w (%.1f%%) | source of an edit %d w (%.1f%%) | dropped %d lines / %d w (%.1f%%)" % (
        sum(r[3] for r in k), 100.0 * sum(r[3] for r in k) / A.words, ea, 100.0 * ea / A.words, len(dropped), words(s for _, s, _ in dropped), 100.0 * words(s for _, s, _ in dropped) / A.words))
    pos = {s: i for i, s in enumerate(a_lines)}
    seq = [pos[r[2]] for r in k]
    import bisect
    tails = []
    for x in seq:
        i = bisect.bisect_left(tails, x)
        tails[i:i + 1] = [x]
    print("kept lines in the same relative order: %d of %d" % (len(tails), len(seq)))
    secs = []
    for sec, _, _ in SA + SB:
        if sec not in secs:
            secs.append(sec)
    print("\n%-38s %6s %6s | %5s %5s %5s | %5s" % ("section", "A w", "B w", "kept", "edit", "new", "drop"))
    for sec in secs:
        aw = words(s for x, s, _ in SA if x == sec); bw = words(s for x, s, _ in SB if x == sec)
        print("%-38s %6d %6d | %5d %5d %5d | %5d" % (sec, aw, bw, sum(r[3] for r in k if r[1] == sec), sum(r[3] for r in e if r[1] == sec),
              sum(r[3] for r in n if r[1] == sec), words(s for x, s, _ in dropped if x == sec)))
    src = {}
    for r in n:
        fs = first_seen(r[2])
        key = "verbatim elsewhere, first seen " + fs if fs else "nowhere verbatim before 5.2"
        src.setdefault(key, [0, 0]); src[key][0] += 1; src[key][1] += r[3]
    print("\nprovenance of the %d lines with no 5.1 counterpart:" % len(n))
    for key, (c, w) in sorted(src.items(), key=lambda x: -x[1][1]):
        print("   %4d w  %2d lines  %s" % (w, c, key))
    gone = [(sec, s) for sec, s, _ in dropped if not carried_by(s)]
    print("\nfate of the %d dropped lines: still in another model's latest entry %d lines / %d w; in none %d lines / %d w" % (
        len(dropped), len(dropped) - len(gone), words(s for _, s, _ in dropped) - words(s for _, s in gone), len(gone), words(s for _, s in gone)))
elif MODE == "ledger":
    for st, sec, s, w, src, r in rows:
        if st == "K":
            continue
        if st == "E":
            fs = first_seen(s)
            print("[E %.2f] <%s> %dw%s\n    %s\n" % (r, sec, w, " | 5.2 wording also in " + fs if fs else "", wdiff(src, s)))
        else:
            fs = first_seen(s)
            if fs:
                tag = "verbatim since %s; latest entries: %s" % (fs, ", ".join(carried_by(s)))
            else:
                nr, nl, nt = nearest_any(s)
                tag = "NEW (nearest %.2f in %s)" % (nr, nl)
            print("[N] <%s> %dw | %s\n    %s\n" % (sec, w, tag, s))
elif MODE == "blocks":
    refs = [("F5.1", A), ("O5.5", L["O5.5@261027"]), ("H5.5", L["H5.5@261026"]), ("S5.5", L["S5.5@261027"])]
    order = []
    for sec, _, tag in SB:
        if sec not in order:
            order.append(sec)
    print("%-38s %5s | %s" % ("block of Fable 5.2", "words", "  ".join("%5s" % n for n, _ in refs)))
    for sec in order:
        ls = [s for x, s, tag in SB if x == sec and not tag]
        if not ls:
            continue
        w = words(ls)
        print("%-38s %5d | %s" % (sec, w, "  ".join("%4.0f%%" % (100.0 * words(l for l in ls if l in v.lineset) / w) for _, v in refs)))
else:
    for sec, s, _ in dropped:
        origin = "since 09-01" if s in A0.lineset else "added 10-30"
        cb = carried_by(s)
        print("[D] <%s> %dw | in 5.1 %s | still in: %s\n    %s\n" % (sec, len(s.split()), origin, ", ".join(cb) if cb else "NONE", s))
