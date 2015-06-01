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
     Urusan, RekeningModel, ProgramModel, KegiatanModel)
from osipkd.models.apbd_tu_models import *
from datetime import datetime
import os
from pyramid.renderers import render_to_response

from anggaran import AnggaranBaseViews
from pyjasper import (JasperGenerator)
from pyjasper import (JasperGeneratorWithSubreport)
import xml.etree.ElementTree as ET
from pyramid.path import AssetResolver

def get_rpath(filename):
    a = AssetResolver('osipkd')
    resolver = a.resolve(''.join(['reports/',filename]))
    return resolver.abspath()
    
#KETETAPAN-Generator
class b102r001Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b102r001Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuskpd/R102001.jrxml')
        self.xpath = '/apbd/ketetapan'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'ketetapan')
            ET.SubElement(xml_greeting, "tahun_id").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "unit_nm").text = row.units.nama
            ET.SubElement(xml_greeting, "rek_kd").text = row.rekenings.kode
            ET.SubElement(xml_greeting, "rek_nm").text = row.rekenings.nama
            ET.SubElement(xml_greeting, "nama").text = row.nama
            ET.SubElement(xml_greeting, "tgl_ketetapan").text = unicode(row.tgl_ketetapan)
            ET.SubElement(xml_greeting, "jumlah").text = unicode(row.jumlah)
        return self.root

#TBP-Generator
class b102r002Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b102r002Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuskpd/R102002.jrxml')
        self.xpath = '/apbd/arinvoice'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'arinvoice')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "arinvoice_id").text = unicode(row.arinvoice_id)
            ET.SubElement(xml_greeting, "kode").text = row.kode
            ET.SubElement(xml_greeting, "arinvoice_nm").text = row.arinvoice_nm
            ET.SubElement(xml_greeting, "tgl_terima").text = unicode(row.tgl_terima)
            ET.SubElement(xml_greeting, "tgl_validasi").text = unicode(row.tgl_validasi)
            ET.SubElement(xml_greeting, "bendahara_nm").text = row.bendahara_nm
            ET.SubElement(xml_greeting, "penyetor").text = row.penyetor
            ET.SubElement(xml_greeting, "alamat").text = row.alamat
            ET.SubElement(xml_greeting, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_greeting, "nilai").text = unicode(row.nilai)
        return self.root
       
#STS-Generator
class b102r003Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b102r003Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuskpd/R102003.jrxml')
        self.xpath = '/apbd/sts'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'sts')
            ET.SubElement(xml_greeting, "tahun_id").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "unit_nm").text = row.units.nama
            ET.SubElement(xml_greeting, "id").text = unicode(row.id)
            ET.SubElement(xml_greeting, "kode").text = row.kode
            ET.SubElement(xml_greeting, "nama").text = row.nama
            ET.SubElement(xml_greeting, "jenis").text = unicode(row.jenis)
            ET.SubElement(xml_greeting, "tgl_sts").text = unicode(row.tgl_sts)
            ET.SubElement(xml_greeting, "tgl_validasi").text = unicode(row.tgl_validasi)
            ET.SubElement(xml_greeting, "nominal").text = unicode(row.nominal)
            ET.SubElement(xml_greeting, "bank_nama").text = row.bank_nama
            ET.SubElement(xml_greeting, "bank_account").text = row.bank_account
        return self.root

class b103r001Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b103r001Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuskpd/R103001.jrxml')
        self.xpath = '/apbd/invoice'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""

        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'invoice')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "jenis").text = row.jenis
            ET.SubElement(xml_greeting, "invoice_id").text = unicode(row.invoice_id)
            ET.SubElement(xml_greeting, "invoice_nm").text = row.invoice_nm
            ET.SubElement(xml_greeting, "tgl_invoice").text = unicode(row.tgl_invoice)
            ET.SubElement(xml_greeting, "ap_nomor").text = row.ap_nomor
            ET.SubElement(xml_greeting, "ap_nama").text = row.ap_nama
            ET.SubElement(xml_greeting, "ap_rekening").text = row.ap_rekening
            ET.SubElement(xml_greeting, "ap_npwp").text = row.ap_npwp
            ET.SubElement(xml_greeting, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_greeting, "nilai").text = unicode(row.nilai)
        return self.root

class b103r002Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b103r002Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuskpd/R103002.jrxml')
        self.xpath = '/apbd/spp'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spp')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_greeting, "no_perkdh").text = row.no_perkdh
            ET.SubElement(xml_greeting, "tgl_perkdh").text = unicode(row.tgl_perkdh)
            ET.SubElement(xml_greeting, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_greeting, "spp_kd").text = row.spp_kd
            ET.SubElement(xml_greeting, "nama").text = row.nama
            ET.SubElement(xml_greeting, "bank_nama").text = row.bank_nama
            ET.SubElement(xml_greeting, "bank_account").text = row.bank_account
            ET.SubElement(xml_greeting, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_greeting, "jenis").text = row.jenis
            ET.SubElement(xml_greeting, "nominal").text = unicode(row.nominal)
            ET.SubElement(xml_greeting, "spd_kd").text = row.spd_kd
            ET.SubElement(xml_greeting, "tgl_spd").text = unicode(row.tgl_spd)
        return self.root

class b103r0021Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b103r0021Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuskpd/R1030021.jrxml')
        self.xpath = '/apbd/spp'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spp')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_greeting, "no_perkdh").text = row.no_perkdh
            ET.SubElement(xml_greeting, "tgl_perkdh").text = unicode(row.tgl_perkdh)
            ET.SubElement(xml_greeting, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_greeting, "spp_kd").text = row.spp_kd
            ET.SubElement(xml_greeting, "nama").text = row.nama
            ET.SubElement(xml_greeting, "bank_nama").text = row.bank_nama
            ET.SubElement(xml_greeting, "bank_account").text = row.bank_account
            ET.SubElement(xml_greeting, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_greeting, "jenis").text = row.jenis
            ET.SubElement(xml_greeting, "nominal").text = unicode(row.nominal)
            ET.SubElement(xml_greeting, "spd_kd").text = row.spd_kd
            ET.SubElement(xml_greeting, "tgl_spd").text = unicode(row.tgl_spd)
        return self.root

class b103r0022Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b103r0022Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuskpd/R1030022.jrxml')
        self.xpath = '/apbd/spp'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spp')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_greeting, "no_perkdh").text = row.no_perkdh
            ET.SubElement(xml_greeting, "tgl_perkdh").text = unicode(row.tgl_perkdh)
            ET.SubElement(xml_greeting, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_greeting, "spp_kd").text = row.spp_kd
            ET.SubElement(xml_greeting, "nama").text = row.nama
            ET.SubElement(xml_greeting, "bank_nama").text = row.bank_nama
            ET.SubElement(xml_greeting, "bank_account").text = row.bank_account
            ET.SubElement(xml_greeting, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_greeting, "jenis").text = row.jenis
            ET.SubElement(xml_greeting, "nominal").text = unicode(row.nominal)
            ET.SubElement(xml_greeting, "spd_kd").text = row.spd_kd
            ET.SubElement(xml_greeting, "tgl_spd").text = unicode(row.tgl_spd)
        return self.root

class b103r0023Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b103r0023Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuskpd/R1030023.jrxml')
        self.xpath = '/apbd/spp'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spp')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_greeting, "no_perkdh").text = row.no_perkdh
            ET.SubElement(xml_greeting, "tgl_perkdh").text = unicode(row.tgl_perkdh)
            ET.SubElement(xml_greeting, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_greeting, "spp_kd").text = row.spp_kd
            ET.SubElement(xml_greeting, "nama").text = row.nama
            ET.SubElement(xml_greeting, "bank_nama").text = row.bank_nama
            ET.SubElement(xml_greeting, "bank_account").text = row.bank_account
            ET.SubElement(xml_greeting, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_greeting, "jenis").text = row.jenis
            ET.SubElement(xml_greeting, "nominal").text = unicode(row.nominal)
            ET.SubElement(xml_greeting, "spd_kd").text = row.spd_kd
            ET.SubElement(xml_greeting, "tgl_spd").text = unicode(row.tgl_spd)
        return self.root

class b103r003Generator(JasperGeneratorWithSubreport):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        self.mainreport = get_rpath('apbd/tuskpd/R103003.jrxml')

        self.subreportlist = []
        self.subreportlist.append(get_rpath('apbd/tuskpd/R103003_subreport1.jrxml'))
        self.subreportlist.append(get_rpath('apbd/tuskpd/R103003_subreport2.jrxml'))
        self.subreportlist.append(get_rpath('apbd/tuskpd/R103003_subreport3.jrxml'))

        self.xpath = '/apbd/spm'
        
        self.root = ET.Element('apbd')

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""

        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spm')
            ET.SubElement(xml_greeting, "spm_id").text = unicode(row.spm_id)
            ET.SubElement(xml_greeting, "spm_kd").text = row.spm_kd
            ET.SubElement(xml_greeting, "spm_nm").text = row.spm_nm
            ET.SubElement(xml_greeting, "spm_tgl").text = unicode(row.spm_tgl)
            ET.SubElement(xml_greeting, "spp_id").text = unicode(row.spp_id)
            ET.SubElement(xml_greeting, "spp_kd").text = row.spp_kd
            ET.SubElement(xml_greeting, "spp_nm").text = row.spp_nm
            ET.SubElement(xml_greeting, "spp_tgl").text = unicode(row.spp_tgl)
            ET.SubElement(xml_greeting, "jenis").text = unicode(row.jenis)
            ET.SubElement(xml_greeting, "bank_nama").text = row.bank_nama
            ET.SubElement(xml_greeting, "bank_account").text = row.bank_account
            ET.SubElement(xml_greeting, "ap_nama").text = row.ap_nama
            ET.SubElement(xml_greeting, "ap_bank").text = row.ap_bank
            ET.SubElement(xml_greeting, "ap_rekening").text = row.ap_rekening
            ET.SubElement(xml_greeting, "ap_npwp").text = row.ap_npwp
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "keg_kd").text = row.keg_kd
            ET.SubElement(xml_greeting, "keg_nm").text = row.keg_nm
            ET.SubElement(xml_greeting, "prg_kd").text = row.prg_kd
            ET.SubElement(xml_greeting, "prg_nm").text = row.prg_nm
            ET.SubElement(xml_greeting, "spd_id").text = unicode(row.spd_id)
            ET.SubElement(xml_greeting, "nilai").text = unicode(row.nilai)
            ET.SubElement(xml_greeting, "ppn").text = unicode(row.ppn)
            ET.SubElement(xml_greeting, "pph").text = unicode(row.pph)
            ET.SubElement(xml_greeting, "potongan").text = unicode(row.potongan)

            rows = DBSession.query(RekeningModel.kode, RekeningModel.nama,
               func.sum(APInvoiceItemModel.nilai).label('jumlah')
               ).filter(RekeningModel.id==KegiatanItemModel.rekening_id, 
               KegiatanItemModel.id==APInvoiceItemModel.kegiatan_item_id,
               SppItemModel.apinvoice_id==APInvoiceItemModel.apinvoice_id,
               SppItemModel.spp_id==row.spp_id, func.substr(RekeningModel.kode,1,1)=='5'
               ).group_by(RekeningModel.kode, RekeningModel.nama
               ).order_by(RekeningModel.kode)
            for row2 in rows :
                xml_a = ET.SubElement(xml_greeting, "rekening")
                ET.SubElement(xml_a, "rek_kd").text =row2.kode
                ET.SubElement(xml_a, "rek_nm").text =row2.nama
                ET.SubElement(xml_a, "jumlah").text =unicode(row2.jumlah)

            rows1 = DBSession.query(RekeningModel.kode, RekeningModel.nama,
               (KegiatanItemModel.vol_4_1* KegiatanItemModel.vol_4_2*KegiatanItemModel.hsat_4).label('jumlah')
               ).filter(RekeningModel.id==KegiatanItemModel.rekening_id, 
               KegiatanItemModel.id==APInvoiceItemModel.kegiatan_item_id,
               SppItemModel.apinvoice_id==APInvoiceItemModel.apinvoice_id,
               SppItemModel.spp_id==row.spp_id, func.substr(RekeningModel.kode,1,1)=='7'
               ).order_by(RekeningModel.kode)
            for row3 in rows1 :
                xml_b = ET.SubElement(xml_greeting, "potongan")
                ET.SubElement(xml_b, "rek_kd").text =row3.kode
                ET.SubElement(xml_b, "rek_nm").text =row3.nama
                ET.SubElement(xml_b, "jumlah").text =unicode(row3.jumlah)

            rows2 = DBSession.query(SpdModel.kode.label('spd_no'), SpdModel.tanggal.label('spd_tgl'),
               func.sum(SpdItemModel.nominal).label('spd_jml')
               ).filter(SpdModel.id==SpdItemModel.spd_id, 
               SpdModel.id==row.spd_id
               ).group_by(SpdModel.kode,SpdModel.tanggal)
            for row4 in rows2 :
                xml_c = ET.SubElement(xml_greeting, "spd")
                ET.SubElement(xml_c, "spd_no").text =row4.spd_no
                ET.SubElement(xml_c, "spd_tgl").text =unicode(row4.spd_tgl)
                ET.SubElement(xml_c, "spd_jml").text =unicode(row4.spd_jml)

        return self.root

class b104r000Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b104r000Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuskpd/R104000.jrxml')
        self.xpath = '/apbd/invoice'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'invoice')
            ET.SubElement(xml_greeting, "tahun_id").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "tgl_invoice").text = unicode(row.tgl_invoice)
            ET.SubElement(xml_greeting, "jenis").text = row.jenis
            ET.SubElement(xml_greeting, "invoice_kd").text = row.invoice_kd
            ET.SubElement(xml_greeting, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "jumlah").text = unicode(row.jumlah)
        return self.root

class b104r1001Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b104r1001Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuskpd/R1041001.jrxml')
        self.xpath = '/apbd/spp'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""

        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spp')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "jenis").text = row.jenis
            ET.SubElement(xml_greeting, "spp_kd").text = row.spp_kd
            ET.SubElement(xml_greeting, "spp_nm").text = row.spp_nm
            ET.SubElement(xml_greeting, "tgl_spp").text = unicode(row.tgl_spp)
            ET.SubElement(xml_greeting, "spm_kd").text = row.spm_kd
            ET.SubElement(xml_greeting, "tgl_spm").text = unicode(row.tgl_spm)
            ET.SubElement(xml_greeting, "sp2d_kd").text = row.sp2d_kd
            ET.SubElement(xml_greeting, "tgl_sp2d").text = unicode(row.tgl_sp2d)
            ET.SubElement(xml_greeting, "nominal").text = unicode(row.nominal)
        return self.root

class b104r1002Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b104r1002Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuskpd/R1041002.jrxml')
        self.xpath = '/apbd/spp'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""

        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spp')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "tgl_spp").text = unicode(row.tgl_spp)
            ET.SubElement(xml_greeting, "spp_kd").text = row.spp_kd
            ET.SubElement(xml_greeting, "spp_nm").text = row.spp_nm
            ET.SubElement(xml_greeting, "UP").text = unicode(row.UP)
            ET.SubElement(xml_greeting, "GU").text = unicode(row.GU)
            ET.SubElement(xml_greeting, "TU").text = unicode(row.TU)
            ET.SubElement(xml_greeting, "LS_GJ").text = unicode(row.LS_GJ)
            ET.SubElement(xml_greeting, "LS").text = unicode(row.LS)
        return self.root

class b104r1003Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b104r1003Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuskpd/R1041003.jrxml')
        self.xpath = '/apbd/spp'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""

        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spp')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "tgl_spp").text = unicode(row.tgl_spp)
            ET.SubElement(xml_greeting, "spp_kd").text = row.spp_kd
            ET.SubElement(xml_greeting, "spp_nm").text = row.spp_nm
            ET.SubElement(xml_greeting, "UP").text = unicode(row.UP)
            ET.SubElement(xml_greeting, "GU").text = unicode(row.GU)
            ET.SubElement(xml_greeting, "TU").text = unicode(row.TU)
            ET.SubElement(xml_greeting, "LS").text = unicode(row.LS)
        return self.root

class b104r1004Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b104r1004Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuskpd/R1041004.jrxml')
        self.xpath = '/apbd/spp'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""

        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spp')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "tgl_spm").text = unicode(row.tgl_spm)
            ET.SubElement(xml_greeting, "spm_kd").text = row.spm_kd
            ET.SubElement(xml_greeting, "spm_nm").text = row.spm_nm
            ET.SubElement(xml_greeting, "BRUTO").text = unicode(row.BRUTO)
            ET.SubElement(xml_greeting, "POTONGAN").text = unicode(row.POTONGAN)
            ET.SubElement(xml_greeting, "NETTO").text = unicode(row.NETTO)
            ET.SubElement(xml_greeting, "INFORMASI").text = unicode(row.INFORMASI)
        return self.root 

class b104r2001Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b104r2001Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuskpd/R1042001.jrxml')
        self.xpath = '/apbd/spp'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""

        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spp')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "jenis").text = row.jenis
            ET.SubElement(xml_greeting, "spp_kd").text = row.spp_kd
            ET.SubElement(xml_greeting, "spp_nm").text = row.spp_nm
            ET.SubElement(xml_greeting, "tgl_spp").text = unicode(row.tgl_spp)
            ET.SubElement(xml_greeting, "spm_kd").text = row.spm_kd
            ET.SubElement(xml_greeting, "tgl_spm").text = unicode(row.tgl_spm)
            ET.SubElement(xml_greeting, "sp2d_kd").text = row.sp2d_kd
            ET.SubElement(xml_greeting, "tgl_sp2d").text = unicode(row.tgl_sp2d)
            ET.SubElement(xml_greeting, "nominal").text = unicode(row.nominal)
        return self.root

class b104r2002Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b104r2002Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuskpd/R1042002.jrxml')
        self.xpath = '/apbd/spp'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""

        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spp')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "tgl_spp").text = unicode(row.tgl_spp)
            ET.SubElement(xml_greeting, "spp_kd").text = row.spp_kd
            ET.SubElement(xml_greeting, "spp_nm").text = row.spp_nm
            ET.SubElement(xml_greeting, "UP").text = unicode(row.UP)
            ET.SubElement(xml_greeting, "GU").text = unicode(row.GU)
            ET.SubElement(xml_greeting, "TU").text = unicode(row.TU)
            ET.SubElement(xml_greeting, "LS_GJ").text = unicode(row.LS_GJ)
            ET.SubElement(xml_greeting, "LS").text = unicode(row.LS)
        return self.root

class b104r2003Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b104r2003Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuskpd/R1042003.jrxml')
        self.xpath = '/apbd/spp'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""

        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spp')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "tgl_spp").text = unicode(row.tgl_spp)
            ET.SubElement(xml_greeting, "spp_kd").text = row.spp_kd
            ET.SubElement(xml_greeting, "spp_nm").text = row.spp_nm
            ET.SubElement(xml_greeting, "UP").text = unicode(row.UP)
            ET.SubElement(xml_greeting, "GU").text = unicode(row.GU)
            ET.SubElement(xml_greeting, "TU").text = unicode(row.TU)
            ET.SubElement(xml_greeting, "LS").text = unicode(row.LS)
        return self.root

class b104r2004Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b104r2004Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuskpd/R1042004.jrxml')
        self.xpath = '/apbd/spp'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""

        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spp')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "tgl_spm").text = unicode(row.tgl_spm)
            ET.SubElement(xml_greeting, "spm_kd").text = row.spm_kd
            ET.SubElement(xml_greeting, "spm_nm").text = row.spm_nm
            ET.SubElement(xml_greeting, "BRUTO").text = unicode(row.BRUTO)
            ET.SubElement(xml_greeting, "POTONGAN").text = unicode(row.POTONGAN)
            ET.SubElement(xml_greeting, "NETTO").text = unicode(row.NETTO)
            ET.SubElement(xml_greeting, "INFORMASI").text = unicode(row.INFORMASI)
        return self.root 

class b104r300Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b104r300Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuskpd/R104300.jrxml')
        self.xpath = '/apbd/spj'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""

        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spj')
            ET.SubElement(xml_greeting, "tahun_id").text = unicode(row.tahun_id)
        return self.root 

class b104r400Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b104r400Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuskpd/R104400.jrxml')
        self.xpath = '/apbd/spj'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""

        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spj')
            ET.SubElement(xml_greeting, "tahun_id").text = unicode(row.tahun_id)
        return self.root 

class ViewTUSKPDLap(BaseViews):
    def __init__(self, context, request):
        BaseViews.__init__(self, context, request)
        self.app = 'tuskpd'

        #if 'app' in request.params and request.params['app'] == self.app and self.logged:
        row = DBSession.query(TahunModel.status_apbd).filter(TahunModel.tahun==self.tahun).first()
        self.session['status_apbd'] = row and row[0] or 0


        self.status_apbd =  'status_apbd' in self.session and self.session['status_apbd'] or 0        
        #self.status_apbd_nm =  status_apbd[str(self.status_apbd)]        
        
        self.all_unit =  'all_unit' in self.session and self.session['all_unit'] or 0        
        self.unit_id  = 'unit_id' in self.session and self.session['unit_id'] or 0
        self.unit_kd  = 'unit_kd' in self.session and self.session['unit_kd'] or "X.XX.XX"
        self.unit_nm  = 'unit_nm' in self.session and self.session['unit_nm'] or "Pilih Unit"
        self.keg_id  = 'keg_id' in self.session and self.session['keg_id'] or 0
        
        self.datas['status_apbd'] = self.status_apbd 
        #self.datas['status_apbd_nm'] = self.status_apbd_nm
        self.datas['all_unit'] = self.all_unit
        self.datas['unit_kd'] = self.unit_kd
        self.datas['unit_nm'] = self.unit_nm
        self.datas['unit_id'] = self.unit_id
        
#KETETAPAN
    @view_config(route_name="b102_r001_act")
    def b102_r001_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if self.is_akses_mod('read'):
                query = DBSession.query(KetetapanModel
                      ).filter(KetetapanModel.unit_id==Unit.id,
                      KetetapanModel.unit_id==self.unit_id,
                      KetetapanModel.tahun_id==self.tahun
                      ).order_by(KetetapanModel.tgl_ketetapan
                      )
                generator = b102r001Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#TBP
    @view_config(route_name="b102_r002_act")
    def b102_r002_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if self.is_akses_mod('read'):
                query = DBSession.query(ARInvoiceModel.tahun_id.label('tahun'), Unit.nama.label('unit_nm'),
                      ARInvoiceModel.id.label('arinvoice_id'), ARInvoiceModel.kode, ARInvoiceModel.nama.label('arinvoice_nm'), 
                      ARInvoiceModel.tgl_terima, ARInvoiceModel.tgl_validasi, ARInvoiceModel.bendahara_nm, 
                      ARInvoiceModel.penyetor, ARInvoiceModel.alamat, KegiatanSubModel.nama.label('kegiatan_nm'),
                      func.sum(ARInvoiceItemModel.nilai).label('nilai')
                      ).filter(ARInvoiceModel.unit_id==Unit.id, ARInvoiceModel.kegiatan_sub_id==KegiatanSubModel.id,
                      ARInvoiceItemModel.arinvoice_id==ARInvoiceModel.id, ARInvoiceModel.unit_id==self.unit_id,
                      ARInvoiceModel.tahun_id==self.tahun, ARInvoiceModel.id==pk_id
                      ).group_by(ARInvoiceModel.tahun_id, Unit.nama,
                      ARInvoiceModel.id, ARInvoiceModel.kode, ARInvoiceModel.nama, 
                      ARInvoiceModel.tgl_terima, ARInvoiceModel.tgl_validasi, ARInvoiceModel.bendahara_nm, 
                      ARInvoiceModel.penyetor, ARInvoiceModel.alamat, KegiatanSubModel.nama
                      )
                generator = b102r002Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#STS
    @view_config(route_name="b102_r003_act")
    def b102_r003_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if self.is_akses_mod('read'):
                query = DBSession.query(StsModel
                      ).filter(StsModel.unit_id==Unit.id, 
                      StsModel.unit_id==self.unit_id,
                      StsModel.tahun_id==self.tahun, StsModel.id==pk_id
                      )
                generator = b102r003Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b103_r001_act")
    def b103_r001_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if url_dict['act']=='001' and self.is_akses_mod('read'):
                query = DBSession.query(APInvoiceModel.tahun_id.label('tahun'), Unit.nama.label('unit_nm'),
                      case([(APInvoiceModel.jenis==1,"UP"),(APInvoiceModel.jenis==2,"TU"),(APInvoiceModel.jenis==3,"GU"),
                      (APInvoiceModel.jenis==4,"LS")], else_="").label('jenis'),
                      APInvoiceModel.id.label('invoice_id'), APInvoiceModel.nama.label('invoice_nm'), 
                      APInvoiceModel.ap_tanggal.label('tgl_invoice'),APInvoiceModel.ap_nomor, APInvoiceModel.ap_nama, 
                      APInvoiceModel.ap_rekening, APInvoiceModel.ap_npwp, KegiatanSubModel.nama.label('kegiatan_nm'),
                      func.sum(APInvoiceItemModel.nilai).label('nilai')
                      ).filter(APInvoiceModel.unit_id==Unit.id, APInvoiceModel.kegiatan_sub_id==KegiatanSubModel.id,
                      APInvoiceItemModel.apinvoice_id==APInvoiceModel.id, APInvoiceModel.unit_id==self.unit_id,
                      APInvoiceModel.tahun_id==self.tahun, APInvoiceModel.id==pk_id
                      ).group_by(APInvoiceModel.tahun_id, Unit.nama,
                      case([(APInvoiceModel.jenis==1,"UP"),(APInvoiceModel.jenis==2,"TU"),(APInvoiceModel.jenis==3,"GU"),
                      (APInvoiceModel.jenis==4,"LS")], else_=""),
                      APInvoiceModel.id, APInvoiceModel.nama, 
                      APInvoiceModel.ap_tanggal,APInvoiceModel.ap_nomor, APInvoiceModel.ap_nama, 
                      APInvoiceModel.ap_rekening, APInvoiceModel.ap_npwp, KegiatanSubModel.nama
                      )
                generator = b103r001Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b103_r002_act")
    def b103_r002_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if url_dict['act']=='001' and self.is_akses_mod('read'):
                query = DBSession.query(SppModel.tahun_id.label('tahun'), Unit.kode.label('unit_kd'), 
                      Unit.nama.label('unit_nm'), KegiatanSubModel.nama.label('kegiatan_nm'),
                      TahunModel.no_perkdh, TahunModel.tgl_perkdh, Urusan.nama.label('urusan_nm'),
                      SppModel.kode.label('spp_kd'), SppModel.nama, SppModel.bank_nama, SppModel.bank_account,
                      SppModel.tanggal, case([(SppModel.jenis==1,"UP"),(SppModel.jenis==2,"TU"),(SppModel.jenis==3,"GU"),
                      (SppModel.jenis==4,"LS")], else_="").label('jenis'), SppModel.nominal,
                      SpdModel.kode.label('spd_kd'), SpdModel.tanggal.label('tgl_spd')
                      ).join(Unit,TahunModel,SppItemModel,APInvoiceModel,KegiatanSubModel
                      ).outerjoin(SpdModel,SpdModel.id==SppModel.spd_id
                      ).outerjoin(Urusan,Unit.urusan_id==Urusan.id
                      ).filter(SppModel.unit_id==Unit.id, SppModel.id==SppItemModel.spp_id, 
                      SppItemModel.apinvoice_id==APInvoiceModel.id, KegiatanSubModel.id==APInvoiceModel.kegiatan_sub_id,
                      SppModel.tahun_id==TahunModel.id, SppModel.unit_id==self.unit_id, 
                      SppModel.tahun_id==self.tahun, SppModel.id==pk_id
                      )
                generator = b103r002Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
                
            elif url_dict['act']=='002' and self.is_akses_mod('read'):
                query = DBSession.query(SppModel.tahun_id.label('tahun'), Unit.kode.label('unit_kd'), 
                      Unit.nama.label('unit_nm'), KegiatanSubModel.nama.label('kegiatan_nm'),
                      TahunModel.no_perkdh, TahunModel.tgl_perkdh, Urusan.nama.label('urusan_nm'),
                      SppModel.kode.label('spp_kd'), SppModel.nama, SppModel.bank_nama, SppModel.bank_account,
                      SppModel.tanggal, case([(SppModel.jenis==1,"UP"),(SppModel.jenis==2,"TU"),(SppModel.jenis==3,"GU"),
                      (SppModel.jenis==4,"LS")], else_="").label('jenis'), SppModel.nominal,
                      SpdModel.kode.label('spd_kd'), SpdModel.tanggal.label('tgl_spd')
                      ).join(Unit,TahunModel,SppItemModel,APInvoiceModel,KegiatanSubModel
                      ).outerjoin(SpdModel,SpdModel.id==SppModel.spd_id
                      ).outerjoin(Urusan,Unit.urusan_id==Urusan.id
                      ).filter(SppModel.unit_id==Unit.id, SppModel.id==SppItemModel.spp_id, 
                      SppItemModel.apinvoice_id==APInvoiceModel.id, KegiatanSubModel.id==APInvoiceModel.kegiatan_sub_id,
                      SppModel.tahun_id==TahunModel.id, SppModel.unit_id==self.unit_id, 
                      SppModel.tahun_id==self.tahun, SppModel.id==pk_id
                      )
                generator = b103r0022Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response

            elif url_dict['act']=='003' and self.is_akses_mod('read'):
                query = DBSession.query(SppModel.tahun_id.label('tahun'), Unit.kode.label('unit_kd'), 
                      Unit.nama.label('unit_nm'), KegiatanSubModel.nama.label('kegiatan_nm'),
                      TahunModel.no_perkdh, TahunModel.tgl_perkdh, Urusan.nama.label('urusan_nm'),
                      SppModel.kode.label('spp_kd'), SppModel.nama, SppModel.bank_nama, SppModel.bank_account,
                      SppModel.tanggal, case([(SppModel.jenis==1,"UP"),(SppModel.jenis==2,"TU"),(SppModel.jenis==3,"GU"),
                      (SppModel.jenis==4,"LS")], else_="").label('jenis'), SppModel.nominal,
                      SpdModel.kode.label('spd_kd'), SpdModel.tanggal.label('tgl_spd')
                      ).join(Unit,TahunModel,SppItemModel,APInvoiceModel,KegiatanSubModel
                      ).outerjoin(SpdModel,SpdModel.id==SppModel.spd_id
                      ).outerjoin(Urusan,Unit.urusan_id==Urusan.id
                      ).filter(SppModel.unit_id==Unit.id, SppModel.id==SppItemModel.spp_id, 
                      SppItemModel.apinvoice_id==APInvoiceModel.id, KegiatanSubModel.id==APInvoiceModel.kegiatan_sub_id,
                      SppModel.tahun_id==TahunModel.id, SppModel.unit_id==self.unit_id, 
                      SppModel.tahun_id==self.tahun, SppModel.id==pk_id
                      )
                generator = b103r0023Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response

            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
  
    @view_config(route_name="b103_r003_act")
    def b103_r003_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0

            if url_dict['act']=='001' and self.is_akses_mod('read'):
                subq1 = DBSession.query(SpmModel.id.label('spm_id'), SpmModel.kode.label('spm_kd'), SpmModel.nama.label('spm_nm'), SpmModel.tanggal.label('spm_tgl'), SppModel.id.label('spp_id'), 
                         SppModel.kode.label('spp_kd'), SppModel.nama.label('spp_nm'), SppModel.tanggal.label('spp_tgl'), SppModel.jenis.label('jenis'), 
                         SppModel.bank_nama.label('bank_nama'), SppModel.bank_account.label('bank_account'), SppModel.ap_nama.label('ap_nama'), SppModel.ap_bank.label('ap_bank'), SppModel.ap_rekening.label('ap_rekening'), SppModel.ap_npwp.label('ap_npwp'), 
                         SppModel.tahun_id.label('tahun_id'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), KegiatanModel.kode.label('keg_kd'), 
                         KegiatanModel.nama.label('keg_nm'), ProgramModel.kode.label('prg_kd'), ProgramModel.nama.label('prg_nm'), SppModel.spd_id.label('spd_id'),
                         func.sum(APInvoiceItemModel.nilai).label('nilai'), func.sum(APInvoiceItemModel.ppn).label('ppn'), 
                         func.sum(APInvoiceItemModel.pph).label('pph'), literal_column('0').label('potongan')
                         ).filter(SpmModel.spp_id==SppModel.id, SppModel.unit_id==Unit.id,
                         SppItemModel.spp_id==SppModel.id, SppItemModel.apinvoice_id==APInvoiceItemModel.apinvoice_id, APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                         KegiatanItemModel.rekening_id==RekeningModel.id, KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                         KegiatanSubModel.kegiatan_id==KegiatanModel.id, KegiatanModel.program_id==ProgramModel.id,
                         SppModel.unit_id==self.unit_id, SppModel.tahun_id==self.tahun, SpmModel.id==pk_id,
                         func.left(RekeningModel.kode,1)=='5'
                         ).group_by(SpmModel.id, SpmModel.kode, 
                         SpmModel.nama, SpmModel.tanggal, SppModel.id, SppModel.kode, SppModel.nama, SppModel.tanggal, 
                         SppModel.jenis, SppModel.bank_nama, SppModel.bank_account, SppModel.ap_nama, SppModel.ap_bank, 
                         SppModel.ap_rekening, SppModel.ap_npwp, SppModel.tahun_id, Unit.kode, Unit.nama, 
                         KegiatanModel.kode, KegiatanModel.nama, ProgramModel.kode, ProgramModel.nama, SppModel.spd_id
                         )                         

                subq2 = DBSession.query(SpmModel.id.label('spm_id'), SpmModel.kode.label('spm_kd'), SpmModel.nama.label('spm_nm'), SpmModel.tanggal.label('spm_tgl'), SppModel.id.label('spp_id'), 
                         SppModel.kode.label('spp_kd'), SppModel.nama.label('spp_nm'), SppModel.tanggal.label('spp_tgl'), SppModel.jenis.label('jenis'), 
                         SppModel.bank_nama.label('bank_nama'), SppModel.bank_account.label('bank_account'), SppModel.ap_nama.label('ap_nama'), SppModel.ap_bank.label('ap_bank'), SppModel.ap_rekening.label('ap_rekening'), SppModel.ap_npwp.label('ap_npwp'), 
                         SppModel.tahun_id.label('tahun_id'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), KegiatanModel.kode.label('keg_kd'), 
                         KegiatanModel.nama.label('keg_nm'), ProgramModel.kode.label('prg_kd'), ProgramModel.nama.label('prg_nm'), SppModel.spd_id.label('spd_id'),
                         literal_column('0').label('nilai'), literal_column('0').label('ppn'), 
                         literal_column('0').label('pph'), func.sum(APInvoiceItemModel.nilai).label('potongan')
                         ).filter(SpmModel.spp_id==SppModel.id, SppModel.unit_id==Unit.id,
                         SppItemModel.spp_id==SppModel.id, SppItemModel.apinvoice_id==APInvoiceItemModel.apinvoice_id, APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                         KegiatanItemModel.rekening_id==RekeningModel.id, KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                         KegiatanSubModel.kegiatan_id==KegiatanModel.id, KegiatanModel.program_id==ProgramModel.id,
                         SppModel.unit_id==self.unit_id, SppModel.tahun_id==self.tahun, SpmModel.id==pk_id,
                         func.left(RekeningModel.kode,1)=='7'
                         ).group_by(SpmModel.id, SpmModel.kode, 
                         SpmModel.nama, SpmModel.tanggal, SppModel.id, SppModel.kode, SppModel.nama, SppModel.tanggal, 
                         SppModel.jenis, SppModel.bank_nama, SppModel.bank_account, SppModel.ap_nama, SppModel.ap_bank, 
                         SppModel.ap_rekening, SppModel.ap_npwp, SppModel.tahun_id, Unit.kode, Unit.nama, 
                         KegiatanModel.kode, KegiatanModel.nama, ProgramModel.kode, ProgramModel.nama, SppModel.spd_id 
                         )                         
                
                subq = subq1.union(subq2).subquery()
                
                query = DBSession.query(subq.c.spm_id, subq.c.spm_kd, 
                         subq.c.spm_nm, subq.c.spm_tgl, subq.c.spp_id, subq.c.spp_kd, subq.c.spp_nm, subq.c.spp_tgl, 
                         subq.c.jenis, subq.c.bank_nama, subq.c.bank_account, subq.c.ap_nama, subq.c.ap_bank, subq.c.ap_rekening, 
                         subq.c.ap_npwp, subq.c.tahun_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.keg_kd, subq.c.keg_nm, subq.c.prg_kd, 
                         subq.c.prg_nm, subq.c.spd_id, func.sum(subq.c.nilai).label('nilai'),func.sum(subq.c.ppn).label('ppn'), 
                         func.sum(subq.c.pph).label('pph'),func.sum(subq.c.potongan).label('potongan')
                         ).group_by(subq.c.spm_id, subq.c.spm_kd, 
                         subq.c.spm_nm, subq.c.spm_tgl, subq.c.spp_id, subq.c.spp_kd, subq.c.spp_nm, subq.c.spp_tgl, 
                         subq.c.jenis, subq.c.bank_nama, subq.c.bank_account, subq.c.ap_nama, subq.c.ap_bank, subq.c.ap_rekening, 
                         subq.c.ap_npwp, subq.c.tahun_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.keg_kd, subq.c.keg_nm, subq.c.prg_kd, 
                         subq.c.prg_nm, subq.c.spd_id
                         )                         

                generator = b103r003Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

# Invoice Lap
    @view_config(route_name="b104_r000", renderer="osipkd:templates/apbd/tuskpd/b104r000.pt")
    def b104_r000(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas,)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b104_r000_act")
    def b104_r000_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            tipe = 'tipe' in params and params['tipe'] and int(params['tipe']) or 0
            mulai = 'mulai' in params and params['mulai'] or 0
            selesai = 'selesai' in params and params['selesai'] or 0
            if url_dict['act']=='1' and self.is_akses_mod('read'):
              if tipe==0 :
                query = DBSession.query(APInvoiceModel.tahun_id.label('tahun'), Unit.nama.label('unit_nm'),
                      APInvoiceModel.ap_tanggal.label('tgl_invoice'),
                      case([(APInvoiceModel.jenis==1,"UP"),(APInvoiceModel.jenis==2,"TU"),(APInvoiceModel.jenis==3,"GU"),
                      (APInvoiceModel.jenis==4,"LS")], else_="").label('jenis'),
                      APInvoiceModel.ap_nomor.label('invoice_kd'), KegiatanSubModel.nama.label('kegiatan_nm'), 
                      RekeningModel.kode.label('rek_kd'),RekeningModel.nama.label('rek_nm'), 
                      func.sum(APInvoiceItemModel.nilai).label('jumlah')
                      ).filter(APInvoiceModel.unit_id==Unit.id, APInvoiceModel.kegiatan_sub_id==KegiatanSubModel.id,
                      APInvoiceModel.id==APInvoiceItemModel.apinvoice_id, APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                      KegiatanItemModel.rekening_id==RekeningModel.id, APInvoiceModel.unit_id==self.unit_id,
                      APInvoiceModel.tahun_id==self.session['tahun'],  
                      APInvoiceModel.ap_tanggal.between(mulai,selesai)
                      ).group_by(APInvoiceModel.tahun_id, Unit.nama,
                      APInvoiceModel.ap_tanggal,
                      case([(APInvoiceModel.jenis==1,"UP"),(APInvoiceModel.jenis==2,"TU"),(APInvoiceModel.jenis==3,"GU"),
                      (APInvoiceModel.jenis==4,"LS")], else_=""),
                      APInvoiceModel.ap_nomor, KegiatanSubModel.nama, 
                      RekeningModel.kode,RekeningModel.nama
                      ).order_by(APInvoiceModel.ap_tanggal).all()
              else:
                    query = DBSession.query(APInvoiceModel.tahun_id.label('tahun'), Unit.nama.label('unit_nm'),
                      APInvoiceModel.ap_tanggal.label('tgl_invoice'),
                      case([(APInvoiceModel.jenis==1,"UP"),(APInvoiceModel.jenis==2,"TU"),(APInvoiceModel.jenis==3,"GU"),
                      (APInvoiceModel.jenis==4,"LS")], else_="").label('jenis'),
                      APInvoiceModel.ap_nomor.label('invoice_kd'), KegiatanSubModel.nama.label('kegiatan_nm'), 
                      RekeningModel.kode.label('rek_kd'),RekeningModel.nama.label('rek_nm'), 
                      func.sum(APInvoiceItemModel.nilai).label('jumlah')
                      ).filter(APInvoiceModel.unit_id==Unit.id, APInvoiceModel.kegiatan_sub_id==KegiatanSubModel.id,
                      APInvoiceModel.id==APInvoiceItemModel.apinvoice_id, APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                      KegiatanItemModel.rekening_id==RekeningModel.id, APInvoiceModel.unit_id==self.unit_id,
                      APInvoiceModel.tahun_id==self.session['tahun'], APInvoiceModel.jenis==tipe, 
                      APInvoiceModel.ap_tanggal.between(mulai,selesai)
                      ).group_by(APInvoiceModel.tahun_id, Unit.nama,
                      APInvoiceModel.ap_tanggal,
                      case([(APInvoiceModel.jenis==1,"UP"),(APInvoiceModel.jenis==2,"TU"),(APInvoiceModel.jenis==3,"GU"),
                      (APInvoiceModel.jenis==4,"LS")], else_=""),
                      APInvoiceModel.ap_nomor, KegiatanSubModel.nama, 
                      RekeningModel.kode,RekeningModel.nama
                      ).order_by(APInvoiceModel.ap_tanggal).all()

              generator = b104r000Generator()
              pdf = generator.generate(query)
              response=req.response
              response.content_type="application/pdf"
              response.content_disposition='filename=output.pdf' 
              response.write(pdf)
              return response
            else:
              return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#SPP Lap
    @view_config(route_name="b104_r100", renderer="osipkd:templates/apbd/tuskpd/b104r100.pt")
    def b104_r100(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas,)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b104_r100_act")
    def b104_r100_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            tipe = 'tipe' in params and params['tipe'] and int(params['tipe']) or 0
            mulai = 'mulai' in params and params['mulai'] or 0
            selesai = 'selesai' in params and params['selesai'] or 0
            if url_dict['act']=='1' and self.is_akses_mod('read'):
                if tipe ==0 :
                   query = DBSession.query(SppModel.tahun_id.label('tahun'), Unit.nama.label('unit_nm'),
                      case([(SppModel.jenis==1,"UP"),(SppModel.jenis==2,"TU"),(SppModel.jenis==3,"GU"),(SppModel.jenis==4,"LS")], else_="").label('jenis'),
                      SppModel.kode.label('spp_kd'), SppModel.nama.label('spp_nm'), SppModel.tanggal.label('tgl_spp'),
                      SpmModel.kode.label('spm_kd'), SpmModel.tanggal.label('tgl_spm'),
                      Sp2dModel.kode.label('sp2d_kd'), Sp2dModel.tanggal.label('tgl_sp2d'),
                      func.sum(APInvoiceItemModel.nilai).label('nominal')
                      ).filter(SppItemModel.spp_id==SppModel.id, SppItemModel.apinvoice_id==APInvoiceModel.id,
                      APInvoiceItemModel.apinvoice_id==APInvoiceModel.id, APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                      KegiatanItemModel.rekening_id==RekeningModel.id,
                      SppModel.unit_id==Unit.id, SppModel.unit_id==self.unit_id,
                      SppModel.tahun_id==self.session['tahun'],
                      SppModel.tanggal.between(mulai,selesai)        
                      ).outerjoin(SpmModel,SpmModel.spp_id==SppModel.id
                      ).outerjoin(Sp2dModel,Sp2dModel.spm_id==SpmModel.id
                      ).group_by(SppModel.tahun_id, Unit.nama,
                      case([(SppModel.jenis==1,"UP"),(SppModel.jenis==2,"TU"),(SppModel.jenis==3,"GU"),(SppModel.jenis==4,"LS")], else_=""),
                      SppModel.kode, SppModel.nama, SppModel.tanggal,
                      SpmModel.kode, SpmModel.tanggal,
                      Sp2dModel.kode, Sp2dModel.tanggal,
                      ).order_by(SppModel.tanggal).all()
                else:
                    query = DBSession.query(SppModel.tahun_id.label('tahun'), Unit.nama.label('unit_nm'),
                      case([(SppModel.jenis==1,"UP"),(SppModel.jenis==2,"TU"),(SppModel.jenis==3,"GU"),(SppModel.jenis==4,"LS")], else_="").label('jenis'),
                      SppModel.kode.label('spp_kd'), SppModel.nama.label('spp_nm'), SppModel.tanggal.label('tgl_spp'),
                      SpmModel.kode.label('spm_kd'), SpmModel.tanggal.label('tgl_spm'),
                      Sp2dModel.kode.label('sp2d_kd'), Sp2dModel.tanggal.label('tgl_sp2d'),
                      func.sum(APInvoiceItemModel.nilai).label('nominal')
                      ).filter(SppItemModel.spp_id==SppModel.id, SppItemModel.apinvoice_id==APInvoiceModel.id,
                      APInvoiceItemModel.apinvoice_id==APInvoiceModel.id, APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                      KegiatanItemModel.rekening_id==RekeningModel.id,
                      SppModel.unit_id==Unit.id, SppModel.unit_id==self.unit_id,
                      SppModel.tahun_id==self.session['tahun'], SppModel.jenis==tipe, 
                      SppModel.tanggal.between(mulai,selesai)
                      ).outerjoin(SpmModel,SpmModel.spp_id==SppModel.id
                      ).outerjoin(Sp2dModel,Sp2dModel.spm_id==SpmModel.id
                      ).group_by(SppModel.tahun_id, Unit.nama,
                      case([(SppModel.jenis==1,"UP"),(SppModel.jenis==2,"TU"),(SppModel.jenis==3,"GU"),(SppModel.jenis==4,"LS")], else_=""),
                      SppModel.kode, SppModel.nama, SppModel.tanggal,
                      SpmModel.kode, SpmModel.tanggal,
                      Sp2dModel.kode, Sp2dModel.tanggal,
                      ).order_by(SppModel.tanggal).all()
                      
                generator = b104r1001Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif url_dict['act']=='2' and self.is_akses_mod('read'):
                if tipe ==0 :
                    query = DBSession.query(SppModel.tahun_id.label('tahun'), 
                      Unit.nama.label('unit_nm'), SppModel.tanggal.label('tgl_spp'), 
                      SppModel.kode.label('spp_kd'), SppModel.nama.label('spp_nm'),
                      func.sum(case([(SppModel.jenis==1,APInvoiceItemModel.nilai)], else_=0)).label('UP'),
                      func.sum(case([(SppModel.jenis==2,APInvoiceItemModel.nilai)], else_=0)).label('GU'),
                      func.sum(case([(SppModel.jenis==3,APInvoiceItemModel.nilai)], else_=0)).label('TU'),
                      func.sum(case([(and_(SppModel.jenis==4,func.substr(RekeningModel.kode,1,5)=='5.2.1'),APInvoiceItemModel.nilai)], else_=0)).label('LS_GJ'),
                      func.sum(case([(and_(SppModel.jenis==4,not_(func.substr(RekeningModel.kode,1,5)=='5.2.1')),APInvoiceItemModel.nilai)], else_=0)).label('LS')
                      ).filter(SppItemModel.spp_id==SppModel.id, SppItemModel.apinvoice_id==APInvoiceModel.id,
                      APInvoiceItemModel.apinvoice_id==APInvoiceModel.id, APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                      KegiatanItemModel.rekening_id==RekeningModel.id,
                      SppModel.unit_id==Unit.id, SppModel.unit_id==self.unit_id,
                      SppModel.tahun_id==self.session['tahun'], 
                      SppModel.tanggal.between(mulai,selesai)        
                      ).group_by(SppModel.tahun_id, Unit.nama, SppModel.tanggal, 
                      SppModel.kode, SppModel.nama
                      ).order_by(SppModel.tanggal).all()
                else:
                    query = DBSession.query(SppModel.tahun_id.label('tahun'), 
                      Unit.nama.label('unit_nm'), SppModel.tanggal.label('tgl_spp'), 
                      SppModel.kode.label('spp_kd'), SppModel.nama.label('spp_nm'),
                      func.sum(case([(SppModel.jenis==1,APInvoiceItemModel.nilai)], else_=0)).label('UP'),
                      func.sum(case([(SppModel.jenis==2,APInvoiceItemModel.nilai)], else_=0)).label('GU'),
                      func.sum(case([(SppModel.jenis==3,APInvoiceItemModel.nilai)], else_=0)).label('TU'),
                      func.sum(case([(and_(SppModel.jenis==4,func.substr(RekeningModel.kode,1,5)=='5.2.1'),APInvoiceItemModel.nilai)], else_=0)).label('LS_GJ'),
                      func.sum(case([(and_(SppModel.jenis==4,not_(func.substr(RekeningModel.kode,1,5)=='5.2.1')),APInvoiceItemModel.nilai)], else_=0)).label('LS')
                      ).filter(SppItemModel.spp_id==SppModel.id, SppItemModel.apinvoice_id==APInvoiceModel.id,
                      APInvoiceItemModel.apinvoice_id==APInvoiceModel.id, APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                      KegiatanItemModel.rekening_id==RekeningModel.id,
                      SppModel.unit_id==Unit.id, SppModel.unit_id==self.unit_id,
                      SppModel.tahun_id==self.session['tahun'], SppModel.jenis==tipe, 
                      SppModel.tanggal.between(mulai,selesai)        
                      ).group_by(SppModel.tahun_id, Unit.nama, SppModel.tanggal, 
                      SppModel.kode, SppModel.nama
                      ).order_by(SppModel.tanggal).all()
                      
                generator = b104r1002Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif url_dict['act']=='3' and self.is_akses_mod('read'):
                if tipe ==0 :
                    query = DBSession.query(SppModel.tahun_id.label('tahun'), 
                      Unit.nama.label('unit_nm'), SppModel.tanggal.label('tgl_spp'), 
                      SppModel.kode.label('spp_kd'), SppModel.nama.label('spp_nm'),
                      case([(SppModel.jenis==1,SppModel.nominal)], else_=0).label('UP'),
                      case([(SppModel.jenis==2,SppModel.nominal)], else_=0).label('GU'),
                      case([(SppModel.jenis==3,SppModel.nominal)], else_=0).label('TU'),
                      case([(SppModel.jenis==4,SppModel.nominal)], else_=0).label('LS'),
                      ).filter(SppModel.unit_id==Unit.id, SppModel.unit_id==self.unit_id,
                      SppModel.tahun_id==self.session['tahun'], 
                      SppModel.tanggal.between(mulai,selesai)        
                      ).order_by(SppModel.tanggal).all()
                else:
                    query = DBSession.query(SppModel.tahun_id.label('tahun'), 
                      Unit.nama.label('unit_nm'), SppModel.tanggal.label('tgl_spp'), 
                      SppModel.kode.label('spp_kd'), SppModel.nama.label('spp_nm'),
                      case([(SppModel.jenis==1,SppModel.nominal)], else_=0).label('UP'),
                      case([(SppModel.jenis==2,SppModel.nominal)], else_=0).label('GU'),
                      case([(SppModel.jenis==3,SppModel.nominal)], else_=0).label('TU'),
                      case([(SppModel.jenis==4,SppModel.nominal)], else_=0).label('LS'),
                      ).filter(SppModel.unit_id==Unit.id, SppModel.unit_id==self.unit_id,
                      SppModel.tahun_id==self.session['tahun'], SppModel.jenis==tipe, 
                      SppModel.tanggal.between(mulai,selesai)        
                      ).order_by(SppModel.tanggal).all()
                      
                generator = b104r1003Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif url_dict['act']=='4' and self.is_akses_mod('read'):
                if tipe ==0 :
                    query = DBSession.query(SppModel.tahun_id.label('tahun'), 
                      Unit.nama.label('unit_nm'), SppModel.tanggal.label('tgl_spm'), 
                      SppModel.kode.label('spm_kd'), SppModel.nama.label('spm_nm'),
                      case([(SppModel.nominal==1,SppModel.nominal)], else_=0).label('BRUTO'),
                      case([(SppModel.nominal==2,SppModel.nominal)], else_=0).label('POTONGAN'),
                      case([(SppModel.nominal==3,SppModel.nominal)], else_=0).label('NETTO'),
                      case([(SppModel.nominal==4,SppModel.nominal)], else_=0).label('INFORMASI')
                      ).filter(SppModel.unit_id==Unit.id, SppModel.unit_id==self.unit_id,
                      SppModel.tahun_id==self.session['tahun'], 
                      SppModel.tanggal.between(mulai,selesai)        
                      ).order_by(SppModel.tanggal).all()
                else:
                    query = DBSession.query(SppModel.tahun_id.label('tahun'), 
                      Unit.nama.label('unit_nm'), SppModel.tanggal.label('tgl_spm'), 
                      SppModel.kode.label('spm_kd'), SppModel.nama.label('spm_nm'),
                      case([(SppModel.nominal==1,SppModel.nominal)], else_=0).label('BRUTO'),
                      case([(SppModel.nominal==2,SppModel.nominal)], else_=0).label('POTONGAN'),
                      case([(SppModel.nominal==3,SppModel.nominal)], else_=0).label('NETTO'),
                      case([(SppModel.nominal==4,SppModel.nominal)], else_=0).label('INFORMASI')
                      ).filter(SppModel.unit_id==Unit.id, SppModel.unit_id==self.unit_id,
                      SppModel.tahun_id==self.session['tahun'], SppModel.jenis==tipe, 
                      SppModel.tanggal.between(mulai,selesai)        
                      ).order_by(SppModel.tanggal).all()
                    
                generator = b104r1004Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
#SPM Lap
    @view_config(route_name="b104_r200", renderer="osipkd:templates/apbd/tuskpd/b104r200.pt")
    def b104_r200(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas,)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b104_r200_act")
    def b104_r200_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            tipe = 'tipe' in params and params['tipe'] and int(params['tipe']) or 0
            mulai = 'mulai' in params and params['mulai'] or 0
            selesai = 'selesai' in params and params['selesai'] or 0
            if url_dict['act']=='1' and self.is_akses_mod('read'):
                if tipe ==0 :
                   query = DBSession.query(SppModel.tahun_id.label('tahun'), Unit.nama.label('unit_nm'),
                      case([(SppModel.jenis==1,"UP"),(SppModel.jenis==2,"TU"),(SppModel.jenis==3,"GU"),(SppModel.jenis==4,"LS")], else_="").label('jenis'),
                      SppModel.kode.label('spp_kd'), SppModel.nama.label('spp_nm'), SppModel.tanggal.label('tgl_spp'),
                      SpmModel.kode.label('spm_kd'), SpmModel.tanggal.label('tgl_spm'),
                      Sp2dModel.kode.label('sp2d_kd'), Sp2dModel.tanggal.label('tgl_sp2d'),
                      func.sum(APInvoiceItemModel.nilai).label('nominal')
                      ).filter(SppItemModel.spp_id==SppModel.id, SppItemModel.apinvoice_id==APInvoiceModel.id,
                      APInvoiceItemModel.apinvoice_id==APInvoiceModel.id, APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                      KegiatanItemModel.rekening_id==RekeningModel.id,
                      SppModel.unit_id==Unit.id, SppModel.unit_id==self.unit_id,
                      SppModel.tahun_id==self.session['tahun'],
                      SpmModel.tanggal.between(mulai,selesai)        
                      ).outerjoin(SpmModel,SpmModel.spp_id==SppModel.id
                      ).outerjoin(Sp2dModel,Sp2dModel.spm_id==SpmModel.id
                      ).group_by(SppModel.tahun_id, Unit.nama,
                      case([(SppModel.jenis==1,"UP"),(SppModel.jenis==2,"TU"),(SppModel.jenis==3,"GU"),(SppModel.jenis==4,"LS")], else_=""),
                      SppModel.kode, SppModel.nama, SppModel.tanggal,
                      SpmModel.kode, SpmModel.tanggal,
                      Sp2dModel.kode, Sp2dModel.tanggal
                      ).order_by(SppModel.tanggal).all()

                else:
                    query = DBSession.query(SppModel.tahun_id.label('tahun'), Unit.nama.label('unit_nm'),
                      case([(SppModel.jenis==1,"UP"),(SppModel.jenis==2,"TU"),(SppModel.jenis==3,"GU"),(SppModel.jenis==4,"LS")], else_="").label('jenis'),
                      SppModel.kode.label('spp_kd'), SppModel.nama.label('spp_nm'), SppModel.tanggal.label('tgl_spp'),
                      SpmModel.kode.label('spm_kd'), SpmModel.tanggal.label('tgl_spm'),
                      Sp2dModel.kode.label('sp2d_kd'), Sp2dModel.tanggal.label('tgl_sp2d'),
                      func.sum(APInvoiceItemModel.nilai).label('nominal')
                      ).filter(SppItemModel.spp_id==SppModel.id, SppItemModel.apinvoice_id==APInvoiceModel.id,
                      APInvoiceItemModel.apinvoice_id==APInvoiceModel.id, APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                      KegiatanItemModel.rekening_id==RekeningModel.id,
                      SppModel.unit_id==Unit.id, SppModel.unit_id==self.unit_id,
                      SppModel.tahun_id==self.session['tahun'], SppModel.jenis==tipe, 
                      SpmModel.tanggal.between(mulai,selesai)
                      ).outerjoin(SpmModel,SpmModel.spp_id==SppModel.id
                      ).outerjoin(Sp2dModel,Sp2dModel.spm_id==SpmModel.id
                      ).group_by(SppModel.tahun_id, Unit.nama,
                      case([(SppModel.jenis==1,"UP"),(SppModel.jenis==2,"TU"),(SppModel.jenis==3,"GU"),(SppModel.jenis==4,"LS")], else_=""),
                      SppModel.kode, SppModel.nama, SppModel.tanggal,
                      SpmModel.kode, SpmModel.tanggal,
                      Sp2dModel.kode, Sp2dModel.tanggal,
                      ).order_by(SppModel.tanggal).all()
                     
                generator = b104r2001Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif url_dict['act']=='2' and self.is_akses_mod('read'):
                if tipe ==0 :
                    query = DBSession.query(SppModel.tahun_id.label('tahun'), 
                      Unit.nama.label('unit_nm'), SpmModel.tanggal.label('tgl_spp'), 
                      SpmModel.kode.label('spp_kd'), SpmModel.nama.label('spp_nm'),
                      func.sum(case([(SppModel.jenis==1,APInvoiceItemModel.nilai)], else_=0)).label('UP'),
                      func.sum(case([(SppModel.jenis==2,APInvoiceItemModel.nilai)], else_=0)).label('GU'),
                      func.sum(case([(SppModel.jenis==3,APInvoiceItemModel.nilai)], else_=0)).label('TU'),
                      func.sum(case([(and_(SppModel.jenis==4,func.substr(RekeningModel.kode,1,5)=='5.2.1'),APInvoiceItemModel.nilai)], else_=0)).label('LS_GJ'),
                      func.sum(case([(and_(SppModel.jenis==4,not_(func.substr(RekeningModel.kode,1,5)=='5.2.1')),APInvoiceItemModel.nilai)], else_=0)).label('LS')
                      ).filter(SppItemModel.spp_id==SppModel.id, SppItemModel.apinvoice_id==APInvoiceModel.id,
                      APInvoiceItemModel.apinvoice_id==APInvoiceModel.id, APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                      KegiatanItemModel.rekening_id==RekeningModel.id,
                      SppModel.unit_id==Unit.id, SppModel.unit_id==self.unit_id,
                      SppModel.tahun_id==self.session['tahun'],  
                      SpmModel.tanggal.between(mulai,selesai)        
                      ).outerjoin(SpmModel,SpmModel.spp_id==SppModel.id
                      ).outerjoin(Sp2dModel,Sp2dModel.spm_id==SpmModel.id
                      ).group_by(SppModel.tahun_id, Unit.nama, SpmModel.tanggal, 
                      SpmModel.kode, SpmModel.nama
                      ).order_by(SpmModel.tanggal).all()
                else:
                    query = DBSession.query(SppModel.tahun_id.label('tahun'), 
                      Unit.nama.label('unit_nm'), SpmModel.tanggal.label('tgl_spp'), 
                      SpmModel.kode.label('spp_kd'), SpmModel.nama.label('spp_nm'),
                      func.sum(case([(SppModel.jenis==1,APInvoiceItemModel.nilai)], else_=0)).label('UP'),
                      func.sum(case([(SppModel.jenis==2,APInvoiceItemModel.nilai)], else_=0)).label('GU'),
                      func.sum(case([(SppModel.jenis==3,APInvoiceItemModel.nilai)], else_=0)).label('TU'),
                      func.sum(case([(and_(SppModel.jenis==4,func.substr(RekeningModel.kode,1,5)=='5.2.1'),APInvoiceItemModel.nilai)], else_=0)).label('LS_GJ'),
                      func.sum(case([(and_(SppModel.jenis==4,not_(func.substr(RekeningModel.kode,1,5)=='5.2.1')),APInvoiceItemModel.nilai)], else_=0)).label('LS')
                      ).outerjoin(SpmModel,SpmModel.spp_id==SppModel.id
                      ).outerjoin(Sp2dModel,Sp2dModel.spm_id==SpmModel.id
                      ).filter(SppItemModel.spp_id==SppModel.id, SppItemModel.apinvoice_id==APInvoiceModel.id,
                      APInvoiceItemModel.apinvoice_id==APInvoiceModel.id, APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                      KegiatanItemModel.rekening_id==RekeningModel.id,
                      SppModel.unit_id==Unit.id, SppModel.unit_id==self.unit_id,
                      SppModel.tahun_id==self.session['tahun'], SppModel.jenis==tipe,   
                      SpmModel.tanggal.between(mulai,selesai)        
                      ).group_by(SppModel.tahun_id, Unit.nama, SpmModel.tanggal, 
                      SpmModel.kode, SpmModel.nama
                      ).order_by(SpmModel.tanggal).all()

                generator = b104r2002Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif url_dict['act']=='3' and self.is_akses_mod('read'):
                if tipe ==0 :
                    query = DBSession.query(SppModel.tahun_id.label('tahun'), 
                      Unit.nama.label('unit_nm'), SppModel.tanggal.label('tgl_spp'), 
                      SppModel.kode.label('spp_kd'), SppModel.nama.label('spp_nm'),
                      case([(SppModel.jenis==1,SppModel.nominal)], else_=0).label('UP'),
                      case([(SppModel.jenis==2,SppModel.nominal)], else_=0).label('GU'),
                      case([(SppModel.jenis==3,SppModel.nominal)], else_=0).label('TU'),
                      case([(SppModel.jenis==4,SppModel.nominal)], else_=0).label('LS'),
                      ).filter(SppModel.unit_id==Unit.id, SppModel.unit_id==self.unit_id,
                      SppModel.tahun_id==self.session['tahun'], 
                      SppModel.tanggal.between(mulai,selesai)        
                      ).order_by(SppModel.tanggal).all()
                else:
                    query = DBSession.query(SppModel.tahun_id.label('tahun'), 
                      Unit.nama.label('unit_nm'), SppModel.tanggal.label('tgl_spp'), 
                      SppModel.kode.label('spp_kd'), SppModel.nama.label('spp_nm'),
                      case([(SppModel.jenis==1,SppModel.nominal)], else_=0).label('UP'),
                      case([(SppModel.jenis==2,SppModel.nominal)], else_=0).label('GU'),
                      case([(SppModel.jenis==3,SppModel.nominal)], else_=0).label('TU'),
                      case([(SppModel.jenis==4,SppModel.nominal)], else_=0).label('LS'),
                      ).filter(SppModel.unit_id==Unit.id, SppModel.unit_id==self.unit_id,
                      SppModel.tahun_id==self.session['tahun'], SppModel.jenis==tipe, 
                      SppModel.tanggal.between(mulai,selesai)        
                      ).order_by(SppModel.tanggal).all()
                      
                generator = b104r2003Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif url_dict['act']=='4' and self.is_akses_mod('read'):
                if tipe ==0 :
                    query = DBSession.query(SppModel.tahun_id.label('tahun'), 
                      Unit.nama.label('unit_nm'), SppModel.tanggal.label('tgl_spm'), 
                      SppModel.kode.label('spm_kd'), SppModel.nama.label('spm_nm'),
                      case([(SppModel.nominal==1,SppModel.nominal)], else_=0).label('BRUTO'),
                      case([(SppModel.nominal==2,SppModel.nominal)], else_=0).label('POTONGAN'),
                      case([(SppModel.nominal==3,SppModel.nominal)], else_=0).label('NETTO'),
                      case([(SppModel.nominal==4,SppModel.nominal)], else_=0).label('INFORMASI')
                      ).filter(SppModel.unit_id==Unit.id, SppModel.unit_id==self.unit_id,
                      SppModel.tahun_id==self.session['tahun'], 
                      SppModel.tanggal.between(mulai,selesai)        
                      ).order_by(SppModel.tanggal).all()
                else:
                    query = DBSession.query(SppModel.tahun_id.label('tahun'), 
                      Unit.nama.label('unit_nm'), SppModel.tanggal.label('tgl_spm'), 
                      SppModel.kode.label('spm_kd'), SppModel.nama.label('spm_nm'),
                      case([(SppModel.nominal==1,SppModel.nominal)], else_=0).label('BRUTO'),
                      case([(SppModel.nominal==2,SppModel.nominal)], else_=0).label('POTONGAN'),
                      case([(SppModel.nominal==3,SppModel.nominal)], else_=0).label('NETTO'),
                      case([(SppModel.nominal==4,SppModel.nominal)], else_=0).label('INFORMASI')
                      ).filter(SppModel.unit_id==Unit.id, SppModel.unit_id==self.unit_id,
                      SppModel.tahun_id==self.session['tahun'], SppModel.jenis==tipe, 
                      SppModel.tanggal.between(mulai,selesai)        
                      ).order_by(SppModel.tanggal).all()
                    
                generator = b104r2004Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

# SPJ Fungsional
    @view_config(route_name="b104_r300", renderer="osipkd:templates/apbd/tuskpd/b104r300.pt")
    def b104_r300(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas,)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b104_r300_act")
    def b104_r300_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            bulan = 'bulan' in params and params['bulan'] and int(params['bulan']) or 0
            if url_dict['act']=='1' and self.is_akses_mod('read'):
                query = DBSession.query(APInvoiceModel
                      ).filter(APInvoiceModel.unit_id==Unit.id, APInvoiceModel.kegiatan_sub_id==KegiatanSubModel.id,
                      APInvoiceModel.id==APInvoiceItemModel.apinvoice_id, APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                      KegiatanItemModel.rekening_id==RekeningModel.id, APInvoiceModel.unit_id==self.unit_id,
                      APInvoiceModel.tahun_id==self.session['tahun'],  
                      ).order_by(APInvoiceModel.ap_tanggal).all()
                generator = b104r300Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

# SPJ Administratif
    @view_config(route_name="b104_r400", renderer="osipkd:templates/apbd/tuskpd/b104r400.pt")
    def b104_r400(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas,)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b104_r400_act")
    def b104_r400_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            bulan = 'bulan' in params and params['bulan'] and int(params['bulan']) or 0
            if url_dict['act']=='1' and self.is_akses_mod('read'):
                query = DBSession.query(APInvoiceModel
                      ).filter(APInvoiceModel.unit_id==Unit.id, APInvoiceModel.kegiatan_sub_id==KegiatanSubModel.id,
                      APInvoiceModel.id==APInvoiceItemModel.apinvoice_id, APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                      KegiatanItemModel.rekening_id==RekeningModel.id, APInvoiceModel.unit_id==self.unit_id,
                      APInvoiceModel.tahun_id==self.session['tahun'],  
                      ).order_by(APInvoiceModel.ap_tanggal).all()
                generator = b104r400Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
