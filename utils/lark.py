import requests
import json

# class LarkNotice():
#     def __init__(self, notice_text) -> None:
#         self.notice_text = notice_text

def alarm_lark_text(webhook:str, text:str, __retry=3)->bool:
    ''' 飞书普通文本告警 '''
    ''' Expamle Json Send
    {
	    "msg_type": "text",
	    "content": {"text": "test hello world."}
    }'''
    params = {
	    "msg_type": "text",
	    "content": {"text": f"{text}"}
    }
    # print(f"request: {webhook} | {params}")
    try:
        resp = requests.post(url=webhook, json=params)
        # print(f"response: {resp.status_code} {resp.content}")
        if resp.status_code != 200:
            # return False
            raise KeyError("resp.status_code != 200")
        resp = resp.json()
        if resp["code"] != 0:
            # return False
            raise KeyError("resp['code'] != 0")
    except Exception as e:
        print(f"alarm_lark_text > requests.post failed, webhook:{webhook}, error:{e}, retry:{__retry}")
        if __retry > 0:
            return alarm_lark_text(webhook=webhook, text=text, __retry=__retry-1)
        else:
            return False
    else:
        print(f"Lark > 已通知飞书: {resp}")
        return True

if __name__ == "__main__":
    webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/34755f1e-5fc7-46c9-9fee-177317a581ee"
    text = "【%s】 \n告警信息:%s \n机器IP:%s \n详情:%s \n告警时间:%s"%("Crawler_Name", "测试通知", "127.0.0.1", "测试，忽略😶♻🏝💨💦🙏👀✨💬", "2024/05/27 17:36")
    alarm_lark_text(webhook=webhook, text=text)