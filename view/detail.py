#!/bin/env python
# encoding=utf-8

from flask import Blueprint, render_template
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

__author__ = 'xiangfeng'


detail = Blueprint('detail', __name__)


@detail.route('/', methods=['GET'])
def index_page():
    return render_template("detail/index.html")


@detail.route('/<item>', methods=['GET'])
def index_page(item):

    return render_template("detail/index.html")
