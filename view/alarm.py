#!/bin/env python
# encoding=utf-8

from flask import Blueprint, render_template
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

__author__ = 'xiangfeng'


alarm = Blueprint('alarm', __name__)


@alarm.route('', methods=['GET'])
def index_page():
    return render_template("alarm/index.html")
