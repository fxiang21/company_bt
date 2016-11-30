#!/bin/env python
# encoding=utf-8

from flask import Flask, Blueprint, render_template, request, g, session, jsonify, redirect, url_for
from flask import current_app
import requests
from lib import monitor as stm
from lib.bean import AlchemyEncoder
from lib.common import record_list, table_args, SqlResultConvert, InfluxData, is_valid_domain_or_ip
from permissions import auth
import json
import hashlib
import sys
import time
from datetime import datetime

reload(sys)
sys.setdefaultencoding('utf-8')

__author__ = 'xiangfeng'

monitor = Blueprint('monitor', __name__)


@monitor.route('', methods=['GET'])
@monitor.route('/all', methods=['GET'])
@auth.require()
def index_page():
    try:
        args = request.values.to_dict()
        if not g.user.is_sam_admin:
            args['creator'] = session.get('CAS_USERNAME', '')
        pl, offset, page = table_args(args.get('perpage', ''), args.get('page', ''))
        r, total = stm.MonitorTargets.query_num(limit=pl, offset=offset, desc='created', **args)
        res = SqlResultConvert.to_list(r)
        for i in res:
            i["live"] = dict()
            i["alive"] = 0
            i["dead"] = 0
            if i.get("monitor_type") == "PING":
                measurement_1 = '%s__icmp_ping_%s' % (i.get('name'), 'alive')
                measurement_2 = '%s__icmp_ping_%s' % (i.get('name'), 'msec')
            else:
                measurement_1 = '%s__net_http_%s' % (i.get('name'), 'alive')
                measurement_2 = '%s__net_http_%s' % (i.get('name'), 'msec')
            cmd1 = "select * from \"%s\" where object='%s' group by station order by time desc limit 1;"\
                  % (measurement_1, i.get('target'))
            cmd2 = "select * from \"%s\" where object='%s' group by station order by time desc limit 1;" \
                   % (measurement_2, i.get('target'))
            r1 = InfluxData.remote_influxdb_execute(cmd1)
            r2 = InfluxData.remote_influxdb_execute(cmd2)
            try:
                res1 = r1.get('results')[0].get('series')
                res2 = r2.get('results')[0].get('series')
            except Exception:
                res1 = []
                res2 = []
            if res1:
                for k in res1:
                    val_index = k.get('columns').index('value')
                    for v in k.get('values'):
                        if v[val_index] == 1:
                            i['alive'] += 1
                        else:
                            i["dead"] += 1
                resp_times = []
                for k in res2:
                    for v in k.get('values'):
                        resp_times.append(v[val_index])
                i['msec_avg'] = round(sum(resp_times) / len(resp_times), 2) if resp_times else 0
            else:
                stations = i.get("stations").split('.')
                for k in stations:
                    i["live"][k] = 0
                i["alive"] = 0
                i['dead'] = len(stations)
                i['msec_avg'] = '---'
        return render_template("monitor/index.html",
                               item='',
                               item1=args.get('monitor_type', ''),
                               res=res,
                               per_page=pl,
                               current_page=page,
                               offset=offset,
                               total_number=total)
    except Exception as e:
        print str(e)
        return "500"


@monitor.route('/new/tips', methods=['GET'])
@auth.require()
def new_tips():
    return render_template("monitor/index.html",
                           item='tips')


@monitor.route('/target/new', methods=['GET'])
@auth.require()
def new_target():
    user = g.user.username
    monitor_type = request.values.get('type', '').upper()
    if not monitor_type:
        return redirect(url_for('monitor.new_tips'))
    if monitor_type == 'PING':
        cms = record_list(stm.CollectPingModel, user)
        ats = record_list(stm.AlarmTemplate, user, **{'alarm_type': monitor_type})
    elif monitor_type == 'HTTP':
        cms = cms = record_list(stm.CollectHttpModel, user)
        ats = record_list(stm.AlarmTemplate, user, **{'alarm_type': monitor_type})
    else:
        cms = list()
        ats = record_list(stm.AlarmTemplate, user, **{'alarm_type': monitor_type})
    try:
        return render_template("monitor/index.html",
                               item='new',
                               item1=monitor_type,
                               monitor_type=monitor_type,
                               cms=cms,
                               teams=record_list(stm.Team, user),
                               stations=record_list(stm.Station, user),
                               ats=ats)
    except Exception as e:
        print str(e)
        return "50000"


@monitor.route('/targets', methods=['GET', 'POST', 'PUT', 'DELETE'])
@auth.require()
def targets_action():
    if request.method == 'GET':
        user = g.user.username
        args = {'mt_id': request.values.get('_id',''),
                'creator': session.get('CAS_USERNAME')}
        r = stm.MonitorTargets.query(**args)
        res = {}
        select_sta = []
        cms = []
        ats = []
        if r:
            res = SqlResultConvert.to_list(r)[0]
            if res['monitor_type'] == 'PING':
                cms = record_list(stm.CollectPingModel, user)
            elif res['monitor_type'] == 'HTTP':
                cms = record_list(stm.CollectHttpModel, user)
            ats = record_list(stm.AlarmTemplate, user, **{'alarm_type': res['monitor_type']})
            # get the selected stations
            r_sta = stm.Station.query_inner_join_names(res['mt_id'])
            if r_sta:
                select_sta = [_id[0] for _id in r_sta]
        try:
            return render_template("monitor/index.html",
                                   item="update",
                                   res=res,
                                   cms=cms,
                                   teams=record_list(stm.Team, user),
                                   select_sta=select_sta,
                                   stations=record_list(stm.Station, user),
                                   monitor_type=res.get('monitor_type', ''),
                                   ats=ats)
        except Exception as e:
            print str(e)
            return str(e)
    elif request.method == 'POST':
        res = dict()
        try:
            req_data = json.loads(request.form.get('data'))
            targets = req_data.get('target', '').split('\r\n')
            del req_data['target']
            req_data['stations'] = '.'.join(req_data['stations'])
            if req_data.get('note_group'):
                req_data['note_group'] = '.'.join(req_data['note_group'])
            req_data['creator'] = session.get('CAS_USERNAME', '')
            for target in targets:
                if req_data.get('monitor_type') == 'PING':
                    if not is_valid_domain_or_ip(target):
                        res.setdefault('failed', []).append(' '.join([target, u'格式不正确']))
                        continue
                if req_data['monitor_type'] == 'HTTP':
                    if target.startswith('https://'):
                        pass
                    elif not target.startswith('http://'):
                        target = 'http://' + target
                _mt = stm.MonitorTargets()
                req_data['target'] = target
                req_data['updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                query_data = {'target': req_data.get('target', ''),
                              'monitor_type': req_data.get('monitor_type', ''),
                              'request_method': req_data.get('request_method', '')}
                if _mt.exist(**query_data):
                    res.setdefault('failed', []).append(' '.join([target, u'已经存在该监控项']))
                    continue
                mt_id = _mt.add(**req_data)
                if mt_id:
                    res.setdefault('success', []).append(target)
                else:
                    res.setdefault('failed', []).append(target)
                stm.Log().add(**{'monitor_name': req_data.get('name'),
                                 'user': g.user.username,
                                 'target': req_data.get("target", '')})
        except Exception as e:
            print str(e)
            res['error'] = str(e)
        return json.dumps(res)
    elif request.method == 'PUT':
        res = dict()
        req_data = json.loads(request.form.get('data'))
        req_data['updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conditions = {'mt_id': req_data.get('_id')}
        req_data['stations'] = '.'.join(req_data['stations'])
        req_data['note_group'] = '.'.join(req_data['note_group'])
        if request.values.get('mt_id', ''):
            del req_data['mt_id']
        status = stm.MonitorTargets.update(conditions, **req_data)

        if status:
            res['success'] = req_data.get('target')
        else:
            res['failed'] = req_data.get('target')
        stm.Log().add(**{'monitor_name': req_data.get('name'),
                         'action': 'UPDATE',
                         'user': g.user.username,
                         'target': req_data.get("target", '')})
        return json.dumps(res)
    elif request.method == 'DELETE':
        del_args = {'mt_id': request.values.get('_id')}
        if not g.user.is_sam_admin:
            del_args['creator'] = g.user.username
        r = stm.MonitorTargets.query_one(**{'mt_id': request.values.get('_id')})
        add_args = {'monitor_name': r.name,
                    'action': 'DELETE',
                    'user': g.user.username,
                    'target': r.target}
        status = stm.MonitorTargets.delete(**del_args)
        if r:
            try:
                stm.Log().add(**add_args)
            except Exception as e:
                print str(e)
        return json.dumps({'status': status})


@monitor.route('/targets/stop', methods=['POST'])
@auth.require()
def target_stop():
    conditions = {'mt_id': request.values.get('_id'),
                  'creator': session.get('CAS_USERNAME')}
    status = stm.MonitorTargets.update(conditions, **{'enabled': request.values.get('enabled') == 'true',
                                                      'updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    r = stm.MonitorTargets.query_one(**{'mt_id': request.values.get('_id')})
    if r:
        stm.Log().add(**{'monitor_name': r.name,
                         'action': 'UPDATE',
                         'user': session.get('CAS_USERNAME'),
                         'target': r.target})
    return jsonify(status=status)


@monitor.route('/cpm', methods=['GET', 'POST'])
@auth.require()
def cpm_models():
    cpm = stm.CollectPingModel()
    if request.method == 'GET':
        args = {'creator': 'ADMIN'}
        r = cpm.query(**args)
        res = list()
        for i in r:
            res.append({'_id': i.cpm_id, 'name': i.name, 'interval': i.interval})
        if request.values.get('username'):
            args = {'creator': request.values.get('username')}
            r2 = cpm.query(**args)
            for j in r2:
                res.append({'_id': j.cpm_id, 'name': j.name, 'interval': j.interval})
        return json.dumps(res)
    elif request.method == 'POST':
        res = dict()
        try:
            req_data = json.loads(request.data)
            for data in req_data:
                if stm.judge_and_add(cpm, request.values.get('username', ''), **data):
                    res.setdefault('success', []).append(data.get('name'))
                else:
                    res.setdefault('failed', []).append(data.get('name'))
        except Exception as e:
            res['error'] = str(e)
        return json.dumps(res)


@monitor.route('/cpm/details/<item>', methods=['GET'])
@auth.require()
def cpm_details(item):
    res = dict()
    if item.isdigit():
        args = {'cpm_id': item}
        cpm = stm.CollectPingModel()
        res_origin = cpm.query(**args)
        for i in res_origin:
            res = {'_id': i.cpm_id, 'interval': i.interval, 'name': i.name, 'creator': i.creator}
            break
    return json.dumps(res)


@monitor.route('/chm/details/<item>', methods=['GET'])
@auth.require()
def chm_details(item):
    res = dict()
    if item.isdigit():
        args = {'chm_id': item}
        chm = stm.CollectHttpModel()
        res_origin = chm.query(**args)
        for i in res_origin:
            res = {'_id': i.chm_id,
                   'interval': i.interval,
                   'name': i.name,
                   'method': i.method,
                   'response':i.response,
                   'postcontent':i.postcontent,
                   'cookie':i.cookie,
                   'match':i.match,
                   'creator': i.creator}
            break
    return json.dumps(res)


@monitor.route('/cm/exist', methods=['GET'])
@auth.require()
def cm_exit():
    data = json.loads(request.data)
    if data.get('cm_type') == 'PING':
        obj = stm.CollectPingModel
    elif data.get('cm_type') == 'HTTP':
        obj = ''
        pass
    else:
        obj = ''
    return jsonify(exist=exist(obj, data.get('username')))


@monitor.route('/cm/info', methods=['GET', 'POST'])
@auth.require()
def cm_info():
    data = request.form.to_dict()
    if data.get('type') == 'PING':
        del data["type"]
        obj = stm.CollectPingModel()
    elif data.get('type') == 'HTTP':
        del data['type']
        obj = stm.CollectHttpModel()
    _id = obj.exist(**data)
    if _id:
        _id = False
    else:
        _id = obj.add(**data)
    return jsonify(_id=_id)


@monitor.route('/atpl/info', methods=['GET', 'POST'])
@auth.require()
def alarm_info():
    if request.method == 'GET':
        pass
    else:
        obj = stm.AlarmTemplate()
        data = request.form.to_dict()

        args = {'name': data.get('name'),
                'creator': g.user.username if g.user.username else data.get('creator')}
        _id = obj.exist(**args)
        if _id:
            _id = False
        else:
            if data.get('alarm_type') == 'PING':
                if not data.get('ping_msec').isdigit():
                    return jsonify(_id=-1, msg=u'请输入数字')
                if data.get('ping_msec'):
                    strategy1 = '>'.join(['icmp_ping_msec', data.get('ping_msec')])
                else:
                    strategy1 = ''
                if data.get('ping_loss'):
                    strategy2 = '>'.join(['icmp_ping_loss', data.get('ping_loss')])
                else:
                    strategy2 = ''
                data['strategy'] = '||'.join([strategy1, strategy2])
            elif data.get('alarm_type') == 'HTTP':
                if not data.get('http_msec').isdigit():
                    return jsonify(_id=-1, msg=u'请输入数字')
                if data.get('http_msec'):
                    strategy1 = '>'.join(['net_http_msec', data.get('http_msec')])
                else:
                    strategy1 = ''
                if data.get('http_alive'):
                    strategy2 = '=='.join(['net_http_alive', data.get('http_alive')])
                else:
                    strategy2 = ''
                data['strategy'] = '||'.join([strategy1, strategy2])
            _id = obj.add(**data)
        return jsonify(_id=_id)


@monitor.route('/atpl/details/<item>', methods=['GET'])
@auth.require()
def atpl_details(item):
    res = dict()
    if item.isdigit():
        args = {'at_id': item}
        cpm = stm.AlarmTemplate()
        res_origin = cpm.query(**args)
        res = json.dumps(res_origin, cls=AlchemyEncoder, check_circular=False)
        return res
    return json.dumps(res)


# *************************show information on monitor items according to charts******
@monitor.route('/detailinfo', methods=['GET'])
@auth.require()
def detail_info():
    mt_id = request.values.get('_id')
    args = {'mt_id': mt_id}
    if not g.user.is_sam_admin:
        args['creator'] = g.user.username
    r = stm.MonitorTargets.query_one(**args)
    try:
        if r:
            alert_tpl = stm.AlarmTemplate.query_one(**{'at_id': r.at_id})
            groups = r.note_group.split('.')
            grps = stm.Team.query(in_column='tid', belong=groups)
            cm = {}
            if r.monitor_type == 'PING':
                cm = stm.CollectPingModel.query_one(**{'cpm_id': r.cm_id})
            elif r.monitor_type == 'HTTP':
                cm = stm.CollectHttpModel.query_one(**{'chm_id': r.cm_id})
            return render_template("monitor/detail_index.html",
                                   item1='overview',
                                   item2='overview',
                                   mt_id=mt_id,
                                   res=r,
                                   cm=cm,
                                   atpl=alert_tpl,
                                   groups=grps)
        return jsonify(message=u'没有找到该监控项,或者您没有权限查看该监控项')
    except Exception as e:
        print str(e)
        return jsonify(status=200)


@monitor.route('/detail/mapinfo', methods=['GET', 'POST'])
@auth.require()
def map_info():
    name = request.values.get('name')
    target = request.values.get('target')
    mtype = request.values.get('mtype')
    method = request.values.get('method')
    if mtype == "HTTP":
        measurement_1 = '/%s__net_http_%s' % (name, '(msec)|(code)|(alive)/')
    else:
        measurement_1 = '/%s__icmp_ping_%s' % (name, '(msec)|(loss)|(alive)/')
    cmd = "select station,value from %s where object='%s' group by station order by time desc limit 1" % (measurement_1, target)
    res = InfluxData.remote_influxdb_execute(cmd)

    if mtype == "HTTP":
        measurement_2 = '%s__net_http_ip' % name
        cmd_ip = "select station,value from %s where object='%s' group by station order by time desc limit 1" % (measurement_2, target)
        res_ip = InfluxData.remote_influxdb_execute(cmd_ip)
        try:
            res.get('results')[0].get('series').extend(res_ip.get('results')[0].get('series'))
        except Exception as e:
            print str(e)
    return json.dumps(res)

@monitor.route('/detail/24hourinfo/<name>', methods=['GET'])
@auth.require()
def tfhour_info(name):
    data = dict()
    stations = request.values.get('stations').split('.')
    for i in stations:
        tmp = stm.Station.query_one(**{'s_id': i})
        data.setdefault(tmp.name, [])
    mtype = request.values.get('mtype', '')
    if mtype == 'HTTP':
        table_name = name + "__net_http_alive"
    else:
        table_name = name + "__icmp_ping_alive"
    now = time.time()
    day_ago = (now - 24 * 60 * 60).__str__().split('.')[0] + '000000000'
    # print now,day_ago
    cmd = "select station,value from \"%s\" where object=\'%s\' and time > %s" %\
          (table_name, request.values.get('target'), day_ago)
    res = InfluxData.remote_influxdb_cmd(cmd)
    if not res:
        return json.dumps(data)
    # print res[table_name]
    label = []  # [time,station,value]
    for i in res[table_name]['columns']:
        label.append(i)
    # 按站点分组
    split_by_station = dict()
    for i in res[table_name]['values']:
        # split_by_station.setdefault(i[label.index('station')], []).append(i)
        if i[label.index('station')] not in split_by_station:
            split_by_station[i[label.index('station')]] = []
        split_by_station[i[label.index('station')]].append(i)
    # 统计站点连续存活或连续挂掉占总时间的比例
    for i in split_by_station:
        total_count = len(split_by_station[i]) + 0.0
        alive = 0
        count = 0
        # start_time = split_by_station[i][0].index('time')
        for j in split_by_station[i]:
            if i not in data:
                data[i] = []
            if int(j[label.index('value')]) != alive:
                if count != 0:
                    data[i].append([count / total_count, alive])
                count = 1
                alive = 0 if alive == 1 else 1
            else:
                # print j
                count += 1
        data[i].append([count / total_count, alive])
    return json.dumps(data)


# @monitor.route('/data/test', methods=['GET'])
# def data_test():
#     cmd = "select * from %s where object='%s' and time > 1471335824000000000"  % ("test02__icmp_ping_msec",'eastmoney.com')
#     print cmd
#     res = InfluxData.remote_influxdb_cmd(cmd)
#     print res
#     return json.dumps(res)


# *****************************************#
def cpm_models_get(obj, username=''):
    args = {'creator': 'ADMIN'}
    r = obj.query(**args)
    res = list()
    for i in r:
        res.append({'_id': i.cpm_id, 'name': i.name, 'interval': i.interval})
    if username:
        args = {'creator': username}
        r2 = obj.query(**args)
        for j in r2:
            res.append({'_id': j.cpm_id, 'name': j.name, 'interval': j.interval})
    return res


def exist(obj, user):
    args = {'creator': user}
    res = obj.exist(**args)
    if res:
        return True
    else:
        args = {'creator': 'ADMIN'}
        res = obj.exist(**args)
    return res


def station_all():
    s = stm.Station()
    kwargs = dict()
    r = s.query(**kwargs)
    res = list()
    if r:
        res = json.dumps(r, cls=AlchemyEncoder, check_circular=False)
        return res
    else:
        return json.dumps(res)



