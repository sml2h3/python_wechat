#coding=utf-8
import requests
import json
import qrcode_terminal
import os
import sys
import re
import random
sys.path.append(os.path.abspath('..'))
from Logger.Logger import Logger
import xml.dom.minidom
import time
reload(sys)
sys.setdefaultencoding('utf-8')


class Login(object):
    def __init__(self):
        self.logger = Logger('Login')
        self.get_base_cookies = "https://wx.qq.com/"
        self.get_ptqr_url = "https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_=1488277801955"
        self.qrcode = "https://login.weixin.qq.com/qrcode/"
        self.code = open('code.png', 'w')
        self.check = "https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid={uuid}&tip=0&r=2073077620&_=1488280416522"
        self.jm = "http://jiema.wwei.cn/fileupload/index/op/jiema.html"
        self.baseinfo = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=2056259748&lang=zh_CN&pass_ticket="
        self.info = {}
        self._run()

    def _run(self):
        #开启一个会话
        session = requests.session()
        result = session.get(self.get_base_cookies)
        if result.status_code == 200:
            header = {
                'Host': 'login.wx.qq.com',
                'Referer': 'https://wx.qq.com/'
            }
            result = session.get(self.get_ptqr_url, headers=header)
            if result.status_code == 200:
                pat = re.compile('window.QRLogin.uuid = "(.*?)"', re.S)
                self.target = pat.findall(result.text)
                if len(self.target) == 1:
                    qrcode = self.qrcode + self.target[0]
                    self.logger.info('正在获取二维码图片')
                    result = session.get(qrcode)
                    self.code.write(result.content)
                    self.code.close()
                    try:
                        rtext = requests.post(self.jm, files={'file': open('code.png', 'rb')})
                    except Exception as e:
                        self.logger.debug('upload qcord error')
                    if rtext.status_code == 200:
                        try:
                            jtext = json.loads(rtext.text)
                        except ValueError as e:
                            self.logger.error('二维码解析返回不正常')
                            return {'result': '-1', 'reason': '二维码解析返回不正常'}
                        self.logger.info('请扫描屏幕中的二维码')
                        url = jtext['jiema']
                        # 将二维码打印到控制台
                        qrcode_terminal.draw(url)
                        self.logger.info('二维码获取结束')
                        flag = True
                        while flag:
                            result = requests.get(self.check.replace('{uuid}', self.target[0]))
                            pat = re.compile('window.code=(.*?);', re.S)
                            self.c = pat.findall(result.text)
                            if self.c[0] == '200':
                                self.logger.info('登录成功')
                                break
                            if self.c[0] == 408:
                                self.logger.info('等待扫码')
                            if self.c[0] == 201:
                                self.logger.info('扫码成功，请在手机端点击确认')
                        pat = re.compile('window.redirect_uri="(.*?)";', re.S)
                        self.redurl = pat.findall(result.text)
                        if len(self.redurl) == 1:
                            url = self.redurl[0]
                            result = requests.get(url, allow_redirects=False)
                            real_cookies = result.cookies
                            print result.text
                            for node in xml.dom.minidom.parseString(result.text).documentElement.childNodes:
                                if len(node.childNodes) == 0:
                                    continue
                                else:
                                    data = node.childNodes[0].data
                                    if node.nodeName == 'ret':
                                        self.info['ret'] = data
                                        if data == '0':
                                            continue
                                        else:
                                            self.logger.info('登录失败')
                                            break
                                    if node.nodeName == 'skey':
                                        self.info['skey'] = data
                                    if node.nodeName == 'wxsid':
                                        self.info['wxsid'] = data
                                    if node.nodeName == 'wxuin':
                                        self.info['wxuin'] = data
                                    if node.nodeName == 'pass_ticket':
                                        self.info['pass_ticket'] = data
                                    if node.nodeName == 'isgrayscale':
                                        self.info['isgrayscale'] = data
                            if self.info['ret'] == '0':
                                self.info['DeviceID'] = 'e' + repr(random.random())[2:17]
                                header = {
                                    "Host": "wx2.qq.com",
                                    "Origin": "https://wx2.qq.com",
                                    "Referer": "https://wx2.qq.com/?&lang=zh_CN"
                                }
                                data = json.dumps({
                                    "BaseRequest":{
                                        "Uin": self.info['wxuin'],
                                        "Sid": self.info['wxsid'],
                                        "Skey": self.info['skey'],
                                        "DeviceID": self.info['DeviceID']
                                    }
                                })
                                result = requests.post(self.baseinfo + self.info['pass_ticket'], cookies=real_cookies, headers=header, data=data)
                                result.encoding = "utf-8"
                                print result.text
                            else:
                                return False
                        else:
                            self.logger.info('登录失败，可能是二维码已超时')
                    else:
                        self.logger.info('网络连接有问题，请检查后重试')
                else:
                    self.logger.info('网络出错，请在github上给我发issue，我的github地址为https://github.com/sml2h3')
            else:
                self.logger.info('网络连接有问题，请检查后重试')
        else:
            self.logger.info('网络连接有问题，请检查后重试')



if __name__ == '__main__':
    Login()