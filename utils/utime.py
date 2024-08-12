# -*- coding: UTF8 -*-
import time
import random

# from utils.logger import init_logger
# logger = init_logger("utils/time")

def random_sleep(rand_range:int, rand_st:int):
    '''随机等待[rand_st, rand_st+rand_range]秒'''
    if rand_range < 1:
        rand_range = 5
    if rand_st < 1:
        rand_st = 5
    rand_range = random.randint(rand_st, rand_st + rand_range)
    # logger.info(f"random_sleep {rand_range} seconds")
    print(f"random_sleep > {rand_range} seconds")
    time.sleep(rand_range)
    return

def get_now_time_string():
    ''' 返回现在时间戳字符串 | 格式：%年%月%日-%时:%分:%秒 '''
    return time.strftime("%Y%m%d-%H:%M:%S", time.localtime())

def get_now_time_string_short():
    ''' 返回现在时间戳字符串 | 格式：%年%月%日%时%分%秒 '''
    return time.strftime("%Y%m%d%H%M%S", time.localtime())

def get_time_stamp()->int:
    ''' 获取当前时间戳 '''
    return int(time.time())

def parse_time_string_with_colon(time_str)->int:
    ''' 将时间字符串按照 : 分割, 换算秒数 '''
    ret_sec = 0
    try:
        if ":" in time_str:
            time_parts = list(map(int, time_str.split(':')))

            # 根据长度判断输入的格式
            if len(time_parts) == 3:
                hours, minutes, seconds = time_parts
            elif len(time_parts) == 2:
                hours = 0
                minutes, seconds = time_parts
            elif len(time_parts) == 1:
                hours = 0
                minutes = 0
                seconds = time_parts[0]
            else:
                raise ValueError("Invalid time format")

            # 计算总秒数
            ret_sec = hours * 3600 + minutes * 60 + seconds
        else:
            ret_sec = int(time_str)
    except Exception as e:
        print(f"parse_time_string_with_colon {time_str} failed", e.__str__)
    finally:
        return ret_sec

def format_second_to_time_string(sec=0.0) -> str:
    ''' 转化秒数为时间字符串 '''
    if sec < 60:
        return f"{sec:.2f}秒"
    elif sec < 3600:
        minutes = int(sec // 60)
        seconds = sec % 60
        return f"{minutes}分钟{seconds:.2f}秒" if seconds > 0 else f"{minutes}分钟"
    else:
        hours = int(sec // 3600)
        minutes = int((sec % 3600) // 60)
        seconds = sec % 60
        time_str = f"{hours}小时"
        if minutes > 0:
            time_str += f"{minutes}分钟"
        if seconds > 0:
            time_str += f"{seconds:.2f}秒"
        return time_str