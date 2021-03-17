import requests


def push_text(msg: str, token: str):
    data = {
        "template": "html",
        "token": token,
        "title": "cloud189app-action",
        "content": msg.replace("\n", "<br>").replace(" ", "&nbsp;")
    }
    return requests.post("http://www.pushplus.plus/send", data=data).text
