#!/bin/env python
# encoding=utf-8

__author__ = 'xiangfeng'

import os
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.header import Header
import email
import datetime
from bs4 import BeautifulSoup
import requests
from flask import current_app
#设置命令窗口输出使用中文编码
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from extensions import db
from models.EmailFilter import EmailFilter
from models.EmailFilterCondition import EmailFilterCondition


class AccountManage():
    def __init__(self):
        pass

    def add_user(self):
        pass


class DispatchList():
    def __init__(self):
        pass

