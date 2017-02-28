#coding=utf-8
import os
import sys
sys.path.append(os.path.abspath('module'))
reload(sys)
sys.setdefaultencoding('utf-8')
import json
from Logger.Logger import Logger
from Login.Login import  Login

class Controller(object):
    def __init__(self):
        self.logger = Logger('ControllerCenter')
        self.logger.info('#################################################################')
        self.logger.info("#欢迎来到sml2h3的微信机器人，下面是我的菜单，请回复菜单编号后回车 #")
        self.logger.info("#作者:sml2h3 Github:https://github.com/sml2h3                   #")
        self.logger.info("#作者博客:https://www.fkgeek.com                                #")
        self.logger.info("#1、启动微信机器人                                                #")
        self.logger.info('#2、访问作者博客                                                #')
        self.logger.info('#################################################################')
        flag = True
        while flag:
            command = raw_input('>>')
            if command == '1':
                flag = False
                self._run()

    def _run(self):
        return