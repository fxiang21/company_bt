#!/bin/env python
# encoding=utf-8

__author__ = 'xiangfeng'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from flask import Blueprint, redirect, render_template,request,jsonify,session
from lib import db as data
from lib.common import SqlResultConvert


index = Blueprint('index', __name__)


@index.route('', methods=['GET'])
def index_page():
    try:
        # groups_db = data.NewsGroup.query()
        # groups = SqlResultConvert.to_list(groups_db)
        news = dict()
        # for group in groups:
        #     r, num = data.News.query_num(limit=5, desc="created", **{"group": group.get("ngid")})
        #     news[group.get("ngid")] = SqlResultConvert.to_list(r)
        return render_template('homepage.html', m_type='hp', news=news)
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




