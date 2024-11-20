from utils.utime import get_time_stamp
from requests import get, post
from uuid import uuid4
from database.ytb_model import Video
from json import dumps

import os
import pymysql

def sign_database(video:Video):
    '''创建ytb记录'''
      # 数据库配置
    db_config = {
        'user': os.getenv("USER"),
        'password': os.getenv("PASSWORD"),
        'host': os.getenv("HOST"),
        'database': os.getenv("DATABASE")
    }
    # 连接数据库
    db = pymysql.connect(**db_config)
    cursor = db.cursor()

    req = video.dict()

    # info_dict ={}
    # info_dict['cloud_save_path'] = ""
    # info = dumps(info_dict)
    # 入库(方法)
    vid = req.get('vid')
    position = req.get('position')
    source_type = req.get('source_type')
    source_link = str(req.get('source_link'))
    duration = int(req.get('duration'))
    cloud_type = int(req.get('cloud_type'))
    cloud_path = str(req.get('cloud_path'))
    language = str(req.get('language'))
    status = int(req.get('status'))
    lock = req.get('`lock`')
    info = req.get('info')
    source_id = req.get('source_id')

    insert_sql = 'INSERT INTO ytb_dlp (vid, position, source_type, source_link, duration, cloud_type, cloud_path, language, status, `lock`, info, source_id) \
      VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    values = (vid, position, source_type, source_link, duration, cloud_type, cloud_path, language, status, lock, info, source_id)
    cursor.execute(insert_sql, values)

    # 提交事务
    db.commit()

    # 关闭数据库
    cursor.close()
    db.close()
    
    return
