import subprocess
import os
import re
from time import time
from database.ytb_model import Video

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
    :return: List[Video,Video]] - 返回包含视频网页链接和时长的列表.格式为   
        (Video(vid=None, position=1, source_id=UCgdiE5jT-77eUMLXn66NLCQ, source_type=3, source_link=https://www.youtube.com/watch?v=XYjL_pXK8V8, duration=328, cloud_type=0, cloud_path=None, language=None, status=0, `lock`=0, info={}))
    """
    # 目前下载的主要是 webpage_url 和 duration 俩个字段信息，使用 yt-dlp 命令获取视频网页链接和时长
    # yt-dlp --flat-playlist --print "%(webpage_url)s %(duration)s" --sleep-requests 2 -v https://www.youtube.com/@kinitv/videos
    command = f'yt-dlp --flat-playlist --print "%(webpage_url)s %(duration)s" --sleep-requests 2 -v {url}'
    output_lines = []
    # 使用 Popen 捕获 yt-dlp 输出
    # process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)
    # process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True, encoding="utf-8")
    for line in process.stdout:
        print(line, end='')
        if line.startswith("https://www.youtube.com"):
            line = str(line.strip().split('\n')[0])
            output_lines.append(line)
    # stdout, stderr = process.communicate()
    process.wait()

    # 错误检查
    if process.stderr:
        error_message = process.stderr.decode('utf-8').strip()
        raise ValueError(f"yt-dlp解析失败, {error_message}")
    
    output_list = []
    for line in output_lines:
        # 检查每行数据并解析网页链接和视频时长
        parts = line.split(' ')
        if len(parts) >= 3:
            video_url = parts[0]
            duration = int(float(parts[1])) if parts[1] != 'NA' else 0
            channel_id = parts[2]
            output_list.append(Video(source_link=video_url, duration=duration , source_id=channel_id, language=language, blogger_url=url))
        else:
            print(f"Warning: 无法解析数据行: '{line}'")
    print(f"共获取到 {len(output_list)} 条视频数据")
    return output_list

if __name__ == "__main__":
    # yt_dlp_read_url_from_file_v3(
    #     url="https://www.youtube.com/@Fei-zi/videos",
    #     language="yue"
    # )
    pass
# https://www.youtube.com/watch?v=S4e8ncrOKLo 658.0 UCgdiE5jT-77eUMLXn66NLCQ