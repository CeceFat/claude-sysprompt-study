"""Index-page numeric claims, recomputed independently. Usage: python -I c_index1.py <repo_root>"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import facts  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
vs, M = facts.load(sys.argv[1])
L = facts.by_label(vs)


def pct(a, b):
    return "%.1f%%" % (100.0 * a / b)


print("=== (1) newness vs versions dated strictly earlier ===")
for lab in ["O5.5@260922", "S5.5@260928", "S5.5@261007", "H5.5@261007", "H5.5@261026", "O5.5@261027", "S5.5@261027"]:
    t = L[lab]
    refs = facts.strictly_earlier(vs, t)
    r = facts.newness(t, refs)
    print("%s total=%d (file words %d) | verbatim %d %s | minor-edit %d %s | new %d %s | refs=%d" % (
        lab, r["total"], t.words, r["verbatim"], pct(r["verbatim"], r["total"]), r["edit"], pct(r["edit"], r["total"]), r["new"], pct(r["new"], r["total"]), len(refs)))
    for w, b, ln in r["newlines"]:
        print("      new %4d w (best %.2f): %s" % (w, b, ln[:120]))

print()
print("=== (1b) same, but reference set also includes same-day siblings (sensitivity) ===")
for lab in ["O5.5@261027", "S5.5@261027", "H5.5@261007", "S5.5@261007"]:
    t = L[lab]
    refs = [v for v in vs if v.date <= t.date and v is not t]
    r = facts.newness(t, refs)
    print("%s verbatim %s | minor %s | new %d" % (lab, pct(r["verbatim"], r["total"]), pct(r["edit"], r["total"]), r["new"]))

print()
print("=== (2) lineage of O5.5@260922: verbatim lines by source ===")
t = L["O5.5@260922"]
o5, f51 = L["O5@260724"], L["F5.1@260901"]
earlier = facts.strictly_earlier(vs, t)
anyset = set()
for v in earlier:
    anyset |= v.lineset
tot = sum(len(l.split()) for l in t.lines)
b = {"F5.1 only": 0, "O5 only": 0, "both": 0, "other earlier": 0, "not verbatim": 0}
for l in t.lines:
    w = len(l.split())
    inO, inF = l in o5.lineset, l in f51.lineset
    if inO and inF:
        b["both"] += w
    elif inF:
        b["F5.1 only"] += w
    elif inO:
        b["O5 only"] += w
    elif l in anyset:
        b["other earlier"] += w
    else:
        b["not verbatim"] += w
for k, v in b.items():
    print("   %-14s %5d  %s" % (k, v, pct(v, tot)))
print("   O5 ∪ F5.1 = %s ; all verbatim = %s" % (pct(b["both"] + b["F5.1 only"] + b["O5 only"], tot), pct(tot - b["not verbatim"], tot)))
oth = {}
for l in t.lines:
    if l not in o5.lineset and l not in f51.lineset and l in anyset:
        src = [v.label for v in earlier if l in v.lineset]
        oth[l[:70]] = (len(l.split()), src[:1] + src[-1:])
for k, v in oth.items():
    print("      other-earlier %4d w first/last=%s : %s" % (v[0], v[1], k))

print()
print("=== (3) section word counts ===")
for lab in ["O4.7@260416", "O4.8@260528", "O5@260724", "F5.1@260901", "O5.5@260922", "O5.5@261027"]:
    print("   tone_and_formatting %-12s %d" % (lab, L[lab].section_words("tone_and_formatting")))
for tag in ["refusal_handling", "user_wellbeing", "tone_and_formatting", "product_information", "evenhandedness"]:
    rank = sorted(((v.section_words(tag), v.label) for v in vs if v.col), reverse=True)[:4]
    print("   top %-20s %s" % (tag, rank))
for lab in ["O5.5@261027", "S5.5@261027", "H5.5@261026"]:
    v = L[lab]
    secs = sorted(((v.section_words(tg), tg) for tg in v.tags() if tg not in ("claude_behavior",)), reverse=True)[:5]
    print("   largest sections of %s: %s" % (lab, secs))

print()
print("=== (4) style counters for the latest 5.5 entries ===")
for lab in ["O5.5@261027", "S5.5@261027", "H5.5@261026", "O5.5@260922", "S5.5@260928", "H5.5@261007"]:
    t = L[lab].text
    low = t.lower()
    sents = [s for s in re.split(r"(?<=[.!?])\s+", L[lab].ws) if re.search(r"rest of (the|that) conversation", s, re.I)]
    print("%s words=%d examples=%d because=%d CAPS=%d [%s] rest-of-conv occurrences=%d sentences=%d bad_response=%d good_response=%d" % (
        lab, L[lab].words, t.count("<example>"), len(re.findall(r"\bbecause\b", low)),
        len(re.findall(r"\b(NEVER|MUST|REFUSE|CRITICAL)\b", t)), ",".join(re.findall(r"\b(NEVER|MUST|REFUSE|CRITICAL)\b", t)),
        len(re.findall(r"rest of (?:the|that) conversation", low)), len(sents), t.count("<bad_response>"), t.count("<good_response>")))
    if lab in ("O5.5@261027", "H5.5@261026"):
        for s in sents:
            print("      · " + s[:150])
allcaps = {}
for lab in ["O5.5@261027", "S5.5@261027", "H5.5@261026"]:
    allcaps[lab] = sorted(set(re.findall(r"\b[A-Z]{4,}\b", L[lab].text)))
    print("   all-caps tokens >=4 letters in %s: %s" % (lab, allcaps[lab]))

print()
print("=== (6) political module paragraphs ===")
h = L["H5.5@261026"]
pol = [l for l in h.lines if l.startswith("For questions about politicians") or l.startswith("Information about the user")]
for l in pol:
    holders = [v.label for v in vs if l in v.lineset]
    print("   %d words | verbatim line in %d versions: %s | %s" % (len(l.split()), len(holders), holders, l[:80]))
prev = L["H5.5@261007"]
print("   evenhandedness words: " + ", ".join("%s=%d" % (x, L[x].section_words("evenhandedness")) for x in ["H5.5@261007", "H5.5@261026", "O5.5@260922", "O5.5@261027", "S5.5@261007", "S5.5@261027", "O5@260724", "O5@261030", "F5.1@260901", "F5.1@261030", "F5@260609", "F5@261030"]))

print()
print("=== (7) lines shared verbatim by the three latest 5.5 entries ===")
A, B, C = L["O5.5@261027"], L["S5.5@261027"], L["H5.5@261026"]
common = A.lineset & B.lineset & C.lineset
for v in (A, B, C):
    print("   %s shared-by-all words = %d of %d" % (v.label, sum(len(l.split()) for l in v.lines if l in common), v.words))
A, B, C = L["O5.5@260922"], L["S5.5@260928"], L["H5.5@261007"]
common = A.lineset & B.lineset & C.lineset
for v in (A, B, C):
    print("   first entries: %s shared-by-all words = %d of %d" % (v.label, sum(len(l.split()) for l in v.lines if l in common), v.words))
