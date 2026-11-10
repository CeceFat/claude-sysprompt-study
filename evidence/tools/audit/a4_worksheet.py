"""Audit A4: turn a site page into an annotated plain-text worksheet.

Every English quotation is annotated with the exact set of version files that contain it
(case-sensitive, whitespace-normalised), so that the attribution written around it can be checked
by reading. Unlike the site's own verify_quotes.py this is case-sensitive, reports *which*
versions contain an inline quote, flags quotes that cross a paragraph boundary, and lists English
runs that are not marked up as quotes at all.

Usage: python -I a4_worksheet.py <repo_root> <page.html> [<out.txt>]
"""
import html
import os
import re
import sys
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import facts  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ROOT, PAGE = sys.argv[1], sys.argv[2]
OUT = sys.argv[3] if len(sys.argv) > 3 else None
vs, M = facts.load(ROOT)
bystem = {v.stem: v for v in vs}

extra = ""
for d in ("diffs", "external"):
    p = os.path.join(ROOT, "evidence", d)
    for f in sorted(os.listdir(p)):
        t = open(os.path.join(p, f), encoding="utf-8", newline="").read()
        if d == "diffs":
            t = re.sub(r"\[-|-\]|\{\+|\+\}", "", t)
            t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
        extra += "\n" + re.sub(r"\s+", " ", t)

SPLIT = re.compile(r"\s*(?:…|\.\.\.)\s*")


def annotate(seg):
    seg = re.sub(r"\s+", " ", seg).strip()
    hits = [v for v in vs if v.has(seg)]
    if hits:
        cross = [v.label for v in hits if not v.in_one_line(seg)]
        note = "n=%d: %s" % (len(hits), facts.fmt_set(hits, 12))
        if cross:
            note += " ‼CROSSES-PARAGRAPH in " + ",".join(cross[:3])
        return note
    ci = [v for v in vs if v.has(seg, ci=True)]
    if ci:
        return "‼CASE-MISMATCH (ci n=%d: %s)" % (len(ci), facts.fmt_set(ci, 6))
    if seg in extra:
        return "not in versions; found in diffs/external"
    if seg.lower() in extra.lower():
        return "‼CASE-MISMATCH; found (ci) in diffs/external"
    return "‼NOT FOUND ANYWHERE"


BLOCK = {"p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "table", "ul", "ol", "section", "header", "footer",
         "nav", "blockquote", "details", "summary", "figure", "figcaption", "main", "article", "thead", "tbody", "br", "title", "dt", "dd", "dl"}
CELL = {"td", "th"}


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.cur = []
        self.stack = []  # (tag, kind, buf, attrs)
        self.skip = None
        self.raw_script = []
        self.in_script = False
        self.nq = self.nen = 0

    def flush(self):
        s = re.sub(r"[ \t\r\n]+", " ", "".join(self.cur)).strip()
        if s:
            self.out.append(s)
        self.cur = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script":
            self.in_script = True
            self.flush()
            if a.get("src"):
                self.out.append("[script src=%s]" % a["src"])
            return
        if tag == "style":
            self.skip = "style"
            return
        cls = (a.get("class") or "").split()
        if tag == "span" and "en" in cls:
            self.stack.append(("span", "en", [], a))
            return
        if tag == "div" and "q" in cls and a.get("data-file"):
            self.flush()
            self.stack.append(("div", "q", [], a))
            return
        if self.stack:
            # nested tag inside a captured element
            self.stack.append((tag, "nest", None, a))
            if tag == "cite":
                self.stack[-1] = (tag, "cite", None, a)
            return
        if tag in BLOCK:
            self.flush()
            if tag in ("h1", "h2", "h3", "h4"):
                self.cur.append("\n%s " % ("#" * int(tag[1])))
            if cls and tag in ("div", "section", "p", "li"):
                self.cur.append("[.%s] " % ".".join(cls))
            if a.get("id") and tag in ("h1", "h2", "h3", "h4", "section", "div"):
                self.cur.append("{#%s} " % a["id"])
        elif tag in CELL:
            self.cur.append(" | ")
        elif tag == "a" and a.get("href"):
            self.cur.append("⟨a:%s⟩" % a["href"])
        elif tag == "code":
            self.cur.append("`")
        if tag == "div" and a.get("data-file") and "q" not in cls:
            self.cur.append("[data-file=%s] " % a["data-file"])

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False
            if self.raw_script:
                self.out.append("[inline script follows]")
                self.out.append("".join(self.raw_script).strip())
                self.raw_script = []
            return
        if tag == "style":
            self.skip = None
            return
        if self.stack:
            t, kind, buf, a = self.stack[-1]
            if kind in ("nest", "cite"):
                if t == tag:
                    self.stack.pop()
                return
            if kind == "en" and tag == "span":
                self.stack.pop()
                txt = re.sub(r"\s+", " ", "".join(buf)).strip()
                self.nen += 1
                notes = []
                for seg in SPLIT.split(txt):
                    seg = seg.strip(" \"“”「」")
                    if len(seg) < 4:
                        continue
                    notes.append(annotate(seg))
                target = self.stack[-1][2] if self.stack and self.stack[-1][2] is not None else self.cur
                target.append("«%s»⟦%s⟧" % (txt, " ‖ ".join(notes)))
                return
            if kind == "q" and tag == "div":
                self.stack.pop()
                txt = re.sub(r"\s+", " ", "".join(buf)).strip()
                self.nq += 1
                f = a["data-file"]
                stem = f[:-4] if f.endswith(".txt") else f
                v = bystem.get(stem)
                lines = ["Q#%d file=%s cite=%r term=%r" % (self.nq, v.label if v else "‼MISSING FILE " + f, a.get("data-cite"), a.get("data-term"))]
                lines.append("   text: " + txt)
                if v:
                    if a.get("data-term") is not None:
                        term = a["data-term"]
                        lines.append("   term in cited file: %s" % ("yes" if v.has(term) else ("‼ci-only" if v.has(term, True) else "‼NO")))
                    for seg in SPLIT.split(txt):
                        seg = seg.strip(" \"“”「」")
                        if len(seg) < 4:
                            continue
                        ok = v.has(seg)
                        others = [x for x in vs if x.has(seg)]
                        first = others[0].label if others else "-"
                        flag = "ok" if ok else ("‼CASE-MISMATCH in cited file" if v.has(seg, True) else "‼NOT IN CITED FILE")
                        if ok and not v.in_one_line(seg):
                            flag += " ‼CROSSES-PARAGRAPH"
                        lines.append("   seg %s | present in n=%d versions, earliest %s; set: %s | «%s»" % (flag, len(others), first, facts.fmt_set(others, 9), seg[:70] + ("…" if len(seg) > 70 else "")))
                self.flush()
                self.out.append("\n".join(lines))
                return
            return
        if tag in BLOCK:
            self.flush()
        elif tag == "code":
            self.cur.append("`")
        elif tag == "a":
            self.cur.append("⟨/a⟩")

    def handle_data(self, data):
        if self.in_script:
            self.raw_script.append(data)
            return
        if self.skip:
            return
        if self.stack:
            # find nearest capturing element
            for t, kind, buf, a in reversed(self.stack):
                if kind == "cite":
                    return
                if buf is not None:
                    buf.append(data)
                    return
            return
        self.cur.append(data)


src = open(os.path.join(ROOT, PAGE), encoding="utf-8", newline="").read().replace("\r\n", "\n")
p = P()
p.feed(src)
p.flush()
text = "\n".join(p.out)

# English runs that are not inside a marked quote
unmarked = []
plain = re.sub(r"«[^»]*»⟦[^⟧]*⟧", " ", text)
plain = "\n".join(l for l in plain.split("\n") if not l.startswith("Q#") and not l.startswith("   "))
for m in re.finditer(r"[A-Za-z][A-Za-z'’\-]*(?:[ ,;:]+[A-Za-z0-9'’\-<>_/().]+){4,}", plain):
    s = m.group(0).strip()
    hits = [v for v in vs if v.has(s)]
    unmarked.append((s, len(hits), facts.fmt_set(hits, 6) if hits else ("ci:" + facts.fmt_set([v for v in vs if v.has(s, True)], 4))))

hdr = ["WORKSHEET for %s  (q blocks: %d, en spans: %d)" % (PAGE, p.nq, p.nen),
       "label = <Family initial><version>@<yymmdd><t|i for text-only / text+images>; n = number of version files containing the exact string",
       ""]
body = "\n".join(hdr) + text + "\n\n=== ENGLISH RUNS (>=5 words) NOT MARKED AS QUOTES ===\n" + "\n".join("  [%s] n=%d %s" % (s, n, w) for s, n, w in unmarked) + "\n"
if OUT:
    open(OUT, "w", encoding="utf-8", newline="\n").write(body)
    print("wrote", OUT, len(body), "chars;", "q", p.nq, "en", p.nen, "unmarked runs", len(unmarked))
else:
    print(body)
