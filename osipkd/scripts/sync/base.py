#!/usr/bin/python
import sys
#from config import (db_url_dst)
from tools import humanize_time, print_log, eng_profile, stop_daemon
import os
import demon
import signal
import csv
import os
import io
from time import time
from sqlalchemy import create_engine, func
from sqlalchemy.sql.expression import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import DatabaseError
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Sequence, SmallInteger, BigInteger
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship
    )
    
from datetime import datetime
from urllib import unquote_plus
from urlparse import urlparse
from optparse import OptionParser
from datetime import date
sys.path.insert(0,'/etc/opensipkd')
from zosipkd import bphtb, pbb, padl, osipkd

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d        
    
def info(s):
    print_log(s)
    log.info(s)
    
def error(s):
    print_log(s,'ERROR')
    log.error(s)    

if bphtb['db_url']:
    bphtb_Base = declarative_base()
    bphtb_eng  = create_engine(bphtb['db_url'])
    bphtb_Session = scoped_session(sessionmaker())
    bphtb_Session.configure(bind=bphtb_eng)
    bphtb_Base.metadata.bind = bphtb_eng


if osipkd['db_url']:
    osipkd_Base = declarative_base()
    osipkd_eng  = create_engine(osipkd['db_url'])
    osipkd_Session = scoped_session(sessionmaker())
    osipkd_Session.configure(bind=osipkd_eng)
    osipkd_Base.metadata.bind = osipkd_eng
    #osipkd_eng.echo = True
    
class base(object):
    def to_dict(self): # Elixir like
        values = {}
        for column in self.__table__.columns:
            values[column.name] = getattr(self, column.name)
        return values
        
    def from_dict(self, values):
        for column in self.__table__.columns:
            if column.name in values:
                setattr(self, column.name, values[column.name])

    def as_timezone(self, fieldname):
        date_ = getattr(self, fieldname)
        return date_ and as_timezone(date_) or None
        
    @classmethod
    def get_id_by_kode(cls, kode):
          return DBSession.query(cls.id).filter(cls.kode==kode)
          
