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