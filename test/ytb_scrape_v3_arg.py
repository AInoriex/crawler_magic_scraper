from dotenv import load_dotenv
load_dotenv()
from os import getpid
from sys import argv
from time import sleep
from ytb_scrape_ytb_search import scrape_pipeline
from ytb_scrape_yt_dlp import scrape_ytb_channel_data, import_data_to_db
from handler.yt_dlp_save_url_to_file import yt_dlp_read_url_from_file_v3
from utils import logger

import time
import multiprocessing

# 初始化
logger = logger.init_logger("ytb_scrape")
# yt-dlp
def main_v2():
    if len(argv) <= 2:
        print("[ERROR] Too less arguments of urls to scrape.")
        print("[INFO] Example: python ytb_scrape_arg.py yue https://www.youtube.com/@video-df1md")
        exit()
    pid = getpid()
    target_language = argv[1]
    opt = input(f"[DEBUG] Check your input, language:{target_language}, url:{argv[2:]}. Continue?(Y/N)")
    if opt in ["Y", "y", "YES", "yes"]:
        for url in argv[2:]:
            print(f"[INFO] Now scrape url:{url}")
            sleep(1)
            for channel_url in argv[2:]:
                logger.info(f"Scraper Pipeline > {pid} 当前处理频道: {channel_url} | 语言：{target_language}")
                target_youtuber_blogger_urls = yt_dlp_read_url_from_file_v3(url=channel_url, language=target_language)
                if len(target_youtuber_blogger_urls) <= 0:
                    logger.error("Scraper Pipeline > no watch urls to import.")
                    # exit()
                    continue
                # 使用多进程处理video_url_list入库 # 创建进程池
                pool = multiprocessing.Pool(5)
                # 将列表分成5个子集，分配给每个进程
                # chunks = np.array_split(target_youtuber_blogger_urls, 5)
                chunk_size = len(target_youtuber_blogger_urls) // 5
                chunks = [target_youtuber_blogger_urls[i:i + chunk_size] for i in range(0, len(target_youtuber_blogger_urls), chunk_size)]
                # print(chunks)
                # 列表的长度可能会有剩余的元素，我们将它们分配到最后一个子集中
                if len(chunks) < 5:
                    chunks.append(target_youtuber_blogger_urls[len(chunks)*chunk_size:])
                # 启动进程池中的进程，传递各自的子集和进程ID
                for i, chunk in enumerate(chunks):
                    pool.apply_async(import_data_to_db, (pid, tuple(chunk), i, target_language))
                    # print(i,chunk)
                # 关闭进程池
                pool.close()
                # 等待所有进程结束
                pool.join()
    else:
        print(f"You input {opt}. Bye!")
        exit()

if __name__ == "__main__":
    main_v2()