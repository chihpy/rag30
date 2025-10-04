"""
"""
import os
import json
import time
from tqdm import tqdm

from dotenv import find_dotenv, load_dotenv
_ = load_dotenv(find_dotenv())

from prompts import prompt_en_llama, prompt_zh_llama, prompt_gemma, prompt_gpt_llama
from utils import mkdir, json_load, json_dump
from utils import get_mcq_tool_list
from utils import get_llm

DEST_DIR = os.path.join('data', 'temp')
mkdir(DEST_DIR)


def run_tool(llm, tool, prompt_template, qid, query):
    message = prompt_template.format_messages(text=query)[0]
    try:
        start = time.time()
        resp = llm.chat_with_tools(
            [tool],
            user_msg=message,
            tool_required=True,  # can optionally force the tool call
        )
        end = time.time()
        tool_calls = llm.get_tool_calls_from_response(
            resp, error_on_no_tool_call=False
        )
        result = tool_calls[0].model_dump()['tool_kwargs']
        _ = resp.raw.pop('message')  # this line in openai models will error
        rv = {
            'qid_source': qid,
            'qset_txt': query,
            'profiling': resp.raw,
            'response': result,
            'py_times': end - start,
        }
        succ = True
    except Exception as e:
        print(f"error qid: {qid}, error type: {type(e).__name__}, error msg: {e}")
        rv = {
            'qid_source': qid,
            'qset_txt': query
        }
        succ = False
    return succ, rv


def run_complete(llm, prompt, qid, query, j_mode):
    txt = prompt.format(text=query)
    try:
        start = time.time()
        resp = llm.complete(txt)
        end = time.time()
        _ = resp.raw.pop('message')
        if j_mode:
            result = json.loads(resp.text)
        else:
            result = resp.text
        rv = {
            'qid_source': qid,
            'qset_txt': query,
            'profiling': resp.raw,
            'response': result,
            'py_times': end - start,
        }
        succ = True
    except Exception as e:
        print(f"error qid: {qid}, error type: {type(e).__name__}, error msg: {e}")
        rv = {
            'qid_source': qid,
            'qset_txt': query
        }
        succ = False
    return succ, rv


if __name__ == "__main__":
    file_path = os.path.join('data/source/structured_output_dataset.json')
    exams = json_load(file_path)['examples']
    print(len(exams))
    tool = get_mcq_tool_list()[0]

    EXP_NAMES = ['1_llama_en', '2_llama_zh', '3_llama_chat', '4_gemma', '5_json_gemma']
    PROMPTS = [prompt_en_llama, prompt_zh_llama, prompt_gpt_llama, prompt_gemma, prompt_gemma]
    LLM_NAMES = ['llama', 'llama', 'llama', 'gemma', 'gemma']
    for exp_name, prompt, llm_name in zip(EXP_NAMES, PROMPTS, LLM_NAMES):
        print(exp_name)
        save_file_path = os.path.join(DEST_DIR, f'{exp_name}.json')
        if exp_name == '5_json_gemma':
            j_mode = True
        else:
            j_mode = False
        llm = get_llm(llm_name, json_mode=j_mode)
        start = time.time()
        error_qid = []
        rvs = []
        for idx, qset in enumerate(tqdm(exams)):
            qid = idx + 1
            query = qset['reference_context'][0]
            if llm_name != 'gemma':
                ret, qset = run_tool(llm, tool, prompt, qid, query)
            else:
                ret, qset = run_complete(llm, prompt, qid, query, j_mode)
            if not ret:
                error_qid.append(idx)
                rvs.append(qset)
            else:
                rvs.append(qset)
#            if idx == 3:
#                break
        end = time.time()
        json_dump(save_file_path, rvs)
        print(f"total dur: {end - start:.2f} sec")