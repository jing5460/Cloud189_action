import xmltodict
import requests

import sys
import uuid
import json
import time
from urllib import parse
from utils import DataEncode
from utils import Tests


class Client189:
    class __User:
        def __init__(self, username, password):
            self.username = username
            self.password = password
            self.userIconUrl = ""
            self.nickName = ""
            self.openId = ""
            self.accessToken = ""
            self.atExpiresIn = ""
            self.userRiskRating = ""
            self.ipRiskRating = ""
            self.userId = ""
            self.loginNum = ""
            self.loginMode = ""
            self.timeStamp = ""
            self.rfExpiresIn = ""
            self.mailp = ""
            self.refreshToken = ""
            self.mobileName = ""

            self.sessionKey = ""
            self.sessionSecret = ""
            self.eAccessToken = ""
            self.familySessionKey = ""
            self.familySessionSecret = ""

    class __Device:
        def __init__(self, deviceId: str, guid: str):
            self.deviceId = deviceId
            self.guid = guid
            self.imei = ""
            self.imsi = ""
            self.terminalInfo = "MI MIX3"
            self.osType = "Android"
            self.osVersion = "10"
            self.osInfo = self.osType + ":" + self.osVersion
            self.mobileBrand = "Xiaomi"
            self.mobileModel = "MI MIX3"

    __key = "g7qP45TVkQ5G6iNbbhaU5nXlAelGcAcs"
    __sha1Key = "fe5734c74c2f96a38157f420b32dc995"
    __appKey = "600100885"
    __ctaSdkVersion = "3.8.1"
    __clientType = "TELEANDROID"
    __clientVersion = "8.9.0"
    __clientPackageName = "com.cn21.ecloud"
    __clientPackageNameSign = "1c71af12beaa24e4d4c9189f3c9ad576"

    def __init__(self, username: str, password: str):
        self.__session = None
        self.user = None
        self.device = None
        self.msg = None
        self.isLogin = False
        self.login(username, password)

    def logout(self):
        if self.__session is not None:
            self.__session.close()
        self.isLogin = False

    def login(self, username, password) -> bool:
        r"""登录账号"""

        self.logout()
        self.__session = requests.session()
        self.user = self.__User(username, password)
        self.device = self.__Device(DataEncode.md5(username + password), DataEncode.md5(password))
        init_url = "https://open.e.189.cn/api/logbox/config/encryptConf.do"
        headers = {
            "Host": "open.e.189.cn",
            "User-Agent": "Mozilla/5.0 (Linux; " + self.device.osType + " " + self.device.osVersion + "; " + self.device.mobileModel + " Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.66 Mobile Safari/537.36 clientCtaSdkVersion/v" + self.__ctaSdkVersion + " deviceSystemVersion/" + self.device.osVersion + " deviceSystemType/" + self.device.osType + " clientPackageName/" + self.__clientPackageName + " clientPackageNameSign/" + self.__clientPackageNameSign,
            "Content-type": "application/x-www-form-urlencoded",
            "Origin": "null",
            "X-Requested-With": self.__clientPackageName,
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        data = {
            "appId": "cloud"
        }
        response = self.__session.post(init_url, data=data, headers=headers)
        Tests.myDebug(response.text)
        res = json.loads(response.text)
        pre = res.get("data").get("pre")
        pubKey = res.get("data").get("pubKey")

        login_url = "https://open.e.189.cn/api/logbox/oauth2/oAuth2SdkLoginByPassword.do"
        deviceInfo = {
            "imei": self.device.imei,
            "imsi": self.device.imsi,
            "deviceId": self.device.deviceId,
            "terminalInfo": self.device.terminalInfo,
            "osInfo": self.device.osInfo,
            "mobileBrand": self.device.mobileBrand,
            "mobileModel": self.device.mobileModel,
        }
        data = {
            "appKey": "cloud",
            "deviceInfo": DataEncode.encodeHex(json.dumps(deviceInfo), self.__key),
            "apptype": "wap",
            "loginType": "1",
            "dynamicCheck": "false",
            "userName": pre + DataEncode.rsa_encode(pubKey, self.user.username),
            "password": pre + DataEncode.rsa_encode(pubKey, self.user.password),
            "validateCode": "",
            "captchaToken": "",
            "jointWay": "1|2",
            "jointVersion": "v"+self.__ctaSdkVersion,
            "operator": "",
            "nwc": "WIFI",
            "nws": "2",
            "guid": self.device.guid,
            "reqId": "undefined",
            "headerDeviceId": self.device.guid
        }
        Tests.myDebug(data)
        response = self.__session.post(login_url, data=data, headers=headers)
        Tests.myDebug(response.text)
        if str(response.json()["result"]) != "0":
            self.msg = response.json()["msg"]
            self.isLogin = False
            return False
        else:
            paras = parse.parse_qs(response.json()["returnParas"]).get("paras")[0]
            Tests.myDebug(paras)
            data = DataEncode.decodeHex(paras, self.__key)
            paras = parse.parse_qs(data)
            self.user.accessToken = paras.get("accessToken")[0]

            rand = time.time()
            data = {
                "rand": str(rand*1000),
                "accessToken": self.user.accessToken,
                "clientType": self.__clientType,
                "version": self.__clientVersion,
                "clientSn": "null",
                "model": self.device.mobileModel,
                "osFamily": self.device.osType,
                "osVersion": str(int(self.device.osVersion)+19),
                "networkAccessMode": "WIFI",
                "telecomsOperator": "unknow",
                "channelId": "uc"
            }
            merged_url = "https://api.cloud.189.cn/login4MergedClient.action?"+parse.urlencode(data)
            data = "AppKey="+self.__appKey+"&Operate=POST&RequestURI=/login4MergedClient.action&Timestamp="+str(rand)
            headers = {
                "Host": "api.cloud.189.cn",
                "x-request-id": str(uuid.uuid4()),
                "Content-type": "application/x-www-form-urlencoded",
                "user-agent": "Ecloud/"+self.__clientVersion+" ("+self.device.mobileModel+"; ; uc) Android/"+str(int(self.device.osVersion)+19),
                "X-Requested-With": self.__clientPackageName,
                "appkey": self.__appKey,
                "appsignature": DataEncode.hmac_sha1(data, self.__sha1Key),
                "timestamp": str(rand),
                "Accept-Encoding": "gzip",
                "content-type": "text/xml; charset=utf-8"
            }
            response = self.__session.post(merged_url, headers=headers)
            Tests.myDebug(response.text)
            res = xmltodict.parse(response.text)
            data = json.loads(json.dumps(res))
            self.user.sessionKey = data.get("userSession").get("sessionKey")
            self.user.sessionSecret = data.get("userSession").get("sessionSecret")
            self.msg = "登录成功"

            self.isLogin = True
            return True

    def sign(self) -> bool:
        if not self.isLogin:
            self.msg = "请先登录账号"
            return False

        rand = time.time()
        sign_url = "https://api.cloud.189.cn/mkt/userSign.action?rand=" + str(rand) + "&clientType="+self.__clientType+"&version="+self.__clientVersion+"&model="+self.device.mobileModel
        now = time.strftime("%a, %d %b %Y %X GMT", time.localtime(rand))
        data = "SessionKey="+self.user.sessionKey+"&Operate=GET&RequestURI=/mkt/userSign.action&Date="+now
        Tests.myDebug(data)
        headers = {
            "Host": "api.cloud.189.cn",
            "x-request-id": str(uuid.uuid4()),
            "user-agent": "Ecloud/" + self.__clientVersion + " (" + self.device.mobileModel + "; ; uc) Android/" + str(int(self.device.osVersion) + 19),
            "sessionkey": self.user.sessionKey,
            "signature": DataEncode.hmac_sha1(data, self.user.sessionSecret),
            "date": now,
            "Accept-Encoding": "gzip",
            "content-type": "text/xml; charset=utf-8"
        }
        response = self.__session.get(sign_url, headers=headers)
        Tests.myDebug(response.text)
        res = xmltodict.parse(response.text)
        data = json.loads(json.dumps(res))
        '''
        {
            'userSignResult': {
                'result': '-1',
                'resultTip': '获得35M空间',
                'activityFlag': '2',
                'prizeListUrl': 'https://m.cloud.189.cn/zhuanti/2016/sign/myPrizeList.jsp',
                'buttonTip': '点击领取红包',
                'buttonUrl': 'https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp',
                'activityTip': '每天签到可领取更多福利哟，记得常来！'
            }
        }
        '''
        msg = ""
        if data.get("userSignResult").get("result") == '-1':
            msg = "今日已签到"
        else:
            msg = "签到成功"
        self.msg = msg+", "+data.get("userSignResult").get("resultTip")

        return data.get("userSignResult").get("result") == '0'

    def draw(self):
        r"""todo: 完善每日抽奖功能"""
        pass
        # draw_url = f'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN&activityId=ACT_SIGNIN'


def hide_username(u: str) -> str:
    u_len = len(u)
    fill_len = int(u_len * 0.3) + 1
    b_index = int((u_len - fill_len) / 2)
    e_index = u_len - fill_len - b_index
    return u[:b_index] + "*" * fill_len + u[-e_index:]


def print_msg(msg: str):
    print(" "*4 + msg)


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

    print()
    print(hide_username(username)+":")
    cloud = Client189(username, password)
    print_msg(cloud.msg)
    if not cloud.isLogin:
        exit(-1)
    cloud.sign()
    print_msg(cloud.msg)
