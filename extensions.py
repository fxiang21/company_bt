# encoding=utf-8


from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache


__all__ = ['mail', 'db', 'cache', 'celery']


mail = Mail()
db = SQLAlchemy()
cache = Cache()
