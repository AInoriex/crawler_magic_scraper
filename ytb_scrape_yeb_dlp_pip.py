# 加载.env文件
from dotenv import load_dotenv
load_dotenv()
from database import ytb_api, ytb_api_v2, ytb_init_video
from handler.yt_dlp_save_url_to_file import yt_dlp_read_url_from_file, yt_dlp_read_url_from_file_v2, yt_dlp_read_url_from_file_v3
from handler.yt_dlp import ytb_dlp_format_video, get_ytb_blogger_url
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
# import numpy as np
import sys
import uuid

# 初始化
logger = logger.init_logger("ytb_scrape_pip")
local_ip = get_local_ip()
public_ip = get_public_ip()
continue_fail_count = 0 # 连续失败的任务个数

LIMIT_FAIL_COUNT = int(os.getenv("LIMIT_FAIL_COUNT"))
# LIMIT_FAIL_COUNT = 10
''' 处理失败任务限制数 '''
LIMIT_LAST_COUNT = int(os.getenv("LIMIT_LAST_COUNT"))
# LIMIT_LAST_COUNT = 100
''' 连续处理任务限制数 '''

target_language = "yue_text"

# 正在处理
CHANNEL_URL_LIST = ["https://www.youtube.com/@Bobtivation/videos"]

def import_data_to_db_pip(video_urls:ytb_init_video.Video, pool_num:int, pid:int, task_id:str):
    """
    油管信息导入数据库

    :param video_urls: 视频信息 Video(tuple, tuple, ...)
    :param pool_num: 线程编号
    :param spend_scrape_time: 采集总时间
    :param pid: 进程ID
    :param task_id: 任务ID
    """
    # 大幅度需求
    # channel_url_name = video_urls.channel_url.split('@')[1].split(r"/")[0]
    # 频道通知开始
    # 数据导入数据库
    index = 0
    for video_url, duration, source_id in zip(video_urls.source_link, video_urls.duration, video_urls.source_id):
        if duration == 'NA':
            duration = int(0)
        index += 1
        try:
            logger.info(f"import_data_to_db_pip > 第{pool_num}个进程, 开始处理第{index}个数据: {video_url}")
            time_st = time.time()
            video_object = get_ytb_blogger_url(
                # file_name = channel_url_name,
                video_url=video_url,
                language=video_urls.language,
                duration=int(float(duration)),
                task_id=task_id,
                source_id=source_id
            )
            # 将数据更新入库
            # ytb_api.create_video(video_object)
            ytb_api_v2.sign_database(video_object)  # 用于测试
            time.sleep(0.5)

            # 日志记录
            time_ed = time.time()
            spend_time = time_ed - time_st
            logger.info(f"import_data_to_db_pip > 第{pool_num}个进程, 处理第{index}个数据: {video_url} 完毕, 花费时间: {spend_time} seconds")
            # alarm to Lark Bot
            now_str = get_now_time_string()
            notice_text = f"[Youtube Scraper | DEBUG] 数据已采集入库. \
                \n\t进程ID: {pid} \
                \n\t任务ID: {task_id} \
                \n\t频道信息: {video_urls.language} | {video_urls.channel_url} \
                \n\t线程信息: {f'第{pool_num}个进程, 处理第{index}个数据: {video_url}'} \
                \n\t共处理了{format_second_to_time_string(spend_time)} \
                \n\tIP: {local_ip} | {public_ip} \
                \n\tTime: {now_str}"
            alarm_lark_text(webhook=os.getenv("NOTICE_WEBHOOK"), text=notice_text)
        except Exception as e:
            # continue_fail_count += 1
            logger.error(f"import_data_to_db_pip > 第{pool_num}个进程, 处理第{index}个数据 {video_url} 失败, {e}")
            # logger.error(e, stack_info=True)
            # alarm to Lark Bot
            notice_text = f"[Youtube Scraper | ERROR] 数据采集入库失败 \
                \n\t进程ID: {pid} \
                \n\t任务ID: {task_id} \
                \n\t频道信息: {video_urls.language} | {video_urls.channel_url} \
                \n\t线程信息: {f'我是第{pool_num}个进程, 处理第{index}个数据: {video_url}'} \
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
        if not channel_url:  # 判断channel_url是否获取到链接
            logger.info("没有获取到链接")
        logger.info(f"Scraper Pipeline > {pid} 当前处理频道: {channel_url} | 语言：{target_language}")
        time_st = time.time()  # 获取采集数据的起始时间
        target_youtuber_channel_urls = yt_dlp_read_url_from_file_v3(url=channel_url, language=target_language)
        # print(len(target_youtuber_channel_urls))
        if len(target_youtuber_channel_urls) <= 0:
            logger.error("Scraper Pipeline > no watch urls to import.")
            # exit()
            continue
        # 统计总时长
        total_duration = sum(
            [float(duration_url[1]) 
             for duration_url in target_youtuber_channel_urls 
             if 'NA' not in duration_url])
        # 统计总视频数量
        total_count = len(target_youtuber_channel_urls)
        try:
            # 使用多进程处理video_url_list入库 # 创建进程池
            with multiprocessing.Pool(5) as pool:
                # 将列表分成5个子集，分配给每个进程
                # chunks = np.array_split(target_youtuber_blogger_urls, 5)
                chunk_size = len(target_youtuber_channel_urls) // 5
                chunks = [target_youtuber_channel_urls[i:i + chunk_size] for i in range(0, total_count, chunk_size)]
                # print(chunks)
                # 列表的长度可能会有剩余的元素，我们将它们分配到最后一个子集中
                if len(chunks) < 5:
                    chunks.append(target_youtuber_channel_urls[len(chunks)*chunk_size:])
                # 启动进程池中的进程，传递各自的子集和进程ID
                for pool_num, chunk in enumerate(chunks):
                    # 将各项参数封装为Video对象
                    video_chunk = ytb_dlp_format_video(channel_url, chunk, target_language)
                    pool.apply_async(import_data_to_db_pip, (video_chunk, pool_num, pid, task_id))
                    time.sleep(0.5)
                pool.close()
                pool.join()  # 等待所有进程结束
                time_ed = time.time()
                # 频道通知开始
                spend_scrape_time =  time_ed - time_st  # 采集总时间
                now_str = get_now_time_string()
                notice_text = f"[Youtube Scraper | DEBUG] 采集结束. \
                    \n\t频道URL: {channel_url} \
                    \n\t语言: {target_language} \
                    \n\t入库视频数量: {total_count} \
                    \n\t入库时长(小时):{round((total_duration / 3600),3)} \
                    \n\t入库时长(分钟):{round((total_duration / 60),3)} \
                    \n\t任务ID: {task_id} \
                    \n\t任务处理时间: {format_second_to_time_string(spend_scrape_time)} \
                    \n\t通知时间: {now_str}"
                alarm_lark_text(webhook=os.getenv("NOTICE_WEBHOOK_V2"), text=notice_text)
        except KeyboardInterrupt:
            # 捕获到 Ctrl+C 时，确保终止所有子进程
            logger.warning("KeyboardInterrupt detected, terminating pool...")
            pool.terminate()
            sys.exit()  # 退出主程序
            

if __name__ == '__main__':
    ytb_main()