"""把目標版本中「沒有逐字前例」的行再分成：小幅改寫（與任一更早行相似度>=0.8）與真正新增。
用法：python -I newness.py <target> <older files...>
"""
import difflib, os, sys
def lines(p):
    return [l.strip() for l in open(p, encoding="utf-8").read().split("\n") if l.strip()]
target = sys.argv[1]
old = []
for p in sys.argv[2:]:
    if os.path.abspath(p) != os.path.abspath(target):
        old.extend(lines(p))
oldset = set(old)
tot = verb = edit = new = 0
news = []
for ln in lines(target):
    w = len(ln.split()); tot += w
    if ln in oldset:
        verb += w; continue
    best = max((difflib.SequenceMatcher(None, ln, o, autojunk=False).ratio() for o in old if abs(len(o) - len(ln)) < 0.6 * len(ln) + 20), default=0)
    if best >= 0.8:
        edit += w
    else:
        new += w; news.append((w, round(best, 2), ln))
print(os.path.basename(target), "total", tot, "| verbatim %d (%.1f%%) | minor-edit %d (%.1f%%) | new %d (%.1f%%)" % (verb, 100*verb/tot, edit, 100*edit/tot, new, 100*new/tot))
for w, b, ln in news:
    print("   new %4d w (best sim %.2f): %s" % (w, b, ln[:110]))
