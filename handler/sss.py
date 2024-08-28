import pytz
from os import path, makedirs, walk, getenv
from datetime import datetime
from uuid import uuid4
from json import dumps
from traceback import format_exception # Python 3.10+
# from urllib.parse import urljoin, urlparse, unquote
from time import sleep
# from database import ytb_model, ytb_api
# from utils.utime import random_sleep, parse_time_string_with_colon
from youtubesearchpython import Playlist, playlist_from_channel_id
from youtubesearchpython import ChannelsSearch





def format_search_into_video(url_id:str, language:str) -> str:
    ''' 获取并保存频道下所有视频
    @channel_id:str 频道id
    @lanuage:str    频道视频语言
    '''
    #判断视频列表的数量
    playlist_num = Playlist(f'https://www.youtube.com/playlist?list={url_id}')
    link_len_videos = len(playlist_num.videos)
    # print(playlist_num.getNextVideos)
    # channel_id = "PLgyY1WylJUmj22QQfq1MJncAa2zbRJWJ0" # Đậu Phộng TV

    is_first = True
    page_count = int(0) #总视频数
    total_videos_count = int(0) #总页数
    ret = (total_videos_count, page_count)
    try:
        while 1:
            page_count += 1
            if is_first:
                playlist = Playlist.get(f'https://www.youtube.com/playlist?list={url_id}', timeout=10)
                is_first = False
            else:
                playlist_num.getNextVideos
                playlist = Playlist.get(f'https://www.youtube.com/playlist?list={url_id}', timeout=10)
                # print(playlist)
            # link_playlist_len = len(playlist_num.videos)
            # actual_len = link_playlist_len - total_videos_count
            # print(f'get_playlist_by_channelid > Playlist retrieved new {actual_len} videos')

            vid = "ytb_"+str(playlist.get('id', uuid4()))
            cloud_type = int(0)
            cloud_path = str('')
            position = int(3) # 3:qw
            source_type = int(3) # 3:youtube
            # source_type = int(0) # 0:save in db but not download
            source_link = playlist.get('videos')[page_count]['link']
            duration_str = str(playlist.get('videos')[page_count]['duration'])
            duration = parse_time_string_with_colon(duration_str) if duration_str else 0
            print(source_link,duration)
            info = dumps(playlist)

            # print(vid,cloud_type,cloud_path,position,source_type,source_link,duration,info)
            if page_count > link_len_videos - 1:
                exit()
            
        return page_count
    except Exception as e:
        err_str = "".join(format_exception(e)).strip()
        print(f"get_playlist_by_channelid > ERROR | {err_str}")
        # if __retry > 0:
        #     random_sleep(rand_st=5, rand_range=5)
        #     return get_playlist_by_channelid(channel_id, language, __retry=__retry-1)
        raise Exception(err_str)
    # else:
    #     print(f"get_playlist_by_channelid > Found all the videos. Total retrieved:{total_videos_count}")
    finally:
        ret = (total_videos_count, page_count)
        return ret


def parse_time_string_with_colon(time_str)->int:
    ''' 将时间字符串按照 : 分割, 换算秒数 '''
    ret_sec = 0
    try:
        if ":" in time_str:
            time_parts = list(map(int, time_str.split(':')))

            # 根据长度判断输入的格式
            if len(time_parts) == 3:
                hours, minutes, seconds = time_parts
            elif len(time_parts) == 2:
                hours = 0
                minutes, seconds = time_parts
            elif len(time_parts) == 1:
                hours = 0
                minutes = 0
                seconds = time_parts[0]
            else:
                raise ValueError("Invalid time format")

            # 计算总秒数
            ret_sec = hours * 3600 + minutes * 60 + seconds
        else:
            ret_sec = int(time_str)
    except Exception as e:
        print(f"parse_time_string_with_colon {time_str} failed", e.__str__)
    finally:
        return ret_sec

url_id = "PLgyY1WylJUmj22QQfq1MJncAa2zbRJWJ0"
print(format_search_into_video(url_id,'fil'))




