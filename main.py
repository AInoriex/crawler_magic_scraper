from dotenv import load_dotenv
load_dotenv()
from database import ytb_model
from database import ytb_api
from utils import obs

def main():
    # 更新vid信息
    # ytb_model.uploaded_download(id=id, cloud_type="obs", cloud_path=link)

    # v = youtube_api.get_download_list()
    # if v is None:
    #     print("Nothing to get")
    #     return
    # print(v)

    # v.cloud_type = 2
    # v.cloud_path = "www.google.com"
    # youtube_api.update_status(v)

    from_path = str("C:\\Users\\AInoriex\\Pictures\\faceswap_photos\\")
    to_path = "QUWAN_DATA/Vietnam/debug/"
    obs.upload_file(from_path, to_path)

    print("[MAIN END]")

if __name__ == "__main__":
    main()