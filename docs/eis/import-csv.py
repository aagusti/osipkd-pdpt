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
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import DatabaseError
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Sequence
from datetime import datetime
from urllib import unquote_plus
from urlparse import urlparse
from optparse import OptionParser

def info(s):
    print_log(s)
    log.info(s)
    
def error(s):
    print_log(s, 'ERROR')
    log.error(s)    
    
def data_found(source):
    sql = text("""SELECT COUNT(*) C FROM eis.ar_payment_detail
                  WHERE tahun = :tahun AND kode = :kode AND ref_kode = :ref_kode""") 
    return eng_dst.execute(sql,kode    = source['kode'],
                        tahun          = source['tahun'],
                        ref_kode       = source['ref_kode'],).scalar()

def insert(source):
    sql = text("""INSERT INTO eis.ar_payment_detail(kode, disabled, created, 
                    updated, create_uid, nama, tahun, amount, ref_kode, 
                    ref_nama, tanggal, kecamatan_kd, kecamatan_nm, kelurahan_kd, 
                    kelurahan_nm, is_kota, sumber_data, sumber_id) 
                  VALUES(:kode, :disabled, :created, :updated, :create_uid, 
                         :nama, :tahun, :amount, :ref_kode, :ref_nama, :tanggal, 
                         :kecamatan_kd, :kecamatan_nm, :kelurahan_kd, 
                         :kelurahan_nm, :is_kota, :sumber_data, :sumber_id)""")
                         
    eng_dst.execute(sql,kode           = source['kode'],
                        disabled       = 0,
                        created        = datetime.now(),
                        updated        = datetime.now(),
                        create_uid     = 1,
                        nama           = source['nama'],
                        tahun          = source['tahun'],
                        amount         = source['amount'],
                        ref_kode       = source['ref_kode'],
                        ref_nama       = source['ref_nama'],
                        tanggal        = source['tanggal'],
                        kecamatan_kd   = source['kecamatan_kd'],
                        kecamatan_nm   = source['kecamatan_nm'],
                        kelurahan_kd   = source['kelurahan_kd'],
                        kelurahan_nm   = source['kelurahan_nm'],
                        is_kota        = source['is_kota'],
                        sumber_data    = source['sumber_data'],
                        sumber_id      = source['sumber_id'],
                    )

def update(source):
    sql = text("""UPDATE eis.ar_payment_detail 
                    set kode           = :kode,
                        disabled       = :disabled,
                        created        = :created,
                        updated        = :updated,
                        create_uid     = :create_uid,
                        nama           = :nama,
                        tahun          = :tahun,
                        amount         = :amount,
                        ref_kode       = :ref_kode,
                        ref_nama       = :ref_nama,
                        tanggal        = :tanggal,
                        kecamatan_kd   = :kecamatan_kd,
                        kecamatan_nm   = :kecamatan_nm,
                        kelurahan_kd   = :kelurahan_kd,
                        kelurahan_nm   = :kelurahan_nm,
                        is_kota        = :is_kota,
                        sumber_data    = :sumber_data,
                        sumber_id      = :sumber_id
                WHERE tahun = :tahun AND kode = :kode AND ref_kode = :ref_kode""")
                
    eng_dst.execute(sql,kode           = source['kode'],
                        disabled       = 0,
                        created        = datetime.now(),
                        updated        = datetime.now(),
                        create_uid     = 1,
                        nama           = source['nama'],
                        tahun          = source['tahun'],
                        amount         = source['amount'],
                        ref_kode       = source['ref_kode'],
                        ref_nama       = source['ref_nama'],
                        tanggal        = source['tanggal'],
                        kecamatan_kd   = source['kecamatan_kd'],
                        kecamatan_nm   = source['kecamatan_nm'],
                        kelurahan_kd   = source['kelurahan_kd'],
                        kelurahan_nm   = source['kelurahan_nm'],
                        is_kota        = source['is_kota'],
                        sumber_data    = source['sumber_data'],
                        sumber_id      = source['sumber_id'],
                    )
                
filenm = 'import-eis'
pid_file = '/var/run/%s.pid' % filenm
pid = demon.make_pid(pid_file)
log = demon.Log('/var/log/%s.log' % filenm)

arg = sys.argv[0]
c = len(sys.argv) 
print c
#if c < 1:
#    print 'python import-csv [path]'
#    sys.exit()
    
path = "/home/eis/"
if c>1:
    path = sys.argv[1]

eng_dst = create_engine(db_url_dst)
eng_dst.echo=True
for file in os.listdir('%s' % path):
    fileName, fileExtension = os.path.splitext(file)
    #file = 
    if fileExtension == '.csv':
        with open('%s/%s' %(path,file), 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in spamreader:
                c = row.count
                datas = {}    
                datas['kode']         = row and row[0] and row[ 0].strip() or None
                datas['nama']         = row and row[1] and row[ 1].strip() or None
                datas['tahun']        = row and row[2] and row[ 2].strip() or None
                datas['amount']       = row and row[3] and row[ 3].strip() or None       
                datas['ref_kode']     = row and row[4] and row[ 4].strip() or None
                datas['ref_nama']     = row and row[5] and row[ 5].strip() or None
                datas['tanggal']      = row and row[6] and row[ 6].strip() or None          
                datas['kecamatan_kd'] = row and c > 7  and row[ 7].strip() or None          
                datas['kecamatan_nm'] = row and c > 8  and row[ 8].strip() or None          
                datas['kelurahan_kd'] = row and c > 9  and row[ 9].strip() or None          
                datas['kelurahan_nm'] = row and c > 10 and row[10].strip() or None          
                datas['is_kota']      = row and c > 11 and row[11].strip() or None          
                datas['sumber_data']  = row and c > 12 and row[12].strip() or None          
                datas['sumber_id']    = row and c > 13 and row[13].strip() or None          
                # print datas
                # print datas['kode']
                
                if data_found(datas):
                    update(datas)
                else:
                    insert(datas)
            # csvfile.cose()                          
            os.rename('%s/%s' %(path,file), '/home/eis-bak/%s-%s.bak' % (file, datetime.now()))   
info('Selesai')          
os.remove(pid_file)