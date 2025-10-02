"""
"""
import os

from spliter import split_by_number_dot
from utils import txt_read, json_load, json_dump

TXT_FILE_PATH = os.path.join('data', 'temp', '114_針灸科學.txt')
EXAM_FILE_PATH = os.path.join('data', 'temp', '114_針灸科學_re.json')
SAVE_FILE_PATH = os.path.join('data', 'deliverables', 'structured_output_dataset.json')

if __name__ == "__main__":
    txt = txt_read(TXT_FILE_PATH)
    blocks = split_by_number_dot(txt)
    meta_txt = blocks.pop(0)
    print(f'len of blocks: {len(blocks)}')
    qsets = json_load(EXAM_FILE_PATH)
    print(f'len of qsets: {len(qsets)}')
    assert len(blocks) == 80
    assert len(qsets) == len(blocks)
    examples = []
    for block, qset in zip(blocks, qsets):
        query = "Pydantic"
        query_by = "human"
        reference_answer = qset
        reference_answer_by = {"model_name": "re", "type": "ai"}
        reference_context = [block]

        examples.append({
            'query': query,
            'query_by': query_by,
            'reference_answer': qset,
            'reference_answer_by': reference_answer_by,
            'reference_context': reference_context
        })
    so_data = {'examples': examples}
    json_dump(SAVE_FILE_PATH, so_data)
    # reload
    reload_data = json_load(SAVE_FILE_PATH)
    example = reload_data['examples'][0]
    print(example)

    



