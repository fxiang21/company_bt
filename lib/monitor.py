#!/bin/env python
# encoding=utf-8

from extensions import db
from flask import current_app
from models import station_monitor as model
from .bean import Bean
import copy
import sys
from flask import request
reload(sys)
sys.setdefaultencoding('utf-8')


class CollectPingModel(Bean):

    _tbl = model.CollectPingModel
    _id = 'cpm_id'
    tid = 'cpm_id'

    def __init__(self):
        super(CollectPingModel, self).__init__()
        self.tbl = model.CollectPingModel()

    @classmethod
    def exist(self, **kwargs):
        r = db.session.query(self._tbl)
        for i in kwargs:
            if i == 'creator':
                r = r.filter(getattr(self._tbl, i) == 'ADMIN')
            elif hasattr(self._tbl, i):
                r = r.filter(getattr(self._tbl, i) == kwargs[i])
        r = r.first()
        if r:
            return getattr(CollectPingModel, self._id)
        else:
            return super(CollectPingModel, self).exist(**kwargs)


class CollectHttpModel(Bean):

    _tbl = model.CollectHttpModel
    _id = 'chm_id'
    tid = 'chm_id'

    def __init__(self):
        super(CollectHttpModel, self).__init__()
        self.tbl = model.CollectHttpModel()

    @classmethod
    def exist(self, **kwargs):
        r = db.session.query(self._tbl)
        for i in kwargs:
            print i,kwargs[i]
            if i == 'creator':
                r = r.filter(getattr(self._tbl, i) == 'ADMIN')
            elif hasattr(self._tbl, i):
                r = r.filter(getattr(self._tbl, i) == kwargs[i])
        r = r.first()
        if r:
            return getattr(CollectHttpModel, self._id)
        else:
            return super(CollectHttpModel, self).exist(**kwargs)

    @classmethod
    def exist_except_self(self, id, **kwargs):
        r = db.session.query(self._tbl)
        for i in kwargs:
            if i == 'creator':
                r = r.filter(getattr(self._tbl, i) == 'ADMIN')
            elif hasattr(self._tbl, i):
                r = r.filter(getattr(self._tbl, i) == kwargs[i])
        r = r.first()
        if r and r.getattr(self._tbl, '_id') != id:
            return getattr(r, self._id)
        else:
            return super(CollectHttpModel, self).exist_except_self(id, **kwargs)


class AlarmTemplate(Bean):

    _tbl = model.AlarmTpl
    _id = 'at_id'
    tid = 'at_id'

    def __init__(self):
        super(AlarmTemplate, self).__init__()
        self.tbl = model.AlarmTpl()

    def add(self, **kwargs):
        exist_id = super(AlarmTemplate, self).exist(**kwargs)
        if not exist_id:
            exist_id = super(AlarmTemplate, self).add(**kwargs)
        return exist_id


    @classmethod
    def exist(self, **kwargs):
        r = db.session.query(self._tbl)
        for i in kwargs:
            if i == 'creator':
                r = r.filter(getattr(self._tbl, i) == 'ADMIN')
            elif hasattr(self._tbl, i):
                r = r.filter(getattr(self._tbl, i) == kwargs[i])
        r = r.first()
        if r:
            return getattr(AlarmTemplate, self._id)
        else:
            return super(AlarmTemplate, self).exist(**kwargs)


class MonitorTargets(Bean):

    _tbl = model.MonitorTarget
    _id = 'mt_id'
    tid = 'mt_id'

    def __init__(self):
        super(MonitorTargets, self).__init__()
        self.tbl = model.MonitorTarget()

    def add(self, **kwargs):
        for i in kwargs:
            if hasattr(self.tbl, i):
                setattr(self.tbl, i, kwargs[i])
        db.session.add(self.tbl)
        print getattr(self.tbl, self._id)
        try:
            db.session.commit()
            print getattr(self.tbl, self._id)
            stations = kwargs.get('stations').split('.')
            for station in stations:
                rst = model.RelStaTarget()
                rst.s_id = eval(station) if station.isdigit() else ''
                rst.mt_id = getattr(self.tbl, self._id)
                db.session.add(rst)
            db.session.commit()
            return getattr(self.tbl, self._id)
        except Exception as e:
            db.session.rollback()
            print str(e)
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
        except Exception as e:
            current_app.logger.error(str(e))
            return False
        if kwargs.get('stations'):
            stations = kwargs.get('stations').split('.')
            for station in stations:
                rst = model.RelStaTarget()
                res = RelStationTarget.query(**{'s_id': eval(station) if station.isdigit() else '',
                                                'mt_id': conditions['mt_id']})
                if res:
                    rst.rst_id = res[0].rst_id
                rst.s_id = eval(station) if station.isdigit() else ''
                rst.mt_id = conditions['mt_id']
                db.session.merge(rst)
        try:
            db.session.commit()
            return True
        except Exception as e:
            print str(e)
            db.session.rollback()
            current_app.logger.error(str(e))
            return False


class Station(Bean):

    _tbl = model.Station
    _id = 's_id'
    tid = 's_id'

    def __init__(self):
        super(Station, self).__init__()
        self.tbl = model.Station()

    @classmethod
    def query_inner_join_names(cls, mt_id):
        r = db.session.query(cls._tbl.s_id).join(model.RelStaTarget, model.RelStaTarget.s_id == cls._tbl.s_id).\
            filter(model.RelStaTarget.mt_id == mt_id).all()
        return r


class RelStationTarget(Bean):

    _tbl = model.RelStaTarget
    _id = 'rst_id'
    tid = 'rst_id'

    def __init__(self):
        super(RelStationTarget, self).__init__()
        self.tbl = model.RelStaTarget()


class Receiver(Bean):

    _tbl = model.User
    _id = 'uid'
    tid = 'uid'

    def __init__(self):
        super(Receiver, self).__init__()
        self.tbl = model.User()

    @classmethod
    def exist_name(cls, **kwargs):
        args = {'name': kwargs.get('name'), 'creator': 'ADMIN'}
        if super(Receiver, cls).exist(**args):
            return True
        return super(Receiver, cls).exist(**kwargs)


class Log(Bean):

    _tbl = model.Log
    _id = 'l_id'
    tid = 'l_id'

    def __init__(self):
        super(Log, self).__init__()
        self.tbl = model.Log()


class Team(Bean):

    _tbl = model.Team
    _id = 'tid'
    tid = 'tid'

    def __init__(self):
        super(Team, self).__init__()
        self.tbl = model.Team()

    @classmethod
    def team_users(cls, tid):
        r = db.session.query(model.RelTeamUser.uid).filter(model.RelTeamUser.tid == tid).all()
        users = list()
        for i in r:
            tmp = db.session.query(model.User).filter(model.User.uid == i.uid).first()
            users.append({"uid": tmp.uid,
                          "name": tmp.name,
                          "nickname": tmp.nickname,
                          "email": tmp.email,
                          "qq": tmp.qq,
                          "phone": tmp.phone,
                          "creator": tmp.creator})
        return users

    def exist(self, **kwargs):
        r = db.session.query(self._tbl)
        for i in kwargs:
            if i == 'creator':
                r = r.filter(getattr(self._tbl, i) == 'ADMIN')
            elif hasattr(self._tbl, i):
                r = r.filter(getattr(self._tbl, i) == kwargs[i])
        r = r.first()
        if r:
            return getattr(r, self._id)
        else:
            return super(Team, self).exist(**kwargs)


class RelationTeamUser(Bean):
    _tbl = model.RelTeamUser
    _id = 'rid'
    tid = 'rid'

    def __init__(self):
        super(RelationTeamUser, self).__init__()
        self.tbl = model.RelTeamUser()

    def update_new(self, **kwargs):
        del_args = {'tid': kwargs.get('tid')}
        if super(RelationTeamUser, self).delete(**del_args):
            return super(RelationTeamUser, self).add(**kwargs)
        else:
            return False


def judge_and_add(action_obj, username, **data):
    data_judge = copy.copy(data)
    data_add = copy.copy(data)
    if 'interval' in data_judge:  # for judge if the data exist in db
        del data_judge['interval']
    if 'creator' not in data:  # for add data
        data_judge['creator'] = username
        data_add['creator'] = username
    if action_obj.exist(**data_judge):
        return False
    return action_obj.add(**data_add)



