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

    :param url: (str) YouTube频道页面URL 
            exp. https://www.youtube.com/@Nhyxinhne/videos
    :param language:  (str, optional): 语言代码. Defaults to "".
    :return: 保存的文件的绝对路径
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
    使用 yt-dlp 从指定的 YouTube 频道页面 URL 中提取视频信息。

    :param url: YouTube 频道页面的 URL - 例如:https://www.youtube.com/@Nhyxinhne/videos
    :param language (str, optional) - 语言代码. Defaults to "".
    :return: List[Tuple[str, str]] - 返回包含视频网页链接和时长的列表.格式为 (webpage_url, duration)
    """
    # 目前下载的主要是 webpage_url 和 duration 俩个字段信息，使用 yt-dlp 命令获取视频网页链接和时长
    # command = ['yt-dlp', '--flat-playlist', '--print', '%(webpage_url)s %(duration)s', INPUT_URL]
    command = f'yt-dlp --flat-playlist --print \"%(webpage_url)s %(duration)s\" {url}'

    # 使用 Popen 捕获 yt-dlp 输出
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # 错误检查
    if stderr:
        error_message = stderr.decode('utf-8').strip()
        print(f"Error: {error_message}")
        return []  # 如果发生错误，返回空列表
    
   # 解析标准输出数据
    output_list = []
    output_lines = stdout.decode('utf-8').strip().split('\n')
    
    for line in output_lines:
        # 检查每行数据并解析网页链接和视频时长
        parts = line.split(' ')
        if len(parts) >= 2:
            video_url = parts[0]
            duration = parts[1]
            output_list.append((video_url, duration))
        else:
            print(f"Warning: 无法解析数据行: '{line}'")
    
    print(f"共获取到 {len(output_list)} 条视频数据")
    return output_list

if __name__ == "__main__":
    yt_dlp_read_url_from_file_v3(
        url="https://www.youtube.com/@user-qx9so9pk1m/videos",
        language="yue"
    )
    pass