#!/bin/env python
# encoding=utf-8

from extensions import db
from flask import current_app
from models import cbt as model
from .bean import Bean
import copy
import sys
from flask import request
reload(sys)
sys.setdefaultencoding('utf-8')


class News(Bean):

    _tbl = model.News
    _id = 'nid'
    tid = 'nid'

    def __init__(self):
        super(News, self).__init__()
        self.tbl = model.News()


class NewsGroup(Bean):

    _tbl = model.NewsGroup
    _id = 'ngid'
    tid = 'ngid'

    def __init__(self):
        super(NewsGroup, self).__init__()
        self.tbl = model.NewsGroup()


