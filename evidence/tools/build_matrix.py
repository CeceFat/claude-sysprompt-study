"""重建特徵矩陣：沿用 data/matrix.json 的 32 欄與 118 片語，追加新欄（33–39）與新片語。
- 出現判定：不分大小寫子字串（等同 PowerShell IndexOf(OrdinalIgnoreCase)）。
- 先驗證：舊 32 欄 × 118 片語重算結果必須與既有矩陣逐格相同，否則中止。
輸出：evidence/feature_matrix.txt、data/matrix.json、data/matrix.js
用法：python -I build_matrix.py <repo_root>
"""
import json
import os
import sys

ROOT = sys.argv[1]
VDIR = os.path.join(ROOT, "evidence", "versions")

NEW_COLS = [  # (i, file stem, model, family, date)
    (33, "claude-sonnet-5__June_30_2026__default", "Sonnet 5", "Sonnet", "2026-06-30"),
    (34, "claude-opus-5-5__September_22_2026__default", "Opus 5.5", "Opus", "2026-09-22"),
    (35, "claude-sonnet-5-5__September_28_2026__default", "Sonnet 5.5", "Sonnet", "2026-09-28"),
    (36, "claude-sonnet-5-5__October_7_2026__default", "Sonnet 5.5", "Sonnet", "2026-10-07"),
    (37, "claude-haiku-5-5__October_7_2026__default", "Haiku 5.5", "Haiku", "2026-10-07"),
    (38, "claude-haiku-4-5__October_7_2026__default", "Haiku 4.5", "Haiku", "2026-10-07"),
    (39, "claude-sonnet-4-6__October_7_2026__default", "Sonnet 4.6", "Sonnet", "2026-10-07"),
]

NEW_PHRASES = [
    "respects the person's judgment",
    "bad_response",
    "matches its effort to the ask",
    "<rationale>",
    "pattern level",
    "detection mechanics",
    "mentally reframing",
    "self-sexualization",
    "that decision stands",
    "anyone can delete the note",
    "A story with a child in it",
    "rest of the conversation",
    "wanting to die",
    "plainly that it is an AI",
    "such as 988",
    "provide_crisis_resources",
    "source of stability",
    "medical_guidance",
    "DailyMed",
    "memory_listing",
    "proactivity",
    "conversational_register",
    "markdown formatting to make outputs more readable",
    "Above Opus sits",
    "Mythos 5.1",
    "training-data cutoff",
    "earlier generation and remains available",
    "transcripts",
]


def read(stem):
    with open(os.path.join(VDIR, stem + ".txt"), encoding="utf-8") as fh:
        return fh.read()


with open(os.path.join(ROOT, "data", "matrix.json"), encoding="utf-8") as fh:
    M = json.load(fh)

# 可重跑：不論 matrix.json 目前是 32 欄或已擴充，一律以第 1–32 欄與前 118 個片語為基準
cols = sorted([c for c in M["columns"] if c["i"] <= 32], key=lambda c: c["i"])
assert [c["i"] for c in cols] == list(range(1, 33)), "existing columns must include 1..32"
M["phrases"] = [{"p": p["p"], "v": p["v"][:32]} for p in M["phrases"][:118]]

# 驗證舊矩陣
texts = {c["i"]: read(c["file"]).lower() for c in cols}
bad = 0
for p in M["phrases"]:
    v = "".join("Y" if p["p"].lower() in texts[c["i"]] else "." for c in cols)
    if v != p["v"]:
        bad += 1
        print("MISMATCH", repr(p["p"]), p["v"], v)
if bad:
    sys.exit("old matrix does not reproduce; abort")
print("old 118 x 32 reproduced exactly")

for i, stem, model, fam, date in NEW_COLS:
    raw = read(stem)
    cols.append({
        "i": i, "file": stem,
        "bytes": len(raw.encode("utf-8")),
        "words": len(raw.split()),
        "model": model, "slug": stem.split("__")[0], "date": date, "variant": "—",
        "txt": "evidence/versions/%s.txt" % stem, "family": fam,
    })
    texts[i] = raw.lower()

existing = {p["p"].lower() for p in M["phrases"]}
phrases = [p["p"] for p in M["phrases"]] + [p for p in NEW_PHRASES if p.lower() not in existing]
rows = [{"p": p, "v": "".join("Y" if p.lower() in texts[c["i"]] else "." for c in cols)} for p in phrases]
for r in rows[118:]:
    if "Y" not in r["v"]:
        sys.exit("new phrase never matches: %r" % r["p"])

out = {"columns": cols, "phrases": rows}
js = json.dumps(out, ensure_ascii=False, indent=1)
with open(os.path.join(ROOT, "data", "matrix.json"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(js + "\n")
with open(os.path.join(ROOT, "data", "matrix.js"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("/* 由 evidence/feature_matrix.txt 產生：%d 欄版本索引 + %d 個片語出現矩陣 */\n" % (len(cols), len(rows)))
    fh.write("window.MATRIX = " + js + ";\n")

lines = ["=== COLUMN KEY (index: file | bytes | words) ==="]
for c in cols:
    lines.append("%2d: %-60s%5d B %5d w" % (c["i"], c["file"], c["bytes"], c["words"]))
lines.append("")
lines.append("=== FEATURE MATRIX (Y = present, . = absent; column n = index n above, digit = n mod 10) ===")
lines.append("%-45s%s" % ("phrase", "".join(str(c["i"] % 10) for c in cols)))
for r in rows:
    lines.append("%-45s%s" % (r["p"], r["v"]))
with open(os.path.join(ROOT, "evidence", "feature_matrix.txt"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(lines) + "\n")
print("columns:", len(cols), "phrases:", len(rows))
for r in rows[118:]:
    print("  %-50s %s" % (r["p"], r["v"]))
