from urllib import parse
from cloud189 import utils
from cloud189 import consts
from cloud189.UserInfo import UserInfo
from cloud189.libs import crypto


class Client:
    def __init__(self, username, password):
        self.__session = utils.initRequestSession()
        self.configInfo = utils.initConfigInfo(username, password)
        self.user = UserInfo(username, password)
        self.msg = ""
        self.isLogin = self.login()

    def checkLogin(self):
        if self.isLogin:
            return True
        else:
            self.msg = "请先登录账号"
            return False

    def needCaptcha(self):
        data = {
            "appKey": "cloud",
            "userName": "{RSA}" + crypto.rsa_encryptHex(self.user.username),
            "guid": self.configInfo.get("device", "guid"),
            "reqId": "undefined",
            "headerDeviceId": self.configInfo.get("device", "guid")
        }
        response = utils.sendPostRequest(self.__session, consts.URL_1_needCaptcha, data, consts.HeaderType_Origin_1)

        if response.text != 0:
            self.msg = "当前账号登录需要验证, 请在手机端完成登录后重试"
            return False
        return True

    def mergedSession(self, accessToken: str):
        rand = str(utils.getTimestamp())
        data = {
            "rand": rand,
            "accessToken": accessToken,
            "clientType": self.configInfo.get("client", "clientType"),
            "version": self.configInfo.get("client", "clientVersion"),
            "clientSn": "null",
            "model": self.configInfo.get("device", "mobileModel"),
            "osFamily": self.configInfo.get("device", "osType"),
            "osVersion": self.configInfo.get("device", "osAPI"),
            "networkAccessMode": "WIFI",
            "telecomsOperator": "unknow",
            "channelId": "uc"
        }
        appkey = "600100885"
        headers = {
            "appkey": appkey,
            "appsignature": crypto.getSignatureHex(f"AppKey={appkey}&Operate=POST&RequestURI=/login4MergedClient.action&Timestamp={rand}").upper(),
            "timestamp": rand
        }

        response = utils.sendPostRequest(self.__session, consts.URL_2_login4MergedClient, data, consts.HeaderType_Signature_2, headers)
        data = utils.xml2dict(response.text)
        if "userSession" in data:
            self.user.sessionKey = data['userSession']['sessionKey']
            self.user.sessionSecret = data['userSession']['sessionSecret']
            self.user.eAccessToken = data['userSession']['eAccessToken']
            self.user.familySessionKey = data['userSession']['familySessionKey']
            self.user.familySessionSecret = data['userSession']['familySessionSecret']
            return True
        else:
            self.msg = data['error']['message']
            return False

    def login(self):
        r"""登录失败则由失败方法设置提示信息, login() 方法中只负责设置最终登录成功提示"""

        if self.needCaptcha():
            return False

        deviceInfo = {
            'imei': None, 'imsi': None, 'deviceId': None, 'terminalInfo': None,
            'osInfo': None, 'mobileBrand': None, 'mobileModel': None
        }
        for key in deviceInfo.keys():
            if self.configInfo.has_option("device", key.lower()):
                deviceInfo[key] = self.configInfo.get("device", key.lower())
            deviceInfo['terminalInfo'] = self.configInfo.get("device", "mobileModel".lower())
            deviceInfo['osInfo'] = self.configInfo.get("device", "osType".lower()) + ":" + self.configInfo.get("device", "osVersion".lower())
        data = {
            "appKey": "cloud",
            "deviceInfo": crypto.encryptHex(str(deviceInfo)),
            "apptype": "wap",
            "loginType": "1",
            "dynamicCheck": "false",
            "userName": "{RSA}" + crypto.rsa_encryptHex(self.user.username),
            "password": "{RSA}" + crypto.rsa_encryptHex(self.user.password),
            "validateCode": "",
            "captchaToken": "",
            "jointWay": "1|2",
            "jointVersion": "v" + self.configInfo.get("client", "ctaSdkVersion"),
            "operator": "",
            "nwc": "WIFI",
            "nws": "2",
            "guid": self.configInfo.get("device", "guid"),
            "reqId": "undefined",
            "headerDeviceId": self.configInfo.get("device", "guid")
        }
        response = utils.sendPostRequest(self.__session, consts.URL_1_oAuth2SdkLoginByPassword, data, consts.HeaderType_Origin_1)
        if str(response.json()["result"]) != "0":
            self.msg = response.json()["msg"]
            return False
        data = parse.parse_qs(crypto.decryptHex(parse.parse_qs(response.json()["returnParas"]).get("paras")[0]))
        self.user.nickName = data.get("nickName")[0]

        if self.mergedSession(data.get("accessToken")[0]):
            self.msg = self.user.nickName + ", 登录成功"
            return True
        return False

    def sign(self):
        if not self.checkLogin():
            return False
        rand = str(utils.getTimestamp())
        params = {
            "rand": rand,
            "clientType": self.configInfo.get("client", "clientType"),
            "version": self.configInfo.get("client", "clientVersion"),
            "model": self.configInfo.get("device", "mobileModel")
        }
        t = utils.CST2GMTString(int(rand))
        headers = {
            "sessionkey": self.user.sessionKey,
            "date": t,
            "signature": crypto.getSignatureHex(f"SessionKey={self.user.sessionKey}&Operate=GET&RequestURI=/mkt/userSign.action&Date={t}", self.user.sessionSecret)
        }
        url = consts.URL_2_userSign+"?"+parse.urlencode(params)
        response = utils.sendGetRequest(self.__session, url, consts.HeaderType_Signature_2, headers)
        data = utils.xml2dict(response.text)

        flag = False
        if "error" in data:
            self.msg = data['error']['message']
        elif "userSignResult" not in data:
            self.msg = str(data) if str(data) != "" else "请求失败"
        elif data['userSignResult']['result'] == '1':
            flag = True
            self.msg = "签到成功, "+data['userSignResult']['resultTip']
        elif data['userSignResult']['result'] == '-1':
            self.msg = "不能重复签到, 今日已"+data['userSignResult']['resultTip']
        else:
            self.msg = "[" + data['userSignResult']['result'] + "]: " + data['userSignResult']['resultTip']
        return flag

    def draw(self):
        if not self.checkLogin():
            return False
        # todo: 用户抽奖
        self.msg = "抽奖功能正在开发中..."
        return False
