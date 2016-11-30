#!/bin/env python
# encoding=utf-8

from flask import Blueprint, render_template
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

__author__ = 'xiangfeng'


history = Blueprint('history', __name__)


@history.route('', methods=['GET'])
def h_index():
    return render_template("history/index.html")