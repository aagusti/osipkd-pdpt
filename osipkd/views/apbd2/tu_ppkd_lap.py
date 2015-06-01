import unittest
import os.path
import sqlalchemy
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from pyramid.security import remember
from pyramid.security import forget
from pyramid.security import has_permission
from sqlalchemy import *
from sqlalchemy import distinct
from sqlalchemy import text
from sqlalchemy.sql.functions import concat
from sqlalchemy.sql.expression import literal_column
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

#SPD
class b203r003Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b203r003Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R203003.jrxml')
        self.xpath = '/apbd/spd'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spd')
            ET.SubElement(xml_greeting, "kode").text = row.kode
            ET.SubElement(xml_greeting, "nama").text = row.nama
            ET.SubElement(xml_greeting, "tahun_id").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "triwulan_id").text = unicode(row.triwulan_id)
            ET.SubElement(xml_greeting, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_greeting, "is_bl").text = unicode(row.is_bl)
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "no_perda").text = row.no_perda
            ET.SubElement(xml_greeting, "tgl_perda").text = unicode(row.tgl_perda)
            ET.SubElement(xml_greeting, "no_perkdh").text = row.no_perkdh
            ET.SubElement(xml_greeting, "tgl_perkdh").text = unicode(row.tgl_perkdh)
            ET.SubElement(xml_greeting, "no_perda_rev").text = row.no_perda_rev
            ET.SubElement(xml_greeting, "tgl_perda_rev").text = unicode(row.tgl_perda_rev)
            ET.SubElement(xml_greeting, "no_perkdh_rev").text = row.no_perkdh_rev
            ET.SubElement(xml_greeting, "tgl_perkdh_rev").text = unicode(row.tgl_perkdh_rev)
            ET.SubElement(xml_greeting, "nominal").text = unicode(row.nominal)
            ET.SubElement(xml_greeting, "anggaran").text = unicode(row.anggaran)
            ET.SubElement(xml_greeting, "lalu").text = unicode(row.lalu)
            
        return self.root

#SP2D
class b203r001Generator(JasperGeneratorWithSubreport):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        self.mainreport = get_rpath('apbd/tuppkd/R203001.jrxml')

        self.subreportlist = []
        self.subreportlist.append(get_rpath('apbd/tuppkd/R203001_subreport1.jrxml'))
        self.subreportlist.append(get_rpath('apbd/tuppkd/R203001_subreport2.jrxml'))

        #        for filename in os.listdir(os.path.abspath(self.reportrootdir)):
        #            if filename.startswith(self.reportbase + '-subreport'):
        #                self.subreportlist.append(os.path.join(self.reportrootdir, filename))
        
        self.xpath = '/apbd/sp2d'
        
        self.root = ET.Element('apbd')

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'sp2d')
            ET.SubElement(xml_greeting, "sp2d_id").text = unicode(row.sp2d_id)
            ET.SubElement(xml_greeting, "sp2d_kd").text = row.sp2d_kd
            ET.SubElement(xml_greeting, "sp2d_tgl").text = unicode(row.sp2d_tgl)
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

        return self.root

#GIRO
class b203r002Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b203r002Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R203002.jrxml')
        self.xpath = '/apbd/spd'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spd')
            ET.SubElement(xml_greeting, "kode").text = row.kode
            ET.SubElement(xml_greeting, "nama").text = row.nama
            ET.SubElement(xml_greeting, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_greeting, "nominal").text = unicode(row.nominal)
            ET.SubElement(xml_greeting, "sp2d_kd").text = row.sp2d_kd
            ET.SubElement(xml_greeting, "spm_nm").text = row.spm_nm
            ET.SubElement(xml_greeting, "bank_nama").text = row.bank_nama
            ET.SubElement(xml_greeting, "bank_account").text = row.bank_account
            ET.SubElement(xml_greeting, "ap_bank").text = row.ap_bank
            ET.SubElement(xml_greeting, "ap_rekening").text = row.ap_rekening
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
        return self.root
        
# Register SP2D
class b204r000Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b204r000Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R204000.jrxml')
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

class b204r0001Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b204r0001Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R2040001.jrxml')
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


#Realisasi
class b204r100Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b204r100Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R204100.jrxml')
        self.xpath = '/apbd/realisasi'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'realisasi')
            ET.SubElement(xml_greeting, "bulan").text = unicode(bln)
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_greeting, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "jumlah").text = unicode(row.jumlah)
            ET.SubElement(xml_greeting, "realisasi").text = unicode(row.realisasi)
        return self.root

#Realisasi SKPD Kegiatan
class b204r200Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b204r200Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R204200.jrxml')
        self.xpath = '/apbd/realisasi'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'realisasi')
            ET.SubElement(xml_greeting, "tahun_id").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "bulan").text = unicode(bln)
            ET.SubElement(xml_greeting, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_greeting, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_greeting, "unit_id").text = unicode(row.unit_id)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "program_kd").text = row.program_kd
            ET.SubElement(xml_greeting, "program_nm").text = row.program_nm
            ET.SubElement(xml_greeting, "kegiatan_kd").text = row.kegiatan_kd
            ET.SubElement(xml_greeting, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_greeting, "jenis").text = unicode(row.jenis)
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_greeting, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_greeting, "rekening_id").text = unicode(row.rekening_id)
            ET.SubElement(xml_greeting, "jumlah").text = unicode(row.jumlah)
            ET.SubElement(xml_greeting, "realisasi").text = unicode(row.realisasi)
        return self.root

#Realisasi SKPD
class b204r300Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(b204r300Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R204300.jrxml')
        self.xpath = '/apbd/realisasi'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'realisasi')
            ET.SubElement(xml_greeting, "unit_nm").text = unit_nama
            ET.SubElement(xml_greeting, "bulan").text = unicode(bln)
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_greeting, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "jumlah").text = unicode(row.jumlah)
            ET.SubElement(xml_greeting, "realisasi").text = unicode(row.realisasi)
        return self.root

class ViewTUPPKDLap(BaseViews):
    def __init__(self, context, request):
        BaseViews.__init__(self, context, request)
        self.app = 'tuppkd'

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

        #bulan = 'bulan' in request.params and request.params['bulan'] and int(request.params['bulan']) or 0
        
#SPD
    @view_config(route_name="b203_r003_act")
    def b203_r003_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if self.is_akses_mod('read'):
                query = DBSession.query(SpdModel.kode, SpdModel.nama, SpdModel.tahun_id,
                   SpdModel.triwulan_id, SpdModel.tanggal, SpdModel.is_bl, Unit.nama.label('unit_nm'),
                   TahunModel.no_perda, TahunModel.tgl_perda, TahunModel.no_perkdh, TahunModel.tgl_perkdh,
                   TahunModel.no_perda_rev, TahunModel.tgl_perda_rev, TahunModel.no_perkdh_rev, TahunModel.tgl_perkdh_rev,
                   func.sum(SpdItemModel.nominal).label('nominal'), func.sum(SpdItemModel.anggaran).label('anggaran'),
                   func.sum(SpdItemModel.lalu).label('lalu')
                   ).filter(SpdModel.unit_id==Unit.id, SpdModel.id==SpdItemModel.spd_id,
                   SpdModel.tahun_id==TahunModel.id, SpdModel.tahun_id==self.tahun, 
                   SpdModel.unit_id==self.unit_id, SpdModel.id==pk_id
                   ).group_by(SpdModel.kode, SpdModel.nama, SpdModel.tahun_id,
                   SpdModel.triwulan_id, SpdModel.tanggal, SpdModel.is_bl, Unit.nama,
                   TahunModel.no_perda, TahunModel.tgl_perda, TahunModel.no_perkdh, TahunModel.tgl_perkdh,
                   TahunModel.no_perda_rev, TahunModel.tgl_perda_rev, TahunModel.no_perkdh_rev, TahunModel.tgl_perkdh_rev
                   )
                   
                generator = b203r003Generator()
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
#SP2D
    @view_config(route_name="b203_r001_act")
    def b203_r001_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if self.is_akses_mod('read'):
                '''subq = DBSession.query(SppModel.id.label('sspp_id'), func.sum(APInvoiceItemModel.nilai).label('potongan')
                  ).filter(SppModel.id==SppItemModel.spp_id, 
                    SppItemModel.apinvoice_id==APInvoiceItemModel.apinvoice_id,
                    APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                    KegiatanItemModel.rekening_id==RekeningModel.id,
                    func.substr(RekeningModel.kode,1,1)=='7'
                  ).group_by(SppModel.id
                  ).subquery()
                  
                query = DBSession.query(Sp2dModel.id.label('sp2d_id'), SppModel.id.label('spp_id'),
                  Sp2dModel.kode.label('sp2d_kd'), SppModel.tahun_id.label('tahun'), SppModel.jenis, 
                  Unit.nama.label('unit_nm'), SpmModel.kode.label('spm_kd'),
                  SpmModel.nama.label('spm_nm'), SpmModel.tanggal.label('spm_tgl'),
                  SppModel.bank_nama, SppModel.bank_account, SppModel.ap_nama,
                  SppModel.ap_bank, SppModel.ap_bank, SppModel.ap_rekening, SppModel.ap_npwp,
                  func.sum(APInvoiceItemModel.nilai).label('nominal'),
                  func.sum(APInvoiceItemModel.ppn).label('ppn'),
                  func.sum(APInvoiceItemModel.pph).label('pph'),
                  ).filter( Sp2dModel.spm_id==SpmModel.id, SpmModel.spp_id==SppModel.id,
                  SppModel.unit_id==Unit.id, SppItemModel.spp_id==SppModel.id,
                  SppItemModel.apinvoice_id==APInvoiceItemModel.apinvoice_id,
                  SppModel.tahun_id==self.tahun, SppModel.unit_id==self.unit_id, Sp2dModel.id==pk_id
                  ).group_by(Sp2dModel.id.label('sp2d_id'), SppModel.id.label('spp_id'),
                  Sp2dModel.kode, SppModel.tahun_id, SppModel.jenis, Unit.nama, SpmModel.kode,
                  SpmModel.nama, SpmModel.tanggal, SppModel.bank_nama, SppModel.bank_account, SppModel.ap_nama,
                  SppModel.ap_bank, SppModel.ap_bank, SppModel.ap_rekening, SppModel.ap_npwp
                  )
                '''
                
                subq1 = DBSession.query(Sp2dModel.id.label('sp2d_id'), Sp2dModel.kode.label('sp2d_kd'), Sp2dModel.tanggal.label('sp2d_tgl'), 
                         SpmModel.id.label('spm_id'), SpmModel.kode.label('spm_kd'), SpmModel.nama.label('spm_nm'), SpmModel.tanggal.label('spm_tgl'), SppModel.id.label('spp_id'), 
                         SppModel.kode.label('spp_kd'), SppModel.nama.label('spp_nm'), SppModel.tanggal.label('spp_tgl'), SppModel.jenis.label('jenis'), 
                         SppModel.bank_nama.label('bank_nama'), SppModel.bank_account.label('bank_account'), SppModel.ap_nama.label('ap_nama'), SppModel.ap_bank.label('ap_bank'), SppModel.ap_rekening.label('ap_rekening'), SppModel.ap_npwp.label('ap_npwp'), 
                         SppModel.tahun_id.label('tahun_id'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), KegiatanModel.kode.label('keg_kd'), 
                         KegiatanModel.nama.label('keg_nm'), ProgramModel.kode.label('prg_kd'), ProgramModel.nama.label('prg_nm'), 
                         func.sum(APInvoiceItemModel.nilai).label('nilai'), func.sum(APInvoiceItemModel.ppn).label('ppn'), 
                         func.sum(APInvoiceItemModel.pph).label('pph'), literal_column('0').label('potongan')
                         ).filter(Sp2dModel.spm_id==SpmModel.id, SpmModel.spp_id==SppModel.id, SppModel.unit_id==Unit.id,
                         SppItemModel.spp_id==SppModel.id, SppItemModel.apinvoice_id==APInvoiceItemModel.apinvoice_id, APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                         KegiatanItemModel.rekening_id==RekeningModel.id, KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                         KegiatanSubModel.kegiatan_id==KegiatanModel.id, KegiatanModel.program_id==ProgramModel.id,
                         SppModel.unit_id==self.unit_id, SppModel.tahun_id==self.tahun, Sp2dModel.id==pk_id,
                         func.left(RekeningModel.kode,1)=='5'
                         ).group_by(Sp2dModel.id, Sp2dModel.kode, Sp2dModel.tanggal, SpmModel.id, SpmModel.kode, 
                         SpmModel.nama, SpmModel.tanggal, SppModel.id, SppModel.kode, SppModel.nama, SppModel.tanggal, 
                         SppModel.jenis, SppModel.bank_nama, SppModel.bank_account, SppModel.ap_nama, SppModel.ap_bank, 
                         SppModel.ap_rekening, SppModel.ap_npwp, SppModel.tahun_id, Unit.kode, Unit.nama, 
                         KegiatanModel.kode, KegiatanModel.nama, ProgramModel.kode, ProgramModel.nama 
                         )                         

                subq2 = DBSession.query(Sp2dModel.id.label('sp2d_id'), Sp2dModel.kode.label('sp2d_kd'), Sp2dModel.tanggal.label('sp2d_tgl'), 
                         SpmModel.id.label('spm_id'), SpmModel.kode.label('spm_kd'), SpmModel.nama.label('spm_nm'), SpmModel.tanggal.label('spm_tgl'), SppModel.id.label('spp_id'), 
                         SppModel.kode.label('spp_kd'), SppModel.nama.label('spp_nm'), SppModel.tanggal.label('spp_tgl'), SppModel.jenis.label('jenis'), 
                         SppModel.bank_nama.label('bank_nama'), SppModel.bank_account.label('bank_account'), SppModel.ap_nama.label('ap_nama'), SppModel.ap_bank.label('ap_bank'), SppModel.ap_rekening.label('ap_rekening'), SppModel.ap_npwp.label('ap_npwp'), 
                         SppModel.tahun_id.label('tahun_id'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), KegiatanModel.kode.label('keg_kd'), 
                         KegiatanModel.nama.label('keg_nm'), ProgramModel.kode.label('prg_kd'), ProgramModel.nama.label('prg_nm'), 
                         literal_column('0').label('nilai'), literal_column('0').label('ppn'), 
                         literal_column('0').label('pph'), func.sum(APInvoiceItemModel.nilai).label('potongan')
                         ).filter(Sp2dModel.spm_id==SpmModel.id, SpmModel.spp_id==SppModel.id, SppModel.unit_id==Unit.id,
                         SppItemModel.spp_id==SppModel.id, SppItemModel.apinvoice_id==APInvoiceItemModel.apinvoice_id, APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                         KegiatanItemModel.rekening_id==RekeningModel.id, KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                         KegiatanSubModel.kegiatan_id==KegiatanModel.id, KegiatanModel.program_id==ProgramModel.id,
                         SppModel.unit_id==self.unit_id, SppModel.tahun_id==self.tahun, Sp2dModel.id==pk_id,
                         func.left(RekeningModel.kode,1)=='7'
                         ).group_by(Sp2dModel.id, Sp2dModel.kode, Sp2dModel.tanggal, SpmModel.id, SpmModel.kode, 
                         SpmModel.nama, SpmModel.tanggal, SppModel.id, SppModel.kode, SppModel.nama, SppModel.tanggal, 
                         SppModel.jenis, SppModel.bank_nama, SppModel.bank_account, SppModel.ap_nama, SppModel.ap_bank, 
                         SppModel.ap_rekening, SppModel.ap_npwp, SppModel.tahun_id, Unit.kode, Unit.nama, 
                         KegiatanModel.kode, KegiatanModel.nama, ProgramModel.kode, ProgramModel.nama 
                         )                         
                
                subq = subq1.union(subq2).subquery()
                
                query = DBSession.query(subq.c.sp2d_id, subq.c.sp2d_kd, subq.c.sp2d_tgl, subq.c.spm_id, subq.c.spm_kd, 
                         subq.c.spm_nm, subq.c.spm_tgl, subq.c.spp_id, subq.c.spp_kd, subq.c.spp_nm, subq.c.spp_tgl, 
                         subq.c.jenis, subq.c.bank_nama, subq.c.bank_account, subq.c.ap_nama, subq.c.ap_bank, subq.c.ap_rekening, 
                         subq.c.ap_npwp, subq.c.tahun_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.keg_kd, subq.c.keg_nm, subq.c.prg_kd, 
                         subq.c.prg_nm, func.sum(subq.c.nilai).label('nilai'),func.sum(subq.c.ppn).label('ppn'), 
                         func.sum(subq.c.pph).label('pph'),func.sum(subq.c.potongan).label('potongan')
                         ).group_by(subq.c.sp2d_id, subq.c.sp2d_kd, subq.c.sp2d_tgl, subq.c.spm_id, subq.c.spm_kd, 
                         subq.c.spm_nm, subq.c.spm_tgl, subq.c.spp_id, subq.c.spp_kd, subq.c.spp_nm, subq.c.spp_tgl, 
                         subq.c.jenis, subq.c.bank_nama, subq.c.bank_account, subq.c.ap_nama, subq.c.ap_bank, subq.c.ap_rekening, 
                         subq.c.ap_npwp, subq.c.tahun_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.keg_kd, subq.c.keg_nm, subq.c.prg_kd, 
                         subq.c.prg_nm
                         )                         

                generator = b203r001Generator()
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
#GIRO
    @view_config(route_name="b203_r002_act")
    def b203_r002_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            #pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if self.is_akses_mod('read'):
                query = DBSession.query(GiroModel.kode, GiroModel.nama, GiroModel.tanggal,
                   GiroModel.nominal, Sp2dModel.kode.label('sp2d_kd'), SpmModel.nama.label('spm_nm'),
                   SppModel.bank_nama, SppModel.bank_account, SppModel.ap_bank, SppModel.ap_rekening,
                   Unit.nama.label('unit_nm')
                   ).filter(GiroModel.sp2d_id==Sp2dModel.id, Sp2dModel.spm_id==SpmModel.id,
                   SpmModel.spp_id==SppModel.id, GiroModel.tahun_id==self.tahun, GiroModel.unit_id==Unit.id,
                   GiroModel.unit_id==self.unit_id
                   ).order_by(GiroModel.tanggal).all()
                   
                generator = b203r002Generator()
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
            
#LAP SP2D
    @view_config(route_name="b204_r000", renderer="osipkd:templates/apbd/tuppkd/b204r000.pt")
    def b204_r000(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas,)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b204_r000_act")
    def b204_r000_act(self):
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
                      Sp2dModel.tanggal.between(mulai,selesai)        
                      ).outerjoin(SpmModel,SpmModel.spp_id==SppModel.id
                      ).outerjoin(Sp2dModel,Sp2dModel.spm_id==SpmModel.id
                      ).group_by(SppModel.tahun_id, Unit.nama,
                      case([(SppModel.jenis==1,"UP"),(SppModel.jenis==2,"TU"),(SppModel.jenis==3,"GU"),(SppModel.jenis==4,"LS")], else_=""),
                      SppModel.kode, SppModel.nama, SppModel.tanggal,
                      SpmModel.kode, SpmModel.tanggal,
                      Sp2dModel.kode, Sp2dModel.tanggal
                      ).order_by(Sp2dModel.tanggal).all()

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
                      Sp2dModel.tanggal.between(mulai,selesai)
                      ).outerjoin(SpmModel,SpmModel.spp_id==SppModel.id
                      ).outerjoin(Sp2dModel,Sp2dModel.spm_id==SpmModel.id
                      ).group_by(SppModel.tahun_id, Unit.nama,
                      case([(SppModel.jenis==1,"UP"),(SppModel.jenis==2,"TU"),(SppModel.jenis==3,"GU"),(SppModel.jenis==4,"LS")], else_=""),
                      SppModel.kode, SppModel.nama, SppModel.tanggal,
                      SpmModel.kode, SpmModel.tanggal,
                      Sp2dModel.kode, Sp2dModel.tanggal,
                      ).order_by(Sp2dModel.tanggal).all()
                     
                generator = b204r000Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif url_dict['act']=='2' and self.is_akses_mod('read'):
                if tipe ==0 :
                    query = DBSession.query(SppModel.tahun_id.label('tahun'), 
                      Unit.nama.label('unit_nm'), Sp2dModel.tanggal.label('tgl_spp'), 
                      Sp2dModel.kode.label('spp_kd'), SppModel.nama.label('spp_nm'),
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
                      Sp2dModel.tanggal.between(mulai,selesai)        
                      ).outerjoin(SpmModel,SpmModel.spp_id==SppModel.id
                      ).outerjoin(Sp2dModel,Sp2dModel.spm_id==SpmModel.id
                      ).group_by(SppModel.tahun_id, Unit.nama, Sp2dModel.tanggal, 
                      Sp2dModel.kode, SppModel.nama
                      ).order_by(Sp2dModel.tanggal).all()
                else:
                    query = DBSession.query(SppModel.tahun_id.label('tahun'), 
                      Unit.nama.label('unit_nm'), Sp2dModel.tanggal.label('tgl_spp'), 
                      Sp2dModel.kode.label('spp_kd'), SppModel.nama.label('spp_nm'),
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
                      Sp2dModel.tanggal.between(mulai,selesai)        
                      ).group_by(SppModel.tahun_id, Unit.nama, Sp2dModel.tanggal, 
                      Sp2dModel.kode, SppModel.nama
                      ).order_by(Sp2dModel.tanggal).all()

                generator = b204r0001Generator()
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

#Lap Realisasi Anggaran
    @view_config(route_name="b204_r100", renderer="osipkd:templates/apbd/tuppkd/b204r100.pt")
    def b204_r100(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas,)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b204_r100_act")
    def b204_r100_act(self):
        global bln
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            bln = 'bulan' in params and params['bulan'] and int(params['bulan']) or 0
            if url_dict['act']=='1' and self.is_akses_mod('read'):
                subq1 = (DBSession.query(RekeningModel.kode.label('subrek_kd'),RekeningModel.nama.label('subrek_nm'),
                    KegiatanSubModel.tahun_id.label('tahun_id'),
                    (KegiatanItemModel.vol_4_1* KegiatanItemModel.vol_4_2*KegiatanItemModel.hsat_4).label('jml'), 
                    sqlalchemy.sql.literal_column("0").label('realisasi')
                    ).filter(KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                            KegiatanItemModel.rekening_id==RekeningModel.id,
                            KegiatanSubModel.tahun_id==self.tahun
                    ).union(DBSession.query(
                    RekeningModel.kode.label('subrek_kd'),RekeningModel.nama.label('subrek_nm'),
                    SppModel.tahun_id.label('tahun_id'), sqlalchemy.sql.literal_column("0").label('jml'),
                    func.max(APInvoiceItemModel.nilai).label('realisasi')
                    ).filter(APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                            APInvoiceItemModel.apinvoice_id==APInvoiceModel.id,
                            KegiatanItemModel.rekening_id==RekeningModel.id,
                            SppItemModel.apinvoice_id==APInvoiceModel.id,
                            SppItemModel.spp_id==SppModel.id,
                            SpmModel.spp_id==SppModel.id,                            
                            Sp2dModel.spm_id==SpmModel.id, 
                            SppModel.tahun_id==self.tahun, extract('month',Sp2dModel.tanggal) <= bln
                    ).group_by(RekeningModel.kode, RekeningModel.nama, SppModel.tahun_id
                    ))).subquery()
   
                subq2 = DBSession.query(subq1.c.subrek_kd.label('subrek_kd'), subq1.c.subrek_nm.label('subrek_nm'), 
                    subq1.c.tahun_id.label('tahun_id'), 
                    func.sum(subq1.c.jml).label('jml'), func.sum(subq1.c.realisasi).label('realisasi')
                    ).group_by(subq1.c.subrek_kd, subq1.c.subrek_nm, subq1.c.tahun_id).subquery()                    

                query = DBSession.query(RekeningModel.kode.label('rek_kd'), RekeningModel.nama.label('rek_nm'),
                    RekeningModel.level_id, RekeningModel.defsign, subq2.c.tahun_id, 
                    func.sum(subq2.c.jml).label('jumlah'),
                    func.sum(subq2.c.realisasi).label('realisasi'),
                    ).filter(RekeningModel.kode==func.left(subq2.c.subrek_kd, func.length(RekeningModel.kode)),
                    RekeningModel.level_id<3)\
                    .group_by(RekeningModel.kode, RekeningModel.nama,
                    RekeningModel.level_id, RekeningModel.defsign, subq2.c.tahun_id)\
                    .order_by(RekeningModel.kode).all()                    

                generator = b204r100Generator()
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

#LAP Realisasi Anggaran/SKPD
    @view_config(route_name="b204_r300", renderer="osipkd:templates/apbd/tuppkd/b204r300.pt")
    def b204_r300(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas,)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b204_r300_act")
    def b204_r300_act(self):
        global bln, unit_nama
        unit_nama = self.unit_nm
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            bln = 'bulan' in params and params['bulan'] and int(params['bulan']) or 0
            if url_dict['act']=='1' and self.is_akses_mod('read'):
                subq1 = (DBSession.query(RekeningModel.kode.label('subrek_kd'),RekeningModel.nama.label('subrek_nm'),
                    KegiatanSubModel.tahun_id.label('tahun_id'),
                    (KegiatanItemModel.vol_4_1* KegiatanItemModel.vol_4_2*KegiatanItemModel.hsat_4).label('jml'), 
                    sqlalchemy.sql.literal_column("0").label('realisasi')
                    ).filter(KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                            KegiatanItemModel.rekening_id==RekeningModel.id,
                            KegiatanSubModel.tahun_id==self.tahun, KegiatanSubModel.unit_id==self.unit_id
                    ).union(DBSession.query(
                    RekeningModel.kode.label('subrek_kd'),RekeningModel.nama.label('subrek_nm'),
                    SppModel.tahun_id.label('tahun_id'), sqlalchemy.sql.literal_column("0").label('jml'),
                    func.max(APInvoiceItemModel.nilai).label('realisasi')
                    ).filter(APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                            APInvoiceItemModel.apinvoice_id==APInvoiceModel.id,
                            KegiatanItemModel.rekening_id==RekeningModel.id,
                            SppItemModel.apinvoice_id==APInvoiceModel.id,
                            SppItemModel.spp_id==SppModel.id,
                            SpmModel.spp_id==SppModel.id,                            
                            Sp2dModel.spm_id==SpmModel.id, 
                            SppModel.tahun_id==self.tahun, extract('month',Sp2dModel.tanggal) <= bln,
                            SppModel.unit_id==self.unit_id
                    ).group_by(RekeningModel.kode, RekeningModel.nama, SppModel.tahun_id
                    ))).subquery()
   
                subq2 = DBSession.query(subq1.c.subrek_kd.label('subrek_kd'), subq1.c.subrek_nm.label('subrek_nm'), 
                    subq1.c.tahun_id.label('tahun_id'), 
                    func.sum(subq1.c.jml).label('jml'), func.sum(subq1.c.realisasi).label('realisasi')
                    ).group_by(subq1.c.subrek_kd, subq1.c.subrek_nm, subq1.c.tahun_id).subquery()                    

                query = DBSession.query(RekeningModel.kode.label('rek_kd'), RekeningModel.nama.label('rek_nm'),
                    RekeningModel.level_id, RekeningModel.defsign, subq2.c.tahun_id, 
                    func.sum(subq2.c.jml).label('jumlah'),
                    func.sum(subq2.c.realisasi).label('realisasi'),
                    ).filter(RekeningModel.kode==func.left(subq2.c.subrek_kd, func.length(RekeningModel.kode)),
                    RekeningModel.level_id<3)\
                    .group_by(RekeningModel.kode, RekeningModel.nama,
                    RekeningModel.level_id, RekeningModel.defsign, subq2.c.tahun_id)\
                    .order_by(RekeningModel.kode).all()                    

                generator = b204r300Generator()
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

#LAP Realisasi Anggaran/Kegiatan/SKPD
    @view_config(route_name="b204_r200", renderer="osipkd:templates/apbd/tuppkd/b204r200.pt")
    def b204_r200(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas,)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b204_r200_act")
    def b204_r200_act(self):
        global bln, unit_nama
        unit_nama = self.unit_nm
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            bln = 'bulan' in params and params['bulan'] and int(params['bulan']) or 0
            if url_dict['act']=='1' and self.is_akses_mod('read'):
                subq1 = (DBSession.query(RekeningModel.kode.label('subrek_kd'),RekeningModel.nama.label('subrek_nm'),
                    Unit.id.label('unit_id'),Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                    Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), 
                    KegiatanSubModel.tahun_id.label('tahun_id'),
                    ProgramModel.kode.label('program_kd'), ProgramModel.nama.label('program_nm'), 
                    KegiatanModel.kode.label('kegiatan_kd'), KegiatanModel.nama.label('kegiatan_nm'),
                    (KegiatanItemModel.vol_4_1* KegiatanItemModel.vol_4_2*KegiatanItemModel.hsat_4).label('jml'), 
                    sqlalchemy.sql.literal_column("0").label('realisasi')
                    ).filter(KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                            KegiatanItemModel.rekening_id==RekeningModel.id, KegiatanSubModel.unit_id==Unit.id, 
                            Unit.urusan_id==Urusan.id, KegiatanSubModel.kegiatan_id==KegiatanModel.id,
                            KegiatanModel.program_id==ProgramModel.id,
                            KegiatanSubModel.tahun_id==self.tahun, KegiatanSubModel.unit_id==self.unit_id
                    ).union(DBSession.query(
                    RekeningModel.kode.label('subrek_kd'),RekeningModel.nama.label('subrek_nm'),
                    Unit.id.label('unit_id'),Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                    Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), 
                    SppModel.tahun_id.label('tahun_id'), 
                    ProgramModel.kode.label('program_kd'), ProgramModel.nama.label('program_nm'), 
                    KegiatanModel.kode.label('kegiatan_kd'), KegiatanModel.nama.label('kegiatan_nm'),
                    sqlalchemy.sql.literal_column("0").label('jml'),
                    func.max(APInvoiceItemModel.nilai).label('realisasi')
                    ).filter(APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                            APInvoiceItemModel.apinvoice_id==APInvoiceModel.id,
                            KegiatanItemModel.rekening_id==RekeningModel.id,
                            SppModel.unit_id==Unit.id,
                            Unit.urusan_id==Urusan.id,
                            KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                            KegiatanSubModel.kegiatan_id==KegiatanModel.id,
                            KegiatanModel.program_id==ProgramModel.id,
                            SppItemModel.apinvoice_id==APInvoiceModel.id,
                            SppItemModel.spp_id==SppModel.id,
                            SpmModel.spp_id==SppModel.id,                            
                            Sp2dModel.spm_id==SpmModel.id, 
                            SppModel.tahun_id==self.tahun, extract('month',Sp2dModel.tanggal) <= bln,
                            SppModel.unit_id==self.unit_id
                    ).group_by(RekeningModel.kode, RekeningModel.nama, Unit.id, Unit.kode, Unit.nama,
                            Urusan.kode, Urusan.nama, SppModel.tahun_id, ProgramModel.kode, ProgramModel.nama, 
                            KegiatanModel.kode, KegiatanModel.nama
                    ))).subquery()

                subq = DBSession.query(subq1.c.subrek_kd.label('subrek_kd'), subq1.c.subrek_nm.label('subrek_nm'), 
                    subq1.c.unit_id, subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.urusan_kd, subq1.c.urusan_nm, 
                    subq1.c.tahun_id, subq1.c.program_kd, subq1.c.program_nm, subq1.c.kegiatan_kd, subq1.c.kegiatan_nm,
                    func.sum(subq1.c.jml).label('jml'), func.sum(subq1.c.realisasi).label('realisasi')
                    ).group_by(subq1.c.subrek_kd.label('subrek_kd'), subq1.c.subrek_nm.label('subrek_nm'), 
                    subq1.c.unit_id, subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.urusan_kd, subq1.c.urusan_nm, 
                    subq1.c.tahun_id, subq1.c.program_kd, subq1.c.program_nm, subq1.c.kegiatan_kd, subq1.c.kegiatan_nm
                    ).subquery()                    

                query = DBSession.query(RekeningModel.kode.label('rek_kd'), RekeningModel.nama.label('rek_nm'),
                    RekeningModel.level_id, RekeningModel.defsign, RekeningModel.id.label('rekening_id'),
                    subq.c.unit_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.urusan_kd, subq.c.urusan_nm, 
                    subq.c.tahun_id, subq.c.program_kd, subq.c.program_nm, subq.c.kegiatan_kd, subq.c.kegiatan_nm, 
                    case([(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='10'),1),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='21'),2),
                    (and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='31'),4),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='32'),5)], 
                    else_=3).label('jenis'),                    
                    func.sum(subq.c.jml).label('jumlah'),func.sum(subq.c.realisasi).label('realisasi')
                    ).filter(RekeningModel.kode==func.left(subq.c.subrek_kd, func.length(RekeningModel.kode))
                    ).group_by(RekeningModel.kode, RekeningModel.nama,
                    RekeningModel.level_id, RekeningModel.defsign, RekeningModel.id, 
                    subq.c.unit_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.urusan_kd, subq.c.urusan_nm, subq.c.tahun_id,
                    subq.c.program_kd, subq.c.program_nm, subq.c.kegiatan_kd, subq.c.kegiatan_nm,
                    case([(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='10'),1),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='21'),2),
                    (and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='31'),4),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='32'),5)], 
                    else_=3))\
                    .order_by(case([(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='10'),1),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='21'),2),
                    (and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='31'),4),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='32'),5)], 
                    else_=3),subq.c.urusan_kd, subq.c.unit_kd, subq.c.program_kd, subq.c.kegiatan_kd, RekeningModel.kode).all() 
            
                generator = b204r200Generator()
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

