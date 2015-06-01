import os
import uuid
from osipkd.tools import row2dict, xls_reader
from datetime import datetime
from sqlalchemy import not_, func, or_
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from osipkd.models import DBSession
from osipkd.models.apbd import Jurnal, JurnalItem
from osipkd.models.pemda_model import *

from pyjasper import (JasperGenerator)
from pyjasper import (JasperGeneratorWithSubreport)
import xml.etree.ElementTree as ET
from pyramid.path import AssetResolver

    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah ak-report gagal'
SESS_EDIT_FAILED = 'Edit ak-report gagal'

def get_rpath(filename):
    a = AssetResolver('osipkd')
    resolver = a.resolve(''.join(['reports/',filename]))
    return resolver.abspath()
            
class view_ak_jurnal_item(BaseViews):
    def __init__(self, context, request):
        global customer

        BaseViews.__init__(self, context, request)
        self.cust_nm = 'cust_nm' in self.session and self.session['cust_nm'] or ''
        customer = self.cust_nm

    ########                    
    # List #
    ########    
    @view_config(route_name='ak-report', renderer='templates/ak-report/list.pt',
                 permission='read')
    def view_list(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        return dict(project='Akrual')
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name="ak-report-act")
    def ak_report_act(self):
        global mulai, selesai, tingkat
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        mulai   = 'mulai' in params and params['mulai'] or 0
        selesai = 'selesai' in params and params['selesai'] or 0
        kel   = 'kel' in params and params['kel'] or 0
        rekid = 'rekid' in params and params['rekid'] or 0
        sapid   = 'sapid' in params and params['sapid'] or 0
          
        if url_dict['act']=='bb' :
            if kel == '1' :
                query = DBSession.query(Jurnal.kode.label('jurnal_kd'), Jurnal.nama.label('jurnal_nm'), Jurnal.tanggal, Jurnal.tgl_transaksi, 
                   Jurnal.tahun_id, Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), Jurnal.periode, Jurnal.jv_type, Jurnal.source, Jurnal.source_no,
                   JurnalItem.amount, Sap.kode.label('rek_kd'), Sap.nama.label('rek_nm'), 
                   ).filter(Jurnal.id==JurnalItem.jurnal_id, Jurnal.unit_id==Unit.id, 
                   Jurnal.tahun_id==self.session['tahun'], Jurnal.tanggal.between(mulai,selesai),
                   JurnalItem.sap_id==Sap.id
                   ).order_by(Jurnal.tanggal).all()
                generator = r011Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif kel == '2' :
                """subq = DBSession.query(JurnalItem.rekening_id).filter(JurnalItem.sap_id==sapid, 
                   Jurnal.id==JurnalItem.jurnal_id, Jurnal.unit_id==self.session['unit_id'], 
                   Jurnal.tahun_id==self.session['tahun']
                   ).group_by(JurnalItem.rekening_id).subquery()
                """
                query = DBSession.query(Jurnal.kode.label('jurnal_kd'), Jurnal.nama.label('jurnal_nm'), Jurnal.tanggal, Jurnal.tgl_transaksi, 
                   Jurnal.tahun_id, Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), Jurnal.periode, Jurnal.jv_type, Jurnal.source, Jurnal.source_no,
                   JurnalItem.amount, Sap.kode.label('rek_kd'), Sap.nama.label('rek_nm'), 
                   ).filter(Jurnal.id==JurnalItem.jurnal_id, Jurnal.unit_id==Unit.id, 
                   Jurnal.unit_id==self.session['unit_id'], 
                   Jurnal.tahun_id==self.session['tahun'], Jurnal.tanggal.between(mulai,selesai),
                   JurnalItem.sap_id==Sap.id
                   ).order_by(Jurnal.tanggal).all()
                generator = r012Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response

        elif url_dict['act']=='lrasap' :
          if kel=='1' :
              subq = DBSession.query(Sap.kode.label('subrek_kd'), Sap.nama.label('rek_nm'), 
                 JurnalItem.amount, Jurnal.tahun_id
                 ).filter(JurnalItem.sap_id==Sap.id, JurnalItem.jurnal_id==Jurnal.id, 
                 JurnalItem.amount>0,
                 Jurnal.tahun_id==self.session['tahun']
                 ).subquery()
                 
              query = DBSession.query(Sap.kode, Sap.nama, subq.c.tahun_id.label('tahun_id'),
                 func.sum(subq.c.amount).label('amount')
                 ).filter(Sap.kode==func.left(subq.c.subrek_kd, func.length(Sap.kode)),
                 func.substr(Sap.kode,1,1).in_(['4','5','6']) 
                 ).group_by(Sap.kode, Sap.nama, subq.c.tahun_id,
                 ).order_by(Sap.kode)
              generator = r021Generator()
              pdf = generator.generate(query)
              response=req.response
              response.content_type="application/pdf"
              response.content_disposition='filename=output.pdf' 
              response.write(pdf)
              return response
          elif kel=='2' :
              subq = DBSession.query(Sap.kode.label('subrek_kd'), Sap.nama.label('rek_nm'), Unit.kode.label('unit_kd'),
                 Unit.nama.label('unit_nm'), JurnalItem.amount, Jurnal.tahun_id
                 ).filter(JurnalItem.sap_id==Sap.id, JurnalItem.jurnal_id==Jurnal.id, Jurnal.unit_id==Unit.id, 
                 JurnalItem.amount>0,
                 Jurnal.tahun_id==self.session['tahun'],Jurnal.unit_id==self.session['unit_id']
                 ).subquery()
                 
              query = DBSession.query(Sap.kode, Sap.nama, subq.c.tahun_id.label('tahun_id'),
                 subq.c.unit_kd.label('unit_kd'), subq.c.unit_nm.label('unit_nm'), func.sum(subq.c.amount).label('amount')
                 ).filter(Sap.kode==func.left(subq.c.subrek_kd, func.length(Sap.kode)), 
                 func.substr(Sap.kode,1,1).in_(['4','5','6']) 
                 ).group_by(Sap.kode, Sap.nama, subq.c.tahun_id,
                 subq.c.unit_kd, subq.c.unit_nm
                 ).order_by(Sap.kode)
              generator = r022Generator()
              pdf = generator.generate(query)
              response=req.response
              response.content_type="application/pdf"
              response.content_disposition='filename=output.pdf' 
              response.write(pdf)
              return response
              
        elif url_dict['act']=='lo' :
          if kel=='1' :
              subq = DBSession.query(Sap.kode.label('subrek_kd'), Sap.nama.label('rek_nm'), 
                 JurnalItem.amount, Jurnal.tahun_id
                 ).filter(JurnalItem.sap_id==Sap.id, JurnalItem.jurnal_id==Jurnal.id, 
                 JurnalItem.amount>0,
                 Jurnal.tahun_id==self.session['tahun']
                 ).subquery()
                 
              query = DBSession.query(Sap.kode, Sap.nama, subq.c.tahun_id.label('tahun_id'),
                 func.sum(subq.c.amount).label('amount')
                 ).filter(Sap.kode==func.left(subq.c.subrek_kd, func.length(Sap.kode)), 
                 func.substr(Sap.kode,1,1).in_(['8','9']) 
                 ).group_by(Sap.kode, Sap.nama, subq.c.tahun_id,
                 ).order_by(Sap.kode)
              generator = r051Generator()
              pdf = generator.generate(query)
              response=req.response
              response.content_type="application/pdf"
              response.content_disposition='filename=output.pdf' 
              response.write(pdf)
              return response
          elif kel=='2' :
              subq = DBSession.query(Sap.kode.label('subrek_kd'), Sap.nama.label('rek_nm'), Unit.kode.label('unit_kd'),
                 Unit.nama.label('unit_nm'), JurnalItem.amount, Jurnal.tahun_id
                 ).filter(JurnalItem.sap_id==Sap.id, JurnalItem.jurnal_id==Jurnal.id, Jurnal.unit_id==Unit.id, 
                 JurnalItem.amount>0,
                 Jurnal.tahun_id==self.session['tahun'],Jurnal.unit_id==self.session['unit_id']
                 ).subquery()
                 
              query = DBSession.query(Sap.kode, Sap.nama, subq.c.tahun_id.label('tahun_id'),
                 subq.c.unit_kd.label('unit_kd'), subq.c.unit_nm.label('unit_nm'), func.sum(subq.c.amount).label('amount')
                 ).filter(Sap.kode==func.left(subq.c.subrek_kd, func.length(Sap.kode)), 
                 func.substr(Sap.kode,1,1).in_(['8','9']) 
                 ).group_by(Sap.kode, Sap.nama, subq.c.tahun_id,
                 subq.c.unit_kd, subq.c.unit_nm
                 ).order_by(Sap.kode)
              generator = r052Generator()
              pdf = generator.generate(query)
              response=req.response
              response.content_type="application/pdf"
              response.content_disposition='filename=output.pdf' 
              response.write(pdf)
              return response

class r011Generator(JasperGenerator):
    def __init__(self):
        super(r011Generator, self).__init__()
        self.reportname = get_rpath('apbd/akskpd/BB001001.jrxml')
        self.xpath = '/apbd/akuntansi'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'akuntansi')
            ET.SubElement(xml_greeting, "jurnal_kd").text = row.jurnal_kd
            ET.SubElement(xml_greeting, "jurnal_nm").text = row.jurnal_nm
            ET.SubElement(xml_greeting, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_greeting, "tgl_transaksi").text = unicode(row.tgl_transaksi)
            ET.SubElement(xml_greeting, "tahun_id").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "periode").text = unicode(row.periode)
            ET.SubElement(xml_greeting, "jv_type").text = unicode(row.jv_type)
            ET.SubElement(xml_greeting, "source").text = row.source
            ET.SubElement(xml_greeting, "source_no").text = row.source_no
            ET.SubElement(xml_greeting, "amount").text = unicode(row.amount)
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "mulai").text = mulai
            ET.SubElement(xml_greeting, "selesai").text = selesai
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r012Generator(JasperGenerator):
    def __init__(self):
        super(r012Generator, self).__init__()
        self.reportname = get_rpath('apbd/akskpd/BB001002.jrxml')
        self.xpath = '/apbd/akuntansi'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'akuntansi')
            ET.SubElement(xml_greeting, "jurnal_kd").text = row.jurnal_kd
            ET.SubElement(xml_greeting, "jurnal_nm").text = row.jurnal_nm
            ET.SubElement(xml_greeting, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_greeting, "tgl_transaksi").text = unicode(row.tgl_transaksi)
            ET.SubElement(xml_greeting, "tahun_id").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "periode").text = unicode(row.periode)
            ET.SubElement(xml_greeting, "jv_type").text = unicode(row.jv_type)
            ET.SubElement(xml_greeting, "source").text = row.source
            ET.SubElement(xml_greeting, "source_no").text = row.source_no
            ET.SubElement(xml_greeting, "amount").text = unicode(row.amount)
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "mulai").text = mulai
            ET.SubElement(xml_greeting, "selesai").text = selesai
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r021Generator(JasperGenerator):
    def __init__(self):
        super(r021Generator, self).__init__()
        self.reportname = get_rpath('apbd/akskpd/BB002001.jrxml')
        self.xpath = '/apbd/akuntansi'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'akuntansi')
            ET.SubElement(xml_greeting, "kode").text = row.kode
            ET.SubElement(xml_greeting, "nama").text = row.nama
            ET.SubElement(xml_greeting, "tahun_id").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "amount").text = unicode(row.amount)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r022Generator(JasperGenerator):
    def __init__(self):
        super(r022Generator, self).__init__()
        self.reportname = get_rpath('apbd/akskpd/BB002002.jrxml')
        self.xpath = '/apbd/akuntansi'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'akuntansi')
            ET.SubElement(xml_greeting, "kode").text = row.kode
            ET.SubElement(xml_greeting, "nama").text = row.nama
            ET.SubElement(xml_greeting, "tahun_id").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "amount").text = unicode(row.amount)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r051Generator(JasperGenerator):
    def __init__(self):
        super(r051Generator, self).__init__()
        self.reportname = get_rpath('apbd/akskpd/BB005001.jrxml')
        self.xpath = '/apbd/akuntansi'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'akuntansi')
            ET.SubElement(xml_greeting, "kode").text = row.kode
            ET.SubElement(xml_greeting, "nama").text = row.nama
            ET.SubElement(xml_greeting, "tahun_id").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "amount").text = unicode(row.amount)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r052Generator(JasperGenerator):
    def __init__(self):
        super(r052Generator, self).__init__()
        self.reportname = get_rpath('apbd/akskpd/BB005002.jrxml')
        self.xpath = '/apbd/akuntansi'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'akuntansi')
            ET.SubElement(xml_greeting, "kode").text = row.kode
            ET.SubElement(xml_greeting, "nama").text = row.nama
            ET.SubElement(xml_greeting, "tahun_id").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "amount").text = unicode(row.amount)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

