# 稽核用的獨立程式（2026-11-10）

這個資料夾的程式是 2026-11-10 全站稽核時另外寫的，刻意不 import 上一層的工具，用來交叉驗證前三輪的產出。全部只讀證據包、不連網。結果見 `report/audit-2026-11-10-zh-TW.md`。三支 `d_*.py` 是之後為 `report/fable-5-1-to-5-2-diff-zh-TW.md` 寫的。

共用模組 `facts.py` 會載入所有版本檔並提供量測函式（字數、區塊字數、片語追蹤、逐字／小改／新寫比例、兩版共有段落）。版本標籤格式是「系列縮寫＋版號@yymmdd」，例如 `O5.5@261027`、`F5.2@261109`；Sonnet 3.5 與 Haiku 3.5 的變體加 `t`（text-only）或 `i`（text+images）。

| 程式 | 做什麼 | 用法 |
|---|---|---|
| `a1_sources.py` | 用另一種解析方式從 `sources/*.md` 重切版本檔，逐位元組比對 `versions/`；列出圍欄外的官方說明文字 | `python -I a1_sources.py ../../sources ../../versions` |
| `a2_matrix.py` | 獨立重算特徵矩陣每一格，核對 `matrix.json`、`matrix.js`、`feature_matrix.txt` 三份是否一致；測 `**` 標記、換行、大小寫三種敏感度 | `python -I a2_matrix.py <repo_root>` |
| `a3_diffs.py` | 重新產生每一組版本 diff，逐位元組比對 `diffs/` | `python -I a3_diffs.py <repo_root>` |
| `a4_worksheet.py` | 把一個網頁轉成稽核底稿：每段英文引文後面標出它實際出現在哪些版本（區分大小寫），並標示跨段落拼接與沒有標記的英文句 | `python -I a4_worksheet.py <repo_root> index.html out.txt` |
| `a5_report.py` | 對 `report/`、README、`data/versions.js` 這些引文查核工具沒涵蓋的檔案，機械式檢查 4 個字以上的英文句是否逐字存在 | `python -I a5_report.py <repo_root> report/changelog-zh-TW.md` |
| `c_index1.py` | 重算總覽頁的血緣比例、區塊字數、三個 5.5 模型的對照表數字 | `python -I c_index1.py <repo_root>` |
| `c_branches2.py` | 各頁新條目對自己前一條目的保留率、兩個來源的獨占比例、同日 Sonnet／Haiku 的相同比例 | `python -I c_branches2.py <repo_root>` |
| `c_parents.py` | 一個版本對兩個候選來源的歸屬：逐字、逐字加小改的比例，以及區塊組成的異同（F-48、F-56、F-68 的數字） | `python -I c_parents.py <repo_root>` |
| `d_f51_f52.py` | Fable 5.1（10-30）對 Fable 5.2 的逐行台帳：保留、改寫、新增、刪除，以及 5.2 各區塊與哪一版逐字相同 | `python -I -B d_f51_f52.py <repo_root> [summary\|ledger\|dropped\|blocks]` |
| `d_f51_f52_sent.py` | 同一組比對的逐句版，另查每一句的來源與去向；`md` 模式產生差異分析報告的附錄 | `python -I -B d_f51_f52_sent.py <repo_root> [summary\|added\|removed\|edited\|stats\|near\|base\|md]` |
| `d_pair_sent.py` | 任兩個版本的逐句比對（方法同上）；`length` 模式另算「長度與直說重點」的一般性指示有幾句、幾個字、出現在哪些模型頁（差異報告第 8.3 節） | `python -I -B d_pair_sent.py <repo_root> F5.1@261030 O5.5@261027 [summary\|aonly\|bonly\|edited]`；`python -I -B d_pair_sent.py <repo_root> length <label> ...` |
| `r4_fable52.py`、`r4_traces.py` | Fable 5.2 的血緣、來源歸屬、拿掉與新增的段落、各片語首見版本 | `python -I r4_fable52.py <repo_root>` |

注意：在 Windows 的 Git Bash 用 heredoc 餵 Python 時，`"\\n"` 會被壓成 `"\n"`。需要字面反斜線的程式（例如處理 Sonnet 3.5 兩個 2024-10-22 檔）請存成檔案再執行。
