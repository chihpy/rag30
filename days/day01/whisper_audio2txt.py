"""
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
"""
import os
import json
import time
from faster_whisper import WhisperModel
from pathlib import Path

def transcribe_faster_whisper(
    audio_file: str | Path,
    model_name: str = "large-v3",
    device: str = "auto",          # "cuda" | "cpu" | "auto"
    compute_type: str = "auto",     # "float16" | "int8_float16" | "int8" | "auto"
    language: str | None = None,    # "zh"、"en"、None=自動偵測
):
    audio_file = str(audio_file)
    model = WhisperModel(model_name, device=device, compute_type=compute_type)
    segments, info = model.transcribe(
        audio_file,
        language=language,
        vad_filter=True,        # 內建 Voice Activity Detection，通常品質更穩
        beam_size=5,
    )
    # 收集所有 segments
    segs = []
    full_text = []
    for seg in segments:
        segs.append({"start": seg.start, "end": seg.end, "text": seg.text})
        full_text.append(seg.text)
    return {
        "text": " ".join(full_text).strip(),
        "segments": segs,
        "language": info.language,
        "language_probability": info.language_probability,
    }

if __name__ == "__main__":
    audio_path = os.path.join('..', '..', 'data', 'hung.mp3')
    start = time.time()
    result = transcribe_faster_whisper(audio_path, model_name="large-v3")
    print(result["language"], result["language_probability"])
    print(result["text"][:100])
    end = time.time()
    print(f'dur: {end - start} sec')

    output_path = os.path.join('..', '..', 'data', 'hung.json')
    with open(output_path, 'w') as f:
        print("write result to: " + output_path)
        json.dump(result, f, indent=1, ensure_ascii=False)