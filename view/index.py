#!/bin/env python
# encoding=utf-8

__author__ = 'xiangfeng'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from flask import Blueprint, redirect, render_template,request,jsonify,session
from lib.util import cache_key
from flask import current_app,g
import json,hashlib, thread
from permissions import auth
from sendmail import SendHtmlEmail
from lib.util import Username, Auth, IsLogin
import math
from lib.util import get_show_pages
from lib import monitor as stm
from lib.common import record_list, table_args, SqlResultConvert, InfluxData


index = Blueprint('index', __name__)


@index.route('', methods=['GET'])
def index_page():
    try:
        return render_template('homepage.html', m_type='hp')
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




