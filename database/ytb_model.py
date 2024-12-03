import time
import random
from os import getenv
from typing import List

TABLE_NAME = str("crawler_download_info")

# CREATE TABLE `crawler_download_info` (
#   `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增唯一ID',
#   `vid` varchar(255) NOT NULL COMMENT '资源ID',
#   `position` tinyint(4) DEFAULT '0' COMMENT '1: cas, 2: cuhk, 3: quwan',
#   `source_type` tinyint(4) NOT NULL COMMENT '1: Bilibili, 2: 喜马拉雅, 3: YouTube',
#   `source_link` text COMMENT '资源原始链接',
#   `duration` int(11) DEFAULT '0' COMMENT '原始长度(秒)',
#   `cloud_type` tinyint(4) DEFAULT '0' COMMENT '1: cos, 2: obs',
#   `cloud_path` varchar(255) DEFAULT '' COMMENT '云存储的路径',
#   `language` varchar(10) DEFAULT '' COMMENT '视频主要语言',
#   `status` tinyint(4) DEFAULT '0' COMMENT '0: 已爬取, 1: 本地已下载, 2: 已上传云端未处理, 3: 已处理未上传, 4: 已处理已上传',
#   `lock` tinyint(4) DEFAULT '0' COMMENT '处理锁',
#   `info` json DEFAULT NULL COMMENT 'meta数据',
#   `comment` text COMMENT '备注',
#   `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '数据创建时间',
#   `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '数据更新时间',
#   PRIMARY KEY (`id`),
#   UNIQUE KEY `UNQ_KEY` (`vid`) USING BTREE,
#   KEY `index_0` (`status`,`lock`),
#   KEY `index_1` (`status`,`language`,`lock`),
#   KEY `index_2` (`status`,`cloud_type`,`cloud_path`),
#   KEY `index_3` (`language`,`status`,`lock`),
#   KEY `index_4` (`source_type`,`status`,`lock`)
# ) ENGINE=InnoDB AUTO_INCREMENT=5020 DEFAULT CHARSET=utf8mb4 COMMENT='爬虫数据采集记录表';

# CREATE TABLE `crawler_download_info` (
#   `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增唯一ID',
#   `vid` varchar(255) NOT NULL COMMENT '资源ID',
#   `position` tinyint(4) DEFAULT '0' COMMENT '1: cas, 2: cuhk, 3: quwan',
#   `source_type` tinyint(4) NOT NULL COMMENT '1: Bilibili, 2: 喜马拉雅, 3: YouTube',
#   `source_link` text COMMENT '资源原始链接',
#   `duration` int(11) DEFAULT '0' COMMENT '原始长度(秒)',
#   `cloud_type` tinyint(4) DEFAULT '0' COMMENT '1: cos, 2: obs',
#   `cloud_path` varchar(255) DEFAULT '' COMMENT '云存储的路径',
#   `language` varchar(10) DEFAULT '' COMMENT '视频主要语言',
#   `status` tinyint(4) DEFAULT '0' COMMENT '0: 已爬取, 1: 本地已下载, 2: 已上传云端未处理, 3: 已处理未上传, 4: 已处理已上传, -100:无效数据',
#   `lock` tinyint(4) DEFAULT '0' COMMENT '处理锁',
#   `info` json DEFAULT NULL COMMENT 'meta数据',
#   `comment` text COMMENT '备注',
#   `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '数据创建时间',
#   `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '数据更新时间',
#   `source_id` varchar(50) DEFAULT '' COMMENT '资源来源id',
#   PRIMARY KEY (`id`),
#   UNIQUE KEY `UNQ_KEY` (`vid`) USING BTREE,
#   KEY `index_0` (`status`,`lock`),
#   KEY `index_1` (`status`,`language`,`lock`),
#   KEY `index_2` (`status`,`cloud_type`,`cloud_path`),
#   KEY `index_4` (`source_type`,`status`,`lock`),
#   KEY `index_3` (`source_type`,`language`,`status`,`lock`) USING BTREE
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='爬虫数据采集记录表';

class Video:
    """
    视频数据

    Attributes:
        id: 主键id
        vid: 视频ID
        position: 1: cas, 2: cuhk, 3: quwan
        source_type: 1: Bilibili, 2: 喜马拉雅, 3: YouTube
        source_link: 完整视频链接
        duration: 原始长度
        language: 视频主要语言
        cloud_type: 云存储类型
        cloud_path: 云存储的路径
        result_path: 处理结果路径
        status: 0: 已爬取, 1: 本地已下载, 2: 已上传云端未处理, 3: 已处理未上传, 4: 已处理已上传, -1 失败
        lock: 处理锁, 0: 未锁定, 1: 锁定
        info: meta数据, json格式
    """

    def __init__(
        self,
        vid: str = None,
        source_type: int = 3,
        cloud_path: str = None,
        id: int = 0,
        position: int = 1,
        cloud_type: int = 0,
        source_link: str = None,
        duration: int = 0,
        language: str = None,
        status=0,
        lock=0,
        info={},
        source_id: str = "",
        blogger_url: str = None,
    ):
        self.id = id
        self.vid = vid
        self.position = position
        self.source_type = source_type
        self.blogger_url = blogger_url
        self.source_link = source_link
        self.duration = duration
        self.cloud_type = cloud_type
        self.cloud_path = cloud_path
        self.language = language
        self.status = status
        self.lock = lock
        self.info = info
        self.source_id = source_id

    def __str__(self) -> str:
        return (
            f"Video(vid={self.vid}, position={self.position}, source_id={self.source_id}, "
            f"source_type={self.source_type}, source_link={self.source_link}, duration={self.duration}, "
            f"cloud_type={self.cloud_type}, cloud_path={self.cloud_path}, blogger_url={self.blogger_url}, "
            f"language={self.language}, status={self.status}, `lock`={self.lock}, info={self.info})"
        )
    
    def dict(self)->dict:
        return {
            "id": self.id,
            "vid": self.vid,
            "position": self.position,
            "source_type": self.source_type,
            "blogger_url": self.blogger_url,
            "source_link": self.source_link,
            "duration": self.duration,
            "cloud_type": self.cloud_type,
            "cloud_path": self.cloud_path,
            "language": self.language,
            "status": self.status,
            "lock": self.lock,
            "info": self.info,
            "source_id": self.source_id
        }

if __name__ == "__main__":
    # Example Usage
    video_data = Video(
        vid="VID12345",
        position=1,
        source_type=1,
        source_link="https://www.youtube.com/watch?v=12345",
        duration=100,
        cloud_type=2,
        cloud_path="/cloud/path/to/video",
        language="en",
        status=0,
        lock=0,
        info='{"key": "value"}',
        source_id="UCgdiE5jT-77eUMLXn66NLCQ"
    )
    print(video_data)
    pass
