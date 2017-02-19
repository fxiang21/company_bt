#!/usr/bin/env python
#encoding=utf-8

__author__ = 'xiangfeng'

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from extensions import db
from sqlalchemy.dialects.mysql import LONGTEXT

class DocsInfo(db.Model):
    __tablename__ = "docs_info"

    d_id = db.Column(db.SmallInteger, primary_key=True, nullable=False, autoincrement=True)
    group_id = db.Column(db.SmallInteger, db.ForeignKey("doc_relation.d_id"), primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    keys = db.Column(db.String(256))
    url = db.Column(db.Text(), nullable=True)
    docs_type = db.Column(db.Enum('PDF', 'URL', 'HTML', 'DOC'))
    version = db.Column(db.String(6), nullable=False)
    author = db.Column(db.String(32), nullable=False)
    input_time = db.Column(db.DateTime(), nullable=False)
    update_time = db.Column(db.DateTime(), nullable=False)
    comment = db.Column(db.Text())
    hits = db.Column(db.Integer())
    details = db.Column(LONGTEXT)
    doc_md5 = db.Column(db.String(32))


class DocGroup(db.Model):
    __tablename__ = "doc_group"

    d_id = db.Column(db.SmallInteger, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)

    __table_args__ = (db.UniqueConstraint("name"), )


class DocRelation(db.Model):
    __tablename__ = 'doc_relation'

    d_id = db.Column(db.SmallInteger, primary_key=True, nullable=False, autoincrement=True)

    group_id = db.Column(db.SmallInteger, db.ForeignKey("doc_group.d_id"), primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    __table_args__ = (db.UniqueConstraint("group_id", "name", name="group_id_name"), )


class DocResponse(db.Model):
    __tablename__ = 'doc_response'

    d_id = db.Column(db.SmallInteger, primary_key=True, nullable=False, autoincrement=True)

    user = db.Column(db.String(32), nullable=False)
    time = db.Column(db.DateTime(), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    resp_doc_id = db.Column(db.SmallInteger, db.ForeignKey("docs_info.d_id"), primary_key=True)

    rep_id = db.Column(db.Integer())  # 如果是针对某一条子记录的回复，则不为空


class DocEditStatus(db.Model):
    __tablename__ = 'doc_edit_status'

    es_id = db.Column(db.SmallInteger, primary_key=True, nullable=False, autoincrement=True)

    d_id = db.Column(db.SmallInteger, db.ForeignKey("docs_info.d_id"), primary_key=True)
    user = db.Column(db.String(64), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)
    content = db.Column(LONGTEXT)
