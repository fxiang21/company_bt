#!/bin/env python
# encoding=utf-8

from flask import Blueprint, render_template, request, jsonify
from lib import db
from lib.common import SqlResultConvert
import json
import os
import re
from werkzeug import secure_filename

from flask import Blueprint, redirect, render_template,request,jsonify,session, send_from_directory, current_app
import json,hashlib
from datetime import datetime
from lib.util import PrpCrypt
from sendmail import SendHtmlEmail
from lib.docs import DocManage
import math
from lib.util import get_show_pages
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


__author__ = 'xiangfeng'

docs = Blueprint('docs', __name__)

prp_crypt = PrpCrypt('!@#$%^&*12qwaszx')
doc_manager = DocManage()


# @docs.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])
# def index_page():
#     if request.method == "GET":
#         try:
#             groups_db = db.NewsGroup.query()
#             groups = SqlResultConvert.to_list(groups_db)
#             news = dict()
#             for group in groups:
#                 r, num = db.News.query_num(limit=5, desc="created", **{"group": group.get("ngid")})
#                 news[group.get("ngid")] = SqlResultConvert.to_list(r)
#             print groups
#             print news
#             return render_template("docs/docs.html")
#         except Exception as e:
#             return json.dumps({"message": str(e)})
#     elif request.method == "POST":
#         pass
#     elif request.method == "PUT":
#         pass
#     elif request.method == "DELETE":
#         pass
#     else:
#         return json.dumps({"message": u"不支持的方法"})


@docs.route('/', methods=['GET'])
def doc_index():
    sec_groups = list()
    query_dict = dict()
    query_dict['group_id'] = request.values.get('sec_group', '').strip()
    if not query_dict['group_id']:
        first_group = request.values.get('first_group')
        if first_group:
            d_id = first_group.rsplit('_', 1)[0]
            r = doc_manager.doc_groups_sec_id(d_id)
            for i in r:
                sec_groups.append(i.d_id)
    query_dict['title'] = request.values.get('doc_title', '').strip()
    query_dict['keys'] = request.values.get('doc_keys', '').strip()
    if request.values.get('perpage', '').isdigit():
        per_page = int(request.values.get('perpage', ''))
        if per_page and per_page not in [10, 25, 50, 100]:
            per_page = current_app.config['PER_PAGE']
    else:
        per_page = current_app.config['PER_PAGE']
    page = request.values.get('page', '1')
    if page.isdigit():
        page = int(page)
    else:
        page = 1
    if isinstance(page, int) and page > 1:
        offset_number = (page - 1) * per_page
    else:
        offset_number = 0
    try:
        (total_number, result) = doc_manager.doc_info(offset_number, per_page, sec_groups, **query_dict)
        pages = int(math.ceil(float(total_number)/per_page))
        page_shows = get_show_pages(page, pages)
    except Exception as e:
        print str(e)
    groups = doc_manager.doc_groups_first()
    sec_group_rels = doc_manager.sec_group_rels()
    try:
        return render_template('docs/index.html',
                               result=result,
                               offset_number=offset_number,
                               per_page=int(per_page),
                               total_number=int(total_number),
                               current_page=int(page),
                               pages=pages,
                               page_shows=page_shows,
                               doc_groups=groups,
                               author=session.get('CAS_USERNAME', ''),
                               sec_group_rels=sec_group_rels,
                               active_item='docs')
    except Exception as e:
        print str(e)
    return 'error: ', str(e)


@docs.route('/trees', methods=['POST'])
def doc_trees():
    groups = doc_manager.doc_groups_first_dict()
    group_rels = doc_manager.doc_groups_rels()
    return jsonify(doc_groups=groups, group_rels=group_rels)


@docs.route('/input', methods=['GET', 'POST'])
def docs_input():
    load_file(request.files.getlist("file[]"))


@docs.route('/delete', methods=['GET', 'POST'])
def docs_delete():
    d_id = request.values.get('d_id')
    sta = doc_manager.delete_info(d_id)
    return jsonify(code=sta)


@docs.route('/view/<item>')
def doc_view(item):
    if item.isdigit():
        query_dict = {'d_id': int(item)}
    else:
        query_dict = {}
    doc_manager.doc_hit(item, '')
    (total_number, result) = doc_manager.doc_info(0, 1, '', **query_dict)
    if total_number:
        try:
            return render_template('docs/docs.html', result=result)
        except Exception as e:
            return jsonify(error=str(e))
    else:
        return redirect('/docs/')


@docs.route('/groups', methods=['POST', 'GET'])
def doc_groups():
    first_group = request.values.get('first_group')
    d_id = first_group.rsplit('_', 1)[0]
    if d_id:
        groups = doc_manager.doc_groups_sec_id(d_id)
    else:
        groups = doc_manager.doc_groups_first()
    result = list()
    for i in groups:
        result.append({'d_id': i.d_id, 'name': i.name})
    return jsonify(result=result)


@docs.route('/sec_groups', methods=['POST'])
def doc_sec_groups():
    sec_groups = doc_manager.doc_groups_sec_ids(request.values.get('id'))
    return jsonify(res=sec_groups)


@docs.route('/sec_groups/add', methods=['POST'])
def doc_sec_groups_add():
    rels = dict()
    rels['group_id'] = request.values.get('first_group')
    rels['name'] = request.values.get('sec_group')
    rels['description'] = request.values.get('group_desc','')
    sta, sec_id = doc_manager.new_docs_rel(**rels)
    return jsonify(status=sta)


@docs.route('/upload', methods=['POST'])  # 上传文件
def upload_file():
    action = request.values.get('action')
    try:
        docs_info = dict()
        docs_info['title'] = request.values.get('doc_title', '')
        if action == 'create':
            version = '1.0'
            first_group = request.values.get('first_group')
            first_groups = first_group.rsplit('_', 1)
            first_g_id = first_groups[0]
            first_group_name = first_groups[1]
            sec_group = request.values.get('sec_group')
            #----------分组不存在则添加新分组--------#
            if not doc_manager.exist_groups_sec(first_g_id, sec_group):
                new_rel = dict()
                new_rel['group_id'] = first_g_id
                new_rel['name'] = sec_group
                sta, d_id = doc_manager.new_docs_rel(**new_rel)
            else:
                d_id = doc_manager.sec_group_id(first_g_id, sec_group)
        elif action == 'upgrade':
            d_id = request.values.get('group_id')
            #-------------建立版本---------------#
            kwargs = dict()
            kwargs['title'] = docs_info['title']
            num = doc_manager.version_num(d_id, docs_info['title'])
            version = '.'.join([str(num + 1), '0'])
            first_group_name, sec_group = doc_manager.fs_name(d_id)
        else:
            return jsonify(message=u'失败:不支持的方法')
        docs_info['version'] = version
        docs_info['group_id'] = d_id
        docs_info['docs_type'] = request.values.get('doc_type')
        if docs_info['docs_type'] == 'pdf':
            uploaded_files = request.files.getlist("file[]")
            directory = os.path.join(current_app.config['DOCS_DIR'], first_group_name, sec_group)
            #-----------存储文件------------------#
            try:
                for file in uploaded_files:
                    if file and allowed_file(file.filename):
                        directory_outer = os.path.join(current_app.config['DOCS_DIR'], first_group_name)
                        if not os.path.exists(directory_outer):
                            os.mkdir(directory_outer)
                        if not os.path.exists(directory):
                            os.mkdir(directory)
                        tmp = file.filename.rsplit('.', 1)
                        files = [tmp[0], version, tmp[1]]
                        filename = '.'.join(files)
                        try:
                            file.save(os.path.join(directory, filename))
                            docs_info['url'] = os.path.join(directory[1:], filename)
                        except Exception as e:
                            print str(e)
            except Exception as e:
                print str(e)
        else:
            docs_info['url'] = request.values.get('doc_url')
        docs_info['keys'] = request.values.get('doc_keys', '')
        docs_info['comment'] = request.values.get('doc_comment')
        docs_info['author'] = session.get('CAS_USERNAME', '')
        content = ';'.join([str(docs_info['group_id']), docs_info['title']])
        docs_info['doc_md5'] = hashlib.md5(content.encode("utf8")).hexdigest()
        docs_info['hits'] = 0
        sta = doc_manager.new_docs(**docs_info)
    except Exception as e:
        print str(e)
    return redirect('/docs')


@docs.route('/equip/uploads/<filename>')  # 下载文件
def uploaded_file(filename):
    return send_from_directory(current_app.config['CONF_DIR'], filename)


@docs.route('/info', methods=['POST'])
def docs_infos():
    query_dict = dict()
    query_dict['d_id'] = request.values.get('d_id')
    (total_number, r) = doc_manager.doc_info(0, 1, '', **query_dict)
    result = dict()
    for i in r:
        result['comment'] = i.comment
        result['keys'] = i.keys
        result['title'] = i.title
        result['d_id'] = i.d_id
        result['group_id'] = i.group_id
        result['doc_md5'] = i.doc_md5
    first_group = doc_manager.first_group_id_from_sec(result['group_id'])
    sec_groups = doc_manager.doc_groups_sec_ids(first_group)
    return jsonify(result=result, sec_groups=sec_groups, first_group=first_group)


@docs.route('/update', methods=['POST'])
def docs_update():
    sec_group = request.values.get('update_sec_group', '')
    title = request.values.get('doc_title_update', '')
    if doc_manager.doc_exist(sec_group, title):
        return jsonify(code=202)
    else:
        doc_md5 = request.values.get('update_doc_md5')
        update_info = dict()
        update_info['keys'] = request.values.get('keys')
        update_info['comment'] = request.values.get('comment')
        update_info['group_id'] = request.values.get('update_sec_group')
        update_info['title'] = request.values.get('doc_title_update')
        content = ';'.join([str(sec_group), title])
        update_info['doc_md5'] = hashlib.md5(content.encode("utf8")).hexdigest()
        try:
            sta = doc_manager.change_docs_from_md5(doc_md5, **update_info)
        except Exception as e:
            print str(e)
            sta = 202
        return jsonify(code=sta)


@docs.route('/download')  # 下载文件
def download_file():
    filename = request.values.get('filename')
    doc_manager.doc_hit('', filename)
    total_paths = filename.split('/', 5)
    directory = '.' + '/'.join(total_paths[:5])
    name = total_paths[5]
    return send_from_directory(directory, name)


@docs.route('/edit', methods=['GET', 'POST'])
def docs_edit():
    if request.method == 'POST':
        res = request.values
        doc_details = dict()
        doc_details['details'] = res.get('details', '')
        doc_details['group_id'] = res.get('sec_group', '')
        doc_details['title'] = res.get('title', '')
        doc_details['comment'] = res.get('comment', '')
        doc_details['author'] = session.get('CAS_USERNAME', '')
        doc_details['docs_type'] = 'DOC'
        doc_details['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        doc_md5 = res.get('doc_md5', '')
        d_id = res.get('d_id', '')
        if doc_manager.doc_exist_id(d_id):
            # 首先需要判断文档是否存在更新
            if not doc_manager.exist_update(d_id, doc_md5):
                finished = doc_manager.update_docs(d_id, **doc_details)
                if finished:
                    edit_info = dict()
                    edit_info['d_id'] = d_id
                    edit_info['user'] = session.get('CAS_USERNAME')
                    edit_info['content'] = doc_details['details']
                    edit_info['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    sta = doc_manager.add_doc_edit_status(**edit_info)
                    return_code = 200
                else:
                    finished = True
                    return_code = 500
            else:
                finished = True
                return_code = 409
        else:
            doc_details['hits'] = 0
            doc_details['version'] = '1.0'
            finished = doc_manager.new_docs(**doc_details)
            return_code = 200
        return render_template('docs/edit.html', finished=finished, return_code=return_code)
    else:
        groups = doc_manager.doc_groups_first_dict()
        d_id = request.values.get('id')
        if d_id:
            doc_details = doc_manager.docs_details(d_id)
            first_group_id = doc_manager.belong_first_group(doc_details.group_id)
            sec_groups = doc_manager.doc_groups_sec_ids(first_group_id)
        else:
            doc_details = {}
            first_group_id = groups[0].get('d_id') if groups else 0
            sec_groups = doc_manager.doc_groups_sec_ids(first_group_id)

        if doc_details:
            content = doc_details.details
            allowed_edit = session.get('CAS_USERNAME') == doc_details.author
        else:
            content = ''
            allowed_edit = True
        return render_template('docs/edit.html',
                               doc_details=doc_details,
                               groups=groups,
                               sec_groups=sec_groups,
                               first_group_id=first_group_id,
                               doc_md5=hashlib.md5(content.encode("utf8")).hexdigest(),
                               allowed_edit=allowed_edit,
                               finished=False)


@docs.route('/upload/file/<item>', methods=['POST'])
def upload_files(item):
    try:
        uploaded_file = request.files.get('file')
        if uploaded_file and allowed_file(uploaded_file.filename):
            files_parts = os.path.splitext(uploaded_file.filename)
            if len(files_parts) == 2:
                f_suffix = files_parts[1]
            else:
                f_suffix = ''
            if item == 'app_user':
                dir_name = datetime.now().strftime('%Y-%m')
                directory_middle = ''
                dir_path = os.path.join('./static', directory_middle, dir_name)
            elif item == 'img':
                dir_name = datetime.now().strftime('%Y-%m')
                directory_middle = 'resource/docs/images'
                dir_path = os.path.join('./static', directory_middle, dir_name)
            elif item == 'sendmail':
                dir_name = datetime.now().strftime('%Y-%m')
                directory_middle = 'resource/mails/send'
                dir_path = os.path.join('./static', directory_middle, dir_name)
            else:
                directory_middle = 'resource/app/file'
                dir_path = os.path.join('./static', directory_middle)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)
            file_name = ''.join([create_unique_string(session.get('CAS_USERNAME', '')), f_suffix])
            try:
                uploaded_file.save(os.path.join(dir_path, file_name))
            except Exception, e:
                current_app.logger.error(str(e))
                print str(e)
                return jsonify(link='')
            return jsonify(link=os.path.join(dir_path, file_name)[1:])
            # return jsonify(link=os.path.join('/static', directory_middle, file_name))
        else:
            return jsonify(link='')
    except Exception as e:
        print str(e)
        return jsonify(link='')


@docs.route('/render', methods=['GET'])
def rend():
    encrypt_id = request.values.get('id')
    d_id = prp_crypt.decrypt(encrypt_id)
    doc_details = doc_manager.docs_details(d_id)
    try:
        return render_template('docs/doc_content.html',
                               doc_details=doc_details)
    except Exception as e:
        return jsonify(error=str(e))


@docs.route('/is_new', methods=['POST'])
def doc_is_new():
    d_id = request.values.get('d_id', '')
    if d_id:
        exist_update = doc_manager.exist_update(d_id, request.values.get('doc_md5'))
    else:
        exist_update = False
    return jsonify(exist_update=exist_update)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']


def load_file(uploaded_files):
    filenames = list()
    try:
        uploaded_files = request.files.getlist("file[]")
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                directory = os.path.join(current_app.config['CONF_DIR'], 'docs')
                if not os.path.exists(directory):
                    os.mkdir(directory)
                filename = secure_filename(file.filename)
                file.save(os.path.join(directory, filename))
                filenames.append(filename)
    except Exception as e:
        print str(e)


def create_unique_string(str1):
    rand_str = ''.join(map(lambda xx:(hex(ord(xx))[2:]), os.urandom(16)))
    time_now = datetime.now().strftime('%y%m%d%H%M%S%f')
    unique_str = ''.join([rand_str, time_now, str1])
    return hashlib.md5(unique_str.encode("utf8")).hexdigest()