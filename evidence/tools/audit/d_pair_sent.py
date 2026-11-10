"""Sentence-level comparison of any two versions, same method as d_f51_f52_sent.py: tags and list
dashes are ignored; a sentence is identical, edited (similarity >= 0.6, paired one-to-one), or
present in only one of the two versions.

Mode `length` instead counts, for every label given, the general instructions about how long, dense,
direct or repetitive a reply should be. The list is hand-made (LENGTH_STARTS): a sentence counts when
its subject is the length, density, directness or redundancy of the reply, including progress updates
and the reply after tool calls. Formatting, tone and word bans are not counted, and neither are
topic-specific sentences (risky conversations, the suicide and voting paragraphs, one-word answers
on contested issues). The list was built from Fable 5.1, Opus 5.5 and Fable 5.2 only, so counts for
other versions may be incomplete.

Usage: python -I -B d_pair_sent.py <repo_root> <labelA> <labelB> [summary|aonly|bonly|edited]
       python -I -B d_pair_sent.py <repo_root> length <label> [<label> ...]
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
INNER = {"user", "response", "rationale", "example", "bad_response", "good_response"}
SPLIT = re.compile(r"""(?<=[.!?])\s+(?=[A-Z"'(\[])|(?<=[.!?]["')\]])\s+(?=[A-Z"'(\[])""")
TAG = re.compile(r"</?[a-z_]+>")
LENGTH_STARTS = [
    "Claude keeps responses focused, brief, and concise",
    "Disclaimers and caveats are brief",
    "When asked to explain something, Claude gives a high-level summary",
    "Claude can give answers over multiple turns",
    "In typical conversation and for simple questions",
    "Claude can let the person know that it has more to add",
    "Claude balances the need to give a dense comprehensive answer",
    "Every word in Claude's response",
    "Typically cliche phrases",
    "Claude takes a moment to summarize its own thoughts",
    "If Claude is making many tool calls",
    "After its last tool call in a turn",
    "Claude does not repeat in the reply",
    "Claude's outputs are reasonably concise",
    "Claude matches its effort to the ask",
    "A simple question gets a direct answer",
    "Conversations generally span multiple turns",
    "Claude adds extra examples, tips, and alternatives only when",
]


def sentences(v):
    """[(block, sentence, line number)] in order; structural tag lines are skipped."""
    out, stack = [], []
    for n, raw in enumerate(v.text.split("\n"), 1):
        s = raw.strip()
        if not s:
            continue
        m = re.fullmatch(r"<(/?)([a-z_]+)>", s)
        if m:
            if m.group(2) not in INNER:
                if m.group(1):
                    if stack and stack[-1] == m.group(2):
                        stack.pop()
                else:
                    stack.append(m.group(2))
            continue
        s = re.sub(r"^- ", "", TAG.sub("", s)).strip()
        for x in SPLIT.split(s):
            x = x.strip()
            if x:
                out.append((stack[-1] if stack else "-", x, n))
    return out


def words(xs):
    return sum(len(x.split()) for x in xs)


if sys.argv[2] == "length":
    for lab in sys.argv[3:]:
        v = L[lab]
        rows = [(n, s) for _, s, n in sentences(v) if any(s.startswith(p) for p in LENGTH_STARTS)]
        tot = words([s for _, s in rows])
        print("== %s: %d sentences, %d words (%.1f%% of %d)" % (lab, len(rows), tot, 100.0 * tot / v.words, v.words))
        for n, s in rows:
            only = [x.label for x in vs if x.has(s)]
            models = sorted({x.model for x in vs if x.has(s)})
            print("   L%-4d %3dw  in %2d versions (%s)  %s" % (n, len(s.split()), len(only), ", ".join(models), s))
    sys.exit(0)

A, B = L[sys.argv[2]], L[sys.argv[3]]
MODE = sys.argv[4] if len(sys.argv) > 4 else "summary"
SA, SB = sentences(A), sentences(B)
bs, as_ = {s for _, s, _ in SB}, {s for _, s, _ in SA}
ar = [x for x in SA if x[1] not in bs]
br = [x for x in SB if x[1] not in as_]
cands = []
for i, (_, s, _) in enumerate(ar):
    for j, (_, t, _) in enumerate(br):
        if min(len(s), len(t)) * 2.5 < max(len(s), len(t)):
            continue
        r = difflib.SequenceMatcher(None, s, t, autojunk=False).ratio()
        if r >= 0.6:
            cands.append((r, i, j))
cands.sort(reverse=True)
pa, pb = {}, {}
for r, i, j in cands:
    if i not in pa and j not in pb:
        pa[i] = j
        pb[j] = i
aonly = [x for i, x in enumerate(ar) if i not in pa]
bonly = [x for j, x in enumerate(br) if j not in pb]
if MODE == "summary":
    same = [s for _, s, _ in SA if s in bs]
    print("%s: %d sentences, %d words | %s: %d sentences, %d words"
          % (A.label, len(SA), words([s for _, s, _ in SA]), B.label, len(SB), words([s for _, s, _ in SB])))
    print("identical: %d sentences, %d words" % (len(same), words(same)))
    print("edited pairs: %d (%d -> %d words)" % (len(pa), words([ar[i][1] for i in pa]), words([br[j][1] for j in pb])))
    for v, lst in ((A, aonly), (B, bonly)):
        agg = {}
        for b, s, _ in lst:
            agg.setdefault(b, [0, 0])
            agg[b][0] += 1
            agg[b][1] += len(s.split())
        print("only in %s: %d sentences, %d words" % (v.label, len(lst), words([s for _, s, _ in lst])))
        print("   by block: " + ", ".join("%s %d/%dw" % (k, n, w) for k, (n, w) in agg.items()))
elif MODE in ("aonly", "bonly"):
    for b, s, n in (aonly if MODE == "aonly" else bonly):
        print("L%-4d <%s> %dw | %s" % (n, b, len(s.split()), s))
elif MODE == "edited":
    for i, j in sorted(pa.items()):
        print("A L%-4d <%s> %s" % (ar[i][2], ar[i][0], ar[i][1]))
        print("B L%-4d <%s> %s" % (br[j][2], br[j][0], br[j][1]))
        print()
