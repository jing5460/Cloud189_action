import requests


def push_text(msg, token):
    data = {
        "token": token,
        "title": "cloud189app-action",
        "content": msg
    }
    return requests.post("http://www.pushplus.plus/send", data=data).text
