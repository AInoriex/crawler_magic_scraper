from dotenv import load_dotenv
import json
import yt_dlp
import os

load_dotenv()

# num = 0
# list_urls = []

SAVE_DIR = "G:\crawler_magic_scraper\download"  # 你可以设置为想保存的目录
OAUTH2_PATH = "./cache/yt-dlp_1"

# list_url = 'https://www.youtube.com/watch?v=gA0Z1qd0ymQ'
# num = 1

# def download_wav(list_url: str, num: int):
#     ydl_opts = {
#     'write-subs': SAVE_DIR,
#     'skip_download': True,  # 不下载视频
#     'write_auto_sub': True,  # 下载自动生成的字幕
#     'sub-format': 'srt',
#     'convert_subs': 'srt',  # 转换字幕为 SRT 格式
#     'outtmpl': '%(id)s.%(ext)s',  # 输出文件路径和命名格式
#     'username': 'oauth2',  # OAuth2 用户名
#     'password': '',  # OAuth2 密码
#     'cachedir': OAUTH2_PATH,  # 缓存路径
# }

#     # 使用 yt-dlp 下载字幕
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         try:
#             print(f"Downloading from URL: {list_url}")
#             ydl.download(list_url)  # 下载并转换
#             print(f"Download completed for URL: {list_url}")
#         except Exception as e:
#             print(f"Failed to download {list_urls}: {e}")

# # 调用函数并获取更新后的 num
# download_wav(list_url, num)
import yt_dlp

def download_subtitles(video_url: str, output_dir: str = './', lang: str = 'en'):
    ydl_opts = {
        'skip_download': True,  # 不下载视频
        'write_auto_sub': True,  # 下载自动生成的字幕
        'convert_subs': 'srt',  # 转换字幕为 SRT 格式
        'outtmpl': f'{output_dir}/%(id)s.%(ext)s',  # 输出文件路径和命名格式
        'sub-langs': lang,  # 下载指定语言的字幕

        'username': 'oauth2',  # OAuth2 用户名
        'password': '',  # OAuth2 密码
        'cachedir': OAUTH2_PATH,  # 缓存路径
        'verbose': True,
        'quiet': False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            print(f"Downloading subtitles from URL: {video_url}")
            ydl.download([video_url])  # 下载字幕
            print(f"Download completed for URL: {video_url}")
        except Exception as e:
            print(f"Failed to download subtitles for {video_url}: {e}")

# 示例调用
download_subtitles("https://www.youtube.com/watch?v=TImtNKeNk78", output_dir='./subtitles', lang='en')
#yt-dlp --skip-download --write-automatic-subs --convert-subs "srt" https://www.youtube.com/watch?v=TImtNKeNk78