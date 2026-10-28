# 證據包重現步驟（第一輪抓取 2026-09-07；第二輪重抓 2026-10-28）

1. 抓取原始頁：`curl -sL -H "Accept: text/markdown" https://platform.claude.com/docs/en/release-notes/system-prompts/<slug>.md`，slug 見 sources/ 檔名。第一輪為 overview 加 18 個模型頁；第二輪為 overview 加 22 個模型頁（新增 Opus 5.5、Sonnet 5.5、Haiku 5.5、Sonnet 5），sources/ 現存檔案即第二輪版本。
2. 切分版本：依每頁的 `## <日期>` 標題與 `Text only:` / `Text and images:` 標籤，把 ```text 圍欄內文寫入 `versions/<slug>__<日期>__<變體>.txt`。同一條目被 MDX 切成多個圍欄時依序以換行接回（Fable 5.1、Opus 5.5 在 `<example>` 處；Sonnet 5 在 `<proactivity>` 前後）。第二輪用 `tools/split_versions.py`，以第一輪的原始頁重切可逐位元組重現 34 個舊版本檔中的 32 個。
   - 更正：第一輪曾寫「Oct 22 2024 條目的字面 `\n` 已正規化」，實際只有 Haiku 3.5 兩檔正規化，Sonnet 3.5 的兩個 2024-10-22 檔仍是單行字面 `\n`（字數 1,903／2,088 是在未正規化檔上算的，正規化後為 1,939／2,126）。為維持既有數字可追溯，兩檔保留原樣。
3. 逐字比對：`git diff --no-index -U0 --word-diff=plain 舊檔 新檔`，去掉前 4 行檔頭，輸出 `[-舊-]{+新+}` 格式存於 diffs/（檔名前綴為比對編號，內含比對方向）。00–20 為第一輪，21–31 為第二輪（31 是 overview 本身 09-07 → 10-28 的變更）。
4. 特徵矩陣：`feature_matrix.txt`，146 個片語 × 39 版；不分大小寫子字串比對。第一輪 118 × 32 以 PowerShell `IndexOf(OrdinalIgnoreCase)` 產生（當時文件誤寫為 115 片語）；第二輪 `tools/build_matrix.py` 先以 Python 重算確認舊 118 × 32 逐格相同，再追加 7 欄（33–39）與 28 個片語。表頭數字為版本序號末位，序號對照見同檔上方 COLUMN KEY。第 33 欄（Sonnet 5，標 2026-06-30）依加入順序編號，不依日期。
5. 血緣比例（第二輪新增）：`tools/newness.py <目標> <參照組…>`，以段落（版本檔一行）為單位；完全相同＝逐字沿用，與參照組任一段 `difflib` 相似度 ≥ 0.8＝小幅改寫，其餘＝新寫；參照組為目標版本發布日以前已公開的所有版本。`tools/lineage.py` 依來源拆分逐字段落，`tools/overlap.py` 算多版共同段落，`tools/metrics.py` 算區塊字數與 because／never／全大寫等指標，`tools/trace.py` 追蹤片語出現在哪些版本。
6. 引文查核：`python -I tools/verify_quotes.py <repo_root>`，檢查全站每一段英文引文都能在 versions/（overview 引文則在 diffs/）逐字找到。

注意：sources/ 內為官方頁面原文；versions/、diffs/、feature_matrix.txt 與 tools/ 為本分析產物；報告與網站中所有引文均可在 versions/ 內以原文字串搜尋驗證。
