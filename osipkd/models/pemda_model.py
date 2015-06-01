from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    SmallInteger,
    Text,
    DateTime,
    String,
    ForeignKey,
    text,
    UniqueConstraint,
    
    )
    
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,backref    )
from ..models import Base, DBSession, CommonModel, DefaultModel

from base_model import NamaModel

def unitfinder(userid, request):
    if userid and hasattr(request, 'user') and request.user:
        units = [('%s,%s' % (u.kode,u.sub_unit)) for u in request.user.units]
        return units
    return []
    
STATUS_APBD = ((1, "RKA"),
               (2, "DPA"),
               (3, "PRKA"),
               (4, "DPPA"))

JENIS_BELANJA = {"0":"Pilih",
                 "1":"UP",
                 "2":"TU",
                 "3":"GU",
                 "4":"LS",                 
                }            
JENIS_INDIKATOR = {"0":"Pilih",
                 "1":"Capaian Program",
                 "2":"Masukan",
                 "3":"Keluaran",
                 "4":"Hasil",                 
                }            
TRIWULAN        = {"0":"Pilih",
                 "1":"Triwulan I",
                 "2":"Triwulan II",
                 "3":"Triwulan III",
                 "4":"Triwulan IV",                 
                }  
                
class Urusan(Base, NamaModel):
    __tablename__  = 'urusans'
    __table_args__ = {'extend_existing':True, 
                      'schema' : 'admin',}

class Unit(Base, NamaModel):
    __tablename__  = 'units'
    __table_args__ = {'extend_existing':True, 
                      'schema' : 'admin',}
                       
    #urusan_id = Column(Integer, ForeignKey('admin.urusans.id'))
    kategori  = Column(String(32))
    alamat    = Column(String(255))
    singkat   = Column(String(32))
    level_id  = Column(SmallInteger)
    header_id = Column(SmallInteger)
    urusan_id = Column(Integer, ForeignKey('admin.urusans.id'))
    urusans   = relationship("Urusan", backref="units")

class UserUnit(Base, CommonModel):
    __tablename__  = 'user_units'
    __table_args__ = {'extend_existing':True, 
                      'schema' : 'admin',}
     
    units    = relationship("Unit", backref="users")
    users    = relationship("User", backref="units")                  
    user_id  = Column(Integer, ForeignKey('users.id'),       primary_key=True)
    unit_id  = Column(Integer, ForeignKey('admin.units.id'), primary_key=True)
    sub_unit = Column(SmallInteger, nullable=False)
    
    @classmethod
    def query_user_id(cls, user_id):
        return DBSession.query(cls).filter_by(user_id = user_id)

    @classmethod
    def ids(cls, user_id):
        r = ()
        units = DBSession.query(cls.unit_id,cls.sub_unit, Unit.kode
                     ).join(Unit).filter(cls.unit_id==Unit.id,
                            cls.user_id==user_id).all() 
        for unit in units:
            if unit.sub_unit:
                rows = DBSession.query(Unit.id).filter(Unit.kode.ilike('%s%%' % unit.kode)).all()
            else:
                rows = DBSession.query(Unit.id).filter(Unit.kode==unit.kode).all()
            for i in range(len(rows)):
                print '***', rows[i]
                r = r + (rows[i])
        return r
        
    @classmethod
    def unit_granted(cls, user_id, unit_id):
        
        print 'A*******',  user_id, unit_id
        units = DBSession.query(cls.unit_id,cls.sub_unit, Unit.kode
                     ).join(Unit).filter(cls.unit_id==Unit.id,
                            cls.user_id==user_id).all() 
        for unit in units:
            if unit.sub_unit:
                rows = DBSession.query(Unit.id).filter(Unit.kode.ilike('%s%%' % unit.kode)).all()
            else:
                rows = DBSession.query(Unit.id).filter(Unit.kode==unit.kode).all()
            for i in range(len(rows)):
                if int(rows[i][0])  == int(unit_id):
                    return True
        return False
        
    @classmethod
    def get_filtered(cls, request):
        filter = "'%s' LIKE admin.units.kode||'%%'" % request.session['unit_kd']
        q1 = DBSession.query(Unit.kode, UserUnit.sub_unit).join(UserUnit).\
                       filter(UserUnit.user_id==request.user.id,
                              UserUnit.unit_id==Unit.id,
                              text(filter))
        return q1.first()
        
class Rekening(NamaModel, Base):
    __tablename__ = 'rekenings'
    __table_args__= (UniqueConstraint('kode', 'tahun', name='rekening_uq'),
                      {'extend_existing':True, 
                      'schema' : 'admin',})
                      
    tahun     = Column(Integer)
    nama      = Column(String(256))
    level_id  = Column(SmallInteger, default=1)
    parent_id = Column(BigInteger,   ForeignKey('admin.rekenings.id'))
    disabled  = Column(SmallInteger, default=0)
    defsign   = Column(SmallInteger, default=1)
    children  = relationship("Rekening", backref=backref('parent', remote_side='Rekening.id'))
    
    @classmethod
    def get_next_level(cls,id):
        return cls.query_id(id).first().level_id+1
        
class Sap(NamaModel, Base):
    __tablename__ = 'saps'
    __table_args__= (UniqueConstraint('kode', 'tahun', name='sap_uq'),
                      {'extend_existing':True, 
                      'schema' : 'admin',})
                      
    tahun     = Column(Integer)
    nama      = Column(String(256))
    level_id  = Column(SmallInteger, default=1)
    parent_id = Column(BigInteger,   ForeignKey('admin.saps.id'))
    disabled  = Column(SmallInteger, default=0)
    defsign   = Column(SmallInteger, default=1)
    children  = relationship("Sap", backref=backref('parent', remote_side='Sap.id'))
    
    @classmethod
    def get_next_level(cls,id):
        return cls.query_id(id).first().level_id+1

class RekeningSap(DefaultModel, Base):
    __tablename__    = 'rekenings_saps'
    __table_args__   = {'extend_existing':True,'schema' : 'admin'}
                     
    rekening_id      = Column(Integer, ForeignKey("admin.rekenings.id"))        
    db_lo_sap_id     = Column(Integer, nullable=True)
    kr_lo_sap_id     = Column(Integer, nullable=True)
    db_lra_sap_id    = Column(Integer, nullable=True)
    kr_lra_sap_id    = Column(Integer, nullable=True)
    neraca_sap_id    = Column(Integer, nullable=True)
    pph_id           = Column(String(64))
    
    rekenings   = relationship("Rekening", backref="rekenings_saps")
        
class DasarHukum(DefaultModel, Base):
    __tablename__  = 'dasar_hukums'
    __table_args__ = {'extend_existing':True,'schema' : 'admin'}
    
    rekenings   = relationship("Rekening", backref="dasar_hukums")
    rekening_id = Column(Integer, ForeignKey("admin.rekenings.id"))   
    no_urut     = Column(Integer)     
    nama        = Column(String(256))