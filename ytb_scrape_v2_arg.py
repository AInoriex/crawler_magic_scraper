from dotenv import load_dotenv
load_dotenv()
from os import getpid
from sys import argv
from time import sleep
from utils import logger
from ytb_scrape_ytb_search import scrape_pipeline
from ytb_scrape_yeb_dlp_pip import import_data_to_db_pip
from ytb_scrape_yt_dlp import scrape_ytb_channel_data, import_data_to_db
from handler.yt_dlp_save_url_to_file import yt_dlp_read_url_from_file_v3
from database import ytb_api, ytb_api_v2, ytb_init_video

import sys
import os
import time
import multiprocessing 
import uuid

# 初始化
logger = logger.init_logger("ytb_scrape")

# youtube_search_python
def main():
    if len(argv) <= 2:
        print("[ERROR] Too less arguments of urls to scrape.")
        print("[INFO] Example: python ytb_scrape.py yue https://www.youtube.com/@video-df1md https://www.youtube.com/@MjrmGames")
        exit()
    pid = getpid()
    language = argv[1]
    opt = input(f"[DEBUG] Check your input, language:{language}, url:{argv[2:]}. Continue?(Y/N)")
    if opt in ["Y", "y", "YES", "yes"]:
        for url in argv[2:]:
            print(f"[INFO] Now scrape url:{url}")
            sleep(1)
            scrape_pipeline(pid, channel_url=url, language=language)
    else:
        print(f"You input {opt}. Bye!")
        exit()

# yt-dlp
def main_v2():
    """
    通过命令行获取博主链接并写入txt文本,读取文本入库
    """
    if len(argv) <= 2:
        print("[ERROR] Too less arguments of urls to scrape.")
        print("[INFO] Example: python ytb_scrape_arg.py yue https://www.youtube.com/@video-df1md")
        exit()
    pid = getpid()
    language = argv[1]
    opt = input(f"[DEBUG] Check your input, language:{language}, url:{argv[2:]}. Continue?(Y/N)")
    if opt in ["Y", "y", "YES", "yes"]:
        for url in argv[2:]:
            print(f"[INFO] Now scrape url:{url}")
            sleep(1)
            for channel_url in argv[2:]:
                count = 0
                target_youtuber_blogger_urls = scrape_ytb_channel_data(pid=pid,channel_url=channel_url, language=language)
                if len(target_youtuber_blogger_urls) <= 0:
                    continue
                for watch_url in target_youtuber_blogger_urls:
                    import_data_to_db(pid, watch_url, language=language)
                    print(f"{count} | {watch_url} 处理完毕")
                    count += 1
                    time.sleep(0.5)
    else:
        print(f"You input {opt}. Bye!")
        exit()

# yt-dlp
def main_v3():
    """
    通过命令行获取博主链接并对同一对象多进程入库
    """
    if len(argv) <= 2:
        print("[ERROR] Too less arguments of urls to scrape.")
        print("[INFO] Example: python ytb_scrape_arg.py yue https://www.youtube.com/@video-df1md")
        exit()
    pid = getpid()  # 捕获进程
    task_id = str(uuid.uuid4())  # 获取任务ID
    target_language = argv[1]
    opt = input(f"[DEBUG] Check your input, language:{target_language}, url:{argv[2:]}. Continue?(Y/N)")
    if opt in ["Y", "y", "YES", "yes"]:
        for url in argv[2:]:
            print(f"[INFO] Now scrape url:{url}")
            sleep(1)
            for channel_url in argv[2:]:
                time_st = time.time()  # 获取采集数据的起始时间
                target_youtuber_blogger_urls = yt_dlp_read_url_from_file_v3(url=channel_url, language=target_language)
                # 统计总时长
                total_duration = sum([int(duration_url.split(' ')[1].strip().split('.')[0]) for duration_url in target_youtuber_blogger_urls])
                if len(target_youtuber_blogger_urls) <= 0:
                    logger.error("ytb_scrape_v2_arg > no watch urls to import.")
                    # exit()
                    continue
                try:
                    # 使用多进程处理video_url_list入库 # 创建进程池
                    pool = multiprocessing.Pool(5)
                    # 将列表分成5个子集，分配给每个进程
                    # chunks = np.array_split(target_youtuber_blogger_urls, 5)
                    chunk_size = len(target_youtuber_blogger_urls) // 5
                    chunks = [target_youtuber_blogger_urls[i:i + chunk_size] for i in range(0, len(target_youtuber_blogger_urls), chunk_size)]
                    # 列表的长度可能会有剩余的元素，我们将它们分配到最后一个子集中
                    if len(chunks) < 5:
                        chunks.append(target_youtuber_blogger_urls[len(chunks)*chunk_size:])
                    time_ed = time.time()
                    spend_scrape_time =  time_ed - time_st  # 采集总时间
                    # 启动进程池中的进程，传递各自的子集和进程ID
                    for pool_num, chunk in enumerate(chunks):
                        # 将各项参数封装为Video对象
                        video_chunk = ytb_init_video.Video(channel_url, chunk, total_duration, target_language, len(target_youtuber_blogger_urls))
                        pool.apply_async(import_data_to_db_pip, (video_chunk, pool_num, spend_scrape_time, pid, task_id))
                    pool.close()
                    pool.join()
                except KeyboardInterrupt:
                    # 捕获到 Ctrl+C 时，确保终止所有子进程
                    logger.warning("KeyboardInterrupt detected, terminating pool...")
                    pool.terminate()
                    sys.exit()  # 退出主程序


if __name__ == "__main__":
    main_v3()