import os
import json
import pandas as pd
import asyncio
from tqdm import tqdm

from utils import json_load, json_dump, mkdir

from baseline_rag_workflow import RAGWorkflow

from dotenv import find_dotenv, load_dotenv
_ = load_dotenv(find_dotenv())

SOURCE_DIR = os.path.join('data', 'source', 'rag_dataset')
DEST_DIR = os.path.join('data', 'deliverables')
mkdir(DEST_DIR)
INDEX_DIR = 'storage'

async def main():
    save_file_path = os.path.join(DEST_DIR, 'baseline_rag_result_R3.json')
    dataset_file_path = os.path.join(SOURCE_DIR, 'lee_course0_rag_dataset.csv')
    df = pd.read_csv(dataset_file_path)

    w = RAGWorkflow()
    index = await w.run(index_dir=INDEX_DIR)
    
    inference_result = []
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        query = row.query
        result = await w.run(query=query, index=index)
        print(result['response'])
        inference_result.append(result)
    json_dump(save_file_path, inference_result)

if __name__ == "__main__":
    asyncio.run(main())