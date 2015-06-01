#!/usr/bin/python

from base import *

from sync_osipkd import ARInvoice, ARPayment, Rekening, Unit, Sync,osipkd_eng
from datetime import timedelta
class BphtbBank(bphtb_Base, base):
  __tablename__ ='bphtb_bank'
  __table_args__ = {'extend_existing':True,
         'schema' :'bphtb','autoload':True}
  
  @classmethod
  def query(cls):
      return bphtb_Session.query(cls)
  
  @classmethod
  def get_by_kode(cls,kode):
      return cls.query().filter_by(kode=kode).first()
  
  @classmethod
  def import_data(cls, tanggal=datetime.now()):
    #Tanggal = datetime.now()
    print tanggal
    tahun   = tanggal.year
    rows = cls.query().filter_by(tanggal=datetime.date(tanggal)).all()
    if not rows:
        print 'data tidak ditemukan'
    rekening = Rekening.get_by_kode(bphtb['rekening_kd'])
    i = 0
    for row in rows:
      odata = ARPayment.get_by_ref_kode(row.tahun,''.join([row.transno,'/',str(row.seq)]))
      if not odata:
          odata = ARPayment()
          odata.unit_id         = Unit.get_by_kode(bphtb['unit_kd'])
          odata.kode            = rekening.kode
          odata.disabled        = 0
          odata.created         = tanggal
          odata.create_uid      = 1
          odata.nama            = 'Setoran BPHTB WP'
          odata.tahun           = row.tahun
          odata.amount          = row.bayar
          odata.unit_id         = Unit.get_by_kode(bphtb['unit_kd']).id
          odata.rekening_id     = Rekening.get_by_kode(bphtb['rekening_kd']).id
          odata.ref_kode        = '%s/%s' % (row.transno,row.seq)
          odata.ref_nama        = row.wpnama
          odata.tanggal         = row.tanggal
          odata.sumber_data     = 'BPHTB'
          odata.sumber_id       = 3
          odata.posted          = 0
          osipkd_Session.add(odata)
          osipkd_Session.flush()

      #odata = ARInvoice.get_by_ref_kode(row.tahun,''.join([row.transno,'/',str(row.seq)]))
      #if not odata:
      #    odata = ARInvoice()
      #    odata.unit_id         = Unit.get_by_kode(bphtb['unit_kd'])
      #    odata.kode            = rekening.kode
      #    odata.disabled        = 0
      #    odata.created         = tanggal
      #    odata.create_uid      = 1
      #    odata.nama            = 'Setoran BPHTB WP'
      #    odata.tahun           = row.tahun
      #    odata.amount          = row.bayar
      #    odata.unit_id         = Unit.get_by_kode(bphtb['unit_kd']).id
      #    odata.rekening_id     = Rekening.get_by_kode(bphtb['rekening_kd']).id
      #    odata.ref_kode        = '%s/%s' % (row.transno,row.seq)
      #    odata.ref_nama        = row.wpnama
      #    odata.tanggal         = row.tanggal
      #    odata.sumber_data     = 'BPHTB'
      #    odata.sumber_id       = 3
      #    odata.posted          = 0
      #    osipkd_Session.add(odata)
      #    osipkd_Session.flush()
      i += 1
      if i/100 == i/100.0:
        print 'Commit ', i
        osipkd_Session.commit()
          
    osipkd_Session.commit()
    
if __name__ == '__main__':
    print sys.argv
    osipkd_Base.metadata.create_all()
    if len(sys.argv)>1:
        tanggal = datetime.strptime(sys.argv[1],'%Y%m%d')
        BphtbBank.import_data(tanggal)
        #print tanggal.year
    else:
        tanggal = datetime.combine(date.today(), datetime.min.time())
        qdata = osipkd_Session.query(Sync).first()
        if not qdata:
            qdata = Sync()
            qdata.bphtb = datetime.strptime('2015-01-01','%Y-%m-%d')
        if not qdata.bphtb:
            qdata.bphtb = datetime.strptime('2015-01-01','%Y-%m-%d')
        old = qdata.bphtb
        while old < tanggal+timedelta(days=1):
            BphtbBank.import_data(old)
            old = old +timedelta(days=1)
        qdata.bphtb = tanggal
        osipkd_Session.add(qdata)
        osipkd_Session.flush()
        osipkd_Session.commit()
