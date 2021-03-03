import requests
import xmltodict
import hashlib
import json
import uuid
import os
import time
from configparser import ConfigParser
from urllib.parse import urlparse
from cloud189.consts import *

__ini = ConfigParser()


def initConfigInfo(username, password):
    __ini.read(os.path.join(os.path.dirname(__file__), "ConfigInfo.ini"), encoding="utf-8")
    if __ini.get("device", "deviceId") == "":
        __ini.set("device", "deviceId", md5(username + password))
    if __ini.get("device", "guid") == "":
        __ini.set("device", "guid", md5(password))
    return __ini


def getConfigInfo(section, key):
    r"""read data form ConfigInfo.ini

    example: getConfigInfo("device", "osType")

    this method will be removed in 0.2.0
    """

    return __ini.get(section, key)


def initRequestSession():
    session = requests.session()
    session.headers['User-Agent'] = ""
    return session


def getRequestHeaders(url: str, header_Type=HeaderType_Origin_1) -> dict:
    r"""this method will be removed in 0.2.0"""

    headers = dict()
    parser = urlparse(url)
    headers['Host'] = parser.hostname

    # 原生设备 UA headers
    if header_Type == HeaderType_Origin_1:
        osType = getConfigInfo("device", "osType")
        osVersion = getConfigInfo("device", "osVersion")
        mobileModel = getConfigInfo("device", "mobileModel")
        ctaSdkVersion = getConfigInfo("client", "ctaSdkVersion")
        clientPackageName = getConfigInfo("client", "clientPackageName")
        clientPackageNameSign = getConfigInfo("client", "clientPackageNameSign")
        headers[
            'User-Agent'] = f"Mozilla/5.0 (Linux; {osType} {osVersion}; {mobileModel} Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.66 Mobile Safari/537.36 clientCtaSdkVersion/v{ctaSdkVersion} deviceSystemVersion/{osVersion} deviceSystemType/{osType} clientPackageName/{clientPackageName} clientPackageNameSign/{clientPackageNameSign}"
        headers['X-Requested-With'] = clientPackageName
        headers['Accept'] = "*/*"
        headers['Content-type'] = "application/x-www-form-urlencoded"
        headers['Origin'] = "null"
        headers['Sec-Fetch-Site'] = "cross-site"
        headers['Sec-Fetch-Mode'] = "cors"
        headers['Sec-Fetch-Dest'] = "empty"
        headers['Accept-Encoding'] = "gzip, deflate"
        headers['Accept-Language'] = "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"

    # 非原生 UA headers
    elif header_Type == HeaderType_Signature_2:
        clientVersion = getConfigInfo("client", "clientVersion")
        mobileModel = getConfigInfo("device", "mobileModel")
        osAPI = getConfigInfo("device", "osAPI")
        headers['x-request-id'] = str(uuid.uuid4())
        headers['user-agent'] = f"Ecloud/{clientVersion} ({mobileModel}; ; uc) Android/{osAPI}"

    return headers


def sendGetRequest(session, url, headerType=1, headers=None):
    r"""
    :rtype: requests.Response
    """

    if headers is None:
        headers = {}
    headers.update(getRequestHeaders(url, headerType))
    return session.get(url, headers=headers)


def sendPostRequest(session, url, data, headerType=1, headers=None):
    r"""
    :rtype: requests.Response
    """

    if headers is None:
        headers = {}
    headers.update(getRequestHeaders(url, headerType))
    return session.post(url, data=data, headers=headers)


def getTimestamp(isSecond: bool = False) -> int:
    r"""return millisecond-timestamp(13) or second-timestamp(10)"""
    t = time.time()
    t = t if isSecond else t*1000
    return int(t)


def CST2GMTString(millisecond: int) -> str:
    r"""CST millisecond to GMT string"""

    millisecond -= 28800 * 1000
    t = time.strftime("%a, %d %b %Y %X GMT", time.localtime(millisecond / 1000))
    t = t.replace(", 0", ", ")
    return t


def xml2dict(xml_data: str) -> dict:
    data = json.dumps(xmltodict.parse(xml_data))
    return json.loads(data)


def md5(string: str, encoding="utf-8"):
    return hashlib.md5(string.encode(encoding)).hexdigest()

