#!/usr/bin/python

from base import *

from sync_osipkd import ARInvoice, ARPayment, Rekening, Unit, Sync
from datetime import timedelta
import sys
import requests
import json
import hmac
import hashlib
import base64
import urllib
from datetime import datetime

def import_pbb(tanggal):
    utc_date = datetime.utcnow()
    tStamp = utc_date-datetime.strptime('1970-01-01 00:00:00','%Y-%m-%d %H:%M:%S'); 
    value = "DISPENDAAKUNTANSI&%s" % int(tStamp.total_seconds()); 
    key = "SISMIOP2015";

    signature = hmac.new(key, msg=value, digestmod=hashlib.sha256).digest() 
    encodedSignature = base64.encodestring(signature).replace('\n', '')
    data = {"commandCount":1,
            "command": [ {
                "cmd":"trx.tgl",
                "paramCount":1,
                "param": [tanggal.strftime('%Y-%m-%d')]
              } ]
            }
    print data
    jsondata=json.dumps(data, ensure_ascii=False)        
    headers = {'f-client':'DISPENDAAKUNTANSI',
               'f-signature':encodedSignature,
               'f-key':int(tStamp.total_seconds())}
               
    #url = "http://192.168.56.5:6543/test"
    url = "http://192.168.168.5:8181/pbbws/sismiop/trxlive"
    rows = requests.post(url, data=jsondata,headers=headers)
    datas = json.loads(rows.text)
    # Loop through the result.
    
    tahun   = tanggal.year
    rekening = Rekening.get_by_kode(pbb['rekening_kd'])
    denda    = Rekening.get_by_kode(pbb['denda_kd'])

    if 'trx.tgl' not in datas:
        print datas
        return -1 
    
    i = 0
    for row in datas['trx.tgl']:
      odata = ARPayment.get_by_ref_kode(tahun,''.join([row['nop'],'-',row['thn_pajak_sppt'],'-',str(row['pembayaran_sppt_ke'])]))
      if not odata:
          odata = ARPayment()
          odata.unit_id         = Unit.get_by_kode(pbb['unit_kd']).id
          odata.kode            = rekening.kode
          odata.disabled        = 0
          odata.created         = tanggal
          odata.create_uid      = 1
          odata.nama            = 'Setoran PBB WP'
          odata.tahun           = tahun
          odata.amount          = row['pokok']
          odata.rekening_id     = rekening.id
          odata.ref_kode        = ''.join([row['nop'],'-',row['thn_pajak_sppt'],'-',str(row['pembayaran_sppt_ke'])])
          odata.ref_nama        = row['nama_wp']
          odata.tanggal         = row['tgl_pembayaran_sppt'] #Y-m-d
          odata.sumber_data     = 'PBB'
          odata.sumber_id       = 2
          odata.posted          = 0
          osipkd_Session.add(odata)
          osipkd_Session.flush()

      if row['jumlah']-row['pokok']>0:
          odata = ARPayment.get_by_ref_kode(tahun,''.join([row['nop'],'-',row['thn_pajak_sppt'],'-',
                    str(row['pembayaran_sppt_ke']),'D']))
          if not odata:
              odata = ARPayment()
              odata.unit_id         = Unit.get_by_kode(pbb['unit_kd']).id
              odata.kode            = denda.kode
              odata.disabled        = 0
              odata.created         = tanggal
              odata.create_uid      = 1
              odata.nama            = 'Setoran Denda PBB WP'
              odata.tahun           = tahun
              odata.amount          = row['jumlah']-row['pokok']
              odata.rekening_id     = denda.id
              odata.ref_kode        = ''.join([row['nop'],'-',row['thn_pajak_sppt'],'-',str(row['pembayaran_sppt_ke']),'D'])
              odata.ref_nama        = row['nama_wp']
              odata.tanggal         = row['tgl_pembayaran_sppt'] #Y-m-d
              odata.sumber_data     = 'PBB'
              odata.sumber_id       = 2
              odata.posted          = 0
              osipkd_Session.add(odata)
              osipkd_Session.flush()
          odata = ARInvoice.get_by_ref_kode(tahun,''.join([row['nop'],'-',row['thn_pajak_sppt'],'-',
                                          str(row['pembayaran_sppt_ke']),'D']))
          """if not odata:
              odata = ARInvoice()
              odata.unit_id         = Unit.get_by_kode(pbb['unit_kd']).id
              odata.kode            = denda.kode
              odata.disabled        = 0
              odata.created         = tanggal
              odata.create_uid      = 1
              odata.nama            = 'Ketetapan Denda PBB WP'
              odata.tahun           = tahun
              odata.amount          = row['pokok']
              odata.rekening_id     = denda.id
              odata.ref_kode        = ''.join([row['nop'],'-',row['thn_pajak_sppt'],'-',str(row['pembayaran_sppt_ke']),'D'])
              odata.ref_nama        = row['nama_wp']
              odata.tanggal         = row['tgl_pembayaran_sppt'] #Y-m-d
              odata.sumber_data     = 'PBB'
              odata.sumber_id       = 2
              odata.posted          = 0
              osipkd_Session.add(odata)
              osipkd_Session.flush()"""


          #odata.updated         =
          #odata.update_uid      =
      i += 1
      if i/100 == i/100.0:
        print 'Commit ', i
        osipkd_Session.commit()
          
    osipkd_Session.commit()
    return True
if __name__ == '__main__':
    print sys.argv
    osipkd_Base.metadata.create_all()
    if len(sys.argv)>1:
        tanggal = datetime.strptime(sys.argv[1],'%Y%m%d')
        import_pbb(tanggal)
    else:
        #tanggal = date.today() +  timedelta(days=1)
        tanggal = datetime.combine(date.today(), datetime.min.time())
        qdata = osipkd_Session.query(Sync).first()
        if not qdata:
            qdata = Sync()
            qdata.pbb = datetime.strptime('2015-01-01','%Y-%m-%d')
        if not qdata.pbb:
            qdata.pbb = datetime.strptime('2015-01-01','%Y-%m-%d')
        old = qdata.pbb
        print 'old',  old
        while old < tanggal+timedelta(days=1):
            if import_pbb(old)==-1:
                print old
                print 'Koneksi Error'
                sys.exit()
            qdata.pbb = old
            old = old + timedelta(days=1)
            print tanggal, old, old + timedelta(days=-1)
            #qdata.pbb = old #+timedelta(days=-1)

            osipkd_Session.add(qdata)
            osipkd_Session.flush()
            osipkd_Session.commit()

    
