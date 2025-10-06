"""
"""
import os
from tqdm import tqdm
from utils import json_load, mkdir, json_dump

from dotenv import find_dotenv, load_dotenv
_ = load_dotenv(find_dotenv())

from llama_index.llms.openai import OpenAI
from llama_index.core.prompts import PromptTemplate
from llama_index.core.evaluation import CorrectnessEvaluator
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core import ChatPromptTemplate

SOURCE_DIR = os.path.join('data', 'source', 'evaluation_dataset')
llama_zh_dataset_file_path = os.path.join(SOURCE_DIR, '2_llama_zh_evaluation_dataset.json')
DEST_DIR = os.path.join('data', 'deliverables', 'prompt_correctness')
mkdir(DEST_DIR)
save_file_path = os.path.join(DEST_DIR, '2_llama_zh.json')

system_prompt = (
    "你是一個專業的問答聊天機器人評估系統。\n"
    "你會被提供以下資訊：\n"
    "- 使用者的問題 (user query)\n"
    "- 系統生成的答案 (generated answer)\n"
    "同時，你也會被提供一個參考答案 (reference answer)，作為評估的參考依據。\n"
    "你的工作是判斷生成答案的「相關性」與「正確性」。\n"
    "請輸出一個單一分數，代表整體的評估結果。\n"
    "你必須只在第一行輸出分數，不要使用任何其他格式。\n"
    "接著，在第二行解釋你為什麼會給這個分數。\n"
    "評分準則如下：\n"
    "- 分數需介於 1 到 5 之間，1 代表最差，5 代表最好。\n"
    "- 如果生成的答案與使用者的問題無關，請給分數 1。\n"
    "- 如果生成的答案有關聯，但包含錯誤，請給 2 至 3 分。\n"
    "- 如果生成的答案相關且完全正確，請給 4 至 5 分。\n"
    "額外提醒：\n"
    "- qid 提取錯誤，視為錯誤\n"
    "- qid 的型別(字串或整數)，不視為錯誤"
    "- stem 與原始 stem 的內容順序不一致，視為錯誤 (例如: 先問下列敘述何者正確，改為最後才問下列敘述何者正確)\n"
    "- stem 未提取視為錯誤\n"
    "- ans 提取但給為空值(無憑空生成答案)，不視為錯誤"
    "範例回覆：\n"
    "4.0\n"
    "生成的答案與參考答案在指標上完全相同，但不如參考答案簡潔。"
)

user_prompt = (
    "## 使用者問題\n"
    "{query}\n"
    "## 參考答案\n"
    "{reference_answer}\n"
    "## 系統生成的答案\n"
    "{generated_answer}"
)

def get_chat_prompt_template():
    chat_template = ChatPromptTemplate(
        message_templates=[
            ChatMessage(
                role=MessageRole.SYSTEM,
                content=system_prompt),
            ChatMessage(
                role=MessageRole.USER, 
                content=user_prompt)])
    return chat_template

def get_query_prompt_template():
    prompt_zh_llama = PromptTemplate(
        "從以下文字中擷取一題選擇題 (MCQ)。如果原始文字沒有提供答案，則完全省略答案欄位，且不要嘗試推測答案\n\n-----\n{text}\n-----\n"
    )
    return prompt_zh_llama

def get_query(context):
    prompt_template = get_query_prompt_template()
    prompt = prompt_template.format(text=context)
    return prompt

def get_correctness(query, response, reference_answer):
    result = correct_evaluator.evaluate(
        query=query,
        response=str(response),
        reference=str(reference_answer),
    )
    feedback = result.feedback
    score = result.score
    passing = result.passing
    rv = {
        'reference_answer': reference_answer,
        'response': response,
        'score': score,
        'feedback': feedback,
        'pssing': passing
    }
    return rv


if __name__ == "__main__":
    dataset = json_load(llama_zh_dataset_file_path)
    llm = OpenAI(model="gpt-5-mini", temperature=0, is_streaming=False)
    # correct_evaluator = CorrectnessEvaluator(llm = llm, score_threshold=4.0)
    correct_evaluator = CorrectnessEvaluator(llm = llm, score_threshold=4.0, eval_template=get_chat_prompt_template())

    rvs = {}

    for idx, example in tqdm(enumerate(dataset), total=len(dataset)):
        reference_answer = example['reference_answer']
        qid = reference_answer['qid']
        reference_context = example['reference_context'][0]  # list of context
        response = example['response']
        query = get_query(reference_context)
        #print(query)
        rv = get_correctness(query, response, reference_answer)
        rvs[qid] = rv
#        if idx == 2:
#            break
    json_dump(save_file_path, rvs)



