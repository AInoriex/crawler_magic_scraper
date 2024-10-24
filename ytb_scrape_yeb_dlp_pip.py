# 加载.env文件
from dotenv import load_dotenv
load_dotenv()
from database import ytb_api, ytb_api_v2, ytb_init_video
from handler.yt_dlp import get_ytb_blogger_url, ytb_dlp_automatic
from handler.yt_dlp_save_url_to_file import yt_dlp_read_url_from_file, yt_dlp_read_url_from_file_v2, yt_dlp_read_url_from_file_v3
from utils import logger
from utils.ip import get_local_ip, get_public_ip
from utils.lark import alarm_lark_text
from utils.utime import get_now_time_string, format_second_to_time_string
from multiprocessing import Value
# from utils.cos import upload_file
# from utils.obs import upload_file
import json
import multiprocessing
import os
import time
import numpy as np
import sys
import uuid

# 初始化
logger = logger.init_logger("ytb_scrape")
local_ip = get_local_ip()
public_ip = get_public_ip()
continue_fail_count = 0 # 连续失败的任务个数

LIMIT_FAIL_COUNT = int(os.getenv("LIMIT_FAIL_COUNT"))
# LIMIT_FAIL_COUNT = 10
''' 处理失败任务限制数 '''
LIMIT_LAST_COUNT = int(os.getenv("LIMIT_LAST_COUNT"))
# LIMIT_LAST_COUNT = 100
''' 连续处理任务限制数 '''

target_language = "th"

CHANNEL_URL_LIST = ["https://www.youtube.com/@TheDoShow0909"]

def import_data_to_db_pip(video_urls:ytb_init_video.Video, pool_num:int, spend_scrape_time:float, pid:int, task_id:str):
    """
    油管信息导入数据库

    :param video_urls: 视频信息 Video(tuple, tuple, ...)
    :param pool_num: 线程编号
    :param spend_scrape_time: 采集总时间
    :param pid: 进程ID
    :param task_id: 任务ID
    """
    # 频道通知开始
    now_str = get_now_time_string()
    notice_text = f"[Youtube Scraper | DEBUG] 第{pool_num}个线程开始采集. \
        \n\t频道URL: {video_urls.blogger_url} \
        \n\t语言: {video_urls.language} \
        \n\t入库视频数量: {video_urls.count} \
        \n\t入库时长(小时):{round((video_urls.duration / 3600),3)} \
        \n\t任务ID: {task_id} \
        \n\t任务处理时间: {format_second_to_time_string(spend_scrape_time)} \
        \n\t通知时间: {now_str}"
    alarm_lark_text(webhook=os.getenv("NOTICE_WEBHOOK"), text=notice_text)
    # 数据导入数据库
    for index, video_url in enumerate(video_urls.video_url):
        try:
            logger.info(f"import_data_to_db_pip > 第{pool_num}个进程, 开始处理第{index}个数据: {video_url}")
            time_st = time.time()
            video_object = get_ytb_blogger_url(
                blogger_url=video_url,
                language=video_urls.language,
                task_id=task_id
            )
            # print(f'{video_url} 我是第{pool}个进程, 处理第{count}个URL')
            # 将数据更新入库
            ytb_api.create_video(video_object)
            # ytb_api_v2.sign_database(video_object)
            time.sleep(0.5)

            # 日志记录
            time_ed = time.time()
            spend_time = time_ed - time_st
            logger.info(f"import_data_to_db_pip > 第{pool_num}个进程, 处理第{index}个数据: {video_url} 完毕, 花费时间: {spend_time} seconds")
            # alarm to Lark Bot
            now_str = get_now_time_string()
            notice_text = f"[Youtube Scraper | DEBUG] 数据已采集入库. \
                \n\t进程ID: {pid} \
                \n\t频道信息: {video_urls.language} | {video_urls.blogger_url} \
                \n\t线程信息: {f'第{pool_num}个进程, 处理第{index}个数据: {video_url}'} \
                \n\t共处理了{format_second_to_time_string(spend_time)} \
                \n\t任务ID: {task_id} \
                \n\tIP: {local_ip} | {public_ip} \
                \n\tTime: {now_str}"
            alarm_lark_text(webhook=os.getenv("NOTICE_WEBHOOK"), text=notice_text)
        except Exception as e:
            # continue_fail_count += 1
            logger.error(f"import_data_to_db_pip > 第{pool_num}个进程, 处理第{index}个数据 {video_url} 失败, {e}")
            # logger.error(e, stack_info=True)

            # alarm to Lark Bot
            now_str = get_now_time_string()
            notice_text = f"[Youtube Scraper | ERROR] 数据采集入库失败 \
                \n\t进程ID: {pid} \
                \n\t频道信息: {video_urls.language} | {video_urls.blogger_url} \
                \n\t线程信息: {f'我是第{pool_num}个进程, 处理第{index}个数据: {video_url}'} \
                \n\t任务ID: {task_id} \
                \n\tError: {e} \
                \n\tIP: {local_ip} | {public_ip} \
                \n\tTime: {now_str}"
            alarm_lark_text(webhook=os.getenv("NOTICE_WEBHOOK"), text=notice_text)
            # 失败过多直接退出
            # if continue_fail_count > LIMIT_FAIL_COUNT:
            #     logger.error(f"Scraper Pipeline > pid {pid} unexpectable exit beceuse of too much fail count: {continue_fail_count}")
            #     exit(1)
            continue

        except KeyboardInterrupt:
            logger.warning(f"Scraper Pipeline > pid {pid} interrupted processing, exit.")
            pool_num.terminate()  # 直接终止所有子进程
            sys.exit(1)  # 退出程序
            raise KeyboardInterrupt
        finally:
            #time.sleep(1)
            pass

def ytb_main():
    pid = os.getpid()  # 捕获进程
    task_id = str(uuid.uuid4())  # 获取任务ID
    if target_language == "":
        print("[ERROR] please input target language.")
        exit()
    for channel_url in CHANNEL_URL_LIST:
        logger.info(f"Scraper Pipeline > {pid} 当前处理频道: {channel_url} | 语言：{target_language}")
        time_st = time.time()  # 获取采集数据的起始时间
        target_youtuber_blogger_urls = yt_dlp_read_url_from_file_v3(url=channel_url, language=target_language)
        # 统计总时长
        total_duration = sum([int(duration_url.split(' ')[1].strip().split('.')[0]) for duration_url in target_youtuber_blogger_urls])
        print(total_duration) 
        if len(target_youtuber_blogger_urls) <= 0:
            logger.error("Scraper Pipeline > no watch urls to import.")
            # exit()
            continue
        try:
            # 使用多进程处理video_url_list入库 # 创建进程池
            with multiprocessing.Pool(5) as pool:
                # 将列表分成5个子集，分配给每个进程
                # chunks = np.array_split(target_youtuber_blogger_urls, 4)
                chunk_size = len(target_youtuber_blogger_urls) // 4
                chunks = [target_youtuber_blogger_urls[i:i + chunk_size] for i in range(0, len(target_youtuber_blogger_urls), chunk_size)]
                # print(chunks)
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
                    time.sleep(0.5)
                pool.close()
                pool.join()  # 等待所有进程结束
        except KeyboardInterrupt:
            # 捕获到 Ctrl+C 时，确保终止所有子进程
            logger.warning("KeyboardInterrupt detected, terminating pool...")
            pool.terminate()
            sys.exit()  # 退出主程序
            

if __name__ == '__main__':
    ytb_main()