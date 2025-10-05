"""
"""
import os
import json

SOURCE_DIR = os.path.join('data', 'source')
DEST_DIR = os.path.join('data', 'deliverables', 'evaluation_dataset')
os.makedirs(DEST_DIR, exist_ok=True)

dataset_file_path = os.path.join(SOURCE_DIR, 'structured_output_dataset.json')
file_names = [
    '1_llama_en_response.json',
    '2_llama_zh_response.json',
    '3_llama_chat_response.json',
    '4_gemma_response.json',
    '5_json_gemma_response.json',
]

def json_load(file_path):
    with open(file_path, 'r') as f:
        data_dict = json.load(f)
    return data_dict

def json_dump(file_path, data):
    with open(file_path, 'w') as f:
        print("write result to: " + file_path)
        json.dump(data, f, indent=1, ensure_ascii=False)

def get_base_name(file_name):
    elements = file_name.split('_')
    if elements[0] == '4':
        return '_'.join(elements[:2])
    else:
        return '_'.join(elements[:3])


if __name__ == "__main__":
    # print(os.listdir(SOURCE_DIR))
    dataset = json_load(dataset_file_path)
    for file_name in file_names:
        base_name = get_base_name(file_name)
        print(base_name)
        file_path = os.path.join(SOURCE_DIR, file_name)
        result = json_load(file_path)

        evaluation_data = []
        for example in dataset['examples']:
            reference_answer = example['reference_answer']
            reference_context = example['reference_context']
            qid = reference_answer['qid']
            # get result
            try:
                response = result[qid]['response']
                if isinstance(response, str):
                    response = json.loads(response)
            except:
                print(f"qid: {qid} has response no found in {base_name}")
                response = ''
            rv = {
                'reference_answer': reference_answer,
                'reference_context': reference_context,
                'response': response
            }
            evaluation_data.append(rv)
        save_file_path = os.path.join(DEST_DIR, f"{base_name}_evaluation_dataset.json")
        json_dump(save_file_path, evaluation_data)
