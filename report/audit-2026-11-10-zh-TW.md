# Claude 系統提示詞演進自學站：全站稽核報告（2026-11-10）

稽核者：Claude Fable 5.2（在 Claude Code 內執行；單線逐項查核，不抽樣）
稽核對象：commit c0cd231 的全部產出，包括 9 個網頁、`data/`、兩份 README、證據包 `evidence/`、報告原檔 `report/changelog-zh-TW.md`
同時進行：第四次重抓官方頁面（2026-11-10），確認官方有沒有新的公開資訊
引文規則：英文引文皆為官方原文逐字，版本以「模型 / 條目日期」標示；標「推論」者是解讀，不是條文明文
後記（2026-11-10，稽核完成之後）：自我檢測頁 `quiz.html` 已整頁改寫成 26 題情境題。本報告提到的「quiz 第 N 題」都是改寫前的 24 題（commit 6d6273e 及之前的版本），題號與現在的頁面對不上。新題目的引文由 `evidence/tools/audit/a6_quiz.py` 另行查核

---

## 0. 結論

1. 證據包站得住。官方頁面、版本檔、diff、特徵矩陣四層，用另外寫的程式獨立重做一遍，全部重現，0 處不符。
2. 引文站得住。全站 51 個引文區塊、286 段行內引文、報告原檔 354 段英文引文，改用區分大小寫的比對後全部逐字成立，沒有跨段落拼接。
3. 問題出在引文周圍的中文敘述。逐頁核對每個數字、每個日期、每句「首見／只有／全部／第一次」之後，記下 66 項發現（編號 F-01 到 F-68；F-13 沒有使用，F-17 查核後撤回），全部已經修正或加註：

| 類別 | 項數 | 說明 |
|---|---|---|
| A | 25 | 數字、日期、首見版本寫錯，或描述與條文不符 |
| B | 9 | 範圍寫得太寬（「唯一」「第一次」「全部」「只剩」） |
| C | 8 | 推論寫得比證據強，或沒有證據 |
| D | 12 | 前幾輪留下的過期敘述（寫的時候對，後來沒回頭改） |
| E | 10 | 補充註記（不算錯，但少了一句會誤導） |
| F | 2 | 查核工具與圖表的問題 |

4. 主要結論不變，但有四個說法要改：
   - 「舊模型整份重建」不是 2026-10-30 才開始。10-07 的 Sonnet 4.6、Haiku 4.5 已經只有 22.6%、27.9% 逐字留自自己的前一版，和 10-30 的 Opus 4.6（15.4%）、Opus 4.7（24.5%）是同一個量級（F-47）。
   - 「5.5 世代的行為組件不談工具」寫得太滿。沒有的是工具作業區塊，政策段落裡還留著「有網搜就查」這類條件句（F-06）。
   - 三個「骨架」的說法寫得太滿。影響最大的是總覽頁的標題式說法「Opus 5.5＝Opus 5 骨架＋Fable 5.1 模組」：量過之後，Opus 5.5 的逐字段落 49.9% 見於 Fable 5.1、36.7% 見於 Opus 5，區塊的組成也和 Fable 5.1 相同，應該說是兩份合併、較靠近 Fable 5.1（F-68）。Opus 5 的文字是 4.8 與 Fable 5 兩邊都取（F-48）；Sonnet 5.5 見於 Opus 5.5 的比見於 Sonnet 5 的多（F-56）。
   - 「判斷給 Opus、規則給 Haiku」的分層推論，因為官方新條目而改弱（見第 5 節）。
5. 官方有新資訊：系統提示詞發行說明多了一個模型頁 Fable 5.2（條目日期 2026-11-09，4,975 字，目前最長）；其餘 22 頁與 11-05 的快照逐位元組相同。已整合進網站與證據包（第四輪）。
6. 稽核過程中我自己有兩次說得太早，後來查證不成立，已當場更正，記在第 4 節。

---

## 1. 範圍與方法

### 1.1 稽核對象

| 層 | 內容 | 稽核前的狀態（c0cd231） |
|---|---|---|
| 官方來源 | `evidence/sources/`：overview＋22 個模型頁的 .md | 2026-11-05 快照 |
| 版本檔 | `evidence/versions/` | 53 個 |
| 逐字差異 | `evidence/diffs/` | 47 組（46 組版本對版本，1 組 overview） |
| 特徵矩陣 | `data/matrix.json`、`data/matrix.js`、`evidence/feature_matrix.txt` | 166 片語 × 51 版，8,466 格 |
| 網頁 | index、shifts、themes、branches、matrix、versions、method、quiz、about | 9 頁 |
| 資料與說明 | `data/versions.js`、`README.md`、`evidence/README.md` | — |
| 報告原檔 | `report/changelog-zh-TW.md`（§0–§7、附錄、§A、§B） | 489 行 |
| 外部來源 | `evidence/external/excerpts.txt` | 兩篇官方文章的逐字句 |

不在範圍內：repo 以外的檔案；模型的實際行為（本站只處理公開條文）；Fable 5.2 發布公告所引用的 System Card。

### 1.2 方法

稽核分六層，由下往上做，下層沒過就不往上走。

- 第 0 層，官方來源：把 overview 與每個模型頁重抓一次（`curl` 取 .md 原始檔），與 11-05 的快照逐位元組比對，看官方有沒有回溯改寫，有沒有新頁、新條目。
- 第 1 層，證據包重現：不 import 前幾輪的工具，另外寫程式從原始頁重切版本檔、重算矩陣每一格、重新產生每一組 diff，與現存檔案逐位元組比對。
- 第 2 層，引文：全站引文改用區分大小寫的比對；另外替每一頁產生「底稿」，在每段英文引文後面列出它實際出現在哪些版本，再由我逐段對照文字所說的版本。
- 第 3 層，主張：逐頁、逐句核對數字、日期、「首見／最後／只有／全部／第一次／最大」這類說法，每一項都寫追蹤程式回到版本檔驗證，不憑印象。
- 第 4 層，外部來源：重抓本站引用的官方文章，確認被引用的句子、日期、作者都還在。
- 第 5 層，工具與呈現：檢查查核工具本身會不會漏掉錯誤，圖表有沒有畫錯。

血緣數字沿用本站公開的定義重新實作：單位是段落（一行），參照組是日期嚴格早於目標的所有版本（同日的兄弟版不算），整行相同算逐字沿用，相似度 0.8 以上算小幅改寫，其餘算新寫，以字數加權。

### 1.3 限制

- 稽核者本身就是 Fable 5.2。本報告關於 Fable 5.2 條文的敘述，一律以官方公開頁面的文字為據，不以模型的自述為據。
- 行內引文（`.en`）是否歸屬到正確的版本，工具只能列出候選版本，最後一步是人工對照，可能還有漏網的。
- 沒有實測任何模型行為。凡是「行為由訓練承擔」這類說法，都只是由段落消失反推。
- 報告原檔的第一輪本文（§0–§7、附錄）照既有慣例不改動，更正一律寫進增補 §C。

---

## 2. 各層結果

| 層 | 結果 | 內容 |
|---|---|---|
| 0 官方來源 | 通過 | 22 個既有模型頁與 11-05 快照逐位元組相同，沒有回溯改寫。overview 多一張 Fable 5.2 的卡片。新增一頁 Fable 5.2，一個條目（2026-11-09）。 |
| 1 版本檔 | 通過 | 用另一支解析程式從原始頁重切，53 個版本檔全部逐位元組相同。圍欄外的官方說明文字只有四個頁面上的 `**` 差異標記說明，網站已經揭露（品質警語 Q4）。 |
| 1 diff | 通過 | 46 組版本 diff 全部重新產生，逐位元組相同；diff 31（overview 09-07 → 10-28）用 git 歷史裡的兩份 overview 重做，也相同。 |
| 1 矩陣 | 通過 | 166 × 51 共 8,466 格獨立重算，0 格不符（2,007 格為有）；`matrix.js`、`matrix.json`、`feature_matrix.txt` 三份一致。官方的 `**` 標記與換行不影響任何一格。 |
| 2 引文 | 通過 | 51 個引文區塊、286 段行內引文，區分大小寫全部找得到，引文區塊的每一段都在它標示的檔案裡，沒有跨段落拼接。報告原檔 354 段英文引文全部找得到。 |
| 3 主張 | 66 項發現 | 見第 3 節。 |
| 4 外部來源 | 通過，附一項限制 | 兩篇官方文章重抓後，被引用的句子、日期、作者都還在。但網頁含動態內容，重抓的 SHA-256 與 11-05 不同，雜湊只能標示當次抓到的那一份。 |
| 5 工具與呈現 | 2 項發現 | `verify_quotes.py` 不分大小寫（F-08）；版本頁長條圖溢出（F-64）。 |

第四輪整合與全部修正完成後，同一套程式再跑一次的結果：版本檔 54 個全部重現；版本 diff 49 組全部重現（另有 2 組 overview diff，共 51 組）；矩陣 181 × 52 共 9,412 格 0 不符（2,088 格為有），舊的 8,466 格逐格不變；`verify_quotes.py`（已改成區分大小寫）查 436 段，0 失敗。

矩陣有一個要知道的特性：片語是不分大小寫的子字串比對，所以短片語會命中包含它的較長句子。實際只有 3 格受影響：片語「Markdown formatting」在第 35、36、44 欄（三個 Sonnet 5.5 條目）亮起，命中的是另一句小寫的「markdown formatting to make outputs more readable」（F-11）。

---

## 3. 發現清單

每一項的格式：位置｜原文｜查核｜處理。位置寫的是稽核前的網頁段落；「報告」指 `report/changelog-zh-TW.md`，它的本文不改，更正寫在增補 §C。

### 3.1 A 類：數字、日期、首見版本寫錯，或描述與條文不符（25 項）

**F-01　Opus 5.5 血緣拆分的兩個百分比**
- 位置：index 原理段、method 血緣表下方、報告 §A.1 第 1 點
- 原文：「Opus 5 有、Fable 5.1 沒有的佔 10.7%，兩者都有的佔 25.9%」
- 查核：443／4,119＝10.755%，1,069／4,119＝25.953%。前幾輪的血緣腳本印出來的就是 10.8 與 26.0，抄進網頁時被截斷。另外兩項（23.9%、9.3%）與合計 69.9% 沒錯。
- 處理：改成 10.8%、26.0%，並註明四項各自四捨五入、加總與 69.9% 差 0.1。

**F-05　tool_search 的首見版本**
- 位置：index 六個轉變對照表、shifts E-2 標題與說明
- 原文：「Opus 4.8 起的 tool_search 延遲載入」；E-2 標題「工具延遲載入（Opus 4.8）」
- 查核：tool_search 與「available but deferred」在 Opus 4.7（2026-04-16）的 capability_check 就有；SKILL.md 才是 Opus 4.8（2026-05-28）首見。
- 處理：對照表改成「Opus 4.7 起的 tool_search 延遲載入、Opus 4.8 起的 SKILL.md」；E-2 改題為「工具探索獨立成區塊」，並說明 4.7 已有、4.8 擴寫成 `<tool_discovery>`。

**F-10　Haiku 4.5 頁的差異標記**
- 位置：method 品質警語 Q7
- 原文：「2026-10-07 回補條目才改成 treat，同時拿掉該頁的 ** 差異標記」
- 查核：該頁的頁首說明句與 2026-01-18 條目裡的 11 處標記都還在，只是 10-07 的新條目沒有再用標記。
- 處理：改寫成「新條目沒有再用 ** 標示差異；該頁 01-18 條目裡的標記與頁首說明句都還在」。

**F-14　兒童用藥段不是同一份文字**
- 位置：index 原理段與世代對照表、shifts F-5、themes 4.5、branches 兄弟版表、報告 §A.1 第 9 點
- 原文：index 寫「兒童用藥段也一樣」（接在政治中立段「五天內逐字裝進 6 個模型」之後），對照表寫「兒童用藥、政治中立以同一段文字在數天內推到多個模型」；其他幾頁寫「寫法三種」
- 查核：`<medical_guidance>` 有四份文字。213 字版見於 Sonnet 5.5（10-07 起）、10-27 與 10-30 的八頁、Fable 5.2；247 字版見於 Haiku 5.5 的兩個條目；258 字版見於 Haiku 4.5 的兩個條目；210 字版見於 Sonnet 4.6 的兩個條目。10-07 首發的四頁是四份文字，到 10-30 才統一，前後 23 天。五天內逐字推到 6 個模型的只有政治中立段。
- 處理：各頁統一寫成「四頁四份文字、三種寫法（Sonnet 5.5 與 Haiku 5.5 只差一句與一個詞）」，index 把兩個模組分開敘述。

**F-16　Opus 5.5 對照範例的描述**
- 位置：index 原理 1、shifts F-2、quiz 第 17 題解析
- 原文：好示範「只問一句會不會讓她難堪」；壞示範換成「比較安全」的版本
- 查核：`<good_response>` 問了兩件事：「Should the pregnancy hint be something just she gets or more overt?」與「Would that embarrass your friend?」［Opus 5.5 / 2026-10-27］。「比較安全」是本站的轉述，條文沒有這個詞，卻加了引號。
- 處理：改成「只問暗示要含蓄還是明顯、會不會讓她難堪」與「改寫成不帶暗示的版本」。

**F-18　兒少「拒絕後提高警覺」的年代**
- 位置：index 與過往世代的對照表，「多輪攻防」列
- 原文：2024–2025 欄寫「兒少：拒絕後提高警覺」
- 查核：「all subsequent requests in the same conversation」那一條首見於 Opus 4.7（2026-04-16）。2025 年的條文只有「escalating detachment from reality」那一句（2025-07-31 到 2025-10-15）。
- 處理：2024–2025 欄改成「只有 2025-07 起的『留意逐步脫離現實』」，兒少與武器兩條移到 2026 上半欄並標明版本。

**F-20　「三年後」**
- 位置：shifts 躍遷 A
- 原文：`{{currentDateTime}}`「這個小細節預示了三年後整套組裝式架構」
- 查核：2024-07 到 2025-11（公開區塊變成 `<claude_behavior>` 組件）是 16 個月。
- 處理：改成「預示了 2025-11 之後的組裝式架構」。

**F-23　Sonnet 5 與 Fable 5.1 的先後**
- 位置：shifts F-4
- 原文：「Fable 5.1 加 reply_after_tool_calls，Sonnet 5 再加一段 `<proactivity>`」
- 查核：Sonnet 5 的條目標 2026-06-30，早於 Fable 5.1（09-01）。
- 處理：順序對調，並標上日期。

**F-26　語言跟隨規則的首見版本**
- 位置：shifts C-1、`data/versions.js` 第 11 列、報告 §2 第 11 列
- 原文：Sonnet 3.7「首見……語言跟隨規則」
- 查核：「always responds to the user in the language they use or request」在 Sonnet 3.5 的 2024-07-12 首版就有。稱呼先後寫成 user（2024-07、09）、human（2024-10、11）、person（Sonnet 3.7）；Sonnet 3.7 多的只是法語、冰島語的例子與「Claude is fluent in a wide variety of world languages」。themes 4.13 的日期本來就對，兩頁互相矛盾。
- 處理：shifts 與 versions.js 改寫成「不是這一版才有，這一版只是改寫並加例子」。

**F-27　引文警語在 Sonnet 3.7 就拿掉了**
- 位置：shifts C-2、報告 §3.3
- 原文：Claude 4 整批移除的補丁清單裡有「引文警語」
- 查核：「If Claude mentions or cites particular articles」一句最後見於 Sonnet 3.5 的 2024-11-22 條目，Sonnet 3.7（2025-02-24）已經沒有。
- 處理：從清單拿掉，改註「引文警語與『不能開網址』更早，在 Sonnet 3.7 就已拿掉」。

**F-30　三個固定句的結束日期**
- 位置：themes 4.1 兩列、報告 §4.1
- 原文：「2024-07-12 → 2025-09-29」
- 查核：「The assistant is Claude, created by Anthropic.」等三句最後見於 Haiku 4.5 的 2025-10-15 條目。
- 處理：改成 2025-10-15。

**F-31　Haiku 4.5 的截止日與選舉**
- 位置：themes 4.2、quiz 第 5 題解析
- 原文：回補的 Haiku 4.5 保留 `<election_info>`，「它的截止日仍在選舉結果之前」；quiz 寫「截止日是 2025-01，選舉結果仍在訓練資料之外」
- 查核：該條目自述的截止日是 end of January 2025，在 2024 年 11 月的選舉與 2025-01-20 的就職之後。
- 處理：改成「截止日（2025 年 1 月底）在選舉之後、緊貼就職日，條文仍補上這段事實」。

**F-32　claude-sonnet-5-5 開始列出的日期**
- 位置：themes 4.3 model string 列
- 原文：「10-07 各頁才改列 claude-sonnet-5-5、claude-haiku-5-5」
- 查核：claude-sonnet-5-5 從 09-28 的 Sonnet 5.5 頁就列了；claude-haiku-5-5 從 10-07 開始；Opus 5.5 自己的清單到 10-27 才更新。
- 處理：三個日期分開寫明。

**F-33　「Claude 3 model family」一句的首見日期**
- 位置：themes 4.3、報告 §4.3
- 原文：產品知識時效聲明標 2024-10-22
- 查核：「does not know any other details of the Claude 3 model family」在 Sonnet 3.5 的 2024-07-12 首版就有（共 8 個版本檔）。
- 處理：日期改成 2024-07-12。

**F-34　「beta products」**
- 位置：themes 4.3 Google Workspace 列
- 原文：「同一輪 Chrome、Excel、PowerPoint 等不再稱 beta products」
- 查核：「beta products」見於 10 個版本，最後是 Sonnet 5（2026-06-30）；Opus 5（07-24）起的新模型從來沒用過。10 月只是回補的舊模型條目跟著拿掉。
- 處理：改寫成上述事實。

**F-35　「concise response」一句的年代**
- 位置：themes 4.4 的 2024-10-22 列、報告 §4.4
- 原文：把「Rather than giving a long response, it gives a concise response and offers to elaborate」列為 2024-10-22 的內容
- 查核：這一句 2024-07-12 就有（到 2024-10-22 共 5 個版本檔），2024-11-22 才刪。
- 處理：加註「這句從 2024-07 就有，11-22 刪」。

**F-36　反條列規則的首見版本**
- 位置：themes 4.4、報告 §4.4
- 原文：反條列規則標 2024-11-22
- 查核：「its prose should never include bullets or numbered lists anywhere」先見於 Haiku 3.5 text-only（標 2024-10-22），再進 Sonnet 3.5 的 11-22 條目。
- 處理：日期欄改成「2024-10-22（Haiku 3.5）、2024-11-22（Sonnet 3.5）」。

**F-39　「Claude is honest by default」的首見版本與字單**
- 位置：themes 4.8、報告 §4.8
- 原文：「Fable 5.1 «Claude is honest by default» 成為禁用強調詞（genuinely／honestly／actually）的理由」
- 查核：這一句首見於 Opus 5（2026-07-24），只見於 Opus 5 與 Fable 5.1 的四個條目。附這個理由的字單是 genuinely／honestly／straightforward；actually 屬於 Opus 4.8 的版本，那一版沒有理由句。
- 處理：改成「Opus 5（2026-07-24）與 Fable 5.1」，字單改正，並註明 Opus 4.8 的 actually 版沒有附理由。

**F-44　「20 個月後原封不動」**
- 位置：branches 規則來回表與結論框
- 原文：「intellectually curious」段「2025 年 5 月被刪除，20 個月後原封不動出現在 Opus 5」
- 查核：這是兩句話。「intellectually curious」那句見於 2024-07-12 到 2024-11-22，Sonnet 3.7（2025-02）已經沒有；「engages in authentic conversation」那句見於 2024-10-22 到 Sonnet 3.7，Claude 4（2025-05）才刪。兩句在 Opus 5（2026-07-24）一起回來，第二句逐字相同，第一句改寫過。從 2025-05 到 2026-07 是 14 個月。
- 處理：表格的首見與刪除日期各列兩個，敘述改成「第二句逐字相同，第一句改寫過；距離被刪 14 個月」。

**F-50　沒有任何檔案被正規化過**
- 位置：method 查核紀錄、`evidence/README.md` 步驟 2、報告 §A.0
- 原文：「Oct 22 2024 條目已正規化」只對 Haiku 3.5 成立（Haiku 3.5 的兩檔有正規化）
- 查核：Haiku 3.5 的官方原始頁從來沒有字面反斜線 n（09-07 與 11-05 兩份快照都是 0 個）。有的只有 Sonnet 3.5 頁（147 個），它的兩個 2024-10-22 版本檔一直保留原樣（72 與 75 個）。
- 處理：改寫成「沒有任何檔案被正規化」。

**F-57　Sonnet 4.5 刪掉的段數**
- 位置：shifts D-1、quiz 第 2 題解析、`data/versions.js` 第 18 列、報告 §2 第 18 列
- 原文：Sonnet 4.5（2025-09-29）「一次刪掉 AI 本性、反諂媚、紅旗等 12 段」
- 查核：Opus 4.1 有 17 段（共 1,048 字）在 Sonnet 4.5 的 09-29 條目找不到相似度 0.6 以上的對應段落。「12」是 2025-07-31 新增的段數；那 12 段裡被刪的是 7 段，留下 5 段（3 段逐字、2 段只改一兩個字）。另外 10 段是 05-22 就有的。
- 處理：改成「17 段在新版找不到對應」。

**F-59　「markdown for code 一直都在」**
- 位置：quiz 第 3 題解析
- 原文：「markdown for code 是格式規則，一直都在」
- 查核：「uses markdown for code」見於 10 個版本，最後是 Sonnet 3.7（2025-02-24），Claude 4（2025-05-22）起已經沒有。
- 處理：解析改寫。順帶發現官方 overview 至今還拿「always providing code snippets in Markdown」當例子，新增為品質警語 Q11。

**F-62　「砍半」**
- 位置：versions 學習目標
- 原文：「2025-09-29（砍半）」
- 查核：2,880 → 1,973 是減少 31.5%；對同一線的 Sonnet 4（2,561）是減少 23.0%。
- 處理：改成「砍掉三成」。

**F-65　引號裡的字不是逐字**
- 位置：`data/versions.js` 第 9／10 列、報告 §2 第 9／10 列
- 原文：刪「concise and offers to elaborate」
- 查核：沒有任何版本含這串字；原句是「gives a concise response and offers to elaborate」。這個欄位不在引文查核工具的涵蓋範圍，所以前幾輪沒抓到。
- 處理：改成「concise response and offers to elaborate」一句。

**F-67　報告 §0 與 §3.3 互相矛盾**
- 位置：報告 §0 第 6 點（網頁沒有這一句）
- 原文：Claude 4（2025-05-22）拿掉的補丁包括「不能開 URL」
- 查核：「cannot open URLs」見於 9 個版本檔，最後是 Sonnet 3.5 的 2024-11-22 條目。報告 §3.3 自己寫著它「早在 3.7 就已刪除」。
- 處理：列入增補 §C.3。

### 3.2 B 類：範圍寫得太寬（9 項）

**F-03　Haiku 5.5 新寫的 1,577 字「全部在教它守住」**
- 位置：index 5.5 對照表引言、shifts F-3、`data/versions.js` 第 37 列、報告 §A.1 第 6 點
- 原文：「除了開頭一段記憶指令，全部在教它『守住』」
- 查核：1,577 字裡還有一句 18 字的身分定位，以及同一天推到四個模型頁的兒童用藥段（Haiku 版 247 字）。算法不把同日的兄弟版當參照；若算進去，Haiku 自己新寫的是 1,360 字。
- 處理：改成「除了開頭一段記憶指令和一句身分定位，都在教它守住」，並註明 1,360 這個對照數字。

**F-04　「第一次」出現最快的模型拿最長的 prompt**
- 位置：index 字數走勢說明、quiz 第 18 題解析
- 原文：「5.5 世代首版第一次出現『最快的模型拿最長的 prompt』」
- 查核：2025-10-15 的 Haiku 4.5（1,976 字）已經比 Sonnet 4.5（1,973 字）多 3 個字，當時 Opus 4.5 還沒發布。
- 處理：拿掉「第一次」，括號補上 2025-10 的前例，並說明那兩份幾乎是同一份文字。

**F-06　5.5 世代「不談工具」**
- 位置：index 世代對照表、六個轉變對照表、十點結論第 8 點；shifts F-4 與躍遷 F 結論 3；themes 4.11；報告 §A.3
- 原文：「三個 5.5 版本的行為組件不談工具」「5.5 世代全部移出」「唯一的例外是 Haiku 5.5 開頭的記憶指令」
- 查核：5.5 條目確實沒有工具作業區塊（acting_vs_clarifying、capability_check、tool_discovery、reply_after_tool_calls、proactivity 都不在）。但政策段落裡留著條件句：兒童用藥段「If web search is available, Claude uses it to find the product's label」，出口管制通知「Claude checks for newer information when it can search」，知識截止段「points to web search」，以及 Haiku 5.5 的 `<memory_listing>` 指令。
- 處理：全站改成「沒有工具作業區塊，只剩政策段落裡的條件句」；themes 4.11 新增一列列出這些條件句。

**F-07　「唯一公開的設計說明」**
- 位置：index「推論的限度」
- 原文：「Anthropic 唯一公開的設計說明是上面那篇 Claude Code 部落格」
- 查核：本站無從證明「唯一」。光是這一輪，就多了一篇與條文直接對應的官方公告（Fable 5.2 發布公告談訓練限制與安全路由）。
- 處理：改成「本站引用的官方說明只有兩篇」，並列出是哪兩篇、各談到什麼。

**F-12　公開區塊「只剩一個組件」**
- 位置：index 十點結論第 4 點、themes 4.1、報告 §0 第 4 點
- 原文：「2025-11-19 起公開區塊只剩一個 `<claude_behavior>` 組件」
- 查核：有 9 個版本在 `</claude_behavior>` 之後另有一塊：Opus 4.8、Opus 5、Fable 5.1（各兩個條目）掛 5 個字的 `<tone_preference>`，Sonnet 5（兩個條目）掛 79 個字的 `<conversational_register>`，Fable 5.2 掛 171 個字的 `<forged_notices>`。
- 處理：改成「以 `<claude_behavior>` 組件為主體」，並列出這些例外。

**F-19　「舊模型」**
- 位置：index 原理 3、shifts F-6、themes 4.4、報告 §B.1 第 6 點
- 原文：「禁詞只留在舊模型、新的文風禁令也只加給舊模型」
- 查核：10-30 仍保留禁詞、並新加「does not quote or paraphrase」一句的模型包括 Fable 5.1，它當時是最高階的在售模型，不能叫舊模型。「Claude writes plainly」那一段則只加給 Opus 5 一個模型。
- 處理：改成「5.5 世代以前發布的模型（包括當時仍是最高階的 Fable 5.1）」「新的文風禁令只加給 Opus 5」。

**F-24　prompt 是「唯一管道」**
- 位置：shifts 躍遷 F 結論、index 原理段末句
- 原文：「prompt 是把新政策送進舊快照的唯一管道」
- 查核：本站自己就記錄了別的管道：分類器觸發的 `<anthropic_reminders>`，以及安全路由。
- 處理：改成「一條公開可見的管道（另外還有分類器提醒與安全路由）」；index 同一句加上「推論」標示。

**F-45　Sonnet 與 Haiku「第一次」差異很大**
- 位置：branches Sonnet／Haiku 分支卡
- 原文：「到 5.5 世代，Sonnet 與 Haiku 第一次在同一天拿到差異很大的兩份文字」
- 查核：2024-10-22 的 Sonnet 3.5 與 Haiku 3.5（text-only）逐字相同的段落只有 489 字，佔 Haiku 的 31%、Sonnet 的 25%。4.5 世代的同日條目有 98% 相同，5.5 世代是 55%。
- 處理：改寫成這三個數字，拿掉「第一次」。

**F-46　「Opus 4.8 起」不引用 system prompt**
- 位置：branches 實務含意第 6 點
- 原文：「Opus 4.8 起 «does not attribute its behavior to its system prompt»」
- 查核：這一句只見於 Opus 4.8 的兩個條目（2026-05-28、10-30），之後的模型都沒有。
- 處理：改成「只有 Opus 4.8 的條文寫著……Fable 5 以後的模型都沒有這一段」，並把結尾的建議改成直接對照公開條文。

### 3.3 C 類：推論寫得比證據強，或沒有證據（8 項）

**F-02　tone_and_formatting「從 918 字縮到 362 字」**
- 位置：index 原理 3、shifts F-1、themes 4.4、報告 §A.1 第 5 點
- 原文：「`<tone_and_formatting>` 從 Opus 4.7 的 918 字縮到 362 字」
- 查核：兩個數字都對，但會讓人以為 Opus 5.5 把這一塊砍掉六成。Opus 4.7 的 918 字裡巢狀著 lists_and_bullets（265 字）、acting_vs_clarifying（205 字）、capability_check（140 字）。逐版是 918（Opus 4.7）→ 427（Opus 4.8）→ 338（Opus 5）→ 362（Opus 5.5）；Fable 5.1 是 503 字。Opus 5.5 比直接前身還多 24 字。
- 處理：改成「362 字，比 Fable 5.1 的 503 字短，但比直接前身 Opus 5 的 338 字略長」，並說明 918 字裡有 345 字是巢狀的工具區塊。

**F-29　安全路由「在使用者不知情下」換模型**
- 位置：shifts 躍遷 E 結論 2、報告 §3.5
- 原文：「安全路由甚至可在使用者不知情下換模型」
- 查核：條文只寫「The user may be confused about this situation」［Opus 5 / 2026-07-24 / fable_safeguards_routing］，沒有說不告知。官方的 Fable 5 發布文寫的是「Users will be informed whenever this occurs」，Fable 5.2 的公告也稱之為 transparent fallbacks。
- 處理：改成「條文自己寫著使用者可能因此困惑」，並引條文那一句與 Fable 5 發布文那一句。

**F-40　語言跟隨規則「刪除後行為未變」**
- 位置：themes 4.13、quiz 第 13 題解析
- 原文：「一條明確、可觀察、且刪除後行為未變的規則」
- 查核：這是行為主張，證據包裡沒有任何行為資料；本站在別處明講只處理條文。
- 處理：改成「從 prompt 消失後沒有再回來」，並註明「現在的 Claude 仍會跟著使用者的語言回答」只是一般使用經驗，本站沒有實測。

**F-47　舊模型重建的起點**
- 位置：index 原理段、十點結論第 9 點、世代對照表；shifts F-5、F-6 與結論；branches 分支卡；method Q8；`data/versions.js` 第 38、39 列；quiz；報告 §A.2 與 §B.1 第 5 點
- 原文：10-07 的舊模型是「舊骨架＋新模組」（Haiku 4.5「保留 2026-01 的骨架」），10-30 的舊 Opus 才是「用新格式整份重建」
- 查核：用本站自己的算法，新條目逐字留自自己前一條目的比例是：Sonnet 4.6（10-07）22.6%、Haiku 4.5（10-07）27.9%、Opus 4.6（10-30）15.4%、Opus 4.7（10-30）24.5%。10-07 的 Sonnet 4.6 留下的比 10-30 的 Opus 4.7 還少。Sonnet 4.6 有 48.4% 只見於 Opus 4.8 的五月版，Haiku 4.5 有 50.2% 只見於 Sonnet 5。真正屬於就地增補的是 10-30 的 Opus 4.8（68.0%）、Opus 5（72.9%）、Fable 5（74.7%）、Fable 5.1（81.6%）、Sonnet 5（82.5%）。
- 處理：全站改成「舊模型從 10-07 起陸續重建」，各頁補上這幾個數字。這是本次稽核影響面最大的一項。

**F-48　Opus 5 的骨架「不是 Fable 5」**
- 位置：branches Opus 分支卡、quiz 第 9 題、`data/versions.js` 第 31 列、報告 §0 第 9 點
- 原文：「Opus 5 的骨架承自 Opus 4.8，不是同期的 Fable 5」；quiz 解析「時間上更近的版本不代表血緣更近」
- 查核：Opus 5 確實把 Fable 5 刪掉的 default_stance、tone_preference、Claude Design、CBRN 全段從 4.8 裝了回來。但逐字段落有 48.4% 見於 Opus 4.8、46.2% 見於 Fable 5（只見於 4.8 的 15.9%，只見於 Fable 5 的 13.7%，兩邊都有的 32.5%）；連小幅改寫一起算是 69.7% 對 57.8%，偏向 4.8，但不是「不是 Fable 5」。區塊的組成兩邊都不完全相同：4.8 的 tool_discovery、respond_without_citing_system_prompt、lists_and_bullets，Opus 5 都沒有。
- 處理：改成「把 Fable 5 刪掉的幾塊從 4.8 裝了回來，文字則兩邊都取」，補上百分比；quiz 第 9 題的題幹、選項與解析改寫（答案仍是第二個選項）。稽核中途我一度把它改成「區塊結構承自 Opus 4.8」，複核區塊清單後發現這也說得太滿，再改成現在的寫法。

**F-56　Sonnet 5.5 是「Sonnet 5 骨架」**
- 位置：`data/versions.js` 第 35 列、branches Sonnet 分支卡、報告 §A.2
- 原文：結構欄寫「Sonnet 5 骨架」
- 查核：Sonnet 5.5（09-28）的逐字段落有 69.3% 見於六天前的 Opus 5.5，56.2% 見於 Sonnet 5；只見於 Opus 5.5 的 32.1%，只見於 Sonnet 5 的 19.0%。
- 處理：改成「模組庫組裝（69% 逐字同 Opus 5.5、56% 同 Sonnet 5）」。

**F-66　「行為未見回退報導」**
- 位置：shifts D-1 的推論說明
- 原文：「此推論的依據是『段落消失』加上行為未見回退報導，強度中等」
- 查核：證據包裡沒有任何關於行為回退與否的資料，這半句沒有出處。
- 處理：改成「依據只有『段落消失』」，並加上「也沒有實測行為」。

**F-68　Opus 5.5 是「Opus 5 骨架＋Fable 5.1 模組」**
- 位置：index 原理 3 與十點結論第 10 點、branches Opus 分支卡、quiz 第 16 題解析、`data/versions.js` 第 34 列、報告 §A.1 第 1 點與 §A.2 第 34 列
- 原文：「Opus 5.5 的骨架是 Opus 5……裝進來的是 Fable 5.1 的模組」；「Opus 5.5＝Opus 5 骨架＋Fable 5.1 模組」
- 查核：網頁自己列的出處拆分就不支持「骨架是 Opus 5」。Opus 5.5（09-22）的逐字段落見於 Fable 5.1 的佔 49.9%（986＋1,069 字），見於 Opus 5 的佔 36.7%（443＋1,069 字）；連小幅改寫一起算是 70.6% 對 55.3%。區塊的組成和 Fable 5.1 相同（只少 reply_after_tool_calls 與 tone_preference），Opus 5 沒有的 `<lists_and_bullets>` 它有。只見於 Opus 5 的 443 字是產品資訊的六段（257 字）、常規武器段（124 字）和另外兩句。
- 處理：全站改成「Opus 5 與 Fable 5.1 合併，較靠近 Fable 5.1」，兩邊各貢獻什麼的清單保留。這一項是寫本報告時，拿 F-48、F-56 的同一把尺回頭量才發現的。

### 3.4 D 類：前幾輪留下的過期敘述（12 項）

這一類寫的時候是對的，後來的幾輪補了新條目卻沒有回頭改。

| 編號 | 位置 | 原文 | 現況與處理 |
|---|---|---|---|
| F-15 | index 原理 4 | Opus 5.5 的模型清單「停在 09-22 當下：列 Sonnet 5 與 Haiku 4.5」 | 09-22 條目確實如此，但 10-27 的修訂已改列 Sonnet 5.5、Haiku 5.5。補上這一句。 |
| F-21 | shifts E-5 | Fable 5.1 是「本站證據包唯一需要手動合併還原的頁面」 | 現在 Fable 5.1、Opus 5.5、Sonnet 5 三頁的六個條目與 Fable 5.2 都被切成多塊，而且是腳本接回，不是手動。改寫。 |
| F-22 | shifts F-1 | Opus 5.5 的 `<refusal_handling>`（1,774 字）「是全部 39 版裡最大」 | 當時是 39 版；現在最大的是同一頁 10-27 條目的 1,793 字。改成「當時 39 版裡最大」並補後續。 |
| F-38 | themes 4.5 著作權列 | 「Fable 5.1 獨有」 | 同一列後面就寫 Opus 5.5 整段收了進去。改成「首見」。 |
| F-41 | branches 註與頁尾 | 「32 組 word-diff」 | 稽核時是 47 組（同一頁別處寫的是 47），現在 51 組。更正。 |
| F-43 | branches 規則來回表 | genuinely 禁詞「5.5 世代全刪，只留在回補的 Sonnet 4.6」；星號動作、emoji 兩列同樣只提 10-07 的回補條目 | 10-30 的 Opus 4.6、Opus 5、Fable 5.1（與 Opus 4.8 的 actually 版）也保留禁詞；Opus 4.6 保留星號規則；Opus 4.6、4.7、4.8 保留 emoji 規則。三列補齊。 |
| F-49 | method 附錄 A | 「Sonnet 5.5（兩個條目）」 | 現在三個條目（09-28、10-07、10-27）。拿掉括號。 |
| F-51 | method Q7 | or／nor 並存的版本清單只列到 10-07 | 第三輪之後 or 的寫法見於 12 個版本，加上 Fable 5.2 是 13 個；nor 只在 4 個。補齊。 |
| F-54 | `data/versions.js` 檔頭註解 | 「39 個分析版本……33–39 為 2026-10-28 重抓新增」 | 檔案早已有 51 列（現在 52）。註解更新。 |
| F-55 | `data/versions.js` 第 32 列 | Fable 5.1（09-01）「歷史最長」 | 當時最長（4,267 字）；10 月下旬起陸續被超過，目前最長是 Fable 5.2 的 4,975 字。改成「當時最長」。 |
| F-60 | matrix 自我檢測第 4 題 | training-data cutoff「只出現在第 31 欄與第 38 欄」 | 現在是第 31、38、41、47、49、50 欄。題目更新。 |
| F-61 | matrix 頁尾 | 矩陣原始檔由 PowerShell 逐一比對產生 | 第一輪是這樣，2026-10-28 起由 `evidence/tools/build_matrix.py` 重建。更正。 |

### 3.5 E 類：補充註記（10 項）

這一類不算錯，但少了一句容易誤讀。

| 編號 | 位置 | 問題 | 處理 |
|---|---|---|---|
| F-09 | 全站「51 個版本」 | 官方條目其實是 53 個，哪兩個沒列、為什麼，沒有一處用一句話講清楚 | method 與 versions 頁補上：Opus 4 的 2025-07-31、08-05 兩個條目與 Sonnet 4 同日版本只差名稱、定位語與 model string，不另列欄。 |
| F-11 | matrix | 子字串比對讓短片語命中較長的另一句（3 格） | matrix 頁與 method 頁加說明，舉「Markdown formatting」為例。 |
| F-25 | shifts A | Haiku 3「功能只有四件事」 | 全文另有一句列出能幫的任務、一句要它不主動提這些關於自己的資訊。改成「主要做四件事」並補上這兩句。 |
| F-28 | shifts D-2 | 「三個從 2024 年沿用至今的固定句」 | 第三句在 2024 年寫的是 a human，2025-02 起才是 a person。加註。 |
| F-37 | themes 4.4 | 把「should instead write in prose and paragraphs without any lists」列為 2025-05-22 的內容 | 前半句 2024-11 就有，Sonnet 3.7 沒有，Claude 4 加回並補上粗體限制。加註。 |
| F-42 | branches 兄弟版表的引言 | 「47 組 word-diff 中，跨模型比對的十二組」 | 表列的比對不都有對應的 diff 檔（Sonnet 4 對 Opus 4 就沒有）。改成「十四組跨模型比對（多數有對應的 word-diff 檔）」。 |
| F-52 | method 血緣算法 | 算法的四個限制沒有揭露 | 補上：參照組用的是條目上標的日期（Sonnet 5 頁是事後上架的）；Sonnet 3.5 的兩個 2024-10-22 檔各只有一行，無法逐段比對；帶 `**` 標記的段落不會和沒有標記的同一段算成相同；同日的兄弟版不算參照，所以同一天推到多頁的模組在每一頁都算新寫。 |
| F-53 | method 附錄 B、Q7 | 附錄 B 漏了 Haiku 4.5 的 2025-11-19 條目 | 該條目只列 Sonnet 的 model string「claude-sonnet-4-5-20250929」，沒有 Haiku 自己的。補進附錄 B，並在 Q7 記一筆。 |
| F-58 | shifts D-1、quiz 第 2 題 | 「2,880 → 1,973」 | 這是 Opus 4.1 對 Sonnet 4.5；同一線的 Sonnet 4 是 2,561。兩個基準都寫出來。 |
| F-63 | versions 長條圖說明 | 「每次大改寫之後，字數會在 3 到 6 個月內回到原來的軌跡」 | Claude 4（05-22）之後兩個多月就超過原水準，Sonnet 4.5 之後約五個月。改成「幾個月內」並列出這兩個數字。 |

### 3.6 F 類：工具與呈現（2 項）

**F-08　引文查核工具有兩個盲點**
- 位置：`evidence/tools/verify_quotes.py`
- 問題：一，比對前把大小寫抹平，所以大小寫不符的引文也會過關。二，行內引文只檢查「出現在某個版本」，不檢查是不是文字所說的那個版本；`data/versions.js`、報告、README 也不在涵蓋範圍內。
- 影響：這一次沒有因此漏掉錯的引文（改成區分大小寫後全數通過），但 F-65 那種引號裡不是逐字的情況，工具本來就抓不到。
- 處理：改成區分大小寫；第二個盲點寫進工具的說明，並提供 `tools/audit/a4_worksheet.py`（列出每段引文實際出現的版本）與 `a5_report.py`（檢查報告、README、versions.js 裡的英文句）。

**F-64　版本頁長條圖溢出**
- 位置：versions 頁的字數長條圖
- 問題：比例尺的上限寫死成 4,400 字。超過約 4,800 字的長條會畫出圖框，約 4,560 字以上的數字標籤被裁掉，受影響的是 Haiku 5.5（4,587）、Opus 5.5（4,821）、Fable 5.1（4,853）幾列。
- 處理：上限改成由資料的最大值決定。

### 3.7 編號對照

- A 類（25）：F-01、05、10、14、16、18、20、23、26、27、30、31、32、33、34、35、36、39、44、50、57、59、62、65、67
- B 類（9）：F-03、04、06、07、12、19、24、45、46
- C 類（8）：F-02、29、40、47、48、56、66、68
- D 類（12）：F-15、21、22、38、41、43、49、51、54、55、60、61
- E 類（10）：F-09、11、25、28、37、42、52、53、58、63
- F 類（2）：F-08、64
- 未使用：F-13。撤回：F-17（見第 4 節）。

---

## 4. 撤回的發現，與稽核過程中我自己的錯

稽核者也會錯。以下幾件事都在過程中被自己的複核抓到，沒有留在任何成品裡，但應該留下紀錄。

1. F-17 撤回。我一度認定「Opus 5.5 收了 Fable 5.1 的毒品減害段」這句話是錯的，理由是用區分大小寫的方式搜尋 drug 找不到。那一段用的詞是 illegal substances 與 harm-reduction，確實在 Fable 5.1（09-01）與所有 5.5 條目裡，Opus 5.5 只改了一個詞（user 改成 person）。原敘述正確。教訓：追一個主題要用條文實際的用詞，不能用自己想的關鍵字。
2. 我曾告訴使用者，網站「完全沒有揭露」官方頁面上那句關於 `**` 差異標記的說明。其實有，就是品質警語 Q4。下一則訊息就更正了，沒有寫進任何檔案。
3. F-48 的第一次修正把「骨架承自 Opus 4.8」改成「區塊結構承自 Opus 4.8」。寫本報告時複核區塊清單，發現這個說法同樣太滿（Opus 4.8 有三個區塊是 Opus 5 沒有的），於是再改一次。也是這次複核帶出了 F-68。
4. 底稿曾記「2025-07-31 新增的 12 段裡有 4 段留到 Sonnet 4.5」。複核是 5 段（3 段逐字、2 段只改一兩個字），被刪的是 7 段。網頁與報告用的是複核後的數字。
5. 一個工具陷阱：在 Windows 的 Git Bash 用 heredoc 把程式餵給 Python 時，兩個連續的反斜線會被壓成一個，讓一支比對 Sonnet 3.5 與 Haiku 3.5 的程式算出 0% 相同。改成存檔後執行就正常。這一點已寫進 `evidence/tools/audit/README.md`。

---

## 5. 官方的新資訊（第四次重抓，2026-11-10）

### 5.1 系統提示詞發行說明

- overview 與 23 個模型頁全部重抓。22 個既有模型頁與 11-05 的快照逐位元組相同。
- overview 只多一張卡片，指向新頁 Fable 5.2（`evidence/diffs/50_overview_1105_to_1110.diff`）。
- 新頁 Fable 5.2 只有一個條目，日期 2026-11-09。原始頁在 `<example>` 處被切成兩塊，接回後 4,975 字，是 52 個版本裡最長的。

### 5.2 Fable 5.2 這一版的重點

逐字引文與座標見報告增補 §C.1，這裡只列數字。

- 組成：69.9% 逐字沿用更早的版本（3,477 字、102 段），9.5% 小幅改寫，20.6% 新寫（1,023 字）。
- 血緣：逐字段落見於 Opus 5.5（10-27）的佔 64.8%，見於前身 Fable 5.1（10-30）的只有 47.1%；102 段全部至少見於三個 5.5 模型之一，只見於 Fable 5.1 的是 0 字。區塊的組成也和 Opus 5.5（10-27）相同，只多一個 `<forged_notices>`。
- 拿掉的：Fable 線自己首創的條文幾乎都不在了（兒少 pattern level 與 detection mechanics、毒品段、禁詞、reply_after_tool_calls、tone_preference 等）。
- 沒拿的：Opus 5.5 的灰色地帶「先問一句」程序與對照範例。
- 拿到的：Haiku 5.5 那一型「此後整段對話有效」的規則（不寫遺書、不給飲食數字）。
- 新寫的七件事：兒少三條改寫（269 字）、投票協助段（205 字）、不寫遺書規則的擴寫（178 字）、頁尾新區塊 `<forged_notices>`（171 字）、訓練時限制特定能力的說明（86 字）、簡短段（82 字）、身分句（30 字）。
- 幾個歷來最大：全文 4,975 字、兒少區塊 545 字、`<evenhandedness>` 737 字。

### 5.3 官方發布公告（輔助來源）

Anthropic 2026-11-09 的 Fable 5.2 發布公告（https://www.anthropic.com/claude-fable-and-mythos-5-2）有幾句與條文直接對應，已逐字收進 `evidence/external/excerpts.txt`：

- 訓練時限制了最能直接加速 AI 研發的特定研究能力，相關領域的表現大約在 Opus 5.5 的水準；這些限制做在訓練階段，不是在推論階段調整。對應條文裡新寫的訓練限制說明。
- 被安全分類器擋下的查詢，資安類改由 Opus 4.8 回答、生物類改由 Opus 5 回答；AI 研發領域另有少數題目改由 Opus 5 回答。Fable 5.2 的公開條文本身沒有路由段。
- Fable 與 Mythos 是同一個底層模型。

另外補收了 2026-06-09 Fable 5 發布文裡的一句「Users will be informed whenever this occurs」，用來更正 F-29。

### 5.4 對既有結論的影響

- 變弱的：「判斷給 Opus、規則給 Haiku」的分層推論。Fable 5.2 定位在 Opus 之上，卻拿到 Haiku 式的持續性規則，沒有先問程序，也沒有全大寫強調。比較站得住的說法是持續性規則正往各模型擴散；「先問一句」只有 Opus 5.5 一個模型有，看不出是層級特徵還是單一模型的補丁。
- 變強的：「各分支收斂成一個模組庫」。Fable 這條分支到這一版併了回去。
- 多了一種「prompt 只寫權重不可能知道的事」：模型在訓練時被刻意少學了什麼，由 prompt 告訴它。
- 選舉時間的低強度推論再降一級：政治中立模組在期中選舉之後不但保留，還加寫了投票協助段，不是選前限定。

---

## 6. 這次動了哪些檔案

| 檔案 | 變動 |
|---|---|
| `evidence/sources/claude-fable-5-2.md` | 新增（官方原始頁） |
| `evidence/sources/overview.md` | 更新為 2026-11-10 的版本（多一張卡片） |
| `evidence/versions/claude-fable-5-2__November_9_2026__default.txt` | 新增（第 54 個版本檔） |
| `evidence/diffs/47`–`50` | 新增四組：Fable 5.1 → 5.2、Opus 5.5 對 Fable 5.2、Haiku 5.5 對 Fable 5.2、overview 11-05 → 11-10 |
| `data/matrix.json`、`data/matrix.js`、`evidence/feature_matrix.txt` | 重建：多第 52 欄與 15 個片語，舊格逐格不變 |
| `evidence/tools/build_matrix.py` | 加入第 52 欄與 15 個片語 |
| `evidence/tools/verify_quotes.py` | 改成區分大小寫，說明裡寫明涵蓋範圍的限制 |
| `evidence/tools/audit/` | 新增：稽核用的獨立程式與說明 |
| `evidence/external/excerpts.txt` | 加上雜湊不可重驗的說明、兩篇舊來源的重驗紀錄、Fable 5.2 發布公告的逐字句 |
| `index.html`、`shifts.html`、`themes.html`、`branches.html`、`method.html`、`quiz.html`、`matrix.html`、`versions.html`、`about.html` | 第 3 節各項更正，加上 Fable 5.2 的內容（總覽新增一節、躍遷 F-7、各主題的新列、兩題新測驗、品質警語 Q11、稽核紀錄一節） |
| `data/versions.js` | 11 列措辭更正（第 9／10、11、18、31、32、34、35、37、38、39、51 列），新增第 52 列 |
| `README.md`、`evidence/README.md` | 數字與說明更新 |
| `report/changelog-zh-TW.md` | 檔頭一行、文末新增增補 §C；第一輪本文與 §A、§B 不動 |
| `report/audit-2026-11-10-zh-TW.md` | 本報告 |

---

## 7. 重現方式

全部在 repo 根目錄執行，只讀證據包，不連網。

```
python -I evidence/tools/audit/a1_sources.py evidence/sources evidence/versions
python -I evidence/tools/audit/a2_matrix.py .
python -I evidence/tools/audit/a3_diffs.py .
python -I evidence/tools/verify_quotes.py .
python -I evidence/tools/audit/a4_worksheet.py . index.html worksheet_index.txt
python -I evidence/tools/audit/a5_report.py . report/changelog-zh-TW.md
python -I evidence/tools/audit/c_index1.py .
python -I evidence/tools/audit/c_branches2.py .
python -I evidence/tools/audit/c_parents.py .
python -I evidence/tools/audit/r4_fable52.py .
```

前四支是機械式的重現檢查，應該印出 0 處不符。`a4_worksheet.py` 產生的底稿要人讀：每段英文引文後面列著它實際出現的版本，逐段對照文字所說的版本。後四支重算血緣比例、各版本對兩個候選來源的歸屬（F-48、F-56、F-68 的數字）與 Fable 5.2 的各項數字。各程式的說明在 `evidence/tools/audit/README.md`。

要重驗官方來源是否改過，照 `evidence/README.md` 的步驟 1 重抓一次，再與 `evidence/sources/` 比對。

---

## 8. 沒有做的事

- 沒有實測任何模型的行為。
- 沒有讀 Fable 5.2 發布公告所引用的 System Card；本站對訓練限制與安全路由的說明只到公告為止。
- 報告原檔的第一輪本文沒有重寫，更正集中在增補 §C；直接讀本文的人要記得對照 §C.3 與 §C.4。
- 行內引文的版本歸屬仍然靠人工對照底稿，沒有做成自動檢查。
- 外部網頁的雜湊無法重驗（網頁含動態內容），能重驗的只有逐字句。
