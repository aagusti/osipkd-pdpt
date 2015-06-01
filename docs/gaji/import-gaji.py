#!/usr/bin/python

# Synchronizer untuk yang kurang bayar
# Logic by: aa.gustiana@gmail.com
# Finishing by: sugiana@gmail.com

import sys
from config import (db_url_src, db_url_dst)
from tools import humanize_time, print_log, eng_profile, stop_daemon, rt_rw
import os
#import demon
#import signal
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
    #log.info(s)
    
def error(s):
    print_log(s, 'ERROR')
    #log.error(s)    

def get_syncs():
    sql = text("""SELECT *
    FROM pegawai_gaji
    WHERE tahun=:tahun AND bulan=:bulan AND jenis=:jenis
    ORDER by nip""")
    return eng_src.execute(sql, tahun=tahun, bulan=bulan, jenis=jenis)

def insert():
    sql = text("""INSERT INTO gaji_pegawai(
       tahun, bulan, jenis, nip, unitkd,  nama, tgl_lahir, 
       tmp_lahir, jns_kelamin, bank, rekening, npwp, no_pegawai, nojjp, 
       alamat, namasi, sts_pegawaikd, tmt_pegawai, sts_kwn, sts_sipil, 
       agama, jml_si, jml_anak, golongankd, tmt_golongan, masakerja, 
       jbt_fungsikd, jbt_strukturkd, tmt_jabatan, tunj_jab_fungsi, tunj_jab_struktur, 
       gaji_pokok, tmt_gaji_pokok, tunj_istri, tunj_anak, tunj_beras, 
       gurukd, operator, tgl_ubah, tunj_kerja, tdtkd, pend_terakhir, 
       pend_jurusan, v_jab_struktur, pot_iwp, pot_taperum, pot_sewa_rumah, 
       pot_pangan, pot_korpri, pot_gaji_lebih, pot_hutang, pembulatan, 
       pph, tunj_umum, tunj_umum_tamb, tunj_otsus, tunj_dt, tunj_askes, 
       tunj_penghasilan, biaya_jabatan, biaya_pensiun, persen_gaji, 
       isttu, aktif_kd, ptkp, aktif_tgl, tmt_fungsi) 
       VALUES (:tahun, :bulan, :jenis, :nip, :unitkd, :nama, :tgl_lahir, 
       :tmp_lahir, :jns_kelamin, :bank, :rekening, :npwp, :no_pegawai, :nojjp, 
       :alamat, :namasi, :sts_pegawaikd, :tmt_pegawai, :sts_kwn, :sts_sipil, 
       :agama, :jml_si, :jml_anak, :golongankd, :tmt_golongan, :masakerja, 
       :jbt_fungsikd, :jbt_strukturkd, :tmt_jabatan, :tunj_jab_fungsi, :tunj_jab_struktur, 
       :gaji_pokok, :tmt_gaji_pokok, :tunj_istri, :tunj_anak, :tunj_beras, 
       :gurukd, :operator, :tgl_ubah, :tunj_kerja, :tdtkd, :pend_terakhir, 
       :pend_jurusan, :v_jab_struktur, :pot_iwp, :pot_taperum, :pot_sewa_rumah, 
       :pot_pangan, :pot_korpri, :pot_gaji_lebih, :pot_hutang, :pembulatan, 
       :pph, :tunj_umum, :tunj_umum_tamb, :tunj_otsus, :tunj_dt, :tunj_askes, 
       :tunj_penghasilan, :biaya_jabatan, :biaya_pensiun, :persen_gaji, 
       :isttu, :aktif_kd, :ptkp, :aktif_tgl, :tmt_fungsi)""")
    eng_dst.execute(sql, tahun                 = source.TAHUN            ,
                        bulan                  = source.BULAN            ,
                        jenis                  = source.JENIS            ,
                        nip                    = source.NIP              ,
                        unitkd                 = source.UNITKD           ,
                        nama                   = source.NAMA             ,
                        tgl_lahir              = source.TGL_LAHIR        ,
                        tmp_lahir              = source.TMP_LAHIR        ,
                        jns_kelamin            = source.JNS_KELAMIN      ,
                        bank                   = source.BANK             ,
                        rekening               = source.REKENING         ,
                        npwp                   = source.NPWP             ,
                        no_pegawai             = source.NO_PEGAWAI       ,
                        nojjp                  = source.NOJJP            ,
                        alamat                 = source.ALAMAT           ,
                        namasi                 = source.NAMASI           ,
                        sts_pegawaikd          = source.STS_PEGAWAIKD    ,
                        tmt_pegawai            = source.TMT_PEGAWAI      ,
                        sts_kwn                = source.STS_KWN          ,
                        sts_sipil              = source.STS_SIPIL        ,
                        agama                  = source.AGAMA            ,
                        jml_si                 = source.JML_SI           ,
                        jml_anak               = source.JML_ANAK         ,
                        golongankd             = source.GOLONGANKD       ,
                        tmt_golongan           = source.TMT_GOLONGAN     ,
                        masakerja              = source.MASAKERJA        ,
                        jbt_fungsikd           = source.JBT_FUNGSIKD     ,
                        jbt_strukturkd         = source.JBT_STRUKTURKD   ,
                        tmt_jabatan            = source.TMT_JABATAN      ,
                        tunj_jab_fungsi        = source.TUNJ_JAB_FUNGSI  ,
                        tunj_jab_struktur      = source.TUNJ_JAB_STRUKTUR,
                        gaji_pokok             = source.GAJI_POKOK       ,
                        tmt_gaji_pokok         = source.TMT_GAJI_POKOK   ,
                        tunj_istri             = source.TUNJ_ISTRI       ,
                        tunj_anak              = source.TUNJ_ANAK        ,
                        tunj_beras             = source.TUNJ_BERAS       ,
                        gurukd                 = source.GURUKD           ,
                        operator               = source.OPERATOR         ,
                        tgl_ubah               = source.TGL_UBAH         ,
                        tunj_kerja             = source.TUNJ_KERJA       ,
                        tdtkd                  = source.TDTKD            ,
                        pend_terakhir          = source.PEND_TERAKHIR    ,
                        pend_jurusan           = source.PEND_JURUSAN     ,
                        v_jab_struktur         = source.V_JAB_STRUKTUR   ,
                        pot_iwp                = source.POT_IWP          ,
                        pot_taperum            = source.POT_TAPERUM      ,
                        pot_sewa_rumah         = source.POT_SEWA_RUMAH   ,
                        pot_pangan             = source.POT_PANGAN       ,
                        pot_korpri             = source.POT_KORPRI       ,
                        pot_gaji_lebih         = source.POT_GAJI_LEBIH   ,
                        pot_hutang             = source.POT_HUTANG       ,
                        pembulatan             = source.PEMBULATAN       ,
                        pph                    = source.PPH              ,
                        tunj_umum              = source.TUNJ_UMUM        ,
                        tunj_umum_tamb         = source.TUNJ_UMUM_TAMB   ,
                        tunj_otsus             = source.TUNJ_OTSUS       ,
                        tunj_dt                = source.TUNJ_DT          ,
                        tunj_askes             = source.TUNJ_ASKES       ,
                        tunj_penghasilan       = source.TUNJ_PENGHASILAN ,
                        biaya_jabatan          = source.BIAYA_JABATAN    ,
                        biaya_pensiun          = source.BIAYA_PENSIUN    ,
                        persen_gaji            = source.Persen_Gaji      ,
                        isttu                  = source.IsTTU            ,
                        aktif_kd               = source.AKTIF_KD         ,
                        ptkp                   = source.PTKP             ,
                        aktif_tgl              = source.AKTIF_TGL        ,
                        tmt_fungsi             = source.TMT_FUNGSI       ,
                    )

filenm = 'import-units'
pid_file = '/var/run/%s.pid' % filenm
#pid = demon.make_pid(pid_file)
#log = demon.Log('/var/log/%s.log' % filenm)
#eng_src.echo=True
tahun = '2014'
bulan = '01'
jenis = '0'

arg = sys.argv[0]
c = len(sys.argv) 
if c > 1 and c < 3:
    print 'python import-gaji [tahun] [bulan]'
    sys.exit()
if c>1:
    tahun = sys.argv[1]
    bulan = sys.argv[2]

eng_src = create_engine(db_url_src)
print(db_url_src)
eng_src.connect()
eng_dst = create_engine(db_url_dst)

sql = text("""SELECT count(*) count  FROM pegawai_gaji 
              WHERE tahun=:tahun AND bulan=:bulan AND jenis=:jenis""")
              
q = eng_src.execute(sql, tahun=tahun, bulan=bulan, jenis=jenis)
count = q.fetchone().count
msg = 'Ada %d baris yang akan diselaraskan' % count
print_log(msg)
if count:
    #log.info(msg)
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
            #log.info(msg)
            log_row = 0

info('Selesai')
#os.remove(pid_file)
