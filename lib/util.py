#!/usr/bin/env python
#encoding=utf-8

__author__ = 'lucky'


import uuid
import datetime
import json
import os
import requests
import hashlib
import re
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

from functools import wraps
from flask import session, current_app
import urllib

from flask import session, current_app, g, redirect, request
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

pipe = None


def GenUUID():
    return str(uuid.uuid4())


def SetPipe(p):
    global pipe
    pipe = p


def SendMsg(data):
    pipe.send(json.dumps(data))


def RecvMsg():
    data = pipe.recv()
    return json.loads(data)


def CurrentTime():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def Username():
    return session.get('CAS_USERNAME')


def Name():
    return session.get('CAS_NAME')


def Number():
    return session.get('CAS_NUMBER')


def IsLogin():
    return Username() is not None


def Auth(resource):
    return True


def row2dict(row):
    d = dict()
    for c in row.__table__.columns:
        d[c.name] = getattr(row, c.name)
    return d


def values2dict(values):
    data = dict()
    for key in values.keys():
        if len(values.getlist(key)) == 1:
            data[key] = values.get(key)
        else:
            data[key] = values.getlist(key)
    return data


def get_show_pages(page, pages):
    page_shows = []
    if page > pages:
        page_shows = []
    else:
        for i in xrange(5):
            if i:
                m1 = page - i
                if m1 in xrange(1,pages+1):
                    page_shows.append(m1)
                m2 = page + i
                if m2 in xrange(1,pages+1):
                    page_shows.append(m2)
            else:
                page_shows.append(page)
            if len(page_shows)>=5:
                break
    page_shows.sort()
    return page_shows


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']


def create_unique_string(str1):
    rand_str = ''.join(map(lambda xx:(hex(ord(xx))[2:]), os.urandom(16)))
    time_now = datetime.datetime.now().strftime('%y%m%d%H%M%S%f')
    unique_str = ''.join([rand_str, time_now, str1])
    return hashlib.md5(unique_str.encode("utf8")).hexdigest()


def validate_email(mail):
    pattern = "^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$"
    if len(mail) > 7:
        if re.match(pattern, mail):
            return True
    return False


def gen_email(self, user, email_suffix):
    if not email_suffix:
        email_suffix = 'dianping.com'
    if not self.validate_email(user):
        user = '@'.join([user, email_suffix])
    return user


def parse_mail_user(user_string):
    """
    parsing user and mail from user_string,
    for example: aaaa<xxxx@dianping.com> --> aaaa, xxxx and <xxxx@dianping.com>
    :param user_string:
    :return: user, account, mail
    """
    p = re.compile(r'<[.a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[.a-zA-Z0-9_-]+>)')
    user_tmp = p.search(user_string)
    if user_tmp:
        user_mail = user_tmp.group()
        user = user_string[:user_string.find(user_mail)]
        tmp = user_mail.split('@')
        if tmp:
            account = tmp[0][1:]
        else:
            account = user
    else:
        user = account = user_string
        user_mail = user_string
    return user, account, user_mail.strip('<>')


def cache_key():
    args = request.values.to_dict()
    args['creator'] = session.get('CAS_USERNAME', '')
    key = request.path + '?' + urllib.urlencode([
        (k, args.get(k)) for k in sorted(args.keys())
    ])
    return key


class PrpCrypt:  # AES加解密算法
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC

    # 加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext)

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip('\0')