import pytz
from os import path, makedirs, walk, getenv
from datetime import datetime
from uuid import uuid4
from json import dumps
from traceback import format_exception # Python 3.10+
from urllib.parse import urljoin, urlparse, unquote
from time import sleep
from database import ytb_model, ytb_api
from utils.utime import random_sleep, parse_time_string_with_colon
from youtubesearchpython import Playlist, playlist_from_channel_id
from youtubesearchpython import ChannelsSearch

MAX_RETRY = int(getenv("YTB_MAX_RETRY"))

# 预创建下载目录
# |—— audio
# |—— info
def make_path(save_path):
    save_audio_path = path.join(save_path, "audio")
    save_info_path = path.join(save_path, "info")
    makedirs(save_audio_path, exist_ok=True)
    makedirs(save_info_path, exist_ok=True)
    return save_audio_path, save_info_path


def try_to_get_file_name(save_dir:str, vid:str, default_name='')->str:
    ''' 尝试获取下载文件名 '''
    ret_name = ""
    # files = []
    for dirpath, dirnames, filenames in walk(save_dir):
        for filename in filenames:
            # files.append(path.join(dirpath, filename))
            if vid in filename:
                ret_name = (path.join(dirpath, filename))
                break
    if ret_name == "":
        ret_name = default_name
    return ret_name


def is_touch_fish_time()->bool:
    ''' 判断是否能摸鱼，以Youtube总部地区为限制 '''
    ytb_timezone = "America/Los_Angeles"

    # 获取当前时间
    now_utc = datetime.now(pytz.utc)
    
    # 转换为美国加利福尼亚州时区时间
    pacific_tz = pytz.timezone(ytb_timezone)
    now_pacific = now_utc.astimezone(pacific_tz)
    
    # 获取当前的小时
    current_hour = now_pacific.hour
    current_mint = now_pacific.minute
    
    # 判断是否在办公时间内(早上9点到下午5点)
    if 9 <= current_hour < 17+1:
        print(f"[×] 非摸鱼时间 > 当地时区 {ytb_timezone} | 当地时间 {current_hour}:{current_mint}")
        return False
    else:
        print(f"[√] 摸鱼时间 > 当地时区 {ytb_timezone} | 当地时间 {current_hour}:{current_mint}")
        return True


def save_channel_all_videos(channel_id:str, language:str, __retry:int=3)->tuple[int, int]:
    ''' 获取并保存频道下所有视频
    @channel_id:str 频道id
    @lanuage:str    频道视频语言
    '''
    # channel_id = "UC6Q8f2fK10PLMo4kkiBSCpXA" # Đậu Phộng TV
    is_first = True
    page_count = int(0) #总视频数
    total_videos_count = int(0) #总页数
    ret = (total_videos_count, page_count)
    try:
        # playlist = Playlist(playlist_from_channel_id(channel_id))
        # print(f'Videos Retrieved: {len(playlist.videos)}')
        # if len(playlist.videos) > 0:
        #     for pl in playlist.videos:
        #         dbVideo = format_search_into_video(playlist=pl, language=language)
        #         ytb_api.create_video(dbVideo)
        while 1:
            page_count += 1
            if is_first:
                playlist = Playlist(playlist_from_channel_id(channel_id), timeout=5)
                is_first = False
            else:
                playlist.getNextVideos()
            cur_len_video = len(playlist.videos)
            actual_len = cur_len_video - total_videos_count
            print(f'get_playlist_by_channelid > Playlist retrieved new {actual_len} videos')
            if cur_len_video > 0:
                for pv in playlist.videos[total_videos_count:-1]:
                    print(pv)
                    db_video = format_search_into_video(playlist=pv, language=language)
                    if db_video != None:
                        ytb_api.create_video(db_video)
                        sleep(1)
                    else:
                        print(f"get_playlist_by_channelid > format_search_into_video failed. video:{pv}")
                else:
                    print(f"get_playlist_by_channelid > Create page:{page_count} of videos done, len_playlist_videos:{cur_len_video}")
                    total_videos_count = cur_len_video
            if not playlist.hasMoreVideos:
                print(f"get_playlist_by_channelid > Get no more pages playlist videos, now page_count:{page_count}.")
                break
            if is_touch_fish_time():
                random_sleep(rand_st=5, rand_range=10) #请求失败等待5-15s
            else:
                random_sleep(rand_st=20, rand_range=20) #请求失败等待20-40s(非摸鱼时间)

    except Exception as e:
        err_str = "".join(format_exception(e)).strip()
        print(f"get_playlist_by_channelid > ERROR | {err_str}")
        # if __retry > 0:
        #     random_sleep(rand_st=5, rand_range=5)
        #     return get_playlist_by_channelid(channel_id, language, __retry=__retry-1)
        raise Exception(err_str)
    else:
        print(f"get_playlist_by_channelid > Found all the videos. Total retrieved:{total_videos_count}")
    finally:
        ret = (total_videos_count, page_count)
        return ret


def format_search_into_video(playlist:dict, language:str)-> ytb_model.Video:
    ''' 格式化youtubesearchpython.Playlist为db.ytb_model.Video '''
    # Todo 预检验
    if not (playlist.get('id') and playlist.get('link')):
        return None
    vid = "ytb_"+str(playlist.get('id', uuid4()))
    cloud_type = int(0)
    cloud_path = str('')
    position = int(3) # 3:qw
    source_type = int(3) # 3:youtube
    # source_type = int(0) # 0:save in db but not download
    source_link = str(playlist.get('link'))
    duration_str = str(playlist.get('duration'))
    duration = parse_time_string_with_colon(duration_str) if duration_str else 0
    info = dumps(playlist)
    return ytb_model.Video(
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

def get_youtuber_channel_id(channel_url:str)->str:
    ''' 获取频道id '''
    # https://www.youtube.com/@NoCopyrightSounds
    channel_name = ""
    
     # 解析URL
    parsed_url = urlparse(channel_url)
    path = parsed_url.path
    
    # 判断路径是以'@'还是'/c/'开始，并提取频道名
    if path.startswith("/@"):
        channel_name = path[2:].split('/')[0]
    elif path.startswith("/c/"):
        # 解码URL编码字符
        channel_name = unquote(path[3:].split('/')[0])
    else:
        raise ValueError("detect youtube channel url failed")
    channelsSearch = ChannelsSearch(query=channel_name, limit=1, language="en", region='US') 
    # print(channelsSearch.result())
    search_result = channelsSearch.result()["result"][0]
    channel_id = search_result.get("id")
    return channel_id