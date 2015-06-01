import os
import uuid
from osipkd.tools import row2dict, xls_reader
from datetime import datetime
#from sqlalchemy import not_, func, literal_column
from sqlalchemy import *
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from osipkd.models import DBSession
from osipkd.models.apbd import ARPaymentItem, ARInvoiceItem
from osipkd.models.pemda_model import *

from pyjasper import (JasperGenerator)
from pyjasper import (JasperGeneratorWithSubreport)
import xml.etree.ElementTree as ET
from pyramid.path import AssetResolver
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews
    

SESS_ADD_FAILED = 'Tambah ar-payment-item gagal'
SESS_EDIT_FAILED = 'Edit ar-payment-item gagal'

SUMBER_ID = (
    (1, 'Manual'),
    (2, 'PBB'),
    (3, 'BPHTB'),
    (4, 'PADL'),
    )
    
def get_rpath(filename):
    a = AssetResolver('osipkd')
    resolver = a.resolve(''.join(['reports/',filename]))
    return resolver.abspath()

class view_ar_payment_item(BaseViews):
    def __init__(self, context, request):
        global customer

        BaseViews.__init__(self, context, request)
        self.cust_nm = 'cust_nm' in self.session and self.session['cust_nm'] or ''
        customer = self.cust_nm

    ########                    
    # List #
    ########    
    @view_config(route_name='ar-report-item', renderer='templates/ar-report-item/list.pt',
                 permission='read')
    def view_list(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        #mulai = 'mulai' in params and params['mulai'] or 0
        #selesai = 'selesai' in params and params['selesai'] or 0
        return dict(project='Akrual')
 
    @view_config(route_name="ar-report-item-act")
    def ar_report_item_act(self):
        global mulai, selesai, tingkat
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        mulai   = 'mulai' in params and params['mulai'] or 0
        selesai = 'selesai' in params and params['selesai'] or 0
        level   = 'level' in params and params['level'] or 0
        if level=='1' :
          tingkat = 4
        elif level=='2' :
          tingkat = 5
        elif level=='3' :
          tingkat = 6
          
        if url_dict['act']=='1' :
            query1 = DBSession.query(ARInvoiceItem.tahun.label('tahun'), Rekening.kode.label('subrek_kd'), literal_column('0').label('lalu'),
                func.sum(ARInvoiceItem.amount).label('kini')
                ).join(Rekening
                ).filter(ARInvoiceItem.tahun==self.session['tahun'], ARInvoiceItem.tanggal.between(mulai,selesai        
                )).group_by(ARInvoiceItem.tahun, Rekening.kode)

            query2 = DBSession.query(ARInvoiceItem.tahun.label('tahun'), Rekening.kode.label('subrek_kd'), func.sum(ARInvoiceItem.amount).label('lalu'),
                literal_column('0').label('kini')
                ).join(Rekening
                ).filter(ARInvoiceItem.tahun==self.session['tahun'], ARInvoiceItem.tanggal < mulai        
                ).group_by(ARInvoiceItem.tahun, Rekening.kode)

            subq1 = query1.union(query2).subquery()
            
            subq = DBSession.query(subq1.c.tahun.label('tahun'), subq1.c.subrek_kd.label('subrek_kd'), func.sum(subq1.c.lalu).label('lalu'),
                func.sum(subq1.c.kini).label('kini'
                )).group_by(subq1.c.tahun, subq1.c.subrek_kd).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq.c.tahun, 
                func.sum(subq.c.lalu).label('lalu'),func.sum(subq.c.kini).label('kini'))\
                .filter(Rekening.kode==func.left(subq.c.subrek_kd, func.length(Rekening.kode))
                ,Rekening.level_id<tingkat).group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq.c.tahun)\
                .order_by(Rekening.kode).all()                    

            generator = r001Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
            
        elif url_dict['act']=='2' :
            query1 = DBSession.query(ARPaymentItem.tahun.label('tahun'), Rekening.kode.label('subrek_kd'), literal_column('0').label('lalu'),
                func.sum(ARPaymentItem.amount).label('kini')
                ).join(Rekening
                ).filter(ARPaymentItem.tahun==self.session['tahun'], ARPaymentItem.tanggal.between(mulai,selesai        
                )).group_by(ARPaymentItem.tahun, Rekening.kode)

            query2 = DBSession.query(ARPaymentItem.tahun.label('tahun'), Rekening.kode.label('subrek_kd'), func.sum(ARPaymentItem.amount).label('lalu'),
                literal_column('0').label('kini')
                ).join(Rekening
                ).filter(ARPaymentItem.tahun==self.session['tahun'], ARPaymentItem.tanggal < mulai        
                ).group_by(ARPaymentItem.tahun, Rekening.kode)

            subq1 = query1.union(query2).subquery()
            
            subq = DBSession.query(subq1.c.tahun.label('tahun'), subq1.c.subrek_kd.label('subrek_kd'), func.sum(subq1.c.lalu).label('lalu'),
                func.sum(subq1.c.kini).label('kini'
                )).group_by(subq1.c.tahun, subq1.c.subrek_kd).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq.c.tahun, literal_column('0').label('anggaran'),
                func.sum(subq.c.lalu).label('lalu'),func.sum(subq.c.kini).label('kini'))\
                .filter(Rekening.kode==func.left(subq.c.subrek_kd, func.length(Rekening.kode))
                ,Rekening.level_id<tingkat).group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq.c.tahun)\
                .order_by(Rekening.kode).all()                    

            generator = r002Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
            
        if url_dict['act']=='3' :
            query1 = DBSession.query(ARInvoiceItem.tahun.label('tahun'), Rekening.kode.label('subrek_kd'), 
                literal_column('0').label('inv_lalu'), func.sum(ARInvoiceItem.amount).label('inv_kini'), 
                literal_column('0').label('payment_lalu'), literal_column('0').label('payment_kini')
                ).join(Rekening
                ).filter(ARInvoiceItem.tahun==self.session['tahun'], ARInvoiceItem.tanggal.between(mulai,selesai        
                )).group_by(ARInvoiceItem.tahun, Rekening.kode)

            query2 = DBSession.query(ARInvoiceItem.tahun.label('tahun'), Rekening.kode.label('subrek_kd'), 
                func.sum(ARInvoiceItem.amount).label('inv_lalu'), literal_column('0').label('inv_kini'), 
                literal_column('0').label('payment_lalu'), literal_column('0').label('payment_kini')
                ).join(Rekening
                ).filter(ARInvoiceItem.tahun==self.session['tahun'], ARInvoiceItem.tanggal < mulai        
                ).group_by(ARInvoiceItem.tahun, Rekening.kode)

            query3 = DBSession.query(ARPaymentItem.tahun.label('tahun'), Rekening.kode.label('subrek_kd'), 
                literal_column('0').label('inv_lalu'), literal_column('0').label('inv_kini'), 
                literal_column('0').label('payment_lalu'), func.sum(ARPaymentItem.amount).label('payment_kini')
                ).join(Rekening
                ).filter(ARPaymentItem.tahun==self.session['tahun'], ARPaymentItem.tanggal.between(mulai,selesai        
                )).group_by(ARPaymentItem.tahun, Rekening.kode)

            query4 = DBSession.query(ARPaymentItem.tahun.label('tahun'), Rekening.kode.label('subrek_kd'), 
                literal_column('0').label('inv_lalu'), literal_column('0').label('inv_kini'), 
                func.sum(ARPaymentItem.amount).label('payment_lalu'), literal_column('0').label('payment_kini')
                ).join(Rekening
                ).filter(ARPaymentItem.tahun==self.session['tahun'], ARPaymentItem.tanggal < mulai        
                ).group_by(ARPaymentItem.tahun, Rekening.kode)

            subq1 = query1.union(query2,query3,query4).subquery()
            
            subq = DBSession.query(subq1.c.tahun.label('tahun'), subq1.c.subrek_kd.label('subrek_kd'), 
                func.sum(subq1.c.inv_lalu).label('inv_lalu'), func.sum(subq1.c.inv_kini).label('inv_kini'),
                func.sum(subq1.c.payment_lalu).label('payment_lalu'), func.sum(subq1.c.payment_kini).label('payment_kini'
                )).group_by(subq1.c.tahun, subq1.c.subrek_kd).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq.c.tahun, 
                func.sum(subq.c.inv_lalu).label('inv_lalu'),func.sum(subq.c.inv_kini).label('inv_kini'),
                func.sum(subq.c.payment_lalu).label('payment_lalu'),func.sum(subq.c.payment_kini).label('payment_kini')
                ).filter(Rekening.kode==func.left(subq.c.subrek_kd, func.length(Rekening.kode))
                ,Rekening.level_id<tingkat).group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq.c.tahun)\
                .order_by(Rekening.kode).all()                    

            generator = r003Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            
            return response
            
    @view_config(route_name='ar-report-item-skpd', renderer='templates/ar-report-item/listskpd.pt',
                 permission='read')
    def view_list(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        return dict(project='Akrual')

    @view_config(route_name="ar-report-item-skpd-act")
    def ar_report_item_skpd_act(self):
        global mulai, selesai, tingkat
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        mulai   = 'mulai' in params and params['mulai'] or 0
        selesai = 'selesai' in params and params['selesai'] or 0
        level   = 'level' in params and params['level'] or 0
        if level=='1' :
          tingkat = 4
        elif level=='2' :
          tingkat = 5
        elif level=='3' :
          tingkat = 6
          
        if url_dict['act']=='1' :
            query1 = DBSession.query(ARInvoiceItem.tahun.label('tahun'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Rekening.kode.label('subrek_kd'), literal_column('0').label('lalu'),
                func.sum(ARInvoiceItem.amount).label('kini')
                ).join(Rekening, Unit
                ).filter(ARInvoiceItem.tahun==self.session['tahun'], ARInvoiceItem.unit_id==self.session['unit_id'], 
                ARInvoiceItem.tanggal.between(mulai,selesai        
                )).group_by(ARInvoiceItem.tahun, Unit.kode, Unit.nama, Rekening.kode)

            query2 = DBSession.query(ARInvoiceItem.tahun.label('tahun'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Rekening.kode.label('subrek_kd'), func.sum(ARInvoiceItem.amount).label('lalu'),
                literal_column('0').label('kini')
                ).join(Rekening, Unit
                ).filter(ARInvoiceItem.tahun==self.session['tahun'], ARInvoiceItem.unit_id==self.session['unit_id'], ARInvoiceItem.tanggal < mulai        
                ).group_by(ARInvoiceItem.tahun, Unit.kode, Unit.nama, Rekening.kode)

            subq1 = query1.union(query2).subquery()
            
            subq = DBSession.query(subq1.c.tahun.label('tahun'), subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.subrek_kd.label('subrek_kd'), func.sum(subq1.c.lalu).label('lalu'),
                func.sum(subq1.c.kini).label('kini'
                )).group_by(subq1.c.tahun, subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.subrek_kd).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq.c.tahun, subq1.c.unit_kd, subq1.c.unit_nm, 
                func.sum(subq.c.lalu).label('lalu'),func.sum(subq.c.kini).label('kini'))\
                .filter(Rekening.kode==func.left(subq.c.subrek_kd, func.length(Rekening.kode))
                ,Rekening.level_id<tingkat).group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq.c.tahun, subq1.c.unit_kd, subq1.c.unit_nm)\
                .order_by(Rekening.kode).all()                    

            generator = r101Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
            
        elif url_dict['act']=='2' :
            query1 = DBSession.query(ARPaymentItem.tahun.label('tahun'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), 
                Rekening.kode.label('subrek_kd'), literal_column('0').label('lalu'),
                func.sum(ARPaymentItem.amount).label('kini'), 
                ).join(Rekening, Unit
                ).filter(ARPaymentItem.tahun==self.session['tahun'], ARPaymentItem.unit_id==self.session['unit_id'], 
                ARPaymentItem.unit_id==self.session['unit_id'], ARPaymentItem.tanggal.between(mulai,selesai        
                )).group_by(ARPaymentItem.tahun, Unit.kode, Unit.nama, Rekening.kode)

            query2 = DBSession.query(ARPaymentItem.tahun.label('tahun'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Rekening.kode.label('subrek_kd'), func.sum(ARPaymentItem.amount).label('lalu'),
                literal_column('0').label('kini')
                ).join(Rekening, Unit
                ).filter(ARPaymentItem.tahun==self.session['tahun'], ARPaymentItem.unit_id==self.session['unit_id'], 
                ARPaymentItem.unit_id==self.session['unit_id'], ARPaymentItem.tanggal < mulai        
                ).group_by(ARPaymentItem.tahun, Unit.kode, Unit.nama, Rekening.kode)

            subq1 = query1.union(query2).subquery()
            
            subq = DBSession.query(subq1.c.tahun.label('tahun'), subq1.c.unit_kd, subq1.c.unit_nm, 
                subq1.c.subrek_kd.label('subrek_kd'), func.sum(subq1.c.lalu).label('lalu'),
                func.sum(subq1.c.kini).label('kini'
                )).group_by(subq1.c.tahun, subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.subrek_kd).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq.c.tahun, subq1.c.unit_kd, subq1.c.unit_nm, 
                literal_column('0').label('anggaran'),
                func.sum(subq.c.lalu).label('lalu'),func.sum(subq.c.kini).label('kini'))\
                .filter(Rekening.kode==func.left(subq.c.subrek_kd, func.length(Rekening.kode))
                ,Rekening.level_id<tingkat).group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq.c.tahun, subq1.c.unit_kd, subq1.c.unit_nm)\
                .order_by(Rekening.kode).all()                    

            generator = r102Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
            
        if url_dict['act']=='3' :
            query1 = DBSession.query(ARInvoiceItem.tahun.label('tahun'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), 
                Rekening.kode.label('subrek_kd'), 
                literal_column('0').label('inv_lalu'), func.sum(ARInvoiceItem.amount).label('inv_kini'),  
                literal_column('0').label('payment_lalu'), literal_column('0').label('payment_kini')
                ).join(Rekening, Unit
                ).filter(ARInvoiceItem.tahun==self.session['tahun'], ARInvoiceItem.unit_id==self.session['unit_id'], 
                ARInvoiceItem.tanggal.between(mulai,selesai        
                )).group_by(ARInvoiceItem.tahun, Unit.kode, Unit.nama, Rekening.kode)

            query2 = DBSession.query(ARInvoiceItem.tahun.label('tahun'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), 
                Rekening.kode.label('subrek_kd'), 
                func.sum(ARInvoiceItem.amount).label('inv_lalu'), literal_column('0').label('inv_kini'), 
                literal_column('0').label('payment_lalu'), literal_column('0').label('payment_kini')
                ).join(Rekening, Unit
                ).filter(ARInvoiceItem.tahun==self.session['tahun'], ARInvoiceItem.unit_id==self.session['unit_id'], 
                ARInvoiceItem.tanggal < mulai        
                ).group_by(ARInvoiceItem.tahun, Unit.kode, Unit.nama, Rekening.kode)

            query3 = DBSession.query(ARPaymentItem.tahun.label('tahun'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), 
                Rekening.kode.label('subrek_kd'), 
                literal_column('0').label('inv_lalu'), literal_column('0').label('inv_kini'), 
                literal_column('0').label('payment_lalu'), func.sum(ARPaymentItem.amount).label('payment_kini')
                ).join(Rekening, Unit
                ).filter(ARPaymentItem.tahun==self.session['tahun'], ARPaymentItem.unit_id==self.session['unit_id'], 
                ARPaymentItem.tanggal.between(mulai,selesai        
                )).group_by(ARPaymentItem.tahun, Unit.kode, Unit.nama, Rekening.kode)

            query4 = DBSession.query(ARPaymentItem.tahun.label('tahun'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), 
                Rekening.kode.label('subrek_kd'), 
                literal_column('0').label('inv_lalu'), literal_column('0').label('inv_kini'), 
                func.sum(ARPaymentItem.amount).label('payment_lalu'), literal_column('0').label('payment_kini')
                ).join(Rekening, Unit
                ).filter(ARPaymentItem.tahun==self.session['tahun'], ARPaymentItem.unit_id==self.session['unit_id'], 
                ARPaymentItem.tanggal < mulai        
                ).group_by(ARPaymentItem.tahun, Unit.kode, Unit.nama, Rekening.kode)

            subq1 = query1.union(query2,query3,query4).subquery()
            
            subq = DBSession.query(subq1.c.tahun.label('tahun'), subq1.c.unit_kd, subq1.c.unit_nm, 
                subq1.c.subrek_kd.label('subrek_kd'), 
                func.sum(subq1.c.inv_lalu).label('inv_lalu'), func.sum(subq1.c.inv_kini).label('inv_kini'),
                func.sum(subq1.c.payment_lalu).label('payment_lalu'), func.sum(subq1.c.payment_kini).label('payment_kini'
                )).group_by(subq1.c.tahun, subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.subrek_kd).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq.c.tahun, subq.c.unit_kd, subq.c.unit_nm, 
                func.sum(subq.c.inv_lalu).label('inv_lalu'),func.sum(subq.c.inv_kini).label('inv_kini'),
                func.sum(subq.c.payment_lalu).label('payment_lalu'),func.sum(subq.c.payment_kini).label('payment_kini')
                ).filter(Rekening.kode==func.left(subq.c.subrek_kd, func.length(Rekening.kode))
                ,Rekening.level_id<tingkat).group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq.c.tahun, subq.c.unit_kd, subq.c.unit_nm)\
                .order_by(Rekening.kode).all()                    

            generator = r103Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            
            return response

class r001Generator(JasperGenerator):
    def __init__(self):
        super(r001Generator, self).__init__()
        self.reportname = get_rpath('apbd/akskpd/P001001.jrxml')
        self.xpath = '/apbd/akuntansi'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'akuntansi')
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_greeting, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "lalu").text = unicode(row.lalu)
            ET.SubElement(xml_greeting, "kini").text = unicode(row.kini)
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "mulai").text = mulai
            ET.SubElement(xml_greeting, "selesai").text = selesai
            ET.SubElement(xml_greeting, "tingkat").text = unicode(tingkat)
        return self.root

class r002Generator(JasperGenerator):
    def __init__(self):
        super(r002Generator, self).__init__()
        self.reportname = get_rpath('apbd/akskpd/P001002.jrxml')
        self.xpath = '/apbd/akuntansi'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'akuntansi')
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_greeting, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "anggaran").text = unicode(row.anggaran)
            ET.SubElement(xml_greeting, "lalu").text = unicode(row.lalu)
            ET.SubElement(xml_greeting, "kini").text = unicode(row.kini)
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "mulai").text = mulai
            ET.SubElement(xml_greeting, "selesai").text = selesai
            ET.SubElement(xml_greeting, "tingkat").text = unicode(tingkat)
        return self.root

class r003Generator(JasperGenerator):
    def __init__(self):
        super(r003Generator, self).__init__()
        self.reportname = get_rpath('apbd/akskpd/P001003.jrxml')
        self.xpath = '/apbd/akuntansi'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'akuntansi')
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_greeting, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "inv_lalu").text = unicode(row.inv_lalu)
            ET.SubElement(xml_greeting, "inv_kini").text = unicode(row.inv_kini)
            ET.SubElement(xml_greeting, "payment_lalu").text = unicode(row.payment_lalu)
            ET.SubElement(xml_greeting, "payment_kini").text = unicode(row.payment_kini)
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "mulai").text = mulai
            ET.SubElement(xml_greeting, "selesai").text = selesai
            ET.SubElement(xml_greeting, "tingkat").text = unicode(tingkat)
        return self.root

class r101Generator(JasperGenerator):
    def __init__(self):
        super(r101Generator, self).__init__()
        self.reportname = get_rpath('apbd/akskpd/P002001.jrxml')
        self.xpath = '/apbd/akuntansi'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'akuntansi')
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_greeting, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "lalu").text = unicode(row.lalu)
            ET.SubElement(xml_greeting, "kini").text = unicode(row.kini)
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "mulai").text = mulai
            ET.SubElement(xml_greeting, "selesai").text = selesai
            ET.SubElement(xml_greeting, "tingkat").text = unicode(tingkat)
        return self.root

class r102Generator(JasperGenerator):
    def __init__(self):
        super(r102Generator, self).__init__()
        self.reportname = get_rpath('apbd/akskpd/P002002.jrxml')
        self.xpath = '/apbd/akuntansi'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'akuntansi')
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_greeting, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "anggaran").text = unicode(row.anggaran)
            ET.SubElement(xml_greeting, "lalu").text = unicode(row.lalu)
            ET.SubElement(xml_greeting, "kini").text = unicode(row.kini)
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "mulai").text = mulai
            ET.SubElement(xml_greeting, "selesai").text = selesai
            ET.SubElement(xml_greeting, "tingkat").text = unicode(tingkat)
        return self.root

class r103Generator(JasperGenerator):
    def __init__(self):
        super(r103Generator, self).__init__()
        self.reportname = get_rpath('apbd/akskpd/P002003.jrxml')
        self.xpath = '/apbd/akuntansi'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'akuntansi')
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_greeting, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "inv_lalu").text = unicode(row.inv_lalu)
            ET.SubElement(xml_greeting, "inv_kini").text = unicode(row.inv_kini)
            ET.SubElement(xml_greeting, "payment_lalu").text = unicode(row.payment_lalu)
            ET.SubElement(xml_greeting, "payment_kini").text = unicode(row.payment_kini)
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "mulai").text = mulai
            ET.SubElement(xml_greeting, "selesai").text = selesai
            ET.SubElement(xml_greeting, "tingkat").text = unicode(tingkat)
        return self.root

