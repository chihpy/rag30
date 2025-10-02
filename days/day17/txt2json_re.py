"""this file convert converted txt file to json: our exam question
"""
import re
import os
import unicodedata
from spliter import split_by_number_dot
from utils import txt_read, json_dump

SOURCE_FILE_PATH = os.path.join('data', 'temp', '114_針灸科學.txt')
SAVE_FILE_PATH = os.path.join('data', 'temp', '114_針灸科學_re.json')


OPTION_PUNCT = r"[.\u3002\uFF0E\uFF61,\)\uFF09\uFF0C\u3001]"   # . 。 ． ･ , ) ） ， 、
# 若已做 NFKC，常見會化成 . , )

pattern = re.compile(rf"""
    ^\s*(?P<qid>\d+)\s*                           # 題號
    [\.\)]\s*                                      # 題號後常見標點：. 或 )
    (?P<stem>.*?)                                  # 題幹（非貪婪，吃到 A. 前）
    (?:\n+|\s+)A{OPTION_PUNCT}\s*(?P<A>.*?)        # A 選項
    (?:\n+|\s+)B{OPTION_PUNCT}\s*(?P<B>.*?)        # B 選項
    (?:\n+|\s+)C{OPTION_PUNCT}\s*(?P<C>.*?)        # C 選項
    (?:\n+|\s+)D{OPTION_PUNCT}\s*(?P<D>.*?)        # D 選項
    (?=\n\s*\d+[\.\)]|\Z)                          # 下一題題號或文本結尾作為邊界
""", re.MULTILINE | re.DOTALL | re.VERBOSE)

def normalize(text: str) -> str:
    # 全形→半形、統一換行
    t = unicodedata.normalize("NFKC", text)
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    # 可選：壓縮多個空白
    t = re.sub(r"[ \t]+", " ", t)
    # 把「單一換行」視為空白，保留「連續換行」作為段落分隔
    t = re.sub(r'(?<!\n)\n(?!\n)', ' ', t)
    return t

def parse_questions(raw: str):
    text = normalize(raw)
    results = []
    for m in pattern.finditer(text):
        d = m.groupdict()
        # 去掉尾端多餘空白與換行
        for k, v in d.items():
            d[k] = re.sub(r"\s+$", "", v.strip())
        results.append(d)
    return results


if __name__ == "__main__":
    txt = txt_read(SOURCE_FILE_PATH)
    blocks = split_by_number_dot(txt)
    meta_txt = blocks.pop(0)

    rvs = []
    for block in blocks:
        rv = parse_questions(block)
        rvs.extend(rv)
    json_dump(SAVE_FILE_PATH, rvs)
