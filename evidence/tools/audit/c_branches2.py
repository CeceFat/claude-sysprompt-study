"""Branch-page follow-ups. Written with the Write tool so that backslashes survive.
Usage: python -I c_branches2.py <repo_root>"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import facts  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
vs, M = facts.load(sys.argv[1])
L = facts.by_label(vs)
BS_N = chr(92) + "n"

print("=== files that contain a literal backslash-n ===")
print("  ", [v.label for v in vs if BS_N in v.text])

print("=== Sonnet 3.5 vs Haiku 3.5 text-only, both labelled 2024-10-22 (literal backslash-n normalised) ===")
sa = [x.strip() for x in L["S3.5@241022t"].text.replace(BS_N, "\n").split("\n") if x.strip()]
hb = [x.strip() for x in L["H3.5@241022t"].text.replace(BS_N, "\n").split("\n") if x.strip()]
ws = sum(len(x.split()) for x in sa)
wh = sum(len(x.split()) for x in hb)
sh = sum(len(x.split()) for x in hb if x in set(sa))
ss = sum(len(x.split()) for x in sa if x in set(hb))
print("  S3.5: %d paragraphs, %d w | H3.5: %d paragraphs, %d w" % (len(sa), ws, len(hb), wh))
print("  H3.5 words in paragraphs identical to an S3.5 paragraph: %d (%.1f%%)" % (sh, 100.0 * sh / wh))
print("  S3.5 words in paragraphs identical to an H3.5 paragraph: %d (%.1f%%)" % (ss, 100.0 * ss / ws))
print("  same-day Sonnet/Haiku pairs for comparison:")
for a, b in [("S4.5@251119", "H4.5@251119"), ("S4.5@260118", "H4.5@260118"), ("S5.5@261007", "H5.5@261007")]:
    print("     %s vs %s: %.1f%% of the Haiku words are in lines identical to the Sonnet entry" % (a, b, 100.0 * facts.shared_words(L[b], L[a]) / L[b].words))


def excl(t, a, b):
    T, A, B = L[t], L[a], L[b]
    tot = T.words
    oa = sum(len(l.split()) for l in T.lines if l in A.lineset and l not in B.lineset)
    ob = sum(len(l.split()) for l in T.lines if l in B.lineset and l not in A.lineset)
    both = sum(len(l.split()) for l in T.lines if l in A.lineset and l in B.lineset)
    print("  %s: only %s %.1f%% | only %s %.1f%% | both %.1f%% | neither %.1f%%" % (t, a, 100.0 * oa / tot, b, 100.0 * ob / tot, 100.0 * both / tot, 100.0 * (tot - oa - ob - both) / tot))


print("=== exclusive verbatim shares ===")
excl("O5@260724", "O4.8@260528", "F5@260609")
excl("S5@260630", "F5@260609", "S4.6@260217")
excl("S5@260630", "F5@260609", "O4.8@260528")
excl("S5.5@260928", "S5@260630", "O5.5@260922")
excl("S5.5@260928", "S5@260630", "F5.1@260901")
excl("H5.5@261007", "S5.5@261007", "O5.5@260922")
excl("H4.5@261007", "H4.5@260118", "S5@260630")
excl("S4.6@261007", "S4.6@260217", "O4.8@260528")

print("=== retention of a page's own previous entry (verbatim / minor-edit >=0.8 / new), word-weighted ===")
pairs = [("H4.5@261007", "H4.5@260118"), ("S4.6@261007", "S4.6@260217"), ("S4.6@261014", "S4.6@261007"), ("H4.5@261023", "H4.5@261007"),
         ("O4.6@261030", "O4.6@260205"), ("O4.7@261030", "O4.7@260416"), ("O4.8@261030", "O4.8@260528"), ("F5@261030", "F5@260609"),
         ("S5@261030", "S5@260630"), ("O5@261030", "O5@260724"), ("F5.1@261030", "F5.1@260901"), ("O5.5@261027", "O5.5@260922"),
         ("S5.5@261007", "S5.5@260928"), ("S5.5@261027", "S5.5@261007"), ("H5.5@261026", "H5.5@261007"),
         ("S4.5@251119", "S4.5@250929"), ("S4.5@260118", "S4.5@251119"), ("O4.5@260118", "O4.5@251124"), ("S4@250731", "S4@250522")]
for t, p in pairs:
    r = facts.newness(L[t], [L[p]])
    print("  %-12s vs %-12s verbatim %5.1f%% | minor-edit %5.1f%% | new %5.1f%%  (%d -> %d words)" % (
        t, p, 100.0 * r["verbatim"] / r["total"], 100.0 * r["edit"] / r["total"], 100.0 * r["new"] / r["total"], L[p].words, L[t].words))
