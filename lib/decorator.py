#!/usr/bin/env python
#encoding=utf-8

__author__ = 'lucky'


from flask import current_app, session, redirect


def islogin():
    cas_username_session_key = current_app.config['CAS_USERNAME_SESSION_KEY']
    return cas_username_session_key in session


def login():
    return redirect('/login')


def need_admin(fn):
    def wrapper(*args, **kwargs):
        if islogin():
            pass
        else:
            return login()
        return fn(*args, **kwargs)
    return wrapper


def need_op(fn):
    def wrapper(*args, **kwargs):
        if islogin():
            pass
        else:
            return login()
        return fn(*args, **kwargs)
    return wrapper


def need_monitor(fn):
    def wrapper(*args, **kwargs):
        if islogin():
            pass
        else:
            return login()
        return fn(*args, **kwargs)
    return wrapper


def need_dev(fn):
    def wrapper(*args, **kwargs):
        if islogin():
            pass
        else:
            return login()
        return fn(*args, **kwargs)
    return wrapper
