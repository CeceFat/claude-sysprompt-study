"""不分大小寫追蹤片語出現在哪些版本檔。用法：python -I trace.py <versions_dir> <pattern-file-glob> -- phrase1 phrase2 ..."""
import glob, os, sys
d, pat = sys.argv[1], sys.argv[2]
phrases = sys.argv[sys.argv.index("--") + 1:]
files = sorted(glob.glob(os.path.join(d, pat)))
texts = {os.path.basename(f).replace("__default.txt", "").replace("claude-", ""): open(f, encoding="utf-8").read().lower() for f in files}
for p in phrases:
    hits = [k for k, t in texts.items() if p.lower() in t]
    print("[%s] %s" % (p, " ".join(hits) if hits else "—"))
