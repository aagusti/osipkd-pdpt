from base import *
from unit import Unit
from kegiatan import Kegiatan

class KegiatanSub(Base, base):
  __tablename__ ='kegiatan_subs'
  __table_args__ = {'extend_existing':True, 
         'schema' :'apbd','autoload':True}         
  
  @classmethod
  def get_by_kode(cls, tahun, kegiatan_id, unit_id, no_urut):
      return DBSession.query(cls).filter_by(tahun_id=tahun,
                                            kegiatan_id=kegiatan_id,
                                            unit_id=unit_id,
                                            no_urut=no_urut).first()
      
  @classmethod
  def import_data(cls):
    filenm ='kegiatan_sub.csv'
    with open(filenm, 'rb') as csvfile:
      reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
      i = 0
      for row in reader:
        i += 1
        if i/100 ==i/100.0:
          print i
        #print row
        tahun = row['tahun'].strip()
        kegiatan_id = Kegiatan.get_by_kode(row['kegiatan'].strip()).id
        unit_id = Unit.get_by_kode(row['unit'].strip()).id
        no_urut = row['no_urut'].strip()
        data = cls.get_by_kode(tahun, kegiatan_id, unit_id, no_urut)
        if not data:
          data=cls()
          data.kegiatan_id = kegiatan_id
          data.unit_id = unit_id
          data.no_urut = no_urut
          data.created = datetime.now()
          data.create_uid = 1
          data.tahun_id = row['tahun'] 
          #data.level_id = data.kode.count('.')+1
          #data.parent_id = DBSession.query(Rekening.id).filter(Rekening.kode==data.kode[:data.kode.rfind('.')]).scalar()
          data.disabled = 0
          #data.defsign = 1
          #data.program_id=Program.get_by_kode(''.join([row['urusankd'].strip(),'.',row['programkd'].strip()])).id
        data.kode = row['kegiatan']
        data.nama = row['nama'].strip()
        data.amt_lalu = 0
        data.amt_yad  = 0
        data.ppa      = 0
        data.ppas     = 0
        data.ppa_rev  = 0
        data.ppas_rev = 0
        data.pending  = 0
        data.tahunke  = 0
        data.h0yl     = 0
        data.p0yl     = 0
        data.r0yl     = 0
        data.h1yl     = 0
        data.p1yl     = 0
        data.r1yl     = 0
        data.h2yl     = 0
        data.p2yl     = 0
        data.r2yl     = 0

        DBSession.add(data)
    DBSession.flush()
    DBSession.commit()

if __name__ == '__main__':
  KegiatanSub.import_data()