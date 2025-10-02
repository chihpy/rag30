"""
"""
import os
import json

def mkdir(dir):
    if os.path.isdir(dir):
        print(f"Directory '{dir}' already exists.")
    else:
        os.makedirs(dir)
        print(f"Directory '{dir}' created successfully.")

def txt_dump(file_path, data):
    print("write result to: " + file_path)
    with open(file_path, 'w') as f:
        f.write(data)

def txt_read(file_path):
    print("read file: " + file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        txt = f.read()
    return txt

def json_load(file_path):
    #print("load data from: " + file_path)
    with open(file_path, 'r') as f:
        data_dict = json.load(f)
    return data_dict

def json_dump(file_path, data):
    """
    Dumps a dictionary to a JSON file.
    
    Parameters:
    - data (dict): The dictionary to be dumped.
    - filename (str): The path to the file where the JSON will be saved.
    """
    try:
        with open(file_path, 'w') as f:
            print("write result to: " + file_path)
            json.dump(data, f, indent=1, ensure_ascii=False)

    except Exception as e:
        print(f"Error occurred: {e}")


from pydantic import Field, BaseModel
from typing import List, Optional
from llama_index.core.program.function_program import get_function_tool

class MCQ(BaseModel):
    """單選題結構，包含題號(qid)、題幹(stem)、以及 A、B、C、D 四個選項"""
    qid: int = Field(..., description='題號')
    stem: str = Field(..., description='題幹')
    A: str = Field(..., description="本題的A選項")
    B: str = Field(..., description="本題的B選項")
    C: str = Field(..., description="本題的C選項")
    D: str = Field(..., description="本題的D選項")
    ans: Optional[str] = Field(default=None, description='答案')

def get_mcq_tool_list():
    mcq_tool = get_function_tool(MCQ)
    return [mcq_tool]

from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama

def get_llm(name='llama', json_mode=False):
    if name == 'llama':
        model_name = "llama3.1:latest"
    elif name == 'gemma':
        model_name = "gemma3:12b"
    elif name == 'mini':
        model_name = "gpt-5-mini"
    else:
        print('unknown model name: {name}')
    if name == 'mini':
        print(f"use openai model: {model_name}")
        llm = OpenAI(model="gpt-5-mini", temperature=0, is_streaming=False, json_mode=json_mode)    
    else:
        print(f"use ollama model: {model_name}")
        llm = Ollama(
            model=model_name,
            temperature=0.0,
            request_timeout=120.0,
            context_window=8000,
            json_mode=json_mode
        )
    return llm