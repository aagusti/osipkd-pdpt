#!/usr/bin/python

# Synchronizer untuk yang kurang bayar
# Logic by: aa.gustiana@gmail.com
# Finishing by: sugiana@gmail.com

import sys
from config import (db_url_src, db_url_dst)
from tools import humanize_time, print_log, eng_profile, stop_daemon, rt_rw
import os
import demon
import signal
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

def get_syncs():
    sql = """SELECT unitkd, unitnm
    FROM tblunit
    ORDER by unitkd"""
    return eng_src.execute(sql)

def insert():
    sql = text("""INSERT INTO admin.units (kode, nama, urusan_id, created, updated, disabled) 
        VALUES (:kode, :nama, :urusan_id, :created, :updated, :disabled)""")
    eng_dst.execute(sql, kode = source.unitkd,
        nama = source.unitnm, urusan_id = 1,
        created = datetime.now(), updated=datetime.now(),
        disabled=0)

filenm = 'import-units'
pid_file = '/var/run/%s.pid' % filenm
pid = demon.make_pid(pid_file)
log = demon.Log('/var/log/%s.log' % filenm)

eng_src = create_engine(db_url_src)
eng_dst = create_engine(db_url_dst)

eng_src.debug=True
#sql = 'select count(*) from dbo.tblUnit'
sql = 'SELECT count(*) count  FROM tblunit'
q = eng_src.execute(sql)
count = q.fetchone().count
msg = 'Ada %d baris yang akan diselaraskan' % count
print_log(msg)
if count:
    log.info(msg)
    sources = get_syncs()
    row = 0
    awal = time()
    log_row = 0
    for source in sources.fetchall():
        row += 1
        log_row += 1
        try:
            insert()
        except Exception, e:
            error(e[0])
            sys.exit()
        durasi = time() - awal
        kecepatan = durasi / row
        sisa_row = count - row
        estimasi_selesai = sisa_row * kecepatan
        estimasi = humanize_time(estimasi_selesai)
        msg = '%d/%d estimasi %s' % (row, count, estimasi)
        print_log(msg)
        if log_row == 100: # Hemat log file
            log.info(msg)
            log_row = 0

info('Selesai')
os.remove(pid_file)
