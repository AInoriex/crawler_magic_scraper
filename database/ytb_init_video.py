class Video:
    """
    视频数据
    Attributes:

        channel_url: 博主链接
        video_url: 完整视频链接
        duration: 原始长度
        language: 视频主要语言
        ...
    """
    def __init__(
        self,
        channel_url: str,
        video_url: str,
        duration: float = None,
        language: str = None,
    ):  
        self.channel_url = channel_url
        self.video_url = video_url
        self.duration = duration
        self.language = language

    def __str__(self) -> str:
        return (
            f"Video(blogger_url={self.channel_url}webpage_url={self.video_url}, duration={self.duration}, language={self.language})"
        )
    
    def dict(self) -> dict:
        return {
            "blogger_url": self.channel_url,
            "webpage_url": self.video_url,
            "duration": self.duration,
            "language": self.language,
        }
    
if __name__ == "__main__":
    # Example Usage
    # video_data = Video(
    #     channel_url = "https://www.youtube.com/@user-qx9so9pk1m/videos",
    #     video_url = [('https://www.youtube.com/watch?v=lWHJDgNlmVo', '7121.0'), ('https://www.youtube.com/watch?v=gtCi8QPYrzY', '5408.0'), ('https://www.youtube.com/watch?v=c3E3_vJVQU4', '6006.0'), ('https://www.youtube.com/watch?v=22fcqCHNnAk', '6925.0'), ('https://www.youtube.com/watch?v=ROQcagtrpAc', '5343.0'), ('https://www.youtube.com/watch?v=b5VzTwAJ3hE', '5581.0')],
    #     duration = ['579.0', '636.0', '626.0', '4403.0', '740.0', '162.0'],
    #     language = "es",
    # )
    # print(video_data)
    pass