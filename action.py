import sys
from cloud189 import *
from functions import *


def main(user: str, pwd: str):
    print_msg()
    print_msg(hide_username(user) + ":", True)
    cloud = Client(user, pwd)
    print_msg(cloud.msg)
    if not cloud.isLogin:
        exit(-1)
    cloud.sign()
    print_msg(cloud.msg)
    cloud.draw()
    print_msg(cloud.msg)
    print_msg()


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
