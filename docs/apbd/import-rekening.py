#!/usr/bin/python

import sys
from config import (db_url_dst)
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
    
def data_found(source):
    sql = text("""SELECT COUNT(*) C FROM eis.ar_payment_detail
                  WHERE tahun = :tahun AND kode = :kode AND ref_kode = :ref_kode""") 
    return eng_dst.execute(sql,kode    = source['kode'],
                        tahun          = source['tahun'],
                        ref_kode       = source['ref_kode'],).scalar()

filenm ='result.csv'

eng_dst = create_engine(db_url_dst)
#eng_dst.echo=True

DBSession = scoped_session(sessionmaker())
Base = declarative_base()

DBSession.configure(bind=eng_dst)
Base.metadata.bind = eng_dst

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
    def update(cls, data, **kwargs):
        return False
        
    @classmethod
    def tambah(cls, data, **kwargs):
        if kwargs:
            kode, nama = "", ""
            for name, value in kwargs.items():
                kode = name == 'kode' and value or kode or None
                nama = name == 'nama' and value or nama or None
                
            row = cls(data, kode=kode, nama=nama)
        else:
            row = cls(data)
        DBSession.add(row)
        DBSession.flush()
        DBSession.commit()
        return row.id
        
    @classmethod
    def get_id_by_kode(cls, kode):
          return DBSession.query(cls.id).filter(cls.kode==kode)
          
class Rekening(Base, base):
    __tablename__ ='rekenings'
    __table_args__ = {'extend_existing':True, 
           'schema' :'admin','autoload':True}         
    
with open(filenm, 'rb') as csvfile:
    reader = csv.DictReader(csvfile, delimiter='\t', quotechar='"')
    for row in reader:
        print row
        data = DBSession.query(Rekening).filter_by(kode=row['kode'],
                         tahun=2015).first()
        if not data:
            data=Rekening()
            data.kode = row['kode'].strip()
            data.created = datetime.now()
            data.create_uid = 1
            data.tahun = data.created.year 
            data.level_id = data.kode.count('.')+1
            data.parent_id = DBSession.query(Rekening.id).filter(Rekening.kode==data.kode[:data.kode.rfind('.')]).scalar()
            data.disabled = 0
            data.defsign = 1
        data.nama = row['nama'].strip()
        DBSession.add(data)
    
DBSession.flush()
DBSession.commit()
