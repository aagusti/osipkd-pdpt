from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    SmallInteger,
    Text,
    DateTime,
    Date,
    String,
    UniqueConstraint,
    ForeignKey,
    func,
    Float
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
from ..models.pemda_model import (Rekening)

class Tahun(DefaultModel, Base):
    __tablename__  = 'tahuns'
    __table_args__ = {'extend_existing':True,'schema' : 'apbd'}
    disabled    = Column(Integer, nullable=False, default=0)
    tahun       = Column(Integer)
    status_apbd = Column(SmallInteger, nullable=False, default=1) #status apbd 1 RKA
                                                           #2 DPA 3 RPKA 4 DPPA
    tgl_entry      = Column(Date)
    tgl_evaluasi   = Column(Date)
    tanggal_1      = Column(Date) #Tgl. RKA
    tanggal_2      = Column(Date) #Tgl. DPA
    tanggal_3      = Column(Date) #Tgl. RPKA
    tanggal_4      = Column(Date)  #Tgl. DPPA
    no_perda       = Column(String(50))
    tgl_perda      = Column(Date)
    no_perkdh      = Column(String(50))
    tgl_perkdh     = Column(Date)
    no_perda_rev   = Column(String(50))
    tgl_perda_rev  = Column(Date)
    no_perkdh_rev  = Column(String(50))
    tgl_perkdh_rev = Column(Date)
    no_lpj         = Column(String(50))
    tgl_lpj        = Column(Date)
    
    @classmethod
    def get_by_tahun(cls,tahun):
        return cls.query().filter_by(tahun=tahun).first()
        
class Fungsi(NamaModel, Base):
    __tablename__  = 'fungsis'
    __table_args__ = {'extend_existing':True,'schema' : 'apbd'}

class FungsiUrusan(DefaultModel, Base):
    __tablename__  = 'fungsi_urusans'
    __table_args__ = {'extend_existing':True,'schema' : 'apbd'}

    urusans   = relationship("Urusan", backref=backref('fungsi_urusans'))
    fungsis   = relationship("Fungsi", backref=backref('fungsi_urusans'))
    urusan_id = Column(Integer, ForeignKey("admin.urusans.id"))
    fungsi_id = Column(Integer, ForeignKey("apbd.fungsis.id"))
    nama      = Column(String(128))
    
class Pegawai(NamaModel, Base):
    __tablename__  = 'pegawais'
    __table_args__ = {'extend_existing':True,'schema' : 'apbd'}

class Jabatan(NamaModel, Base):
    __tablename__  = 'jabatans'
    __table_args__ = {'extend_existing':True,'schema' : 'apbd'}
        
class Pejabat(DefaultModel, Base):
    __tablename__  = 'pejabats'
    __table_args__ = {'extend_existing':True,'schema' : 'apbd'}
    unit_id    = Column(Integer, ForeignKey("admin.units.id"))
    units      = relationship("Unit", backref=backref('pejabats'))
    pegawai_id = Column(Integer, ForeignKey("apbd.pegawais.id"))
    pegawais   = relationship("Pegawai", backref=backref('pejabats'))
    jabatan_id = Column(Integer, ForeignKey("apbd.jabatans.id"))
    jabatans   = relationship("Jabatan", backref=backref('pejabats'))
    uraian     = Column(String(200))
    mulai      = Column(Date)
    selesai    = Column(Date)


"""class Tapd(NamaModel, Base):
    __tablename__  = 'tapds'
    __table_args__ = {'extend_existing':True,'schema' : 'apbd'}
    jabatans       = relationship("Jabatan", backref="tapds")
    pegawais       = relationship("Pegawai", backref="tapds")
    jabatan_id     = Column(Integer, ForeignKey("apbd.jabatans.id"))
    pegawai_id     = Column(Integer, ForeignKey("apbd.pegawais.id"))
    mulai          = Column(Date)
    selesai        = Column(Date)

    def __init__(self, data):
        NamaModel.__init__(self,data) 
        self.jabatan_id  = data['jabatan_id'] 
        self.pegawai_id  = data['pegawai_id'] 
        self.mulai       = data['mulai'] 
        self.selesai     = data['selesai'] 
     
    @classmethod
    def update(cls, data):
        data['updated'] = datetime.now()	 
        data['mulai']   = data['mulai'] and datetime.strptime(data['mulai'],'%d-%m-%Y') or None
        data['selesai'] = data['selesai'] and datetime.strptime(data['selesai'],'%d-%m-%Y') or None
        return DBSession.query(cls).filter(cls.id==data['id']).update(data)

class TapdUnit(NamaModel, Base):
    __tablename__  = 'pegawai_jabatans'
    __table_args__ = {'extend_existing':True,'schema' : 'apbd'}
    unit_id = Column(Integer, ForeignKey("apbd.pegawais.id"))
    tapd_id = Column(Integer, ForeignKey("apbd.jabatans.id"))
    mulai   = Column(Date)
    selesai = Column(Date)
    def __init__(self, data):
        NamaModel.__init__(self,data)
        self.unit_id   = data['unit_id']
        self.tapd_id   = data['tapd_id']
        self.mulai     = data['mulai']
        self.selesai   = data['selesai']
"""

class Program(NamaModel, Base):
    __tablename__  = 'programs'
    __table_args__ = {'extend_existing':True,'schema' : 'apbd'}
    sasaran    = Column(String(250))
    agenda_id  = Column(Integer)
    fungsi_id  = Column(Integer)
    urusans    = relationship("Urusan", backref="programs")
    urusan_id  = Column(Integer, ForeignKey("admin.urusans.id"))
           
class Kegiatan(NamaModel, Base):
    __tablename__  = 'kegiatans'
    __table_args__ = {'extend_existing':True,'schema' : 'apbd'}
    nama       = Column(String(256))
    programs   = relationship("Program", backref="kegiatans")
    tmt        = Column(Integer)
    locked     = Column(Integer)
    program_id = Column(Integer, ForeignKey("apbd.programs.id"))

class KegiatanSub(NamaModel, Base):
    __tablename__  = 'kegiatan_subs'
    __table_args__ = {'extend_existing':True, 'schema' : 'apbd',}

    tahun_id    = Column(BigInteger, ForeignKey("apbd.tahuns.id"),    nullable=False)
    unit_id     = Column(Integer,    ForeignKey("admin.units.id"),     nullable=False) 
    kegiatan_id = Column(BigInteger, ForeignKey("apbd.kegiatans.id"), nullable=False)

    kegiatans = relationship("Kegiatan", backref="kegiatansubs")
    units     = relationship("Unit",     backref="kegiatansubs") 
    
    no_urut  = Column(Integer, nullable=False)
    nama    = Column(String(255))
    lokasi   = Column(String(255))
    sifat    = Column(String(50))
    bagian   = Column(String(50))
    kondisi  = Column(String(255))
    waktu    = Column(String(50))
    amt_lalu = Column(BigInteger, nullable=False, default=0)
    amt_yad  = Column(BigInteger, nullable=False, default=0)

    sdana = Column(String(50))
    
    ttd1nip = Column(String(20))
    ttd2nip = Column(String(20))

    notes     = Column(String(255))
    target    = Column(String(250))
    sasaran   = Column(String(250))
    perubahan = Column(String(250))

    ppa      = Column(BigInteger, nullable=False, default=0)
    ppas     = Column(BigInteger, nullable=False, default=0)
    ppa_rev  = Column(BigInteger, nullable=False, default=0)
    ppas_rev = Column(BigInteger, nullable=False, default=0)

    volume = Column(String(100))

    tgl_bahas_1 = Column(Date)
    tgl_bahas_2 = Column(Date)
    tgl_bahas_3 = Column(Date)
    tgl_bahas_4 = Column(Date)
    
    catatan_1 = Column(String(255))
    catatan_2 = Column(String(255))
    catatan_3 = Column(String(255))
    catatan_4 = Column(String(255))
    pending   = Column(SmallInteger, nullable=False, default=0)
    
    tahunke = Column(SmallInteger, nullable=False , default=0)
	
    h0yl = Column(BigInteger, nullable=False, default=0)
    p0yl = Column(BigInteger, nullable=False, default=0)
    r0yl = Column(BigInteger, nullable=False, default=0)
	
    h1yl = Column(BigInteger, nullable=False, default=0)
    p1yl = Column(BigInteger, nullable=False, default=0)
    r1yl = Column(BigInteger, nullable=False, default=0)
	
    h2yl = Column(BigInteger, nullable=False, default=0)
    p2yl = Column(BigInteger, nullable=False, default=0)
    r2yl = Column(BigInteger, nullable=False, default=0)
	
    disabled = Column(SmallInteger, nullable=False, default=0)
    UniqueConstraint('unit_id', 'tahun_id', 'kegiatan_id' , 'no_urut',  
                name = 'kegiatan_sub_ukey')
    @classmethod
    def max_no_urut(cls,tahun_id,unit_id,kegiatan_id):
          return DBSession.query(func.max(cls.no_urut).label('m')).filter(
                   cls.tahun_id   == tahun_id,
                   cls.unit_id    == unit_id,
                   cls.kegiatan_id == kegiatan_id).scalar() or 0

############################################
###    INDIKATOR KEGIATAN    ###
###  KegiatanIndikator  ###
############################################   
class KegiatanIndikator(NamaModel, Base):
    __tablename__  ='kegiatan_indikators'
    __table_args__ = {'extend_existing':True,'schema' :'apbd'}

    kegiatan_sub_id = Column(BigInteger, ForeignKey("apbd.kegiatan_subs.id"), nullable=False)
    tipe           = Column(SmallInteger, nullable=False)
    no_urut        = Column(SmallInteger, nullable=False)

    tolok_ukur_1   = Column(String(255), nullable=False)
    volume_1       = Column(BigInteger,  nullable=False)
    satuan_1       = Column(String(255), nullable=False)

    tolok_ukur_2   = Column(String(255), nullable=False)
    volume_2       = Column(BigInteger,  nullable=False)
    satuan_2       = Column(String(255), nullable=False)

    tolok_ukur_3   = Column(String(255), nullable=False)
    volume_3       = Column(BigInteger,  nullable=False)
    satuan_3       = Column(String(255), nullable=False)

    tolok_ukur_4   = Column(String(255), nullable=False)
    volume_4       = Column(BigInteger,  nullable=False)
    satuan_4       = Column(String(255), nullable=False)

    @classmethod
    def max_no_urut(cls,kegiatan_sub_id):
          return DBSession.query(func.max(cls.no_urut).label('m')).filter(
                   cls.kegiatan_sub_id== kegiatan_sub_id).scalar() or 0
                   
                   
############################################
###  ITEM KEGIATAN    ###
###  KegiatanItem  ###
############################################        
class KegiatanItem(NamaModel, Base):
    __tablename__   ='kegiatan_items'
    __table_args__  = {'extend_existing':True,'schema' :'apbd'}

    kegiatan_subs   = relationship("KegiatanSub", backref="kegiatan_items")    
    rekenings       = relationship("Rekening",    backref="kegiatan_items")

    kegiatan_sub_id = Column(BigInteger, ForeignKey("apbd.kegiatan_subs.id"), nullable=False)
    rekening_id     = Column(Integer ,   ForeignKey("admin.rekenings.id"),     nullable=False)    
    kode            = Column(String(32))
    nama            = Column(String(255), nullable=False)
    no_urut         = Column(Integer , nullable=False)
    header_id       = Column(BigInteger , nullable=True)

    vol_1_1 = Column(Float, nullable=False, default=1)
    sat_1_1 = Column(String(25))
    vol_1_2 = Column(Float, nullable=False, default=1)
    sat_1_2 = Column(String(25))
    hsat_1  = Column(BigInteger, nullable=False, default=0)

    vol_2_1 = Column(Float, nullable=False, default=1)
    sat_2_1 = Column(String(25))
    vol_2_2 = Column(Float, nullable=False, default=1)
    sat_2_2 = Column(String(25))
    hsat_2  = Column(BigInteger, nullable=False, default=0)

    vol_3_1 = Column(Float, nullable=False, default=1)
    sat_3_1 = Column(String(25))
    vol_3_2 = Column(Float, nullable=False, default=1)
    sat_3_2 = Column(String(25))
    hsat_3 = Column(BigInteger,  nullable=False, default=0)

    vol_4_1 = Column(Float, nullable=False, default=1)
    sat_4_1 = Column(String(25))
    vol_4_2 = Column(Float, nullable=False, default=1)
    sat_4_2 = Column(String(25))
    hsat_4 = Column(BigInteger, nullable=False, default=0)

    pelaksana = Column(String(25))
    mulai     = Column(Date)
    selesai   = Column(Date)

    bln01 = Column(BigInteger, nullable=False, default=0)
    bln02 = Column(BigInteger, nullable=False, default=0)
    bln03 = Column(BigInteger, nullable=False, default=0)
    bln04 = Column(BigInteger, nullable=False, default=0)
    bln05 = Column(BigInteger, nullable=False, default=0)
    bln06 = Column(BigInteger, nullable=False, default=0)
    bln07 = Column(BigInteger, nullable=False, default=0)
    bln08 = Column(BigInteger, nullable=False, default=0)
    bln09 = Column(BigInteger, nullable=False, default=0)
    bln10 = Column(BigInteger, nullable=False, default=0)
    bln11 = Column(BigInteger, nullable=False, default=0)
    bln12 = Column(BigInteger, nullable=False, default=0)

    ssh_id = Column(BigInteger) # link ke ssh?????

    is_summary = Column(SmallInteger, nullable=False, default=0)
    is_apbd    = Column(SmallInteger, nullable=False, default=0)

    keterangan = Column(String(255))
    UniqueConstraint ('kegiatan_sub_id','rekening_id','no_urut', name='kegiatan_item_uq')
    
    @classmethod
    def max_no_urut(cls,kegiatan_sub_id,rekening_id):
          return DBSession.query(func.max(cls.no_urut).label('m')).filter(
                   cls.kegiatan_sub_id== kegiatan_sub_id,
                   cls.rekening_id    == rekening_id).scalar() or 0
