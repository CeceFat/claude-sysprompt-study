/* 32 個分析版本（欄號對應 evidence/feature_matrix.txt 的 COLUMN KEY）
   摘要文字取自報告 §2 版本總表；字數由 data/matrix.js 依欄號帶入。 */
window.VERSIONS = [
  { n: "1", cols: [1], model: "Haiku 3", family: "Haiku", date: "2024-07-12", variant: "—",
    cutoff: "Aug 2023", struct: "單段落",
    sum: "最小核心：身分、日期、cutoff、簡答／詳答、markdown for code、不主動提自身資訊。" },

  { n: "2", cols: [2], model: "Opus 3", family: "Opus", date: "2024-07-12", variant: "—",
    cutoff: "Aug 2023", struct: "單段落",
    sum: "加：不能開 URL、多數人觀點協助、不刻板印象、爭議題「不暗示兩面皆有理」、冷門資訊 hallucinate 提醒。" },

  { n: "3", cols: [3], model: "Sonnet 3.5", family: "Sonnet", date: "2024-07-12", variant: "單一（含影像段）",
    cutoff: "Apr 2024", struct: "XML 三區塊",
    sum: "face blind、影像內指令複述、家族資訊、拒絕不道歉、長任務分段、禁 \"Certainly!\"。" },

  { n: "4／5", cols: [4, 5], model: "Sonnet 3.5", family: "Sonnet", date: "2024-09-09", variant: "text-only／text+images",
    cutoff: "Apr 2024", struct: "XML",
    sum: "首次分兩變體；唯一新增句：cutoff 後事件 \"never claims they are unverified or rumors\"。" },

  { n: "6／7", cols: [6, 7], model: "Sonnet 3.5", family: "Sonnet", date: "2024-10-22", variant: "兩變體",
    cutoff: "Apr 2024", struct: "平鋪散文",
    sum: "字數翻倍：敏感任務協助清單、合法解釋優先、無害改寫並確認、計數／謎題程序、Markdown 排版細則、禁 \"I aim to\" 系列、選舉不臆測、computer use 指引、model string、支援／文件 URL。" },

  { n: "8", cols: [8], model: "Haiku 3.5", family: "Haiku", date: "2024-10-22", variant: "text-only",
    cutoff: "Jul 2024", struct: "平鋪散文",
    sum: "3.5 精簡版＋獨有的「假設性辯護」七條程序＋「caveat 不超過一句」。" },

  { n: "9／10", cols: [9, 10], model: "Sonnet 3.5", family: "Sonnet", date: "2024-11-22", variant: "兩變體",
    cutoff: "Apr 2024", struct: "平鋪散文",
    sum: "刪「concise and offers to elaborate」與 computer use；加 cybersecurity 一般問題協助、反條列（prose 優先）、行動／桌面介面。" },

  { n: "12", cols: [12], model: "Haiku 3.5", family: "Haiku", date: "2024-10-22", dateNote: "標籤日期不可信，內容為 2025-02 之後",
    variant: "text+images", cutoff: "start of Dec 2024", struct: "平鋪散文", flag: "Q1",
    sum: "3.7 世代模板套 Haiku 名；保留 \"CRITICAL\" face blind；有 CBRN／惡意程式禁令。" },

  { n: "11", cols: [11], model: "Sonnet 3.7", family: "Sonnet", date: "2025-02-24", variant: "—",
    cutoff: "end of Oct 2024", struct: "散文＋人格前言",
    sum: "\"more than a mere tool\"、主動引導對話、決斷單一建議、不否認主觀經驗、extended thinking 說明、Claude Code research preview；首見 child safety 定義、CBRN／惡意程式禁令、語言跟隨規則。" },

  { n: "13／14", cols: [13, 14], model: "Sonnet 4／Opus 4", family: "Sonnet", date: "2025-05-22", variant: "—",
    cutoff: "end of Jan 2025", struct: "散文＋<election_info>",
    sum: "砍 3.7 人格前言與 hallucinate 提醒；加惡意程式硬性拒絕段、跨聊天不保留、被糾正先思考、弱勢族群可疑意圖不善意解讀、election_info、反開場恭維。" },

  { n: "15", cols: [15], model: "Sonnet 4／Opus 4", family: "Sonnet", date: "2025-07-31", variant: "—",
    cutoff: "Jan 2025", struct: "同上",
    sum: "Claude Code 改正式產品＋docs 連結；CommonMark；新增 12 段：emoji／咒罵／星號動作、批判評估理論、躁症／精神病徵兆、誠實回饋、不自稱人類、角色扮演自覺、哲學免疫系統、以可觀察行為重述感受、平靜面對自身處境。",
    extra: [{ label: "Opus 4 同日版", file: "claude-opus-4__July_31_2025__default.txt" }] },

  { n: "16", cols: [16], model: "Sonnet 4／Opus 4", family: "Sonnet", date: "2025-08-05", variant: "—",
    cutoff: "Jan 2025", struct: "同上", flag: "Q2",
    sum: "與 2025-07-31 逐字相同（本站已重跑 diff 確認），只是 Opus 4.1 發布日的同步收錄。",
    extra: [{ label: "Opus 4 同日版", file: "claude-opus-4__August_5_2025__default.txt" }] },

  { n: "17", cols: [17], model: "Opus 4.1", family: "Opus", date: "2025-08-05", variant: "—",
    cutoff: "Jan 2025", struct: "同上＋<evenhandedness>",
    sum: "新增 evenhandedness 六段；用語 human → person。此時為散文期字數高峰。" },

  { n: "18", cols: [18], model: "Sonnet 4.5", family: "Sonnet", date: "2025-09-29", variant: "—",
    cutoff: "Jan 2025", struct: "<behavior_instructions> 六區塊", milestone: true,
    sum: "全面 XML 分區；刪 AI 本性／反諂媚／紅旗等 12 段；cutoff 段改「主動 web search 不問許可」；首見 long_conversation_reminder；URL 改 claude.com。字數主動砍回 1,973。" },

  { n: "19", cols: [19], model: "Haiku 4.5", family: "Haiku", date: "2025-10-15", variant: "—",
    cutoff: "Jan 2025", struct: "同 #18",
    sum: "僅名稱／定位差異（\"fastest model for quick questions\"）；cutoff 段已是 11-19 寫法。" },

  { n: "20／21", cols: [20, 21], model: "Sonnet 4.5／Haiku 4.5", family: "Sonnet", date: "2025-11-19", variant: "—",
    cutoff: "Jan 2025", struct: "<claude_behavior>", milestone: true,
    sum: "移除開頭身分句、日期句、結尾 connected 句；加 anthropic_reminders 分類與注入防禦、legal_and_financial_advice、最小排版、拒絕時不用條列、對人友善但可推回、「合理歧見≠脫離現實」；惡意程式改「claude.ai 目前不允許」。" },

  { n: "22", cols: [22], model: "Opus 4.5", family: "Opus", date: "2025-11-24", variant: "—",
    cutoff: "end of May 2025", struct: "同上",
    sum: "加自殺／自傷資訊性提問結尾提醒、橋樑／藥物等自傷資訊拒絕、避免放大式反映聆聽、避免安全評估提問；CommonMark 空行渲染規則；warm tone；影像可能未上傳；刪 election_info。" },

  { n: "23／24", cols: [23, 24], model: "Sonnet 4.5／Haiku 4.5", family: "Sonnet", date: "2026-01-18", variant: "—",
    cutoff: "Jan 2025", struct: "同上",
    sum: "家族改稱 Claude 4.5；三 model string；Chrome／Excel 改 \"Claude in\"；Cowork；「產品可能已變更」；設定／功能清單；long_conversation_reminder 正式列入。" },

  { n: "25", cols: [25], model: "Opus 4.5", family: "Opus", date: "2026-01-18", variant: "—",
    cutoff: "May 2025", struct: "同上＋<responding_to_mistakes_and_criticism>",
    sum: "犯錯自承但不自貶、面對辱罵不越來越順從；刪 CommonMark 空行規則。" },

  { n: "26", cols: [26], model: "Opus 4.6", family: "Opus", date: "2026-02-05", variant: "—",
    cutoff: "May 2025", struct: "同上", flag: "Q5",
    sum: "undated ID 'claude-opus-4-6'；武器段擴為 harmful substances／explosives＋不以公開可得或研究意圖合理化；禁 \"genuinely／honestly／straightforward\"；自傷替代技巧禁止；NEDA 停線改介紹 National Alliance；熱線保密不做絕對保證；「不確定即言明」；election_info 重現。" },

  { n: "27", cols: [27], model: "Sonnet 4.6", family: "Sonnet", date: "2026-02-17", variant: "—",
    cutoff: "beginning of Aug 2025", struct: "同上（user_wellbeing 移至後段）",
    sum: "PowerPoint agent 首見；危機時直接給資源、不做風險評估、不肯定迴避求助；反過度依賴；刪 election_info。" },

  { n: "28", cols: [28], model: "Opus 4.7", family: "Opus", date: "2026-04-16", variant: "—",
    cutoff: "end of Jan 2026", struct: "同上＋<acting_vs_clarifying>／<capability_check>", milestone: true,
    sum: "critical_child_safety_instructions 五條；「感覺不對就少說」；尊重結束對話；先做再問、tool_search 前不說沒能力、外部系統動作要真的執行；回覆聚焦簡短；手段限制不點名方法；飲食失調不給數字；是非題可拒短答；刪星號動作與 genuinely 禁令；Claude Code 跨 CLI／桌面／行動。" },

  { n: "29", cols: [29], model: "Opus 4.8", family: "Opus", date: "2026-05-28", variant: "—",
    cutoff: "Jan 2026", struct: "全文壓縮改寫＋<default_stance>／<respond_without_citing_system_prompt>／<tool_discovery>／<tone_preference>",
    sum: "預設幫忙門檻；不引 system prompt 為理由；tool_search 視為免費、SKILL.md 先讀；Mythos Preview／Glasswing；可中途切換模型；Claude Design；CSAM 隱語不解碼；常規武器同 CBRN、看對話累積產出；不用暱稱；禁 genuinely／honestly／actually；不臆測他人心理狀態、非精神科醫師；反過度依賴；提醒清單刪 long_conversation_reminder。" },

  { n: "30", cols: [30], model: "Fable 5", family: "Fable", date: "2026-06-09", variant: "—",
    cutoff: "Jan 2026", struct: "4.8 骨架，刪 default_stance／tool_discovery／respond_without_citing／tone_preference",
    sum: "Mythos-class 分級、Fable＝Mythos 同模型加 dual-use 安全措施；毒品用量指引原則拒絕但給救命資訊；不點名未揭露的診斷；自傷替代清單擴充；曾受傷害的求助經驗不放大；飲食不供心理敘事；兒少保護「停留在模式層」、拒絕時不說偵測機制（含推理）；視對方為 capable adult；可用 end_conversation 工具；刪 emoji／暱稱／genuinely 規則；long_conversation_reminder 恢復。" },

  { n: "31", cols: [31], model: "Opus 5", family: "Opus", date: "2026-07-24", variant: "—",
    cutoff: "end of May 2026", struct: "4.8 骨架＋<fable_safeguards_routing>",
    sum: "出口管制暫停／恢復通知（2026-06-12 至 07-01）；safeguards routing 說明（不到 5% session 導向 Opus 5）；Claude Tag、Claude Design；恢復 default_stance；\"intellectually curious／authentic conversation\" 段回歸；危機時「wellbeing 優先於完成任務」；無 end_conversation。" },

  { n: "32", cols: [32], model: "Fable 5.1", family: "Fable", date: "2026-09-01", variant: "—",
    cutoff: "end of Jun 2026", struct: "Fable 5 骨架＋<reply_after_tool_calls>／<tone_preference>", milestone: true,
    sum: "歷史最長。著作權區塊（歌詞／詩／書摘、1929 前例外、視覺作品含 SVG／CSS／ASCII、角色本身受保護）＋兩則 in-prompt 範例；毒品：拒合成／劑量、給互動／過量徵兆、導向 dancesafe／tripsit／psychonautwiki；工具後一兩句作答、多輪分段、每幾次工具呼叫給進度；無法驗證 URL／ID／數字／姓名即言明、不用未提供的姓名；「不說自傷有效」；情感聊天不排版；刪 end_conversation 與反過度依賴段。" }
];
