"""
[createdByType](https://github.com/run-llama/llama_index/blob/847acaa6d4471ebb1b1ea6f7e7b94001ef787ef3/llama-index-core/llama_index/core/llama_dataset/base.py#L31)
[BaseLlamaDataset](https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/llama_dataset/base.py#L130)
"""
import os
from llama_index.core.llama_dataset import CreatedBy, CreatedByType, LabelledRagDataExample, LabelledRagDataset
from utils import json_load, mkdir

SOURCE_DIR = os.path.join('data', 'temp')
exam_file_path = os.path.join(SOURCE_DIR, "114_針灸科學_re.json")
ans_file_path = os.path.join(SOURCE_DIR, "114_針灸科學_ans.json")
DEST_DIR = os.path.join('data', 'deliverables')
mkdir(DEST_DIR)
save_file_path = os.path.join(DEST_DIR, 'exam_dataset.json')

def LabelledRagDataset2json(dataset):
    examples = [dataset._example_type.model_dump(el) for el in dataset.examples]
    data = {
        "examples": examples,
    }
    return data

if __name__ == "__main__":
    exams = json_load(exam_file_path)
    ans = json_load(ans_file_path)
    examples = []
    for qset in exams:
        query = f"題目: {qset['stem']}\n選項:\n A: {qset['A']}\n B: {qset['B']}\n C: {qset['C']}\n D: {qset['D']}\n"
        query_by = CreatedBy(type=CreatedByType.AI, model_name='re')
        reference_answer = ans[qset['qid']]
        reference_answer_by = CreatedBy(type=CreatedByType.AI, model_name='re')
        # reference_context (Optional[List[str]])
        rag_example = LabelledRagDataExample(
            query=query,
            query_by=query_by,
#            reference_contexts=reference_contexts,
            reference_answer=reference_answer,
            reference_answer_by=reference_answer_by,
        )
        # rag_example.model_dump_json()
        # rag_example.parse_raw(rag_example.json())
        # rag_example.dict()
        # rag_example.parse_obj(rag_example.dict())
        examples.append(rag_example)
    exam_dataset = LabelledRagDataset(examples=examples)
#    exam_dataset.save_json(save_file_path)
    exam_dataset_json = LabelledRagDataset2json(exam_dataset)
    from utils import json_dump
    json_dump(save_file_path, exam_dataset_json)
    print('reload: data')
    ## reload
    reload_rag_dataset = LabelledRagDataset.from_json(save_file_path)
    reload_df = reload_rag_dataset.to_pandas()
    print(reload_df.tail(3))

    print('---')
    from pprint import pprint
    print(rag_example.model_dump_json())