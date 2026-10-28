"""逐行血緣：目標版本的每一行（段落／條列）是否逐字出現在候選前代版本中。
用法：python -I lineage.py <target> <labelA>=<fileA> [<labelB>=<fileB> ...] [--any=<file> ...]
輸出：各來源組合的字數與比例；新行（無一命中）另外列出前 60 字元。
--any= 檔案只用來判斷「是否在任何更早版本出現過」（回流舊句），不列入組合標籤。
"""
import os
import sys
from collections import OrderedDict


def lines(p):
    return [ln.strip() for ln in open(p, encoding="utf-8").read().split("\n") if ln.strip()]


target = sys.argv[1]
srcs = OrderedDict()
anys = []
for a in sys.argv[2:]:
    if a.startswith("--any="):
        anys.append(a[6:])
    else:
        k, v = a.split("=", 1)
        srcs[k] = set(lines(v))
older = set()
for p in anys:
    older |= set(lines(p))

tally = OrderedDict()
new_lines = []
total = 0
for ln in lines(target):
    w = len(ln.split())
    total += w
    hit = [k for k, s in srcs.items() if ln in s]
    if hit:
        key = "+".join(hit)
    elif ln in older:
        key = "older-version"
    else:
        key = "NEW/edited"
        new_lines.append((w, ln))
    tally[key] = tally.get(key, 0) + w

print("target:", os.path.basename(target), "total words:", total)
for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
    print("  %-28s %5d  %5.1f%%" % (k, v, 100.0 * v / total))
print("  -- NEW/edited lines (words: first 90 chars) --")
for w, ln in new_lines:
    print("   %4d: %s" % (w, ln[:90]))
