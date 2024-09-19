from dotenv import load_dotenv
load_dotenv()

import time
from os import getpid, getenv
from sys import argv
from time import sleep
from handler.youtube import get_youtuber_channel_id, save_channel_all_videos_local
from utils import logger
from utils.utime import random_sleep, get_now_time_string, format_second_to_time_string
from utils.lark import alarm_lark_text
from utils.ip import get_local_ip, get_public_ip

LIMIT_FAIL_COUNT = int(getenv("LIMIT_FAIL_COUNT"))
# LIMIT_FAIL_COUNT = 10
''' 处理失败任务限制数 '''
LIMIT_LAST_COUNT = int(getenv("LIMIT_LAST_COUNT"))
# LIMIT_LAST_COUNT = 100
''' 连续处理任务限制数 '''

# 初始化
logger = logger.init_logger("ytb_scrape")
local_ip = get_local_ip()
continue_fail_count = 0 # 连续失败的任务个数

def scrape_pipeline_local(pid:int, channel_url:str):
    try:
        # set query
        channel_id = ""
        # channel_id = "UC6Q8f2fK10PLMo4kkiBSCXA" # Đậu Phộng TV
        channel_id = get_youtuber_channel_id(channel_url)

        logger.info(f"Scraper Pipeline > pid {pid} get {channel_id} success, start scraping")
        time_st = time.time()

        # 油管数据采集
        total_videos_count, page_count = save_channel_all_videos_local(
            channel_id=channel_id,
            save_path=f"./download/{channel_id}.txt",
        )

        # 日志记录
        time_ed = time.time()
        spend_time = time_ed - time_st
        logger.info(
            f"Scraper Pipeline > pid {pid} scraping done, spend_time: %.2f seconds" \
            %(spend_time) \
        )
    
    except KeyboardInterrupt:
        logger.warning(f"Scraper Pipeline > pid {pid} interrupted processing, exit.")
        exit(0)

    except Exception as e:
        continue_fail_count += 1
        logger.error(f"Scraper Pipeline > pid {pid} error processing")
        logger.error(e, stack_info=True)

        # alarm to Lark Bot
        public_ip = get_public_ip()
        now_str = get_now_time_string()
        notice_text = f"[Youtube Scraper | ERROR] 数据采集失败. \
            \n\t进程ID: {pid} \
            \n\t频道URL: {channel_url} \
            \n\t频道ID: {channel_id} \
            \n\t共处理了{format_second_to_time_string(time.time() - time_st)} \
            \n\tIP: {local_ip} | {public_ip} \
            \n\tERROR: {e} \
            \n\t告警时间: {now_str}"
        alarm_lark_text(webhook=getenv("NOTICE_WEBHOOK"), text=notice_text)
        # 失败过多直接退出
        if continue_fail_count > LIMIT_FAIL_COUNT:
            logger.error(f"Scraper Pipeline > pid {pid} unexpectable exit beceuse of too much fail count: {continue_fail_count}")
            exit()
    else:
        # alarm to Lark Bot
        public_ip = get_public_ip()
        now_str = get_now_time_string()
        notice_text = f"[Youtube Scraper | DEBUG] 数据采集完毕. \
            \n\t进程ID: {pid} \
            \n\t频道URL: {channel_url} \
            \n\t频道ID: {channel_id} \
            \n\t总视频数: {total_videos_count} | 总页数: {page_count} \
            \n\t共处理了{format_second_to_time_string(spend_time)} \
            \n\tIP: {local_ip} | {public_ip} \
            \n\tTime: {now_str}"
        alarm_lark_text(webhook=getenv("NOTICE_WEBHOOK"), text=notice_text)

# 启动方法：
# python ytb_scrape_local.py {博主主页链接}
# python ytb_scrape_local.py https://www.youtube.com/@video-df1md
def main():
    if len(argv) <= 1:
        print("[ERROR] Too less arguments of urls to scrape.")
        print("[INFO] Example: python ytb_scrape_local.py https://www.youtube.com/@video-df1md")
        exit()
    pid = getpid()
    opt = input(f"[DEBUG] Check your input, url:{argv[1:]}. Continue?(Y/N)")
    if opt in ["Y", "y", "YES", "yes"]:
        for url in argv[1:]:
            print(f"[INFO] Now scrape url:{url}")
            sleep(1)
            scrape_pipeline_local(pid, channel_url=url)
    else:
        print(f"You input {opt}. Bye!")
        exit()

if __name__ == "__main__":
    main()