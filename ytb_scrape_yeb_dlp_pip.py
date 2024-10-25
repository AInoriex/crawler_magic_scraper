# 加载.env文件
from dotenv import load_dotenv
load_dotenv()

import multiprocessing
import sys
import uuid
from os import getenv, getpid
from time import sleep, time
from database import ytb_api
from handler.yt_dlp import get_ytb_blogger_url
from handler.yt_dlp_save_url_to_file import yt_dlp_read_url_from_file_v3
from utils import logger
from utils.ip import get_local_ip, get_public_ip
from utils.lark import alarm_lark_text
from utils.utime import get_now_time_string, format_second_to_time_string

# 初始化
local_ip = get_local_ip()
public_ip = get_public_ip()
continue_fail_count = 0 # 连续失败的任务个数

LIMIT_FAIL_COUNT = int(getenv("LIMIT_FAIL_COUNT"))
# LIMIT_FAIL_COUNT = 10
''' 处理失败任务限制数 '''
LIMIT_LAST_COUNT = int(getenv("LIMIT_LAST_COUNT"))
# LIMIT_LAST_COUNT = 100
''' 连续处理任务限制数 '''

target_language = "fr"
# https://www.youtube.com/@FRANCE24/videos
CHANNEL_URL_LIST = ["https://www.youtube.com/@franceinfo/videos","https://www.youtube.com/c/LittleAngelFran%C3%A7ais/videos",
                    "https://www.youtube.com/@Kidibli_fr/videos", "https://www.youtube.com/@LeFatShow/videos", "https://www.youtube.com/@FuriousJumper/videos",
                    "https://www.youtube.com/@SYMPA_FR/videos","https://www.youtube.com/@Valouzz_/videos","https://www.youtube.com/@DavidLafargePokemon/videos",
                    "https://www.youtube.com/@joueurdugrenier/videos","https://www.youtube.com/@VodKprod/videos","https://www.youtube.com/@Amixem/videos"]
# CHANNEL_URL_LIST = ["https://www.youtube.com/@Sciencebestiale"]

def import_data_to_db_pip(pid:int, watch_urls:tuple, pool_num:int, duration:int, count:int, channel_url:str, spend_scrape_time:float, task_id:str, language="unknown"):
    """
    油管信息导入数据库

    :param pid: 进程ID
    :param watch_urls: 视频信息 tuple(tuple, tuple, ...)
    :param pool_num: 线程编号
    :param duration: 采集时长
    :param count: 共采集的视频数量
    :param init_url: 任务的开始URL
    :param spend_scrape_time: 采集总时间
    :param task_id: 任务ID
    :param language: 语言
    """
    logger = logger.init_logger("import_data_to_db_pip")

    # 频道通知开始
    notice_text = f"[Youtube Scraper | DEBUG] 第{pool_num}个线程开始采集. \
        \n\t频道URL: {channel_url} \
        \n\t语言: {language} \
        \n\t入库视频数量: {count} \
        \n\t入库时长(小时):{round((duration / 3600),3)} \
        \n\t任务ID: {task_id} \
        \n\t任务处理时间: {format_second_to_time_string(spend_scrape_time)} \
        \n\t通知时间: {get_now_time_string()}"
    alarm_lark_text(webhook=getenv("NOTICE_WEBHOOK_DEBUG"), text=notice_text)

    # 数据导入数据库
    for index, video_tuple in enumerate(watch_urls):
        try:
            logger.info(f"import_data_to_db_pip > 第{pool_num}个进程, 开始处理第{index}个数据: {video_tuple}")
            time_st = time()
            # 格式化视频信息
            # if video_tuple is None:
            #     logger.error("Scraper Pipeline > video_url invalid")
            #     break
            video_object = get_ytb_blogger_url(
                blogger_url=video_tuple,
                language=language,
                task_id=task_id
            )

            # 将数据更新入库
            ytb_api.create_video(video_object)
            # ytb_api_v2.sign_database(video_object)
            sleep(0.5)

            # 日志记录
            time_ed = time()
            spend_time = time_ed - time_st
            logger.info(f"import_data_to_db_pip > 第{pool_num}个进程, 处理第{index}个数据: {video_tuple} 完毕, 花费时间: {spend_time} seconds")
            
            # alarm to Lark Bot
            notice_text = f"[Youtube Scraper | DEBUG] 数据已入库. \
                \n\t进程ID: {pid} \
                \n\t频道信息: {language} | {channel_url} \
                \n\t线程信息: {f'第{pool_num}个进程, 处理第{index}个数据: {video_tuple}'} \
                \n\t共处理了{format_second_to_time_string(spend_time)} \
                \n\t任务ID: {task_id} \
                \n\tIP: {local_ip} | {public_ip} \
                \n\tTime: {get_now_time_string()}"
            alarm_lark_text(webhook=getenv("NOTICE_WEBHOOK_DEBUG"), text=notice_text)
        except Exception as e:
            # continue_fail_count += 1
            logger.error(f"import_data_to_db_pip > 第{pool_num}个进程, 处理第{index}个数据 {video_tuple} 失败")
            logger.error(e, stack_info=True)

            # alarm to Lark Bot
            notice_text = f"[Youtube Scraper | ERROR] 数据入库失败 \
                \n\t进程ID: {pid} \
                \n\t频道信息: {language} | {channel_url} \
                \n\t线程信息: {f'我是第{pool_num}个进程, 处理第{index}个数据: {video_tuple}'} \
                \n\t任务ID: {task_id} \
                \n\tError: {e} \
                \n\tIP: {local_ip} | {public_ip} \
                \n\tTime: {get_now_time_string()}"
            alarm_lark_text(webhook=getenv("NOTICE_WEBHOOK_ERROR"), text=notice_text)
            # 失败过多直接退出
            # if continue_fail_count > LIMIT_FAIL_COUNT:
            #     logger.error(f"Scraper Pipeline > pid {pid} unexpectable exit beceuse of too much fail count: {continue_fail_count}")
            #     exit(1)
            continue

        except KeyboardInterrupt:
            logger.warning(f"Scraper Pipeline > pid {pid} interrupted processing, exit.")
            # pool_num.terminate()  # 直接终止所有子进程
            # sys.exit(1)  # 退出程序
            raise KeyboardInterrupt
        finally:
            #sleep(1)
            pass

def ytb_main():
    logger = logger.init_logger("ytb_main")
    pid = getpid()
    task_id = str(uuid.uuid4())
    if target_language == "":
        logger.error("[ERROR] please input target language.")
        exit()
    for channel_url in CHANNEL_URL_LIST:
        logger.info(f"Scraper Pipeline > 当前处理频道: {channel_url} | 语言：{target_language}")
        target_youtuber_blogger_urls = yt_dlp_read_url_from_file_v3(url=channel_url, language=target_language)
        if len(target_youtuber_blogger_urls) <= 0:
            logger.error("Scraper Pipeline > no watch urls to import.")
            # exit()
            continue
        total_duration = 0
        # total_duration = sum([int(duration_url.split(' ')[1].strip().split('.')[0]) for duration_url in target_youtuber_blogger_urls])
        total_count = len(target_youtuber_blogger_urls)
        init_url = channel_url

        logger.info(f"Scraper Pipeline > 频道:{channel_url}, 总资源数:{total_count}, 总时长:{total_duration}")
        try:
            # 使用多进程处理入库
            # 创建进程池
            with multiprocessing.Pool(4) as pool:
                # 将列表分成4个子集，分配给每个进程
                chunk_size = len(target_youtuber_blogger_urls) // 4
                chunks = [target_youtuber_blogger_urls[i:i + chunk_size] for i in range(0, len(target_youtuber_blogger_urls), chunk_size)]
                # print(chunks)
                # 如果列表的长度不是4的倍数，可能会有剩余的元素，我们将它们分配到最后一个子集中
                if len(chunks) < 4:
                    chunks.append(target_youtuber_blogger_urls[len(chunks)*chunk_size:])
                for i, chunk in enumerate(chunks):
                    print(i,chunk)
                    # TODO tuple format to video class
                    pool.apply_async(import_data_to_db_pip, (pid, tuple(chunk), i, total_duration, total_count, init_url, 0.0, task_id, target_language))
                    sleep(30)
                pool.close()
                pool.join()  # 等待所有进程结束
        except KeyboardInterrupt:
            # 捕获到 Ctrl+C 时，确保终止所有子进程
            logger.warning("KeyboardInterrupt detected, terminating pool...")
            pool.terminate()
            sys.exit()  # 退出主程序
            

if __name__ == '__main__':
    ytb_main()