import requests


def push_text(msg: str, token: str) -> str:
    data = {
        "template": "html",
        "token": token,
        "title": "cloud189app-action",
        "content": msg.replace("\n", "<br>").replace(" ", "&nbsp;")
    }
    response = requests.post("http://www.pushplus.plus/send", data=data)

    try:
        j = response.json()
        return j['msg'] if j['data'] is None else j['data']
    except ValueError:
        return response.text