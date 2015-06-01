from base import *
from program import Program

class Kegiatan(Base, base):
  __tablename__ ='kegiatans'
  __table_args__ = {'extend_existing':True, 
         'schema' :'apbd','autoload':True}         
  
  @classmethod
  def get_by_kode(cls,kode):
      return DBSession.query(cls).filter_by(kode=kode).first()
      
  @classmethod
  def import_data(cls):
    filenm ='kegiatan.csv'
    with open(filenm, 'rb') as csvfile:
      reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
      for row in reader:
        print row
        kode = row['kode'].strip()
        data = cls.get_by_kode(kode)
        if not data:
          data=cls()
          data.kode = kode
          data.created = datetime.now()
          data.create_uid = 1
          #data.tahun = data.created.year 
          #data.level_id = data.kode.count('.')+1
          #data.parent_id = DBSession.query(Rekening.id).filter(Rekening.kode==data.kode[:data.kode.rfind('.')]).scalar()
          data.disabled = 0
          #data.defsign = 1
          data.program_id=Program.get_by_kode(''.join([row['urusankd'].strip(),'.',row['programkd'].strip()])).id
        data.nama = row['nama'].strip()
        DBSession.add(data)
    DBSession.flush()
    DBSession.commit()

if __name__ == '__main__':
  Kegiatan.import_data()