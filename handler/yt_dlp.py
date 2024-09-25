# 加载.env文件
from dotenv import load_dotenv
load_dotenv()

from os import getenv
from yt_dlp import YoutubeDL
from uuid import uuid4
from json import dumps
from database import ytb_model, ytb_api

'''
https://www.youtube.com/@daihanoi-htv/videos
https://www.youtube.com/@toancanh24/videos
https://www.youtube.com/@vtv24/videos

'''

# CHANNEL_URL = "https://www.youtube.com/@failarmy/videos"

def get_ytb_blogger_url(blogger_url: str, language:str)->list:
    ''' 格式化视频信息为数据库模型 
    @Paras blogger_url: 博主url;eg:"https://www.youtube.com/@failarmy/videos"
    @Return [Video]
    '''
    # See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
    # See details at https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py
    DEBUG_MODE = getenv("YTB_DEBUG", False) == "True"
    OAUTH2_PATH = getenv("YTB_OAUTH2_PATH") if getenv("YTB_OAUTH2_PATH") else ""
    if OAUTH2_PATH:
        print(f"Yt-dlp+oauth2 > load cache in {OAUTH2_PATH}")
    else:
        print(f"Yt-dlp+oauth2 > use default cache")

    ydl_opts = {
    'flat_playlist': True,
    'print_to_file': {
        'default': ['%(title)s.txt'],
    },
    # 下载配置
    "proxy": (
            getenv("HTTP_PROXY")
            if getenv("HTTP_PROXY") != ""
            else None
        ),
    # 账号鉴权
        "username": "oauth2",
        "password": "",
        "cachedir": OAUTH2_PATH, # Location of the cache files in the filesystem. False to disable filesystem cache.
        "verbose": True, # Print additional info to stdout.
        "quiet": False,
}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(blogger_url, download=False)

        watch_urls = []
    
        if 'entries' in info:
            for entry in info['entries']:
                if 'webpage_url' in entry:
                    # 创建一个字典来包含视频信息
                    # print(entry.get('webpage_url'))
                    playlist_info = {
                        'id': entry.get('id'),  # 视频 ID
                        'link': entry['webpage_url'],  # 视频链接
                        'duration': entry.get('duration'),  # 视频时长
                    }
                    # print(playlist_info)
                    
                    # 将字典传递给 format_search_into_video
                    db_video = format_search_into_video(playlist=playlist_info, language=language)
                    watch_urls.append(db_video)
    return watch_urls        

def format_search_into_video(playlist: dict, language: str) -> ytb_model.Video:
    ''' 格式化视频信息为数据库模型 '''
    if not (playlist.get('id') and playlist.get('link')):
        return None
    id = int(0)
    vid = "ytb_bby_" + str(playlist.get('id', uuid4()))
    cloud_type = int(0)
    cloud_path = str('')
    position = int(3)  # 3:qw
    source_type = int(7)  # :youtube
    source_link = str(playlist.get('link'))
    duration = int(playlist.get('duration', 0))
    info = ""
    return ytb_model.Video(
        id=id,
        vid=vid,
        position=position,
        source_type=source_type,
        cloud_type=cloud_type,
        cloud_path=cloud_path,
        source_link=source_link,
        language=language,
        duration=duration,
        info=info
    )

# 调用函数
# get_ytb_blogger_url(CHANNEL_URL, ydl_opts)
