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


def save_playlist_all_videos(playlist_id:str, language:str ) -> str:
    ''' 获取并保存频道下所有视频
    @playlist_id:str 频道id
    @lanuage:str    频道视频语言
    '''
    # playlist_id = "PL6xnAvlFTCA05ibBrxlb-vwbiMoTATI1P" # Đậu Phộng TV
    is_first = True
    num_videos = current_num_videos = int(0)  # 累计视频数量 # 当前视频总数
    playlist_data = Playlist(f'https://www.youtube.com/playlist?list={playlist_id}') # 播放列表信息
    try:
        while 1:
            if is_first:
                for pd_list in playlist_data.videos[num_videos:]:
                    db_playlist_video = format_search_into_video(playlist=pd_list, language=language)
                    print(num_videos)
                    print(db_playlist_video)
                    time.sleep(0.5)
                    num_videos += 1
                current_num_videos = len(playlist_data.videos)
                is_first = False

            else:
                while playlist_data.hasMoreVideos:
                    playlist_data.getNextVideos()
                    current_num_videos = len(playlist_data.videos)  # 获取当前视频总数
                    print("当前视频总数:" + str(current_num_videos))
                    actual_len = current_num_videos - num_videos  # 实际视频数量
                    print(f'get_playlist_by_playlistid > Playlist retrieved new {actual_len} videos')
                    if current_num_videos > 0:
                        time.sleep(1)
                        for pd_list in playlist_data.videos[num_videos:]:
                            db_playlist_video = format_search_into_video(playlist=pd_list, language=language)
                            print(num_videos)
                            print(db_playlist_video)
                            time.sleep(1.5)
                            num_videos += 1
                            # if db_playlist_video != None:
                            #     print(db_playlist_video)
                            # else:
                            #     print(f"get_playlist_by_playlistid > format_search_into_video failed. video:{pd_list}")
                        else:
                            print(f"get_playlist_by_playlistid > Create page:{num_videos} of videos done, len_playlist_videos:{current_num_videos}")
                            actual_len = current_num_videos
                else:
                    print(f"get_playlist_by_playlistid > Get no more pages playlist videos, now num_videos:{actual_len}.")
                    break
  
    except Exception as e:
        print(e)
        raise Exception(e)
    else:
        print(f"get_playlist_by_channelid > Found all the videos. Total retrieved:{actual_len}")
    finally:
        ret = (num_videos, current_num_videos)
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
    # duration_str = str(playlist.get('duration'))
    # duration = parse_time_string_with_colon(duration_str) if duration_str else 0
    # info = dumps(playlist)
    return [vid,position,source_type,cloud_type,cloud_path,source_link,language]




playlist_id = "PL6xnAvlFTCA05ibBrxlb-vwbiMoTATI1P"
print(save_playlist_all_videos(playlist_id,"en"))
