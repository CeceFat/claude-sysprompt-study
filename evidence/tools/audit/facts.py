"""Shared fact base for the audit: loads every version file and offers independent measurements.

Nothing here imports the site's own tools; the algorithms are re-implemented from their documented
definitions so that the audit does not inherit their bugs.
"""
import difflib
import json
import os
import re

MONTHS = {m: i + 1 for i, m in enumerate("January February March April May June July August September October November December".split())}
ABBR = {"haiku": "H", "opus": "O", "sonnet": "S", "fable": "F"}


class Version:
    def __init__(self, stem, text, col):
        self.stem = stem
        self.text = text
        self.col = col
        slug, date, var = stem.split("__")
        parts = slug.replace("claude-", "").split("-")
        self.family = parts[0].capitalize()
        self.ver = ".".join(parts[1:])
        self.model = "%s %s" % (self.family, self.ver)
        mo, d, y = date.split("_")
        self.date = "%s-%02d-%02d" % (y, MONTHS[mo], int(d))
        self.variant = {"default": "", "textonly": "t", "textimages": "i"}[var]
        self.label = "%s%s@%s%s" % (ABBR[parts[0]], self.ver, self.date[2:].replace("-", ""), self.variant)
        self.words = len(text.split())
        self.ws = re.sub(r"\s+", " ", text)
        self.lines = [l.strip() for l in text.split("\n") if l.strip()]
        self.lineset = set(self.lines)

    def has(self, s, ci=False):
        s = re.sub(r"\s+", " ", s).strip()
        return (s.lower() in self.ws.lower()) if ci else (s in self.ws)

    def in_one_line(self, s):
        s = re.sub(r"\s+", " ", s).strip()
        return any(s in re.sub(r"\s+", " ", l) for l in self.lines)

    def section(self, tag):
        m = re.search(r"<%s>(.*?)</%s>" % (tag, tag), self.text, re.S)
        return m.group(1) if m else None

    def section_words(self, tag):
        s = self.section(tag)
        return len(s.split()) if s is not None else 0

    def tags(self):
        return sorted(set(re.findall(r"<([a-z_]+)>", self.text)))


def load(root, extra_dirs=()):
    vdir = os.path.join(root, "evidence", "versions")
    M = json.load(open(os.path.join(root, "data", "matrix.json"), encoding="utf-8"))
    colof = {c["file"]: c["i"] for c in M["columns"]}
    vs = []
    for f in sorted(os.listdir(vdir)):
        if f.endswith(".txt"):
            t = open(os.path.join(vdir, f), encoding="utf-8", newline="").read().replace("\r\n", "\n")
            vs.append(Version(f[:-4], t, colof.get(f[:-4])))
    for d in extra_dirs:
        for f in sorted(os.listdir(d)):
            if f.endswith(".txt"):
                t = open(os.path.join(d, f), encoding="utf-8", newline="").read().replace("\r\n", "\n")
                vs.append(Version(f[:-4], t, None))
    vs.sort(key=lambda v: (v.date, v.col if v.col is not None else 999, v.stem))
    return vs, M


def by_label(vs):
    return {v.label: v for v in vs}


def find(vs, key):
    """key like 'O5.5@261027' or a stem or a column number."""
    for v in vs:
        if key == v.label or key == v.stem or key == v.col:
            return v
    raise KeyError(key)


def trace(vs, phrase, ci=False):
    return [v for v in vs if v.has(phrase, ci)]


def fmt_set(vlist, maxn=10):
    labs = [v.label for v in vlist]
    if len(labs) <= maxn:
        return " ".join(labs)
    return " ".join(labs[:4]) + " … " + " ".join(labs[-3:])


def newness(target, refs, threshold=0.8):
    """Word-weighted share of target lines that are verbatim / minor-edit / new relative to refs."""
    old = []
    for r in refs:
        old.extend(r.lines)
    oldset = set(old)
    tot = verb = edit = new = 0
    newlines = []
    for ln in target.lines:
        w = len(ln.split())
        tot += w
        if ln in oldset:
            verb += w
            continue
        best = 0.0
        for o in oldset:
            if abs(len(o) - len(ln)) < 0.6 * len(ln) + 20:
                sm = difflib.SequenceMatcher(None, ln, o, autojunk=False)
                if sm.real_quick_ratio() < threshold or sm.quick_ratio() < threshold:
                    continue
                r = sm.ratio()
                if r > best:
                    best = r
        if best >= threshold:
            edit += w
        else:
            new += w
            newlines.append((w, round(best, 2), ln))
    return {"total": tot, "verbatim": verb, "edit": edit, "new": new, "newlines": newlines}


def strictly_earlier(vs, target):
    return [v for v in vs if v.date < target.date]


def shared_words(a, b):
    """Words of a's lines that appear verbatim as a line of b."""
    return sum(len(l.split()) for l in a.lines if l in b.lineset)
