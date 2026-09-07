# 證據包重現步驟（抓取時間 2026-09-07）

1. 抓取原始頁：`curl -sL -H "Accept: text/markdown" https://platform.claude.com/docs/en/release-notes/system-prompts/<slug>.md`，slug 見 sources/ 檔名（overview 加 18 個模型頁）。
2. 切分版本：依每頁的 `## <日期>` 標題與 `Text only:` / `Text and images:` 標籤，把 ```text 圍欄內文寫入 `versions/<slug>__<日期>__<變體>.txt`；Fable 5.1 頁因 `<example>` 內含巢狀圍欄而被 MDX 切成兩塊，已合併；Oct 22 2024 條目的字面 `\n` 已正規化為換行。
3. 逐字比對：`git diff --no-index -U0 --word-diff=plain 舊檔 新檔`，輸出 `[-舊-]{+新+}` 格式存於 diffs/（檔名前綴為比對編號，內含比對方向）。
4. 特徵矩陣：`feature_matrix.txt`，115 個片語 × 32 版，PowerShell `IndexOf(OrdinalIgnoreCase)` 逐一比對；表頭數字為版本序號末位，序號對照見同檔上方 COLUMN KEY。

注意：sources/ 內為官方頁面原文；versions/ 與 diffs/ 為本分析產物；報告中所有引文均可在 versions/ 內以原文字串搜尋驗證。
