from dotenv import load_dotenv
load_dotenv()

from uuid import uuid4
from os import getpid, getenv
from sys import argv
from time import sleep, time
from utils import logger as ulog
from handler.yt_dlp_save_url_to_file import yt_dlp_read_url_from_file_v3
from utils.lark import alarm_lark_text
from utils.utime import get_now_time_string, format_second_to_time_string

# youtube_search_python
def main():
    from ytb_scrape_ytb_search import scrape_pipeline
    # logger = ulog.init_logger("main")

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
    # logger = ulog.init_logger("main_v2")

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
                target_youtuber_blogger_urls = scrape_ytb_channel_data(pid=pid,channel_url=channel_url, language=language)
                if len(target_youtuber_blogger_urls) <= 0:
                    continue
                for watch_url in target_youtuber_blogger_urls:
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
    from ytb_scrape_yeb_dlp_pip import import_data_to_db_pip
    from multiprocessing import Pool

    logger = ulog.init_logger("main_v3")
    if len(argv) <= 2:
        print("[ERROR] Too less arguments of urls to scrape.")
        print("[INFO] Example: python ytb_scrape_arg.py yue https://www.youtube.com/@video-df1md")
        exit(0)
    
    pid = getpid()  # 捕获进程
    task_id = str(uuid4())  # 获取任务ID
    target_language = argv[1]
    opt = input(f"[DEBUG] Check your input, language:{target_language}, url:{argv[2:]}. Continue?(Y/N)")
    if opt not in ["Y", "y", "YES", "yes"]:
        logger.error("[ERROR] please input target language.")
        exit(1)

    for channel_url in argv[2:]:
        try:
            # 解析数据
            time_1 = time()
            logger.info(f"main_v3 > 当前正在解析频道: {channel_url} | 语言：{target_language}")
            target_youtuber_blogger_urls = yt_dlp_read_url_from_file_v3(url=channel_url, language=target_language)
            time_2 = time()
            spend_scrape_time =  time_2 - time_1
            logger.info(f"main_v3 > 解析{channel_url}完毕, 花费{format_second_to_time_string(spend_scrape_time)}")
            if len(target_youtuber_blogger_urls) <= 0:
                logger.error("main_v3 > 无资源导入")
                # continue
                raise ValueError("target_youtuber_blogger_urls 为空")
        except KeyboardInterrupt:
            logger.warning("KeyboardInterrupt detected, terminating pool...")
            exit(1)
        except Exception as e:
            # continue_fail_count += 1
            logger.error(f"main_v3 > 频道获取链接失败, {e}")
            logger.error(e, stack_info=True)

            # alarm to Lark Bot
            now_str = get_now_time_string()
            notice_text = f"[Ytb Scraper | ERROR] 数据采集失败 \
                \n\t频道信息: {target_language} | {channel_url} \
                \n\t任务ID: {task_id} \
                \n\tError: {e} \
                \n\t通知时间: {now_str}"
            alarm_lark_text(webhook=getenv("NOTICE_WEBHOOK_ERROR"), text=notice_text)

        else:
            init_url = channel_url
            # 统计时长和数量
            total_duration = 0
            # total_duration = sum([int(duration_url.split(' ')[1].strip().split('.')[0]) for duration_url in target_youtuber_blogger_urls])
            total_count = len(target_youtuber_blogger_urls)
            logger.info(f"main_v3 > 频道:{channel_url}, 总资源数:{total_count}, 总时长:{total_duration}")

        try:
            time_3 = time()
            # 使用多进程处理入库
            # 创建进程池
            with Pool(4) as pool:
                # 将列表分成4个子集，分配给每个进程
                chunk_size = len(target_youtuber_blogger_urls) // 4
                chunks = [target_youtuber_blogger_urls[i:i + chunk_size] for i in range(0, len(target_youtuber_blogger_urls), chunk_size)]
                # print(chunks)
                # 如果列表的长度不是4的倍数，可能会有剩余的元素，我们将它们分配到最后一个子集中
                if len(chunks) < 4:
                    chunks.append(target_youtuber_blogger_urls[len(chunks)*chunk_size:])
                for i, chunk in enumerate(chunks):
                    # print(i,chunk)
                    pool.apply_async(import_data_to_db_pip, (pid, tuple(chunk), i, total_duration, total_count, init_url, 0.0, task_id, target_language))
                    sleep(10)
                pool.close()
                pool.join()  # 等待所有进程结束
            time_4 = time()
            spend_import_time =  time_4 - time_3
        except KeyboardInterrupt:
            # 捕获到 Ctrl+C 时，确保终止所有子进程
            logger.warning("KeyboardInterrupt detected, terminating pool...")
            pool.terminate()
            print("All processes have been terminated.")
            exit(1)
        except Exception as e:
            # continue_fail_count += 1
            logger.error(f"main_v3 > 入库失败, {e}")
            logger.error(e, stack_info=True)

            # alarm to Lark Bot
            now_str = get_now_time_string()
            notice_text = f"[Ytb Scraper | ERROR] 数据入库失败 \
                \n\t频道信息: {target_language} | {channel_url} \
                \n\t任务ID: {task_id} \
                \n\tError: {e} \
                \n\t通知时间: {now_str}"
            alarm_lark_text(webhook=getenv("NOTICE_WEBHOOK_ERROR"), text=notice_text)
        else:
            # alarm to Lark Bot
            now_str = get_now_time_string()
            notice_text = f"[Ytb Scraper | SUCCESS] 频道数据采集入库成功 \
                \n\t频道信息: {target_language} | {channel_url} \
                \n\t任务ID: {task_id} \
                \n\t数据总数量: {total_count} \
                \n\t数据总时长: {total_duration} \
                \n\t采集时间: {format_second_to_time_string(spend_scrape_time)} \
                \n\t入库时间: {format_second_to_time_string(spend_import_time)} \
                \n\t通知时间: {now_str}"
            alarm_lark_text(webhook=getenv("NOTICE_WEBHOOK_ERROR"), text=notice_text)

if __name__ == "__main__":
    main_v3()