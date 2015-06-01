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
                "cmd":"trx.today",
                "paramCount":0,
                "param": ""
              } ]
            }
    jsondata=json.dumps(data, ensure_ascii=False)        
    headers = {'f-client':'DISPENDAAKUNTANSI',
               'f-signature':encodedSignature,
               'f-key':int(tStamp.total_seconds())}
               
    url = "http://192.168.56.5:6543/test"
    url = "http://192.168.168.5:8181/pbbws/sismiop/trxlive"
    rows = requests.post(url, data=jsondata,headers=headers)
    datas = json.loads(rows.text)
    # Loop through the result.
    tahun   = tanggal.year
    rekening = Rekening.get_by_kode(pbb['rekening_kd'])
    if 'trx.today' not in datas:
       return False
    
    i = 0
    for row in datas['trx.today']:
      print row
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
          odata.rekening_id     = Rekening.get_by_kode(pbb['rekening_kd']).id
          odata.ref_kode        = ''.join([row['nop'],'-',row['thn_pajak_sppt'],'-',str(row['pembayaran_sppt_ke'])])
          odata.ref_nama        = row['nama_wp']
          odata.tanggal         = row['tgl_pembayaran_sppt'] #Y-m-d
          odata.sumber_data     = 'PBB'
          odata.sumber_id       = 2
          odata.posted          = 0
          osipkd_Session.add(odata)
          osipkd_Session.flush()

          #odata.updated         =
          #odata.update_uid      =
      i += 1
      if i/100 == i/100.0:
        print 'Commit ', i
        osipkd_Session.commit()
    if i==0:
        return False
    osipkd_Session.commit()
    return True
if __name__ == '__main__':
    print sys.argv
    osipkd_Base.metadata.create_all()
    if len(sys.argv)>1:
        tanggal = datetime.strptime(sys.argv[1],'%Y%m%d')
        import_pbb(tanggal)
    else:
        tanggal = datetime.combine(date.today(), datetime.min.time())
        qdata = osipkd_Session.query(Sync).first()
        if not import_pbb(tanggal):
            print 'Data Kosong'
                #sys.exit()
    
