# 油管视频URL采集器

## Description

​	本项目用于采集油管视频页url，目前只支持批量获取油管博主主页下所有视频。


## Usage

1. 安装第三方依赖包

   ```
   pip install -r requirements.txt
   ```

2. 创建 `.env` 配置文件在根目录，样例如下

   ```
   # .env
   
   # COMMON
   DEBUG=True
   LOG_PATH=logs
   DOWNLOAD_PATH=download
   TMP_FOLDER_PATH=temp
   PROCESS_NUM=3
   LIMIT_FAIL_COUNT=5
   LIMIT_LAST_COUNT=10
   
   # DATABASE
   DATABASE_GET_API=https://xxx/ytb_get_download_list
   DATABASE_UPDATE_API=https://xxx/ytb_update_status
   DATABASE_CREATE_API=https://xxx/ytb_create_record
   
   # LARK
   NOTICE_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/xxx-xxx

   # Youtube
   YTB_MAX_RETRY=3
   ```

3. 运行程序

   1. 本地代码执行
   
      - 修改`ytb_scrape_yeb_dlp_pip` 代码， 填写`CHANNEL_URL_LIST` 油管链接 和 `target_language` 语言编码（详见3.3）
   
      - 运行程序
   
         ```python
         python ytb_scrape_yeb_dlp_pip.py
         ```
   
   2.  命令行执行
   
     - 执行以下命令，参数1：语言编码（详见3.3）；参数2-N：n个油管链接
   
       ```python
       # exp01 语言:马来语 Youtuber:AlyssaDezekTV
       python ytb_scrape_v2_arg.py ms https://www.youtube.com/@AlyssaDezekTV/videos
           
       # exp02 语言:德语 Youtuber:AlyssaDezekTV
       python ytb_scrape_v2_arg.py de https://www.youtube.com/@gronkh/videos
       ```
   
   3. 附：语言编码规范参考
   
      - 优先使用：[ISO 639-1 - 维基百科，自由的百科全书](https://zh.wikipedia.org/wiki/ISO_639-1)
      - [ISO 639-3 - 维基百科，自由的百科全书](https://zh.wikipedia.org/wiki/ISO_639-3)



## 特别鸣谢

   [alexmercerind/youtube-search-python](https://github.com/alexmercerind/youtube-search-python)

   [yt-dlp/yt-dlp: A feature-rich command-line audio/video downloader](https://github.com/yt-dlp/yt-dlp)
​	