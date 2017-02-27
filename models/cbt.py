# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String, text,Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import LONGTEXT

Base = declarative_base()
metadata = Base.metadata


class News(Base):
    __tablename__ = 'News'

    nid = Column(Integer, primary_key=True)
    group = Column(Integer, nullable=False)
    title = Column(String(256), nullable=False, server_default=text("''"))
    created = Column(DateTime)
    author = Column(String(45))
    url = Column(String(256))
    content = Column(LONGTEXT)


class NewsGroup(Base):
    __tablename__ = 'News_Group'

    ngid = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False, server_default=text("''"))
    alias = Column(String(128), nullable=False, server_default=text("''"))


class DefaultInfo(Base):
    __tablename__ = u'default_info'

    did = Column(Integer, primary_key=True)
    category = Column(String(128), nullable=False, server_default=text("''"))
    content = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)
    status = Column(String(64))
