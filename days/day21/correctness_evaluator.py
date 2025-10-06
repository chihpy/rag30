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

SOURCE_DIR = os.path.join('data', 'source', 'evaluation_dataset')
llama_zh_dataset_file_path = os.path.join(SOURCE_DIR, '2_llama_zh_evaluation_dataset.json')
DEST_DIR = os.path.join('data', 'deliverables', 'correctness')
mkdir(DEST_DIR)
save_file_path = os.path.join(DEST_DIR, '2_llama_zh.json')

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
    correct_evaluator = CorrectnessEvaluator(llm = llm, score_threshold=4.0)

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



