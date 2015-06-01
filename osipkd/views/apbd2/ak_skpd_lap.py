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
from osipkd.models.apbd_ak_models import (JurnalModel, JurnalItemModel)
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
    
#Jurnal Penerimaan-Generator
class c102r001Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(c102r001Generator, self).__init__()
        self.reportname = get_rpath('apbd/akskpd/C102001.jrxml')
        self.xpath = '/apbd/jurnal'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'jurnal')
            ET.SubElement(xml_greeting, "tanggal").text = unicode(row.jurnals.tanggal)
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.jurnals.tahun_id)
            ET.SubElement(xml_greeting, "periode").text = unicode(row.jurnals.periode)
            ET.SubElement(xml_greeting, "unit_id").text = unicode(row.jurnals.unit_id)
            ET.SubElement(xml_greeting, "unit_nm").text = row.jurnals.units.nama
            ET.SubElement(xml_greeting, "uraian").text = row.jurnals.nama
            ET.SubElement(xml_greeting, "source").text = row.jurnals.source
            ET.SubElement(xml_greeting, "source_no").text = row.jurnals.source_no
            ET.SubElement(xml_greeting, "jv_type").text = unicode(row.jurnals.jv_type)
            ET.SubElement(xml_greeting, "is_skpd").text = unicode(row.jurnals.is_skpd)
            ET.SubElement(xml_greeting, "debet").text = unicode(row.debet)
            ET.SubElement(xml_greeting, "kredit").text = unicode(row.kredit)
            ET.SubElement(xml_greeting, "jumlah").text = unicode(row.amounttrans)
            
        return self.root

#Jurnal Pengeluaran-Generator
class c102r002Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(c102r002Generator, self).__init__()
        self.reportname = get_rpath('apbd/akskpd/C102002.jrxml')
        self.xpath = '/apbd/jurnal'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'jurnal')
            ET.SubElement(xml_greeting, "tanggal").text = unicode(row.jurnals.tanggal)
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.jurnals.tahun_id)
            ET.SubElement(xml_greeting, "periode").text = unicode(row.jurnals.periode)
            ET.SubElement(xml_greeting, "unit_id").text = unicode(row.jurnals.unit_id)
            ET.SubElement(xml_greeting, "unit_nm").text = row.jurnals.units.nama
            ET.SubElement(xml_greeting, "uraian").text = row.jurnals.nama
            ET.SubElement(xml_greeting, "source").text = row.jurnals.source
            ET.SubElement(xml_greeting, "source_no").text = row.jurnals.source_no
            ET.SubElement(xml_greeting, "jv_type").text = unicode(row.jurnals.jv_type)
            ET.SubElement(xml_greeting, "is_skpd").text = unicode(row.jurnals.is_skpd)
            ET.SubElement(xml_greeting, "debet").text = unicode(row.debet)
            ET.SubElement(xml_greeting, "kredit").text = unicode(row.kredit)
            ET.SubElement(xml_greeting, "jumlah").text = unicode(row.amounttrans)
            
        return self.root

#Jurnal Umum-Generator
class c102r003Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(c102r003Generator, self).__init__()
        self.reportname = get_rpath('apbd/akskpd/C102003.jrxml')
        self.xpath = '/apbd/jurnal'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'jurnal')
            ET.SubElement(xml_greeting, "tanggal").text = unicode(row.jurnals.tanggal)
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.jurnals.tahun_id)
            ET.SubElement(xml_greeting, "periode").text = unicode(row.jurnals.periode)
            ET.SubElement(xml_greeting, "unit_id").text = unicode(row.jurnals.unit_id)
            ET.SubElement(xml_greeting, "unit_nm").text = row.jurnals.units.nama
            ET.SubElement(xml_greeting, "uraian").text = row.jurnals.nama
            ET.SubElement(xml_greeting, "source").text = row.jurnals.source
            ET.SubElement(xml_greeting, "source_no").text = row.jurnals.source_no
            ET.SubElement(xml_greeting, "jv_type").text = unicode(row.jurnals.jv_type)
            ET.SubElement(xml_greeting, "is_skpd").text = unicode(row.jurnals.is_skpd)
            ET.SubElement(xml_greeting, "debet").text = unicode(row.debet)
            ET.SubElement(xml_greeting, "kredit").text = unicode(row.kredit)
            ET.SubElement(xml_greeting, "jumlah").text = unicode(row.amounttrans)
            
        return self.root

#Jurnal Koreksi-Generator
class c102r004Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(c102r004Generator, self).__init__()
        self.reportname = get_rpath('apbd/akskpd/C102004.jrxml')
        self.xpath = '/apbd/jurnal'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'jurnal')
            ET.SubElement(xml_greeting, "tanggal").text = unicode(row.jurnals.tanggal)
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.jurnals.tahun_id)
            ET.SubElement(xml_greeting, "periode").text = unicode(row.jurnals.periode)
            ET.SubElement(xml_greeting, "unit_id").text = unicode(row.jurnals.unit_id)
            ET.SubElement(xml_greeting, "unit_nm").text = row.jurnals.units.nama
            ET.SubElement(xml_greeting, "uraian").text = row.jurnals.nama
            ET.SubElement(xml_greeting, "source").text = row.jurnals.source
            ET.SubElement(xml_greeting, "source_no").text = row.jurnals.source_no
            ET.SubElement(xml_greeting, "jv_type").text = unicode(row.jurnals.jv_type)
            ET.SubElement(xml_greeting, "is_skpd").text = unicode(row.jurnals.is_skpd)
            ET.SubElement(xml_greeting, "debet").text = unicode(row.debet)
            ET.SubElement(xml_greeting, "kredit").text = unicode(row.kredit)
            ET.SubElement(xml_greeting, "jumlah").text = unicode(row.amounttrans)
            
        return self.root

#Jurnal Penutup-Generator
class c102r005Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(c102r005Generator, self).__init__()
        self.reportname = get_rpath('apbd/akskpd/C102005.jrxml')
        self.xpath = '/apbd/jurnal'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'jurnal')
            ET.SubElement(xml_greeting, "tanggal").text = unicode(row.jurnals.tanggal)
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.jurnals.tahun_id)
            ET.SubElement(xml_greeting, "periode").text = unicode(row.jurnals.periode)
            ET.SubElement(xml_greeting, "unit_id").text = unicode(row.jurnals.unit_id)
            ET.SubElement(xml_greeting, "unit_nm").text = row.jurnals.units.nama
            ET.SubElement(xml_greeting, "uraian").text = row.jurnals.nama
            ET.SubElement(xml_greeting, "source").text = row.jurnals.source
            ET.SubElement(xml_greeting, "source_no").text = row.jurnals.source_no
            ET.SubElement(xml_greeting, "jv_type").text = unicode(row.jurnals.jv_type)
            ET.SubElement(xml_greeting, "is_skpd").text = unicode(row.jurnals.is_skpd)
            ET.SubElement(xml_greeting, "debet").text = unicode(row.debet)
            ET.SubElement(xml_greeting, "kredit").text = unicode(row.kredit)
            ET.SubElement(xml_greeting, "jumlah").text = unicode(row.amounttrans)
            
        return self.root

class ViewAkSKPDLap(BaseViews):
    def __init__(self, context, request):
        BaseViews.__init__(self, context, request)
        self.app = 'akskpd'

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
        
#Jurnal Penerimaan
    @view_config(route_name="c102_r001_act")
    def c102_r001_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if self.is_akses_mod('read'):
                query = DBSession.query(JurnalItemModel
                      ).filter(JurnalModel.id==JurnalItemModel.jurnal_id,
                      JurnalModel.unit_id==Unit.id,
                      JurnalModel.unit_id==self.unit_id,
                      JurnalModel.tahun_id==self.tahun
                      ).order_by(JurnalModel.tanggal
                      )
                generator = c102r001Generator()
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

#Jurnal Pengeluaran
    @view_config(route_name="c102_r002_act")
    def c102_r002_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if self.is_akses_mod('read'):
                query = DBSession.query(JurnalItemModel
                      ).filter(JurnalModel.id==JurnalItemModel.jurnal_id,
                      JurnalModel.unit_id==Unit.id,
                      JurnalModel.unit_id==self.unit_id,
                      JurnalModel.tahun_id==self.tahun
                      ).order_by(JurnalModel.tanggal
                      )
                generator = c102r002Generator()
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

#Jurnal Umum
    @view_config(route_name="c102_r003_act")
    def c102_r003_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if self.is_akses_mod('read'):
                query = DBSession.query(JurnalItemModel
                      ).filter(JurnalModel.id==JurnalItemModel.jurnal_id,
                      JurnalModel.unit_id==Unit.id,
                      JurnalModel.unit_id==self.unit_id,
                      JurnalModel.tahun_id==self.tahun
                      ).order_by(JurnalModel.tanggal
                      )
                generator = c102r003Generator()
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

#Jurnal Koreksi
    @view_config(route_name="c102_r004_act")
    def c102_r004_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if self.is_akses_mod('read'):
                query = DBSession.query(JurnalItemModel
                      ).filter(JurnalModel.id==JurnalItemModel.jurnal_id,
                      JurnalModel.unit_id==Unit.id,
                      JurnalModel.unit_id==self.unit_id,
                      JurnalModel.tahun_id==self.tahun
                      ).order_by(JurnalModel.tanggal
                      )
                generator = c102r004Generator()
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

#Jurnal Penutup
    @view_config(route_name="c102_r005_act")
    def c102_r005_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if self.is_akses_mod('read'):
                query = DBSession.query(JurnalItemModel
                      ).filter(JurnalModel.id==JurnalItemModel.jurnal_id,
                      JurnalModel.unit_id==Unit.id,
                      JurnalModel.unit_id==self.unit_id,
                      JurnalModel.tahun_id==self.tahun
                      ).order_by(JurnalModel.tanggal
                      )
                generator = c102r005Generator()
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

