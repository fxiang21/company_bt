#!/bin/env python
# encoding=utf-8

__author__ = 'xiangfeng'

import os
from lib.docs import DocManage
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from flask import Blueprint, redirect, render_template,request,jsonify,session
from lib import db as data
from lib.common import SqlResultConvert


index = Blueprint('index', __name__)
doc_manager = DocManage()


@index.route('', methods=['GET'])
def index_page():
    try:
        # groups_db = data.NewsGroup.query()
        # groups = SqlResultConvert.to_list(groups_db)
        news = dict()
        # for group in groups:
        #     r, num = data.News.query_num(limit=5, desc="created", **{"group": group.get("ngid")})
        #     news[group.get("ngid")] = SqlResultConvert.to_list(r)
        total_number_2, docs_list_1 = doc_manager.doc_info("", 5, "", **{"group_id": 28})
        total_number_1, docs_list_2 = doc_manager.doc_info("", 5, "", **{"group_id": 25})
        total_number_3, docs_list_3 = doc_manager.doc_info("", 5, "", **{"group_id": 29})
        print '.......'
        print docs_list_1
        print docs_list_2
        print docs_list_3
        return render_template('homepage.html', m_type='hp', news=news, docs_list_1=docs_list_1,
                               docs_list_2=docs_list_2, docs_list_3=docs_list_3)
    except Exception as e:
        return jsonify(message=str(e))


@index.route("details/<string:item>", methods=["GET"])
def details(item):
    m_type = "corp_register" if item is None else item
    return render_template("content/content_list.html", m_type=m_type)


@index.route("detail/<string:item>", methods=["GET"])
def detail(item):
    m_type = "corp_register" if item is None else item
    return render_template("content/content_detail.html", m_type=m_type)


@index.route("profile", methods=["GET"])
def profile():
    return render_template("deep_bt.html", m_type="deep_baitong")




