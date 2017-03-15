#!/bin/env python
# encoding=utf-8

import os
from lib.docs import DocManage
from flask import Blueprint, redirect, render_template,request,jsonify,session, url_for
from lib import db as data
from lib.common import SqlResultConvert
from lib import docs
from config import REDIS, REDIS_QQ
import redis
from lib.db import DefaultInfo
from random import choice
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


__author__ = 'xiangfeng'

index = Blueprint('index', __name__)
doc_manager = DocManage()
redis_cache = redis.Redis(host=REDIS['host'],port=REDIS['port'], db=REDIS['db'])


@index.route('', methods=['GET'])
def index_page():
    try:
        news = dict()
        total_number_2, docs_list_1 = doc_manager.doc_info("", 5, "", **{"group_id": 28})
        total_number_1, docs_list_2 = doc_manager.doc_info("", 5, "", **{"group_id": 25})
        total_number_3, docs_list_3 = doc_manager.doc_info("", 5, "", **{"group_id": 29})
        sliders = doc_manager.default_category_article_ids("sliders")
        products = doc_manager.default_category_article_ids("products")
        return render_template('homepage.html', m_type='hp', news=news,
                               docs_list_1=docs_list_1, docs_list_2=docs_list_2,
                               docs_list_3=docs_list_3, sliders=sliders, products=products)
    except Exception as e:
        return jsonify(message=str(e))


@index.route("details/<string:item>", methods=["GET"])
def details(item):
    try:
        m_type = "gonsizhuce" if item is None else item.strip()
        number, r = doc_manager.doc_group_info(**{"alias": m_type})
        if r:
            sec_g_list = doc_manager.doc_groups_sec_ids(r[0].d_id)
        else:
            return redirect(url_for('index.index_page'))
        return render_template("content/content_list.html", m_type=m_type, sec_g_list=sec_g_list)
    except Exception as e:
        return jsonify(message=str(e))


@index.route("detail/<string:item>", methods=["GET"])
def detail(item):
    m_type = "corp_register" if item is None else item
    return render_template("content/content_detail.html", m_type=m_type)


@index.route("first_info/<int:_id>", methods=['GET'])
def first_info(_id):
    r = doc_manager.docs_details_first(_id)
    if r:
        return redirect(url_for("source.source_detail", fid=r.d_id))
    else:
        return redirect('source/list/%d' % _id)


@index.route("profile", methods=["GET"])
def profile():
    return render_template("deep_bt.html", m_type="deep_baitong")


@index.route("items/second", methods=['GET'])
def second_items():
    alias = request.values.get('alias')
    try:
        r = doc_manager.sec_items(alias)
        tpl = render_template('header/sec_items.html', r=r)
    except Exception as e:
        tpl = str(e)
    return jsonify(tpl=tpl)


@index.route("url/<string:item>")
def qiao_url(item):
    """
    随机获取百度商桥链接
    :return:
    """
    try:
        user = '__'.join([REDIS_QQ, request.remote_addr])
        url = redis_cache.get(user)
        if not url:
            r = DefaultInfo.query(**{'status': 'enabled', 'category': item})
            if r:
                url = choice([i.content for i in r])
                redis_cache.set(user, url)
                redis_cache.expire(user, 3600)
        return redirect(url)
    except Exception as e:
        return jsonify(message=e)




