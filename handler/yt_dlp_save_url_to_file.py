import subprocess
import os
import re
from time import time

def yt_dlp_read_url_from_file(TEXT:str, INPUT_URL:str) -> str:
    """通过命令行输入获取url   
                     
    :param: TEXT 保存的文本名字 格式为"{your_name}".txt     
    :param: INPUT_URL 采集的url eg https://www.youtube.com/@xxxxxx/videos...   
    :param: return 保存的文件的绝对路径
    """
    
    # https://www.youtube.com/@Nhyxinhne/videos

    # 目前下载的主要是 webpage_url 和 duration 俩个字段信息
    command = f'yt-dlp --flat-playlist --print-to-file "%(webpage_url)s %(duration)s" "{TEXT}.txt" "{INPUT_URL}"'
    subprocess.run(command, shell=True, capture_output=True, text=True)
    # 获取文件的绝对路径
    file_path = os.path.abspath(f"{TEXT}.txt")
    return file_path

def yt_dlp_read_url_from_file_v2(url:str, language:str="") -> str:
    """
    使用yt-dlp从url中读取视频信息

    :param: url (str): YouTube频道页面URL 
            exp. https://www.youtube.com/@Nhyxinhne/videos
    :param: language (str, optional): 语言代码. Defaults to "".
    :param: return 保存的文件的绝对路径
    """
    filename = url.split("@")[1].split(r"/")[0]
    if filename == "":
        raise KeyError("yt_dlp_read_url_from_file_v2 > 识别youtube url失败")
    if language != "":
        filename = f"{language}_{filename}"
    else:
        filename = f"{int(time())}_{filename}"
    # 目前下载的主要是 webpage_url 和 duration 俩个字段信息
    command = f'yt-dlp --flat-playlist --print-to-file "%(webpage_url)s %(duration)s" "{filename}.txt" "{url}"'
    print("当前执行命令：", command)
    subprocess.run(command, shell=True, capture_output=True, text=True)

    # 获取文件的绝对路径
    file_path = os.path.abspath(f"{filename}.txt")
    print(f"yt_dlp_read_url_from_file_v2 > 信息已写入 {file_path}")
    return file_path

def yt_dlp_read_url_from_file_v3(url:str, language:str="") -> list:
    """
    使用yt-dlp从url中读取视频信息

    :param: url (str): YouTube频道页面URL 
            exp. https://www.youtube.com/@Nhyxinhne/videos
    :param: language (str, optional): 语言代码. Defaults to "".
    :param: return: list对象
    """
    # 目前下载的主要是 webpage_url 和 duration 俩个字段信息
    # command = ['yt-dlp', '--flat-playlist', '--print', '%(webpage_url)s %(duration)s', INPUT_URL]
    command = f'yt-dlp --flat-playlist --print \"%(webpage_url)s %(duration)s\" {url}'
    # 使用 Popen 捕获 yt-dlp 输出
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    # 检查是否有错误
    if stderr:
        print(f"Error: {stderr.decode('utf-8')}")
    # 将标准输出解码成字符串
    output_lines_list = stdout.decode('utf-8').strip().split('\n')
    print('获取到', len(output_lines_list), '条数据')
    return output_lines_list

if __name__ == "__main__":
    # yt_dlp_read_url_from_file_v2(
    #     url="https://www.youtube.com/@RABSHA22",
    #     language=""
    # )
    pass