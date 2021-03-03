import sys
from cloud189 import *


def main(user: str, pwd: str):
    print_msg()
    print_msg(hide_username(user) + ":", True)
    cloud = Client.Client(user, pwd)
    print_msg(cloud.msg)
    if not cloud.isLogin:
        exit(-1)
    cloud.sign()
    print_msg(cloud.msg)
    cloud.draw()
    print_msg(cloud.msg)
    print_msg()


def hide_username(name: str) -> str:
    u_len = len(name)
    fill_len = int(u_len * 0.3) + 1
    b_index = int((u_len - fill_len) / 2)
    e_index = u_len - fill_len - b_index
    return name[:b_index] + "*" * fill_len + name[-e_index:]


def print_msg(msg: str = "", isFirstLine: bool = False):
    if isFirstLine or msg == "":
        indent = ""
    else:
        indent = " " * 4
    print(indent + msg.replace("\n", "\n"+indent))


if __name__ == '__main__':
    # 参数格式: 账号----密码
    if len(sys.argv) == 2 and len(sys.argv[1].split("----")) == 2:
        username = sys.argv[1].split("----")[0]
        password = sys.argv[1].split("----")[1]
    else:
        username = input("请输入账号: ")
        password = input("请输入登录密码: ")
    username = username.strip()
    password = password.strip()

    main(username, password)
