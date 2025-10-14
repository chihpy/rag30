"""
1. ATOM_EXTRACT_PROMPT
2. EVALUATE_SUBQUERY_TEMPLATE
3. QUERY_REFINE_PROMPT
"""
from llama_index.core.prompts import PromptTemplate
ATOM_EXTRACT_PROMPT = PromptTemplate(
    template="""
任務說明：
你是個精準的「事實拆解器（Atomic Fact Extractor）」。  
輸入：一題單選題（原始題目文字 + 選項）。  
輸出：一個 JSON 物件，且**僅**輸出該 JSON（***不要***有任何多餘的文字、說明或 markdown）。
  JSON 必須包含一個 key: "atomic_facts"，其值為一個陣列（list）。
  每個陣列項目代表一個需要被檢核的「原子事實（atomic fact）」，每個原子事實都應該是**可被直接查證的問句**（能被當成檢索 query 使用）

輸出規則與限制：
1. 僅輸出完整 JSON，編碼使用 UTF-8。絕對不可有任何額外文字或解釋。  
2. `atomic_facts` 的數量上限為 5，至少 1。盡量把題目拆到既能覆蓋判斷所需事實，又避免過度拆分。  
3. 每個 `atomic_fact` 必須能直接當作 search query，長度建議不超過 25 個中文字。    
4. 保持 JSON 結構嚴格、格式正確（可被程式 parse）。

請基於上面任務說明與 schema，對輸入題目進行拆解並輸出 JSON。現在開始處理。請只回傳 JSON。

{exam_query}:
"""
)

EVALUATE_SUBQUERY_TEMPLATE = PromptTemplate(
    "你是一個 citation-based QA 助手。"
    "請僅根據所提供的來源回答問題，並以 JSON 格式輸出結果。"
    "你的回覆格式必須完全符合以下 JSON schema：\n"
    "{\n"
    '  "judgment": <true | false>,\n'
    '  "feedback": "<如果能回答，請以 citation 格式回答；如果不能回答，請說明檢索到的來源，並提供一個簡單的下一步檢索建議>"\n'
    "}\n"
    "說明：\n"
    "- 當 context 能回答 query 時，judgment 設為 true，"
    "並在 feedback 中提供帶有來源編號標註的回答（例如：『外丘穴的WHO國際編號是GB36 [0]。』）。\n"
    "- 當 context 無法回答 query 時，judgment 設為 false，"
    "並在 feedback 中說明檢索到的來源內容，以及提供一個簡單的下一步檢索建議（例如：『建議檢索關鍵詞「刺灸心法要訣 禁針穴」』）。\n"
    "- 僅在明確引用該來源時才標註來源編號。\n"
    "- 請勿輸出任何額外文字、標點或解釋，僅輸出純 JSON。\n"
    "以下為示例：\n"
    "Source [0]:\n"
    "國際代碼: GB\n\nGB36 外丘穴\n\n…\n"
    "問題：外丘穴的WHO國際編號是什麼？\n"
    "輸出：\n"
    "{\n"
    '  "judgment": true,\n'
    '  "feedback": "外丘穴的WHO國際編號是GB36 [0]。"\n'
    "}\n"
    "------\n"
    "{context_str}\n"
    "------\n"
    "問題：{query_str}\n"
    "請輸出："
)

QUERY_REFINE_PROMPT = PromptTemplate(
    template="""
你是一個專門生成檢索 query 的 AI 助手。你的任務是：  
根據原始問題（query）和 LLM 對檢索結果的 feedback，產生下一輪更精準的檢索 query，用於資料檢索。  

要求：
1. 輸出 JSON，格式如下：
{
  "refined_query": "query"
}
2. 每個 query 最多 5 個關鍵詞，簡明且可直接檢索。
3. 如果 feedback 已經包含明確可用的關鍵詞，請提取並重組成 query。
4. 如果 feedback 沒有明確關鍵詞，請基於 query 和 feedback 的意圖生成改進的 query。
5. 避免輸出非必要文字或說明，JSON 直接可解析。

範例輸入：
query: "俞府是否為《刺灸心法要訣》禁針穴？"
feedback: "提供的來源主要介紹四關穴（合谷、太衝）的定位、功效與操作，未見提及俞府穴，亦未涉及《刺灸心法要訣》的禁針穴內容，故無法判定。建議檢索關鍵詞「俞府 刺灸心法要訣 禁針穴」或直接查閱《刺灸心法要訣》原文之禁針穴條目。"

範例輸出：
{
  "refined_query": "俞府 刺灸心法要訣 禁針穴"
}

現在輸入：
query: "{query}"
feedback: "{feedback}"

請只輸出 JSON，產生下一輪檢索 query。

"""
)

ANSWER_PROMPT = PromptTemplate(
    template="""
你是一個中醫考題專家，請根據下面的題目回答單選題。

請遵守以下規則：
1. 使用所提供的參考資料作答。
2. 輸出 JSON 格式。
3. JSON 需包含兩個 key：
   - "feedback" ：根據所提供的 context 分析各選項
   - "ans" ： 選擇最貼近題意的答案 (A/B/C/D)
4. 不要加入題目之外的說明或其他文字。

# {query}

參考資料 (context)：
# {context}

請直接輸出 JSON：
"""
)