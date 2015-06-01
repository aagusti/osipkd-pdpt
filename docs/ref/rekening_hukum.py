from base import *
from rekening import Rekening

class DasarHukum(Base, base):
  __tablename__ ='dasar_hukums'
  __table_args__ = {'extend_existing':True, 
         'schema' :'admin','autoload':True}         
  
  @classmethod
  def get_by_kode(cls,rekening_id, no_urut):
      return DBSession.query(cls).filter_by(rekening_id=rekening_id,
                                            no_urut=no_urut).first()
      
  @classmethod
  def import_data(cls):
    filenm ='rekening_hukum.csv'
    with open(filenm, 'rb') as csvfile:
      reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
      for row in reader:
        print row
        rekening_id = Rekening.get_by_kode(row['kode'].strip(),datetime.now().year).id
        no_urut = row['no_urut'].strip()
        data = cls.get_by_kode(rekening_id, no_urut)
        if not data:
          data=cls()
          data.rekening_id = rekening_id
          data.no_urut = no_urut
          #data.created = datetime.now()
          #data.create_uid = 1
          #data.tahun = data.created.year 
          #data.level_id = data.kode.count('.')+1
          #data.parent_id = DBSession.query(Rekening.id).filter(Rekening.kode==data.kode[:data.kode.rfind('.')]).scalar()
          #data.disabled = 0
          #data.defsign = 1
          #data.program_id=Program.get_by_kode(''.join([row['urusankd'].strip(),'.',row['programkd'].strip()])).id
        data.nama = row['nama'].strip()
        DBSession.add(data)
    DBSession.flush()
    DBSession.commit()

if __name__ == '__main__':
  DasarHukum.import_data()