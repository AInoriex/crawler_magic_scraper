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

   - 批量处理：需要填写 `target_youtuber_channel_urls` 批量博主主页链接 和 `target_language` 目标语言
   
      ```
      python ytb_scrape_yt_dlp.py
      ```
   
   - 单个处理：需要填写 `target_youtuber_channel_urls` 批量博主主页链接 和 `target_language` 目标语言
   
     ```
     python ytb_scrape_v2_arg.py ms https://www.youtube.com/@AlyssaDezekTV/videos
     ```


## 特别鸣谢

   [alexmercerind/youtube-search-python](https://github.com/alexmercerind/youtube-search-python)
   
   [yt-dlp/yt-dlp: A feature-rich command-line audio/video downloader](https://github.com/yt-dlp/yt-dlp)
​	