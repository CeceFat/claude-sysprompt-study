"""Audit A1: independent re-derivation of version files from the official source pages.

Independent of evidence/tools/split_versions.py: different parsing strategy (state machine over
*all* headings and *all* fence openers, not just the ones the original regex accepts), so that
anything the original parser silently ignored is surfaced.

Usage: python -I a1_sources.py <sources_dir> <versions_dir>
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
SRC, VER = sys.argv[1], sys.argv[2]

MONTHS = "January February March April May June July August September October November December".split()


def norm_file(p):
    return open(p, encoding="utf-8", newline="").read().replace("\r\n", "\n")


stored = {f: norm_file(os.path.join(VER, f)) for f in sorted(os.listdir(VER))}
accounted = set()
tot_entries = 0
problems = []
outside_notes = []

for fn in sorted(os.listdir(SRC)):
    if not fn.endswith(".md") or fn == "overview.md":
        continue
    slug = fn[:-3]
    lines = norm_file(os.path.join(SRC, fn)).split("\n")
    # frontmatter
    i = 0
    if lines[0].strip() == "---":
        i = 1
        while lines[i].strip() != "---":
            i += 1
        i += 1
    cur_date = None
    cur_var = "default"
    in_f = False
    f_info = None
    buf = []
    groups = {}  # (date, var) -> list of fence bodies
    order = []
    fence_infos = set()
    headings = []
    for n in range(i, len(lines)):
        ln = lines[n]
        if in_f:
            if ln.strip() == "```":
                key = (cur_date, cur_var)
                if key not in groups:
                    groups[key] = []
                    order.append(key)
                groups[key].append("\n".join(buf))
                in_f = False
                buf = []
            else:
                buf.append(ln)
            continue
        s = ln.strip()
        if s.startswith("```"):
            in_f = True
            f_info = s[3:].strip()
            fence_infos.add(f_info)
            if cur_date is None:
                problems.append("%s line %d: fence before any date heading" % (slug, n + 1))
            continue
        if s.startswith("#"):
            headings.append((n + 1, s))
            m = re.match(r"^## (\w+) (\d{1,2}), (\d{4})$", s)
            if m and m.group(1) in MONTHS:
                cur_date = "%s_%s_%s" % (m.group(1), m.group(2), m.group(3))
                cur_var = "default"
            else:
                problems.append("%s line %d: heading not a date: %r" % (slug, n + 1, s))
            continue
        if not s:
            continue
        low = re.sub(r"[*:\s]", "", s).lower()
        if low == "textonly":
            cur_var = "textonly"
        elif low == "textandimages":
            cur_var = "textimages"
        else:
            outside_notes.append((slug, n + 1, cur_date, s))
    if in_f:
        problems.append("%s: unterminated fence" % slug)
    print("%-20s headings=%d entries=%d fence_infos=%s" % (slug, len(headings), len(order), sorted(fence_infos)))
    for key in order:
        tot_entries += 1
        text = "\n".join(groups[key])
        name = "%s__%s__%s.txt" % (slug, key[0], key[1])
        if name not in stored:
            problems.append("no stored version file for %s (blocks=%d)" % (name, len(groups[key])))
            continue
        accounted.add(name)
        want = text.rstrip("\n") + "\n"
        got = stored[name]
        if want == got:
            status = "exact"
        else:
            alt = text.replace("\\n", "\n").rstrip("\n") + "\n"
            if alt == got:
                status = "exact after literal-\\n normalisation"
            elif re.sub(r"\s+", " ", want).strip() == re.sub(r"\s+", " ", got).strip():
                status = "WHITESPACE-ONLY difference"
            else:
                status = "CONTENT DIFFERS"
                problems.append("%s: content differs (src %d chars vs stored %d chars)" % (name, len(want), len(got)))
        if status != "exact":
            print("    %-66s %s (blocks=%d)" % (name, status, len(groups[key])))
        elif len(groups[key]) > 1:
            print("    %-66s exact (blocks=%d joined)" % (name, len(groups[key])))

print()
print("entries found in sources:", tot_entries, "| stored version files:", len(stored), "| accounted:", len(accounted))
for f in stored:
    if f not in accounted:
        problems.append("stored version file has no source entry: " + f)
print()
print("=== lines outside fences that are neither headings nor variant labels (official commentary) ===")
if not outside_notes:
    print("(none)")
for slug, n, d, s in outside_notes:
    print("%s:%d [%s] %s" % (slug, n, d, s[:300]))
print()
print("=== problems ===")
print("\n".join(problems) if problems else "(none)")
