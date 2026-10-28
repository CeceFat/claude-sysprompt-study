"""全站引文查核：每一句英文引文都必須能在證據包的版本檔裡逐字找到。

檢查兩種標記：
1. <div class="q" data-file="X" data-term="T">：T 必須出現在 X（不分大小寫）；
   引文本文以「…」或「...」切段，每段都必須出現在 X。
2. <span class="en">…</span>：每段（同樣以 … / ... 切開）必須出現在至少一個版本檔；
   引自 overview 的句子不在版本檔，改在 evidence/diffs/ 找（去掉 [-舊-]{+新+} 標記與 markdown 連結語法）。
比對前先做 HTML 反跳脫、合併連續空白。
用法：python -I evidence/tools/verify_quotes.py <repo_root>
"""
import glob
import html
import os
import re
import sys

ROOT = sys.argv[1]
VDIR = os.path.join(ROOT, "evidence", "versions")
texts = {os.path.basename(p): open(p, encoding="utf-8").read() for p in glob.glob(os.path.join(VDIR, "*.txt"))}
norm = lambda s: re.sub(r"\s+", " ", html.unescape(s)).strip().lower()
ntexts = {k: norm(v) for k, v in texts.items()}
alltext = "\n".join(ntexts.values())
for p in glob.glob(os.path.join(ROOT, "evidence", "diffs", "*.diff")):
    d = open(p, encoding="utf-8").read()
    d = re.sub(r"\[-|-\]|\{\+|\+\}", "", d)
    d = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", d)
    alltext += "\n" + norm(d)
SPLIT = re.compile(r"\s*(?:…|\.\.\.)\s*")
TAG = re.compile(r"<[^>]+>")

fails = 0
checked = 0
for page in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
    src = open(page, encoding="utf-8").read()
    name = os.path.basename(page)
    for m in re.finditer(r'<div class="q"([^>]*)>(.*?)</div>', src, re.S):
        attrs, body = m.group(1), m.group(2)
        f = re.search(r'data-file="([^"]+)"', attrs)
        if not f:
            continue
        f = f.group(1)
        if f not in ntexts:
            print("MISSING FILE", name, f); fails += 1; continue
        t = re.search(r'data-term="([^"]*)"', attrs)
        if t and norm(t.group(1)) not in ntexts[f]:
            print("TERM NOT FOUND", name, f, repr(html.unescape(t.group(1))[:70])); fails += 1
        body = TAG.sub("", re.sub(r"<cite>.*?</cite>", "", body, flags=re.S))
        for seg in SPLIT.split(norm(body)):
            seg = seg.strip(" .")
            if len(seg) < 12:
                continue
            checked += 1
            if seg not in ntexts[f]:
                print("QUOTE NOT IN FILE", name, f, repr(seg[:80])); fails += 1
    for m in re.finditer(r'<span class=["\']en["\']>(.*?)</span>', src, re.S):
        body = TAG.sub("", m.group(1)).replace('\\"', '"')  # quiz.html 的引文寫在 JS 字串裡
        for seg in SPLIT.split(norm(body)):
            seg = seg.strip(" .\"「」")
            if len(seg) < 12:
                continue
            checked += 1
            if seg not in alltext:
                print("EN NOT FOUND", name, repr(seg[:90])); fails += 1
print("segments checked:", checked, "failures:", fails)
sys.exit(1 if fails else 0)
