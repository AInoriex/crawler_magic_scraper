# from utils.tool import load_cfg
# cfg = load_cfg("config.json")
# from config import Config
# config = Config()
# config.load_cfg("conf/config.json")
# cfg = config.cfg

import time
import random
from os import path, makedirs, walk, getenv
from handler.info import dump_info
from utils.utime import random_sleep
import yt_dlp
from yt_dlp import YoutubeDL
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from datetime import datetime
import pytz
from youtubesearchpython import Playlist, playlist_from_channel_id

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


# 生成视频信息（yt_dlp只获取信息不下载）
def generate_video_info(vid, ydl:YoutubeDL):
    video_info = ydl.extract_info(vid, download=False, process=False)

    info_dict = {
        "id": video_info["id"],
        "title": video_info["title"],
        "full_url": video_info["webpage_url"],
        "author": video_info["uploader_id"],
        "duration": video_info["duration"],
        "categories": video_info["categories"],
        "tags": video_info["tags"],
        "view_count": video_info["view_count"],
        "comment_count": video_info["comment_count"],
        "follower_count": video_info["channel_follower_count"],
        "upload_date": video_info["upload_date"],
    }
    return info_dict


# 下载普通油管链接(支持只有请求参数v)
# exp.  https://www.youtube.com/watch?v=6s416NmSFmw&list
def download_by_watch_url(video_url, save_path, __retry=MAX_RETRY):
    print(f"Yt-dlp > download_by_watch_url参数 video_url:{video_url} save_path:{save_path} retry:{__retry}")
    try:
        save_audio_path, save_info_path = make_path(save_path)
        ydl_opts = load_options(save_audio_path)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = generate_video_info(video_url, ydl)
            vid = info_dict["id"]
            save_to_json_file = f"{save_info_path}/{vid}.json"

            ydl.download(vid)
            dump_info(info_dict, save_to_json_file)
            print(f"Yt-dlp > download_by_watch_url生成下载信息：{save_to_json_file}")
    except Exception as e:
        if __retry > 0:
            __retry = __retry - 1
            random_sleep(rand_st=5, rand_range=5)
            return download_by_watch_url(video_url, save_path, __retry=__retry)
        else:
            save_to_fail_file = f"{save_info_path}/{vid}.fail.json"
            dump_info(info_dict, save_to_fail_file)
            raise e
    else:
        # return path.join(save_audio_path, f"{vid}.webm")
        return try_to_get_file_name(save_audio_path, vid, path.join(save_audio_path, f"{vid}.webm"))

# 下载油管播放列表链接
# exp.  
def download_by_playlist(playlist_url, save_path, max_limit=0):
    save_audio_path, save_info_path = make_path(save_path)

    success_num = 0
    ydl_opts = load_options(save_audio_path)
    result_paths = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        author_info = ydl.extract_info(playlist_url, download=False, process=False)

        for entry in author_info["entries"]:
            if success_num >= max_limit and max_limit != 0:
                print("Yt-dlp > YouTube: Successfully downloaded",
                    max_limit,
                    "video(s). Quitting.",
                )
                break
            vid = entry["id"]
            info_dict = generate_video_info(vid, ydl)

            save_to_json_file = f"{save_info_path}/{vid}.json"
            try:
                ydl.download(vid)
                time.sleep(random.uniform(5, 10))  # sleep in case got banned by YouTube
                dump_info(info_dict, save_to_json_file)
                result_paths.append(path.join(save_audio_path, f"{vid}.webm"))
                success_num += 1
            except Exception as e:
                print("Yt-dlp >  YouTube: \033[31mEXCEPTION OCCURED.\033[0m")
                print(e)
                continue
    return result_paths


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
    ytb_timezone = "'America/Los_Angeles'"

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
        print(f"摸鱼判断 > 当地时区 {ytb_timezone} | 当地时间 {current_hour}:{current_mint}")
        return False
    else:
        return True


def get_channel_playlist(channel_id:str, __retry:3):
    ''' 获取频道下所有视频 '''
    # channel_id = "UC_aEa8K-EOJ3D6gOs7HcyNg" # NoCopyrightSounds
    try:
        playlist = Playlist(playlist_from_channel_id(channel_id))

        print(f'Videos Retrieved: {len(playlist.videos)}')

        while playlist.hasMoreVideos:
            print('Getting more videos...')
            playlist.getNextVideos()
            print(f'Videos Retrieved: {len(playlist.videos)}')

    except Exception as e:
        if __retry > 0:
            __retry = __retry - 1
            random_sleep(rand_st=5, rand_range=5)
            return download_by_watch_url(video_url, save_path, __retry=__retry)
        else:
            raise e
    else:
        print('Found all the videos.')
