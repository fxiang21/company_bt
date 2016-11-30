# coding: utf-8
from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Index, Integer, SmallInteger, String, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class AlarmTpl(Base):
    __tablename__ = 'alarm_tpl'
    __table_args__ = (
        Index('idx_name_creator', 'name', 'creator', 'alarm_type', unique=True),
    )

    at_id = Column(Integer, primary_key=True)
    name = Column(String(64, u'utf8_unicode_ci'), nullable=False)
    min_sta_num = Column(SmallInteger, nullable=False, server_default=text("'1'"))
    min_continue_num = Column(SmallInteger, nullable=False, server_default=text("'1'"))
    strategy = Column(String(1024, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))
    max_alarm_num = Column(SmallInteger, nullable=False, server_default=text("'1'"))
    creator = Column(String(64, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))
    alarm_type = Column(String(8, u'utf8_unicode_ci'), nullable=False, server_default=text("'PING'"))
    note = Column(String(256, u'utf8_unicode_ci'))


class CollectHttpModel(Base):
    __tablename__ = 'collect_http_model'

    chm_id = Column(Integer, primary_key=True)
    name = Column(String(32, u'utf8_unicode_ci'), nullable=False, unique=True, server_default=text("''"))
    interval = Column(SmallInteger, nullable=False, server_default=text("'60'"))
    method = Column(String(8, u'utf8_unicode_ci'), nullable=False, server_default=text("'GET'"))
    response = Column(String(collation=u'utf8_unicode_ci'))
    postcontent = Column(String(collation=u'utf8_unicode_ci'))
    cookie = Column(Text(collation=u'utf8_unicode_ci'))
    match = Column(Enum(u'true', u'false', u'ignore'))
    creator = Column(String(64, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))


class CollectPingModel(Base):
    __tablename__ = 'collect_ping_model'

    cpm_id = Column(Integer, primary_key=True)
    name = Column(String(32, u'utf8_unicode_ci'), nullable=False, unique=True, server_default=text("''"))
    interval = Column(SmallInteger, nullable=False, server_default=text("'60'"))
    creator = Column(String(64, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))


class Log(Base):
    __tablename__ = 'log'

    l_id = Column(Integer, primary_key=True)
    monitor_name = Column(String(32, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))
    target = Column(String(512, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))
    action = Column(String(8, u'utf8_unicode_ci'), nullable=False, server_default=text("'NEW'"))
    user = Column(String(64, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))
    created = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class MonitorAuthUser(Base):
    __tablename__ = 'monitor_auth_user'

    mau_id = Column(Integer, primary_key=True)
    monitor_name = Column(String(32, u'utf8_unicode_ci'), nullable=False, unique=True, server_default=text("''"))
    views_users = Column(String(4096, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))
    other_views_users = Column(String(512, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))
    creator = Column(String(64, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))


class MonitorTarget(Base):
    __tablename__ = 'monitor_target'

    mt_id = Column(Integer, primary_key=True)
    cm_id = Column(Integer, nullable=False)
    at_id = Column(ForeignKey(u'alarm_tpl.at_id'), nullable=False, index=True)
    name = Column(String(32, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))
    target = Column(String(512, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))
    stations = Column(String(1024, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))
    monitor_type = Column(String(8, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))
    request_method = Column(String(8, u'utf8_unicode_ci'))
    note_group = Column(String(512, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))
    run_begin = Column(String(16, u'utf8_unicode_ci'), nullable=False, server_default=text("'00:00:00'"))
    run_end = Column(String(16, u'utf8_unicode_ci'), nullable=False, server_default=text("'24:00:00'"))
    notify_method = Column(Integer, nullable=False, server_default=text("'0'"))
    creator = Column(String(64, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    enabled = Column(Integer, server_default=text("'1'"))

    at = relationship(u'AlarmTpl')


class RelStaTarget(Base):
    __tablename__ = 'rel_sta_target'
    __table_args__ = (
        Index('idx_s_mt_id', 's_id', 'mt_id', unique=True),
    )

    rst_id = Column(Integer, primary_key=True)
    s_id = Column(ForeignKey(u'stations.s_id', ondelete=u'CASCADE'), nullable=False)
    mt_id = Column(ForeignKey(u'monitor_target.mt_id', ondelete=u'CASCADE'), nullable=False, index=True)
    response = Column(Float)

    mt = relationship(u'MonitorTarget')
    s = relationship(u'Station')


class RelTeamUser(Base):
    __tablename__ = 'rel_team_user'

    rid = Column(Integer, primary_key=True)
    tid = Column(ForeignKey(u'team.tid'), nullable=False, index=True)
    uid = Column(ForeignKey(u'user.uid'), nullable=False, index=True)

    team = relationship(u'Team')
    user = relationship(u'User')


class Station(Base):
    __tablename__ = 'stations'

    s_id = Column(Integer, primary_key=True)
    name = Column(String(8, u'utf8_unicode_ci'), unique=True)
    alias = Column(String(64, u'utf8_unicode_ci'))


class Team(Base):
    __tablename__ = 'team'
    __table_args__ = (
        Index('idx_team_name_creator', 'name', 'creator', unique=True),
    )

    tid = Column(Integer, primary_key=True)
    name = Column(String(64, u'utf8_unicode_ci'), nullable=False)
    creator = Column(String(64, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))
    created = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class User(Base):
    __tablename__ = 'user'
    __table_args__ = (
        Index('idx_user_name_creator', 'name', 'creator', unique=True),
    )

    uid = Column(Integer, primary_key=True)
    name = Column(String(64, u'utf8_unicode_ci'), nullable=False)
    passwd = Column(String(64, u'utf8_unicode_ci'), nullable=False, server_default=text("'13572468'"))
    nickname = Column(String(128, u'utf8_unicode_ci'), server_default=text("''"))
    email = Column(String(255, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))
    phone = Column(String(16, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))
    qq = Column(String(16, u'utf8_unicode_ci'), server_default=text("''"))
    role = Column(Integer, nullable=False, server_default=text("'0'"))
    creator = Column(String(64, u'utf8_unicode_ci'), nullable=False, server_default=text("''"))
    created = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
