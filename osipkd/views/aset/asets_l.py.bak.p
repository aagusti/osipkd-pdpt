import unittest
import os.path

from pyjasper import (JasperGenerator)
import xml.etree.ElementTree as ET
from pyramid.path import AssetResolver
def get_rpath(filename):
    a = AssetResolver('osipkd')
    resolver = a.resolve(''.join(['reports/',filename]))
    return resolver.abspath()
    
class rkebijakanGenerator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(rkebijakanGenerator, self).__init__()
        self.reportname = get_rpath('aset/rkebijakan.jrxml')
        self.xpath = '/aset/master/kebijakan'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        xml_a  =  ET.SubElement(self.root, 'master')
        for kode, uraian in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'kebijakan')
            ET.SubElement(xml_greeting, "kode").text = unicode(kode)
            ET.SubElement(xml_greeting, "uraian").text = unicode(uraian)
        return self.root

class rkatGenerator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(rkatGenerator, self).__init__()
        self.reportname = get_rpath('aset/rkat.jrxml')
        self.xpath = '/aset/master/kat'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        xml_a  =  ET.SubElement(self.root, 'master')
        for kode, uraian in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'kat')
            ET.SubElement(xml_greeting, "kode").text = unicode(kode)
            ET.SubElement(xml_greeting, "uraian").text = unicode(uraian)
        return self.root

class r001Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r001Generator, self).__init__()
        self.reportname = get_rpath('aset/R0001.jrxml')
        self.xpath = '/aset/lap01/kib_a'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        #return open('/home/aagusti/env/osipkd/osipkd/reports/apbd/xml/R001.xml').read()
        #ET.SubElement(self.root, 'generator').text = __revision__
        xml_a  =  ET.SubElement(self.root, 'lap01')
        for katnm, katkd, no_register, a_luas_m2, th_beli, a_alamat, a_hak_tanah, a_sertifikat_tgl, a_sertifikat_no, a_penggunaan, asal_usul, harga, keterangan,tahun,unitkd,unitnm in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'kib_a')
            ET.SubElement(xml_greeting, "katnm").text = unicode(katnm)
            ET.SubElement(xml_greeting, "katkd").text = unicode(katkd)
            ET.SubElement(xml_greeting, "no_register").text = unicode(no_register)
            ET.SubElement(xml_greeting, "a_luas_m2").text = unicode(a_luas_m2)
            ET.SubElement(xml_greeting, "th_beli").text = unicode(th_beli)
            ET.SubElement(xml_greeting, "a_alamat").text = unicode(a_alamat)
            ET.SubElement(xml_greeting, "a_hak_tanah").text = unicode(a_hak_tanah)
            ET.SubElement(xml_greeting, "a_sertifikat_tgl").text = unicode(a_sertifikat_tgl)
            ET.SubElement(xml_greeting, "a_sertifikat_no").text = unicode(a_sertifikat_no)
            ET.SubElement(xml_greeting, "a_penggunaan").text = unicode(a_penggunaan)
            ET.SubElement(xml_greeting, "asal_usul").text = unicode(asal_usul)
            ET.SubElement(xml_greeting, "harga").text = unicode(harga)
            ET.SubElement(xml_greeting, "keterangan").text = unicode(keterangan)
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "unitkd").text = unicode(unitkd)
            ET.SubElement(xml_greeting, "unitnm").text = unicode(unitnm)
        return self.root

class r002Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r002Generator, self).__init__()
        self.reportname = get_rpath('aset/R0002.jrxml')
        self.xpath = '/aset/lap01/kib_b'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        #return open('/home/aagusti/env/osipkd/osipkd/reports/apbd/xml/R001.xml').read()
        #ET.SubElement(self.root, 'generator').text = __revision__
        xml_a  =  ET.SubElement(self.root, 'lap01')
        for katnm, katkd, no_register, b_merk, b_type, b_cc, b_bahan, tahun, b_nomor_pabrik, b_nomor_rangka, b_nomor_mesin, b_nomor_polisi, b_nomor_bpkb, asal_usul, harga, keterangan,tahun,unitkd,unitnm  in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'kib_b')
            ET.SubElement(xml_greeting, "katnm").text = unicode(katnm)
            ET.SubElement(xml_greeting, "katkd").text = unicode(katkd)
            ET.SubElement(xml_greeting, "no_register").text = unicode(no_register)
            ET.SubElement(xml_greeting, "b_merk").text = unicode(b_merk)
            ET.SubElement(xml_greeting, "b_type").text = unicode(b_type)
            ET.SubElement(xml_greeting, "b_cc").text = unicode(b_cc)
            ET.SubElement(xml_greeting, "b_bahan").text = unicode(b_bahan)
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "b_nomor_pabrik").text = unicode(b_nomor_pabrik)
            ET.SubElement(xml_greeting, "b_nomor_rangka").text = unicode(b_nomor_rangka)
            ET.SubElement(xml_greeting, "b_nomor_mesin").text = unicode(b_nomor_mesin)
            ET.SubElement(xml_greeting, "b_nomor_polisi").text = unicode(b_nomor_polisi)
            ET.SubElement(xml_greeting, "b_nomor_bpkb").text = unicode(b_nomor_bpkb)
            ET.SubElement(xml_greeting, "asal_usul").text = unicode(asal_usul)
            ET.SubElement(xml_greeting, "harga").text = unicode(harga)
            ET.SubElement(xml_greeting, "keterangan").text = unicode(keterangan)
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "unitkd").text = unicode(unitkd)
            ET.SubElement(xml_greeting, "unitnm").text = unicode(unitnm)
        return self.root

class r003Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r003Generator, self).__init__()
        self.reportname = get_rpath('aset/R0003.jrxml')
        self.xpath = '/aset/lap01/kib_c'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        #return open('/home/aagusti/env/osipkd/osipkd/reports/apbd/xml/R001.xml').read()
        #ET.SubElement(self.root, 'generator').text = __revision__
        xml_a  =  ET.SubElement(self.root, 'lap01')
        for katnm, katkd, no_register, kondisi, c_bertingkat_tidak, c_beton_tidak, c_luas_lantai, c_lokasi, c_dokumen_tanggal, c_dokumen_nomor, c_luas_bangunan, c_status_tanah, c_kode_tanah, asal_usul, harga, keterangan,tahun,unitkd,unitnm in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'kib_c')
            ET.SubElement(xml_greeting, "katnm").text = unicode(katnm)
            ET.SubElement(xml_greeting, "katkd").text = unicode(katkd)
            ET.SubElement(xml_greeting, "no_register").text = unicode(no_register)
            ET.SubElement(xml_greeting, "kondisi").text = unicode(kondisi)
            ET.SubElement(xml_greeting, "c_bertingkat_tidak").text = unicode(c_bertingkat_tidak)
            ET.SubElement(xml_greeting, "c_beton_tidak").text = unicode(c_beton_tidak)
            ET.SubElement(xml_greeting, "c_luas_lantai").text = unicode(c_luas_lantai)
            ET.SubElement(xml_greeting, "c_lokasi").text = unicode(c_lokasi)
            ET.SubElement(xml_greeting, "c_dokumen_tanggal").text = unicode(c_dokumen_tanggal)
            ET.SubElement(xml_greeting, "c_dokumen_nomor").text = unicode(c_dokumen_nomor)
            ET.SubElement(xml_greeting, "c_luas_bangunan").text = unicode(c_luas_bangunan)
            ET.SubElement(xml_greeting, "c_status_tanah").text = unicode(c_status_tanah)
            ET.SubElement(xml_greeting, "c_kode_tanah").text = unicode(c_kode_tanah)
            ET.SubElement(xml_greeting, "asal_usul").text = unicode(asal_usul)
            ET.SubElement(xml_greeting, "harga").text = unicode(harga)
            ET.SubElement(xml_greeting, "keterangan").text = unicode(keterangan)
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "unitkd").text = unicode(unitkd)
            ET.SubElement(xml_greeting, "unitnm").text = unicode(unitnm)
        return self.root

class r004Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r004Generator, self).__init__()
        self.reportname = get_rpath('aset/R0004.jrxml')
        self.xpath = '/aset/lap01/kib_d'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        #return open('/home/aagusti/env/osipkd/osipkd/reports/apbd/xml/R001.xml').read()
        #ET.SubElement(self.root, 'generator').text = __revision__
        xml_a  =  ET.SubElement(self.root, 'lap01')
        for katnm, katkd, no_register, d_konstruksi, d_panjang, d_lebar, d_luas, d_lokasi, d_dokumen_tanggal, d_dokumen_nomor, d_status_tanah, d_kode_tanah, asal_usul, harga, kondisi, keterangan, tahun,unitkd,unitnm in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'kib_d')
            ET.SubElement(xml_greeting, "katnm").text = unicode(katnm)
            ET.SubElement(xml_greeting, "katkd").text = unicode(katkd)
            ET.SubElement(xml_greeting, "no_register").text = unicode(no_register)
            ET.SubElement(xml_greeting, "d_konstruksi").text = unicode(d_konstruksi)
            ET.SubElement(xml_greeting, "d_panjang").text = unicode(d_panjang)
            ET.SubElement(xml_greeting, "d_lebar").text = unicode(d_lebar)
            ET.SubElement(xml_greeting, "d_luas").text = unicode(d_luas)
            ET.SubElement(xml_greeting, "d_lokasi").text = unicode(d_lokasi)
            ET.SubElement(xml_greeting, "d_dokumen_tanggal").text = unicode(d_dokumen_tanggal)
            ET.SubElement(xml_greeting, "d_dokumen_nomor").text = unicode(d_dokumen_nomor)
            ET.SubElement(xml_greeting, "d_status_tanah").text = unicode(d_status_tanah)
            ET.SubElement(xml_greeting, "d_kode_tanah").text = unicode(d_kode_tanah)
            ET.SubElement(xml_greeting, "asal_usul").text = unicode(asal_usul)
            ET.SubElement(xml_greeting, "harga").text = unicode(harga)
            ET.SubElement(xml_greeting, "kondisi").text = unicode(kondisi)
            ET.SubElement(xml_greeting, "keterangan").text = unicode(keterangan)
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "unitkd").text = unicode(unitkd)
            ET.SubElement(xml_greeting, "unitnm").text = unicode(unitnm)
        return self.root

class r005Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r005Generator, self).__init__()
        self.reportname = get_rpath('aset/R0005.jrxml')
        self.xpath = '/aset/lap01/kib_e'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        #return open('/home/aagusti/env/osipkd/osipkd/reports/apbd/xml/R001.xml').read()
        #ET.SubElement(self.root, 'generator').text = __revision__
        xml_a  =  ET.SubElement(self.root, 'lap01')
        for katnm, katkd, no_register, e_judul, e_spek, e_asal, e_pencipta, e_bahan, e_jenis, e_ukuran, jumlah, asal_usul, b_thbuat, harga, keterangan,tahun,unitkd,unitnm in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'kib_e')
            ET.SubElement(xml_greeting, "katnm").text = unicode(katnm)
            ET.SubElement(xml_greeting, "katkd").text = unicode(katkd)
            ET.SubElement(xml_greeting, "no_register").text = unicode(no_register)
            ET.SubElement(xml_greeting, "e_judul").text = unicode(e_judul)
            ET.SubElement(xml_greeting, "e_spek").text = unicode(e_spek)
            ET.SubElement(xml_greeting, "e_asal").text = unicode(e_asal)
            ET.SubElement(xml_greeting, "e_pencipta").text = unicode(e_pencipta)
            ET.SubElement(xml_greeting, "e_bahan").text = unicode(e_bahan)
            ET.SubElement(xml_greeting, "e_jenis").text = unicode(e_jenis)
            ET.SubElement(xml_greeting, "e_ukuran").text = unicode(e_ukuran)
            ET.SubElement(xml_greeting, "jumlah").text = unicode(jumlah)
            ET.SubElement(xml_greeting, "asal_usul").text = unicode(asal_usul)
            ET.SubElement(xml_greeting, "b_thbuat").text = unicode(b_thbuat)
            ET.SubElement(xml_greeting, "harga").text = unicode(harga)
            ET.SubElement(xml_greeting, "keterangan").text = unicode(keterangan)
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "unitkd").text = unicode(unitkd)
            ET.SubElement(xml_greeting, "unitnm").text = unicode(unitnm)
        return self.root

class r006Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r006Generator, self).__init__()
        self.reportname = get_rpath('aset/R0006.jrxml')
        self.xpath = '/aset/lap01/kib_f'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        #return open('/home/aagusti/env/osipkd/osipkd/reports/apbd/xml/R001.xml').read()
        #ET.SubElement(self.root, 'generator').text = __revision__
        xml_a  =  ET.SubElement(self.root, 'lap01')
        for katnm, katkd, kondisi, f_bertingkat_tidak, f_beton_tidak, f_luas_lantai, f_lokasi, f_dokumen_tanggal, f_dokumen_nomor, tgl_perolehan, f_status_tanah, f_kode_tanah, asal_usul, harga, keterangan, tahun, unitkd, unitnm in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'kib_f')
            ET.SubElement(xml_greeting, "katnm").text = unicode(katnm)
            ET.SubElement(xml_greeting, "katkd").text = unicode(katkd)
            ET.SubElement(xml_greeting, "kondisi").text = unicode(kondisi)
            ET.SubElement(xml_greeting, "f_bertingkat_tidak").text = unicode(f_bertingkat_tidak)
            ET.SubElement(xml_greeting, "f_beton_tidak").text = unicode(f_beton_tidak)
            ET.SubElement(xml_greeting, "f_luas_lantai").text = unicode(f_luas_lantai)
            ET.SubElement(xml_greeting, "f_lokasi").text = unicode(f_lokasi)
            ET.SubElement(xml_greeting, "f_dokumen_tanggal").text = unicode(f_dokumen_tanggal)
            ET.SubElement(xml_greeting, "f_dokumen_nomor").text = unicode(f_dokumen_nomor)
            ET.SubElement(xml_greeting, "tgl_perolehan").text = unicode(tgl_perolehan)
            ET.SubElement(xml_greeting, "f_status_tanah").text = unicode(f_status_tanah)
            ET.SubElement(xml_greeting, "f_kode_tanah").text = unicode(f_kode_tanah)
            ET.SubElement(xml_greeting, "asal_usul").text = unicode(asal_usul)
            ET.SubElement(xml_greeting, "harga").text = unicode(harga)
            ET.SubElement(xml_greeting, "keterangan").text = unicode(keterangan)
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "unitkd").text = unicode(unitkd)
            ET.SubElement(xml_greeting, "unitnm").text = unicode(unitnm)
        return self.root

class r008Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r008Generator, self).__init__()
        self.reportname = get_rpath('aset/R0008.jrxml')
        self.xpath = '/aset/lap01/inv'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        #return open('/home/aagusti/env/osipkd/osipkd/reports/apbd/xml/R001.xml').read()
        #ET.SubElement(self.root, 'generator').text = __revision__
        xml_a  =  ET.SubElement(self.root, 'lap01')
        for katkd, no_register, katnm, b_merk, b_type, a_sertifikat_nomor, b_nomor_pabrik, b_nomor_rangka, b_nomor_mesin, b_bahan, asal_usul, th_beli, e_ukuran, d_konstruksi, kondisi, jumlah, harga, keterangan, tahun, unitkd, unitnm in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'inv')
            ET.SubElement(xml_greeting, "katkd").text = unicode(katkd)
            ET.SubElement(xml_greeting, "no_register").text = unicode(no_register)
            ET.SubElement(xml_greeting, "katnm").text = unicode(katnm)
            ET.SubElement(xml_greeting, "b_merk").text = unicode(b_merk)
            ET.SubElement(xml_greeting, "b_type").text = unicode(b_type)
            ET.SubElement(xml_greeting, "a_sertifikat_nomor").text = unicode(a_sertifikat_nomor)
            ET.SubElement(xml_greeting, "b_nomor_pabrik").text = unicode(b_nomor_pabrik)
            ET.SubElement(xml_greeting, "b_nomor_rangka").text = unicode(b_nomor_rangka)
            ET.SubElement(xml_greeting, "b_nomor_mesin").text = unicode(b_nomor_mesin)
            ET.SubElement(xml_greeting, "b_bahan").text = unicode(b_bahan)
            ET.SubElement(xml_greeting, "asal_usul").text = unicode(asal_usul)
            ET.SubElement(xml_greeting, "th_beli").text = unicode(th_beli)
            ET.SubElement(xml_greeting, "e_ukuran").text = unicode(e_ukuran)
            ET.SubElement(xml_greeting, "d_konstruksi").text = unicode(d_konstruksi)
            ET.SubElement(xml_greeting, "kondisi").text = unicode(kondisi)
            ET.SubElement(xml_greeting, "jumlah").text = unicode(jumlah)
            ET.SubElement(xml_greeting, "harga").text = unicode(harga)
            ET.SubElement(xml_greeting, "keterangan").text = unicode(keterangan)
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "unitkd").text = unicode(unitkd)
            ET.SubElement(xml_greeting, "unitnm").text = unicode(unitnm)
        return self.root

class r010Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r010Generator, self).__init__()
        self.reportname = get_rpath('aset/R0010.jrxml')
        self.xpath = '/aset/lap01/neraca'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        #return open('/home/aagusti/env/osipkd/osipkd/reports/apbd/xml/R001.xml').read()
        #ET.SubElement(self.root, 'generator').text = __revision__
        xml_a  =  ET.SubElement(self.root, 'lap01')
        for tahun, unitkd, unitnm, kode, uraian, nilai in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'neraca')
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "unitkd").text = unicode(unitkd)
            ET.SubElement(xml_greeting, "unitnm").text = unicode(unitnm)
            ET.SubElement(xml_greeting, "kode").text = unicode(kode)
            ET.SubElement(xml_greeting, "uraian").text = unicode(uraian)
            ET.SubElement(xml_greeting, "nilai").text = unicode(nilai)
        return self.root

class r101Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r101Generator, self).__init__()
        self.reportname = get_rpath('aset/R1001.jrxml')
        self.xpath = '/aset/lap01/kib_a'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        #return open('/home/aagusti/env/osipkd/osipkd/reports/apbd/xml/R001.xml').read()
        #ET.SubElement(self.root, 'generator').text = __revision__
        xml_a  =  ET.SubElement(self.root, 'lap01')
        for katnm, katkd, no_register, a_luas_m2, th_beli, a_alamat, a_hak_tanah, a_sertifikat_tgl, a_sertifikat_no, a_penggunaan, asal_usul, harga, keterangan,tahun,unitkd,unitnm in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'kib_a')
            ET.SubElement(xml_greeting, "katnm").text = unicode(katnm)
            ET.SubElement(xml_greeting, "katkd").text = unicode(katkd)
            ET.SubElement(xml_greeting, "no_register").text = unicode(no_register)
            ET.SubElement(xml_greeting, "a_luas_m2").text = unicode(a_luas_m2)
            ET.SubElement(xml_greeting, "th_beli").text = unicode(th_beli)
            ET.SubElement(xml_greeting, "a_alamat").text = unicode(a_alamat)
            ET.SubElement(xml_greeting, "a_hak_tanah").text = unicode(a_hak_tanah)
            ET.SubElement(xml_greeting, "a_sertifikat_tgl").text = unicode(a_sertifikat_tgl)
            ET.SubElement(xml_greeting, "a_sertifikat_no").text = unicode(a_sertifikat_no)
            ET.SubElement(xml_greeting, "a_penggunaan").text = unicode(a_penggunaan)
            ET.SubElement(xml_greeting, "asal_usul").text = unicode(asal_usul)
            ET.SubElement(xml_greeting, "harga").text = unicode(harga)
            ET.SubElement(xml_greeting, "keterangan").text = unicode(keterangan)
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "unitkd").text = unicode(unitkd)
            ET.SubElement(xml_greeting, "unitnm").text = unicode(unitnm)
        return self.root

class r102Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r102Generator, self).__init__()
        self.reportname = get_rpath('aset/R1002.jrxml')
        self.xpath = '/aset/lap01/kib_b'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        #return open('/home/aagusti/env/osipkd/osipkd/reports/apbd/xml/R001.xml').read()
        #ET.SubElement(self.root, 'generator').text = __revision__
        xml_a  =  ET.SubElement(self.root, 'lap01')
        for katnm, katkd, no_register, b_merk, b_type, b_cc, b_bahan, tahun, b_nomor_pabrik, b_nomor_rangka, b_nomor_mesin, b_nomor_polisi, b_nomor_bpkb, asal_usul, harga, keterangan,tahun,unitkd,unitnm  in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'kib_b')
            ET.SubElement(xml_greeting, "katnm").text = unicode(katnm)
            ET.SubElement(xml_greeting, "katkd").text = unicode(katkd)
            ET.SubElement(xml_greeting, "no_register").text = unicode(no_register)
            ET.SubElement(xml_greeting, "b_merk").text = unicode(b_merk)
            ET.SubElement(xml_greeting, "b_type").text = unicode(b_type)
            ET.SubElement(xml_greeting, "b_cc").text = unicode(b_cc)
            ET.SubElement(xml_greeting, "b_bahan").text = unicode(b_bahan)
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "b_nomor_pabrik").text = unicode(b_nomor_pabrik)
            ET.SubElement(xml_greeting, "b_nomor_rangka").text = unicode(b_nomor_rangka)
            ET.SubElement(xml_greeting, "b_nomor_mesin").text = unicode(b_nomor_mesin)
            ET.SubElement(xml_greeting, "b_nomor_polisi").text = unicode(b_nomor_polisi)
            ET.SubElement(xml_greeting, "b_nomor_bpkb").text = unicode(b_nomor_bpkb)
            ET.SubElement(xml_greeting, "asal_usul").text = unicode(asal_usul)
            ET.SubElement(xml_greeting, "harga").text = unicode(harga)
            ET.SubElement(xml_greeting, "keterangan").text = unicode(keterangan)
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "unitkd").text = unicode(unitkd)
            ET.SubElement(xml_greeting, "unitnm").text = unicode(unitnm)
        return self.root

class r103Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r103Generator, self).__init__()
        self.reportname = get_rpath('aset/R1003.jrxml')
        self.xpath = '/aset/lap01/kib_c'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        #return open('/home/aagusti/env/osipkd/osipkd/reports/apbd/xml/R001.xml').read()
        #ET.SubElement(self.root, 'generator').text = __revision__
        xml_a  =  ET.SubElement(self.root, 'lap01')
        for katnm, katkd, no_register, kondisi, c_bertingkat_tidak, c_beton_tidak, c_luas_lantai, c_lokasi, c_dokumen_tanggal, c_dokumen_nomor, c_luas_bangunan, c_status_tanah, c_kode_tanah, asal_usul, harga, keterangan,tahun,unitkd,unitnm in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'kib_c')
            ET.SubElement(xml_greeting, "katnm").text = unicode(katnm)
            ET.SubElement(xml_greeting, "katkd").text = unicode(katkd)
            ET.SubElement(xml_greeting, "no_register").text = unicode(no_register)
            ET.SubElement(xml_greeting, "kondisi").text = unicode(kondisi)
            ET.SubElement(xml_greeting, "c_bertingkat_tidak").text = unicode(c_bertingkat_tidak)
            ET.SubElement(xml_greeting, "c_beton_tidak").text = unicode(c_beton_tidak)
            ET.SubElement(xml_greeting, "c_luas_lantai").text = unicode(c_luas_lantai)
            ET.SubElement(xml_greeting, "c_lokasi").text = unicode(c_lokasi)
            ET.SubElement(xml_greeting, "c_dokumen_tanggal").text = unicode(c_dokumen_tanggal)
            ET.SubElement(xml_greeting, "c_dokumen_nomor").text = unicode(c_dokumen_nomor)
            ET.SubElement(xml_greeting, "c_luas_bangunan").text = unicode(c_luas_bangunan)
            ET.SubElement(xml_greeting, "c_status_tanah").text = unicode(c_status_tanah)
            ET.SubElement(xml_greeting, "c_kode_tanah").text = unicode(c_kode_tanah)
            ET.SubElement(xml_greeting, "asal_usul").text = unicode(asal_usul)
            ET.SubElement(xml_greeting, "harga").text = unicode(harga)
            ET.SubElement(xml_greeting, "keterangan").text = unicode(keterangan)
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "unitkd").text = unicode(unitkd)
            ET.SubElement(xml_greeting, "unitnm").text = unicode(unitnm)
        return self.root

class r104Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r104Generator, self).__init__()
        self.reportname = get_rpath('aset/R1004.jrxml')
        self.xpath = '/aset/lap01/kib_d'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        #return open('/home/aagusti/env/osipkd/osipkd/reports/apbd/xml/R001.xml').read()
        #ET.SubElement(self.root, 'generator').text = __revision__
        xml_a  =  ET.SubElement(self.root, 'lap01')
        for katnm, katkd, no_register, d_konstruksi, d_panjang, d_lebar, d_luas, d_lokasi, d_dokumen_tanggal, d_dokumen_nomor, d_status_tanah, d_kode_tanah, asal_usul, harga, kondisi, keterangan, tahun,unitkd,unitnm in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'kib_d')
            ET.SubElement(xml_greeting, "katnm").text = unicode(katnm)
            ET.SubElement(xml_greeting, "katkd").text = unicode(katkd)
            ET.SubElement(xml_greeting, "no_register").text = unicode(no_register)
            ET.SubElement(xml_greeting, "d_konstruksi").text = unicode(d_konstruksi)
            ET.SubElement(xml_greeting, "d_panjang").text = unicode(d_panjang)
            ET.SubElement(xml_greeting, "d_lebar").text = unicode(d_lebar)
            ET.SubElement(xml_greeting, "d_luas").text = unicode(d_luas)
            ET.SubElement(xml_greeting, "d_lokasi").text = unicode(d_lokasi)
            ET.SubElement(xml_greeting, "d_dokumen_tanggal").text = unicode(d_dokumen_tanggal)
            ET.SubElement(xml_greeting, "d_dokumen_nomor").text = unicode(d_dokumen_nomor)
            ET.SubElement(xml_greeting, "d_status_tanah").text = unicode(d_status_tanah)
            ET.SubElement(xml_greeting, "d_kode_tanah").text = unicode(d_kode_tanah)
            ET.SubElement(xml_greeting, "asal_usul").text = unicode(asal_usul)
            ET.SubElement(xml_greeting, "harga").text = unicode(harga)
            ET.SubElement(xml_greeting, "kondisi").text = unicode(kondisi)
            ET.SubElement(xml_greeting, "keterangan").text = unicode(keterangan)
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "unitkd").text = unicode(unitkd)
            ET.SubElement(xml_greeting, "unitnm").text = unicode(unitnm)
        return self.root

class r105Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r105Generator, self).__init__()
        self.reportname = get_rpath('aset/R1005.jrxml')
        self.xpath = '/aset/lap01/kib_e'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        #return open('/home/aagusti/env/osipkd/osipkd/reports/apbd/xml/R001.xml').read()
        #ET.SubElement(self.root, 'generator').text = __revision__
        xml_a  =  ET.SubElement(self.root, 'lap01')
        for katnm, katkd, no_register, e_judul, e_spek, e_asal, e_pencipta, e_bahan, e_jenis, e_ukuran, jumlah, asal_usul, b_thbuat, harga, keterangan,tahun,unitkd,unitnm in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'kib_e')
            ET.SubElement(xml_greeting, "katnm").text = unicode(katnm)
            ET.SubElement(xml_greeting, "katkd").text = unicode(katkd)
            ET.SubElement(xml_greeting, "no_register").text = unicode(no_register)
            ET.SubElement(xml_greeting, "e_judul").text = unicode(e_judul)
            ET.SubElement(xml_greeting, "e_spek").text = unicode(e_spek)
            ET.SubElement(xml_greeting, "e_asal").text = unicode(e_asal)
            ET.SubElement(xml_greeting, "e_pencipta").text = unicode(e_pencipta)
            ET.SubElement(xml_greeting, "e_bahan").text = unicode(e_bahan)
            ET.SubElement(xml_greeting, "e_jenis").text = unicode(e_jenis)
            ET.SubElement(xml_greeting, "e_ukuran").text = unicode(e_ukuran)
            ET.SubElement(xml_greeting, "jumlah").text = unicode(jumlah)
            ET.SubElement(xml_greeting, "asal_usul").text = unicode(asal_usul)
            ET.SubElement(xml_greeting, "b_thbuat").text = unicode(b_thbuat)
            ET.SubElement(xml_greeting, "harga").text = unicode(harga)
            ET.SubElement(xml_greeting, "keterangan").text = unicode(keterangan)
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "unitkd").text = unicode(unitkd)
            ET.SubElement(xml_greeting, "unitnm").text = unicode(unitnm)
        return self.root

class r106Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r106Generator, self).__init__()
        self.reportname = get_rpath('aset/R1006.jrxml')
        self.xpath = '/aset/lap01/kib_f'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        #return open('/home/aagusti/env/osipkd/osipkd/reports/apbd/xml/R001.xml').read()
        #ET.SubElement(self.root, 'generator').text = __revision__
        xml_a  =  ET.SubElement(self.root, 'lap01')
        for katnm, katkd, kondisi, f_bertingkat_tidak, f_beton_tidak, f_luas_lantai, f_lokasi, f_dokumen_tanggal, f_dokumen_nomor, tgl_perolehan, f_status_tanah, f_kode_tanah, asal_usul, harga, keterangan, tahun, unitkd, unitnm in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'kib_f')
            ET.SubElement(xml_greeting, "katnm").text = unicode(katnm)
            ET.SubElement(xml_greeting, "katkd").text = unicode(katkd)
            ET.SubElement(xml_greeting, "kondisi").text = unicode(kondisi)
            ET.SubElement(xml_greeting, "f_bertingkat_tidak").text = unicode(f_bertingkat_tidak)
            ET.SubElement(xml_greeting, "f_beton_tidak").text = unicode(f_beton_tidak)
            ET.SubElement(xml_greeting, "f_luas_lantai").text = unicode(f_luas_lantai)
            ET.SubElement(xml_greeting, "f_lokasi").text = unicode(f_lokasi)
            ET.SubElement(xml_greeting, "f_dokumen_tanggal").text = unicode(f_dokumen_tanggal)
            ET.SubElement(xml_greeting, "f_dokumen_nomor").text = unicode(f_dokumen_nomor)
            ET.SubElement(xml_greeting, "tgl_perolehan").text = unicode(tgl_perolehan)
            ET.SubElement(xml_greeting, "f_status_tanah").text = unicode(f_status_tanah)
            ET.SubElement(xml_greeting, "f_kode_tanah").text = unicode(f_kode_tanah)
            ET.SubElement(xml_greeting, "asal_usul").text = unicode(asal_usul)
            ET.SubElement(xml_greeting, "harga").text = unicode(harga)
            ET.SubElement(xml_greeting, "keterangan").text = unicode(keterangan)
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "unitkd").text = unicode(unitkd)
            ET.SubElement(xml_greeting, "unitnm").text = unicode(unitnm)
        return self.root

class r108Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r108Generator, self).__init__()
        self.reportname = get_rpath('aset/R1008.jrxml')
        self.xpath = '/aset/lap01/inv'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        #return open('/home/aagusti/env/osipkd/osipkd/reports/apbd/xml/R001.xml').read()
        #ET.SubElement(self.root, 'generator').text = __revision__
        xml_a  =  ET.SubElement(self.root, 'lap01')
        for katkd, no_register, katnm, b_merk, b_type, a_sertifikat_nomor, b_nomor_pabrik, b_nomor_rangka, b_nomor_mesin, b_bahan, asal_usul, th_beli, e_ukuran, d_konstruksi, kondisi, jumlah, harga, keterangan, tahun, unitkd, unitnm in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'inv')
            ET.SubElement(xml_greeting, "katkd").text = unicode(katkd)
            ET.SubElement(xml_greeting, "no_register").text = unicode(no_register)
            ET.SubElement(xml_greeting, "katnm").text = unicode(katnm)
            ET.SubElement(xml_greeting, "b_merk").text = unicode(b_merk)
            ET.SubElement(xml_greeting, "b_type").text = unicode(b_type)
            ET.SubElement(xml_greeting, "a_sertifikat_nomor").text = unicode(a_sertifikat_nomor)
            ET.SubElement(xml_greeting, "b_nomor_pabrik").text = unicode(b_nomor_pabrik)
            ET.SubElement(xml_greeting, "b_nomor_rangka").text = unicode(b_nomor_rangka)
            ET.SubElement(xml_greeting, "b_nomor_mesin").text = unicode(b_nomor_mesin)
            ET.SubElement(xml_greeting, "b_bahan").text = unicode(b_bahan)
            ET.SubElement(xml_greeting, "asal_usul").text = unicode(asal_usul)
            ET.SubElement(xml_greeting, "th_beli").text = unicode(th_beli)
            ET.SubElement(xml_greeting, "e_ukuran").text = unicode(e_ukuran)
            ET.SubElement(xml_greeting, "d_konstruksi").text = unicode(d_konstruksi)
            ET.SubElement(xml_greeting, "kondisi").text = unicode(kondisi)
            ET.SubElement(xml_greeting, "jumlah").text = unicode(jumlah)
            ET.SubElement(xml_greeting, "harga").text = unicode(harga)
            ET.SubElement(xml_greeting, "keterangan").text = unicode(keterangan)
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "unitkd").text = unicode(unitkd)
            ET.SubElement(xml_greeting, "unitnm").text = unicode(unitnm)
        return self.root

class r110Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r110Generator, self).__init__()
        self.reportname = get_rpath('aset/R1010.jrxml')
        self.xpath = '/aset/lap01/neraca'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        #return open('/home/aagusti/env/osipkd/osipkd/reports/apbd/xml/R001.xml').read()
        #ET.SubElement(self.root, 'generator').text = __revision__
        xml_a  =  ET.SubElement(self.root, 'lap01')
        for tahun, unitkd, unitnm, kode, uraian, nilai in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'neraca')
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "unitkd").text = unicode(unitkd)
            ET.SubElement(xml_greeting, "unitnm").text = unicode(unitnm)
            ET.SubElement(xml_greeting, "kode").text = unicode(kode)
            ET.SubElement(xml_greeting, "uraian").text = unicode(uraian)
            ET.SubElement(xml_greeting, "nilai").text = unicode(nilai)
        return self.root

if __name__ == '__main__':
        generator = r001Generator()

        generator.generate([('1','2')])
