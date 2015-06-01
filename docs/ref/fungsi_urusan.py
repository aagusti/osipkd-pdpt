from base import *
from urusan import Urusan
from fungsi import Fungsi

class FungsiUrusan(Base, base):
  __tablename__ ='fungsi_urusans'
  __table_args__ = {'extend_existing':True, 
         'schema' :'apbd','autoload':True}         
  
  @classmethod
  def get_by_kode(cls,fungsi_id,urusan_id):
      return DBSession.query(cls).filter_by(fungsi_id=fungsi_id, urusan_id=urusan_id).first()
  @classmethod
  def import_data(cls):
    filenm ='fungsi_urusan.csv'
    with open(filenm, 'rb') as csvfile:
      reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
      for row in reader:
        print row
        fungsi_id = Fungsi.get_by_kode(row['fungsi']).id
        urusan_id = Urusan.get_by_kode(row['urusan']).id
        
        data = cls.get_by_kode(fungsi_id,urusan_id)
        if not data:
          data=cls()
          data.created = datetime.now()
          data.create_uid = 1
          data.fungsi_id = fungsi_id 
          data.urusan_id = urusan_id
        data.nama = row['nama'].strip()
        DBSession.add(data)
    DBSession.flush()
    DBSession.commit()

if __name__ == '__main__':
  FungsiUrusan.import_data()