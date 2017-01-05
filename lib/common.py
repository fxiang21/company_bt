#!/usr/bin/env python
# -*-coding:utf8-*-

from sqlalchemy.ext.declarative import DeclarativeMeta
from datetime import datetime
# from lib import monitor as stm
from flask import current_app
import requests
import json
import hashlib
import redis
import config
import re

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

redis_cache = redis.StrictRedis(host=config.REDIS.get("address"), port=config.REDIS.get('port'), db=config.REDIS.get('db'))


class SqlResultConvert:

    def __init__(self):
        pass

    @classmethod
    def to_list(cls, results):
        res = list()
        for obj in results:
            res.append(cls.sa_obj_to_dict(obj))
        return res

    @classmethod
    def format(cls, data):
        if isinstance(data, datetime):
            data = data.strftime('%Y-%m-%d %H:%M:%S')
        return data

    @classmethod
    def sa_obj_to_dict(cls, obj, filtrate=None, rename=None):
        """
        sqlalchemy object -->> dict
        `filtrate`  column for filter
                    the type is list or tuple
        `rename`    the column for rename, action after filter function
                    type:dict
                    key is the old name and value is the new name
        """
        if isinstance(obj.__class__, DeclarativeMeta):
            cla = obj.__class__.__mro__
            cla = filter(lambda c: hasattr(c, '__table__'), filter(lambda c: isinstance(c, DeclarativeMeta), cla))
            columns = []
            map(lambda c: columns.extend(c.__table__.columns), cla[::-1])
            # columns = obj.__table__.columns
            if filtrate and isinstance(filtrate, (list, tuple)):
                fields = dict(map(lambda c: (c.name, cls.format(getattr(obj, c.name))), filter(lambda c: not c.name in filtrate, columns)))
            else:
                fields = dict(map(lambda c: (c.name, cls.format(getattr(obj, c.name))), columns))
            # fields = dict([(c.name, getattr(obj, c.name)) for c in obj.__table__.columns])
            if rename and isinstance(rename, dict):
                # remove the items witch kew is as same as value
                _rename = dict(filter(lambda (k, v): str(k) != str(v), rename.iteritems()))
                # if the old key not exist, the new key default value is None and
                # if the new key already exist in the old key then old key will be be covered

                # map(lambda (k, v): fields.setdefault(v, fields.pop(k, None)), _rename.iteritems())
                map(lambda (k, v): fields.update({v: fields.pop(k, None)}), _rename.iteritems())
            return fields
        else:
            return {}


class InfluxData:

    def __init__(self):
        pass

    # @classmethod
    # def remote_influxdb_cmd(cls, cmd):
    #     rv = g_cache.get(cmd)
    #     if rv:
    #         return rv
    #     else:
    #         headers = {"Content-Type": "application/x-www-form-urlencoded"}
    #         data = {'cmd': cmd}
    #         r1 = requests.get(current_app.config.get('CMD_EXE_API'), params=data, headers=headers)
    #         r = cls.tidy_series_result(r1)
    #         g_cache.set(cmd, r, timeout=60)
    #         return r
    """
    {u'results': [
        {u'series':
            [
                {
                    u'values': [
                                    [
                                         1477025109,
                                         u'HTTP',
                                         u'http://spzhcs.eastmoney.com/rtcs1?type=rtcs_get_rank&khqz=116&rankType=0&recIdx=0&recCnt=20&rankid=0&userId=8224013323114636&cb=jQuery111307246043437659523_1476945400188&_=1476945400189',
                                         1
                                    ]
                                ],
                    u'name': u'contest__net_http_alive',
                    u'columns': [u'time', u'mtype', u'object', u'value'],
                    u'tags': {u'station': u'shdx2'}
                },
                {
                    u'values': [[1477025120, u'HTTP',
                                             u'http://spzhcs.eastmoney.com/rtcs1?type=rtcs_get_rank&khqz=116&rankType=0&recIdx=0&recCnt=20&rankid=0&userId=8224013323114636&cb=jQuery111307246043437659523_1476945400188&_=1476945400189',
                                             1]],
                    u'name': u'contest__net_http_alive',
                    u'columns': [u'time', u'mtype', u'object', u'value'],
                    u'tags': {u'station': u'shdx'}}]
                }
            ]
    }
                                """
    @classmethod
    def remote_influxdb_cmd(cls, cmd):
        redis_id = hashlib.md5(cmd.encode("utf8")).hexdigest()
        r = redis_cache.get("influx:%s" % redis_id)
        if r:
            return json.loads(r)
        else:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {'cmd': cmd}
            try:
                r1 = requests.get(current_app.config.get('CMD_EXE_API'), params=data, headers=headers).json()
                r = cls.tidy_series_result(r1)
                redis_cache.set("influx:%s" % redis_id, json.dumps(r))
                redis_cache.expire("influx:%s" % redis_id, 60)
                return r
            except Exception as e:
                print str(e)
                current_app.logger.error(str(e))
                return {}

    @classmethod
    def remote_influxdb_execute(cls, cmd):
        redis_id = hashlib.md5(cmd.encode("utf8")).hexdigest()
        r = redis_cache.get("influx:%s" % redis_id)
        if r:
            return json.loads(r)
        else:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {'cmd': cmd}
            try:
                r1 = requests.get(current_app.config.get('CMD_EXE_API'), params=data, headers=headers).json()
                redis_cache.set("influx:%s" % redis_id, json.dumps(r1))
                redis_cache.expire("influx:%s" % redis_id, 60)
                return r1
            except Exception as e:
                print str(e)
                current_app.logger.error(str(e))
                return []

    @classmethod
    def tidy_series_result(cls, r):
        result = dict()
        if r.get('results')[0]:
            try:
                res = r.get('results')[0]
                for i in res.get('series'):
                    name = i['name']
                    del i['name']
                    result[name] = i
            except Exception as e:
                current_app.logger.info(str(e))
        return result


# def record_list(obj, username, **kwargs):
#     res = list()
#     if issubclass(obj, stm.Station):
#         r = obj.query(**kwargs)
#         for i in r:
#             res.append({'_id': i.s_id, 'name': i.alias})
#     # elif issubclass(obj, stm.Receiver):
#     #     r = obj.query(**{})
#     #     for i in r:
#     #         res.append({'_id': i.uid, 'name': i.name})
#     elif issubclass(obj, stm.AlarmTemplate):
#         args = {'creator': 'ADMIN', 'alarm_type': kwargs.get('alarm_type', '')}
#         r = obj.query(**args)
#         for i in r:
#             res.append({'_id': i.at_id, 'name': i.name})
#         if username:
#             args = {'creator': username, 'alarm_type': kwargs.get('alarm_type', '')}
#             r2 = obj.query(**args)
#             for j in r2:
#                 res.append({'_id': j.at_id, 'name': j.name})
#     else:
#         args = {'creator': 'ADMIN'}
#         r = obj.query(**args)
#         for i in r:
#             res.append({'_id': getattr(i, obj.tid), 'name': i.name})
#         if username:
#             args = {'creator': username}
#             r2 = obj.query(**args)
#             for j in r2:
#                 res.append({'_id': getattr(j, obj.tid), 'name': j.name})
#     return res


def get_show_pages(page, pages):
    page_shows = []
    if page > pages:
        page_shows = []
    else:
        for i in xrange(5):
            if i:
                m1 = page - i
                if m1 in xrange(1, pages+1):
                    page_shows.append(m1)
                m2 = page + i
                if m2 in xrange(1, pages+1):
                    page_shows.append(m2)
            else:
                page_shows.append(page)
            if len(page_shows) >= 5:
                break
    page_shows.sort()
    return page_shows


def table_args(pl, page):
    """
    :param pl: page list
    :param page:
    :return:
    """
    pl = eval(pl) if pl.isdigit() and eval(pl) in [10, 25, 50, 100] else 10
    page = eval(page) if page.isdigit() else 1
    offset = (page - 1) * pl if page > 1 else 0
    return pl, offset, page
    # result = []
    # r = op_on_api('%s&page=%d&count=%d' % (url, page, per_page))
    # total_number = r.get('numfound')
    # pages = int(math.ceil(float(total_number)/per_page))
    # page_shows = get_show_pages(page, pages)


def is_valid_domain_or_ip(name):
    p = re.compile(r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$|'
                   r'^(2[0-5]{2}|2[0-4][0-9]|1?[0-9]{1,2}).(2[0-5]{2}|2[0-4][0-9]|'
                   r'1?[0-9]{1,2}).(2[0-5]{2}|2[0-4][0-9]|1?[0-9]{1,2}).(2[0-5]{2}|2[0-4][0-9]|1?[0-9]{1,2})$')
    return p.search(name)
