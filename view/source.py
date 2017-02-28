#!/bin/env python
# encoding=utf-8

from flask import Blueprint, render_template, request, jsonify
from lib.docs import DocManage
from lib.db import News, NewsGroup
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

__author__ = 'xiangfeng'


source = Blueprint('source', __name__)
doc_manager = DocManage()


@source.route('/', methods=['GET'])
def index():
    return render_template("detail/index.html")


@source.route('/detail/<fid>', methods=['GET'])
def source_detail(fid):
    f = doc_manager.docs_details(fid)
    if not f:
        pass
    else:
        sec_id = f.group_id
        sec_g_detail = doc_manager.group_sec_detail(sec_id)
        first_detail = doc_manager.group_detail(sec_g_detail.get('group_id'))

        sec_g_list = doc_manager.doc_groups_sec_ids(sec_g_detail.get('group_id'))
        return render_template("content/content_detail.html", doc_details=f, first_detail=first_detail,
                               sec_g_detail=sec_g_detail, sec_g_list=sec_g_list)


    # group = request.values.get('group')
    # r = NewsGroup.query_one(**{"name": item})
    # if r:
    #     r1 = News.query(**{"group": group,'category':r.ngid})
    #     # if r1:
    #
    # print '.....'
    # print r
    # print r.alias
    # NewsGroup.query(**{})
    # query(cls, limit=None, offset=None, desc=None, in_column=None, belong=None, **kwargs):
    return render_template("content/list_detail.html")


@source.route('/list/<sec_id>', methods=['GET'])
def list_sec(sec_id):
    total_number, docs_list = doc_manager.doc_info("", "", "", **{"group_id": sec_id})
    sec_g_detail = doc_manager.group_sec_detail(sec_id)
    first_detail = doc_manager.group_detail(sec_g_detail.get('group_id'))
    sec_g_list = doc_manager.doc_groups_sec_ids(sec_g_detail.get('group_id'))
    return render_template('content/list_detail.html', docs_list=docs_list, sec_g_detail=sec_g_detail,
                           first_detail=first_detail, sec_g_list=sec_g_list)


@source.route('/<item>', methods=['GET'])
def index_page(item):

    print '.......'

    # group = request.values.get('group')
    # r = NewsGroup.query_one(**{"name": item})
    # if r:
    #     r1 = News.query(**{"group": group,'category':r.ngid})
    #     # if r1:
    #
    # print '.....'
    # print r
    # print r.alias
    # NewsGroup.query(**{})
    # query(cls, limit=None, offset=None, desc=None, in_column=None, belong=None, **kwargs):
    return render_template("content/list_detail.html")