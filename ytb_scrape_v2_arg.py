from dotenv import load_dotenv
load_dotenv()

from uuid import uuid4
from os import getpid, getenv
from sys import argv
from time import sleep, time
from utils import logger as ulog
from handler.yt_dlp_save_url_to_file import yt_dlp_read_url_from_file_v3
from handler.yt_dlp import ytb_dlp_format_video
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
    from ytb_scrape_yeb_dlp_pip import import_data_to_db_pip
    from multiprocessing import Pool

    logger = ulog.init_logger("main_v3")
    pid = getpid()
    task_id = str(uuid4())  # 生成任务ID

    if len(argv) <= 2:
        print("[ERROR] Please check your arguments to scrape.")
        print("Example: python ytb_scrape_arg.py yue https://www.youtube.com/@video-df1md")
        exit(0)
    target_language = argv[1]
    logger.info(f"Task ID:{task_id} | Check your input, language:{target_language}, url:{argv[2:]}")
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
            logger.info(f"main_v3 > 当前正在解析频道: {channel_url} | 语言：{target_language}")
            time_1 = time()
            target_youtuber_channel_urls = yt_dlp_read_url_from_file_v3(url=channel_url, language=target_language)
            time_2 = time()
            spend_scrape_time =  time_2 - time_1  # 采集总时间
            logger.info(f"main_v3 > 解析{channel_url}完毕, 花费{format_second_to_time_string(spend_scrape_time)}")
            if len(target_youtuber_channel_urls) <= 0:
                logger.error("main_v3 > 无资源导入")
                raise ValueError("target_youtuber_channel_urls 为空")
        except KeyboardInterrupt:
            logger.warning("KeyboardInterrupt detected, terminating pool...")
            exit(1)
        except Exception as e:
            logger.error(f"main_v3 > 频道解析链接失败, {e}")
            logger.error(e, stack_info=True)

            # alarm to Lark Bot
            notice_text = f"[Ytb Scraper | ERROR] 数据采集失败 \
                \n\t频道信息: {target_language} | {channel_url} \
                \n\t任务ID: {task_id} \
                \n\tError: {e} \
                \n\t通知时间: {get_now_time_string()}"
            alarm_lark_text(webhook=getenv("NOTICE_WEBHOOK_ERROR"), text=notice_text)
            continue
        else:
            # 统计总时长
            total_duration = sum(
                [float(duration_url[1]) 
                for duration_url in target_youtuber_channel_urls 
                if 'NA' not in duration_url])
            # 统计总视频数量
            total_count = len(target_youtuber_channel_urls)
        finally:
            sleep(1)

        try:
            # 使用多进程处理入库
            logger.info(f"main_v3 > 频道: {channel_url} | 语言：{target_language} 准备入库")
            with Pool(5) as pool:
                # 将列表分成5个子集，分配给每个进程
                # chunks = np.array_split(target_youtuber_channel_urls, 5)
                chunk_size = len(target_youtuber_channel_urls) // 5
                chunks = [target_youtuber_channel_urls[i:i + chunk_size] for i in range(0, len(target_youtuber_channel_urls), chunk_size)]
                # 列表的长度可能会有剩余的元素，分配到最后一个子集中
                if len(chunks) < 5:
                    chunks.append(target_youtuber_channel_urls[len(chunks)*chunk_size:])
                # 启动进程池中的进程，传递各自的子集和进程ID
                for pool_num, chunk in enumerate(chunks):
                    # 将各项参数封装为Video对象
                    video_chunk = ytb_dlp_format_video(channel_url, chunk, target_language)
                    pool.apply_async(import_data_to_db_pip, (video_chunk, pool_num, pid, task_id))
                    sleep(10)
                pool.close()
                pool.join()  # 等待所有进程结束
            logger.info(f"main_v3 > 频道: {channel_url} | 语言：{target_language} 入库完成")
        except KeyboardInterrupt:
            # 捕获到 Ctrl+C 时，确保终止所有子进程
            logger.warning("KeyboardInterrupt detected, terminating pool...")
            pool.terminate()
            print("All processes have been terminated.")
            exit(1)
        except Exception as e:
            logger.error(f"main_v3 > 入库失败, {e}")
            logger.error(e, stack_info=True)

            # alarm to Lark Bot
            notice_text = f"[Ytb Scraper | ERROR] 数据入库失败 \
                \n\t频道信息: {target_language} | {channel_url} \
                \n\t任务ID: {task_id} \
                \n\tError: {e} \
                \n\t通知时间: {get_now_time_string()}"
            alarm_lark_text(webhook=getenv("NOTICE_WEBHOOK_ERROR"), text=notice_text)
        else:
            # alarm to Lark Bot
            notice_text = f"[Ytb Scraper | SUCCESS] 频道数据采集入库成功 \
                \n\t频道信息: {target_language} | {channel_url} \
                \n\t任务ID: {task_id} \
                \n\t数据总数量: {total_count} \
                \n\t数据总时长: {total_duration} \
                \n\t解析时长: {format_second_to_time_string(spend_scrape_time)} \
                \n\t处理总时长: {format_second_to_time_string(time() - time_1)} \
                \n\t通知时间: {get_now_time_string()}"
            alarm_lark_text(webhook=getenv("NOTICE_WEBHOOK_ERROR"), text=notice_text)
        finally:
            sleep(1)

if __name__ == "__main__":
    main_v3()