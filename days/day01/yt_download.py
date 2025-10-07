import os
import yt_dlp

def download_audio(url, output):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output

if __name__ == "__main__":
    urls = ['https://www.youtube.com/watch?v=VuQUF1VVX40',  # lee
            'https://www.youtube.com/watch?v=g4LYbQYDy14',  # hung
    ]
    output_path = os.path.join('..', '..', 'data', 'hung')
    download_audio(urls[1], output_path)