"""
"""
import os
from tqdm import tqdm
from dotenv import find_dotenv, load_dotenv
_ = load_dotenv(find_dotenv())

from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.evaluation import SemanticSimilarityEvaluator

from utils import get_base_name
from utils import mkdir, json_load, json_dump

MODEL_NAME = 'text-embedding-3-small'  # "text-embedding-ada-002"
model_base_name = '-'.join(MODEL_NAME.split('-')[-2:])
SOURCE_DIR = os.path.join('data', 'source', 'evaluation_dataset')
DEST_DIR = os.path.join('data', 'deliverables', f'{model_base_name}_semantic_similarity')
mkdir(DEST_DIR)

def get_evaluator():
    from dotenv import find_dotenv, load_dotenv
    _ = load_dotenv(find_dotenv())
    embed_model = OpenAIEmbedding(model=MODEL_NAME)
    evaluator = SemanticSimilarityEvaluator(
        embed_model=embed_model,
        similarity_threshold=0.8,
    )
    return evaluator

if __name__ == "__main__":
    evaluator = get_evaluator()
    dataset_file_names = os.listdir(SOURCE_DIR)
    for dataset_file_name in dataset_file_names:
        print(f"process: {dataset_file_name}")
        dataset_file_path = os.path.join(SOURCE_DIR, dataset_file_name)
        dataset = json_load(dataset_file_path)
        base_name = get_base_name(dataset_file_name)
        rvs = {}
        for data in tqdm(dataset):
            # get data info
            qid = data['reference_answer']['qid']
            reference_answer = data['reference_answer']['stem']
            reference_context = data['reference_context'][0]
            try:
                response = data['response']['stem']
            except:
                response = ' '
            
            # calling evaluator
            gd_result = evaluator.evaluate(
                response=response,
                reference=reference_answer,
            )

            score = gd_result.score
            
            rvs[qid] = {
                'reference_answer': reference_answer,
                'reference_context': reference_context,
                'response': response,
                'semantic_score': score
            }

#            if qid == '3':
#                break
        save_file_path = os.path.join(DEST_DIR, base_name + '_semantic_result.json')
        json_dump(save_file_path, rvs)


            

            



