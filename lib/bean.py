#!/bin/env python
# encoding=utf-8

from extensions import db
from flask import current_app
import json
from datetime import datetime
from sqlalchemy.ext.declarative import DeclarativeMeta
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class Bean(object):
    _tbl = ''
    _id = 'id'

    def __init__(self):
        self.tbl = ''

    def add(self, **kwargs):
        for i in kwargs:
            if hasattr(self.tbl, i):
                setattr(self.tbl, i, kwargs[i])
        db.session.add(self.tbl)
        try:
            db.session.commit()
            return getattr(self.tbl, self._id)
        except Exception as e:
            print str(e)
            db.session.rollback()
            current_app.logger.error(str(e))
            return False

    @classmethod
    def delete(cls, **kwargs):
        r = db.session.query(cls._tbl)
        for i in kwargs:
            if hasattr(cls._tbl, i):
                r = r.filter(getattr(cls._tbl, i) == kwargs[i])
        r.delete()
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(str(e))
            return False

    @classmethod
    def update(cls, conditions, **kwargs):
        args = dict()
        for i in kwargs:
            if hasattr(cls._tbl, i):
                args[i] = kwargs[i]
        r = db.session.query(cls._tbl)
        for j in conditions:
            if hasattr(cls._tbl, j):
                r = r.filter(getattr(cls._tbl, j) == conditions[j])
        try:
            r.update(args)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(str(e))
            return False

    @classmethod
    def query(cls, limit=None, offset=None, desc=None, in_column=None, belong=None, **kwargs):
        """
        :param limit:
        :param offset:
        :param desc: order_by
        :param in_column: the column for filtering according to in_ method
        :param belong: list type, for filter in_
        :param kwargs:
        :return:
        """
        r = db.session.query(cls._tbl)
        for i in kwargs:
            if hasattr(cls._tbl, i):
                r = r.filter(getattr(cls._tbl, i) == kwargs[i]) #??多个关键词累积??
        if in_column and belong:
            r = r.filter(getattr(cls._tbl, in_column).in_(belong))
        if desc:
            r = r.order_by(getattr(cls._tbl, desc).desc())
        if offset:
            r = r.offset(offset)
        if limit:
            r = r.limit(limit)
        try:
            db.session.commit()
            return r.all()
        except Exception as e:
            current_app.logger.error(str(e))
            return False

    @classmethod
    def query_num(cls, limit=None, offset=None, desc=None, in_column=None, belong=None, **kwargs):
        """
        :param limit:
        :param offset:
        :param desc: order_by
        :param in_column: the column for filtering according to in_ method
        :param belong: list type, for filter in_
        :param kwargs:
        :return:
        """
        r = db.session.query(cls._tbl)
        for i in kwargs:
            if hasattr(cls._tbl, i):
                r = r.filter(getattr(cls._tbl, i) == kwargs[i])
        if in_column and belong:
            r = r.filter(getattr(cls._tbl, in_column).in_(belong))
        if desc:
            r = r.order_by(getattr(cls._tbl, desc).desc())
        total = r.count()
        if offset:
            r = r.offset(offset)
        if limit:
            r = r.limit(limit)
        try:
            db.session.commit()
            return r.all(), total
        except Exception as e:
            current_app.logger.error(str(e))
            return False, False

    @classmethod
    def query_one(cls, in_column=None, belong=None, **kwargs):
        """
        :param in_column: the column for filtering according to in_ method
        :param belong: list type, for filter in_
        :param kwargs:
        :return: one result
        """
        r = db.session.query(cls._tbl)
        for i in kwargs:
            if hasattr(cls._tbl, i):
                r = r.filter(getattr(cls._tbl, i) == kwargs[i])
        if in_column and belong:
            r = r.filter(getattr(cls._tbl, in_column).in_(belong))
        try:
            db.session.commit()
            return r.first()
        except Exception as e:
            current_app.logger.error(str(e))
            return False

    @classmethod
    def exist(cls, **kwargs):
        r = db.session.query(cls._tbl)
        for i in kwargs:
            if hasattr(cls._tbl, i):
                r = r.filter(getattr(cls._tbl, i) == kwargs[i])
        r = r.first()
        if r:
            return getattr(r, cls._id)
        else:
            return False

    @classmethod
    def exist_except_self(cls, _id, **kwargs):
        r = db.session.query(cls._tbl)
        for i in kwargs:
            if hasattr(cls._tbl, i):
                r = r.filter(getattr(cls._tbl, i) == kwargs[i])
        r = r.first()
        if r and r.chm_id != int(_id):
            return getattr(r, cls._id)
        else:
            return False


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    if isinstance(data, datetime):
                        data = data.strftime('%Y-%m-%d %H:%M:%S')
                    json.dumps(data)
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            return fields
        return json.JSONEncoder.default(self, obj)


# def new_alchemy_encoder():
#     _visited_objs = []
#
#     class AlchemyEncoder(json.JSONEncoder):
#         def default(self, obj):
#             if isinstance(obj.__class__, DeclarativeMeta):
#                 # don't re-visit self
#                 if obj in _visited_objs:
#                     return None
#                 _visited_objs.append(obj)
#
#                 # an SQLAlchemy class
#                 fields = {}
#                 for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
#                     data = obj.__getattribute__(field)
#                     try:
#                         if isinstance(data, datetime):
#                             data=data.strftime('%Y-%m-%d %H:%M:%S')
#                         json.dumps(data) # this will fail on non-encodable values, like other classes
#                         fields[field] = data
#                     except TypeError:
#                         fields[field] = None
#                 return fields
#
#             return json.JSONEncoder.default(self, obj)
#     return AlchemyEncoder




