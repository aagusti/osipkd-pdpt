from base import *
from unit import Unit
from kegiatan import Kegiatan
from rekening import Rekening
from kegiatan_sub import KegiatanSub

class KegiatanItem(Base, base):
  __tablename__ ='kegiatan_items'
  __table_args__ = {'extend_existing':True, 
         'schema' :'apbd','autoload':True}         
  
  @classmethod
  def get_by_kode(cls, kegiatan_sub_id, rekening_id, no_urut):
      return DBSession.query(cls).filter_by(
                        kegiatan_sub_id=kegiatan_sub_id,
                        rekening_id=rekening_id,
                        no_urut=no_urut).first()
      
  @classmethod
  def import_data(cls):
    filenm ='kegiatan_item.csv'
    with open(filenm, 'rb') as csvfile:
      reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
      i = 0
      for row in reader:
        i += 1
        if i<48000:
            continue
        if i/100 == i/100.0:
          print i
        if i/1000 == i/1000.0:
          DBSession.commit()
          print 'Commit %s' % i
        tahun = row['tahun'].strip()
        kegiatan_id = Kegiatan.get_by_kode(row['kegiatan'].strip()).id
        unit_id = Unit.get_by_kode(row['unit'].strip()).id
        no_urut = row['no_urut'].strip()
        tahun = row['tahun']
        kegiatan_sub_id = KegiatanSub.get_by_kode(tahun,kegiatan_id, unit_id, no_urut).id
        rekening_id= Rekening.get_by_kode(row['rekening'].strip(),datetime.now().year).id
        no_urut2 = row['no_urut2'].strip()
        data = cls.get_by_kode(kegiatan_sub_id, rekening_id, no_urut2)
        if not data:
          data=cls()
          data.kegiatan_sub_id = kegiatan_sub_id
          data.rekening_id     = rekening_id
          data.no_urut         = row['no_urut2']
          data.created = datetime.now()
          data.create_uid = 1
          data.disabled = 0
          
        data.kode            = row['kode'][:32] or None
        data.vol_1_1         = row['vol_1_1'].replace(',','.') or 0
        data.sat_1_1         = row['sat_1_1'] or None
        data.vol_1_2         = row['vol_1_2'].replace(',','.') or 0
        data.sat_1_2         = row['sat_1_2'] or None
        data.hsat_1          = row['hsat_1'] and int(float(row['hsat_1'].replace(',','.'))) or 0
        data.vol_2_1         = row['vol_1_1'].replace(',','.') or 0
        data.sat_2_1         = row['sat_1_1'] or None
        data.vol_2_2         = row['vol_1_2'].replace(',','.') or 0
        data.sat_2_2         = row['sat_1_2'] or None
        data.hsat_2          = row['hsat_1'] and int(float(row['hsat_1'].replace(',','.'))) or 0
        data.vol_3_1         = row['vol_3_1'].replace(',','.') or 0
        data.sat_3_1         = row['sat_3_1'] or None
        data.vol_3_2         = row['vol_3_2'].replace(',','.') or 0
        data.sat_3_2         = row['sat_3_2'] or None
        data.hsat_3          = row['hsat_3'] and int(float(row['hsat_3'].replace(',','.'))) or 0
        data.vol_4_1         = row['vol_3_1'].replace(',','.') or 0
        data.sat_4_1         = row['sat_3_1'] or None
        data.vol_4_2         = row['vol_3_2'].replace(',','.') or 0
        data.sat_4_2         = row['sat_3_2'] or None
        data.hsat_4          = row['hsat_3'] and int(float(row['hsat_3'].replace(',','.'))) or 0
        data.pelaksana       = row['pelaksana'][:25] or None
        data.mulai           = row['mulai'] and datetime.strptime(row['mulai'],'%d/%m/%Y %H:%M:%S') or None
        data.selesai         = row['selesai'] and datetime.strptime(row['selesai'],'%d/%m/%Y %H:%M:%S') or None
        data.bln01           = row['bln01'] and int(float(row['bln01'].replace(',','.'))) or 0
        data.bln02           = row['bln02'] and int(float(row['bln02'].replace(',','.'))) or 0
        data.bln03           = row['bln03'] and int(float(row['bln03'].replace(',','.'))) or 0
        data.bln04           = row['bln04'] and int(float(row['bln04'].replace(',','.'))) or 0
        data.bln05           = row['bln05'] and int(float(row['bln05'].replace(',','.'))) or 0
        data.bln06           = row['bln06'] and int(float(row['bln06'].replace(',','.'))) or 0
        data.bln07           = row['bln07'] and int(float(row['bln07'].replace(',','.'))) or 0
        data.bln08           = row['bln08'] and int(float(row['bln08'].replace(',','.'))) or 0
        data.bln09           = row['bln09'] and int(float(row['bln09'].replace(',','.'))) or 0
        data.bln10           = row['bln10'] and int(float(row['bln10'].replace(',','.'))) or 0
        data.bln11           = row['bln11'] and int(float(row['bln11'].replace(',','.'))) or 0
        data.bln12           = row['bln12'] and int(float(row['bln12'].replace(',','.'))) or 0
        data.is_summary      = row['is_summary']== -1 and 1 or 0
        data.is_apbd         = row['is_apbd'] == -1 and 1 or 0
        data.keterangan      = row['ket'] or None
        data.nama            = row['nama'].strip()
        DBSession.add(data)
        DBSession.flush()
    DBSession.commit()

if __name__ == '__main__':
  KegiatanItem.import_data()
