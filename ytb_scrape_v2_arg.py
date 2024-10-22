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

import sys
import os
import time
import multiprocessing 

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
    target_language = argv[1]
    opt = input(f"[DEBUG] Check your input, language:{target_language}, url:{argv[2:]}. Continue?(Y/N)")
    if opt in ["Y", "y", "YES", "yes"]:
        for url in argv[2:]:
            print(f"[INFO] Now scrape url:{url}")
            sleep(1)
            for channel_url in argv[2:]:
                time_st = time.time()
                target_youtuber_blogger_urls = yt_dlp_read_url_from_file_v3(url=channel_url, language=target_language)
                # 统计时长和数量
                duration = sum([int(duration_url.split(' ')[1].strip().split('.')[0]) for duration_url in target_youtuber_blogger_urls])
                count = len(target_youtuber_blogger_urls)
                init_url = channel_url
                # logger.info(f"时长:{duration / 3600}小时,{duration / 60}分钟，共获取{count}条链接")
                if len(target_youtuber_blogger_urls) <= 0:
                    logger.error("Scraper Pipeline > no watch urls to import.")
                    # exit()
                    continue
                # 使用多进程处理video_url_list入库 # 创建进程池
                pool = multiprocessing.Pool(4)
                # 将列表分成5个子集，分配给每个进程
                # chunks = np.array_split(target_youtuber_blogger_urls, 5)
                chunk_size = len(target_youtuber_blogger_urls) // 4
                chunks = [target_youtuber_blogger_urls[i:i + chunk_size] for i in range(0, len(target_youtuber_blogger_urls), chunk_size)]
                # print(chunks)
                # 列表的长度可能会有剩余的元素，我们将它们分配到最后一个子集中
                if len(chunks) < 4:
                    chunks.append(target_youtuber_blogger_urls[len(chunks)*chunk_size:])
                time_ed = time.time()
                spend_scrape_time =  time_ed - time_st
                # 启动进程池中的进程，传递各自的子集和进程ID
                try:
                    for i, chunk in enumerate(chunks):
                        pool.apply_async(import_data_to_db_pip, (pid, tuple(chunk), i, duration, count, init_url, spend_scrape_time, target_language))
                        # print(i,chunk)
                    # 关闭进程池    # 等待所有进程结束
                    pool.close()
                    pool.join()
                except KeyboardInterrupt:
                    # 捕获到 Ctrl+C 时，确保终止所有子进程
                    logger.warning("KeyboardInterrupt detected, terminating pool...")
                    pool.terminate()
                    print("All processes have been terminated.")
                    exit(1)  # 直接退出程序
    else:
        print(f"You input {opt}. Bye!")
        exit()

if __name__ == "__main__":
    main_v3()