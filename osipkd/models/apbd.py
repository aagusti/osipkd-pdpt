from datetime import datetime
from sqlalchemy import (Column, Integer, String, SmallInteger, UniqueConstraint, 
                        Date, BigInteger, ForeignKey, func, extract, case)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship, backref
    )
from datetime import datetime
from zope.sqlalchemy import ZopeTransactionExtension
import transaction
from ..tools import as_timezone
from ..models import (DBSession, DefaultModel,Base,)
from ..models.base_model import (NamaModel)
from ..models.pemda_model import (Rekening,Unit)
from ..models.apbd_anggaran import (KegiatanSub)
        
class ARInvoiceItem(NamaModel, Base):
    __tablename__  = 'ar_invoice_item'
    __table_args__ = {'extend_existing':True, 'schema' : 'apbd',}

    units     = relationship("Unit",     backref=backref("ar_invoice_items"))
    rekenings = relationship("Rekening", backref=backref("ar_invoice_items"))

    unit_id      = Column(Integer, ForeignKey("admin.units.id"),     nullable=False)
    rekening_id  = Column(Integer, ForeignKey("admin.rekenings.id"), nullable=False)
    ref_kode     = Column(String(32), unique=True)
    ref_nama     = Column(String(64))
    tanggal      = Column(Date, nullable=False)
    amount       = Column(BigInteger)
    kecamatan_kd = Column(String(32))
    kecamatan_nm = Column(String(64))
    kelurahan_kd = Column(String(32))
    kelurahan_nm = Column(String(64))
    is_kota      = Column(SmallInteger, default=0)
    sumber_id    = Column(SmallInteger)#1, 2, 3, 4
    sumber_data  = Column(String(32)) #Manual, PBB, BPHTB, PADL
    tahun        = Column(Integer)
    bulan        = Column(Integer)
    minggu       = Column(Integer)
    hari         = Column(Integer)
    posted       = Column(SmallInteger, nullable=False, default=0)
    
    @classmethod
    def get_periode(cls, id):
        return DBSession.query(extract('month',cls.tanggal).label('periode'))\
                .filter(cls.id==id,)\
                .group_by(extract('month',cls.tanggal)
                ).scalar() or 0
                
class ARPaymentItem(NamaModel, Base):
    __tablename__  = 'ar_payment_item'
    __table_args__ = {'extend_existing':True, 'schema' : 'apbd',}

    units         = relationship("Unit",        backref=backref("ar_payment_items"))
    #kegiatan_subs = relationship("KegiatanSub", backref=backref("ar_payment_items"))
    rekenings     = relationship("Rekening",    backref=backref("ar_payment_items"))

    unit_id         = Column(Integer, ForeignKey("admin.units.id"),        nullable=False)
    #kegiatan_sub_id = Column(Integer, ForeignKey("apbd.kegiatan_subs.id"), nullable=False)
    rekening_id     = Column(Integer, ForeignKey("admin.rekenings.id"),    nullable=False)
    tahun           = Column(Integer)
    amount          = Column(BigInteger)
    ref_kode        = Column(String(32))
    ref_nama        = Column(String(64))
    tanggal         = Column(Date, nullable=True)
    kecamatan_kd    = Column(String(32))
    kecamatan_nm    = Column(String(64))
    kelurahan_kd    = Column(String(32))
    kelurahan_nm    = Column(String(64))
    is_kota         = Column(SmallInteger, default=0)
    sumber_data     = Column(String(32)) #Manual, PBB, BPHTB, PAD
    sumber_id       = Column(SmallInteger)#1, 2, 3, 4
    bulan           = Column(Integer)
    minggu          = Column(Integer)
    hari            = Column(Integer)
    posted          = Column(SmallInteger, nullable=False, default=0)
    bud_uid         = Column(BigInteger,   nullable=False)
    bud_nip         = Column(String(50),   nullable=False)
    bud_nama        = Column(String(64),   nullable=False)
    
    @classmethod
    def get_periode(cls, id):
        return DBSession.query(extract('month',cls.tanggal).label('periode'))\
                .filter(cls.id==id,)\
                .group_by(extract('month',cls.tanggal)
                ).scalar() or 0
    
    @classmethod
    def get_periode2(cls, id_tbp):
        return DBSession.query(extract('month',cls.tanggal).label('periode'))\
                .filter(cls.id==id_tbp,)\
                .group_by(extract('month',cls.tanggal)
                ).scalar() or 0
                
class ARTargetItem(NamaModel, Base):
    __tablename__ = 'ar_target_item'
    __table_args__ = {'extend_existing':True, 'schema' : 'apbd',}

    units         = relationship("Unit",        backref=backref("ar_target_items"))
    kegiatan_subs = relationship("KegiatanSub", backref=backref("ar_target_items"))
    rekenings     = relationship("Rekening",    backref=backref("ar_target_items"))

    unit_id         = Column(Integer, ForeignKey("admin.units.id"),        nullable=False)
    kegiatan_sub_id = Column(Integer, ForeignKey("apbd.kegiatan_subs.id"), nullable=False)
    rekening_id     = Column(Integer, ForeignKey("admin.rekenings.id"),    nullable=False)
    tahun           = Column(Integer)
    amount_01       = Column(BigInteger)
    amount_02       = Column(BigInteger)
    amount_03       = Column(BigInteger)
    amount_04       = Column(BigInteger)
    amount_05       = Column(BigInteger)
    amount_06       = Column(BigInteger)
    amount_07       = Column(BigInteger)
    amount_08       = Column(BigInteger)
    amount_09       = Column(BigInteger)
    amount_10       = Column(BigInteger)
    amount_11       = Column(BigInteger)
    amount_12       = Column(BigInteger)

############################################
###  JURNAL ANGGARAN    ###
###  KegiatanItem  ###
############################################        
class JurnalAnggaran(DefaultModel, Base):
    __tablename__   ='jurnal_anggaran'
    __table_args__  = {'extend_existing':True,'schema' :'apbd'}

    kegiatan_subs   = relationship("KegiatanSub", backref=backref("jurnal_anggarans"))    
    rekenings       = relationship("Rekening",    backref=backref("jurnal_anggarans"))

    kegiatan_sub_id = Column(BigInteger, ForeignKey("apbd.kegiatan_subs.id"), nullable=False)
    rekening_id     = Column(Integer ,   ForeignKey("admin.rekenings.id"),    nullable=False)    
    amount          = Column(BigInteger, nullable=False, default=0)

class Jurnal(NamaModel, Base):
    __tablename__   = 'jurnals'
    __table_args__  = {'extend_existing':True, 'schema' : 'apbd',}
                    
    units           = relationship("Unit",  backref=backref("jurnals")) 
    unit_id         = Column(Integer,       ForeignKey("admin.units.id"), nullable=False)  
    tahun_id        = Column(BigInteger,    ForeignKey("apbd.tahuns.id"), nullable=False)
    kode            = Column(String(32),    nullable=False)    
    nama            = Column(String(128),   nullable=False)
    jv_type         = Column(SmallInteger,  nullable=False, default=0)
    tanggal         = Column(Date) 
    tgl_transaksi   = Column(Date)
    periode         = Column(Integer,       nullable=False)
    source          = Column(String(10),    nullable=False)
    source_no       = Column(String(30),    nullable=False)
    tgl_source      = Column(Date)           
    posted          = Column(SmallInteger,  nullable=False)
    posted_uid      = Column(Integer) 
    posted_date     = Column(Date) 
    notes           = Column(String(225),   nullable=False)
    is_skpd         = Column(SmallInteger,  nullable=False)
    disabled        = Column(SmallInteger,  nullable=False, default=0)

    @classmethod
    def get_norut(cls, tahun, unit_id):
        return DBSession.query(func.count(cls.id).label('no_urut'))\
               .filter(cls.tahun_id==tahun,
                       cls.unit_id ==unit_id
               ).scalar() or 0
               
    @classmethod
    def get_tipe(cls, jv_type):
        return DBSession.query(case([(cls.jv_type==1,"JT"),(cls.jv_type==2,"JK"),
                          (cls.jv_type==3,"JU"),(cls.jv_type==4,"KR"),
                          (cls.jv_type==5,"CL"),(cls.jv_type==6,"LO")], else_="").label('jv_type'))\
                .filter(cls.jv_type==jv_type
                ).group_by(cls.jv_type
                ).scalar() or 0
                
class JurnalItem(DefaultModel, Base):
    __tablename__   ='jurnal_items'
    __table_args__  = {'extend_existing':True,'schema' :'apbd'}

    jurnals         = relationship("Jurnal", backref="jurnal_items")
    jurnal_id       = Column(BigInteger, ForeignKey("apbd.jurnals.id"), nullable=False)
    kegiatan_sub_id = Column(BigInteger, default=0, nullable=True) 
    rekening_id     = Column(BigInteger, default=0, nullable=True)
    sap_id          = Column(BigInteger, default=0, nullable=True)
    amount          = Column(BigInteger, default=0) 
    notes           = Column(String(225),nullable=True)

 