# Claude 系統提示詞演進 · 自學站

以 Anthropic 官方公開的 [System prompts 發行說明](https://platform.claude.com/docs/en/release-notes/system-prompts/overview) 為據，
把 **2024-07-12 → 2026-11-09**、23 個模型頁、52 個版本的 claude.ai 系統提示詞抓下來逐字比對，
整理成一套可自行查核的自主學習教材。2026-10-28 更新：補入 5.5 世代（Opus 5.5／Sonnet 5.5／Haiku 5.5），總覽頁首改為「為什麼 Opus 5.5 的 system prompt 長這樣」。2026-11-05 更新：補入 10 月下旬 12 個新條目（政治中立段、舊 Opus 重建等），並對照 Anthropic 2026-07-24 的 Claude Code 部落格「刪掉八成」一文。2026-11-10 更新：補入 Fable 5.2（11-09），並由 Claude Fable 5.2 把前三輪的全部產出稽核一遍，記下 66 項發現並全部修正或加註（見 [`report/audit-2026-11-10-zh-TW.md`](report/audit-2026-11-10-zh-TW.md)）。

🔗 **線上閱讀：<https://cecefat.github.io/claude-sysprompt-study/>**

---

## 站台結構

| 頁面 | 內容 |
|---|---|
| `index.html` | 頁首：Opus 5.5 的四個設計原理、5.5 世代三種寫法、Fable 5.2 一節、官方 Claude Code 部落格六個轉變的對照、與過往世代對照；其後為總覽、十行結論、字數走勢圖、五步學習路徑 |
| `versions.html` | 52 版總表（可篩選、可直接讀原文） |
| `shifts.html` | 六次架構躍遷與技術意義（F＝5.5 世代的模組庫組裝，F-6＝10 月下旬第二波，F-7＝Fable 5.2） |
| `themes.html` | 13 條主題軌跡（逐條文、逐版本，補至 2026-11-09） |
| `branches.html` | 分支證據、5.5 世代的收斂、Fable 5.2 併回模組庫、同日兄弟版差異、實務含意 |
| `matrix.html` | 181 片語 × 52 版互動特徵矩陣 |
| `method.html` | 抓取與比對方法、血緣算法、2026-11-10 稽核紀錄、十一項品質警語、附錄 A–D |
| `quiz.html` | 24 題自我檢測 |

每一頁的引文都可以點「在原文中查看」，直接開啟該版本的純文字檔並高亮該句。

## 證據包

```
evidence/
├── sources/           overview + 23 個模型頁的原始 .md（2026-11-10 重抓）
├── versions/          54 個拆分後的版本純文字（模型__日期__變體.txt）
├── diffs/             51 組 word-diff（[-舊-]{+新+} 格式；21–31 第二輪、32–46 第三輪、47–50 第四輪）
├── tools/             第二輪起用的 Python 腳本（切檔、矩陣、血緣、指標、引文查核）；audit/ 是 2026-11-10 稽核用的獨立程式
├── external/          本站引用的官方部落格逐字句與出處（網址、抓取時間、SHA-256；不存全文）
├── feature_matrix.txt 181 個片語 × 52 版出現矩陣與字數表
└── README.md          重現步驟
report/changelog-zh-TW.md         完整中文報告原檔（含 §A、§B、§C 增補）
report/audit-2026-11-10-zh-TW.md  2026-11-10 稽核報告（逐項發現、修正前後對照、重現方式）
```

抓取方式：

```bash
curl -sL -H "Accept: text/markdown" \
  https://platform.claude.com/docs/en/release-notes/system-prompts/<slug>.md
```

比對方式：`git diff --no-index -U0 --word-diff=plain 舊檔 新檔`

## 查核紀錄

第一輪（網頁化之前）：

- ✅ 22 條關鍵引文（Haiku 3 → Fable 5.1）以 `grep -F` 全部逐字命中
- ✅ Q2（2025-08-05 與 07-31 逐字相同）兩組 diff 均為空
- ✅ 字數重算（114／1,973／3,678／4,267）與矩陣一致
- ✅ 19 個來源檔 frontmatter 的 `url:` 全部指向 `platform.claude.com`
- ✅ 34 個版本檔、21 組 diff，與附錄 D 相符
- ⚠️ 報告與證據包 README 寫「115 個片語」，實際矩陣有 **118** 列（無重複）。本站一律以 118 為準，不影響任何實質結論。

第二輪（2026-10-28 重抓）：

- ✅ 18 個舊頁中 16 頁只改了 frontmatter 描述句，prompt 本文逐字未動；Haiku 4.5、Sonnet 4.6 只在頁首新增 2026-10-07 條目
- ✅ 新切檔腳本重現 34 個舊版本檔中的 32 個（逐位元組）；舊矩陣 118 × 32 逐格重現
- ✅ `evidence/tools/verify_quotes.py`：全站 352 段英文引文全部在證據包逐字命中
- ⚠️ 第一輪說 Oct 22 2024 條目已正規化，實際 Sonnet 3.5 兩檔沒有（字數 1,903／2,088 為未正規化計數，正規化後 1,939／2,126）；保留原檔、於方法頁揭露
- 🔧 修正 `assets/app.js` 原文閱讀器：含撇號、引號的搜尋詞先前無法高亮

第三輪（2026-11-05 重抓）：

- ✅ overview 與 10-28 版相同；10 個模型頁沒變，12 頁只在頁首新增 10-14 到 10-30 的條目
- ✅ 矩陣前兩輪 146 × 39 逐格重現；全站引文查核 0 失敗（官方部落格引句對 `evidence/external/excerpts.txt`）
- ⚠️ 發現 Opus 5 的路由段「部落格引文」把型號改成 Opus 5，原文是 Opus 4.8（品質警語 Q10）；第一輪報告 §3.5 據此更正

第四輪與全站稽核（2026-11-10）：

- ✅ 22 個既有模型頁與 11-05 快照逐位元組相同；新增 Fable 5.2 一頁（條目日期 2026-11-09，4,975 字）
- ✅ 用另外寫的程式重做證據包：53 個版本檔、47 組 diff、166 × 51 矩陣（8,466 格）全部重現
- ✅ 全站引文改用區分大小寫的比對，0 失敗；報告原檔 354 段英文引文全部找得到
- ⚠️ 逐頁核對數字與主張後記下 66 項發現（數字、首見日期、過期敘述、推論寫得比證據強），全部已修正或加註，清單見稽核報告
- ⚠️ 外部網頁含動態內容，SHA-256 無法重驗，已在 `evidence/external/excerpts.txt` 註明

## 聲明

- 本站為**個人研究整理，非 Anthropic 官方出版品**，不代表任何雇主立場。
- 引文著作權屬 Anthropic，僅為研究、評註與教學目的節錄；完整原文請參閱官方頁面。
- 標「推論」者為本站解讀，非文件明文。官方的發行說明不附改動理由；「為什麼」幾乎都是由文本差異反推，少數有官方文章可以對照的地方另外標明。
- 官方頁面持續更新，本站快照時間為 **2026-09-07**、**2026-10-28**、**2026-11-05** 與 **2026-11-10**；新模型頁或新條目出現後需重抓才會反映，頁面也可能事後補上。
- 這批 prompt 只適用 claude.ai 網頁與行動 app，官方明言 *"These system prompt updates do not apply to the Claude API"*。

發現錯誤歡迎開 issue，請附上版本檔名與可搜到的字串。

## 授權

站台程式碼（HTML／CSS／JS）與 `evidence/tools/` 腳本採 MIT。`evidence/sources|versions|diffs` 與引文內容的著作權屬 Anthropic，依合理使用原則收錄供查核。
