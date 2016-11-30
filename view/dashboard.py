#!/bin/env python
# encoding=utf-8

from flask import Blueprint, render_template, request, session, g
from lib.common import record_list, table_args, SqlResultConvert, InfluxData
import requests
from lib import monitor as stm
from lib.util import cache_key
from extensions import cache
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

__author__ = 'xiangfeng'


dashboard = Blueprint('dashboard', __name__)


@dashboard.route('', methods=['GET'])
@cache.cached(timeout=60, key_prefix=cache_key)
def index():
    try:
        args = request.values.to_dict()
        if not g.user.is_sam_admin:
            args['creator'] = g.user.username
        pl, offset, page = table_args(args.get('pl', ''), args.get('page', ''))
        r, total = stm.MonitorTargets.query_num(limit=pl, offset=offset, desc='created', **args)
        res = SqlResultConvert.to_list(r)
        for i in res:
            i["live"] = dict()
            i["alive"] = 0
            i["dead"] = 0
            measurement_1 = '%s__icmp_ping_%s' % (i.get('name'), 'alive')
            measurement_2 = '%s__icmp_ping_%s' % (i.get('name'), 'msec')
            cmd1 = "select * from %s where object='%s' group by station order by time desc limit 1;"\
                  % (measurement_1, i.get('target'))
            cmd2 = "select * from %s where object='%s' group by station order by time desc limit 1;" \
                   % (measurement_2, i.get('target'))
            res1 = InfluxData.remote_influxdb_cmd(cmd1)
            res2 = InfluxData.remote_influxdb_cmd(cmd2)
            tmp1 = res1.values()[0].values()
            station = tmp1[2].get('station')
            val_index = tmp1[1].index('value')
            for j in tmp1[0]:
                i["live"][station] = j[val_index]
                if j[val_index] == 1:
                    i["alive"] += 1
                else:
                    i["dead"] += 1
            tmp2 = res2.values()[0].values()

            resp_times = []
            for k in tmp2[0]:
                resp_times.append(k[val_index])
            i['msec_avg'] = round(sum(resp_times)/len(resp_times), 2) if resp_times else 0
        return render_template("dashboard/index.html",
                               item='',
                               item1=args.get('monitor_type', ''),
                               data=res,
                               pl=pl,
                               page=page,
                               offset=offset,
                               total=total)
    except Exception as e:
        print str(e)
        return "500"
