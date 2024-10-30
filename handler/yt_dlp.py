# 加载.env文件
from dotenv import load_dotenv
load_dotenv()

from json import dumps
from database import ytb_model, ytb_init_video 
import re

def get_ytb_channel_url(video_url:str, duration:float, language:str, task_id:str)->ytb_model.Video:
    ''' 格式化视频信息为数据库入库对象
    :param video_url: 博主url; eg: https://www.youtube.com/@failarmy/videos
    :param duration: 时长
    :param language: 语言
    :param task_id: 任务id
    :return: ytb_model.Video
    '''
    # 提取信息
    # print(" ==================== [DEBUG] get_ytb_channel_url ==================== ")
    # print(f"params > channel_url:{channel_url} language:{language} task_id:{task_id}")
    pattern = r'v=([^&]+)'
    vid = re.search(pattern, video_url).group().split('=')[1].split(' ')[0]
    # print(f"object info > vid:{vid} duration:{duration} channel_url:{channel_url}")
    # print(" ==================== [DEBUG] get_ytb_channel_url ==================== ")
    # info_dict = {
    # "cloud_save_path": "/QUWAN_DATA/Vietnam/Beibuyin/"
    # }
    # 封装info
    info_dict ={}
    info_dict['cloud_save_path'] = ""
    info_dict['task_id'] = task_id
    info = dumps(info_dict)

    db_video = ytb_model.Video(
        id=int(0),
        vid="ytb_" + vid,
        position=int(3),
        source_type=int(3),
        cloud_type=int(0),
        cloud_path=str(""),
        source_link=str(video_url),
        language=str(language),
        duration=int(duration),
        info=info
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
    channel_url = video_url.split(' ')[0]

    # 封装info
    info_dict ={}
    info_dict['cloud_save_path'] = ""
    # 判断字幕
    # commend = f'yt-dlp --username "oauth2" --password "" --skip-download --list-subs --verbose {channel_url}'
    # result = subprocess.run(commend, shell=True, capture_output=True, text=True)
    # # print(result.stdout)
    # if "no automatic captions" in result.stdout:  # 判断result中是否存在字幕文件
    #     print(f"{channel_url}: no automatic captions")
    #     info_dict['has_srt'] = False
    # else:
    #     print(f"{channel_url}: have automatic captions")
    #     info_dict['has_srt'] = True
    info = dumps(info_dict)

    db_video = ytb_model.Video(
        id=int(0),
        vid="ytb_" + vid,
        position=int(3),
        source_type=int(3),
        cloud_type=int(0),
        cloud_path="",
        source_link=channel_url,
        language=language,
        duration=duration,
        info=info
    )
    # print(db_video)
    return db_video

def ytb_dlp_format_video(channel_url:str, video_data:list, language:str) -> ytb_init_video.Video:
    """
    格式化视频信息为Video类型

    :param channel_url: 博主url;eg:"https://www.youtube.com/@failarmy/videos"
    :param video_data: 完整视频解析数据list(tuple)
    :param language: 语言   
    :return: ytb_init_video.Video
    """
    # 提取信息
    video_url = []  # 存储视频url列表
    video_duration = []  # 存储视频时长列表
    for v in video_data:
        video_url.append(v[0])
        video_duration.append(v[1])

    pip_video = ytb_init_video.Video(
        channel_url=channel_url,
        video_url=video_url,
        duration=video_duration,
        language=language,
    )
    return pip_video