from utils.utime import get_time_stamp
from requests import get, post
from uuid import uuid4
from database.ytb_model import Video
from os import getenv

# Using the Database Apis
if getenv("DATABASE_GET_API") == '':
    # db_manager = DatabaseManager()
    raise ValueError("Get DATABASE_GET_API failed")
if getenv("DATABASE_UPDATE_API") == '':
    # db_manager = DatabaseManager()
    raise ValueError("Get DATABASE_UPDATE_API failed")
if getenv("DATABASE_CREATE_API") == '':
    # db_manager = DatabaseManager()
    raise ValueError("Get DATABASE_CREATE_API failed")

def get_download_list(qid=0)->Video|None:
    ''' 获取一条ytb记录 '''
    url = "%s?sign=%d&id=%d"%(getenv("DATABASE_GET_API"), get_time_stamp(), qid)
    # print(f"get_download_list > req, url:{url}")
    resp = get(url=url)
    print(f"get_download_list > resp, status_code:{resp.status_code}, content:{resp.content}")
    assert resp.status_code == 200
    resp_json = resp.json()
    # print("get_download_list > resp detail, status_code:%d, content:%s"%(resp_json["code"], resp_json["msg"]))
    if len(resp_json["data"]["result"]) <= 0:
        # print("get_download_list > nothing to get.")
        return None
    resp_data = resp_json["data"]["result"][0]
    video = Video(
        id=resp_data["id"],
        vid=resp_data["vid"],
        position=resp_data["position"],
        source_type=resp_data["source_type"],
        source_link=resp_data["source_link"],
        duration=resp_data["duration"],
        cloud_type=resp_data["cloud_type"],
        cloud_path=resp_data["cloud_path"],
        language=resp_data["language"],
        status=resp_data["status"],
        lock=resp_data["lock"],
        info=resp_data["info"],
    )
    return video

def update_status(video:Video):
    ''' 更新ytb记录 '''
    # url = getenv("DATABASE_UPDATE_API")
    url = "%s?sign=%d"%(getenv("DATABASE_UPDATE_API"), get_time_stamp())
    req = {
        "id": video.id,
        "vid": video.vid,
        "status": video.status,
        "cloud_type": video.cloud_type,
        "cloud_path": video.cloud_path,
    }
    resp = post(url=url, json=req)
    assert resp.status_code == 200
    resp_json = resp.json()
    # print("update_status > resp detail, status_code:%d, content:%s"%(resp_json["code"], resp_json["msg"]))
    resp_code = resp_json["code"]
    if resp_code != 0:
        raise Exception(f"更新数据接口返回失败, req:{req}, resp:{resp.content}")
    else:
        print(f"update_status > 更新状态成功 req:{req}, resp:{resp_json}")

def create_video(video:Video):
    ''' 创建ytb记录 '''
    try:
        # url = getenv("DATABASE_CREATE_API")
        url = "%s?sign=%d"%(getenv("DATABASE_CREATE_API"), get_time_stamp())
        req = video.dict()
        resp = post(url=url, json=req, timeout=5, verify=True)
        assert resp.status_code == 200
        resp_json = resp.json()
        # print("create_video > resp detail, status_code:%d, content:%s"%(resp_json["code"], resp_json["msg"]))
        resp_code = resp_json.get("code")
        if resp_code == 0:
            # print(f"create_video > 创建数据成功 req:{req}, resp:{resp_json}")
            print(f"create_video > 创建数据成功 vid:{req.get('vid')}, link:{req.get('source_link')}")
        elif resp_code == 25000:
            print(f"create_video > 资源存在, 跳过创建 status_code:{resp_json.get('code')}, content:{resp_json.get('msg')}")
        else:
        # elif resp_code != 0:
            print(f"create_video > 资源创建失败, req:{req}, resp:{resp.content}")
            raise Exception(f"创建数据接口返回失败, req:{req}, resp:{resp.content}")
    except Exception as e:
        print("create_video > 未知错误")
        print(e)
        return

if __name__ == "__main__":
    v = get_download_list()