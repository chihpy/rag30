"""
- 試用 pdfplumber 的 extract_tables()
- 假設有一個 table，extract_tables 出來之後大致會是 [[row1], [row2]]
- 把特殊大寫轉掉
"""
import re
import os
import pdfplumber
import unicodedata

from utils import json_dump

def to_halfwidth(s):
    return unicodedata.normalize("NFKC", s)

def extract_qid_from_qname(item):
    match = re.match(r"(\d+)", item)
    return int(match.group(1)) if match else None

def extract_dict_from_tables(tables):
    rv = {}
    for table in tables:
        question_index_lst, answer_index_lst = table
        for qname, answer_name in zip(question_index_lst, answer_index_lst):
            qid = extract_qid_from_qname(qname)
            if qid is not None:
                answer = to_halfwidth(answer_name.strip())
                rv[qid] = answer
    return rv

if __name__ == "__main__":
    file_path = os.path.join('data', 'source', '114_針灸科學_ans.pdf')
    save_file_path = os.path.join('data', 'temp', '114_針灸科學_ans.json')
    with pdfplumber.open(file_path) as pdf:
        num_pages = len(pdf.pages)  # pdf.pages is a list
        print(f'num_pages: {num_pages}')
        tables = []
        for page in pdf.pages:
            extracted_tables = page.extract_tables()
            print(f"type of extracted_tables: {type(extracted_tables)}, len: {len(extracted_tables)}")
            #for table in extracted_tables:
            #    print(f"dtype: {type(table)}, dlen: {len(table)}")
            #    print(table[0])
            #    print(table[1])
            tables.extend(extracted_tables)
    # process tables
    ans = extract_dict_from_tables(tables)
    assert len(ans) == 80
    json_dump(save_file_path, ans)
