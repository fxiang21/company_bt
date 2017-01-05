# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class News(Base):
    __tablename__ = 'News'

    nid = Column(Integer, primary_key=True)
    group = Column(Integer, nullable=False)
    title = Column(String(256), nullable=False, server_default=text("''"))
    created = Column(DateTime)
    author = Column(String(45))
    content = Column(String)
    url = Column(String(256))
    tpl = Column(String(256))
    img = Column(String(256))


class NewsGroup(Base):
    __tablename__ = 'News_Group'

    ngid = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False, server_default=text("''"))
    alias = Column(String(128), nullable=False, server_default=text("''"))