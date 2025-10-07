"""
"""
# setup .env
from dotenv import find_dotenv
from dotenv import load_dotenv
print(find_dotenv())
succ = load_dotenv(find_dotenv())
if not succ:
    raise ValueError('load_dotenv FALSE')

# import
import os
from llama_index.llms.openai import OpenAI
from llama_index.core import SimpleDirectoryReader
from llama_index.core.llama_dataset.generator import RagDatasetGenerator
from llama_index.core.prompts.base import PromptTemplate

# setup
SOURCE_DIR = os.path.join('..', '..', 'data')
DEST_DIR= os.path.join('..', '..', 'data', 'question_from_context')
os.makedirs(DEST_DIR, exist_ok=True)
MODEL_NAME = "gpt-5-mini"
num_questions_per_chunk = 1

# prompt
text_question_template = PromptTemplate(
    f"""你是一位專業的課程助教，你的任務是根據上課內容的片段，設計 {num_questions_per_chunk} 個問題來問學生。
問題風格以單一且直接的問句為主，並且需要在上課內容中找得到答案。
若是要求出複數題，則問題應該盡可能涵蓋不同的面向。

範例輸入:
以下是上課內容片段：
---------------------
"業設計成這樣呢\n為什麼作業要跑三個小時呢\n我只允許這個作業三分鐘\n就應該要>跑完\n我們有當然可以把這些特別花時間\n需要特別花時間訓練的作業拿掉\n但是我還是選>擇在這門課裡面\n保留那一些\n需要一定訓練時間的作業\n因為焦躁的等待人工智慧訓練的結果\n迷茫的調參數\n不知道會不會成功\n這個就是人工智慧的醍醐味\n所以大家需要學習\n在迷茫中前進\n這個就是模型的訓練\n我們特別把這一部分保留在課程裡面\n讓你體驗說\n模型訓練不出來的焦躁\n到底是什麼樣的感覺\n而且我必須要強調啊\n什麼三四個小時的等待訓練時間\n真的不算什麼\n我們過去有很多作業訓練時間都是\n至少三天起跳\n你要至少訓練三天\n你才能夠拿到成績\n那我知道說很多同學在做作業的時候\n往往你都在實現\n最後一天才開始做作業\n但那一種啊\n需要訓練三天以上的模型\n你只在前一天才開始做作業\n你是絕不可能完成的\n這個時候我告訴你\n你唯一可以做的事情\n就是放棄這樣子\n還好我們這堂課裡面呢\n現在是沒有需要訓練一天以上的作業啦\n我們把那種\n特別需要花時間訓練的作業\n還是拿掉了\n只保留了需要訓練三四個小時的作業\n但我只想要強調說\n三四個小時的訓練時間\n真的不算什麼\n如果你要真正用大量的資料\n大規模的訓練模型\n訓練個數週\n其實都是常見的事情\n而這一些\n需要一點訓練時間的作業\n它的定位就像是預防針\n幫助你在未來面對更大的挑戰\n幫助你在未來面對挑戰的時候\n做好心理準備\n另外呢\n鼓勵大家如果有空的話\n可以先看一些線上的錄影進行預習\n那假設你對於生成式AI一無所知的話\n那你可以先看生成式AI導論2024的課程\n那如果2024的課程看完\n你想要進一步了解\n這些AI是怎麼被訓練出來的"
---------------------
範例輸出:
什麼是深度學習的醍醐味？

輸入:
以下是上課內容片段：
---------------------
{{context_str}}
---------------------{{query_str}}
"""
)

question_gen_query = '輸出:\n'

if __name__ == "__main__":
    # llm initial
    llm = OpenAI(model=MODEL_NAME, temperature=0.0)
    # get documents from data/lee.txt
    reader = SimpleDirectoryReader(SOURCE_DIR, required_exts=['.txt'])
    documents = reader.load_data()

    dataset_generator = RagDatasetGenerator.from_documents(
        documents,
        llm=llm,
        num_questions_per_chunk = num_questions_per_chunk,  # set the number of questions per nodes
        text_question_template = text_question_template,
        question_gen_query = question_gen_query,
        show_progress=True,
    )
    # qgen
    questions = dataset_generator.generate_questions_from_nodes()
    # dump
    df = questions.to_pandas()
    df.to_json(
        os.path.join(DEST_DIR, "questions.json"),
        orient="records",
        force_ascii=False,
        indent=2
    )