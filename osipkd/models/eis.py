from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    SmallInteger,
    Text,
    DateTime,
    String,
    UniqueConstraint,
    ForeignKey,
    Index
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship, backref
    )
from zope.sqlalchemy import ZopeTransactionExtension
import transaction
from ..tools import as_timezone
from ..models import (DBSession, DefaultModel,Base,)
from ..models.base_model import (NamaModel)

class Eis(DefaultModel, Base):
    __tablename__ = 'wells'
    __table_args__ = {'extend_existing':True, 
                      'schema' : 'eis',}
    
    tahun = Column(Integer)
    kode  = Column(String(24))
    uraian = Column(String(128))
    amt_tahun = Column(BigInteger)
    amt_bulan = Column(BigInteger)
    amt_minggu = Column(BigInteger)
    amt_hari   = Column(BigInteger)
    order_id   = Column(Integer)
    is_aktif   = Column(SmallInteger)
    disabled   = Column(SmallInteger, default=0)
    

    @classmethod
    def sum_data(cls, kode, tahun):
        q = DBSession.query(cls).filter_by(
                kode==kode,
                tahun=tahun).first()
        if q:
            sum_minggu = q.amt_minggu+q.amt_hari
            sum_bulan  = q.amt_bulan + sum_minggu
            sum_tahun  = q.amt_tahun + sum_bulan
            return  dict(sum_hari = sum_hari, sum_minggu = sum_minggu, 
                         sum_bulan = sum_bulan, sum_tahun = sum_tahun)
            
        return {}
        
    @classmethod
    def sum_order_id(cls, tahun):
        q = DBSession.query(cls).filter_by(
                tahun=tahun)
        if q:
            return  q
        return 

class Slide(NamaModel, Base):
    __tablename__ = 'slides'
    __table_args__ = {'extend_existing':True, 
                      'schema' : 'eis',}
    source_type = Column(String(16)) #grid, image, chart-line, chart-pie, chart-bar
    source_id   = Column(String(128))
    order_id   = Column(Integer, default=0)
    is_aktif   = Column(SmallInteger, default=0)

class Chart(NamaModel, Base):
    __tablename__ = 'charts'
    __table_args__ = (UniqueConstraint('kode'),
                      {'extend_existing':True, 
                      'schema' : 'eis',})
    chart_type = Column(String(16))                  
    label      = Column(String(128)) #digunakan jika chart membutuhkan label                  
    devider    = Column(BigInteger, default=1)
                      
class ChartItem(NamaModel, Base):
    __tablename__ = 'chart_items'
    __table_args__ = (UniqueConstraint('kode'),
                      {'extend_existing':True, 
                      'schema' : 'eis',})
    value_1 = Column(BigInteger, default=0)
    value_2 = Column(BigInteger, default=0)
    value_3 = Column(BigInteger, default=0)
    value_4 = Column(BigInteger, default=0)
    value_5 = Column(BigInteger, default=0)
    value_6 = Column(BigInteger, default=0)
    value_7 = Column(BigInteger, default=0)
    value_8 = Column(BigInteger, default=0)
    value_9 = Column(BigInteger, default=0)
    value10 = Column(BigInteger, default=0)
    value11 = Column(BigInteger, default=0)
    value12 = Column(BigInteger, default=0)
    chart_id = Column(Integer, ForeignKey('eis.charts.id'))
    source_type = Column(String(32), default='realisasi')
    rekening_kd = Column(String(128))
    color = Column(String(6))
    highlight = Column(String(6))
    is_sum   = Column(SmallInteger, default=0)
    chart   = relationship("Chart")
    
class LastUpdate(DefaultModel, Base):
    __tablename__ = 'last_update'
    __table_args__ = {'extend_existing':True, 
                      'schema' : 'eis',}
    
    wells = Column(DateTime(timezone=True), nullable=True)


class ARPaymentDetail(NamaModel, Base):
    __tablename__ = 'ar_payment_detail'
    __table_args__ = {'extend_existing':True, 
                      'schema' : 'eis',}
    tahun = Column(Integer)
    amount = Column(BigInteger)
    ref_kode = Column(String(32))
    ref_nama = Column(String(64))
    tanggal = Column(DateTime(timezone=True), nullable=True)
    kecamatan_kd = Column(String(32))
    kecamatan_nm = Column(String(64))
    kelurahan_kd = Column(String(32))
    kelurahan_nm = Column(String(64))
    is_kota      = Column(SmallInteger)
    sumber_data  = Column(String(32)) #Manual, PBB, BPHTB, PAD
    sumber_id    = Column(SmallInteger)#1, 2, 3, 4
    bulan = Column(Integer)
    minggu = Column(Integer)
    hari = Column(Integer)
        
class ARInvoiceDetail(NamaModel, Base):
    __tablename__ = 'ar_invoice_detail'
    __table_args__ = {'extend_existing':True, 
                      'schema' : 'eis',}
    tahun = Column(Integer, index=True)
    amount = Column(BigInteger)
    ref_kode = Column(String(32), index=True)
    ref_nama = Column(String(64))
    tanggal = Column(DateTime(timezone=True), nullable=True)
    kecamatan_kd = Column(String(32))
    kecamatan_nm = Column(String(64))
    kelurahan_kd = Column(String(32))
    kelurahan_nm = Column(String(64))
    is_kota      = Column(SmallInteger)
    sumber_data  = Column(String(32)) #Manual, PBB, BPHTB, PAD
    sumber_id    = Column(SmallInteger)#1, 2, 3, 4
    bulan = Column(Integer, index=True)
    minggu = Column(Integer, index=True)
    hari = Column(Integer, index=True)
        
class ARTargetDetail(NamaModel, Base):
    __tablename__ = 'ar_target_detail'
    __table_args__ = {'extend_existing':True, 
                      'schema' : 'eis',}
    tahun = Column(Integer)
    amount_01 = Column(BigInteger)
    amount_02 = Column(BigInteger)
    amount_03 = Column(BigInteger)
    amount_04 = Column(BigInteger)
    amount_05 = Column(BigInteger)
    amount_06 = Column(BigInteger)
    amount_07 = Column(BigInteger)
    amount_08 = Column(BigInteger)
    amount_09 = Column(BigInteger)
    amount_10 = Column(BigInteger)
    amount_11 = Column(BigInteger)
    amount_12 = Column(BigInteger)
    