#!/usr/bin/env python
#encoding=utf-8

__author__ = 'xiangfeng'

from datetime import datetime, date
from sqlalchemy import and_, func
from extensions import db
import collections
from flask import current_app
from models.docs import DocGroup, DocRelation, DocResponse, DocsInfo
from sqlalchemy import or_
import hashlib


class DocManage():
    def __init__(self):
        pass

    # @staticmethod  # 查询文档信息
    # def doc_info(offset_number, per_page, **kwargs):
    #     tmp_result = db.session.query(DocsInfo)
    #     for i in kwargs:
    #         if hasattr(DocsInfo(), i):
    #             tmp_result = tmp_result.filter(getattr(DocsInfo(), i) == kwargs[i])
    #     tmp_result = tmp_result.group_by(DocsInfo.title).order_by(DocsInfo.update_time.desc())
    #     total_number = tmp_result.count()
    #     result = tmp_result.offset(offset_number).limit(per_page).all()
    #     return total_number, result

    @staticmethod  # 分类查询文档信息
    def doc_info(offset_number, per_page, group, **kwargs):
        tmp_result = db.session.query(DocsInfo)
        if group:
            tmp_result = tmp_result.filter(DocsInfo.d_id.in_(group))
        for i in kwargs:
            if i == 'keys' and kwargs['keys']:
                tmp_result = tmp_result.filter(or_(getattr(DocsInfo, i).like('%' + kwargs[i] + '%'),
                                                   getattr(DocsInfo, 'details').contains(kwargs[i])))
            elif kwargs[i] and hasattr(DocsInfo(), i):
                tmp_result = tmp_result.filter(getattr(DocsInfo, i) == kwargs[i])
        # tmp_result = tmp_result.group_by(DocsInfo.title).order_by(DocsInfo.update_time.desc())
        tmp_result = tmp_result.order_by(DocsInfo.input_time.desc())
        total_number = tmp_result.count()
        if offset_number:
            tmp_result = tmp_result.offset(offset_number)
        if per_page:
            tmp_result = tmp_result.limit(per_page)
        result = tmp_result.all()
        return total_number, result

    @staticmethod
    def version_num(group_id, title):
        try:
            num = db.session.query(DocsInfo.d_id).filter(and_(DocsInfo.title == title,
                                                            DocsInfo.group_id == group_id)).count()
        except Exception as e:
            current_app.logger.error(str(e))
            num = 0
        return num

    @staticmethod
    def doc_groups_first():  # 查询一级分组
        r = db.session.query(DocGroup).all()
        return r

    @staticmethod
    def doc_groups_first_dict():  # 查询一级分组
        r = db.session.query(DocGroup).all()
        res = list()
        for i in r:
            res.append({'d_id': i.d_id,
                        'name': i.name})
        return res

    @staticmethod
    def first_group_id_from_sec(sec_id):
        r = db.session.query(DocRelation).filter(DocRelation.d_id == sec_id).first()
        return r.group_id

    @staticmethod
    def doc_groups_rels():  # 查询一二级分组关系
        r = db.session.query(DocRelation).all()
        res = dict()
        for i in r:
            if i.group_id not in res:
                res[i.group_id] = [{'d_id': i.d_id,
                                    'name': i.name}]
            else:
                res[i.group_id].append({'d_id': i.d_id,
                                        'name': i.name})
        return res

    @staticmethod
    def sec_group_rels():
        r = db.session.query(DocRelation).all()
        res = dict()
        for i in r:
            res[i.d_id] = i.name
        return res

    @staticmethod
    def doc_groups_sec_id(group_id):  # 根据id查询二级分组
        r = db.session.query(DocRelation).filter(DocRelation.group_id == int(group_id)).all()
        return r

    @staticmethod
    def doc_groups_sec_ids(group_id):  # 根据id查询二级分组
        r = db.session.query(DocRelation).filter(DocRelation.group_id == int(group_id)).all()
        res = list()
        for i in r:
            res.append({'id': i.d_id,
                        'name': i.name})
        return res

    @staticmethod
    def belong_first_group(sec_id):
        r = db.session.query(DocRelation).filter(DocRelation.d_id == sec_id).first()
        if r:
            return r.group_id
        else:
            return ''

    @staticmethod
    def exist_groups_sec(group_id, sec_name):
        r = db.session.query(DocRelation).filter(and_(DocRelation.group_id == int(group_id),
                                                      DocRelation.name == sec_name)).count()
        return r

    @staticmethod
    def fs_name(group_id):  # 根据sec_group id查询相应的名称以及一级分类
        tmp = db.session.query(DocRelation.name, DocRelation.group_id).filter(DocRelation.d_id == int(group_id)).first()
        first_name = u'其他'
        sec_name = u'其他'
        if tmp:
            sec_name = tmp[0]
            r = db.session.query(DocGroup.name).filter(DocGroup.d_id == tmp[1]).first()
            if r:
                first_name = r[0]
        return first_name, sec_name

    @staticmethod
    def group_detail(_id):  # 根据组id获取一级分组详情
        r = db.session.query(DocGroup).filter(DocGroup.d_id == _id).first()
        res = {}
        if r:
            res['d_id'] = r.d_id
            res['name'] = r.name
        return res

    @staticmethod
    def group_sec_detail(_id):  # 根据组id获取详情
        r = db.session.query(DocRelation).filter(DocRelation.d_id == _id).first()
        res = {}
        if r:
            res['d_id'] = r.d_id
            res['name'] = r.name
            res['group_id'] = r.group_id
        return res

    @staticmethod
    def docs_details(d_id):
        r = db.session.query(DocsInfo).filter(DocsInfo.d_id == d_id).first()
        return r

    @staticmethod
    def new_docs(**kwargs):  # 添加新文档信息
        docs_info = DocsInfo()
        docs_info.input_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        docs_info.update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for i in kwargs:
            if hasattr(docs_info, i):
                setattr(docs_info, i, kwargs[i])
        try:
            db.session.add(docs_info)
            db.session.commit()
            sta = True
        except Exception as e:
            current_app.logger.error(str(e))
            print str(e)
            db.session.rollback()
            sta = False
        return sta

    @staticmethod
    def update_docs(d_id, **kwargs):  # 添加新文档信息
        docs_info = dict()
        docs_info['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for i in kwargs:
            if hasattr(DocsInfo, i):
                docs_info[i] = kwargs[i]
        try:
            db.session.query(DocsInfo).filter(DocsInfo.d_id == d_id).update(docs_info)
            db.session.commit()
            sta = True
        except Exception as e:
            current_app.logger.error(str(e))
            db.session.rollback()
            sta = False
        return sta

    @staticmethod
    def doc_exist(sec_group, title):
        num = db.session.query(DocsInfo).filter(and_(DocsInfo.group_id == sec_group,
                                                     DocsInfo.title == title)).count()
        return num

    @staticmethod
    def new_docs_rel(**kwargs):  # 添加新文档分组关系
        doc_rel = DocRelation()
        for i in kwargs:
            if hasattr(doc_rel, i):
                setattr(doc_rel, i, kwargs[i])
        try:
            db.session.add(doc_rel)
            db.session.commit()
            d_id = doc_rel.d_id
            sta = True
        except Exception as e:
            current_app.logger.error(str(e))
            db.session.rollback()
            sta = False
            d_id = ''
        return sta, d_id

    @staticmethod
    def change_docs(d_id, **kwargs):  # 更新文档信息
        r = db.session.query(DocsInfo).filter(DocsInfo.d_id == d_id)
        update_info = dict()
        update_info['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for i in kwargs:
            if hasattr(DocsInfo(), i):
                update_info[i] = kwargs[i]
        try:
            r.update(update_info)
            db.session.commit()
            sta = 200
        except Exception as e:
            print str(e)
            current_app.logger.error(str(e))
            db.session.rollback()
            sta = 500
        return sta

    @staticmethod
    def change_docs_from_md5(md5, **kwargs):  # 更新文档信息
        update_info = dict()
        update_info['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for i in kwargs:
            if hasattr(DocsInfo(), i):
                update_info[i] = kwargs[i]
        r = db.session.query(DocsInfo).filter(DocsInfo.doc_md5 == md5)
        try:
            r.update(update_info)
            db.session.commit()
            sta = 200
        except Exception as e:
            print str(e)
            current_app.logger.error(str(e))
            db.session.rollback()
            sta = 500
        return sta

    @staticmethod  # 删除文档记录
    def delete_info(d_id):
        try:
            db.session.query(DocsInfo).filter(DocsInfo.d_id == d_id).delete()
            db.session.commit()
            sta = 200
        except Exception as e:
            current_app.logger.error(str(e))
            print str(e)
            db.session.rollback()
            sta = 500
        return sta

    @staticmethod
    def sec_group_id(first_id, name):
        r = db.session.query(DocRelation.d_id).filter(and_(DocRelation.group_id == first_id,
                                                           DocRelation.name == name)).first()
        return r[0]

    @staticmethod  # 记录用户点击数
    def doc_hit(d_id, url):
        try:
            r = db.session.query(DocsInfo)
            if d_id:
                r = r.filter(DocsInfo.d_id == d_id)
            if url:
                r = r.filter(DocsInfo.url == url)
            r.update({'hits': DocsInfo.hits + 1})
            db.session.commit()
        except Exception as e:
            print str(e)

    @staticmethod
    def doc_exist_id(d_id):
        num = db.session.query(DocsInfo).filter(DocsInfo.d_id == d_id).count()
        return num

    @staticmethod
    def exist_update(d_id, doc_md5):
        r = db.session.query(DocsInfo).filter(DocsInfo.d_id == d_id).first()
        if r:
            status = hashlib.md5(r.details.encode('utf-8')).hexdigest() != doc_md5
        else:
            status = False
        return status


