# yet, another rag30

## env
```
sudo apt install -y ffmpeg
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
### day1: 先想法辦取得context
- cd to days/day1
- 從youtube取得txt
    - `python get_transcription.py`
        - data/lee.txt
- 從youtube取得mp3->由whisper取得txt
    - `python yt_download.py`
    - `python whisper_audio2txt.py`
        - data/hung.json
### day2: 從 context 生成 question
- cd to day2/day2
- 從context生成question
    - `python context2question.py`
        - data/question_from_context/questions.json
    
# reference:
## github
- [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)