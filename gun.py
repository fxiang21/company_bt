import os
import multiprocessing
import gevent.monkey
gevent.monkey.patch_all()

debug = True
loglevel = 'debug'
bind = '0.0.0.0:5000'
pidfile = 'logs/gunicorn.pid'
logfile = 'logs/gunicorn.log'

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'

x_forwarded_for_header = 'X-FORWARDED-FOR'