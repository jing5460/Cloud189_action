import json
import random
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
        if self.getDrawNum() is None:
            # 签到之前必须调用 getDrawNum() 方法
            return False

        headers = {
            "user-agent": self.getUserAgentString(2) + " " + self.getUserAgentString(5),
            "x-requested-with": "XMLHttpRequest",
            "referer": consts.URL_1_drawPage + "?albumBackupOpened=0"
        }
        url = consts.URL_1_drawPrizeMarketDetails + "?activityId=ACT_SIGNIN&noCache="+str(random.random())
        response = utils.sendGetRequest(self.__session, url + "&taskId=TASK_SIGNIN", 0, headers)
        data = json.loads(response.text)
        self.msg = "签到抽奖: "
        if "prizeName" in data:
            self.msg += data['prizeName']
        elif "errorCode" in data:
            self.msg += data['errorCode']
        else:
            self.msg = response.text

        utils.sendGetRequest(self.__session, consts.URL_1_act + "?act=10", 0, headers)
        headers['referer'] = str(headers['referer'])[:-1] + "1"
        url = consts.URL_1_drawPrizeMarketDetails + "?activityId=ACT_SIGNIN&noCache=" + str(random.random())
        response = utils.sendGetRequest(self.__session, url + "&taskId=TASK_SIGNIN_PHOTOS", 0, headers)
        data = json.loads(response.text)
        self.msg += "\n相册抽奖: "
        if "prizeName" in data:
            self.msg += data['prizeName']
        elif "errorCode" in data:
            self.msg += data['errorCode']
        else:
            self.msg = response.text
        return self.msg

    def getDrawNum(self):
        r"""获取今日抽奖次数
        返回整型抽奖次数 或 None
        """

        html = self.ssoLogin(consts.URL_1_drawPage + "?albumBackupOpened=0")
        b_index = html.find("今天还有<em>")+8
        e_index = html.find("</em>次抽红包机会")
        if b_index == 7:
            self.msg = "进入抽奖页面失败"
            return None
        num = int(html[b_index:e_index])
        num += 1 if html.find("<p>开启自动备份后可<em>+1</em>次抽红包机会</p>") != -1 else 0
        return num

    def ssoLogin(self, redirectUrl):
        params = {
            "sessionKey": self.user.sessionKey,
            "sessionKeyFm": self.user.familySessionKey,
            "appName": self.configInfo.get("client", "clientPackageName"),
            "redirectUrl": redirectUrl
        }
        url = consts.URL_1_ssoLoginMerge + "?" + parse.urlencode(params)
        headers = {
            "User-Agent": self.getUserAgentString(2) + " " + self.getUserAgentString(5),
            "x-requested-with": self.configInfo.get("client", "clientPackageName")
        }
        response = utils.sendGetRequest(self.__session, url, 0, headers)

        return response.text

    def getUserAgentString(self, ua_type: int = 1):
        r""" return User-Agent info

        1. (http.agent): Dalvik/2.1.0 (Linux; U; Android 5.1.1; OPPO R11 Plus Build/NMF26X)
        2. (webview User-Agent): Mozilla/5.0 (Linux; Android 10; MI MIX3 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.66 Mobile Safari/537.36
        3. (client info): clientCtaSdkVersion/v3.8.1 deviceSystemVersion/10 deviceSystemType/Android clientPackageName/com.cn21.ecloud clientPackageNameSign/1c71af12beaa24e4d4c9189f3c9ad576
        4. (util_User-Agent_3): Ecloud/8.9.0 (MI MIX3; ; uc) Android/29
        5. (util_User-Agent_4): Ecloud/8.9.0 Android/29 clientId/null clientModel/MIX 3 imsi/null clientChannelId/uc proVersion/1.0.6
        """

        if ua_type in (1, 2):
            osType = self.configInfo.get("device", "osType")
            osVersion = self.configInfo.get("device", "osVersion")
            mobileModel = self.configInfo.get("device", "mobileModel")
            buildId = self.configInfo.get("device", "buildId")

            if ua_type == 1:
                return f"Dalvik/2.1.0 (Linux; U; {osType} {osVersion}; {mobileModel} Build/{buildId})"
            elif ua_type == 2:
                return f"Mozilla/5.0 (Linux; {osType} {osVersion}; {mobileModel} Build/{buildId}; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.66 Mobile Safari/537.36"
        elif ua_type == 3:
            clientCtaSdkVersion = self.configInfo.get("client", "clientCtaSdkVersion")
            osVersion = self.configInfo.get("device", "osVersion")
            osType = self.configInfo.get("device", "osType")
            clientPackageName = self.configInfo.get("client", "clientPackageName")
            clientPackageNameSign = self.configInfo.get("client", "clientPackageNameSign")

            return f"clientCtaSdkVersion/v{clientCtaSdkVersion} deviceSystemVersion/{osVersion} deviceSystemType/{osType} clientPackageName/{clientPackageName} clientPackageNameSign/{clientPackageNameSign}"
        elif ua_type in (4, 5):
            clientVersion = self.configInfo.get("client", "clientVersion")
            proVersion = self.configInfo.get("client", "proVersion")
            mobileModel = self.configInfo.get("device", "mobileModel")
            osType = self.configInfo.get("device", "osType")
            osVersion = self.configInfo.get("device", "osVersion")
            imei = self.configInfo.get("device", "imei")
            imsi = self.configInfo.get("device", "imsi")
            imei = imei if imsi != "" else "null"
            imsi = imsi if imsi != "" else "null"

            if ua_type == 4:
                return f"Ecloud/{clientVersion} ({mobileModel}; ; uc) {osType}/{osVersion}"
            elif ua_type == 5:
                return f"Ecloud/{clientVersion} {osType}/{osVersion} clientId/{imei} clientModel/{mobileModel} imsi/{imsi} clientChannelId/uc proVersion/{proVersion}"


