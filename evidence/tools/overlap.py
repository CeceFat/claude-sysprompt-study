"""三個 5.5 版本之間逐行（段落）逐字共用的比例（以字數計）。"""
import sys, os
def L(p): return [l.strip() for l in open(p, encoding="utf-8").read().split("\n") if l.strip()]
fs = sys.argv[1:]
S = [set(L(f)) for f in fs]
names = [os.path.basename(f).split("__")[0] + "_" + os.path.basename(f).split("__")[1][:6] for f in fs]
allshared = set.intersection(*S)
for i, f in enumerate(fs):
    tot = sum(len(l.split()) for l in L(f))
    sh = sum(len(l.split()) for l in L(f) if l in allshared)
    uniq = sum(len(l.split()) for l in L(f) if all(l not in S[j] for j in range(len(fs)) if j != i))
    print("%-28s total %4d | shared-by-all %4d (%.1f%%) | unique-to-this %4d (%.1f%%)" % (names[i], tot, sh, 100*sh/tot, uniq, 100*uniq/tot))
