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
    user = Username()
    if user is None:
        return False
    url = current_app.config['OPS_AUTH_URL'] % (user, resource)
    try:
        auth = requests.get(url).json()['auth']
        if auth is not True and auth is not False:
            raise Exception('auth system \' return is not expected.')
    except Exception, e:
        current_app.logger.error('auth user error: %s' % str(e))
        current_app.logger.error('request url: %s' % url)
        auth = False
    return auth


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
