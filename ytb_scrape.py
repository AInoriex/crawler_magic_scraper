

# 加载.env文件
from dotenv import load_dotenv
load_dotenv()

import os
import time
from handler.youtube import save_channel_all_videos, get_youtuber_channel_id
from utils import logger
from utils.utime import random_sleep, get_now_time_string, format_second_to_time_string
from utils.lark import alarm_lark_text
from utils.ip import get_local_ip, get_public_ip
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
target_language = "th"
target_youtuber_channel_urls = [
    # "https://www.youtube.com/@BaoQuandoinhandan/videos",
    # "https://www.youtube.com/@vtcnow/videos",
    # "https://www.youtube.com/@HuynhDuyKhuongofficial/videos",
    # "https://www.youtube.com/@thuyetphapthichdaothinh/videos",

    # Tai
    # "https://www.youtube.com/@Ch3Thailand/videos",
    # "https://www.youtube.com/@one31official/videos",
    # "https://www.youtube.com/@CHANGE2561/videos",
    # "https://www.youtube.com/@CH3Plus/videos",
    # "https://www.youtube.com/@pigkaploy/videos",
    # "https://www.youtube.com/@genierock/videos",
    # "https://www.youtube.com/@zbingz",
    # "https://www.youtube.com/@BieTheSka",
    # "https://www.youtube.com/@KaykaiSalaiderChannel",
    # "https://www.youtube.com/@VrzoTvThailand",
    # "https://www.youtube.com/@mnjtv2020",
    # "https://www.youtube.com/@yimyamtv", # redo
    # "https://www.youtube.com/@primkung.official", # redo
    # "https://www.youtube.com/@PEACHEATLAEK", # redo
    # "https://www.youtube.com/@kamsingfamilychannel", # redo

    # Id
    "https://www.youtube.com/@MDEntertainment/videos",
    "https://www.youtube.com/@RhomaIramaOfficial/videos",
    "https://www.youtube.com/@corbuzier/videos",
    "https://www.youtube.com/@ReyUtamiBenuaEntertainment/videos",
    "https://www.youtube.com/@Ftvhits/videos",
    "https://www.youtube.com/@CERITAUMSU/videos",
    "https://www.youtube.com/@UMSUMedan/videos",
    "https://www.youtube.com/@AkbarFaizalUncensored/videos",
    "https://www.youtube.com/@CNBC_ID/videos"
]

target_youtuber_channel_ids = []

def scrape_pipeline(pid:int, channel_url:str, language="unknown"):
    try:
        # set query
        language = language
        channel_id = ""
        # channel_id = "UC6Q8f2fK10PLMo4kkiBSCXA" # Đậu Phộng TV
        channel_id = get_youtuber_channel_id(channel_url)

        logger.info(f"Scraper Pipeline > pid {pid} get {channel_id} success, start scraping")
        time_st = time.time()

        # 油管数据采集
        total_videos_count, page_count = save_channel_all_videos(
            channel_id=channel_id,
            language=language,
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
        os._exit(0)

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
            \n\t语言: {language} \
            \n\t共处理了{format_second_to_time_string(time.time() - time_st)} \
            \n\tIP: {local_ip} | {public_ip} \
            \n\tERROR: {e} \
            \n\t告警时间: {now_str}"
        alarm_lark_text(webhook=os.getenv("NOTICE_WEBHOOK"), text=notice_text)
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
            \n\t频道ID: {channel_id} | 语言: {language} \
            \n\t总视频数: {total_videos_count} | 总页数: {page_count} \
            \n\t共处理了{format_second_to_time_string(spend_time)} \
            \n\tIP: {local_ip} | {public_ip} \
            \n\tTime: {now_str}"
        alarm_lark_text(webhook=os.getenv("NOTICE_WEBHOOK"), text=notice_text)

def main():
    pid = os.getpid()
    if target_language == "":
        print("[ERROR] please input target language.")
        exit()
    elif len(target_youtuber_channel_urls) <= 0:
        print("[ERROR] please input target channel urls.")
        exit()
    for channel_url in target_youtuber_channel_urls:
        scrape_pipeline(pid, channel_url, language=target_language)

if __name__ == "__main__":
    main()