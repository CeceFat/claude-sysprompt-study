"""Sentence-level ledger of Fable 5.1 (2026-10-30) -> Fable 5.2 (2026-11-09).

Lines are split into sentences; inline XML tags and list dashes are ignored for matching.
Each 5.1 sentence is: KEPT (identical sentence in 5.2, same block), MOVED (identical, other block),
EDITED (best 5.2 sentence similarity >= 0.6, one-to-one) or REMOVED.
Each 5.2 sentence is KEPT / MOVED / EDITED or ADDED.
For ADDED sentences: where else the sentence exists verbatim (first version, and which other models'
latest entries carry it). For REMOVED sentences: which other models' latest entries still carry it.

Usage: python -I -B d_f51_f52_sent.py <repo_root> [summary|removed|added|edited|moved|stats|near|md]
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
LATEST = {}
for v in vs:
    if v.date < B.date and v.model != "Fable 5.1":
        LATEST[v.model] = v
INNER = {"user", "response", "rationale", "example", "bad_response", "good_response"}
SPLIT = re.compile(r"""(?<=[.!?])\s+(?=[A-Z"'(\[])|(?<=[.!?]["')\]])\s+(?=[A-Z"'(\[])""")
TAG = re.compile(r"</?[a-z_]+>")


def sentences(v):
    """[(block, sentence)] in order; structural tag lines are skipped."""
    out, stack = [], []
    for raw in v.text.split("\n"):
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
        s = TAG.sub("", s)
        s = re.sub(r"^- ", "", s).strip()
        for x in SPLIT.split(s):
            x = x.strip()
            if x:
                out.append((stack[-1] if stack else "-", x))
    return out


def words(xs):
    return sum(len(x.split()) for x in xs)


def ratio(a, b):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


SA, SB = sentences(A), sentences(B)
bset = {}
for blk, s in SB:
    bset.setdefault(s, []).append(blk)
aset = {}
for blk, s in SA:
    aset.setdefault(s, []).append(blk)
a_rest = [(blk, s) for blk, s in SA if s not in bset]
b_rest = [(blk, s) for blk, s in SB if s not in aset]
# one-to-one pairing of the leftovers, best similarity first
cands = []
for i, (_, s) in enumerate(a_rest):
    for j, (_, t) in enumerate(b_rest):
        if min(len(s), len(t)) * 2.5 < max(len(s), len(t)):
            continue
        r = ratio(s, t)
        if r >= 0.6:
            cands.append((r, i, j))
cands.sort(reverse=True)
pa, pb = {}, {}
for r, i, j in cands:
    if i not in pa and j not in pb:
        pa[i] = (j, r); pb[j] = (i, r)
removed = [(blk, s) for i, (blk, s) in enumerate(a_rest) if i not in pa]
added = [(blk, s) for j, (blk, s) in enumerate(b_rest) if j not in pb]
edited = [(a_rest[i][0], a_rest[i][1], b_rest[j][0], b_rest[j][1], r) for i, (j, r) in sorted(pa.items())]
kept = [(blk, s) for blk, s in SA if s in bset and blk in bset[s]]
moved = [(blk, s, bset[s]) for blk, s in SA if s in bset and blk not in bset[s]]


def first_seen(s):
    for v in vs:
        if v.label != B.label and s in TAG.sub("", v.ws):
            return v.label
    return None


def carried_by(s):
    return [m for m, v in LATEST.items() if s in TAG.sub("", v.ws)]


def wdiff(a, b):
    ta, tb = a.split(), b.split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes():
        if op == "equal":
            seg = ta[i1:i2]
            out.append(" ".join(seg) if len(seg) <= 12 else " ".join(seg[:5]) + " […] " + " ".join(seg[-5:]))
        else:
            if i2 > i1:
                out.append("[-" + " ".join(ta[i1:i2]) + "-]")
            if j2 > j1:
                out.append("{+" + " ".join(tb[j1:j2]) + "+}")
    return " ".join(out)


if MODE == "summary":
    wa, wb = words(s for _, s in SA), words(s for _, s in SB)
    print("5.1 (10-30): %d sentences, %d words (tags excluded) | 5.2: %d sentences, %d words" % (len(SA), wa, len(SB), wb))
    print("5.1 side: kept in place %d / %d w (%.1f%%) | moved to another block %d / %d w | edited %d / %d w (%.1f%%) | removed %d / %d w (%.1f%%)" % (
        len(kept), words(s for _, s in kept), 100.0 * words(s for _, s in kept) / wa, len(moved), words(s for _, s, _ in moved),
        len(edited), words(e[1] for e in edited), 100.0 * words(e[1] for e in edited) / wa, len(removed), words(s for _, s in removed), 100.0 * words(s for _, s in removed) / wa))
    kb = [(blk, s) for blk, s in SB if s in aset]
    print("5.2 side: identical to a 5.1 sentence %d / %d w (%.1f%%) | edited %d / %d w (%.1f%%) | added %d / %d w (%.1f%%)" % (
        len(kb), words(s for _, s in kb), 100.0 * words(s for _, s in kb) / wb, len(edited), words(e[3] for e in edited), 100.0 * words(e[3] for e in edited) / wb,
        len(added), words(s for _, s in added), 100.0 * words(s for _, s in added) / wb))
    blocks = []
    for blk, _ in SA + SB:
        if blk not in blocks:
            blocks.append(blk)
    print("\n%-38s %6s %6s | %5s %5s %5s | %5s %5s" % ("block", "5.1 w", "5.2 w", "kept", "ed>", "add", "rem", "<ed"))
    for blk in blocks:
        print("%-38s %6d %6d | %5d %5d %5d | %5d %5d" % (blk, words(s for b, s in SA if b == blk), words(s for b, s in SB if b == blk),
              words(s for b, s in SB if b == blk and s in aset), words(e[3] for e in edited if e[2] == blk), words(s for b, s in added if b == blk),
              words(s for b, s in removed if b == blk), words(e[1] for e in edited if e[0] == blk)))
    src = {}
    for blk, s in added:
        fs = first_seen(s)
        key = ("elsewhere since " + fs) if fs else "new in 5.2"
        src.setdefault(key, [0, 0]); src[key][0] += 1; src[key][1] += len(s.split())
    print("\nadded sentences by provenance:")
    for key, (c, w) in sorted(src.items(), key=lambda x: -x[1][1]):
        print("   %4d w  %3d sentences  %s" % (w, c, key))
    gone = [(blk, s) for blk, s in removed if not carried_by(s)]
    print("\nremoved sentences: still in another model's latest entry %d / %d w; in none %d / %d w" % (
        len(removed) - len(gone), words(s for _, s in removed) - words(s for _, s in gone), len(gone), words(s for _, s in gone)))
elif MODE == "removed":
    for blk, s in removed:
        cb = carried_by(s)
        print("[R] <%s> %dw | still in: %s\n    %s" % (blk, len(s.split()), ", ".join(cb) if cb else "NONE", s))
elif MODE == "added":
    for blk, s in added:
        fs = first_seen(s)
        print("[A] <%s> %dw | %s\n    %s" % (blk, len(s.split()), ("since %s; latest: %s" % (fs, ", ".join(carried_by(s)))) if fs else "NEW", s))
elif MODE == "edited":
    for ba, a, bb, b, r in edited:
        fs = first_seen(b)
        print("[E %.2f] <%s>%s %d->%dw%s\n    %s" % (r, ba, "" if ba == bb else " -> <%s>" % bb, len(a.split()), len(b.split()), (" | 5.2 wording since " + fs) if fs else "", wdiff(a, b)))
elif MODE == "moved":
    for blk, s, to in moved:
        print("[M] <%s> -> <%s> %dw\n    %s" % (blk, ",".join(to), len(s.split()), s))

# "current pages": the other model pages that received an entry in October 2026
CURRENT = {m: v for m, v in LATEST.items() if v.date >= "2026-10-01"}
A0 = L["F5.1@260901"]


def current_with(s):
    return [m for m, v in CURRENT.items() if s in TAG.sub("", v.ws)]


if MODE == "stats":
    print("current pages (%d): %s" % (len(CURRENT), ", ".join("%s %s" % (m, v.date[5:]) for m, v in CURRENT.items())))
    new = [(b, s) for b, s in added if not first_seen(s)]
    old = [(b, s) for b, s in added if first_seen(s)]
    print("added: %d sentences / %d w = new wording %d / %d w + wording that already existed elsewhere %d / %d w" % (
        len(added), words(s for _, s in added), len(new), words(s for _, s in new), len(old), words(s for _, s in old)))
    en = [e for e in edited if not first_seen(e[3])]
    eo = [e for e in edited if first_seen(e[3])]
    print("edited: %d pairs; 5.2 wording new %d (5.2 side %d w) | 5.2 wording already existed elsewhere %d (5.2 side %d w)" % (
        len(edited), len(en), words(e[3] for e in en), len(eo), words(e[3] for e in eo)))
    rc = [(b, s) for b, s in removed if current_with(s)]
    rn = [(b, s) for b, s in removed if not current_with(s)]
    print("removed: %d sentences / %d w = still on another current page %d / %d w + on no other current page %d / %d w" % (
        len(removed), words(s for _, s in removed), len(rc), words(s for _, s in rc), len(rn), words(s for _, s in rn)))
    three = [(b, s) for b, s in removed if all(m in current_with(s) for m in ("Opus 5.5", "Sonnet 5.5", "Haiku 5.5"))]
    print("   of which still on all three 5.5 pages: %d / %d w" % (len(three), words(s for _, s in three)))
    for b, s in three:
        print("      <%s> %s" % (b, s[:90]))
    young = [(b, s) for b, s in removed if s not in TAG.sub("", A0.ws)]
    print("removed sentences that 5.1 only gained on 10-30: %d / %d w" % (len(young), words(s for _, s in young)))
    for b, s in young:
        print("      <%s> %s" % (b, s[:110]))
    print("removed and on no other current page, by block:")
    for blk in sorted(set(b for b, _ in rn)):
        print("   %-36s %2d sentences %4d w" % (blk, sum(1 for b, _ in rn if b == blk), words(s for b, s in rn if b == blk)))
    print("new wording by block:")
    for blk in sorted(set(b for b, _ in new)):
        print("   %-36s %2d sentences %4d w" % (blk, sum(1 for b, _ in new if b == blk), words(s for b, s in new if b == blk)))
    words_b_total = words(s for _, s in SB)
    adopted = words(s for _, s in old) + words(e[3] for e in eo)
    fresh = words(s for _, s in new) + words(e[3] for e in en)
    print("5.2 text that differs from 5.1: %d w; of it adopted from existing wording %d w (%.1f%%), fresh wording %d w (%.1f%%)" % (
        adopted + fresh, adopted, 100.0 * adopted / (adopted + fresh), fresh, 100.0 * fresh / (adopted + fresh)))


def corpus_sentences():
    """unique sentence -> first version label, over every version except 5.2"""
    out = {}
    for v in vs:
        if v.label == B.label:
            continue
        for _, s in sentences(v):
            out.setdefault(s, v.label)
    return out


def nearest(s, corpus):
    best, lab, txt = 0.0, None, None
    for t, label in corpus.items():
        if min(len(s), len(t)) * 2 < max(len(s), len(t)):
            continue
        sm = difflib.SequenceMatcher(None, s, t, autojunk=False)
        if sm.real_quick_ratio() <= best or sm.quick_ratio() <= best:
            continue
        r = sm.ratio()
        if r > best:
            best, lab, txt = r, label, t
    return best, lab, txt


if MODE == "near":
    corpus = corpus_sentences()
    print("unique earlier sentences:", len(corpus))
    fresh_w = adapted_w = 0
    rows = [("A", b, s) for b, s in added if not first_seen(s)] + [("E", e[2], e[3]) for e in edited if not first_seen(e[3])]
    for kind, blk, s in rows:
        r, lab, txt = nearest(s, corpus)
        w = len(s.split())
        if r >= 0.8:
            adapted_w += w
        else:
            fresh_w += w
        print("[%s %s %.2f %-13s] <%s> %dw %s" % (kind, "adapted" if r >= 0.8 else "FRESH  ", r, lab, blk[:14], w, s[:70]))
    print("fresh wording %d w | adapted from an earlier sentence (>= 0.8) %d w" % (fresh_w, adapted_w))


def nice(label):
    m = re.fullmatch(r"([HOSF])([\d.]+)@(\d\d)(\d\d)(\d\d)([ti]?)", label)
    fam = {"H": "Haiku", "O": "Opus", "S": "Sonnet", "F": "Fable"}[m.group(1)]
    var = {"t": " text-only", "i": " text+images", "": ""}[m.group(6)]
    return "%s %s%s（20%s-%s-%s）" % (fam, m.group(2), var, m.group(3), m.group(4), m.group(5))


def full_wdiff(a, b):
    ta, tb = a.split(), b.split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes():
        if op == "equal":
            out.append(" ".join(ta[i1:i2]))
        else:
            if i2 > i1:
                out.append("[-" + " ".join(ta[i1:i2]) + "-]")
            if j2 > j1:
                out.append("{+" + " ".join(tb[j1:j2]) + "+}")
    return " ".join(out)


if MODE == "md":
    corpus = corpus_sentences()
    P = print
    P("## 附錄 A：Fable 5.1 有、Fable 5.2 沒有的句子（%d 句，%d 字）\n" % (len(removed), words(s for _, s in removed)))
    P("每句後面標出它還在哪些其他現行模型頁（2026 年 10 月有更新的 11 頁）的最新條目裡逐字出現。「10-30 才加」表示這一句是 Fable 5.1 在 10-30 條目才加上的。\n")
    for k, (blk, s) in enumerate(removed, 1):
        cw = current_with(s)
        P("**A-%02d**　`%s`　%d 字　其他現行頁：%s%s\n" % (k, blk, len(s.split()), "、".join(cw) if cw else "無", "" if s in TAG.sub("", A0.ws) else "　（10-30 才加）"))
        P("> %s\n" % s)
    P("## 附錄 B：Fable 5.2 有、Fable 5.1 沒有的句子（%d 句，%d 字）\n" % (len(added), words(s for _, s in added)))
    P("來源分三種：「沿用」是這一句在更早的版本就逐字存在；「改自」是與某個更早的句子相似度 0.8 以上；「新寫」是找不到相似度 0.8 以上的舊句。\n")
    for k, (blk, s) in enumerate(added, 1):
        fs = first_seen(s)
        if fs:
            src = "沿用，首見 %s；其他現行頁：%s" % (nice(fs), "、".join(current_with(s)) or "無")
        else:
            r, lab, _ = nearest(s, corpus)
            src = ("改自 %s 的句子（相似度 %.2f）" % (nice(lab), r)) if r >= 0.8 else ("新寫（最接近的舊句相似度 %.2f）" % r)
        P("**B-%02d**　`%s`　%d 字　%s\n" % (k, blk, len(s.split()), src))
        P("> %s\n" % s)
    P("## 附錄 C：改寫的句對（%d 對）\n" % len(edited))
    P("格式：`[-5.1 的字-]{+5.2 的字+}`。「5.2 寫法首見」表示改寫後的句子在更早的版本就逐字存在，也就是換用了既有的寫法。\n")
    for k, (ba, a, bb, b, r) in enumerate(edited, 1):
        fs = first_seen(b)
        P("**C-%02d**　`%s`%s　相似度 %.2f　%s\n" % (k, ba, "" if ba == bb else " → `%s`" % bb, r, ("5.2 寫法首見 " + nice(fs)) if fs else "5.2 寫法是新的"))
        P("> %s\n" % full_wdiff(a, b))


if MODE == "base":
    O, H = L["O5.5@261027"], L["H5.5@261026"]
    ot, ht = TAG.sub("", O.ws), TAG.sub("", H.ws)
    osent = [s for _, s in sentences(O)]

    def near_in(s, pool):
        best = 0.0
        for t in pool:
            if min(len(s), len(t)) * 2 < max(len(s), len(t)):
                continue
            sm = difflib.SequenceMatcher(None, s, t, autojunk=False)
            if sm.quick_ratio() <= best:
                continue
            best = max(best, sm.ratio())
        return best

    side = [("added", s) for _, s in added] + [("edited", e[3]) for e in edited]
    cnt = {"in Opus 5.5 (10-27)": 0, "not in Opus 5.5 but in Haiku 5.5 (10-26)": 0, "in neither": 0}
    for kind, s in side:
        w = len(s.split())
        if s in ot:
            cnt["in Opus 5.5 (10-27)"] += w
        elif s in ht:
            cnt["not in Opus 5.5 but in Haiku 5.5 (10-26)"] += w
        else:
            cnt["in neither"] += w
    tot = sum(cnt.values())
    print("5.2 text that differs from 5.1 (%d w):" % tot)
    for k, w in cnt.items():
        print("   %-44s %5d w  %.1f%%" % (k, w, 100.0 * w / tot))
    print("\nremoved 5.1 sentences vs the Opus 5.5 (10-27) text:")
    absent, present = [], []
    for blk, s in removed:
        r = 1.0 if s in ot else near_in(s, osent)
        (present if r >= 0.9 else absent).append((blk, s, r))
    print("   Opus 5.5 does not have it either: %d sentences / %d w" % (len(absent), words(s for _, s, _ in absent)))
    print("   Opus 5.5 has it (verbatim or >= 0.9), 5.2 does not: %d sentences / %d w" % (len(present), words(s for _, s, _ in present)))
    for blk, s, r in present:
        print("      %.2f <%s> %dw %s" % (r, blk[:16], len(s.split()), s[:84]))
    print("\nOpus 5.5 (10-27) sentences that Fable 5.2 lacks (verbatim):")
    bt = TAG.sub("", B.ws)
    lack = [(blk, s) for blk, s in sentences(O) if s not in bt]
    print("   %d sentences / %d w" % (len(lack), words(s for _, s in lack)))
    by = {}
    for blk, s in lack:
        by.setdefault(blk, [0, 0]); by[blk][0] += 1; by[blk][1] += len(s.split())
    for blk, (c, w) in by.items():
        print("      %-36s %2d sentences %4d w" % (blk, c, w))
