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

filenm ='import-eis'
pid_file ='/var/run/%s.pid' % filenm
pid = demon.make_pid(pid_file)
log = demon.Log('/var/log/%s.log' % filenm)

arg = sys.argv[0]
c = len(sys.argv) 
  
"/home/aagusti/env/zosipkd-data/kab-tgr/anggaran"
path = "%s/%s" % (os.path.dirname(os.path.abspath(__file__)),'anggaran')

if c>1:
    path = sys.argv[1]

eng_dst = create_engine(db_url_dst)
#eng_dst.echo=True

DBSession = scoped_session(sessionmaker())
Base = declarative_base()

DBSession.configure(bind=eng_dst)
Base.metadata.bind = eng_dst

class base(object):
    #created = Column(DateTime,  nullable=False, default=datetime.now)
    #updated = Column(DateTime,  nullable=False, default=datetime.now)
    #update_uid = Column(Integer)
    #create_uid = Column(Integer)
    #disabled = Column(SmallInteger) 
    #def __init__(self, data, **kwargs):
    #      self.created = datetime.now()
    #      self.updated = datetime.now()
    #      self.create_uid = 1
          #self.disabled = 0
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
          
class Eis(Base, base):
    __tablename__ ='wells'
    __table_args__ = {'extend_existing':True, 
           'schema' :'eis','autoload':True}         
class AR(Base, base):
    __tablename__ ='ar_payment_detail'
    __table_args__ = {'extend_existing':True, 
           'schema' :'eis','autoload':True}         
class Chart(Base, base):
    __tablename__ ='charts'
    __table_args__ = {'extend_existing':True, 
           'schema' :'eis','autoload':True} 
           
class ChartItem(Base, base):
    __tablename__ ='chart_items'
    __table_args__ = {'extend_existing':True, 
           'schema' :'eis','autoload':True}         
    chart = relationship("Chart")
    
################################################################################     
     
eis_date  = datetime.now()
eis_year  = eis_date.year
eis_month = eis_date.month
eis_day   = eis_date.day
tahun     = eis_year
eis_date  = date(eis_year,eis_month,eis_day) 
eis_week   = eis_date.isocalendar()[1]

#UPDATE DATA wells
#rows = Eis(None)

rows = DBSession.query(Eis).filter(Eis.tahun==tahun).all()
for row in rows:
    row_data = DBSession.query(func.sum(AR.amount).label('s')).\
                  filter(AR.tahun==tahun, AR.bulan < eis_month,
                         AR.kode.ilike("%s%%" % row.kode)).scalar()
    if not row_data:
        row_data = 0
    row.amt_tahun = row_data

    row_data = DBSession.query(func.sum(AR.amount).label('s')).\
                  filter(AR.tahun==tahun, AR.bulan == eis_month,
                         AR.hari < eis_day,
                         AR.kode.ilike("%s%%" % row.kode)).scalar()
    if not row_data:
        row_data = 0
        
    row.amt_bulan = row_data

    row_data = DBSession.query(func.sum(AR.amount).label('s')).\
                  filter(AR.tahun==tahun, AR.bulan == eis_month,
                         AR.hari == eis_day,
                         AR.kode.ilike("%s%%" % row.kode)).scalar()
    if not row_data:
        row_data = 0
    row.amt_hari = row_data
    #update mingguan
    row_data = DBSession.query(func.sum(AR.amount).label('s')).\
                  filter(AR.tahun==tahun, AR.bulan == eis_month,
                         AR.minggu == eis_week,
                         AR.kode.ilike("%s%%" % row.kode)).scalar()
    if not row_data:
        row_data = 0
    row.amt_minggu = row_data - row.amt_hari
    DBSession.add(row)
        
DBSession.flush()

#UPDATE DATA Chart Item Untuk Realisasi
rows = DBSession.query(ChartItem).filter(ChartItem.source_type=='realisasi').all()
for row in rows:
    #JIKA PIE hanya 1 kolom yang di update
    row_dict = row2dict(row)
    tupKode = row.rekening_kd.split(',') # split dulu kode rekening yang digunakan
    if row.chart.chart_type=='pie': 
        row_sum = 0
        for tup in tupKode:
            row_data = DBSession.query(func.sum(AR.amount).label('s')).\
                  filter(AR.tahun==tahun,
                         AR.kode.ilike("%s%%" % tup.strip())).scalar()
            if row_data:
                row_sum += row_data
        row.value_1 = row_sum
        
    elif row.is_sum:
        if row.chart.label[:3]=='JAN':
            row_sum = 0
            for i in range(1,13):
                tupKode = row.rekening_kd.split(',')
                for tup in tupKode:
                    row_data = DBSession.query(func.sum(AR.amount).label('s')).\
                          filter(AR.tahun==tahun,
                                 AR.bulan == i,
                                 AR.kode.ilike("%s%%" % tup.strip())).scalar()
                    if row_data:
                        row_sum = row_sum+row_data
                if i<10:
                    row_dict['value_%s' %i] = row_sum
                else:
                    row_dict['value%s' %i] = row_sum
            row.from_dict(row_dict)
            
        elif row.chart.label[:3]=='JUL':
            row_sum = 0
            for i in range(7,13):
                tupKode = row.rekening_kd.split(',')
                for tup in tupKode:
                    row_data = DBSession.query(func.sum(AR.amount).label('s')).\
                          filter(AR.tahun==tahun,
                                 AR.bulan == i,
                                 AR.kode.ilike("%s%%" % tup.strip())).scalar()
                    if row_data:
                        row_sum += row_data
                row_dict['value_%s' %str(i-6)] = row_sum
            row.from_dict(row_dict)


    else:
        if row.chart.label[:3]=='JAN':
            for i in range(1,13):
                tupKode = row.rekening_kd.split(',')
                row_sum = 0
                for tup in tupKode:
                    row_data = DBSession.query(func.sum(AR.amount).label('s')).\
                          filter(AR.tahun==tahun,
                                 AR.bulan == i,
                                 AR.kode.ilike("%s%%" % tup.strip())).scalar()
                    if row_data:
                        row_sum += row_data
                if i<10:
                    row_dict['value_%s' %i] = row_sum
                else:
                    row_dict['value%s' %i] = row_sum
            row.from_dict(row_dict)
            
        elif row.chart.label[:3]=='JUL':
            for i in range(7,13):
                tupKode = row.rekening_kd.split(',')
                row_sum = 0
                for tup in tupKode:
                    row_data = DBSession.query(func.sum(AR.amount).label('s')).\
                          filter(AR.tahun==tahun,
                                 AR.bulan == i,
                                 AR.kode.ilike("%s%%" % tup.strip())).scalar()
                    if row_data:
                        row_sum += row_data
                row_dict['value_%s' %str(i-6)] = row_sum
                
            row.from_dict(row_dict)
    DBSession.add(row)
    
DBSession.flush()
DBSession.commit()
info('Selesai')          
os.remove(pid_file)