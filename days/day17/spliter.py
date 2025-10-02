"""split large exam txt file to meta and qset
"""
import re
import os
from typing import List

SOURCE_FILE_PATH = os.path.join('data', 'temp', '114_針灸科學.txt')
from utils import txt_read

# 用題號來切 chunck
def split_by_number_dot(text: str) -> List[str]:
    pattern = re.compile(r'(?m)^(\d+)\.\s*')
    matches = list(pattern.finditer(text))
    blocks = []
    # 開頭不是題號的部分
    if matches and matches[0].start() > 0:
        blocks.append((text[:matches[0].start()].strip()))
    # 每一題
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        block = text[start:end].strip()
        blocks.append(block)

    return blocks

if __name__ == "__main__":
    txt = txt_read(SOURCE_FILE_PATH)
    blocks = split_by_number_dot(txt)
    meta_txt = blocks.pop(0)
    print("# meta data part: ")
    print(meta_txt[:100])
    print("# qset data part: ")
    print(f'len of qsets: {len(blocks)}')
    print(f"{blocks[0]}")