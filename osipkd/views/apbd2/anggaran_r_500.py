import unittest
import os.path
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from pyramid.security import remember
from pyramid.security import forget
from pyramid.security import has_permission
from sqlalchemy import *
from sqlalchemy import distinct
from sqlalchemy.sql.functions import concat
from sqlalchemy.exc import DBAPIError
from osipkd.views.views import *
from osipkd.models.model_base import *
from osipkd.models.apbd_rka_models import *
from osipkd.models.apbd_admin_models import (TahunModel, UserApbdModel,Unit,
     Urusan, RekeningModel, ProgramModel, KegiatanModel, DasarHukumModel)
from datetime import datetime
import os
from pyramid.renderers import render_to_response

from anggaran_lap import *

from pyjasper import (JasperGenerator)
from pyjasper import (JasperGeneratorWithSubreport)
import xml.etree.ElementTree as ET
from pyramid.path import AssetResolver

def get_rpath(filename):
    a = AssetResolver('osipkd')
    resolver = a.resolve(''.join(['reports/',filename]))
    return resolver.abspath()

class r500Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r500Generator, self).__init__()
        self.reportname = get_rpath('apbd/R5000.jrxml')
        self.xpath = '/apbd/perda/lamp1'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        xml_a  =  ET.SubElement(self.root, 'perda')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'lamp1')
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_greeting, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_greeting, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_greeting, "jumlah3").text = unicode(row.jumlah3)
            ET.SubElement(xml_greeting, "jumlah4").text = unicode(row.jumlah4)
        return self.root

class r5001Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r5001Generator, self).__init__()
        self.reportname = get_rpath('apbd/R50001.jrxml')
        self.xpath = '/apbd/perda/lamp1'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        xml_a  =  ET.SubElement(self.root, 'perda')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'lamp1')
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_greeting, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_greeting, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_greeting, "jumlah3").text = unicode(row.jumlah3)
            ET.SubElement(xml_greeting, "jumlah4").text = unicode(row.jumlah4)
        return self.root

class r501Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r501Generator, self).__init__()
        self.reportname = get_rpath('apbd/R5001.jrxml')
        self.xpath = '/apbd/perda/lamp2'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        xml_a  =  ET.SubElement(self.root, 'perda')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'lamp2')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_greeting, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "jenis_kd").text = unicode(row.jenis_kd)
            ET.SubElement(xml_greeting, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_greeting, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_greeting, "jumlah3").text = unicode(row.jumlah3)
            ET.SubElement(xml_greeting, "jumlah4").text = unicode(row.jumlah4)
            """ET.SubElement(xml_greeting, "tahun").text = unicode(row.kegiatan_sub.tahun_id)
            ET.SubElement(xml_greeting, "urusan_kd").text = row.kegiatan_sub.kegiatans.programs.urusans.kode
            ET.SubElement(xml_greeting, "urusan_nm").text = row.kegiatan_sub.kegiatans.programs.urusans.nama
            ET.SubElement(xml_greeting, "unit_kd").text = row.kegiatan_sub.units.kode
            ET.SubElement(xml_greeting, "unit_nm").text = row.kegiatan_sub.units.nama
            ET.SubElement(xml_greeting, "jenis_kd").text = unicode(row.kegiatan_sub.kegiatans.id)
            ET.SubElement(xml_greeting, "jumlah1").text = unicode(row.vol_1_1*row.vol_1_2*row.hsat_1)
            ET.SubElement(xml_greeting, "jumlah2").text = unicode(row.vol_2_1*row.vol_2_2*row.hsat_2)
            ET.SubElement(xml_greeting, "jumlah3").text = unicode(row.vol_3_1*row.vol_3_2*row.hsat_3)
            ET.SubElement(xml_greeting, "jumlah4").text = unicode(row.vol_4_1*row.vol_4_2*row.hsat_4)
            """
        return self.root

class r502Generator(JasperGeneratorWithSubreport):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        self.mainreport = get_rpath('apbd/R5002.jrxml')
        self.subreportlist = []
        self.subreportlist.append(get_rpath('apbd/R5002_subreport1.jrxml'))
        self.subreportlist.append(get_rpath('apbd/R5002_subreport2.jrxml'))
        self.subreportlist.append(get_rpath('apbd/R5002_subreport3.jrxml'))
        #self.subreportlist.append(get_rpath('apbd/R5002_subreport2_subreport1.jrxml'))
        print self.mainreport,self.subreportlist
        self.xpath = '/apbd/kegiatan'

        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'kegiatan')
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_id").text = unicode(row.unit_id)
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "program_kd").text = row.program_kd
            ET.SubElement(xml_a, "program_nm").text = row.program_nm
            ET.SubElement(xml_a, "kegiatan_kd").text = row.kegiatan_kd
            ET.SubElement(xml_a, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_a, "lokasi").text = row.lokasi
            ET.SubElement(xml_a, "sdana").text = row.sdana
            ET.SubElement(xml_a, "jenis").text = unicode(row.jenis)
            ET.SubElement(xml_a, "kegiatan_id").text = unicode(row.kegiatan_id)
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.kegiatan_sub_id)
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "rekening_id").text = unicode(row.rekening_id)
            ET.SubElement(xml_a, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_a, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_a, "jumlah3").text = unicode(row.jumlah3)
            ET.SubElement(xml_a, "jumlah4").text = unicode(row.jumlah4)
            
            rows = DBSession.query(KegiatanIndikatorModel)\
              .filter(KegiatanIndikatorModel.kegitan_sub_id==row.kegiatan_sub_id,
              KegiatanIndikatorModel.tipe==4)\
              .order_by(KegiatanIndikatorModel.tipe,KegiatanIndikatorModel.no_urut)
            for row2 in rows :
                xml_b = ET.SubElement(xml_a, "indikator")
                ET.SubElement(xml_b, "tipe").text =unicode(row2.tipe)
                ET.SubElement(xml_b, "no_urut").text =unicode(row2.no_urut)
                ET.SubElement(xml_b, "tolok_ukur_1").text =row2.tolok_ukur_2
                ET.SubElement(xml_b, "volume_1").text =unicode(row2.volume_2)
                ET.SubElement(xml_b, "satuan_1").text =row2.satuan_2
            
            rowhkm = DBSession.query(DasarHukumModel.no_urut,DasarHukumModel.nama)\
               .filter(DasarHukumModel.rekening_id==row.rekening_id)\
               .order_by(DasarHukumModel.no_urut)
                
            for row3 in rowhkm :
                xml_c = ET.SubElement(xml_a, "hukum")
                ET.SubElement(xml_c, "no_urut").text =unicode(row3.no_urut)
                ET.SubElement(xml_c, "uraian").text =row3.nama
                #print "XXXXX"+row3.nama

            rowitem = DBSession.query(KegiatanItemModel.kode.label('item_kd'), KegiatanItemModel.nama.label('item_nm'),
               (KegiatanItemModel.vol_1_1*KegiatanItemModel.vol_1_2).label('volume1'),
               (KegiatanItemModel.vol_2_1*KegiatanItemModel.vol_2_2).label('volume2'),
               (KegiatanItemModel.vol_3_1*KegiatanItemModel.vol_3_2).label('volume3'),
               (KegiatanItemModel.vol_4_1*KegiatanItemModel.vol_4_2).label('volume4'),
               KegiatanItemModel.hsat_1.label('harga1'),KegiatanItemModel.hsat_2.label('harga2'),
               KegiatanItemModel.hsat_3.label('harga3'),KegiatanItemModel.hsat_4.label('harga4'),
               KegiatanItemModel.sat_1_1.label('satuan11'),KegiatanItemModel.sat_1_2.label('satuan12'),
               KegiatanItemModel.sat_2_1.label('satuan21'),KegiatanItemModel.sat_2_2.label('satuan22'),
               KegiatanItemModel.sat_3_1.label('satuan31'),KegiatanItemModel.sat_3_2.label('satuan32'),
               KegiatanItemModel.sat_4_1.label('satuan41'),KegiatanItemModel.sat_4_2.label('satuan42'))\
               .filter(KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                   KegiatanItemModel.rekening_id==RekeningModel.id,
                   KegiatanItemModel.rekening_id==row.rekening_id,
                   KegiatanSubModel.tahun_id==row.tahun,
                   KegiatanSubModel.unit_id==row.unit_id)\
               .order_by(KegiatanItemModel.kode)
            
            for row4 in rowitem :
                xml_d = ET.SubElement(xml_a,"item")
                ET.SubElement(xml_d, "item_kd").text = row4.item_kd
                ET.SubElement(xml_d, "item_nm").text = row4.item_nm
                ET.SubElement(xml_d, "volume1").text = unicode(row4.volume1)
                ET.SubElement(xml_d, "volume2").text = unicode(row4.volume2)
                ET.SubElement(xml_d, "volume3").text = unicode(row4.volume3)
                ET.SubElement(xml_d, "volume4").text = unicode(row4.volume4)
                ET.SubElement(xml_d, "harga1").text = unicode(row4.harga1)
                ET.SubElement(xml_d, "harga2").text = unicode(row4.harga2)
                ET.SubElement(xml_d, "harga3").text = unicode(row4.harga3)
                ET.SubElement(xml_d, "harga4").text = unicode(row4.harga4)
                ET.SubElement(xml_d, "satuan11").text = row4.satuan11
                ET.SubElement(xml_d, "satuan12").text = row4.satuan12
                ET.SubElement(xml_d, "satuan21").text = row4.satuan21
                ET.SubElement(xml_d, "satuan22").text = row4.satuan22
                ET.SubElement(xml_d, "satuan31").text = row4.satuan31
                ET.SubElement(xml_d, "satuan32").text = row4.satuan32
                ET.SubElement(xml_d, "satuan41").text = row4.satuan41
                ET.SubElement(xml_d, "satuan42").text = row4.satuan42
                
        return self.root

class r503Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r503Generator, self).__init__()
        self.reportname = get_rpath('apbd/R5003.jrxml')
        self.xpath = '/apbd/perda/lamp4'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        xml_a  =  ET.SubElement(self.root, 'perda')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'lamp4')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_greeting, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "program_kd").text = row.program_kd
            ET.SubElement(xml_greeting, "program_nm").text = row.program_nm
            ET.SubElement(xml_greeting, "kegiatan_kd").text = row.kegiatan_kd
            ET.SubElement(xml_greeting, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_greeting, "pegawai1").text = unicode(row.pegawai1)
            ET.SubElement(xml_greeting, "jasa1").text = unicode(row.jasa1)
            ET.SubElement(xml_greeting, "modal1").text = unicode(row.modal1)
            ET.SubElement(xml_greeting, "pegawai2").text = unicode(row.pegawai2)
            ET.SubElement(xml_greeting, "jasa2").text = unicode(row.jasa2)
            ET.SubElement(xml_greeting, "modal2").text = unicode(row.modal2)
        return self.root

class r504Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r504Generator, self).__init__()
        self.reportname = get_rpath('apbd/R5004.jrxml')
        self.xpath = '/apbd/perda/lamp5'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        xml_a  =  ET.SubElement(self.root, 'perda')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'lamp5')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_greeting, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "program_kd").text = row.program_kd
            ET.SubElement(xml_greeting, "program_nm").text = row.program_nm
            ET.SubElement(xml_greeting, "kegiatan_kd").text = row.kegiatan_kd
            ET.SubElement(xml_greeting, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_greeting, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_greeting, "jumlah3").text = unicode(row.jumlah3)
            ET.SubElement(xml_greeting, "jumlah4").text = unicode(row.jumlah4)
            """ET.SubElement(xml_greeting, "tahun").text = unicode(row.kegiatan_sub.tahun_id)
            ET.SubElement(xml_greeting, "urusan_kd").text = row.kegiatan_sub.kegiatans.programs.urusans.kode
            ET.SubElement(xml_greeting, "urusan_nm").text = row.kegiatan_sub.kegiatans.programs.urusans.nama
            ET.SubElement(xml_greeting, "unit_kd").text = row.kegiatan_sub.units.kode
            ET.SubElement(xml_greeting, "unit_nm").text = row.kegiatan_sub.units.nama
            ET.SubElement(xml_greeting, "program_kd").text = row.kegiatan_sub.kegiatans.programs.kode
            ET.SubElement(xml_greeting, "program_nm").text = row.kegiatan_sub.kegiatans.programs.nama
            ET.SubElement(xml_greeting, "kegiatan_kd").text = row.kegiatan_sub.kegiatans.kode
            ET.SubElement(xml_greeting, "kegiatan_nm").text = row.kegiatan_sub.kegiatans.nama
            ET.SubElement(xml_greeting, "rek_kd").text = unicode(row.rekenings.kode)
            ET.SubElement(xml_greeting, "jumlah1").text = unicode(row.vol_1_1*row.vol_1_2*row.hsat_1)
            ET.SubElement(xml_greeting, "jumlah2").text = unicode(row.vol_2_1*row.vol_2_2*row.hsat_2)
            ET.SubElement(xml_greeting, "jumlah3").text = unicode(row.vol_3_1*row.vol_3_2*row.hsat_3)
            ET.SubElement(xml_greeting, "jumlah4").text = unicode(row.vol_4_1*row.vol_4_2*row.hsat_4)
            """
        return self.root

class r521Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r521Generator, self).__init__()
        self.reportname = get_rpath('apbd/R5005.jrxml')
        self.xpath = '/apbd/perbup/lamp1'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        xml_a  =  ET.SubElement(self.root, 'perbup')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'lamp1')
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_greeting, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_greeting, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_greeting, "jumlah3").text = unicode(row.jumlah3)
            ET.SubElement(xml_greeting, "jumlah4").text = unicode(row.jumlah4)
        return self.root

class r5211Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r5211Generator, self).__init__()
        self.reportname = get_rpath('apbd/R50051.jrxml')
        self.xpath = '/apbd/perbup/lamp1'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        xml_a  =  ET.SubElement(self.root, 'perbup')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'lamp1')
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_greeting, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_greeting, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_greeting, "jumlah3").text = unicode(row.jumlah3)
            ET.SubElement(xml_greeting, "jumlah4").text = unicode(row.jumlah4)
        return self.root

class r522Generator(JasperGeneratorWithSubreport):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        self.mainreport = get_rpath('apbd/R5006.jrxml')
        self.subreportlist = []
        self.subreportlist.append(get_rpath('apbd/R5006_subreport1.jrxml'))
        self.subreportlist.append(get_rpath('apbd/R5006_subreport2.jrxml'))
        self.subreportlist.append(get_rpath('apbd/R5006_subreport3.jrxml'))
        #self.subreportlist.append(get_rpath('apbd/R5002_subreport2_subreport1.jrxml'))
        print self.mainreport,self.subreportlist
        self.xpath = '/apbd/kegiatan'

        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'kegiatan')
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_id").text = unicode(row.unit_id)
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "program_kd").text = row.program_kd
            ET.SubElement(xml_a, "program_nm").text = row.program_nm
            ET.SubElement(xml_a, "kegiatan_kd").text = row.kegiatan_kd
            ET.SubElement(xml_a, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_a, "lokasi").text = row.lokasi
            ET.SubElement(xml_a, "sdana").text = row.sdana
            ET.SubElement(xml_a, "jenis").text = unicode(row.jenis)
            ET.SubElement(xml_a, "kegiatan_id").text = unicode(row.kegiatan_id)
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.kegiatan_sub_id)
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "rekening_id").text = unicode(row.rekening_id)
            ET.SubElement(xml_a, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_a, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_a, "jumlah3").text = unicode(row.jumlah3)
            ET.SubElement(xml_a, "jumlah4").text = unicode(row.jumlah4)
            
            rows = DBSession.query(KegiatanIndikatorModel)\
              .filter(KegiatanIndikatorModel.kegitan_sub_id==row.kegiatan_sub_id,
              KegiatanIndikatorModel.tipe==4)\
              .order_by(KegiatanIndikatorModel.tipe,KegiatanIndikatorModel.no_urut)
            for row2 in rows :
                xml_b = ET.SubElement(xml_a, "indikator")
                ET.SubElement(xml_b, "tipe").text =unicode(row2.tipe)
                ET.SubElement(xml_b, "no_urut").text =unicode(row2.no_urut)
                ET.SubElement(xml_b, "tolok_ukur_1").text =row2.tolok_ukur_2
                ET.SubElement(xml_b, "volume_1").text =unicode(row2.volume_2)
                ET.SubElement(xml_b, "satuan_1").text =row2.satuan_2
            
            rowhkm = DBSession.query(DasarHukumModel.no_urut,DasarHukumModel.nama)\
               .filter(DasarHukumModel.rekening_id==row.rekening_id)\
               .order_by(DasarHukumModel.no_urut)
                
            for row3 in rowhkm :
                xml_c = ET.SubElement(xml_a, "hukum")
                ET.SubElement(xml_c, "no_urut").text =unicode(row3.no_urut)
                ET.SubElement(xml_c, "uraian").text =row3.nama
                #print "XXXXX"+row3.nama

            rowitem = DBSession.query(KegiatanItemModel.kode.label('item_kd'), KegiatanItemModel.nama.label('item_nm'),
               (KegiatanItemModel.vol_1_1*KegiatanItemModel.vol_1_2).label('volume1'),
               (KegiatanItemModel.vol_2_1*KegiatanItemModel.vol_2_2).label('volume2'),
               (KegiatanItemModel.vol_3_1*KegiatanItemModel.vol_3_2).label('volume3'),
               (KegiatanItemModel.vol_4_1*KegiatanItemModel.vol_4_2).label('volume4'),
               KegiatanItemModel.hsat_1.label('harga1'),KegiatanItemModel.hsat_2.label('harga2'),
               KegiatanItemModel.hsat_3.label('harga3'),KegiatanItemModel.hsat_4.label('harga4'),
               KegiatanItemModel.sat_1_1.label('satuan11'),KegiatanItemModel.sat_1_2.label('satuan12'),
               KegiatanItemModel.sat_2_1.label('satuan21'),KegiatanItemModel.sat_2_2.label('satuan22'),
               KegiatanItemModel.sat_3_1.label('satuan31'),KegiatanItemModel.sat_3_2.label('satuan32'),
               KegiatanItemModel.sat_4_1.label('satuan41'),KegiatanItemModel.sat_4_2.label('satuan42'))\
               .filter(KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                   KegiatanItemModel.rekening_id==RekeningModel.id,
                   KegiatanItemModel.rekening_id==row.rekening_id,
                   KegiatanSubModel.tahun_id==row.tahun,
                   KegiatanSubModel.unit_id==row.unit_id)\
               .order_by(KegiatanItemModel.kode)
            
            for row4 in rowitem :
                xml_d = ET.SubElement(xml_a,"item")
                ET.SubElement(xml_d, "item_kd").text = row4.item_kd
                ET.SubElement(xml_d, "item_nm").text = row4.item_nm
                ET.SubElement(xml_d, "volume1").text = unicode(row4.volume1)
                ET.SubElement(xml_d, "volume2").text = unicode(row4.volume2)
                ET.SubElement(xml_d, "volume3").text = unicode(row4.volume3)
                ET.SubElement(xml_d, "volume4").text = unicode(row4.volume4)
                ET.SubElement(xml_d, "harga1").text = unicode(row4.harga1)
                ET.SubElement(xml_d, "harga2").text = unicode(row4.harga2)
                ET.SubElement(xml_d, "harga3").text = unicode(row4.harga3)
                ET.SubElement(xml_d, "harga4").text = unicode(row4.harga4)
                ET.SubElement(xml_d, "satuan11").text = row4.satuan11
                ET.SubElement(xml_d, "satuan12").text = row4.satuan12
                ET.SubElement(xml_d, "satuan21").text = row4.satuan21
                ET.SubElement(xml_d, "satuan22").text = row4.satuan22
                ET.SubElement(xml_d, "satuan31").text = row4.satuan31
                ET.SubElement(xml_d, "satuan32").text = row4.satuan32
                ET.SubElement(xml_d, "satuan41").text = row4.satuan41
                ET.SubElement(xml_d, "satuan42").text = row4.satuan42
                
        return self.root

class ViewAnggaranRAPBD(BaseViews):
    @view_config(route_name="anggaran_r500", renderer="osipkd:templates/apbd/anggaran/r500.pt")
    def anggaran_r500(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas,)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="anggaran_r500_act")
    def anggaran_r500_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            if url_dict['act']=='r511' and self.is_akses_mod('read'):

                subq1 = DBSession.query(RekeningModel.kode.label('subrek_kd'),RekeningModel.nama.label('subrek_nm'),
                    KegiatanSubModel.tahun_id,
                    (KegiatanItemModel.vol_1_1* KegiatanItemModel.vol_1_2*KegiatanItemModel.hsat_1).label('jml1'),
                    (KegiatanItemModel.vol_2_1* KegiatanItemModel.vol_2_2*KegiatanItemModel.hsat_2).label('jml2'),
                    (KegiatanItemModel.vol_3_1* KegiatanItemModel.vol_3_2*KegiatanItemModel.hsat_3).label('jml3'),
                    (KegiatanItemModel.vol_4_1* KegiatanItemModel.vol_4_2*KegiatanItemModel.hsat_4).label('jml4'))\
                    .filter(KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                            KegiatanItemModel.rekening_id==RekeningModel.id,
                            KegiatanSubModel.tahun_id==self.tahun)\
                    .subquery()

                query = DBSession.query(RekeningModel.kode.label('rek_kd'), RekeningModel.nama.label('rek_nm'),
                    RekeningModel.level_id, RekeningModel.defsign, subq1.c.tahun_id, 
                    func.sum(subq1.c.jml1).label('jumlah1'),func.sum(subq1.c.jml2).label('jumlah2'),
                    func.sum(subq1.c.jml3).label('jumlah3'),func.sum(subq1.c.jml4).label('jumlah4'))\
                    .filter(RekeningModel.kode==func.left(subq1.c.subrek_kd, func.length(RekeningModel.kode)),
                    RekeningModel.level_id<3)\
                    .group_by(RekeningModel.kode, RekeningModel.nama,
                    RekeningModel.level_id, RekeningModel.defsign, subq1.c.tahun_id)\
                    .order_by(RekeningModel.kode).all()                    

                generator = r500Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
               
            elif url_dict['act']=='r5111' and self.is_akses_mod('read'):

                subq1 = DBSession.query(RekeningModel.kode.label('subrek_kd'),RekeningModel.nama.label('subrek_nm'),
                    KegiatanSubModel.tahun_id,
                    (KegiatanItemModel.vol_1_1* KegiatanItemModel.vol_1_2*KegiatanItemModel.hsat_1).label('jml1'),
                    (KegiatanItemModel.vol_2_1* KegiatanItemModel.vol_2_2*KegiatanItemModel.hsat_2).label('jml2'),
                    (KegiatanItemModel.vol_3_1* KegiatanItemModel.vol_3_2*KegiatanItemModel.hsat_3).label('jml3'),
                    (KegiatanItemModel.vol_4_1* KegiatanItemModel.vol_4_2*KegiatanItemModel.hsat_4).label('jml4'))\
                    .filter(KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                            KegiatanItemModel.rekening_id==RekeningModel.id,
                            KegiatanSubModel.tahun_id==self.tahun)\
                    .subquery()

                query = DBSession.query(RekeningModel.kode.label('rek_kd'), RekeningModel.nama.label('rek_nm'),
                    RekeningModel.level_id, RekeningModel.defsign, subq1.c.tahun_id, 
                    func.sum(subq1.c.jml1).label('jumlah1'),func.sum(subq1.c.jml2).label('jumlah2'),
                    func.sum(subq1.c.jml3).label('jumlah3'),func.sum(subq1.c.jml4).label('jumlah4'))\
                    .filter(RekeningModel.kode==func.left(subq1.c.subrek_kd, func.length(RekeningModel.kode)))\
                    .group_by(RekeningModel.kode, RekeningModel.nama,
                    RekeningModel.level_id, RekeningModel.defsign, subq1.c.tahun_id)\
                    .order_by(RekeningModel.kode).all()                    

                generator = r5001Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response

            elif url_dict['act']=='r512' and self.is_akses_mod('read'):

                query = DBSession.query(KegiatanSubModel.tahun_id, Urusan.kode.label('urusan_kd'),
                   Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                   KegiatanSubModel.kegiatan_id.label('jenis_kd'), 
                   (KegiatanItemModel.vol_1_1*KegiatanItemModel.vol_1_2*KegiatanItemModel.hsat_1).label('jumlah1'),
                   (KegiatanItemModel.vol_2_1*KegiatanItemModel.vol_2_2*KegiatanItemModel.hsat_2).label('jumlah2'),
                   (KegiatanItemModel.vol_3_1*KegiatanItemModel.vol_3_2*KegiatanItemModel.hsat_3).label('jumlah3'),
                   (KegiatanItemModel.vol_4_1*KegiatanItemModel.vol_4_2*KegiatanItemModel.hsat_4).label('jumlah4'))\
                   .filter(KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                       KegiatanSubModel.kegiatan_id==KegiatanModel.id, KegiatanModel.program_id==ProgramModel.id,
                       ProgramModel.urusan_id==Urusan.id, KegiatanSubModel.unit_id==Unit.id,
                       KegiatanSubModel.tahun_id==self.session['tahun'])      

                """query = DBSession.query(KegiatanItemModel)\
                    .filter(KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                    KegiatanSubModel.tahun_id==self.session['tahun'])      
                """
                generator = r501Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response

            elif url_dict['act']=='r513' and self.is_akses_mod('read'):
                
                subq = DBSession.query(RekeningModel.kode.label('subrek_kd'),RekeningModel.nama.label('subrek_nm'),
                    (KegiatanItemModel.vol_1_1* KegiatanItemModel.vol_1_2*KegiatanItemModel.hsat_1).label('jml1'),
                    (KegiatanItemModel.vol_2_1* KegiatanItemModel.vol_2_2*KegiatanItemModel.hsat_2).label('jml2'),
                    (KegiatanItemModel.vol_3_1* KegiatanItemModel.vol_3_2*KegiatanItemModel.hsat_3).label('jml3'),
                    (KegiatanItemModel.vol_4_1* KegiatanItemModel.vol_4_2*KegiatanItemModel.hsat_4).label('jml4'),
                    Unit.id.label('unit_id'),Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                    Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), 
                    KegiatanSubModel.tahun_id.label('tahun'), KegiatanSubModel.lokasi, KegiatanSubModel.sdana, 
                    ProgramModel.kode.label('program_kd'), ProgramModel.nama.label('program_nm'), 
                    KegiatanModel.kode.label('kegiatan_kd'), KegiatanModel.nama.label('kegiatan_nm'),
                    KegiatanItemModel.kegiatan_sub_id, KegiatanSubModel.kegiatan_id )\
                    .filter(KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                            KegiatanItemModel.rekening_id==RekeningModel.id,
                            KegiatanSubModel.unit_id==Unit.id,
                            Unit.urusan_id==Urusan.id,
                            KegiatanSubModel.kegiatan_id==KegiatanModel.id,
                            KegiatanModel.program_id==ProgramModel.id,
                            KegiatanSubModel.tahun_id==self.session['tahun'],
                            KegiatanSubModel.unit_id==self.request.params['id'])\
                    .subquery()
                    
                query = DBSession.query(RekeningModel.kode.label('rek_kd'), RekeningModel.nama.label('rek_nm'),
                    RekeningModel.level_id, RekeningModel.defsign, RekeningModel.id.label('rekening_id'),
                    subq.c.unit_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.urusan_kd, subq.c.urusan_nm, 
                    subq.c.tahun, subq.c.lokasi, subq.c.sdana,
                    subq.c.program_kd, subq.c.program_nm, subq.c.kegiatan_kd, subq.c.kegiatan_nm, 
                    subq.c.kegiatan_sub_id,  subq.c.kegiatan_id,
                    case([(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='10'),1),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='21'),2),
                    (and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='31'),4),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='32'),5)], 
                    else_=3).label('jenis'),                    
                    func.sum(subq.c.jml1).label('jumlah1'),func.sum(subq.c.jml2).label('jumlah2'),
                    func.sum(subq.c.jml3).label('jumlah3'),func.sum(subq.c.jml4).label('jumlah4'))\
                    .filter(RekeningModel.kode==func.left(subq.c.subrek_kd, func.length(RekeningModel.kode)))\
                    .group_by(RekeningModel.kode, RekeningModel.nama,
                    RekeningModel.level_id, RekeningModel.defsign, RekeningModel.id, 
                    subq.c.unit_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.urusan_kd, subq.c.urusan_nm, subq.c.tahun,
                    subq.c.lokasi, subq.c.sdana, subq.c.program_kd, subq.c.program_nm, subq.c.kegiatan_kd, subq.c.kegiatan_nm,
                    subq.c.kegiatan_sub_id, subq.c.kegiatan_id,
                    case([(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='10'),1),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='21'),2),
                    (and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='31'),4),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='32'),5)], 
                    else_=3))\
                    .order_by(case([(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='10'),1),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='21'),2),
                    (and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='31'),4),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='32'),5)], 
                    else_=3),subq.c.urusan_kd, subq.c.unit_kd, subq.c.program_kd, subq.c.kegiatan_kd, RekeningModel.kode).all() 
                    
                generator = r502Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
                
            elif url_dict['act']=='r514' and self.is_akses_mod('read'):

                query = DBSession.query(KegiatanSubModel.tahun_id, Urusan.kode.label('urusan_kd'),
                   Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                   ProgramModel.kode.label('program_kd'), ProgramModel.nama.label('program_nm'), 
                   KegiatanModel.kode.label('kegiatan_kd'), KegiatanModel.nama.label('kegiatan_nm'),
                   func.sum(case([(func.substr(RekeningModel.kode,0,6)=='5.2.1',
                   KegiatanItemModel.vol_1_1*KegiatanItemModel.vol_1_2*KegiatanItemModel.hsat_1)], else_=0)).label('pegawai1'),
                   func.sum(case([(func.substr(RekeningModel.kode,0,6)=='5.2.2',
                   KegiatanItemModel.vol_1_1*KegiatanItemModel.vol_1_2*KegiatanItemModel.hsat_1)], else_=0)).label('jasa1'),
                   func.sum(case([(func.substr(RekeningModel.kode,0,6)=='5.2.3',
                   KegiatanItemModel.vol_1_1*KegiatanItemModel.vol_1_2*KegiatanItemModel.hsat_1)], else_=0)).label('modal1'),
                   func.sum(case([(func.substr(RekeningModel.kode,0,6)=='5.2.1',
                   KegiatanItemModel.vol_2_1*KegiatanItemModel.vol_2_2*KegiatanItemModel.hsat_2)], else_=0)).label('pegawai2'),
                   func.sum(case([(func.substr(RekeningModel.kode,0,6)=='5.2.2',
                   KegiatanItemModel.vol_2_1*KegiatanItemModel.vol_2_2*KegiatanItemModel.hsat_2)], else_=0)).label('jasa2'),
                   func.sum(case([(func.substr(RekeningModel.kode,0,6)=='5.2.3',
                   KegiatanItemModel.vol_2_1*KegiatanItemModel.vol_2_2*KegiatanItemModel.hsat_2)], else_=0)).label('modal2'))\
                   .filter(KegiatanItemModel.rekening_id==RekeningModel.id, KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                    KegiatanSubModel.unit_id==Unit.id, Unit.urusan_id==Urusan.id, 
                    KegiatanSubModel.kegiatan_id==KegiatanModel.id,
                    KegiatanModel.program_id==ProgramModel.id,
                    KegiatanSubModel.tahun_id==self.session['tahun'],
                    KegiatanSubModel.kegiatan_id>6)\
                   .group_by(KegiatanSubModel.tahun_id, Urusan.kode, Urusan.nama, 
                   Unit.kode, Unit.nama, ProgramModel.kode, ProgramModel.nama, 
                   KegiatanModel.kode, KegiatanModel.nama)                    
                    
                """query = DBSession.query(KegiatanItemModel)\
                    .filter(KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                    KegiatanSubModel.tahun_id==self.session['tahun'],
                    KegiatanSubModel.kegiatan_id>6)      
                """

                generator = r503Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response

            elif url_dict['act']=='r515' and self.is_akses_mod('read'):

                query = DBSession.query(KegiatanSubModel.tahun_id, Urusan.kode.label('urusan_kd'),
                   Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                   ProgramModel.kode.label('program_kd'), ProgramModel.nama.label('program_nm'),
                   KegiatanModel.kode.label('kegiatan_kd'), KegiatanModel.nama.label('kegiatan_nm'),
                   RekeningModel.kode.label('rek_kd'),
                   (KegiatanItemModel.vol_1_1*KegiatanItemModel.vol_1_2*KegiatanItemModel.hsat_1).label('jumlah1'),
                   (KegiatanItemModel.vol_2_1*KegiatanItemModel.vol_2_2*KegiatanItemModel.hsat_2).label('jumlah2'),
                   (KegiatanItemModel.vol_3_1*KegiatanItemModel.vol_3_2*KegiatanItemModel.hsat_3).label('jumlah3'),
                   (KegiatanItemModel.vol_4_1*KegiatanItemModel.vol_4_2*KegiatanItemModel.hsat_4).label('jumlah4'))\
                   .filter(KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                       KegiatanSubModel.kegiatan_id==KegiatanModel.id, KegiatanModel.program_id==ProgramModel.id,
                       ProgramModel.urusan_id==Urusan.id, KegiatanSubModel.unit_id==Unit.id, 
                       KegiatanItemModel.rekening_id==RekeningModel.id,
                       KegiatanSubModel.tahun_id==self.session['tahun'])      
                """query = DBSession.query(KegiatanItemModel)\
                    .filter(KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                    RekeningModel.id==KegiatanItemModel.rekening_id,
                    KegiatanSubModel.tahun_id==self.session['tahun'])      
                """
                generator = r504Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response

            elif url_dict['act']=='r521' and self.is_akses_mod('read'):

                subq1 = DBSession.query(RekeningModel.kode.label('subrek_kd'),RekeningModel.nama.label('subrek_nm'),
                    KegiatanSubModel.tahun_id,
                    (KegiatanItemModel.vol_1_1* KegiatanItemModel.vol_1_2*KegiatanItemModel.hsat_1).label('jml1'),
                    (KegiatanItemModel.vol_2_1* KegiatanItemModel.vol_2_2*KegiatanItemModel.hsat_2).label('jml2'),
                    (KegiatanItemModel.vol_3_1* KegiatanItemModel.vol_3_2*KegiatanItemModel.hsat_3).label('jml3'),
                    (KegiatanItemModel.vol_4_1* KegiatanItemModel.vol_4_2*KegiatanItemModel.hsat_4).label('jml4'))\
                    .filter(KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                            KegiatanItemModel.rekening_id==RekeningModel.id,
                            KegiatanSubModel.tahun_id==self.tahun)\
                    .subquery()

                query = DBSession.query(RekeningModel.kode.label('rek_kd'), RekeningModel.nama.label('rek_nm'),
                    RekeningModel.level_id, RekeningModel.defsign, subq1.c.tahun_id, 
                    func.sum(subq1.c.jml1).label('jumlah1'),func.sum(subq1.c.jml2).label('jumlah2'),
                    func.sum(subq1.c.jml3).label('jumlah3'),func.sum(subq1.c.jml4).label('jumlah4'))\
                    .filter(RekeningModel.kode==func.left(subq1.c.subrek_kd, func.length(RekeningModel.kode)),
                    RekeningModel.level_id<3)\
                    .group_by(RekeningModel.kode, RekeningModel.nama,
                    RekeningModel.level_id, RekeningModel.defsign, subq1.c.tahun_id)\
                    .order_by(RekeningModel.kode).all()                    

                generator = r521Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response

            elif url_dict['act']=='r5211' and self.is_akses_mod('read'):

                subq1 = DBSession.query(RekeningModel.kode.label('subrek_kd'),RekeningModel.nama.label('subrek_nm'),
                    KegiatanSubModel.tahun_id,
                    (KegiatanItemModel.vol_1_1* KegiatanItemModel.vol_1_2*KegiatanItemModel.hsat_1).label('jml1'),
                    (KegiatanItemModel.vol_2_1* KegiatanItemModel.vol_2_2*KegiatanItemModel.hsat_2).label('jml2'),
                    (KegiatanItemModel.vol_3_1* KegiatanItemModel.vol_3_2*KegiatanItemModel.hsat_3).label('jml3'),
                    (KegiatanItemModel.vol_4_1* KegiatanItemModel.vol_4_2*KegiatanItemModel.hsat_4).label('jml4'))\
                    .filter(KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                            KegiatanItemModel.rekening_id==RekeningModel.id,
                            KegiatanSubModel.tahun_id==self.tahun)\
                    .subquery()

                query = DBSession.query(RekeningModel.kode.label('rek_kd'), RekeningModel.nama.label('rek_nm'),
                    RekeningModel.level_id, RekeningModel.defsign, subq1.c.tahun_id, 
                    func.sum(subq1.c.jml1).label('jumlah1'),func.sum(subq1.c.jml2).label('jumlah2'),
                    func.sum(subq1.c.jml3).label('jumlah3'),func.sum(subq1.c.jml4).label('jumlah4'))\
                    .filter(RekeningModel.kode==func.left(subq1.c.subrek_kd, func.length(RekeningModel.kode)))\
                    .group_by(RekeningModel.kode, RekeningModel.nama,
                    RekeningModel.level_id, RekeningModel.defsign, subq1.c.tahun_id)\
                    .order_by(RekeningModel.kode).all()                    

                generator = r5211Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response

            elif url_dict['act']=='r522' and self.is_akses_mod('read'):
                
                subq = DBSession.query(RekeningModel.kode.label('subrek_kd'),RekeningModel.nama.label('subrek_nm'),
                    (KegiatanItemModel.vol_1_1* KegiatanItemModel.vol_1_2*KegiatanItemModel.hsat_1).label('jml1'),
                    (KegiatanItemModel.vol_2_1* KegiatanItemModel.vol_2_2*KegiatanItemModel.hsat_2).label('jml2'),
                    (KegiatanItemModel.vol_3_1* KegiatanItemModel.vol_3_2*KegiatanItemModel.hsat_3).label('jml3'),
                    (KegiatanItemModel.vol_4_1* KegiatanItemModel.vol_4_2*KegiatanItemModel.hsat_4).label('jml4'),
                    Unit.id.label('unit_id'),Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                    Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), 
                    KegiatanSubModel.tahun_id.label('tahun'), KegiatanSubModel.lokasi, KegiatanSubModel.sdana, 
                    ProgramModel.kode.label('program_kd'), ProgramModel.nama.label('program_nm'), 
                    KegiatanModel.kode.label('kegiatan_kd'), KegiatanModel.nama.label('kegiatan_nm'),
                    KegiatanItemModel.kegiatan_sub_id, KegiatanSubModel.kegiatan_id )\
                    .filter(KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                            KegiatanItemModel.rekening_id==RekeningModel.id,
                            KegiatanSubModel.unit_id==Unit.id,
                            Unit.urusan_id==Urusan.id,
                            KegiatanSubModel.kegiatan_id==KegiatanModel.id,
                            KegiatanModel.program_id==ProgramModel.id,
                            KegiatanSubModel.tahun_id==self.session['tahun'],
                            KegiatanSubModel.unit_id==self.request.params['id'])\
                    .subquery()
                    
                query = DBSession.query(RekeningModel.kode.label('rek_kd'), RekeningModel.nama.label('rek_nm'),
                    RekeningModel.level_id, RekeningModel.defsign, RekeningModel.id.label('rekening_id'),
                    subq.c.unit_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.urusan_kd, subq.c.urusan_nm, 
                    subq.c.tahun, subq.c.lokasi, subq.c.sdana,
                    subq.c.program_kd, subq.c.program_nm, subq.c.kegiatan_kd, subq.c.kegiatan_nm, 
                    subq.c.kegiatan_sub_id,  subq.c.kegiatan_id,
                    case([(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='10'),1),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='21'),2),
                    (and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='31'),4),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='32'),5)], 
                    else_=3).label('jenis'),                    
                    func.sum(subq.c.jml1).label('jumlah1'),func.sum(subq.c.jml2).label('jumlah2'),
                    func.sum(subq.c.jml3).label('jumlah3'),func.sum(subq.c.jml4).label('jumlah4'))\
                    .filter(RekeningModel.kode==func.left(subq.c.subrek_kd, func.length(RekeningModel.kode)))\
                    .group_by(RekeningModel.kode, RekeningModel.nama,
                    RekeningModel.level_id, RekeningModel.defsign, RekeningModel.id, 
                    subq.c.unit_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.urusan_kd, subq.c.urusan_nm, subq.c.tahun,
                    subq.c.lokasi, subq.c.sdana, subq.c.program_kd, subq.c.program_nm, subq.c.kegiatan_kd, subq.c.kegiatan_nm,
                    subq.c.kegiatan_sub_id, subq.c.kegiatan_id,
                    case([(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='10'),1),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='21'),2),
                    (and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='31'),4),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='32'),5)], 
                    else_=3))\
                    .order_by(case([(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='10'),1),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='21'),2),
                    (and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='31'),4),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='32'),5)], 
                    else_=3),subq.c.urusan_kd, subq.c.unit_kd, subq.c.program_kd, subq.c.kegiatan_kd, RekeningModel.kode).all() 
                    
                generator = r522Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response

