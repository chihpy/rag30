"""
"""
import os
import re
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi

def _extract_video_id(url: str) -> str:
    p = urlparse(url)
    if p.netloc.endswith("youtu.be"):
        return p.path.lstrip("/").split("/")[0]
    q = parse_qs(p.query)
    if "v" in q:
        return q["v"][0]
    m = re.search(r"/(shorts|embed)/([A-Za-z0-9_-]{6,})", p.path)
    if m:
        return m.group(2)
    raise ValueError("無法從網址解析出 YouTube 影片 ID。")

def has_youtube_captions(url: str, preferred_langs=None) -> bool:
    """
    檢查 YouTube 影片是否有可用字幕（人工或自動）。
    - url: YouTube 影片連結
    - preferred_langs: 語言優先序，若 None 則不過濾，任意語言有字幕就回 True
    回傳: True = 有字幕可抓, False = 沒有字幕
    """
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled
    from youtube_transcript_api import NoTranscriptFound

    video_id = _extract_video_id(url)
    api = YouTubeTranscriptApi()

    try:
        tlist = api.list(video_id)  # TranscriptList，可疊代
    except (TranscriptsDisabled, NoTranscriptFound):
        return False
    except Exception:
        return False

    if preferred_langs:
        try:
            tlist.find_transcript(preferred_langs)
            return True
        except NoTranscriptFound:
            return False
    else:
        return len(list(tlist)) > 0

def fetch_youtube_captions(
    url: str,
    preferred_langs=None,
    translate_to: str | None = None,
    join_with: str = "\n",
    preserve_formatting: bool = False,
) -> str:
    """
    取得 YouTube 字幕純文字
    - url: YouTube 連結
    - preferred_langs: 語言優先序，預設 ['zh-Hant','zh-TW','zh-Hans','zh','en']
    - translate_to: 翻譯成目標語言（如 'zh-Hant','en'），若為 None 則不翻譯
    - join_with: 合併字幕的分隔符號
    - preserve_formatting: 是否保留 HTML 格式標籤
    """
    if preferred_langs is None:
        preferred_langs = ["zh-Hant", "zh-TW", "zh-Hans", "zh", "en"]

    video_id = _extract_video_id(url)
    from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound

    api = YouTubeTranscriptApi()

    if translate_to:
        # 先找到一個字幕，再翻譯
        tlist = api.list(video_id)
        try:
            base_t = tlist.find_transcript(preferred_langs)
        except NoTranscriptFound:
            base_t = next(iter(tlist), None)
        fetched = base_t.translate(translate_to).fetch(preserve_formatting=preserve_formatting)
    else:
        fetched = api.fetch(video_id, languages=preferred_langs, preserve_formatting=preserve_formatting)

    raw = fetched.to_raw_data()
    lines = [d["text"].strip() for d in raw if d.get("text", "").strip()]
    junk = {"[Music]", "[Applause]", "[Laughter]"}
    return join_with.join([ln for ln in lines if ln not in junk])


if __name__ == "__main__":
    urls = ['https://www.youtube.com/watch?v=VuQUF1VVX40',  # lee
            'https://www.youtube.com/watch?v=g4LYbQYDy14',  # hung
    ]
    save_file_path = os.path.join('..', '..', 'data', 'lee.txt')

    for idx, url in enumerate(urls):
        has_captions = has_youtube_captions(url)
        print(f"link{idx+1} has_youtube_captions: {has_captions}")
        if has_captions:
            print("write result to " + save_file_path)
            txt = fetch_youtube_captions(url)
            with open(save_file_path, 'w') as f:
                f.write(txt)