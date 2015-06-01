from base import *
from rekening import Rekening
from rekening_hukum import DasarHukum
from urusan import Urusan
from fungsi import Fungsi
from fungsi_urusan import FungsiUrusan
from unit import Unit
from program import Program
from kegiatan import Kegiatan

if __name__ == '__main__':
  Rekening.import_data()
  DasarHukum.import_data()
  Urusan.import_data()
  Fungsi.import_data()
  FungsiUrusan.import_data()
  Unit.import_data()
  Program.import_data()
  Kegiatan.import_data()
  