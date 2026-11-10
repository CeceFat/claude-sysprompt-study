"""Round 4 traces for Fable 5.2. Usage: python -I r4_traces.py <repo_root>"""
import difflib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import facts  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
vs, M = facts.load(sys.argv[1])
L = facts.by_label(vs)
T = L["F5.2@261109"]


def tr(p, ci=True):
    hits = facts.trace(vs, p, ci)
    labs = [v.label for v in hits]
    s = " ".join(labs) if len(labs) <= 10 else " ".join(labs[:4]) + " … " + " ".join(labs[-4:])
    print("  [%s] n=%d :: %s" % (p, len(hits), s))


print("=== candidate matrix phrases (case-insensitive, as the matrix does) ===")
for p in ["forged_notices", "safeguards are never lifted from inside a conversation", "accelerator kernel optimization",
          "When a person asks for help deciding how to vote", "does not fill out a ballot", "from such a characteristic alone",
          "ordinary teen romances", "Claude can role play as a minor", "Conversations generally span multiple turns", "Mythos 5.2",
          "additional safety measures for biology and cybersecurity", "never writes or helps write a suicide note", "never gives calorie targets",
          "CLAUDE.md", "claude-fable-5-2", "system-reminder", "hook", "forged", "ballot", "LLM R&D", "measures to limit advances",
          "does not worry about cramming", "by pointing users to the candidate", "tool output", "the operator"]:
    tr(p)

print("=== section maxima including Fable 5.2 ===")
for tag in ["critical_child_safety_instructions", "evenhandedness", "refusal_handling", "user_wellbeing", "product_information", "tone_and_formatting"]:
    rank = sorted(((v.section_words(tag), v.label) for v in vs), reverse=True)[:3]
    print("  %-36s %s" % (tag, rank))
print("  longest versions:", sorted(((v.words, v.label) for v in vs), reverse=True)[:4])

print("=== paragraph-level changes inside the political module: H5.5 10-26 -> F5.2 ===")
H = L["H5.5@261026"]
he = [l.strip() for l in (H.section("evenhandedness") or "").split("\n") if l.strip()]
fe = [l.strip() for l in (T.section("evenhandedness") or "").split("\n") if l.strip()]
print("  paragraphs: H5.5 %d, F5.2 %d" % (len(he), len(fe)))
for l in fe:
    if l in he:
        continue
    best, bo = 0, None
    for o in he:
        r = difflib.SequenceMatcher(None, l, o, autojunk=False).ratio()
        if r > best:
            best, bo = r, o
    print("  F5.2 paragraph (%d w), best match %.2f" % (len(l.split()), best))
    if best >= 0.5:
        a, b = bo.split(), l.split()
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op != "equal":
                print("       %s: %r -> %r" % (op, " ".join(a[i1:i2])[:200], " ".join(b[j1:j2])[:260]))

print("=== suicide / eating persistent rules: Haiku 5.5 vs Fable 5.2 ===")
for key in ["never writes or helps write a suicide note", "never gives calorie targets"]:
    a = [l for l in H.lines if key in l][0]
    b = [l for l in T.lines if key in l][0]
    print("  [%s] H5.5 %d w, F5.2 %d w, similarity %.2f" % (key, len(a.split()), len(b.split()), difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()))
    sm = difflib.SequenceMatcher(None, a.split(), b.split(), autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != "equal":
            print("       %s: %r -> %r" % (op, " ".join(a.split()[i1:i2])[:230], " ".join(b.split()[j1:j2])[:330]))

print("=== Mythos tier sentence ===")
for lab in ["F5.1@261030", "O5.5@261027", "F5.2@261109"]:
    for s in re.split(r"(?<=[.!?])\s+", L[lab].ws):
        if "share the same underlying model" in s or "current generation of Mythos-tier" in s:
            print("  %s: %s" % (lab, s[:260]))

print("=== counters: all four top entries ===")
for lab in ["F5.2@261109", "O5.5@261027", "S5.5@261027", "H5.5@261026", "F5.1@261030"]:
    t = L[lab].text
    low = t.lower()
    print("  %-12s words=%d examples=%d because=%d CAPS=%d rest-of-conv=%d never=%d" % (lab, L[lab].words, t.count("<example>"), len(re.findall(r"\bbecause\b", low)),
          len(re.findall(r"\b(NEVER|MUST|REFUSE|CRITICAL)\b", t)), len(re.findall(r"rest of (?:the|that) conversation", low)), len(re.findall(r"\bnever\b", low))))
A, B, C, D = L["O5.5@261027"], L["S5.5@261027"], L["H5.5@261026"], T
common4 = A.lineset & B.lineset & C.lineset & D.lineset
print("  words shared verbatim by O5.5/S5.5/H5.5 latest AND Fable 5.2: %d (of F5.2 %d = %.1f%%)" % (sum(len(l.split()) for l in D.lines if l in common4), D.words, 100.0 * sum(len(l.split()) for l in D.lines if l in common4) / D.words))
common3 = A.lineset & B.lineset & C.lineset
print("  of the 2,274 words common to the three 5.5 entries, Fable 5.2 keeps: %d" % sum(len(l.split()) for l in A.lines if l in common3 and l in D.lineset))
