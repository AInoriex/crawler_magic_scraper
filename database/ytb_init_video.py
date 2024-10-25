class Video:
    """
    视频数据
    Attributes:

        blogger_url: 博主链接
        video_url: 完整视频链接
        duration: 原始长度
        language: 视频主要语言
        count: 共采集的视频数量
        ...
    """
    def __init__(
        self,
        blogger_url: str,
        video_url: str,
        duration: int = None,
        language: str = None,
        count: str = None,
    ):  
        self.blogger_url = blogger_url
        self.video_url = video_url
        self.duration = duration
        self.language = language
        self.count = count
    def __str__(self) -> str:
        return (
            f"Video(blogger_url={self.blogger_url}, webpage_url={self.video_url}, duration={self.duration}, language={self.language}, count = {self.count})"
        )
    def dict(self) -> dict:
        return {
            "blogger_url": self.blogger_url,
            "webpage_url": self.video_url,
            "duration": self.duration,
            "language": self.language,
            "count": self.count
        }
if __name__ == "__main__":
    # Example Usage
    # video_data = Video(
    #     blogger_url = "https://www.youtube.com/@ElDollop/videos",
    #     duration = int(700),
    #     language = "es",
    # )
    # print(video_data)
    pass