# 加载.env文件
from dotenv import load_dotenv
load_dotenv()

import re
import subprocess

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
                        # blogger_url: str
def get_ytb_blogger_url(blogger_url:tuple, language:str)->list:
    ''' 格式化视频信息为数据库模型 
    @Paras blogger_url: 博主url;eg:"https://www.youtube.com/@failarmy/videos"
    @Return [Video]
    '''
    pattern = r'v=([^&]+)'
    vid = re.search(pattern, blogger_url).group().split('=')[1].split(' ')[0]
    duration = int(blogger_url.split(' ')[1].split('.')[0])
    blogger_url = blogger_url.split(' ')[0]
    # print(blogger_url)
    info_dict = {
    "cloud_save_path": "/QUWAN_DATA/Vietnam/Beibuyin/"
    }
    info = dumps(info_dict)
    db_video = ytb_model.Video(
        id=int(0),
        vid="ytb_bby_" + vid,
        position=int(3),
        source_type=int(7),
        cloud_type=int(0),
        cloud_path="",
        source_link=blogger_url,
        language=language,
        duration=duration,
        info=info
    )
    # print(db_video)
    return db_video

def ytb_dlp_automatic(video_url:tuple,  language:str) -> list:
    # @url:视频链接   
    # @save_path:保存链接的路径   
    # @file_path:读取txt文本链接的路径   
    '''
    判断YouTube的url是否有字幕   
    @video_url:视频链接      
    @language:语言  
    '''
    # 提取信息
    pattern = r'v=([^&]+)'
    vid = re.search(pattern, video_url).group().split('=')[1].split(' ')[0]
    duration = int(video_url.split(' ')[1].split('.')[0])
    blogger_url = video_url.split(' ')[0]

    # 封装info
    info_dict ={}
    info_dict['cloud_save_path'] = ""
    # 判断字幕
    # commend = f'yt-dlp --username "oauth2" --password "" --skip-download --list-subs --verbose {blogger_url}'
    # result = subprocess.run(commend, shell=True, capture_output=True, text=True)
    # # print(result.stdout)
    # if "no automatic captions" in result.stdout:  # 判断result中是否存在字幕文件
    #     print(f"{blogger_url}: no automatic captions")
    #     info_dict['has_srt'] = False
    # else:
    #     print(f"{blogger_url}: have automatic captions")
    #     info_dict['has_srt'] = True
    info = dumps(info_dict)

    db_video = ytb_model.Video(
        id=int(0),
        vid="ytb_" + vid,
        position=int(3),
        source_type=int(3),
        cloud_type=int(0),
        cloud_path="",
        source_link=blogger_url,
        language=language,
        duration=duration,
        info=info
    )
    # print(db_video)
    return db_video