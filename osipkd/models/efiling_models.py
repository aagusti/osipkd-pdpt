import sys
from ..models import Base
from sqlalchemy import (Column, Integer, String, SmallInteger, UniqueConstraint, 
      ForeignKey, BigInteger, Date, DateTime, func)
from datetime import datetime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection

from ..models.base_model import NamaModel, DefaultModel
from ..models import DBSession   
class FilingKategori(NamaModel, Base):
    __tablename__ = 'filing_kategoris'
    __table_args__ = {'extend_existing':True,'schema' : 'efiling'}
    parent_id = Column(Integer, ForeignKey('efiling.filing_kategoris.id'))
    level_id = Column(Integer)
    children = relationship('FilingKategori',
                        cascade="all",
                        backref=backref("parent", remote_side='FilingKategori.id'),
                        collection_class=attribute_mapped_collection('nama'),)
                    
    def __repr__(self):
        return "FilingKategori(nama=%r, id=%r, parent_id=%r)" % (
                    self.nama,
                    self.id,
                    self.parent_id
                )      
    @classmethod
    def get_next_level(cls,id):
        row = cls.query_id(id).first()
        return row and row.level_id+1 or 1                

class FilingLokasi(NamaModel, Base):
    __tablename__ = 'filing_lokasis'
    __table_args__ = {'extend_existing':True,'schema' : 'efiling'}
    parent_id = Column(Integer, ForeignKey('efiling.filing_lokasis.id'))
    level_id = Column(Integer)
    children = relationship('FilingLokasi',
                        cascade="all",
                        backref=backref("parent", remote_side='FilingLokasi.id'),
                        collection_class=attribute_mapped_collection('nama'),)
                    
    def __repr__(self):
        return "FilingLokasi(nama=%r, id=%r, parent_id=%r)" % (
                    self.nama,
                    self.id,
                    self.parent_id
                )      
    @classmethod
    def get_next_level(cls,id):
        row = cls.query_id(id).first()
        return row and row.level_id+1 or 1  
        
class Filing(DefaultModel, Base):
    __tablename__ = 'filings'
    __table_args__ = {'extend_existing':True,'schema' : 'efiling'}
    kategoris = relationship("FilingKategori", backref="filing")
    lokasis = relationship("FilingLokasi", backref="filing")
    kategori_id = Column(Integer, ForeignKey("efiling.filing_kategoris.id"), nullable=False)
    lokasi_id = Column(Integer, ForeignKey("efiling.filing_lokasis.id"), nullable=False)
    disabled = Column(SmallInteger, nullable=False, default=0)
    created  = Column(DateTime, nullable=False, default=datetime.now)
    updated  = Column(DateTime)
    create_uid  = Column(Integer, nullable=False, default=1)
    update_uid  = Column(Integer)
    nama        = Column(String(256),nullable=False)
    tag         = Column(String(256),nullable=False)

class FilingFile(DefaultModel, Base):
    __tablename__ = 'filing_files'
    __table_args__ = {'extend_existing':True,'schema' : 'efiling'}
    filing    = relationship("Filing", backref="files")
    filing_id = Column(Integer, ForeignKey("efiling.filings.id"), nullable=False)
    nama        = Column(String(256),nullable=False)
    path        = Column(String(256),nullable=False)
    
    