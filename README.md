# yet, another rag30

## env
```
sudo apt install -y ffmpeg
sudo apt-get install graphviz
conda create -n rag30 python==3.12

pip install ipykernel
python -m ipykernel install --user --name=rag30


pip install youtube-transcript-api
pip install yt-dlp
pip install faster-whisper
pip install -U --no-cache-dir nvidia-cudnn-cu12 ctranslate2
pip install python-dotenv

pip install spacy
pip install wikipedia

pip install llama-index-llms-openai
pip install llama-index
pip install llama-index-readers-wikipedia
```

```
export LD_LIBRARY_PATH="$(
python - <<'PY'
import os, site
libdirs=[]
for base in site.getsitepackages()+[site.getusersitepackages()]:
    for sub in [("nvidia","cudnn","lib"), ("nvidia","cublas","lib")]:
        d=os.path.join(base, *sub)
        if os.path.isdir(d): libdirs.append(d)
print(":".join(libdirs))
PY
):${LD_LIBRARY_PATH}"
```

# Topics
1. (context, question, answer), gen from context

## Topic 1: (context, question, answer), gen from context

### day1: 先想法辦取得 context
- cd to days/day1
- 從 youtube 取得 txt
    - `python get_transcription.py`
        - data/lee.txt
- 從 youtube 取得 mp3 -> 由 whisper 取得 txt
    - `python yt_download.py`
    - `python whisper_audio2txt.py`
        - data/hung.json

### day2: 從 context 生成 question
- cd to days/day2
- 從 context 生成 question
    - `python context2question.py`
        - data/question_from_context/questions.json

### day3: llama-index2langfuse
- cd to days/day3
- 把 LlamaIndex 的 query 內容傳到 langfuse
    - `python llamaindex2langfuse.py`

### day4: span and download data from langfuse
- cd to days/day4
- simple_span_handler
    - `python span.py`
        ```
        RetrieverQueryEngine.query-9f66c84b-abff-4faf-807a-f6b2ab21b8c2 (9.38712)
        └── RetrieverQueryEngine._query-14f77a30-b42f-4b36-b619-2d36c778af3c (9.386738)
            ├── VectorIndexRetriever.retrieve-40ebf86a-2070-4241-9fd1-6f8f68124d8e (1.460433)
            │   └── VectorIndexRetriever._retrieve-b58dc6e1-00ea-4b1b-86c9-e5996bdd5993 (1.459804)
            │       └── OpenAIEmbedding.get_query_embedding-9fdcc302-ace5-4ad5-916a-69d11afb7186 (1.458764)
            │           └── OpenAIEmbedding._get_query_embedding-f441b1e0-9f80-4807-a43c-07568193d6f0 (1.45732)
            └── CompactAndRefine.synthesize-aa3330ca-fee4-47b1-b8cc-a767f00a0560 (7.924199)
                └── CompactAndRefine.get_response-00f880d2-3d57-4aed-b9f5-20c79c0defeb (7.922752)
                    ├── TokenTextSplitter.split_text-e8e06bca-7f35-47a4-852b-b77bc2f02568 (0.000261)
                    └── CompactAndRefine.get_response-750cc97f-63b7-4afc-b0d8-0fbd720b3522 (7.921415)
                        ├── TokenTextSplitter.split_text-864a7fb0-153b-407e-9fe5-0e7388774ad7 (0.000279)
                        └── DefaultRefineProgram.__call__-2d92b46c-995a-4ba0-96de-727fd6a5ce9c (7.920315)
                            └── OpenAI.predict-411c9a29-3c1d-4f0a-9e75-b94310fe8f37 (7.919715)
                                └── OpenAI.chat-2bb40156-2dfa-4f16-99e4-81481c9f670b (7.919129)
        ```
- download data from langfuse
    - `python langfuse2json`
        - days/day4/RetrieverQueryEngine_example.json

# reference:
## github
- [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)