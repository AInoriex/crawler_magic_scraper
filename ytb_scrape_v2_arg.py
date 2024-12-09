from dotenv import load_dotenv
load_dotenv()

from uuid import uuid4
from os import getpid, getenv
from sys import argv
from time import sleep, time
from traceback import format_exc
from utils.logger import logger
from utils.utime import get_now_time_string, format_second_to_time_string
from utils.lark import alarm_lark_text
from utils.ip import get_local_ip, get_public_ip

# 初始化
local_ip = get_local_ip()
public_ip = get_public_ip()
process_num = int(getenv("PROCESS_NUM"))

# youtube_search_python
def main():
    from ytb_scrape_ytb_search import scrape_pipeline

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
        print(f"[EXIT] You input {opt}. Bye!")
        exit()

# yt-dlp
def main_v2():
    """
    通过命令行获取博主链接并写入txt文本,读取文本入库
    """
    from ytb_scrape_yt_dlp import scrape_ytb_channel_data, import_data_to_db

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
                target_youtuber_channel_urls = scrape_ytb_channel_data(pid=pid,channel_url=channel_url, language=language)
                if len(target_youtuber_channel_urls) <= 0:
                    continue
                for watch_url in target_youtuber_channel_urls:
                    import_data_to_db(pid, watch_url, language=language)
                    print(f"{count} | {watch_url} 处理完毕")
                    count += 1
                    sleep(0.5)
    else:
        print(f"You input {opt}. Bye!")
        exit()

# yt-dlp
def main_v3():
    """
    通过命令行获取博主链接并对同一对象多进程入库
    """
    from multiprocessing import Pool
    from handler.yt_dlp_save_url_to_file import yt_dlp_read_url_from_file_v3
    from ytb_scrape_yeb_dlp_pip import import_data_to_db_pip

    pid = getpid()
    task_id = str(uuid4())  # 生成任务ID
    if len(argv) <= 2:
        print("[ERROR] Too less arguments of urls to scrape.")
        print("[INFO] Example: python ytb_scrape_arg.py yue https://www.youtube.com/@video-df1md")
        exit(0)
    target_language = argv[1]
    print("请检查输入信息是否正确：")
    logger.info(f"任务ID:{task_id} | language:{target_language}, url:{argv[2:]}")
    opt = input(f"\nContinue? (Y/N)")
    if opt not in ["Y", "y", "YES", "yes"]:
        logger.error("[EXIT] bye.")
        exit(1)
    
    for channel_url in argv[2:]:
        # 判断url有效性
        if channel_url == "":
            logger.info(f"main_v3 > [!] url无效，跳过处理")
            continue
        try:
            # 解析数据
            logger.info(f"main_v3 > 当前正在解析频道: {channel_url} | 语言:{target_language}")
            time_1 = time()
            video_list = yt_dlp_read_url_from_file_v3(url=channel_url, language=target_language)
            
            logger.info(f"main_v3 > 解析{channel_url}完毕, 花费{format_second_to_time_string(time()-time_1)}")
            if len(video_list) <= 0:
                logger.error("main_v3 > 无视频数据说导入")
                raise ValueError("video_list 为空")

            # 统计总时长
            total_duration = sum([v.duration for v in video_list])
            # 统计总视频数
            total_count = len(video_list)
            logger.info(f"main_v3 > 频道:{channel_url}, 总视频数:{total_count}, 总时长:{total_duration}")
        except KeyboardInterrupt:
            logger.error("KeyboardInterrupt 退出解析...")
            exit(1)
        except Exception as e:
            logger.error(f"main_v3 > 频道解析链接失败, {e}")
            # logger.error(e, stack_info=True)
            # alarm to Lark Bot
            notice_text = f"[Ytb Scraper | ERROR] 数据采集失败 \
                \n\t频道信息: {target_language} | {channel_url} \
                \n\t任务ID: {task_id} \
                \n\tError: {e} \
                \n\t通知时间: {get_now_time_string()}"
            alarm_lark_text(webhook=getenv("NOTICE_WEBHOOK_ERROR"), text=notice_text)
            continue

        logger.info(f"main_v3 > 频道: {channel_url} | 语言:{target_language} 准备入库 | 进程数:{process_num}")
        sleep(5)
        try:
            # 使用多进程处理入库
            time_2 = time()
            pool = Pool(process_num)
            # 将列表分成process_num个子集，分配给每个进程
            chunk_size = len(video_list) // process_num
            chunks = [video_list[i:i + chunk_size] for i in range(0, len(video_list), chunk_size)]
            # print(chunks)
            # 列表的长度可能会有剩余的元素，我们将它们分配到最后一个子集中
            if len(chunks) < process_num:
                chunks.append(video_list[len(chunks)*chunk_size:])
            # 启动进程池中的进程，传递各自的子集和进程ID
            for pool_num, chunk in enumerate(chunks):
                pool.apply_async(import_data_to_db_pip, (chunk, pool_num, pid, task_id))
                sleep(5)
            pool.close()
            pool.join()  # 等待所有进程结束

            # alarm to Lark Bot
            notice_text = f"[Ytb Scraper | SUCCESS] 频道数据采集入库成功 \
                \n\t频道信息: {target_language} | {channel_url} \
                \n\t任务ID: {task_id} \
                \n\t数据总数量: {total_count} \
                \n\t数据总时长: {format_second_to_time_string(total_duration)} \
                \n\t采集花费: {format_second_to_time_string(time_2 - time_1)} \
                \n\t入库花费: {format_second_to_time_string(time() - time_2)} \
                \n\t处理花费: {format_second_to_time_string(time() - time_1)} \
                \n\t通知时间: {get_now_time_string()}"
            alarm_lark_text(webhook=getenv("NOTICE_WEBHOOK_INFO"), text=notice_text)
        except KeyboardInterrupt:
            logger.error("KeyboardInterrupt 退出信息入库...")
            pool.terminate()
            exit(1)
        except Exception as e:
            logger.error(f"main_v3 > 入库失败, {e}")
            logger.error(format_exc())

            # alarm to Lark Bot
            notice_text = f"[Ytb Scraper | ERROR] 数据入库失败 \
                \n\t频道信息: {target_language} | {channel_url} \
                \n\t任务ID: {task_id} \
                \n\tError: {e} \
                \n\t通知时间: {get_now_time_string()}"
            alarm_lark_text(webhook=getenv("NOTICE_WEBHOOK_ERROR"), text=notice_text)
            logger.error(notice_text)

if __name__ == "__main__":
    main_v3()