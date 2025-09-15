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

### day1: 先想法辦取得context
- 從youtube取得txt
    - `python get_transcription.py`
- 從youtube取得mp3->由whisper取得txt
    - `python yt_download.py`
    - `python whisper_audio2txt.py`

# reference:
## github
- [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)