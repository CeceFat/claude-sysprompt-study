"""Check quiz.html against the version files. Read-only.

For every question (<section class="quiz-q">):
  * exactly four options, data-a within 0..3, the "further reading" target (data-ref) exists,
    and its #anchor exists in that page.
For every block quote (<div class="q" data-file= data-cite= data-in=>):
  * the quote is verbatim (case-sensitive, whitespace-normalised) in the cited file;
  * the cite "Model / YYYY-MM-DD / block" matches the file and the quote lies inside that block;
  * data-in lists exactly those of the four current prompts that contain the quote
    (O = Opus 5.5, F = Fable 5.2, S = Sonnet 5.5, H = Haiku 5.5; each one's latest entry).
  * the models named in the question's kicker ("四個現行模型" = all four) all carry the first quote.
For every inline quote (<span class="en">): where it is found (current prompts, other versions,
  overview diffs, external excerpts), for a human to compare with what the sentence around it says.
Also prints each "第 N 題" cross-reference with the question it points to.

Usage: python -I -B a6_quiz.py <repo_root> [page]
"""
import glob
import html
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import facts  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

ROOT = sys.argv[1]
PAGE = sys.argv[2] if len(sys.argv) > 2 else "quiz.html"
CURRENT = [("O", "claude-opus-5-5"), ("F", "claude-fable-5-2"), ("S", "claude-sonnet-5-5"), ("H", "claude-haiku-5-5")]
NAMES = [("O", "Opus 5.5"), ("F", "Fable 5.2"), ("S", "Sonnet 5.5"), ("H", "Haiku 5.5")]

norm = lambda s: re.sub(r"\s+", " ", html.unescape(s)).strip()
strip_tags = lambda s: re.sub(r"<[^>]+>", "", s)

vs, _ = facts.load(ROOT)
by_file = {v.stem + ".txt": v for v in vs}
cur = {}
for code, slug in CURRENT:
    cands = [v for v in vs if v.stem.startswith(slug + "__")]
    cur[code] = max(cands, key=lambda v: v.date)
print("current prompts:", ", ".join("%s=%s" % (c, cur[c].label) for c, _ in CURRENT))

other = ""
for p in glob.glob(os.path.join(ROOT, "evidence", "diffs", "*.diff")):
    d = io.open(p, encoding="utf-8").read()
    d = re.sub(r"\[-|-\]|\{\+|\+\}", "", d)
    other += "\n" + norm(re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", d))
ext = "\n".join(norm(io.open(p, encoding="utf-8").read()) for p in glob.glob(os.path.join(ROOT, "evidence", "external", "*.txt")))

src = io.open(os.path.join(ROOT, PAGE), encoding="utf-8").read()
fails = 0


def fail(msg):
    global fails
    fails += 1
    print("   FAIL", msg)


secs = re.findall(r'<section class="quiz-q"([^>]*)>(.*?)</section>', src, re.S)
print("questions:", len(secs))
dist = [0, 0, 0, 0]
nq = nen = 0
for n, (attrs, body) in enumerate(secs, 1):
    a = re.search(r'data-a="(\d+)"', attrs)
    ref = re.search(r'data-ref="([^"]+)"', attrs)
    reft = re.search(r'data-ref-t="([^"]+)"', attrs)
    kick = re.search(r'<p class="kicker">(.*?)</p>', body, re.S)
    stem = re.search(r'<p class="stem">(.*?)</p>', body, re.S)
    opts = re.findall(r'<label class="opt">(.*?)</label>', body, re.S)
    print("\nQ%-2d [%s] %s" % (n, norm(strip_tags(kick.group(1))) if kick else "?", norm(strip_tags(stem.group(1)))[:46] if stem else "?"))
    if not (a and ref and reft and kick and stem):
        fail("Q%d: missing data-a / data-ref / data-ref-t / kicker / stem" % n)
        continue
    ai = int(a.group(1))
    if len(opts) != 4:
        fail("Q%d: %d options" % (n, len(opts)))
    if not 0 <= ai < len(opts):
        fail("Q%d: data-a out of range" % n)
    else:
        dist[ai] += 1
        print("   answer %d: %s" % (ai, norm(strip_tags(opts[ai]))[:60]))
    page, _, anchor = ref.group(1).partition("#")
    ppath = os.path.join(ROOT, page)
    if not os.path.exists(ppath):
        fail("Q%d: data-ref target %s does not exist" % (n, page))
    elif anchor and ('id="%s"' % anchor) not in io.open(ppath, encoding="utf-8").read():
        fail("Q%d: anchor #%s not found in %s" % (n, anchor, page))
    if body.count('class="expl"') != 1 or "<b>怎麼用</b>" not in body:
        fail("Q%d: needs exactly one .expl with a 怎麼用 note" % n)

    # models named in the kicker must all carry the first block quote
    ktext = norm(strip_tags(kick.group(1)))
    named = ["O", "F", "S", "H"] if "四個現行模型" in ktext else [c for c, nm in NAMES if nm in ktext]
    first = True
    for qattrs, qbody in re.findall(r'<div class="q"([^>]*)>(.*?)</div>', body, re.S):
        nq += 1
        if first:
            first = False
            got = (re.search(r'data-in="([^"]*)"', qattrs) or [None, ""])[1].split()
            if any(c not in got for c in named):
                fail("Q%d: kicker names %s but the first quote is only in %s" % (n, named, got))
        f = re.search(r'data-file="([^"]+)"', qattrs)
        cite = re.search(r'data-cite="([^"]+)"', qattrs)
        din = re.search(r'data-in="([^"]*)"', qattrs)
        text = norm(strip_tags(qbody))
        if not (f and cite and din is not None):
            fail("Q%d: quote without data-file / data-cite / data-in: %s" % (n, text[:50]))
            continue
        v = by_file.get(f.group(1))
        if v is None:
            fail("Q%d: no such version file %s" % (n, f.group(1)))
            continue
        if not v.has(text):
            fail("Q%d: quote not verbatim in %s: %s" % (n, v.label, text[:60]))
        parts = [p.strip() for p in html.unescape(cite.group(1)).split("/")]
        if len(parts) != 3 or parts[0] != v.model or parts[1] != v.date:
            fail("Q%d: cite %r does not match file %s (%s / %s)" % (n, cite.group(1), v.label, v.model, v.date))
        else:
            sec = v.section(parts[2])
            if sec is None or text not in norm(sec):
                fail("Q%d: quote is not inside <%s> of %s" % (n, parts[2], v.label))
        actual = [c for c, _ in CURRENT if cur[c].has(text)]
        declared = din.group(1).split()
        flag = "ok" if actual == declared else "MISMATCH declared=%s" % declared
        if actual != declared:
            fail("Q%d: data-in %s but actually in %s: %s" % (n, declared, actual, text[:50]))
        nall = len(facts.trace(vs, text))
        print("   q  %-9s in=%-8s all=%2d %s | %s" % (v.label, "".join(actual) or "-", nall, flag, text[:70]))

    for m in re.finditer(r'<span class=["\']en["\']>(.*?)</span>', body, re.S):
        nen += 1
        text = norm(strip_tags(m.group(1))).strip(' ."')
        actual = "".join(c for c, _ in CURRENT if cur[c].has(text))
        nall = len(facts.trace(vs, text))
        where = []
        if actual:
            where.append("current=" + actual)
        if nall:
            where.append("versions=%d" % nall)
            if not actual:
                where.append("(" + facts.fmt_set(facts.trace(vs, text), 4) + ")")
        if not nall and text in other:
            where.append("overview (via diffs)")
        if text in ext:
            where.append("external")
        if not where:
            fail("Q%d: inline quote found nowhere: %s" % (n, text[:60]))
        print("   en %-40s | %s" % (" ".join(where), text[:70]))

    for m in re.finditer(r"第 (\d+) 題", strip_tags(body)):
        t = int(m.group(1))
        if not 1 <= t <= len(secs):
            fail("Q%d: cross-reference to question %d, which does not exist" % (n, t))
        else:
            tk = re.search(r'<p class="stem">(.*?)</p>', secs[t - 1][1], re.S)
            print("   xref -> Q%d: %s" % (t, norm(strip_tags(tk.group(1)))[:40]))

count = re.search(r'id="progress">0 / (\d+) 作答', src)
if not count or int(count.group(1)) != len(secs):
    fail("progress counter does not say %d" % len(secs))
for m in re.finditer(r"(\d+) 題", src.split("<div id=\"qs\">")[0]):
    if int(m.group(1)) != len(secs):
        fail("page header says %s 題 but there are %d questions" % (m.group(1), len(secs)))

print("\nanswer positions (0..3):", dist)
print("block quotes: %d | inline quotes: %d | failures: %d" % (nq, nen, fails))
sys.exit(1 if fails else 0)
