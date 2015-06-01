from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    SmallInteger,
    Text,
    DateTime,
    String,
    func,
    Index
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

EngineMssql = ['']
    
from ..models import Base, DefaultModel, DBSession

class KodeModel(DefaultModel):
    kode = Column(String(32))
    disabled = Column(SmallInteger, nullable=False, default=0, 
                server_default='0')
    created  = Column(DateTime, nullable=False, default=datetime.now,
                server_default='now()')
    updated  = Column(DateTime)
    create_uid  = Column(Integer, nullable=False, default=1,
                    server_default='1')
    update_uid  = Column(Integer)
    
    @classmethod
    def get_by_kode(cls,kode):
        return cls.query().filter_by(kode=kode).first()
        
    @classmethod
    def count(cls):
        return DBSession.query(func.count('*')).scalar()
    
    @classmethod
    def get_active(cls):
        return DBSession.query(cls).filter_by(disabled=0).all()
    
    
    
class UraianModel(KodeModel):
    uraian = Column(String(128))
    @classmethod
    def get_by_uraian(uraian):
        return cls.query().filter_by(uraian=uraian).first()
        
    @classmethod
    def get_nama(uraian):
        return cls.query().filter_by(uraian=uraian)


class NamaModel(KodeModel):
    nama = Column(String(128))
    @classmethod
    def get_by_nama(nama):
        return cls.query().filter_by(nama=nama).first()
        
    @classmethod
    def get_nama(nama):
        return cls.query().filter_by(nama=nama)
        
class App(Base, NamaModel):
    __tablename__  = 'apps'
    __table_args__ = {'extend_existing':True, 
                      'schema' : 'admin',}
    tahun = Column(Integer)
    
    @classmethod
    def count_active(cls):
        return DBSession.query(func.count(cls.id)).filter(cls.disabled==0).scalar()
    @classmethod
    def active_url(cls):
        return DBSession.query(cls.kode).filter(cls.disabled==0).first().kode
        
