"""Audit A2: independent recomputation of the feature matrix and its three serialisations.

Usage: python -I a2_matrix.py <repo_root>
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = sys.argv[1]
VDIR = os.path.join(ROOT, "evidence", "versions")
issues = []


def rd(p):
    return open(p, encoding="utf-8", newline="").read()


M = json.loads(rd(os.path.join(ROOT, "data", "matrix.json")))
js = rd(os.path.join(ROOT, "data", "matrix.js")).replace("\r\n", "\n")
m = re.search(r"window\.MATRIX\s*=\s*(\{.*\})\s*;\s*$", js, re.S)
MJ = json.loads(m.group(1))
print("matrix.js == matrix.json:", MJ == M)
if MJ != M:
    issues.append("matrix.js differs from matrix.json")
print("header comment of matrix.js:", js.split("\n")[0])

cols, phrases = M["columns"], M["phrases"]
print("columns:", len(cols), "phrases:", len(phrases))
print("column indices contiguous 1..N:", [c["i"] for c in cols] == list(range(1, len(cols) + 1)))

# --- columns vs files
allfiles = sorted(f[:-4] for f in os.listdir(VDIR) if f.endswith(".txt"))
colfiles = [c["file"] for c in cols]
print("version files:", len(allfiles), "| distinct column files:", len(set(colfiles)))
print("files that are NOT matrix columns:", [f for f in allfiles if f not in colfiles])
print("columns without file:", [f for f in colfiles if f not in allfiles])

MONTHS = {m: i + 1 for i, m in enumerate("January February March April May June July August September October November December".split())}
raw, lf = {}, {}
print()
print("=== column metadata check (i | model | date | words stored/recomputed | bytes stored / LF / on-disk) ===")
for c in cols:
    p = os.path.join(VDIR, c["file"] + ".txt")
    disk = open(p, "rb").read()
    t = disk.decode("utf-8").replace("\r\n", "\n")
    raw[c["i"]] = t
    w = len(t.split())
    b_lf = len(t.encode("utf-8"))
    slug, date, var = c["file"].split("__")
    mo, d, y = date.split("_")
    iso = "%s-%02d-%02d" % (y, MONTHS[mo], int(d))
    flags = []
    if w != c["words"]:
        flags.append("WORDS %d!=%d" % (c["words"], w))
    if c["bytes"] not in (b_lf, len(disk)):
        flags.append("BYTES stored %d, LF %d, disk %d" % (c["bytes"], b_lf, len(disk)))
    if iso != c["date"]:
        flags.append("DATE %s!=%s" % (c["date"], iso))
    if slug != c["slug"]:
        flags.append("SLUG")
    if c["txt"] != "evidence/versions/%s.txt" % c["file"]:
        flags.append("TXT PATH")
    expect_model = slug.replace("claude-", "").split("-")
    fam = expect_model[0].capitalize()
    ver = ".".join(expect_model[1:])
    if c["model"] != "%s %s" % (fam, ver):
        flags.append("MODEL %r vs slug %r" % (c["model"], "%s %s" % (fam, ver)))
    if c.get("family") != fam:
        flags.append("FAMILY %r" % c.get("family"))
    crlf = b"\r\n" in disk
    print("%2d | %-10s | %s | %-11s | w %5d | bytes %6d (LF %6d, disk %6d%s) %s" % (
        c["i"], c["model"], c["date"], c["variant"], c["words"], c["bytes"], b_lf, len(disk), " CRLF" if crlf else "", " <-- " + "; ".join(flags) if flags else ""))
    if flags:
        issues.append("col %d: %s" % (c["i"], "; ".join(flags)))

# --- date order
dates = [c["date"] for c in cols]
ooo = [(cols[k]["i"], dates[k]) for k in range(1, len(cols)) if dates[k] < dates[k - 1]]
print("columns whose date is earlier than the previous column (append-order exceptions):", ooo)

# --- presence recomputation
def variants(t):
    low = t.lower()
    nostar = t.replace("**", "").lower()
    ws = re.sub(r"\s+", " ", t).lower()
    wsnostar = re.sub(r"\s+", " ", t.replace("**", "")).lower()
    return low, nostar, ws, wsnostar


V = {i: variants(t) for i, t in raw.items()}
mism = 0
star_sens, ws_sens, case_sens = [], [], []
for p in phrases:
    ph = p["p"]
    pl = ph.lower()
    v = "".join("Y" if pl in V[c["i"]][0] else "." for c in cols)
    if v != p["v"]:
        mism += 1
        issues.append("matrix row mismatch: %r" % ph)
        print("ROW MISMATCH", repr(ph), "\n  stored", p["v"], "\n  recomp", v)
    if len(p["v"]) != len(cols):
        issues.append("row length: %r" % ph)
    for c in cols:
        a, b, w, wb = V[c["i"]]
        base = pl in a
        if (pl in b) != base:
            star_sens.append((ph, c["i"], c["model"], c["date"], base, pl in b))
        pws = re.sub(r"\s+", " ", pl)
        if (pws in w) != base:
            ws_sens.append((ph, c["i"], c["model"], c["date"], base, pws in w))
        if base and ph not in raw[c["i"]]:
            case_sens.append((ph, c["i"], c["model"], c["date"]))
print()
print("rows recomputed:", len(phrases), "mismatching rows:", mism, "| cells:", len(phrases) * len(cols), "| Y cells:", sum(p["v"].count("Y") for p in phrases))
print()
print("=== cells whose value changes if official ** change-markers are stripped ===")
for x in star_sens:
    print("  %r col %d (%s %s): raw=%s stripped=%s" % x)
print("(count %d)" % len(star_sens))
print()
print("=== cells whose value changes if whitespace/newlines are collapsed ===")
for x in ws_sens:
    print("  %r col %d (%s %s): raw=%s collapsed=%s" % x)
print("(count %d)" % len(ws_sens))
print()
print("=== Y cells that match only case-insensitively (%d) ===" % len(case_sens))
agg = {}
for ph, i, mo, d in case_sens:
    agg.setdefault(ph, []).append(i)
for ph, lst in agg.items():
    print("  %r cols %s" % (ph, lst))

# --- phrase hygiene
pl = [p["p"].lower() for p in phrases]
dups = sorted({x for x in pl if pl.count(x) > 1})
print()
print("duplicate phrases:", dups)
print("phrases never present:", [p["p"] for p in phrases if "Y" not in p["v"]])
print("phrases present in all columns:", [p["p"] for p in phrases if "." not in p["v"]])
print("phrases with leading/trailing space:", [p["p"] for p in phrases if p["p"] != p["p"].strip()])

# --- feature_matrix.txt
fm = rd(os.path.join(ROOT, "evidence", "feature_matrix.txt")).replace("\r\n", "\n").split("\n")
key_rows = [l for l in fm if re.match(r"^\s*\d+: ", l)]
print()
print("feature_matrix.txt column-key rows:", len(key_rows))
bad = 0
for l, c in zip(key_rows, cols):
    mm = re.match(r"^\s*(\d+): (\S+)\s+(\d+) B\s+(\d+) w$", l)
    if not mm or int(mm.group(1)) != c["i"] or mm.group(2) != c["file"] or int(mm.group(3)) != c["bytes"] or int(mm.group(4)) != c["words"]:
        bad += 1
        print("  KEY ROW MISMATCH:", l)
start = next(k for k, l in enumerate(fm) if l.startswith("phrase"))
hdr = fm[start]
rows = [l for l in fm[start + 1:] if l.strip()]
print("feature_matrix.txt matrix rows:", len(rows), "| key mismatches:", bad)
digits = "".join(str(c["i"] % 10) for c in cols)
print("header digits ok:", hdr.endswith(digits))
badrows = 0
for l, p in zip(rows, phrases):
    if not l.endswith(p["v"]) or l[:-len(p["v"])].rstrip() != p["p"][:len(l[:-len(p["v"])].rstrip())] or not p["p"].startswith(l[:-len(p["v"])].rstrip()[:45].rstrip()):
        # the txt pads phrase to 45 chars; longer phrases are not truncated by %-45s, so compare loosely
        if not (l.endswith(p["v"]) and l[:-len(p["v"])].rstrip() == p["p"].rstrip()):
            badrows += 1
            print("  TXT ROW MISMATCH:", repr(l[:80]))
print("feature_matrix.txt row mismatches:", badrows)
if bad or badrows or len(rows) != len(phrases) or len(key_rows) != len(cols):
    issues.append("feature_matrix.txt inconsistent with matrix.json")

print()
print("=== ISSUES ===")
print("\n".join(issues) if issues else "(none)")
