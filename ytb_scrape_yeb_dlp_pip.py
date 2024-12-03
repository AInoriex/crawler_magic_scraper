# 加载.env文件
from dotenv import load_dotenv
load_dotenv()

import multiprocessing
import sys
import uuid
from os import getenv, getpid
from time import sleep, time
from database import ytb_api, ytb_model
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

target_language = "yue_text"

# 正在处理
CHANNEL_URL_LIST = ["https://www.youtube.com/@%E5%A8%9C%E5%A8%9C%E5%BE%88%E7%A1%AC/videos"]

def import_data_to_db_pip(video_urls:ytb_model.Video, pool_num:int, pid:int, task_id:str):
    """
    油管信息导入数据库

    :param video_urls: 视频信息 Video(tuple, tuple, ...)
    :param pool_num: 线程编号
    :param spend_scrape_time: 采集总时间
    :param pid: 进程ID
    :param task_id: 任务ID
    """
    
    # 数据导入数据库
    index = 0
    for video_info in video_urls:
        print(video_info)
        # print(video_info.source_link, video_info.duration, video_info.source_id)
        # if duration == 'NA':
        #     duration = int(0)
        index += 1
        try:
            logger.info(f"import_data_to_db_pip > 第{pool_num}个进程, 开始处理第{index}个数据: {video_info.source_link}")
            time_st = time()
            # 格式化视频信息
            # if video_tuple is None:
            #     logger.error("Scraper Pipeline > video_url invalid")
            #     break
            video_object = get_ytb_blogger_url(
                # file_name = channel_url_name,
                video_url=video_info.source_link,
                language=video_info.language,
                duration=video_info.duration,
                task_id=task_id,
                source_id=video_info.source_id
            )

            # 将数据更新入库
            ytb_api.create_video(video_object)
            # ytb_api_v2.sign_database(video_object)
            sleep(0.5)

            # 日志记录
            time_ed = time()
            spend_time = time_ed - time_st
            logger.info(f"import_data_to_db_pip > 第{pool_num}个进程, 处理第{index}个数据: {video_object.source_link} 完毕, 花费时间: {spend_time} seconds")
            
            # alarm to Lark Bot
            notice_text = f"[Youtube Scraper | DEBUG] 数据已入库. \
                \n\t进程ID: {pid} \
                \n\t任务ID: {task_id} \
                \n\t频道信息: {video_object.language} | {video_object.blogger_url} \
                \n\t线程信息: {f'第{pool_num}个进程, 处理第{index}个数据: {video_object.source_link}'} \
                \n\t共处理了{format_second_to_time_string(spend_time)} \
                \n\tIP: {local_ip} | {public_ip} \
                \n\tTime: {get_now_time_string()}"
            alarm_lark_text(webhook=getenv("NOTICE_WEBHOOK_DEBUG"), text=notice_text)
        except Exception as e:
            # continue_fail_count += 1
            logger.error(f"import_data_to_db_pip > 第{pool_num}个进程, 处理第{index}个数据 {video_urls.blogger_object.source_link} 失败")
            logger.error(e, stack_info=True)
            # alarm to Lark Bot
            notice_text = f"[Youtube Scraper | ERROR] 数据入库失败 \
                \n\t进程ID: {pid} \
                \n\t任务ID: {task_id} \
                \n\t频道信息: {video_object.language} | {video_object.blogger_url} \
                \n\t线程信息: {f'我是第{pool_num}个进程, 处理第{index}个数据: {video_object.source_link}'} \
                \n\tError: {e} \
                \n\tIP: {local_ip} | {public_ip} \
                \n\tTime: {get_now_time_string()}"
            alarm_lark_text(webhook=getenv("NOTICE_WEBHOOK_ERROR"), text=notice_text)
            # 失败过多直接退出
            # if continue_fail_count > LIMIT_FAIL_COUNT:
            #     logger.error(f"Scraper Pipeline > pid {pid} unexpectable exit beceuse of too much fail count: {continue_fail_count}")
            #     exit(1)
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
            [int(video_info.duration) 
             for video_info in target_youtuber_channel_urls])
        # 统计总视频数量
        total_count = len(target_youtuber_channel_urls)
        print(total_duration, total_count)
        logger.info(f"Scraper Pipeline > 频道:{channel_url}, 总资源数:{total_count}, 总时长:{total_duration}")
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
                    # print(chunk)
                    # 将各项参数封装为Video对象
                    # video_chunk = ytb_dlp_format_video(channel_url, chunk, target_language)
                    pool.apply_async(import_data_to_db_pip, (chunk, pool_num, pid, task_id))
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
                alarm_lark_text(webhook=getenv("NOTICE_WEBHOOK"), text=notice_text)
        except KeyboardInterrupt:
            # 捕获到 Ctrl+C 时，确保终止所有子进程
            logger.warning("KeyboardInterrupt detected, terminating pool...")
            pool.terminate()
            sys.exit()  # 退出主程序
            

if __name__ == '__main__':
    ytb_main()