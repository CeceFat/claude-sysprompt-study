"""把官方 system-prompts 模型頁 (.md) 切成版本純文字檔。

規則與 evidence/README.md 相同：
- 依 `## <日期>` 標題切條目；
- 條目內若有 `Text only:` / `Text and images:` 標籤則依變體分檔，否則為 default；
- 同一變體被 MDX 切成多個 ```text 圍欄時，依序以換行接回（Fable 5.1 的 Q6 處理方式）；
- 圍欄內若只有字面 \n（Oct 22 2024 條目），正規化為真換行。
輸出檔名：<slug>__<Month>_<D>_<YYYY>__<variant>.txt，LF 換行、結尾一個換行。

用法：python -I split_versions.py <src_dir> <out_dir> [slug ...]
"""
import os
import re
import sys

DATE_RE = re.compile(r"^## ([A-Z][a-z]+) (\d{1,2}), (\d{4})\s*$")
FENCE_OPEN = re.compile(r"^```text")
VARIANT_RE = re.compile(r"^\**\s*(Text only|Text and images)\s*:?\**\s*:?\s*$", re.I)


def parse(path):
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().replace("\r\n", "\n").split("\n")
    entries = []  # (date_key, variant, [blocks])
    cur_date, cur_var, in_fence, buf = None, "default", False, []
    for ln in lines:
        if in_fence:
            if ln.strip() == "```":
                entries.append((cur_date, cur_var, "\n".join(buf)))
                in_fence, buf = False, []
            else:
                buf.append(ln)
            continue
        m = DATE_RE.match(ln)
        if m:
            cur_date = "%s_%s_%s" % (m.group(1), m.group(2), m.group(3))
            cur_var = "default"
            continue
        v = VARIANT_RE.match(ln.strip())
        if v:
            cur_var = "textonly" if v.group(1).lower() == "text only" else "textimages"
            continue
        if FENCE_OPEN.match(ln):
            in_fence, buf = True, []
    merged = {}
    order = []
    for d, var, block in entries:
        key = (d, var)
        if key not in merged:
            merged[key] = []
            order.append(key)
        merged[key].append(block)
    out = []
    for key in order:
        text = "\n".join(merged[key])
        if text.count("\n") < 3 and "\\n" in text:
            text = text.replace("\\n", "\n")
        out.append((key[0], key[1], text, len(merged[key])))
    return out


def main():
    src, dst = sys.argv[1], sys.argv[2]
    slugs = sys.argv[3:] or sorted(f[:-3] for f in os.listdir(src) if f.endswith(".md") and f != "overview.md")
    os.makedirs(dst, exist_ok=True)
    for slug in slugs:
        for date, var, text, nblocks in parse(os.path.join(src, slug + ".md")):
            name = "%s__%s__%s.txt" % (slug, date, var)
            with open(os.path.join(dst, name), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text.rstrip("\n") + "\n")
            print("%-62s blocks=%d words=%d" % (name, nblocks, len(text.split())))


if __name__ == "__main__":
    main()
