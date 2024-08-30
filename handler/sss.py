import pytz
import time
from os import path, makedirs, walk, getenv
from datetime import datetime
from uuid import uuid4
from json import dumps
from traceback import format_exception # Python 3.10+
# from urllib.parse import urljoin, urlparse, unquote
# from database import ytb_model, ytb_api
# from utils.utime import random_sleep, parse_time_string_with_colon
from youtubesearchpython import Playlist, playlist_from_channel_id
from youtubesearchpython import ChannelsSearch


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


def save_playlist_all_videos(playlist_id:str, language:str ) -> str:
    ''' 获取并保存频道下所有视频
    @playlist_id:str 频道id
    @lanuage:str    频道视频语言
    '''
    # playlist_id = "PL6xnAvlFTCA05ibBrxlb-vwbiMoTATI1P" # Đậu Phộng TV
    is_first = True
    last_num_videos = current_num_videos = int(0)  # 上个列表 # 当前视频总数
    playlist_data = Playlist(f'https://www.youtube.com/playlist?list={playlist_id}') # 播放列表信息
    try:
        while 1:
            if is_first:
                for pd_list in playlist_data.videos[last_num_videos:]:
                    db_playlist_video = format_search_into_video(playlist=pd_list, language=language)
                    time.sleep(1.2)
                    last_num_videos += 1
                is_first = False

            else:
                while playlist_data.hasMoreVideos:
                    playlist_data.getNextVideos()
                    current_num_videos = len(playlist_data.videos)  # 获取当前视频总数
                    actual_len = current_num_videos - last_num_videos  # 实际视频数量
                    print(f'get_playlist_by_playlistid > Playlist retrieved new {actual_len} videos')
                    if current_num_videos >= 0:
                        for pd_list in playlist_data.videos[last_num_videos:]:
                            db_playlist_video = format_search_into_video(playlist=pd_list, language=language)
                            if db_playlist_video != None:
                                time.sleep(1)
                            else:
                                print(f"get_playlist_by_playlistid > format_search_into_video failed. video:{pd_list}")
                        else:
                            print(f"get_playlist_by_playlistid > Create page:{last_num_videos} of videos done, len_playlist_videos:{actual_len}")
                            actual_len = current_num_videos
                else:
                    print(f"get_playlist_by_playlistid > Get no more pages playlist videos, now page_count:{actual_len}.")
                    break
            # if is_touch_fish_time():
            #     random_sleep(rand_st=5, rand_range=10) #请求失败等待5-15s
            # else:
            #     random_sleep(rand_st=20, rand_range=20) #请求失败等待20-40s(非摸鱼时间)
  
    except Exception as e:
        print(e)
        raise Exception(e)
    else:
        print(f"get_playlist_by_channelid > Found all the videos. Total retrieved:{actual_len}")
    finally:
        ret = (actual_len, current_num_videos)
        return ret



def format_search_into_video(playlist:dict, language:str)-> list:
    ''' 格式化youtubesearchpython.Playlist为db.ytb_model.Video '''
    # Todo 预检验
    if not (playlist.get('id') and playlist.get('link')):
        return None
    vid = "ytb_"+str(playlist['id']) if str(playlist['id']) != None else "ytb_" + str(uuid4())  
    cloud_type = int(0)
    cloud_path = str('')
    position = int(3) # 3:qw
    source_type = int(3) # 3:youtube
    # source_type = int(0) # 0:save in db but not download
    source_link = str(playlist.get('link'))
    duration_str = str(playlist.get('duration'))
    # duration = parse_time_string_with_colon(duration_str) if duration_str else 0
    # info = dumps(playlist)
    return [vid,position,source_type,cloud_type,cloud_path,source_link,language]




playlist_id = "PL6xnAvlFTCA05ibBrxlb-vwbiMoTATI1P"
print(save_playlist_all_videos(playlist_id,"en"))
