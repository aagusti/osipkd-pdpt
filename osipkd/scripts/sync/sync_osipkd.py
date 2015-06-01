from base import *


class ARInvoice(osipkd_Base, base):
  __tablename__ ='ar_invoice_item'
  __table_args__ = {'extend_existing':True, 
         'schema' :'apbd','autoload':True}         
  @classmethod
  def get_by_kode(cls,tahun, ref_kode):
      return osipkd_Session.query(cls).filter_by(tahun=tahun, ref_kode=ref_kode).first()
  @classmethod
  def get_by_ref_kode(cls,tahun, ref_kode):
      return osipkd_Session.query(cls).filter_by(tahun=tahun, ref_kode=ref_kode).first()


class ARPayment(osipkd_Base, base):
  __tablename__ ='ar_payment_item'
  __table_args__ = {'extend_existing':True, 
         'schema' :'apbd','autoload':True}         
  @classmethod
  def get_by_kode(cls,tahun, ref_kode):
      return osipkd_Session.query(cls).filter_by(tahun=tahun, ref_kode=ref_kode).first()
  @classmethod
  def get_by_ref_kode(cls,tahun, ref_kode):
      return osipkd_Session.query(cls).filter_by(tahun=tahun, ref_kode=ref_kode).first()

class Unit(osipkd_Base, base):
  __tablename__ ='units'
  __table_args__ = {'extend_existing':True, 
         'schema' :'admin','autoload':True}         
  @classmethod
  def query(cls):
      return osipkd_Session.query(cls)
      
  @classmethod
  def get_by_kode(cls,kode):
      return cls.query().filter_by(kode=kode).first()

class Rekening(osipkd_Base, base):
  __tablename__ ='rekenings'
  __table_args__ = {'extend_existing':True, 
         'schema' :'admin','autoload':True}         
  @classmethod
  def query(cls):
      return osipkd_Session.query(cls)
      
  @classmethod
  def get_by_kode(cls,kode):
      return cls.query().filter_by(kode=kode).first()
 
class Sync(osipkd_Base, base):
    __tablename__ ='syncs'
    id    = Column(Integer,primary_key=True)
    bphtb = Column(DateTime)
    pbb   = Column(DateTime)

if __name__ == '__main__':
  pass
