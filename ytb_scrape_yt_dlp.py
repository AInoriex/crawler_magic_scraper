# 加载.env文件
from dotenv import load_dotenv
load_dotenv()

import os
import time
from database import ytb_api
from handler.yt_dlp import get_ytb_blogger_url, ytb_dlp_automatic
from handler.yt_dlp_save_url_to_file import yt_dlp_read_url_from_file, yt_dlp_read_url_from_file_v2
from utils import logger
from utils.ip import get_local_ip, get_public_ip
from utils.lark import alarm_lark_text
from utils.utime import get_now_time_string, format_second_to_time_string
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

# 印尼语 DONE
# TEXT = 'Yinniyu'
# target_language = "id"
# https://www.youtube.com/@DylandPROS/videos
# https://www.youtube.com/@radityadika
# https://www.youtube.com/@tvOneNews/videos
# INPUT = 'https://www.youtube.com/@tvOneNews/videos'
# file_path = 'G:\crawler_magic_scraper\download_lang\Yinniyu.txt'

# 俄语
# TEXT = 'Eyu'
target_language = "text"
CHANNEL_URL_LIST = [
    # 已处理
    # "https://www.youtube.com/@RoomFactoryy",
    # "https://www.youtube.com/@Litvin_Misha_11",
    # "https://www.youtube.com/@arishnev",
    # "https://www.youtube.com/@K-Media",
    # "https://www.youtube.com/@EGORIK.SHKRED",
    # "https://www.youtube.com/@standupclubru",
    # "https://www.youtube.com/@xabibkaa",
    # "https://www.youtube.com/@veloloh",
    # "https://www.youtube.com/@redactsiya",
    # "https://www.youtube.com/@YFrostA",
    # "https://www.youtube.com/@Vladus",
    # "https://www.youtube.com/@Masomka",
    # "https://www.youtube.com/@kuplinovplay",

    # 未处理
#     "https://www.youtube.com/@getmovies",
#     "https://www.youtube.com/@MashaBearRUSSIAN",
#     "https://www.youtube.com/@LikeNastya_Vlog",
#     "https://www.youtube.com/@HiBestMan",
#     "https://www.youtube.com/@MrMarmok",
#     "https://www.youtube.com/@TheBrianMaps",
#     "https://www.youtube.com/@ADME_RU",
#     "https://www.youtube.com/@TeremokTV",
#     "https://www.youtube.com/@MasterskayaNastroeny",
# ]

# 阿拉伯语
# TEXT = 'ar_Haider Khalid'
# target_language = "ar"
# INPUT = "https://www.youtube.com/@RABSHA22"
# CHANNEL_URL_LIST = [
    # 已处理
    # "https://www.youtube.com/@RABSHA22",
    # "https://www.youtube.com/@Rita99",
    # "https://www.youtube.com/@aymanTV1",
    # "https://www.youtube.com/@the_horror",
    # "https://www.youtube.com/@LearnWithZakaria",
    # "https://www.youtube.com/@alkottaab",
    # "https://www.youtube.com/@ChefMadni",
    # "https://www.youtube.com/@Espitalia",
    # "https://www.youtube.com/@sa7iChannel",
    # "https://www.youtube.com/@mmoshaya",
    # "https://www.youtube.com/@MashaBearARAB",
    # "https://www.youtube.com/@Ikram-du7fz",
    # "https://www.youtube.com/@khalejiatv",
    # "https://www.youtube.com/@saudchannel4",
    # "https://www.youtube.com/shahidvod",
    # "https://www.youtube.com/@BarryTube",
    # "https://www.youtube.com/@MjrmGames",

    # 未处理
    "https://www.youtube.com/@MBC1",
    "https://www.youtube.com/@monti1u",
]


def scrape_ytb_channel_data(pid:str, channel_url:str, language:str):
    ''' yt-dlp获取频道下所有URL '''
    count = 0
    START_INDEX = 0
    return_url_list = []

    # 1. 使用yt-dlp获取所有url写入txt
    # file_path = yt_dlp_read_url_from_file(TEXT, INPUT)
    file_path = yt_dlp_read_url_from_file_v2(url=channel_url, language=language)

    # 2. 读取txt内url
    # 如果中间断了就更换成文件路径，不用再从新获取视频链接
    with open(file_path, "r") as f:
        while True:
            link = f.readline()
            if not link:  # 如果没有更多行，跳出循环
                break
            # link = link.replace('\n','').strip()
            if count < START_INDEX:
                print(f"Scraper Pipeline > [INFO] 当前{count}跳过, START_INDEX:{START_INDEX}")
                continue
            count += 1
            return_url_list.append(link.strip())
            # 提供一个方法，将拿取的list做进一步处理(暂时处理不了)
            # blogger_url_list.append(yt_dlp_hanfdle_file(line))

    # 目标列表
    logger.info(f"Scraper Pipeline > {channel_url}频道一共获取到{count}条url")
    return return_url_list


def import_data_to_db(pid:int, channel_url:tuple, language="unknown"):
    # 数据导入数据库
    try:
        time_st = time.time()
        
        # # 油管数据采集
        # urls_list = get_ytb_blogger_url(
        #     blogger_url=channel_url,
        #     language=language,
        # )

        # 油管采集字幕
        video_object = ytb_dlp_automatic(
            video_url=channel_url,
            language=language
        )
        # print(urls_list)

        # 将数据更新入库
        ytb_api.create_video(video_object)
        # print("测试成功",video_object)

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
            \n\t频道ID: {''} | 语言: {language} \
            \n\t共处理了{format_second_to_time_string(spend_time)} \
            \n\tIP: {local_ip} | {public_ip} \
            \n\tTime: {now_str}"
        alarm_lark_text(webhook=os.getenv("NOTICE_WEBHOOK"), text=notice_text)

def ytb_main():
    pid = os.getpid()
    if target_language == "":
        print("[ERROR] please input target language.")
        exit()

    for channel_url in CHANNEL_URL_LIST:
        count = 0
        logger.info(f"Scraper Pipeline > {pid} 当前处理频道: {channel_url} | 语言：{target_language}")
        target_youtuber_blogger_urls = scrape_ytb_channel_data(channel_url=channel_url, language=target_language)

        if len(target_youtuber_blogger_urls) <= 0:
            logger.error("Scraper Pipeline > no watch urls to import.")
            # exit()
            continue
        for watch_url in target_youtuber_blogger_urls:
            import_data_to_db(pid, watch_url, language=target_language)
            print(f"{count} | {watch_url} 处理完毕")
            count += 1
            time.sleep(0.5)
            

if __name__ == '__main__':
    ytb_main()