#!/bin/env python
# encoding=utf-8

from flask import Blueprint, render_template, g, session, request, jsonify
from lib import monitor as stm
from lib.common import record_list
import json
from lib.common import record_list, table_args, SqlResultConvert
from permissions import auth
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

__author__ = 'xiangfeng'


config = Blueprint('config', __name__)


@config.route('', methods=['GET'])
@config.route('/team', methods=['GET'])
@auth.require()
def team_page():
    args = request.values.to_dict()
    args['creator'] = session.get('CAS_USERNAME', '')
    pl, offset, page = table_args(args.get('perpage', ''), args.get('page', ''))
    r, total = stm.Team.query_num(limit=pl, offset=offset, desc='created', **args)
    res = SqlResultConvert.to_list(r)
    try:
        return render_template("config/index.html",
                               item='team',
                               item2='view',
                               teams=res,
                               per_page=pl,
                               offset=offset,
                               current_page=page,
                               total_number=total)
    except Exception as e:
        print str(e)
        return jsonify(status=200)


@config.route('/user', methods=['GET', 'POST', 'PUT', 'DELETE'])
@auth.require()
def user_page():
    if request.method == 'GET':
        args = request.values.to_dict()
        creator = session.get('CAS_USERNAME', '')
        pl, offset, page = table_args(args.get('perpage', ''), args.get('page', ''))
        r, total = stm.Receiver.query_num(limit=pl,
                                          offset=offset,
                                          desc='created',
                                          in_column='creator',
                                          belong=['ADMIN', creator])
        res = SqlResultConvert.to_list(r)
        return render_template("config/index.html",
                               item='user',
                               item2='view',
                               users=res,
                               per_page=pl,
                               offset=offset,
                               current_page=page,
                               total_number=total)
    elif request.method == 'PUT':
        kwargs = request.form.to_dict()
        if '_id' not in kwargs:
            return jsonify(status=0, msg=u'没有用户id')
        conditions = {'uid': kwargs.get('_id')}
        del kwargs['_id']
        status = stm.Receiver.update(conditions, **kwargs)
        return jsonify(status=status, msg='')
    elif request.method == 'POST':
        creator = session.get('CAS_USERNAME')
        data = request.form.to_dict()
        data['creator'] = creator
        q = {'name': data.get('name'), 'creator': creator}
        if stm.Receiver.exist_name(**q):
            return jsonify(status=-1)
        else:
            status = stm.Receiver().add(**data)
            return jsonify(status=status)


@config.route('/template/ping',methods=['GET', 'POST', 'PUT', 'DELETE'])
@auth.require()
def template_ping_page():
    if request.method == 'GET': #请求显示数据
        args = request.values.to_dict() #格式化参数
        creator = session.get('CAS_USERNAME','') #获得登陆用户
        pl, offset, page = table_args(args.get('perpage',''), args.get('page','')) #页面显示参数
        r, total = stm.CollectPingModel.query_num(limit=pl,
                                          offset=offset,
                                          desc='cpm_id',
                                          in_column='creator',
                                          belong=['ADMIN',creator]) #查询内容
        res = SqlResultConvert.to_list(r)
        for i in res:
            print i
        return render_template("config/index.html",
                               item='template_ping',
                               item2='view',
                               templates=res,
                               per_page=pl,
                               offset=offset,
                               current_page=page,
                               total_number=total)
    elif request.method == 'PUT': #update
        kwargs = request.form.to_dict()
        if '_id' not in kwargs:
            return jsonify(status=0, msg=u'没有PING报警模版id')
        conditions = {'cpm_id':kwargs.get('_id')}
        del kwargs['_id']
        status = stm.CollectPingModel.update(conditions,**kwargs)
        return jsonify(status=status, msg='')
    elif request.method == 'POST':
        creator = session.get('CAS_USERNAME')
        data = request.form.to_dict()
        data['creator'] = creator
        q = {'name': data.get('name'), 'creator': creator}
        if stm.CollectPingModel().exist(**q):
            return jsonify(status=-1)
        else:
            status = stm.CollectPingModel().add(**data)
            return jsonify(status=status)


@config.route('/template/http',methods=['GET', 'POST', 'PUT', 'DELETE'])
@auth.require()
def template_http_page():
    if request.method == 'GET': #请求显示数据
        args = request.values.to_dict() #格式化参数
        creator = session.get('CAS_USERNAME','') #获得登陆用户
        pl, offset, page = table_args(args.get('perpage',''), args.get('page','')) #页面显示参数
        r, total = stm.CollectHttpModel.query_num(limit=pl,
                                          offset=offset,
                                          desc='chm_id',
                                          in_column='creator',
                                          belong=['ADMIN',creator]) #查询内容
        res = SqlResultConvert.to_list(r)
        return render_template("config/index.html",
                               item='template_http',
                               item2='view',
                               templates=res,
                               per_page=pl,
                               offset=offset,
                               current_page=page,
                               total_number=total)
    elif request.method == 'PUT':
        kwargs = request.form.to_dict()
        if kwargs.get('method') == 'GET':
            kwargs['postcontent'] = ''
        elif kwargs.get('method') == 'HEAD':
            kwargs['postcontent'] = ''
            kwargs['response'] = ''
            kwargs['match'] = 'ignore'
        if '_id' not in kwargs:
            return jsonify(status=0, msg=u'没有HTTP报警模版id')
        q = dict()
        q['creator'] = session.get("CAS_USERNAME")
        q['name'] = kwargs.get("name")
        if stm.CollectHttpModel.exist_except_self(kwargs["_id"],**q):
            return jsonify(status = -1)
        conditions = {'chm_id':kwargs.get('_id')}
        del kwargs['_id']
        status = stm.CollectHttpModel().update(conditions,**kwargs)
        return jsonify(status=status,msg='')
    elif request.method == 'POST':
        creator = session.get('CAS_USERNAME')
        data = request.form.to_dict()
        if data.get('method') == 'GET':
            del data['postcontent']
        elif data.get('method') == 'HEAD':
            del data['postcontent']
            del data['response']
            del data['match']
        data["creator"] = creator
        q = {'name':data.get('name'),'creator':creator}
        if stm.CollectHttpModel().exist(**q):
            return jsonify(status=-1)
        else:
            status = stm.CollectHttpModel().add(**data)
            return jsonify(status=status)


@config.route('/team/update/users', methods=['GET'])
@auth.require()
def update_users():
    team_ids = json.loads(request.values.get('team_ids'))
    users_exists_origin = team_children(team_ids)
    users_exists = list()
    for i in users_exists_origin:
        users_exists.append({'_id': i.get('uid'), 'name': i.get('name')})
    user = g.user.username if g.user.username else 'ADMIN'
    users_all = record_list(stm.Receiver, user)
    return jsonify(users_exists=users_exists, users_all=users_all)


@config.route('/users', methods=['GET'])
@auth.require()
def all_users():
    user = g.user.username if g.user.username else 'ADMIN'
    teams = record_list(stm.Receiver, user)
    return json.dumps(teams)


@config.route('/team/users', methods=['GET', 'POST'])
@auth.require()
def team_users_list():
    if request.method == 'GET':
        team_ids = json.loads(request.values.get('team_ids'))
        users = team_children(team_ids)
        return jsonify(status=True, users=users)
    else:
        instance_team = stm.Team()
        forms = request.form.to_dict()
        user_ids = json.loads(request.values.get('user_ids'))
        team_args = {'name': request.values.get('team_name'), 'creator': g.user.username if g.user.username else 'ADMIN'}
        team_id = request.values.get('team_id', '')
        if not team_id:
            if not instance_team.exist(**team_args):
                team_id = instance_team.add(**team_args)
                if not team_id:
                    return jsonify(status=False)
            else:
                return jsonify(status=False)
        status = instance_team.update({'tid': team_id}, **team_args)
        if not status:
            return jsonify(status=status)
        relations = {'tid': team_id}
        stm.RelationTeamUser.delete(**relations)
        for i in user_ids:
            instance_rel = stm.RelationTeamUser()
            relations['uid'] = i
            _ = instance_rel.add(**relations)
        need_users = forms.get('need_users') == 'true'
        if need_users:
            users = list()
            team_ids = json.loads(request.values.get('team_ids', '[]'))
            team_ids.append(team_id)
            for tid in team_ids:
                user = stm.Team.team_users(tid)
                users.extend(user)
            unduplicate_users = list()
            for i in users:
                if i not in unduplicate_users:
                    unduplicate_users.append(i)
            return jsonify(status=True, users=unduplicate_users, team_id=team_id)
        else:
            return jsonify(status=True)


def team_children(team_ids):
    users = list()
    for tid in team_ids:
        user = stm.Team.team_users(tid)
        users.extend(user)
    unduplicate_users = list()
    for i in users:
        if i not in unduplicate_users:
            unduplicate_users.append(i)
    return unduplicate_users



