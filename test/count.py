import os

def count_txt(folder_path):
    '''统计总文件夹下所有txt文本的总时长和总数量'''
    count = int(0)
    time_sum = int(0)
    # 遍历文件夹中的所有txt文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):  # 只处理txt文件
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as f:
                for line in f:  # 逐行读取
                    parts = line.split(' ')
                    if len(parts) > 1:  # 确保至少有两个部分
                        duration_1 = parts[1].strip()
                        try:
                            duration_2 = int(duration_1.split('.')[0])  # 取整数部分
                            time_sum += duration_2
                        except ValueError:
                            print(f"Invalid duration format in line: {line.strip()}")  # 处理格式错误
    print(f"分钟{time_sum / 60}, 数量 {count}, 平均时长:{(time_sum / 60) / count} \n\n")
    return

def dirs(path_url):
    '''统计总文件夹下各个文本txt的具体时长和总数量'''
    if os.path.isdir(path_url):
        for filename in os.listdir(path_url):
            file_path = os.path.join(path_url, filename)
            print(os.path.abspath(file_path))  # 打印文件的绝对路径
            time_sum = int(0)
            count = int(0)
            with open(os.path.abspath(file_path), 'r') as f:
                while True:
                    link = f.readline()
                    if not link:  # 如果没有更多行，跳出循环
                        break
                    count += 1
                    duration_1 = link.split(' ')[1].strip()
                    try:
                        duration_2 = int(duration_1.split('.')[0])
                        time_sum += duration_2
                    except:
                        pass
            print(f"分钟{time_sum / 60}, 数量 {count}, 平均时长:{(time_sum / 60) / count} \n\n")
    return

def one_time_sum(file_path):
    '''对单个txt文本进行统计'''
    time_sum = int(0)
    count = int(0)
    with open(file_path, 'r') as f:
        while True:
            link = f.readline()
            if not link:  # 如果没有更多行，跳出循环
                break
            count += 1
            duration = int(link.split(' ')[1].strip().split('.')[0])
            time_sum += duration
        print(time_sum, time_sum / 60, time_sum / 3600, count)
    return
                

if __name__ == '__main__':
    
    # folder_paths = 'F:\crawler_magic_scraper\lang_ja\ja_hima72.txt'  # 注意使用双反斜杠或原始字符串
    # one_time_sum(folder_paths)

    # folder_path = 'F:\\crawler_magic_scraper\\lang_yue'  # 注意使用双反斜杠或原始字符串
    # count_txt(folder_path)

    path = 'F:\crawler_magic_scraper\lang_ja'
    dirs(path)