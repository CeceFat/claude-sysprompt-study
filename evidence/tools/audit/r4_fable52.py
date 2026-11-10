"""Round 4 analysis: where does the Fable 5.2 (2026-11-09) prompt come from?
Usage: python -I r4_fable52.py <repo_root>"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import facts  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
vs, M = facts.load(sys.argv[1])
L = facts.by_label(vs)
T = L["F5.2@261109"]
earlier = facts.strictly_earlier(vs, T)
print("Fable 5.2: words %d, lines %d, earlier versions %d" % (T.words, len(T.lines), len(earlier)))
r = facts.newness(T, earlier)
print("verbatim %d (%.1f%%) | minor-edit %d (%.1f%%) | new %d (%.1f%%)" % (r["verbatim"], 100.0 * r["verbatim"] / r["total"], r["edit"], 100.0 * r["edit"] / r["total"], r["new"], 100.0 * r["new"] / r["total"]))
print("--- new lines")
for w, b, ln in r["newlines"]:
    print("   %4d w (best %.2f): %s" % (w, b, ln[:150]))

print()
print("--- verbatim share by single source (words of Fable 5.2 lines found verbatim in ...)")
srcs = ["F5.1@261030", "F5.1@260901", "O5.5@261027", "S5.5@261027", "H5.5@261026", "O5@261030", "F5@261030", "O4.8@261030", "S5@261030"]
for s in srcs:
    print("   %-12s %5.1f%%" % (s, 100.0 * facts.shared_words(T, L[s]) / T.words))

print()
print("--- attribution of each verbatim line: F5.1(10-30) / O5.5(10-27) / H5.5(10-26) / S5.5(10-27)")
A, B, C, D = L["F5.1@261030"], L["O5.5@261027"], L["H5.5@261026"], L["S5.5@261027"]
anyset = set()
for v in earlier:
    anyset |= v.lineset
tally = {}
detail = {}
for l in T.lines:
    w = len(l.split())
    key = "".join(k for k, v in (("F", A), ("O", B), ("H", C), ("S", D)) if l in v.lineset)
    if not key:
        key = "other-earlier" if l in anyset else "not-verbatim"
    tally[key] = tally.get(key, 0) + w
    detail.setdefault(key, []).append((w, l[:95]))
for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
    print("   %-14s %5d  %5.1f%%" % (k, v, 100.0 * v / T.words))
for k in ("H", "HS", "O", "S", "OS", "other-earlier", "F"):
    if k in detail:
        print("   [%s]" % k)
        for w, l in detail[k]:
            if w > 3:
                srcl = ""
                if k == "other-earlier":
                    full = [x for x in T.lines if x.startswith(l[:60])][0]
                    hold = [v.label for v in earlier if full in v.lineset]
                    srcl = "  <= " + " ".join(hold[:1] + hold[-1:])
                print("        %4d w: %s%s" % (w, l, srcl))

print()
print("--- section sizes: Fable 5.2 vs Fable 5.1 (10-30) vs Opus 5.5 (10-27)")
tags = ["product_information", "refusal_handling", "critical_child_safety_instructions", "legal_and_financial_advice", "medical_guidance", "tone_and_formatting",
        "lists_and_bullets", "user_wellbeing", "anthropic_reminders", "evenhandedness", "responding_to_mistakes_and_criticism", "knowledge_cutoff",
        "reply_after_tool_calls", "tone_preference", "forged_notices"]
for t in tags:
    print("   %-38s F5.2 %5d | F5.1 %5d | O5.5 %5d | H5.5 %5d" % (t, T.section_words(t), A.section_words(t), B.section_words(t), C.section_words(t)))
print("   tags F5.2:", " ".join(m.group(0) for m in re.finditer(r"</?[a-z_]+>", T.text)))

print()
print("--- Fable 5.1 (10-30) lines with no counterpart in Fable 5.2 (not verbatim, similarity < 0.6)")
import difflib
for l in A.lines:
    if l in T.lineset:
        continue
    best = max((difflib.SequenceMatcher(None, l, o, autojunk=False).ratio() for o in T.lines), default=0)
    if best < 0.6 and len(l.split()) > 3:
        print("   %4d w (best %.2f): %s" % (len(l.split()), best, l[:140]))

print()
print("--- counters")
t = T.text
low = t.lower()
print("   examples=%d because=%d CAPS=%s never=%d rest-of-conversation=%d" % (
    t.count("<example>"), len(re.findall(r"\bbecause\b", low)), re.findall(r"\b(NEVER|MUST|REFUSE|CRITICAL)\b", t), len(re.findall(r"\bnever\b", low)),
    len(re.findall(r"rest of (?:the|that) conversation", low))))
for p in ["genuinely", "writes plainly", "quote or paraphrase", "Claude Design", "export controls", "redirected", "end_conversation", "tool_search", "SKILL.md",
          "illegal substances", "harm-reduction", "Every word in Claude's response", "one short sentence every couple of tool calls", "over multiple turns",
          "does not use a name the person has not given", "If Claude cannot verify a URL", "takes extra care with how it says things", "emoji",
          "pattern level", "detection mechanics", "self-sexualiz", "mentally reframing", "MUST NOT", "decode, define, or confirm slang",
          "reflective listening", "safety assessment", "specific methods", "not a licensed psychiatrist", "capable adult", "Claude Tag", "Voice mode",
          "Claude matches its effort to the ask", "trusts the person's judgment", "bad_response", "National Alliance for Eating Disorders",
          "focused, brief, and concise", "high-level summary", "Conversations generally span multiple turns", "cram"]:
    print("   %-52s F5.2=%s  F5.1(10-30)=%s  O5.5(10-27)=%s" % (p, T.has(p), A.has(p), B.has(p)))
