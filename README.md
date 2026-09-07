# Claude 系統提示詞演進 · 自學站

以 Anthropic 官方公開的 [System prompts 發行說明](https://platform.claude.com/docs/en/release-notes/system-prompts/overview) 為據，
把 **2024-07-12 → 2026-09-01**、18 個模型頁、32 個版本的 claude.ai 系統提示詞抓下來逐字比對，
整理成一套可自行查核的自主學習教材。

🔗 **線上閱讀：<https://cecefat.github.io/claude-sysprompt-study/>**

---

## 站台結構

| 頁面 | 內容 |
|---|---|
| `index.html` | 總覽、十行結論、字數走勢圖、五步學習路徑 |
| `versions.html` | 32 版總表（可篩選、可直接讀原文） |
| `shifts.html` | 五次架構躍遷與技術意義 |
| `themes.html` | 13 條主題軌跡（逐條文、逐版本） |
| `branches.html` | 三分支證據、同日兄弟版差異、實務含意 |
| `matrix.html` | 118 片語 × 32 版互動特徵矩陣 |
| `method.html` | 抓取與比對方法、七項品質警語、附錄 A–D |
| `quiz.html` | 15 題自我檢測 |

每一頁的引文都可以點「在原文中查看」，直接開啟該版本的純文字檔並高亮該句。

## 證據包

```
evidence/
├── sources/           overview + 18 個模型頁的原始 .md（2026-09-07 抓取）
├── versions/          34 個拆分後的版本純文字（模型__日期__變體.txt）
├── diffs/             21 組 word-diff（[-舊-]{+新+} 格式）
├── feature_matrix.txt 118 個片語 × 32 版出現矩陣與字數表
└── README.md          重現步驟
report/changelog-zh-TW.md   完整中文報告原檔（本站是它的網頁化版本）
```

抓取方式：

```bash
curl -sL -H "Accept: text/markdown" \
  https://platform.claude.com/docs/en/release-notes/system-prompts/<slug>.md
```

比對方式：`git diff --no-index -U0 --word-diff=plain 舊檔 新檔`

## 查核紀錄

網頁化之前重跑了一輪查核：

- ✅ 22 條關鍵引文（Haiku 3 → Fable 5.1）以 `grep -F` 全部逐字命中
- ✅ Q2（2025-08-05 與 07-31 逐字相同）兩組 diff 均為空
- ✅ 字數重算（114／1,973／3,678／4,267）與矩陣一致
- ✅ 19 個來源檔 frontmatter 的 `url:` 全部指向 `platform.claude.com`
- ✅ 34 個版本檔、21 組 diff，與附錄 D 相符
- ⚠️ 報告與證據包 README 寫「115 個片語」，實際矩陣有 **118** 列（無重複）。本站一律以 118 為準，不影響任何實質結論。

## 聲明

- 本站為**個人研究整理，非 Anthropic 官方出版品**，不代表任何雇主立場。
- 引文著作權屬 Anthropic，僅為研究、評註與教學目的節錄；完整原文請參閱官方頁面。
- 標「推論」者為本站解讀，非文件明文。
- 官方頁面持續更新，本站快照時間為 **2026-09-07**；新模型頁出現後需重抓才會反映。
- 這批 prompt 只適用 claude.ai 網頁與行動 app，官方明言 *"These system prompt updates do not apply to the Claude API"*。

發現錯誤歡迎開 issue，請附上版本檔名與可搜到的字串。

## 授權

站台程式碼（HTML／CSS／JS）採 MIT。`evidence/` 與引文內容的著作權屬 Anthropic，依合理使用原則收錄供查核。
