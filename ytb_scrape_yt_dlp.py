# 加载.env文件
from dotenv import load_dotenv
load_dotenv()

import os
import time
from handler.youtube import save_channel_all_videos, get_youtuber_channel_id
from utils import logger
from database import ytb_api
from utils.utime import random_sleep, get_now_time_string, format_second_to_time_string
from utils.lark import alarm_lark_text
from utils.ip import get_local_ip, get_public_ip
from handler.yt_dlp import get_ytb_blogger_url
# from utils.cos import upload_file
# from utils.obs import upload_file

# 初始化
logger = logger.init_logger("ytb_scrape")
local_ip = get_local_ip()
continue_fail_count = 0 # 连续失败的任务个数

LIMIT_FAIL_COUNT = int(os.getenv("LIMIT_FAIL_COUNT"))
# LIMIT_FAIL_COUNT = 10
''' 处理失败任务限制数 '''
LIMIT_LAST_COUNT = int(os.getenv("LIMIT_LAST_COUNT"))
# LIMIT_LAST_COUNT = 100
''' 连续处理任务限制数 '''

# 目标列表
target_language = "vi"
target_youtuber_blogger_urls = [
    # "https://www.youtube.com/@daihanoi-htv/videos"
    # "https://www.youtube.com/@toancanh24/videos"
    # "https://www.youtube.com/@LegacyUnder/videos"
    "https://www.youtube.com/@vtv24/videos"
    # "https://www.youtube.com/@BaoQuandoinhandan/videos",
    # "https://www.youtube.com/@vtcnow/videos",
    # "https://www.youtube.com/@HuynhDuyKhuongofficial/videos",
    # "https://www.youtube.com/@thuyetphapthichdaothinh/videos",
]

target_youtuber_channel_ids = []

def scrape_pipeline(pid:int, channel_url:str, language="unknown"):
    try:
        time_st = time.time()

        # 油管数据采集
        urls_list = get_ytb_blogger_url(
            blogger_url=channel_url,
            language=language,
        )
        print(urls_list)
        # 将数据更新入库
        for urls in urls_list:
            if urls != None:
                ytb_api.create_video(urls)

        # 日志记录
        time_ed = time.time()
        spend_time = time_ed - time_st
        logger.info(
            f"Scraper Pipeline > pid {pid} scraping done, spend_time: %.2f seconds" \
            %(spend_time) \
        )
    
    except KeyboardInterrupt:
        logger.warning(f"Scraper Pipeline > pid {pid} interrupted processing, exit.")
        os._exit(0)

    except Exception as e:
        # continue_fail_count += 1
        logger.error(f"Scraper Pipeline > pid {pid} error processing")
        logger.error(e, stack_info=True)

        # alarm to Lark Bot
        public_ip = get_public_ip()
        now_str = get_now_time_string()
        notice_text = f"[Youtube Scraper | ERROR] 数据采集失败. \
            \n\t进程ID: {pid} \
            \n\t频道URL: {channel_url} \
            \n\t频道ID: {''} \
            \n\t语言: {language} \
            \n\t共处理了{format_second_to_time_string(time.time() - time_st)} \
            \n\tIP: {local_ip} | {public_ip} \
            \n\tERROR: {e} \
            \n\t告警时间: {now_str}"
        alarm_lark_text(webhook=os.getenv("NOTICE_WEBHOOK"), text=notice_text)
        # 失败过多直接退出
        # if continue_fail_count > LIMIT_FAIL_COUNT:
        #     logger.error(f"Scraper Pipeline > pid {pid} unexpectable exit beceuse of too much fail count: {continue_fail_count}")
        #     exit()
    else:
        # alarm to Lark Bot
        public_ip = get_public_ip()
        now_str = get_now_time_string()
        notice_text = f"[Youtube Scraper | DEBUG] 数据采集完毕. \
            \n\t进程ID: {pid} \
            \n\t频道URL: {channel_url} \
            \n\t频道ID: {''} | 语言: {language} \
            \n\t共处理了{format_second_to_time_string(spend_time)} \
            \n\tIP: {local_ip} | {public_ip} \
            \n\tTime: {now_str}"
        alarm_lark_text(webhook=os.getenv("NOTICE_WEBHOOK"), text=notice_text)

def main():
    pid = os.getpid()
    if target_language == "":
        print("[ERROR] please input target language.")
        exit()
    elif len(target_youtuber_blogger_urls) <= 0:
        print("[ERROR] please input target channel urls.")
        exit()
    for channel_url in target_youtuber_blogger_urls:
        scrape_pipeline(pid, channel_url, language=target_language)
        print(channel_url)

if __name__ == "__main__":
    main()