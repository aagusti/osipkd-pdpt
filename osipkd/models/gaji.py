import sys
#from model_base import *
from sqlalchemy import (
    Column, Integer, BigInteger, SmallInteger, String,
    DateTime,
    UniqueConstraint, ForeignKey
    )
from sqlalchemy.orm import (
    relationship
    )

from ..models import DefaultModel, Base, CommonModel
class GajiPegawai(Base, CommonModel):
    __tablename__  = 'gaji_pegawai'
    __table_args__ = (UniqueConstraint('tahun', 'bulan','jenis','nip', name='gaji_pegawai_uq1'),
                      {'extend_existing':True,'schema' : 'gaji'})
    id               = Column(BigInteger, primary_key=True)
    tahun            = Column(String(4),)
    bulan            = Column(String(2),)
    jenis            = Column(SmallInteger,)
    nip              = Column(String(18),)    
    urut             = Column(SmallInteger, default=0)    
    unitkd           = Column(String(24))
    sub              = Column(SmallInteger)    
    nama             = Column(String(40))   
    tgl_lahir        = Column(DateTime)    
    tmp_lahir        = Column(String(40))    
    jns_kelamin      = Column(String(1) )    
    bank             = Column(String(2) )    
    rekening         = Column(String(25))    
    npwp             = Column(String(25))    
    no_pegawai       = Column(String(5))    
    nojjp            = Column(String(12))    
    alamat           = Column(String(100))   
    namasi           = Column(String(40))  
    sts_pegawaikd    = Column(String(1))   
    tmt_pegawai      = Column(DateTime)   
    sts_kwn          = Column(String(1))     
    sts_sipil        = Column(String(6))   
    agama            = Column(String(15))     
    jml_si           = Column(BigInteger)    
    jml_anak         = Column(BigInteger)    
    golongankd       = Column(String(5))  
    tmt_golongan     = Column(DateTime)   
    masakerja        = Column(BigInteger)    
    jbt_fungsikd     = Column(String(5)) 
    jbt_strukturkd   = Column(String(5))
    tmt_jabatan      = Column(DateTime)
    tunj_jab_fungsi  = Column(BigInteger) 
    tunj_jab_struktur= Column(BigInteger) 
    gaji_pokok       = Column(BigInteger)
    tmt_gaji_pokok   = Column(DateTime)
    tunj_istri       = Column(BigInteger) 
    tunj_anak        = Column(BigInteger) 
    tunj_beras       = Column(BigInteger) 
    gurukd           = Column(String(2))
    operator         = Column(String(20)) 
    tgl_ubah         = Column(DateTime)
    tunj_kerja       = Column(BigInteger)
    tdtkd            = Column(String(1))
    pend_terakhir    = Column(String(100))
    pend_jurusan     = Column(String(100)) 
    v_jab_struktur   = Column(String(75)) 
    pot_iwp          = Column(BigInteger) 
    pot_taperum      = Column(BigInteger) 
    pot_sewa_rumah   = Column(BigInteger) 
    pot_pangan       = Column(BigInteger) 
    pot_korpri       = Column(BigInteger) 
    pot_gaji_lebih   = Column(BigInteger) 
    pot_hutang       = Column(BigInteger) 
    pembulatan       = Column(BigInteger) 
    pph              = Column(BigInteger) 
    tunj_umum        = Column(BigInteger) 
    tunj_umum_tamb   = Column(BigInteger) 
    tunj_otsus       = Column(BigInteger) 
    tunj_dt          = Column(BigInteger) 
    tunj_askes       = Column(BigInteger) 
    tunj_penghasilan = Column(BigInteger) 
    biaya_jabatan    = Column(BigInteger) 
    biaya_pensiun    = Column(BigInteger) 
    persen_gaji      = Column(BigInteger) 
    isttu            = Column(SmallInteger)
    aktif_kd         = Column(Integer)
    ptkp             = Column(Integer)
    aktif_tgl        = Column(DateTime)
    tgl_gaji         = Column(DateTime)
    tmt_fungsi       = Column(DateTime)
    penerima_udwudt  = Column(String(50)) 
    tglbyr_udwudt    = Column(DateTime)
    gaji_kotor       = Column(BigInteger)
    potongan         = Column(BigInteger)
    gaji_bersih      = Column(BigInteger)
    

    @classmethod
    def get_by_nip(cls, nip):
        return DBSession.query(cls).filter(
                    cls.nip  == nip
               )
               
    @classmethod           
    def get_by_thn_bln(cls, thn_bln):
        return DBSession.query(cls).filter(
                    cls.tahun       == thn,
                    cls.bulan       == bln
               )       
               
    @classmethod           
    def get_by_nip_thn_bln(cls, nip, thn, bln):
        return DBSession.query(cls).filter(
                    cls.nip         == nip,
                    cls.tahun       == thn,
                    cls.bulan       == bln,
                    
               )       

    @classmethod
    def get_row(cls, ses):
        return DBSession.query(gajiPegawaiModel.tahun, 
                      gajiPegawaiModel.bulan,
                      gajiPegawaiModel.jenis,
                      gajiPegawaiModel.nip,
                      gajiPegawaiModel.nama, 
                      gajiPegawaiModel.gaji_kotor,
                      gajiPegawaiModel.potongan,
                      gajiPegawaiModel.gaji_bersih,
                      ).filter(
                      gajiPegawaiModel.tahun == ses['tahun'],
                      gajiPegawaiModel.bulan == ses['bulan'],
                      gajiPegawaiModel.unitkd == ses['unit_kd'],
            )
 
class GajiPotongan(Base, DefaultModel):
    __tablename__  = 'gaji_potongan'
    __table_args__ = {'extend_existing':True, 
                      'schema' : 'gaji',}
                     
    id               = Column(BigInteger, ForeignKey('gaji.gaji_pegawai.id'), primary_key=True)    
    amount_01       = Column(BigInteger, default=0)
    amount_02       = Column(BigInteger, default=0)
    amount_03       = Column(BigInteger, default=0)
    amount_04       = Column(BigInteger, default=0)
    amount_05       = Column(BigInteger, default=0)
    amount_06       = Column(BigInteger, default=0)
    amount_07       = Column(BigInteger, default=0)
    amount_08       = Column(BigInteger, default=0)
    amount_09       = Column(BigInteger, default=0)
    amount_10       = Column(BigInteger, default=0)
    amount_11       = Column(BigInteger, default=0)
    amount_12       = Column(BigInteger, default=0)
    gajipegawais    = relationship("GajiPegawai", backref="gajipotongans")
    @classmethod
    def get_row(cls, ses):
        return DBSession.query(GajiPotongan.id, 
                      GajiPegawai.nip,
                      GajiPegawai.nama, 
                      GajiPegawai.rekening, 
                      GajiPegawai.gaji_bersih,
                      GajiPotongan.amount_01,
                      GajiPotongan.amount_02,
                      GajiPotongan.amount_03,
                      GajiPotongan.amount_04,
                      GajiPotongan.amount_05,
                      GajiPotongan.amount_06,
                      GajiPotongan.amount_07,
                      GajiPotongan.amount_08,
                      GajiPotongan.amount_09,
                      GajiPotongan.amount_10,
                      GajiPotongan.amount_11,
                      GajiPotongan.amount_12,
                      ).filter(
                      gajiPegawaiModel.tahun == ses['tahun'],
                      gajiPegawaiModel.bulan == ses['bulan'],
                      gajiPegawaiModel.unitkd == ses['unit_kd'],
            )
            