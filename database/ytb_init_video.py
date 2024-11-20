class Video:
    """
    视频数据
    Attributes:

        channel_url: 博主链接
        source_link: 完整视频链接
        duration: 原始长度
        language: 视频主要语言
        souece_id: 视频ID
        ...
    """
    def __init__(
        self,
        channel_url: str,
        source_link: str,
        duration: float = None,
        language: str = None,
        souece_id: str = None,
    ):  
        self.channel_url = channel_url
        self.source_link = source_link
        self.duration = duration
        self.language = language
        self.source_id = souece_id

    def __str__(self) -> str:
        return (
            f"Video(blogger_url={self.channel_url}, source_link={self.source_link}, "
            f"duration={self.duration}, language={self.language}, source_id={self.source_id}"
        )
    
    def dict(self) -> dict:
        return {
            "blogger_url": self.channel_url,
            "source_link": self.source_link,
            "duration": self.duration,
            "language": self.language,
            "source_id": self.source_id
        }
    
if __name__ == "__main__":
    # Example Usage
    # video_data = Video(
    #     channel_url = "https://www.youtube.com/@user-qx9so9pk1m/videos",
    #     video_url = [('https://www.youtube.com/watch?v=lWHJDgNlmVo', '7121.0'), ('https://www.youtube.com/watch?v=gtCi8QPYrzY', '5408.0'), ('https://www.youtube.com/watch?v=c3E3_vJVQU4', '6006.0'), ('https://www.youtube.com/watch?v=22fcqCHNnAk', '6925.0'), ('https://www.youtube.com/watch?v=ROQcagtrpAc', '5343.0'), ('https://www.youtube.com/watch?v=b5VzTwAJ3hE', '5581.0')],
    #     duration = ['579.0', '636.0', '626.0', '4403.0', '740.0', '162.0'],
    #     language = "es",
    #     souece_id= ['UCgdiE5jT-77eUMLXn66NLCQ','UCgdiE5jT-77eUMLXn66NLCQ','UCgdiE5jT-77eUMLXn66NLCQ','UCgdiE5jT-77eUMLXn66NLCQ','UCgdiE5jT-77eUMLXn66NLCQ','UCgdiE5jT-77eUMLXn66NLCQ',]
    # )
    # print(video_data)
    pass