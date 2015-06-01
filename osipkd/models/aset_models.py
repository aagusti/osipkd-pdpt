import sys
from ..models import Base
from sqlalchemy import (Column, Integer, String, SmallInteger, UniqueConstraint, 
      ForeignKey, BigInteger, Date, DateTime, func)
from datetime import datetime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection

from ..models.base_model import UraianModel, DefaultModel
from ..models import DBSession   

class AsetKategori(UraianModel, Base):
    __tablename__  = 'kategoris'
    __table_args__ = {'extend_existing':True,'schema' : 'aset'}
    
    parent_id = Column(Integer, ForeignKey('aset.kategoris.id'))
    level_id  = Column(Integer)
    children  = relationship('AsetKategori',
                        cascade="all",
                        backref=backref("parent", remote_side='AsetKategori.id'),
                        collection_class=attribute_mapped_collection('uraian'),)
                        
    #parent = relationship('AsetKategori', remote_side=[id]) 
                    
    def __repr__(self):
        return "AsetKategori(uraian=%r, id=%r, parent_id=%r)" % (
                    self.uraian,
                    self.id,
                    self.parent_id
                )     
                
    @classmethod
    def get_next_level(cls,id):
        row = cls.query_id(id).first()
        return row and row.level_id+1 or 1                

class AsetKebijakan(DefaultModel, Base):
    __tablename__  = 'kebijakans'
    __table_args__ = {'extend_existing':True,'schema' : 'aset'}
    
    kategoris = relationship("AsetKategori", backref="kebijakans")
    
    kategori_id = Column(Integer, ForeignKey("aset.kategoris.id"), nullable=False)
    created     = Column(DateTime, nullable=False, default=datetime.now)
    updated     = Column(DateTime)
    create_uid  = Column(Integer,  nullable=False, default=1)
    update_uid  = Column(Integer)
    minimum     = Column(BigInteger,   nullable=False)
    tahun       = Column(Integer,      nullable=False)
    masa_guna   = Column(Integer,      nullable=False)
    disabled    = Column(SmallInteger, nullable=False, default=0)
    

class AsetPemilik(UraianModel, Base):
    __tablename__  = 'pemiliks'
    __table_args__ = {'extend_existing':True,'schema' : 'aset'}
        
class AsetKib(DefaultModel, Base):
    __tablename__  = 'kibs'
    __table_args__ = {'extend_existing':True,'schema' : 'aset'}

    unit_id        = Column(Integer, ForeignKey("admin.units.id"),    nullable=False)
    kategori_id    = Column(Integer, ForeignKey("aset.kategoris.id"), nullable=False)
    pemilik_id     = Column(SmallInteger, ForeignKey("aset.pemiliks.id"), nullable=False)
    uraian         = Column(String(255),  nullable=False)
    tahun          = Column(SmallInteger, nullable=False)
    no_register    = Column(Integer, nullable=False)
    tgl_perolehan  = Column(Date, nullable=False)
    cara_perolehan = Column(String(100))

    th_beli   = Column(Integer, nullable=False)

    asal_usul = Column(String(50), nullable=False)
    harga     = Column(BigInteger, nullable=False)
    jumlah    = Column(BigInteger, nullable=False)
    satuan    = Column(String(50))
    kondisi   = Column(String(2),  nullable=False)

    masa_manfaat = Column(SmallInteger, nullable=False, default=0)
    nilai_sisa   = Column(BigInteger,   nullable=False, default=0)

    no_sp2d = Column(String(50))
    no_id   = Column(SmallInteger)

    kib        = Column(String(1), nullable=False)
    keterangan = Column(String(255))
    
    a_luas_m2   = Column(BigInteger)
    a_alamat    = Column(String(255))
    a_hak_tanah = Column(String(20))
    a_sertifikat_tanggal = Column(Date)
    a_sertifikat_nomor   = Column(String(50))
    a_penggunaan = Column(String(50))

    b_kd_ruang = Column(SmallInteger, ForeignKey("aset.ruangs.id"))
    b_merk     = Column(String(50))
    b_type     = Column(String(50))
    b_cc       = Column(String(50))
    b_bahan    = Column(String(50))
    b_nomor_pabrik = Column(String(50))
    b_nomor_rangka = Column(String(50))
    b_nomor_mesin  = Column(String(50))
    b_nomor_polisi = Column(String(10))
    b_nomor_bpkb   = Column(String(50))
    b_ukuran   = Column(String(50))
    b_warna    = Column(String(10))
    b_thbuat   = Column(String(4))

    c_bertingkat_tidak = Column(String(20))
    c_beton_tidak = Column(String(20))
    c_luas_lantai = Column(BigInteger)
    c_lokasi      = Column(String(255))
    c_dokumen_tanggal = Column(Date)
    c_dokumen_nomor   = Column(String(50))
    c_status_tanah  = Column(String(50))
    c_kode_tanah    = Column(BigInteger)
    c_luas_bangunan = Column(BigInteger)

    d_konstruksi = Column(String(20))
    d_panjang    = Column(BigInteger)
    d_lebar      = Column(BigInteger)
    d_luas       = Column(BigInteger)
    d_lokasi     = Column(String(255))
    d_dokumen_tanggal = Column(Date)
    d_dokumen_nomor   = Column(String(50))
    d_status_tanah    = Column(String(50))
    d_kode_tanah = Column(BigInteger)

    e_judul    = Column(String(255))
    e_pencipta = Column(String(255))
    e_bahan    = Column(String(50))
    e_spek     = Column(String(50))
    e_asal     = Column(String(50))
    e_ukuran   = Column(BigInteger)
    e_jenis    = Column(String(50))

    f_bertingkat_tidak = Column(String(20))
    f_beton_tidak = Column(String(20))
    f_panjang     = Column(BigInteger)
    f_lebar       = Column(BigInteger)
    f_luas_lantai = Column(BigInteger)
    f_lokasi      = Column(String(255))
    f_dokumen_tanggal  = Column(Date)
    f_dokumen_nomor = Column(String(50))
    f_status_tanah  = Column(String(50))
    f_kode_tanah    = Column(BigInteger)
    f_luas_bangunan = Column(BigInteger)

    UniqueConstraint('unit_id' , 'kategori_id' , 'no_register', name='kibs_unit_id_kategori_id_no_register_key')
    units    = relationship("Unit",         backref="kibunit")
    kats     = relationship("AsetKategori", backref="kibkat")
    pemiliks = relationship("AsetPemilik",  backref="kibpemilik")
    ruangs   = relationship("AsetRuang",    backref="kibruang")
    
    @classmethod
    def get_no_register(cls, a, b, c):
        return DBSession.query(func.max(cls.no_register).label('no_register'))\
                .filter(cls.tahun==a,
                        cls.unit_id==b,
                        cls.kategori_id==c,
                ).scalar() or 0
                      
    
class AsetDel(UraianModel, Base):
    __tablename__  = 'kib_deletes'
    __table_args__ = {'extend_existing':True,'schema' : 'aset'}
    
    units    = relationship("Unit", backref="kib_deletes")
    
    unit_id  = Column(Integer, ForeignKey("admin.units.id"))
    kode     = Column(String(32))
    uraian   = Column(String(128))
    alasan   = Column(String(200))
    tanggal  = Column(Date)
    disabled = Column(SmallInteger, nullable=False, default=0)
    
    UniqueConstraint('unit_id' , 'kode', name='kib_deletes_unit_id_kode_key')
    
    @classmethod
    def get_norut(cls, id):
        return DBSession.query(func.count(cls.id).label('no_urut'))\
               .scalar() or 0 
               
class AsetDelItem(DefaultModel, Base):
    __tablename__  = 'kib_delete_items'
    __table_args__ = {'extend_existing':True,'schema' : 'aset'}
    
    kibs      = relationship("AsetKib", backref="delitems")
    kibdels   = relationship("AsetDel", backref="delitems")
    
    kib_id    = Column(BigInteger, ForeignKey("aset.kibs.id"), nullable=False, unique=True)
    delete_id = Column(BigInteger, ForeignKey("aset.kib_deletes.id"))
    alasan    = Column(String(200))
    tanggal   = Column(Date, nullable=False)

class AsetRuang(UraianModel, Base):
    __tablename__  = 'ruangs'
    __table_args__ = {'extend_existing':True,'schema' : 'aset'}
    
    units    = relationship("Unit",      backref="ruangs")
    ruangans = relationship("AsetRuang", backref=backref('ruang', remote_side='AsetRuang.id'))
    unit_id  = Column(Integer, ForeignKey("admin.units.id"), nullable=False)
    ruang_id = Column(Integer, ForeignKey('aset.ruangs.id'))
    
    UniqueConstraint('unit_id' , 'ruang_id', name='ruang_unit_ukey')

class AsetHistKondisi(UraianModel, Base):
    __tablename__  = 'hist_kondisi'
    __table_args__ = {'extend_existing':True,'schema' : 'aset'}
    
    kib_id        = Column(BigInteger, ForeignKey("aset.kibs.id"), nullable=False, unique=True)
    tanggal       = Column(Date,      nullable=False)
    kondisi_awal  = Column(String(2), nullable=False)
    kondisi_akhir = Column(String(2), nullable=False)
    biaya         = Column(BigInteger,   nullable=False, default=0)
    is_kapitasi   = Column(SmallInteger, nullable=False, default=0)
    
class AsetHistPemilik(UraianModel, Base):
    __tablename__  = 'hist_pemilik'
    __table_args__ = {'extend_existing':True,'schema' : 'aset'}
    
    kib_id            = Column(BigInteger,   ForeignKey("aset.kibs.id"),     nullable=False, unique=True)
    pemilik_awal_id   = Column(SmallInteger, ForeignKey("aset.pemiliks.id"), nullable=False)
    pemilik_akhir_id  = Column(SmallInteger, ForeignKey("aset.pemiliks.id"), nullable=False)
    tanggal           = Column(Date, nullable=False)

class AsetHistSusut(UraianModel, Base):
    __tablename__  = 'hist_susut'
    __table_args__ = {'extend_existing':True,'schema' : 'aset'}
    
    kib_id        = Column(BigInteger,   ForeignKey("aset.kibs.id"), nullable=False, unique=True)
    tanggal       = Column(Date,         nullable=False)
    nilai_susut   = Column(BigInteger,   nullable=False, default=0)
    is_kapitasi   = Column(SmallInteger, nullable=False, default=0)
    