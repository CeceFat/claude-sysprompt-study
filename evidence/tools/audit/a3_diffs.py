"""Audit A3: regenerate every stored word-diff from the version files and compare byte-for-byte
(after CRLF normalisation). Where the file name leaves the variant ambiguous, every candidate pair is tried.

Usage: python -I a3_diffs.py <repo_root>
"""
import itertools
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = sys.argv[1]
V = os.path.join(ROOT, "evidence", "versions")
D = os.path.join(ROOT, "evidence", "diffs")

F = {
    "s35sep9": ["claude-sonnet-3-5__September_9_2024__textonly", "claude-sonnet-3-5__September_9_2024__textimages"],
    "s35oct22": ["claude-sonnet-3-5__October_22_2024__textonly", "claude-sonnet-3-5__October_22_2024__textimages"],
    "s35nov22": ["claude-sonnet-3-5__November_22_2024__textonly", "claude-sonnet-3-5__November_22_2024__textimages"],
    "h35oct22": ["claude-haiku-3-5__October_22_2024__textonly", "claude-haiku-3-5__October_22_2024__textimages"],
    "h35img": ["claude-haiku-3-5__October_22_2024__textimages"],
    "s37": ["claude-sonnet-3-7__February_24_2025__default"],
    "s4may22": ["claude-sonnet-4__May_22_2025__default"],
    "s4aug5": ["claude-sonnet-4__August_5_2025__default"],
    "o41aug5": ["claude-opus-4-1__August_5_2025__default"],
    "s45sep29": ["claude-sonnet-4-5__September_29_2025__default"],
    "s45nov19": ["claude-sonnet-4-5__November_19_2025__default"],
    "s45jan18": ["claude-sonnet-4-5__January_18_2026__default"],
    "h45oct15": ["claude-haiku-4-5__October_15_2025__default"],
    "h45nov19": ["claude-haiku-4-5__November_19_2025__default"],
    "h45jan18": ["claude-haiku-4-5__January_18_2026__default"],
    "h45oct7": ["claude-haiku-4-5__October_7_2026__default"],
    "h45oct23": ["claude-haiku-4-5__October_23_2026__default"],
    "o45nov24": ["claude-opus-4-5__November_24_2025__default"],
    "o45jan18": ["claude-opus-4-5__January_18_2026__default"],
    "o46feb5": ["claude-opus-4-6__February_5_2026__default"],
    "o46oct30": ["claude-opus-4-6__October_30_2026__default"],
    "s46feb17": ["claude-sonnet-4-6__February_17_2026__default"],
    "s46oct7": ["claude-sonnet-4-6__October_7_2026__default"],
    "s46oct14": ["claude-sonnet-4-6__October_14_2026__default"],
    "o47apr16": ["claude-opus-4-7__April_16_2026__default"],
    "o47oct30": ["claude-opus-4-7__October_30_2026__default"],
    "o48may28": ["claude-opus-4-8__May_28_2026__default"],
    "o48oct30": ["claude-opus-4-8__October_30_2026__default"],
    "f5jun9": ["claude-fable-5__June_9_2026__default"],
    "f5oct30": ["claude-fable-5__October_30_2026__default"],
    "o5jul24": ["claude-opus-5__July_24_2026__default"],
    "o5oct30": ["claude-opus-5__October_30_2026__default"],
    "f51sep1": ["claude-fable-5-1__September_1_2026__default"],
    "f51oct30": ["claude-fable-5-1__October_30_2026__default"],
    "s5jun30": ["claude-sonnet-5__June_30_2026__default"],
    "s5oct30": ["claude-sonnet-5__October_30_2026__default"],
    "o55sep22": ["claude-opus-5-5__September_22_2026__default"],
    "o55oct27": ["claude-opus-5-5__October_27_2026__default"],
    "s55sep28": ["claude-sonnet-5-5__September_28_2026__default"],
    "s55oct7": ["claude-sonnet-5-5__October_7_2026__default"],
    "s55oct27": ["claude-sonnet-5-5__October_27_2026__default"],
    "h55oct7": ["claude-haiku-5-5__October_7_2026__default"],
    "h55oct26": ["claude-haiku-5-5__October_26_2026__default"],
    "f52nov9": ["claude-fable-5-2__November_9_2026__default"],
}

PAIRS = {
    "00_s35_sep9_to_oct22": ("s35sep9", "s35oct22"),
    "01_s45sep29_vs_h45oct15": ("s45sep29", "h45oct15"),
    "02_s45nov19_vs_h45nov19": ("s45nov19", "h45nov19"),
    "03_s45jan18_vs_h45jan18": ("s45jan18", "h45jan18"),
    "04_s45_sep29_to_nov19": ("s45sep29", "s45nov19"),
    "05_s45_nov19_to_jan18": ("s45nov19", "s45jan18"),
    "06_s45nov19_vs_o45nov24": ("s45nov19", "o45nov24"),
    "07_o45_nov24_to_jan18": ("o45nov24", "o45jan18"),
    "08_o45jan18_to_o46feb5": ("o45jan18", "o46feb5"),
    "09_o46_vs_s46": ("o46feb5", "s46feb17"),
    "10_o46_to_o47": ("o46feb5", "o47apr16"),
    "11_o47_to_o48": ("o47apr16", "o48may28"),
    "12_o48_to_f5": ("o48may28", "f5jun9"),
    "13_f5_vs_o5": ("f5jun9", "o5jul24"),
    "14_f5_to_f51": ("f5jun9", "f51sep1"),
    "15_o5_to_f51": ("o5jul24", "f51sep1"),
    "16_o41aug5_to_s45sep29": ("o41aug5", "s45sep29"),
    "17_s4aug5_vs_o41aug5": ("s4aug5", "o41aug5"),
    "18_s37_to_s4may22": ("s37", "s4may22"),
    "19_h35img_to_s37": ("h35img", "s37"),
    "20_s35nov22_vs_h35oct22": ("s35nov22", "h35oct22"),
    "21_o5_to_o55": ("o5jul24", "o55sep22"),
    "22_f51_to_o55": ("f51sep1", "o55sep22"),
    "23_f5_to_s5": ("f5jun9", "s5jun30"),
    "24_s5_to_s55sep28": ("s5jun30", "s55sep28"),
    "25_s55_sep28_to_oct7": ("s55sep28", "s55oct7"),
    "26_o55_vs_s55sep28": ("o55sep22", "s55sep28"),
    "27_s55oct7_vs_h55": ("s55oct7", "h55oct7"),
    "28_o55_vs_h55": ("o55sep22", "h55oct7"),
    "29_h45_jan18_to_oct7": ("h45jan18", "h45oct7"),
    "30_s46_feb17_to_oct7": ("s46feb17", "s46oct7"),
    "32_h45_oct7_to_oct23": ("h45oct7", "h45oct23"),
    "33_s46_oct7_to_oct14": ("s46oct7", "s46oct14"),
    "34_h55_oct7_to_oct26": ("h55oct7", "h55oct26"),
    "35_s55_oct7_to_oct27": ("s55oct7", "s55oct27"),
    "36_o55_sep22_to_oct27": ("o55sep22", "o55oct27"),
    "37_f51_sep1_to_oct30": ("f51sep1", "f51oct30"),
    "38_o5_jul24_to_oct30": ("o5jul24", "o5oct30"),
    "39_s5_jun30_to_oct30": ("s5jun30", "s5oct30"),
    "40_f5_jun9_to_oct30": ("f5jun9", "f5oct30"),
    "41_o48_may28_to_oct30": ("o48may28", "o48oct30"),
    "42_o47_apr16_to_oct30": ("o47apr16", "o47oct30"),
    "43_o46_feb5_to_oct30": ("o46feb5", "o46oct30"),
    "44_o55oct27_vs_s55oct27": ("o55oct27", "s55oct27"),
    "45_o48oct30_vs_o47oct30": ("o48oct30", "o47oct30"),
    "46_o47oct30_vs_o46oct30": ("o47oct30", "o46oct30"),
    "47_f51_oct30_to_f52_nov9": ("f51oct30", "f52nov9"),
    "48_o55oct27_vs_f52nov9": ("o55oct27", "f52nov9"),
    "49_h55oct26_vs_f52nov9": ("h55oct26", "f52nov9"),
}


def gitdiff(a, b):
    r = subprocess.run(["git", "diff", "--no-index", "-U0", "--word-diff=plain",
                        os.path.join(V, a + ".txt"), os.path.join(V, b + ".txt")],
                       capture_output=True)
    out = r.stdout.decode("utf-8", errors="replace").replace("\r\n", "\n")
    lines = out.split("\n")
    return "\n".join(lines[4:]) if len(lines) > 4 else ""


stored_names = sorted(f[:-5] for f in os.listdir(D) if f.endswith(".diff"))
ok = 0
bad = []
for name in stored_names:
    st = open(os.path.join(D, name + ".diff"), encoding="utf-8", newline="").read().replace("\r\n", "\n")
    if name not in PAIRS:
        print("%-28s (no version pair: not regenerated) size=%d" % (name, len(st)))
        continue
    ka, kb = PAIRS[name]
    hit = None
    tried = []
    for a, b in itertools.product(F[ka], F[kb]):
        g = gitdiff(a, b)
        tried.append((a, b, g))
        if g == st or g.rstrip("\n") == st.rstrip("\n"):
            hit = (a, b, g == st)
            break
    if hit:
        ok += 1
        va = hit[0].split("__")[2]
        vb = hit[1].split("__")[2]
        note = "" if (va == "default" and vb == "default") else "  [variants: %s -> %s]" % (va, vb)
        print("%-28s REPRODUCED%s%s" % (name, "" if hit[2] else " (trailing-newline only)", note))
    else:
        bad.append(name)
        a, b, g = tried[0]
        gl, sl = g.split("\n"), st.split("\n")
        k = next((i for i in range(min(len(gl), len(sl))) if gl[i] != sl[i]), min(len(gl), len(sl)))
        print("%-28s NOT REPRODUCED (tried %d pair(s)); first difference at line %d of %d/%d" % (name, len(tried), k + 1, len(gl), len(sl)))
        print("      regen : %r" % (gl[k][:160] if k < len(gl) else "<EOF>"))
        print("      stored: %r" % (sl[k][:160] if k < len(sl) else "<EOF>"))
print()
print("reproduced %d of %d version-pair diffs; not reproduced: %s" % (ok, len(PAIRS), bad or "none"))
print("stored diffs not covered by a pair:", [n for n in stored_names if n not in PAIRS])
