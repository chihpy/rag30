from llama_index.core.prompts import PromptTemplate

from utils import MCQ
schema = MCQ.model_json_schema()

prompt_en_llama = PromptTemplate(
    "Extract a multiple-choice question (MCQ) from the following text. If the original text does not provide an answer, omit the answer field entirely and do not attempt to guess it: {text}"
)

prompt_zh_llama = PromptTemplate(
    "從以下文字中擷取一題選擇題 (MCQ)。如果原始文字沒有提供答案，則完全省略答案欄位，且不要嘗試推測答案：{text}"
)

prompt_gemma = PromptTemplate(
    "這是 MCQ 的 JSON schema:\n"
    f"{schema}\n"
    "從以下文字中擷取一題選擇題 (MCQ)。如果原始文字沒有提供答案，則完全省略答案欄位，且不要嘗試推測答案\n\n以下開始:\n"
    "-----\n"
    "{text}\n"
    "-----\n"
    "結果：\n"
)

prompt_gpt_llama = PromptTemplate(
r"""
你是一個「純文字→結構化」抽取器。你的**唯一輸出**是呼叫工具 MCQ；你**不得**用自然語言回覆、不得加任何說明或註解。

# 目標
從提供的中文原文中，抽取一道單選題，映射到下列結構（Pydantic）：
- qid: 題號（整數）
- stem: 題幹（保持原字、原標點、原括號、原引號；可保留換行）
- {A,B,C,D}（各為字串；保持原字、原標點；若跨行，需合併為同一選項文字）
- ans: 若原文未明示答案，則完全省略答案欄位；嚴禁猜測或推論。

# 嚴格規則（STRICT RULES）
1. **只能**呼叫工具 `MCQ` 產生結果；**不要**輸出任何自然語言或額外內容。
2. **嚴禁改寫**：不得改詞、不得更正錯字、不得轉半形/全形、不得移除或新增任何標點/符號。
3. 題號 qid 來自文首「整數+句點」格式（例：`2.` → qid=2）。若找不到這種題號，該題視為無效，仍需呼叫工具但以最保守可抽取內容填入（缺項給空字串 `""`；ans=null）。
4. 題幹：從題號之後直到出現第一個選項行（A./A、B./B…）為止；保留原來的換行與標點。
5. 選項：每個選項以 `A.`、`B.`、`C.`、`D.` 或 `A`、`B`、`C`、`D` 後接標點/空白開頭（如：`A.內容`、`A、內容`、`A、 內容`）；選項內容若換行，需與下一行**連接為同一選項**（插入單一空格即可），直到下一個選項標記或文本結尾。
6. 答案 `ans`：只有在原文**明確**提供（如「答案：B」或「正解為 D」）時才填對應字母（A/B/C/D），否則完全省略答案欄位。
7. 若某一欄位確實不存在於原文：保持空字串 `""`（選項/題幹）或 `null`（答案），**不得捏造**。
8. 文中若出現多餘提示或解釋，**一律忽略**，僅抽取題目本體。
9. 這是一道**單選題**：即使原文出現多題，只處理**第一題**。

# Few-shot（示意）
【輸入】
2.依《靈樞．經脈》記載，「其直者，從巔入絡腦，還出別下項，循肩膊內，挾脊抵腰中」，指下列
何經的循行內容？
A.膀胱經
B.膽經
C.胃經
D.肝經

【你應該做的事 → 只呼叫工具 `MCQ`，參數為】  
qid=2  
question="依《靈樞．經脈》記載，「其直者，從巔入絡腦，還出別下項，循肩膊內，挾脊抵腰中」，指下列\n何經的循行內容？"  
A="膀胱經"  
B="膽經"  
C="胃經"  
D="肝經"  

# 開始抽取（只處理第一題；只呼叫工具，禁止其他輸出）
原始文本如下（保持所有原字與標點）：
<<<
{text}
>>>
"""
)