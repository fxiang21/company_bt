# -*- coding:utf-8 -*- 

__author__ = 'xiangfeng'

from flask import Markup, current_app
import requests


def markup(content):
    return Markup(content)


def auth(username, resource):
    return True


def is_admin(obj):
    return obj.is_sam_admin


def get_qq_face(qq):
    url = current_app.config.get('GET_QQ_FACE')
    ret = requests.get(url % qq).json()
    return ret.get(qq, '')


def user_details(user):
    try:
        ret = requests.get('http://ops.auth.dp/userService/queryEmployeeByKeyword?keyword=%s' % user).json()
        if ret:
            return ret[0]
    except Exception as e:
        current_app.logger.error(str(e))
        return {}


def wx_portrait(user_number):
    try:
        ret = requests.get('http://ops.auth.dp/contactsService/getUser?userId=%s' % user_number).json()
        return ret.get('user').get('avatar', '') if ret.get('user') else '/static/dist/img/user2-160x160.jpg'
    except Exception, e:
        current_app.logger.error(str(e))
        return '/static/dist/img/user2-160x160.jpg'


def content_parse(a):
    tmp = a.split(' ')
    res = list()
    for i in tmp:
        if i.strip():
            res.append(i.strip())
    return res
