# 加载.env文件
from dotenv import load_dotenv
load_dotenv()
from json import dumps
from database import ytb_model, ytb_init_video 

import re

'''
https://www.youtube.com/@daihanoi-htv/videos
https://www.youtube.com/@toancanh24/videos
https://www.youtube.com/@vtv24/videos

'''

# CHANNEL_URL = "https://www.youtube.com/@failarmy/videos"
                        # blogger_url: str
def get_ytb_blogger_url(video_url:str, duration:int, language:str, task_id:str, source_id:str)->ytb_model.Video:
    ''' 格式化视频信息为数据库模型 
    @Paras video_url: 博主url;eg:"https://www.youtube.com/@failarmy/videos"
    @Return [Video]
    '''
    # 提取信息
    # print(" ==================== [DEBUG] get_ytb_blogger_url ==================== ")
    # print(f"params > blogger_url:{blogger_url} language:{language} task_id:{task_id}")
    pattern = r'v=([^&]+)'
    vid = re.search(pattern, video_url).group().split('=')[1].split(' ')[0]
    # print(f"object info > vid:{vid} duration:{duration} blogger_url:{blogger_url}")
    # print(" ==================== [DEBUG] get_ytb_blogger_url ==================== ")
    # info_dict = {
    # "cloud_save_path": "/QUWAN_DATA/Vietnam/Beibuyin/"
    # "cloud_save_path": "/QUWAN_DATA/大幅度/Youtuber-{file_name}"
    # }
    # 封装info
    info_dict ={}
    info_dict['cloud_save_path'] = ""
    info_dict['task_id'] = task_id
    info = dumps(info_dict)

    db_video = ytb_model.Video(
        id=int(0),
        # vid="ytb_bby_" + vid,
        # vid="dafudu_ytb_" + vid,
        vid="ytb_" + vid,
        position=int(3),
        source_type=int(3),
        cloud_type=int(0),
        cloud_path="",
        source_link=video_url,
        language=language,
        duration=duration,
        info=info,
        source_id=source_id
    )
    # print(db_video)
    return db_video

def ytb_dlp_automatic(video_url:tuple,  language:str) -> list:
    # @url:视频链接   
    # @save_path:保存链接的路径   
    # @file_path:读取txt文本链接的路径   
    '''
    判断YouTube的url是否有字幕 [暂时没有开启该功能]  
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

def ytb_dlp_format_video(channel_url:str, video_urls:list, language:str) -> ytb_model.Video:
    """
    格式化视频信息为Video类型

    :param channel_url: 博主url;eg:"https://www.youtube.com/@failarmy/videos"
    :param video_url: 完整视频链接
    :param language: 语言   
    """
    # 提取信息
    video_url = []  # 存储视频url列表
    video_duration = []  # 存储视频时长列表
    video_source_id = []  # 存储视频ID
    for video_info in video_urls:
        video_url.append(video_info[0])
        video_duration.append(video_info[1])
        video_source_id.append(video_info[2])

    # print(video_url,"#########",video_duration)
    pip_video = ytb_init_video.Video(
        channel_url=channel_url,
        source_link=video_url,
        duration=video_duration,
        language=language,
        souece_id=video_source_id
    )
    return pip_video