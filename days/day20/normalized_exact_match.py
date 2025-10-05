"""
"""
import os
import re
import json
import unicodedata
from typing import List, Tuple

SOURCE_DIR = os.path.join('data', 'deliverables', 'evaluation_dataset')
DEST_DIR = os.path.join('data', 'deliverables', 'evaluation_result')
os.makedirs(DEST_DIR, exist_ok=True)

def json_load(file_path):
    with open(file_path, 'r') as f:
        data_dict = json.load(f)
    return data_dict

def json_dump(file_path, data):
    with open(file_path, 'w') as f:
        print("write result to: " + file_path)
        json.dump(data, f, indent=1, ensure_ascii=False)

def _remove_punctuation(text: str) -> str:
    # 移除所有 Unicode 標點 (類別以 'P' 開頭)
    return "".join(ch for ch in text if not unicodedata.category(ch).startswith('P'))

def _remove_all_whitespace(text: str) -> str:
    # \s 包含空格、tab、換行、全形空白等各種空白
    return re.sub(r"\s+", "", text)

def normalize_text(
    s: str,
    *,
    use_nfkc: bool = True,
    lowercase: bool = True,
    remove_space: bool = True,
    remove_punct: bool = True
) -> str:
    """
    常見 normalized exact match 的正規化步驟：
    - NFKC：全形→半形、相容字元折疊（建議開）
    - lowercase：小寫化（對中文無影響，但混合文本時建議開）
    - remove_space：移除所有空白（做比對時建議開）
    - remove_punct：移除所有標點（建議開，以避免中英標點差異）
    """
    if s is None:
        return ""
    if use_nfkc:
        s = unicodedata.normalize("NFKC", s)
    if lowercase:
        s = s.lower()
    if remove_punct:
        s = _remove_punctuation(s)
    if remove_space:
        s = _remove_all_whitespace(s)
    return s

def evaluate(data, return_all=True):
    all_case = []
    num_succ = 0
    num_fail = 0
    total = len(data)
    fail_case = []
    for example in data:
        qid = example['reference_answer']['qid']
        label_stem = example['reference_answer']['stem']
        try:
            pred_stem = example['response']['stem']
        except:
            pred_stem = ''
        nlabel_stem = normalize_text(label_stem)
        npred_stem = normalize_text(pred_stem)
        if nlabel_stem == npred_stem:
            num_succ+=1
            ispass = True
        else:
            num_fail+=1
            ispass = False
            if not return_all:
                fail_case.append(
                    {
                        'qid': qid,
                        'ispass': ispass,
                        'label': label_stem,
                        'pred': pred_stem,
                        'nlabel': nlabel_stem,
                        'npred': npred_stem,
                    }
                )
        if return_all:
            all_case.append(
                    {
                        'qid': qid,
                        'ispass': ispass,
                        'label': label_stem,
                        'pred': pred_stem,
                        'nlabel': nlabel_stem,
                        'npred': npred_stem,
                    }
            )
    print(f"succ_rate: {num_succ/total:.2f}")
    if return_all:
        return all_case
    else:
        return fail_case


if __name__ == "__main__":
    file_names = os.listdir(SOURCE_DIR)
    for file_name in file_names:
        print(file_name)
        file_path = os.path.join(SOURCE_DIR, file_name)
        data = json_load(file_path)
        cases = evaluate(data)

        save_file_path = os.path.join(DEST_DIR, file_name.replace('dataset', 'result'))
        json_dump(save_file_path, cases)