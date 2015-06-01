#!/usr/bin/python

# PEMBAYARAN SPPT Synchronizer
# Logic by: aa.gustiana@gmail.com
# Finishing by: sugiana@gmail.com

import sys
sys.path.insert(0, '/etc/opensipkd')
sys.path.insert(0, '/usr/share/opensipkd')

from db_connection import db_eis as db_url
from tools import humanize_time, print_log, eng_profile, stop_daemon
import os
import demon
import signal
import ntpath

from time import time
from datetime import datetime
from urllib import unquote_plus
from urlparse import urlparse
from optparse import OptionParser

from sqlalchemy import create_engine
from sqlalchemy.sql.expression import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import DatabaseError
from sqlalchemy import Column, BigInteger, Integer, String, Boolean, DateTime, Sequence, Numeric
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import select,func
from sqlalchemy.orm import create_session

db_url ="postgresql://osipkd:z30s@localhost/gaji_pns"
def info(s):
    print_log(s)
    log.info(s)
    
def error(s):
    print_log(s, 'ERROR')
    log.error(s)

def conf_info():
    if not db_url:
        print('Sesuaikan /etc/opensipkd/db_connection.py, lalu ' + \
              '%s --configure' % SYNC_TABLE)
        sys.exit()

###############################################################################
pars = OptionParser()
pars.add_option('-c', '--configure', action='store_true',
                help='Configure database')
pars.add_option('', '--configuration-check', action='store_true',
                help='Configuration check')
pars.add_option('', '--stop', action='store_true',
                help='Stop daemon')
option, remain = pars.parse_args(sys.argv[1:])

conf_info()

if option.configuration_check:
    sys.exit()
################################################################################
if option.stop:
    stop_daemon(pid_file)


###############################################################################    


SYNC_TABLE = ntpath.basename(sys.argv[0])
SYNC_SEQ = '%s_seq' % SYNC_TABLE
pid_file = '/var/run/%s.pid' % SYNC_TABLE

if pos_field_type==1:
    SYNC_FIELD = "kd_kanwil, kd_kantor, "
    SYNC_FIELD_NEW = "new.kd_kanwil, new.kd_kantor, "
else:
    SYNC_FIELD = "kd_kanwil_bank, kd_kppbb_bank, kd_bank_tunggak, kd_bank_persepsi, "
    SYNC_FIELD_NEW = "new.kd_kanwil_bank, new.kd_kppbb_bank, new.kd_bank_tunggak, new.kd_bank_persepsi, "
#Create Engine
eng_src = create_engine(db_url_src)
BasePg  = declarative_base()
BasePg.metadata.bind = eng_src

eng_dst = create_engine(db_url_dst)
BaseOra = declarative_base()
BaseOra.metadata.bind = eng_dst
################################################################################

class Sync(BasePg):
    __tablename__ = SYNC_TABLE
    __table_args__ = {'extend_existing':True,
                      'schema' : db_schema_pg,
                     }
    id = Column(BigInteger, primary_key=True)
    kd_propinsi = Column(String(2), nullable=False)
    kd_dati2 = Column(String(2), nullable=False)
    kd_kecamatan = Column(String(3), nullable=False)
    kd_kelurahan = Column(String(3), nullable=False)
    kd_blok = Column(String(3), nullable=False)
    no_urut = Column(String(4), nullable=False)
    kd_jns_op = Column(String(1), nullable=False)
    thn_pajak_sppt = Column(String(4), nullable=False)
    pembayaran_sppt_ke = Column(Numeric(2,0), nullable=False)
    if pos_field_type==2:
        kd_kanwil_bank = Column(String(2), nullable=False)
        kd_kppbb_bank = Column(String(2), nullable=False)
        kd_bank_tunggal = Column(String(2), nullable=False)
        kd_bank_persepsi = Column(String(2), nullable=False)
    else:
        kd_kanwil = Column(String(2), nullable=False)
        kd_kantor = Column(String(2), nullable=False)
        
    kd_tp = Column(String(2), nullable=False)
    jns_sinkron = Column(String(1), nullable=False)

class BaseTable(object):
    __tablename__ = ''
    @classmethod
    def get_count(cls):
        return DBSession.query(func.count(cls.id)).first()
    
class PembayaranPg(BasePg):
    __tablename__ = 'pembayaran_sppt'
    __table_args__ = {'extend_existing':True,
                      'schema' : db_schema_pg,
                      'autoload':True,
                      }
    
    
class PembayaranOra(BaseOra):
    __tablename__ = 'pembayaran_sppt'
    __table_args__ = {'extend_existing':True,
                      'schema' : db_schema_ora,
                      'autoload':True
                      }
TRIGGER_SYNC_INSERT = """CREATE OR REPLACE FUNCTION %s.%s_AIU()
    RETURNS TRIGGER AS
    $BODY$
    BEGIN
        IF new.nip_rekam_byr_sppt='999999999' THEN
            IF TG_OP='INSERT' THEN
                INSERT INTO %s (kd_propinsi, kd_dati2, kd_kecamatan,
                    kd_kelurahan, kd_blok, no_urut, kd_jns_op, thn_pajak_sppt, 
                    pembayaran_sppt_ke, %s kd_tp, jns_sinkron)
                SELECT new.kd_propinsi, new.kd_dati2, new.kd_kecamatan,
                    new.kd_kelurahan, new.kd_blok, new.no_urut, new.kd_jns_op,
                    new.thn_pajak_sppt, new.pembayaran_sppt_ke, %s new.kd_tp, '2';
                RETURN NEW;
            ELSIF TG_OP='UPDATE' THEN
                INSERT INTO %s (kd_propinsi, kd_dati2, kd_kecamatan,
                    kd_kelurahan, kd_blok, no_urut, kd_jns_op, thn_pajak_sppt, 
                    pembayaran_sppt_ke, %s kd_tp, jns_sinkron)
                SELECT new.kd_propinsi, new.kd_dati2, new.kd_kecamatan,
                    new.kd_kelurahan, new.kd_blok, new.no_urut, new.kd_jns_op,
                    new.thn_pajak_sppt, new.pembayaran_sppt_ke, %s new.kd_tp, '3';
                RETURN NEW;

            END IF;
        ELSE
            RETURN NEW;
        END IF;
    END;
    $BODY$
    LANGUAGE plpgsql VOLATILE
    COST 100;
    """ % (db_schema_pg, SYNC_TABLE, 
           SYNC_TABLE, SYNC_FIELD, SYNC_FIELD_NEW, 
           SYNC_TABLE, SYNC_FIELD, SYNC_FIELD_NEW)

TRIGGER_INSERT = """CREATE TRIGGER %s_trg
AFTER INSERT OR UPDATE ON %s.pembayaran_sppt FOR EACH ROW
EXECUTE PROCEDURE %s.%s_aiu();
""" % (SYNC_TABLE,db_schema_pg,db_schema_pg,SYNC_TABLE)

def init_db():
    try:
        BasePg.metadata.create_all(eng_src)
    except DatabaseError, e:
        print(e)
        sys.exit()
    print('Create table %s' % SYNC_TABLE)
    seq = Sequence(SYNC_SEQ)
    print('Create sequence %s' % SYNC_SEQ)
    seq.create(eng_src)
    create_trigger(eng_src, TRIGGER_SYNC_INSERT)
    create_trigger(eng_src, TRIGGER_INSERT)

if option.configure:
    init_db()
    sys.exit()

pid = demon.make_pid(pid_file)
log = demon.Log('/var/log/%s.log' % SYNC_TABLE)

session = create_session()

#sync = Sync.create()
row = session.query(func.count(Sync.id).label('c')).first()
count = row.c
msg = 'Ada %d baris yang akan diselaraskan' % count
print_log(msg)
if not count:
    os.remove(pid_file)
    sys.exit()
    
log.info(msg)
sources = session.query(PembayaranPg,Sync).\
    filter(Sync.kd_propinsi==PembayaranPg.kd_propinsi,
           Sync.kd_dati2==PembayaranPg.kd_dati2,
           Sync.kd_kecamatan==PembayaranPg.kd_kecamatan,
           Sync.kd_kelurahan==PembayaranPg.kd_kelurahan,
           Sync.kd_blok==PembayaranPg.kd_blok,
           Sync.no_urut==PembayaranPg.no_urut,
           Sync.kd_jns_op==PembayaranPg.kd_jns_op,
           Sync.thn_pajak_sppt==PembayaranPg.thn_pajak_sppt,
           Sync.pembayaran_sppt_ke==PembayaranPg.pembayaran_sppt_ke,
           Sync.kd_kanwil==PembayaranPg.kd_kanwil,
           Sync.kd_kantor==PembayaranPg.kd_kantor,
           Sync.kd_tp==PembayaranPg.kd_tp,
    ).all()

row = 0
log_row = 0
awal = time()
for source in sources:
    row += 1
    log_row += 1
    jenis = int(source.jns_sinkron)
    try:
        if jenis == 2: #Insert (copy data dari source ke target
            adata = PembayaranOra()
            adata.kd_propinsi = source.kd_propinsi
            adata.kd_dati2 = source.kd_dati2
            adata.kd_kecamatan = source.kd_kecamatan
            adata.kd_kelurahan = source.kd_kelurahan
            adata.kd_blok = source.kd_blok
            adata.no_urut = source.no_urut
            adata.kd_jns_op = source.kd_jns_op
            adata.thn_pajak_sppt = source.thn_pajak_sppt
            adata.pembayaran_sppt_ke = source.pembayaran_sppt_ke
            if pos_field_type==1:
                adata.kd_kanwil = source.kd_kanwil
                adata.kd_kantor = source.kd_kantor
            else:
                adata.kd_kanwil_bank = source.kd_kanwil_bank
                adata.kd_kppbb_bank = source.kd_kppbb_bank
                adata.kd_bank_tunggal = source.kd_bank_tunggal
                adata.kd_bank_persepsi = source.kd_bank_persepsi
            adata.kd_tp = source.kd_tp
            adata.denda_sppt = source.denda_sppt
            adata.jml_sppt_yg_dibayar = source.jml_sppt_yg_dibayar
            adata.tgl_rekam_bayar_sppt = source.tgl_rekam_bayar_sppt
            adata.tgl_pembayaran_sppt = source.tgl_pembayaran_sppt
            adata.nip_rekam_byr_sppt = source.nip_rekam_byr_sppt
            session.add(adata)
            
        elif jenis == 3: #Update (copy data dari source ke target
           #adata = lambda source: {c.name: str(getattr(source, c.name)) for c in PembayaranOra.__table__.columns}
            d = {}
            for column in PembayaranOra.__table__.columns:
                #print column.name, source.kd_propinsi
                d[column.name] = str(getattr(source, column.name))

            print adata
            sys.exit()
            session.query(PembayaranOra).filter(
               source.kd_propinsi==PembayaranPg.kd_propinsi,
               source.kd_dati2==PembayaranPg.kd_dati2,
               source.kd_kecamatan==PembayaranPg.kd_kecamatan,
               source.kd_kelurahan==PembayaranPg.kd_kelurahan,
               source.kd_blok==PembayaranPg.kd_blok,
               source.no_urut==PembayaranPg.no_urut,
               source.kd_jns_op==PembayaranPg.kd_jns_op,
               source.thn_pajak_sppt==PembayaranPg.thn_pajak_sppt,
               source.pembayaran_sppt_ke==PembayaranPg.pembayaran_sppt_ke,
               source.kd_kanwil==PembayaranPg.kd_kanwil,
               source.kd_kantor==PembayaranPg.kd_kantor,
               source.kd_tp==PembayaranPg.kd_tp,
            ).update(adata)
           
        else:
            print('Field jns_sinkron %d belum dibuat.' % jenis)
            print('Periksa lagi programnya.')
            sys.exit()
            
            #session.query(Sync).filter(Sync.id==source.sync_id).delete()
            #session.commit()
    except Exception, e:
          error(e[0])
#        sys.exit()
    if log_row == 100: # Hemat log file
        durasi = time() - awal
        kecepatan = durasi / row
        sisa_row = count - row
        estimasi_selesai = sisa_row * kecepatan
        estimasi = humanize_time(estimasi_selesai)
        msg = '%d / %d %s' % (row, count, estimasi)
        print_log(msg)                
        log.info(msg)
        log_row = 0
info('Selesai')
os.remove(pid_file)
