import os
import unittest
import os.path
import uuid
import sqlalchemy

from osipkd.tools import row2dict, xls_reader

from datetime import datetime
#from sqlalchemy import not_, func, case
from sqlalchemy import *
from sqlalchemy.sql.expression import literal_column
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from osipkd.models import DBSession
from osipkd.models.apbd_anggaran import Kegiatan, KegiatanSub, KegiatanItem
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

from pyjasper import (JasperGenerator)
from pyjasper import (JasperGeneratorWithSubreport)
import xml.etree.ElementTree as ET
from pyramid.path import AssetResolver

from osipkd.models.base_model import *
from osipkd.models.pemda_model import *
from osipkd.models.apbd import * 
from osipkd.models.apbd_anggaran import * 
from osipkd.models.apbd_tu import *

"""import unittest
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
"""

angka = {1:'sat',2:'dua',3:'tiga',4:'empat',5:'lima',6:'enam',7:'tujuh',\
         8:'delapan',9:'sembilan'}
b = ' puluh '
c = ' ratus '
d = ' ribu '
e = ' juta '
f = ' miliyar '
g = ' triliun '
def Terbilang(x):   
    y = str(x)         
    n = len(y)        
    if n <= 3 :        
        if n == 1 :   
            if y == '0' :   
                return ''   
            else :         
                return angka[int(y)]   
        elif n == 2 :
            if y[0] == '1' :                
                if y[1] == '1' :
                    return 'sebelas'
                elif y[0] == '0':
                    x = y[1]
                    return Terbilang(x)
                elif y[1] == '0' :
                    return 'sepuluh'
                else :
                    return angka[int(y[1])] + ' belas'
            elif y[0] == '0' :
                x = y[1]
                return Terbilang(x)
            else :
                x = y[1]
                return angka[int(y[0])] + b + Terbilang(x)
        else :
            if y[0] == '1' :
                x = y[1:]
                return 'seratus ' + Terbilang(x)
            elif y[0] == '0' : 
                x = y[1:]
                return Terbilang(x)
            else :
                x = y[1:]
                return angka[int(y[0])] + c + Terbilang(x)
    elif 3< n <=6 :
        p = y[-3:]
        q = y[:-3]
        if q == '1' :
            return 'seribu' + Terbilang(p)
        elif q == '000' :
            return Terbilang
            return Terbilang(q) + d + Terbilang(p)
    elif 6 < n <= 9 :
        r = y[-6:]
        s = y[:-6]
        return Terbilang(s) + e + Terbilang(r)
    elif 9 < n <= 12 :
        t = y[-9:]
        u = y[:-9]
        return Terbilang(u) + f + Terbilang(t)
    else:
        v = y[-12:]
        w = y[:-12]
        return Terbilang(w) + g + Terbilang(v)
        
def get_rpath(filename):
    a = AssetResolver('osipkd')
    resolver = a.resolve(''.join(['reports/',filename]))
    return resolver.abspath()

class ViewTUPPKDLap(BaseViews):
    def __init__(self, context, request):
        global customer
        global logo
        BaseViews.__init__(self, context, request)
        self.app = 'tuppkd'

        #if 'app' in request.params and request.params['app'] == self.app and self.logged:
        row = DBSession.query(Tahun.status_apbd).filter(Tahun.tahun==self.tahun).first()
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

        self.cust_nm = 'cust_nm' in self.session and self.session['cust_nm'] or ''
        customer = self.cust_nm
        #bulan = 'bulan' in request.params and request.params['bulan'] and int(request.params['bulan']) or 0
        logo = self.request.static_url('osipkd:static/img/logo.png')

    # SPD
    @view_config(route_name="ap-report-spd", renderer="templates/report-ppkd/spd.pt", permission="read")
    def ap_report_spd(self):
        params = self.request.params
        return dict(datas=self.datas,)

    @view_config(route_name="ap-report-spd-act", renderer="json", permission="read")
    def ap_report_spd_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        mulai = 'mulai' in params and params['mulai'] or 0
        selesai = 'selesai' in params and params['selesai'] or 0
        if url_dict['act']=='1' :
            query = DBSession.query(Spd.tahun_id, Spd.kode, Spd.tanggal, Unit.kode.label('unit_kd'), 
               Unit.nama.label('unit_nm'), Urusan.kode.label('urusan_kd'),
               func.sum(case([(Kegiatan.kode=='0.00.00.21',SpdItem.nominal)], else_=0)).label('btl'),
               func.sum(case([(Kegiatan.kode<>'0.00.00.21',SpdItem.nominal)], else_=0)).label('bl'),
               ).join(Unit).join(Urusan).join(SpdItem).join(KegiatanSub).join(Kegiatan
               ).filter(Spd.tahun_id==self.session['tahun'], 
               Spd.tanggal.between(mulai,selesai),
               ).group_by(Spd.tahun_id, Spd.kode, Spd.tanggal, Unit.kode, 
               Unit.nama, Urusan.kode,
               ).order_by(Spd.tanggal)
                 
            generator = b203r0034Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        elif url_dict['act']=='2' :
            query = DBSession.query(Spd.tahun_id, Spd.kode, Spd.tanggal, Unit.kode.label('unit_kd'), 
               Unit.nama.label('unit_nm'), Urusan.kode.label('urusan_kd'),
               func.sum(case([(Kegiatan.kode=='0.00.00.21',SpdItem.nominal)], else_= 0)).label('btl'),
               func.sum(case([(Kegiatan.kode<>'0.00.00.21',SpdItem.nominal)], else_= 0)).label('bl'),
               ).join(Unit).join(Urusan).join(SpdItem).join(KegiatanSub).join(Kegiatan
               ).filter(Spd.tahun_id==self.session['tahun'], 
               Spd.tanggal.between(mulai,selesai),
               ).group_by(Spd.tahun_id, Spd.kode, Spd.tanggal, Unit.kode, 
               Unit.nama, Urusan.kode,
               ).order_by(Spd.tanggal)
                 
            generator = b203r0035Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
            
        ### SPD 1
        elif url_dict['act']=='spd1' :
            mulai = 'spd1' in params and params['spd1'] 
            selesai = 'spd2' in params and params['spd2'] 
            query = DBSession.query(Spd.kode, Spd.nama, Spd.tahun_id,
               Spd.triwulan_id, Spd.tanggal, Spd.is_bl, Unit.nama.label('unit_nm'),
               Tahun.no_perda, Tahun.tgl_perda, Tahun.no_perkdh, Tahun.tgl_perkdh,
               Tahun.no_perda_rev, Tahun.tgl_perda_rev, Tahun.no_perkdh_rev, Tahun.tgl_perkdh_rev,
               func.sum(SpdItem.nominal).label('nominal'), func.sum(SpdItem.anggaran).label('anggaran'),
               func.sum(SpdItem.lalu).label('lalu')
               ).filter(Spd.unit_id==Unit.id, Spd.id==SpdItem.ap_spd_id,
               Spd.tahun_id==Tahun.id, Spd.tahun_id==self.session['tahun'], 
               func.substr(Spd.kode,6,5).between(mulai,selesai),
               ).group_by(Spd.kode, Spd.nama, Spd.tahun_id,
               Spd.triwulan_id, Spd.tanggal, Spd.is_bl, Unit.nama,
               Tahun.no_perda, Tahun.tgl_perda, Tahun.no_perkdh, Tahun.tgl_perkdh,
               Tahun.no_perda_rev, Tahun.tgl_perda_rev, Tahun.no_perkdh_rev, Tahun.tgl_perkdh_rev
               ).order_by(Spd.kode)
               
            generator = b203r0031Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ### SPD 2
        elif url_dict['act']=='spd2' :
            mulai = 'spd1' in params and params['spd1'] 
            selesai = 'spd2' in params and params['spd2'] 
            query = DBSession.query(Spd.kode, Spd.nama, Spd.tahun_id,
               Spd.triwulan_id, Spd.tanggal, Unit.nama.label('unit_nm'),
               Urusan.kode.label('urusan_kd'), Unit.kode.label('unit_kd'), Kegiatan.kode.label('keg_kd'), 
               SpdItem.anggaran, SpdItem.nominal, SpdItem.lalu
               ).join(Unit).join(Urusan).join(SpdItem).join(KegiatanSub).join(Kegiatan
               ).filter(Spd.tahun_id==self.session['tahun'], 
               func.substr(Spd.kode,6,5).between(mulai,selesai),
               Kegiatan.kode=='0.00.00.21'
               ).order_by(Spd.kode)
               
            generator = b203r0032Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ### SPD 3
        elif url_dict['act']=='spd3' :
            mulai = 'spd1' in params and params['spd1'] 
            selesai = 'spd2' in params and params['spd2'] 
            query = DBSession.query(Spd.kode, Spd.nama, Spd.tahun_id,
               Spd.triwulan_id, Spd.tanggal, Unit.nama.label('unit_nm'),
               Urusan.kode.label('urusan_kd'), Unit.kode.label('unit_kd'), Kegiatan.kode.label('keg_kd'), 
               SpdItem.anggaran, SpdItem.nominal, SpdItem.lalu
               ).join(Unit).join(Urusan).join(SpdItem).join(KegiatanSub).join(Kegiatan
               ).filter(Spd.tahun_id==self.session['tahun'], 
               func.substr(Spd.kode,6,5).between(mulai,selesai),
               Kegiatan.kode<>'0.00.00.21'
               ).order_by(Spd.kode)
               
            generator = b203r0033Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
               
            generator = b203r0033Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

    # SP2D
    @view_config(route_name="ap-report-sp2d", renderer="templates/report-ppkd/sp2d.pt", permission="read")
    def ap_report_sp2d(self):
        params = self.request.params
        return dict(datas=self.datas,)

    @view_config(route_name="ap-report-sp2d-act", renderer="json", permission="read")
    def ap_report_sp2d_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        tipe = 'tipe' in params and params['tipe'] and int(params['tipe']) or 0
        mulai = 'mulai' in params and params['mulai'] or 0
        selesai = 'selesai' in params and params['selesai'] or 0
        if url_dict['act']=='1' :
            if tipe ==0 :
               query = DBSession.query(Spp.tahun_id.label('tahun'), Unit.id.label('unit_id'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                  Spp.jenis, 
                  Sp2d.kode.label('sp2d_kd'), Sp2d.tanggal.label('tgl_sp2d'), Sp2d.nama.label('sp2d_nm'),
                  Sp2d.bud_nip, Sp2d.bud_nama, Spp.ap_nama, Spp.nama.label('spp_nm'), 
                  func.sum(case([(func.substr(Rekening.kode,1,5)=='5.1.1',APInvoiceItem.amount)], else_=0)).label('nominal_gj'),
                  func.sum(case([(func.substr(Rekening.kode,1,5)!='5.1.1',APInvoiceItem.amount)], else_=0)).label('nominal')
                  ).filter(Sp2d.ap_spm_id==Spm.id, Spm.ap_spp_id==Spp.id, Spp.unit_id==Unit.id,
                  SppItem.ap_spp_id==Spp.id, APInvoiceItem.ap_invoice_id==SppItem.ap_invoice_id,
                  APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                  KegiatanItem.rekening_id==Rekening.id, Spp.unit_id==self.session['unit_id'],
                  Spp.tahun_id==self.session['tahun'],
                  Sp2d.tanggal.between(mulai,selesai)        
                  ).group_by(Spp.tahun_id, Unit.id, Unit.kode, Unit.nama,
                  Spp.jenis, Sp2d.kode, Sp2d.tanggal, Sp2d.nama,
                  Sp2d.bud_nip, Sp2d.bud_nama, Spp.ap_nama, Spp.nama 
                  ).order_by(Sp2d.tanggal).all()

            else:
               query = DBSession.query(Spp.tahun_id.label('tahun'), Unit.id.label('unit_id'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                  Spp.jenis, 
                  Sp2d.kode.label('sp2d_kd'), Sp2d.tanggal.label('tgl_sp2d'), Sp2d.nama.label('sp2d_nm'),
                  Sp2d.bud_nip, Sp2d.bud_nama, Spp.ap_nama, Spp.nama.label('spp_nm'), 
                  func.sum(case([(func.substr(Rekening.kode,1,5)=='5.1.1',APInvoiceItem.amount)], else_=0)).label('nominal_gj'),
                  func.sum(case([(func.substr(Rekening.kode,1,5)!='5.1.1',APInvoiceItem.amount)], else_=0)).label('nominal')
                  ).filter(Sp2d.ap_spm_id==Spm.id, Spm.ap_spp_id==Spp.id, Spp.unit_id==Unit.id,
                  SppItem.ap_spp_id==Spp.id, APInvoiceItem.ap_invoice_id==SppItem.ap_invoice_id,
                  APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                  KegiatanItem.rekening_id==Rekening.id, Spp.unit_id==self.session['unit_id'],
                  Spp.tahun_id==self.session['tahun'], Spp.jenis==tipe,
                  Sp2d.tanggal.between(mulai,selesai)        
                  ).group_by(Spp.tahun_id, Unit.id, Unit.kode, Unit.nama,
                  Spp.jenis, Sp2d.kode, Sp2d.tanggal, Sp2d.nama,
                  Sp2d.bud_nip, Sp2d.bud_nama, Spp.ap_nama, Spp.nama 
                  ).order_by(Sp2d.tanggal).all()

            generator = b204r0000Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        elif url_dict['act']=='2' :
            if tipe ==0 :
                query = DBSession.query(Spp.tahun_id.label('tahun'), Unit.id.label('unit_id'), Unit.kode.label('unit_kd'), 
                  Unit.nama.label('unit_nm'), Spp.nama.label('spp_nm'), Spp.jenis, Spp.ap_nama,
                  Sp2d.kode.label('sp2d_kd'), Sp2d.tanggal.label('tgl_sp2d'), Sp2d.nama.label('sp2d_nm'),
                  Sp2d.bud_nip, Sp2d.bud_nama,  
                  func.sum(case([(Spp.jenis==1,APInvoiceItem.amount)], else_=0)).label('UP'),
                  func.sum(case([(Spp.jenis==2,APInvoiceItem.amount)], else_=0)).label('TU'),
                  func.sum(case([(Spp.jenis==3,APInvoiceItem.amount)], else_=0)).label('GU'),
                  func.sum(case([(and_(Spp.jenis==4,func.substr(Rekening.kode,1,5)=='5.1.1'),APInvoiceItem.amount)], else_=0)).label('LS_GJ'),
                  func.sum(case([(and_(Spp.jenis==4,func.substr(Rekening.kode,1,5)!='5.1.1'),APInvoiceItem.amount)], else_=0)).label('LS')
                  ).filter(Sp2d.ap_spm_id==Spm.id, Spm.ap_spp_id==Spp.id, Spp.unit_id==Unit.id,
                  SppItem.ap_spp_id==Spp.id, APInvoiceItem.ap_invoice_id==SppItem.ap_invoice_id,
                  APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                  KegiatanItem.rekening_id==Rekening.id, Spp.unit_id==self.session['unit_id'],
                  Spp.tahun_id==self.session['tahun'],  
                  Sp2d.tanggal.between(mulai,selesai)        
                  ).group_by(Spp.tahun_id, Unit.id, Unit.kode, Unit.nama, Spp.nama, Spp.jenis, Spp.ap_nama, 
                  Sp2d.tanggal, Sp2d.kode, Sp2d.nama, Sp2d.bud_nip, Sp2d.bud_nama, 
                  ).order_by(Sp2d.tanggal).all()
            else:
                query = DBSession.query(Spp.tahun_id.label('tahun'), Unit.id.label('unit_id'), Unit.kode.label('unit_kd'), 
                  Unit.nama.label('unit_nm'), Spp.nama.label('spp_nm'), Spp.jenis, Spp.ap_nama,
                  Sp2d.kode.label('sp2d_kd'), Sp2d.tanggal.label('tgl_sp2d'), Sp2d.nama.label('sp2d_nm'),
                  Sp2d.bud_nip, Sp2d.bud_nama,  
                  func.sum(case([(Spp.jenis==1,APInvoiceItem.amount)], else_=0)).label('UP'),
                  func.sum(case([(Spp.jenis==2,APInvoiceItem.amount)], else_=0)).label('TU'),
                  func.sum(case([(Spp.jenis==3,APInvoiceItem.amount)], else_=0)).label('GU'),
                  func.sum(case([(and_(Spp.jenis==4,func.substr(Rekening.kode,1,5)=='5.1.1'),APInvoiceItem.amount)], else_=0)).label('LS_GJ'),
                  func.sum(case([(and_(Spp.jenis==4,func.substr(Rekening.kode,1,5)!='5.1.1'),APInvoiceItem.amount)], else_=0)).label('LS')
                  ).filter(Sp2d.ap_spm_id==Spm.id, Spm.ap_spp_id==Spp.id, Spp.unit_id==Unit.id,
                  SppItem.ap_spp_id==Spp.id, APInvoiceItem.ap_invoice_id==SppItem.ap_invoice_id,
                  APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                  KegiatanItem.rekening_id==Rekening.id, Spp.unit_id==self.session['unit_id'],
                  Spp.tahun_id==self.session['tahun'],  Spp.jenis==tipe,  
                  Sp2d.tanggal.between(mulai,selesai)        
                  ).group_by(Spp.tahun_id, Unit.id, Unit.kode, Unit.nama, Spp.nama, Spp.jenis, Spp.ap_nama, 
                  Sp2d.tanggal, Sp2d.kode, Sp2d.nama, Sp2d.bud_nip, Sp2d.bud_nama, 
                  ).order_by(Sp2d.tanggal).all()

            generator = b204r0001Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        elif url_dict['act']=='3' :
            if tipe ==0 :
               query = DBSession.query(Spp.tahun_id.label('tahun'), Unit.id.label('unit_id'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                  Spp.jenis, 
                  Sp2d.kode.label('sp2d_kd'), Sp2d.tanggal.label('tgl_sp2d'), Sp2d.nama.label('sp2d_nm'),
                  Sp2d.bud_nip, Sp2d.bud_nama, Spp.ap_nama, Spp.nama.label('spp_nm'), 
                  func.sum(case([(func.substr(Rekening.kode,1,5)=='5.1.1',APInvoiceItem.amount)], else_=0)).label('nominal_gj'),
                  func.sum(case([(func.substr(Rekening.kode,1,5)!='5.1.1',APInvoiceItem.amount)], else_=0)).label('nominal')
                  ).filter(Sp2d.ap_spm_id==Spm.id, Spm.ap_spp_id==Spp.id, Spp.unit_id==Unit.id,
                  SppItem.ap_spp_id==Spp.id, APInvoiceItem.ap_invoice_id==SppItem.ap_invoice_id,
                  APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                  KegiatanItem.rekening_id==Rekening.id, Spp.unit_id==self.session['unit_id'],
                  Spp.tahun_id==self.session['tahun'],
                  Sp2d.tanggal.between(mulai,selesai)        
                  ).group_by(Spp.tahun_id, Unit.id, Unit.kode, Unit.nama,
                  Spp.jenis, Sp2d.kode, Sp2d.tanggal, Sp2d.nama,
                  Sp2d.bud_nip, Sp2d.bud_nama, Spp.ap_nama, Spp.nama 
                  ).order_by(Sp2d.tanggal).all()
            else:
               query = DBSession.query(Spp.tahun_id.label('tahun'), Unit.id.label('unit_id'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                  Spp.jenis, 
                  Sp2d.kode.label('sp2d_kd'), Sp2d.tanggal.label('tgl_sp2d'), Sp2d.nama.label('sp2d_nm'),
                  Sp2d.bud_nip, Sp2d.bud_nama, Spp.ap_nama, Spp.nama.label('spp_nm'), 
                  func.sum(case([(func.substr(Rekening.kode,1,5)=='5.1.1',APInvoiceItem.amount)], else_=0)).label('nominal_gj'),
                  func.sum(case([(func.substr(Rekening.kode,1,5)!='5.1.1',APInvoiceItem.amount)], else_=0)).label('nominal')
                  ).filter(Sp2d.ap_spm_id==Spm.id, Spm.ap_spp_id==Spp.id, Spp.unit_id==Unit.id,
                  SppItem.ap_spp_id==Spp.id, APInvoiceItem.ap_invoice_id==SppItem.ap_invoice_id,
                  APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                  KegiatanItem.rekening_id==Rekening.id, Spp.unit_id==self.session['unit_id'],
                  Spp.tahun_id==self.session['tahun'], Spp.jenis==tipe,
                  Sp2d.tanggal.between(mulai,selesai)        
                  ).group_by(Spp.tahun_id, Unit.id, Unit.kode, Unit.nama,
                  Spp.jenis, Sp2d.kode, Sp2d.tanggal, Sp2d.nama,
                  Sp2d.bud_nip, Sp2d.bud_nama, Spp.ap_nama, Spp.nama 
                  ).order_by(Sp2d.tanggal).all()

            generator = b204r0002Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        elif url_dict['act']=='4' :
            if tipe ==0 :
                query = DBSession.query(Spp.tahun_id.label('tahun'), Unit.id.label('unit_id'), Unit.kode.label('unit_kd'), 
                  Unit.nama.label('unit_nm'), Spp.nama.label('spp_nm'), Spp.jenis, Spp.ap_nama,
                  Spm.id.label('spm_id'),
                  Sp2d.kode.label('sp2d_kd'), Sp2d.tanggal.label('tgl_sp2d'), Sp2d.nama.label('sp2d_nm'),
                  Sp2d.bud_nip, Sp2d.bud_nama, Spp.nominal, 
                  ).filter(Sp2d.ap_spm_id==Spm.id, Spm.ap_spp_id==Spp.id, Spp.unit_id==Unit.id,
                  SppItem.ap_spp_id==Spp.id, APInvoiceItem.ap_invoice_id==SppItem.ap_invoice_id,
                  APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                  KegiatanItem.rekening_id==Rekening.id, Spp.unit_id==self.session['unit_id'],
                  Spp.tahun_id==self.session['tahun'], Spp.jenis==4, func.substr(Rekening.kode,1,5)=='5.1.1',
                  Sp2d.tanggal.between(mulai,selesai)        
                  ).order_by(Sp2d.tanggal).all()
            else:
                query = DBSession.query(Spp.tahun_id.label('tahun'), Unit.id.label('unit_id'), Unit.kode.label('unit_kd'), 
                  Unit.nama.label('unit_nm'), Spp.nama.label('spp_nm'), Spp.jenis, Spp.ap_nama,
                  Spm.id.label('spm_id'),
                  Sp2d.kode.label('sp2d_kd'), Sp2d.tanggal.label('tgl_sp2d'), Sp2d.nama.label('sp2d_nm'),
                  Sp2d.bud_nip, Sp2d.bud_nama, Spp.nominal, 
                  ).filter(Sp2d.ap_spm_id==Spm.id, Spm.ap_spp_id==Spp.id, Spp.unit_id==Unit.id,
                  SppItem.ap_spp_id==Spp.id, APInvoiceItem.ap_invoice_id==SppItem.ap_invoice_id,
                  APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                  KegiatanItem.rekening_id==Rekening.id, Spp.unit_id==self.session['unit_id'],
                  Spp.tahun_id==self.session['tahun'], Spp.jenis==4, func.substr(Rekening.kode,1,5)=='5.1.1',
                  Sp2d.tanggal.between(mulai,selesai)        
                  ).order_by(Sp2d.tanggal).all()

            generator = b204r0003Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        elif url_dict['act']=='5' :
            if tipe ==0 :
               query = DBSession.query(Spp.tahun_id.label('tahun'), Unit.id.label('unit_id'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                  Spp.jenis, 
                  Sp2d.kode.label('sp2d_kd'), Sp2d.tanggal.label('tgl_sp2d'), Sp2d.nama.label('sp2d_nm'),
                  Sp2d.bud_nip, Sp2d.bud_nama, Spp.ap_nama, Spp.nama.label('spp_nm'), 
                  func.sum(case([(func.substr(Rekening.kode,1,5)=='5.1.1',APInvoiceItem.amount)], else_=0)).label('nominal_gj'),
                  func.sum(case([(func.substr(Rekening.kode,1,5)!='5.1.1',APInvoiceItem.amount)], else_=0)).label('nominal'),
                  func.sum(APInvoiceItem.ppn).label('ppn'),
                  func.sum(APInvoiceItem.pph).label('pph')
                  ).filter(Sp2d.ap_spm_id==Spm.id, Spm.ap_spp_id==Spp.id, Spp.unit_id==Unit.id,
                  SppItem.ap_spp_id==Spp.id, APInvoiceItem.ap_invoice_id==SppItem.ap_invoice_id,
                  APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                  KegiatanItem.rekening_id==Rekening.id, Spp.unit_id==self.session['unit_id'],
                  Spp.tahun_id==self.session['tahun'],
                  Sp2d.tanggal.between(mulai,selesai)        
                  ).group_by(Spp.tahun_id, Unit.id, Unit.kode, Unit.nama,
                  Spp.jenis, Sp2d.kode, Sp2d.tanggal, Sp2d.nama,
                  Sp2d.bud_nip, Sp2d.bud_nama, Spp.ap_nama, Spp.nama 
                  ).order_by(Sp2d.tanggal).all()
            else:
               query = DBSession.query(Spp.tahun_id.label('tahun'), Unit.id.label('unit_id'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                  Spp.jenis, 
                  Sp2d.kode.label('sp2d_kd'), Sp2d.tanggal.label('tgl_sp2d'), Sp2d.nama.label('sp2d_nm'),
                  Sp2d.bud_nip, Sp2d.bud_nama, Spp.ap_nama, Spp.nama.label('spp_nm'), 
                  func.sum(case([(func.substr(Rekening.kode,1,5)=='5.1.1',APInvoiceItem.amount)], else_=0)).label('nominal_gj'),
                  func.sum(case([(func.substr(Rekening.kode,1,5)!='5.1.1',APInvoiceItem.amount)], else_=0)).label('nominal'),
                  func.sum(APInvoiceItem.ppn).label('ppn'),
                  func.sum(APInvoiceItem.pph).label('pph')
                  ).filter(Sp2d.ap_spm_id==Spm.id, Spm.ap_spp_id==Spp.id, Spp.unit_id==Unit.id,
                  SppItem.ap_spp_id==Spp.id, APInvoiceItem.ap_invoice_id==SppItem.ap_invoice_id,
                  APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                  KegiatanItem.rekening_id==Rekening.id, Spp.unit_id==self.session['unit_id'],
                  Spp.tahun_id==self.session['tahun'], Spp.jenis==tipe,
                  Sp2d.tanggal.between(mulai,selesai)        
                  ).group_by(Spp.tahun_id, Unit.id, Unit.kode, Unit.nama,
                  Spp.jenis, Sp2d.kode, Sp2d.tanggal, Sp2d.nama,
                  Sp2d.bud_nip, Sp2d.bud_nama, Spp.ap_nama, Spp.nama 
                  ).order_by(Sp2d.tanggal).all()

            generator = b204r0004Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        elif url_dict['act']=='sp2d' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            subq1 = DBSession.query(Sp2d.id.label('sp2d_id'), Sp2d.kode.label('sp2d_kd'), Sp2d.tanggal.label('sp2d_tgl'), 
                     Spm.id.label('spm_id'), Spm.kode.label('spm_kd'), Spm.nama.label('spm_nm'), Spm.tanggal.label('spm_tgl'), Spp.id.label('spp_id'), 
                     Spp.kode.label('spp_kd'), Spp.nama.label('spp_nm'), Spp.tanggal.label('spp_tgl'), Spp.jenis.label('jenis'), 
                     Spp.ap_nama.label('ap_nama'), Spp.ap_bank.label('ap_bank'), Spp.ap_rekening.label('ap_rekening'), Spp.ap_npwp.label('ap_npwp'), 
                     Spp.tahun_id.label('tahun_id'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), Kegiatan.kode.label('keg_kd'), 
                     Kegiatan.nama.label('keg_nm'), Program.kode.label('prg_kd'), Program.nama.label('prg_nm'), 
                     func.sum(APInvoiceItem.amount).label('nilai'), func.sum(APInvoiceItem.ppn).label('ppn'), 
                     func.sum(APInvoiceItem.pph).label('pph'), literal_column('0').label('potongan')
                     ).filter(Sp2d.ap_spm_id==Spm.id, Spm.ap_spp_id==Spp.id, Spp.unit_id==Unit.id,
                     SppItem.ap_spp_id==Spp.id, SppItem.ap_invoice_id==APInvoiceItem.ap_invoice_id, APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                     KegiatanItem.rekening_id==Rekening.id, KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                     KegiatanSub.kegiatan_id==Kegiatan.id, Kegiatan.program_id==Program.id,
                     Spp.unit_id==self.session['unit_id'], Spp.tahun_id==self.session['tahun'], Sp2d.id==pk_id,
                     func.left(Rekening.kode,1)=='5'
                     ).group_by(Sp2d.id, Sp2d.kode, Sp2d.tanggal, Spm.id, Spm.kode, 
                     Spm.nama, Spm.tanggal, Spp.id, Spp.kode, Spp.nama, Spp.tanggal, 
                     Spp.jenis, Spp.ap_nama, Spp.ap_bank, 
                     Spp.ap_rekening, Spp.ap_npwp, Spp.tahun_id, Unit.kode, Unit.nama, 
                     Kegiatan.kode, Kegiatan.nama, Program.kode, Program.nama 
                     )                         

            subq2 = DBSession.query(Sp2d.id.label('sp2d_id'), Sp2d.kode.label('sp2d_kd'), Sp2d.tanggal.label('sp2d_tgl'), 
                     Spm.id.label('spm_id'), Spm.kode.label('spm_kd'), Spm.nama.label('spm_nm'), Spm.tanggal.label('spm_tgl'), Spp.id.label('spp_id'), 
                     Spp.kode.label('spp_kd'), Spp.nama.label('spp_nm'), Spp.tanggal.label('spp_tgl'), Spp.jenis.label('jenis'), 
                     Spp.ap_nama.label('ap_nama'), Spp.ap_bank.label('ap_bank'), Spp.ap_rekening.label('ap_rekening'), Spp.ap_npwp.label('ap_npwp'), 
                     Spp.tahun_id.label('tahun_id'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), Kegiatan.kode.label('keg_kd'), 
                     Kegiatan.nama.label('keg_nm'), Program.kode.label('prg_kd'), Program.nama.label('prg_nm'), 
                     literal_column('0').label('nilai'), literal_column('0').label('ppn'), 
                     literal_column('0').label('pph'), func.sum(APInvoiceItem.amount).label('potongan')
                     ).filter(Sp2d.ap_spm_id==Spm.id, Spm.ap_spp_id==Spp.id, Spp.unit_id==Unit.id,
                     SppItem.ap_spp_id==Spp.id, SppItem.ap_invoice_id==APInvoiceItem.ap_invoice_id, APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                     KegiatanItem.rekening_id==Rekening.id, KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                     KegiatanSub.kegiatan_id==Kegiatan.id, Kegiatan.program_id==Program.id,
                     Spp.unit_id==self.session['unit_id'], Spp.tahun_id==self.session['tahun'], Sp2d.id==pk_id,
                     func.left(Rekening.kode,1)=='7'
                     ).group_by(Sp2d.id, Sp2d.kode, Sp2d.tanggal, Spm.id, Spm.kode, 
                     Spm.nama, Spm.tanggal, Spp.id, Spp.kode, Spp.nama, Spp.tanggal, 
                     Spp.jenis, Spp.ap_nama, Spp.ap_bank, 
                     Spp.ap_rekening, Spp.ap_npwp, Spp.tahun_id, Unit.kode, Unit.nama, 
                     Kegiatan.kode, Kegiatan.nama, Program.kode, Program.nama 
                     )                         
            
            subq = subq1.union(subq2).subquery()
            
            query = DBSession.query(subq.c.sp2d_id, subq.c.sp2d_kd, subq.c.sp2d_tgl, subq.c.spm_id, subq.c.spm_kd, 
                     subq.c.spm_nm, subq.c.spm_tgl, subq.c.spp_id, subq.c.spp_kd, subq.c.spp_nm, subq.c.spp_tgl, 
                     subq.c.jenis, subq.c.ap_nama, subq.c.ap_bank, subq.c.ap_rekening, 
                     subq.c.ap_npwp, subq.c.tahun_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.keg_kd, subq.c.keg_nm, subq.c.prg_kd, 
                     subq.c.prg_nm, func.sum(subq.c.nilai).label('nilai'),func.sum(subq.c.ppn).label('ppn'), 
                     func.sum(subq.c.pph).label('pph'),func.sum(subq.c.potongan).label('potongan')
                     ).group_by(subq.c.sp2d_id, subq.c.sp2d_kd, subq.c.sp2d_tgl, subq.c.spm_id, subq.c.spm_kd, 
                     subq.c.spm_nm, subq.c.spm_tgl, subq.c.spp_id, subq.c.spp_kd, subq.c.spp_nm, subq.c.spp_tgl, 
                     subq.c.jenis, subq.c.ap_nama, subq.c.ap_bank, subq.c.ap_rekening, 
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

        elif url_dict['act']=='giro' :
            query = DBSession.query(Giro.kode, Giro.nama, Giro.tanggal,
               Giro.nominal, Sp2d.kode.label('sp2d_kd'), Spm.nama.label('spm_nm'),
               Spp.ap_bank, Spp.ap_rekening,
               Unit.nama.label('unit_nm')
               ).filter(Giro.ap_sp2d_id==Sp2d.id, Sp2d.ap_spm_id==Spm.id,
               Spm.ap_spp_id==Spp.id, Giro.tahun_id==self.session['tahun'], Giro.unit_id==Unit.id,
               Giro.unit_id==self.session['unit_id']
               ).order_by(Giro.tanggal).all()
               
            generator = b203r002Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
            
    #### Realisasi
    @view_config(route_name="ap-report-real", renderer="templates/report-ppkd/realisasi.pt", permission="read")
    def ar_report_real(self):
        params = self.request.params
        return dict(datas=self.datas,)

    @view_config(route_name="ap-report-real-act", renderer="json", permission="read")
    def ap_report_real_act(self):
        global bln
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        bln = 'bulan' in params and params['bulan'] and int(params['bulan']) or 0
        #### Realisasi 1
        if url_dict['act']=='1' :
            subq1 = (DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                KegiatanSub.tahun_id.label('tahun_id'),
                (KegiatanItem.vol_4_1* KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jml'), 
                sqlalchemy.sql.literal_column("0").label('realisasi')
                ).filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                        KegiatanItem.rekening_id==Rekening.id,
                        KegiatanSub.tahun_id==self.session['tahun']
                ).union(DBSession.query(
                Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                Spp.tahun_id.label('tahun_id'), sqlalchemy.sql.literal_column("0").label('jml'),
                func.max(APInvoiceItem.amount).label('realisasi')
                ).filter(APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                        APInvoiceItem.ap_invoice_id==APInvoice.id,
                        KegiatanItem.rekening_id==Rekening.id,
                        SppItem.ap_invoice_id==APInvoice.id,
                        SppItem.ap_spp_id==Spp.id,
                        Spm.ap_spp_id==Spp.id,                            
                        Sp2d.ap_spm_id==Spm.id, 
                        Spp.tahun_id==self.session['tahun'], extract('month',Sp2d.tanggal) <= bln
                ).group_by(Rekening.kode, Rekening.nama, Spp.tahun_id
                ))).subquery()

            subq2 = DBSession.query(subq1.c.subrek_kd.label('subrek_kd'), subq1.c.subrek_nm.label('subrek_nm'), 
                subq1.c.tahun_id.label('tahun_id'), 
                func.sum(subq1.c.jml).label('jml'), func.sum(subq1.c.realisasi).label('realisasi')
                ).group_by(subq1.c.subrek_kd, subq1.c.subrek_nm, subq1.c.tahun_id).subquery()                    

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq2.c.tahun_id, 
                func.sum(subq2.c.jml).label('jumlah'),
                func.sum(subq2.c.realisasi).label('realisasi'),
                ).filter(Rekening.kode==func.left(subq2.c.subrek_kd, func.length(Rekening.kode)),
                Rekening.level_id<4)\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq2.c.tahun_id)\
                .order_by(Rekening.kode).all()                    

            generator = b204r100Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        #### Realisasi 2
        elif url_dict['act']=='2' :
            subq1 = (DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                KegiatanSub.tahun_id.label('tahun_id'),
                (KegiatanItem.vol_4_1* KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jml'), 
                sqlalchemy.sql.literal_column("0").label('realisasi')
                ).filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                        KegiatanItem.rekening_id==Rekening.id,
                        KegiatanSub.tahun_id==self.session['tahun'], KegiatanSub.unit_id==self.session['unit_id']
                ).union(DBSession.query(
                Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                Spp.tahun_id.label('tahun_id'), sqlalchemy.sql.literal_column("0").label('jml'),
                func.max(APInvoiceItem.amount).label('realisasi')
                ).filter(APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                        APInvoiceItem.ap_invoice_id==APInvoice.id,
                        KegiatanItem.rekening_id==Rekening.id,
                        SppItem.ap_invoice_id==APInvoice.id,
                        SppItem.ap_spp_id==Spp.id,
                        Spm.ap_spp_id==Spp.id,                            
                        Sp2d.ap_spm_id==Spm.id, 
                        Spp.tahun_id==self.session['tahun'], extract('month',Sp2d.tanggal) <= bln,
                        Spp.unit_id==self.session['unit_id']
                ).group_by(Rekening.kode, Rekening.nama, Spp.tahun_id
                ))).subquery()

            subq2 = DBSession.query(subq1.c.subrek_kd.label('subrek_kd'), subq1.c.subrek_nm.label('subrek_nm'), 
                subq1.c.tahun_id.label('tahun_id'), 
                func.sum(subq1.c.jml).label('jml'), func.sum(subq1.c.realisasi).label('realisasi')
                ).group_by(subq1.c.subrek_kd, subq1.c.subrek_nm, subq1.c.tahun_id).subquery()                    

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq2.c.tahun_id, 
                func.sum(subq2.c.jml).label('jumlah'),
                func.sum(subq2.c.realisasi).label('realisasi'),
                ).filter(Rekening.kode==func.left(subq2.c.subrek_kd, func.length(Rekening.kode)),
                Rekening.level_id<4)\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq2.c.tahun_id)\
                .order_by(Rekening.kode).all()                    

            generator = b204r300Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        elif url_dict['act']=='3' :
            subq1 = (DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                Unit.id.label('unit_id'),Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), 
                KegiatanSub.tahun_id.label('tahun_id'),
                Program.kode.label('program_kd'), Program.nama.label('program_nm'), 
                Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                (KegiatanItem.vol_4_1* KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jml'), 
                sqlalchemy.sql.literal_column("0").label('realisasi')
                ).filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                        KegiatanItem.rekening_id==Rekening.id, KegiatanSub.unit_id==Unit.id, 
                        Unit.urusan_id==Urusan.id, KegiatanSub.kegiatan_id==Kegiatan.id,
                        Kegiatan.program_id==Program.id,
                        KegiatanSub.tahun_id==self.session['tahun'], KegiatanSub.unit_id==self.session['unit_id']
                ).union(DBSession.query(
                Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                Unit.id.label('unit_id'),Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), 
                Spp.tahun_id.label('tahun_id'), 
                Program.kode.label('program_kd'), Program.nama.label('program_nm'), 
                Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                sqlalchemy.sql.literal_column("0").label('jml'),
                func.max(APInvoiceItem.amount).label('realisasi')
                ).filter(APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                        APInvoiceItem.ap_invoice_id==APInvoice.id,
                        KegiatanItem.rekening_id==Rekening.id,
                        Spp.unit_id==Unit.id,
                        Unit.urusan_id==Urusan.id,
                        KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                        KegiatanSub.kegiatan_id==Kegiatan.id,
                        Kegiatan.program_id==Program.id,
                        SppItem.ap_invoice_id==APInvoice.id,
                        SppItem.ap_spp_id==Spp.id,
                        Spm.ap_spp_id==Spp.id,                            
                        Sp2d.ap_spm_id==Spm.id, 
                        Spp.tahun_id==self.session['tahun'], extract('month',Sp2d.tanggal) <= bln,
                        Spp.unit_id==self.session['unit_id']
                ).group_by(Rekening.kode, Rekening.nama, Unit.id, Unit.kode, Unit.nama,
                        Urusan.kode, Urusan.nama, Spp.tahun_id, Program.kode, Program.nama, 
                        Kegiatan.kode, Kegiatan.nama
                ))).subquery()

            subq = DBSession.query(subq1.c.subrek_kd.label('subrek_kd'), subq1.c.subrek_nm.label('subrek_nm'), 
                subq1.c.unit_id, subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.urusan_kd, subq1.c.urusan_nm, 
                subq1.c.tahun_id, subq1.c.program_kd, subq1.c.program_nm, subq1.c.kegiatan_kd, subq1.c.kegiatan_nm,
                func.sum(subq1.c.jml).label('jml'), func.sum(subq1.c.realisasi).label('realisasi')
                ).group_by(subq1.c.subrek_kd.label('subrek_kd'), subq1.c.subrek_nm.label('subrek_nm'), 
                subq1.c.unit_id, subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.urusan_kd, subq1.c.urusan_nm, 
                subq1.c.tahun_id, subq1.c.program_kd, subq1.c.program_nm, subq1.c.kegiatan_kd, subq1.c.kegiatan_nm
                ).subquery()                    

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, Rekening.id.label('rekening_id'),
                subq.c.unit_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.urusan_kd, subq.c.urusan_nm, 
                subq.c.tahun_id, subq.c.program_kd, subq.c.program_nm, subq.c.kegiatan_kd, subq.c.kegiatan_nm, 
                case([(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='10'),1),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='21'),2),
                (and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='31'),4),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='32'),5)], 
                else_=3).label('jenis'),                    
                func.sum(subq.c.jml).label('jumlah'),func.sum(subq.c.realisasi).label('realisasi')
                ).filter(Rekening.kode==func.left(subq.c.subrek_kd, func.length(Rekening.kode))
                ).group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, Rekening.id, 
                subq.c.unit_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.urusan_kd, subq.c.urusan_nm, subq.c.tahun_id,
                subq.c.program_kd, subq.c.program_nm, subq.c.kegiatan_kd, subq.c.kegiatan_nm,
                case([(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='10'),1),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='21'),2),
                (and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='31'),4),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='32'),5)], 
                else_=3))\
                .order_by(case([(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='10'),1),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='21'),2),
                (and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='31'),4),(and_(subq.c.program_kd=='00',subq.c.kegiatan_kd=='32'),5)], 
                else_=3),subq.c.urusan_kd, subq.c.unit_kd, subq.c.program_kd, subq.c.kegiatan_kd, Rekening.kode).all() 
        
            generator = b204r200Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

#SPD 1
class b203r0031Generator(JasperGenerator):
    def __init__(self):
        super(b203r0031Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R2030031.jrxml')
        self.xpath = '/apbd/spd'
        self.root = ET.Element('apbd') 
    
    def generate_xml(self, tobegreeted):
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
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "logo").text = logo
            
        return self.root

#SPD 2
class b203r0032Generator(JasperGenerator):
    def __init__(self):
        super(b203r0032Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R2030032.jrxml')
        self.xpath = '/apbd/spd'
        self.root = ET.Element('apbd') 
    
    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spd')
            ET.SubElement(xml_greeting, "kode").text = row.kode
            ET.SubElement(xml_greeting, "nama").text = row.nama
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "triwulan_id").text = unicode(row.triwulan_id)
            ET.SubElement(xml_greeting, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "keg_kd").text = row.keg_kd
            ET.SubElement(xml_greeting, "anggaran").text = unicode(row.anggaran)
            ET.SubElement(xml_greeting, "nominal").text = unicode(row.nominal)
            ET.SubElement(xml_greeting, "lalu").text = unicode(row.lalu)
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "logo").text = logo
            
        return self.root

#SPD 3
class b203r0033Generator(JasperGenerator):
    def __init__(self):
        super(b203r0033Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R2030033.jrxml')
        self.xpath = '/apbd/spd'
        self.root = ET.Element('apbd') 
    
    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spd')
            ET.SubElement(xml_greeting, "kode").text = row.kode
            ET.SubElement(xml_greeting, "nama").text = row.nama
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "triwulan_id").text = unicode(row.triwulan_id)
            ET.SubElement(xml_greeting, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "keg_kd").text = row.keg_kd
            ET.SubElement(xml_greeting, "anggaran").text = unicode(row.anggaran)
            ET.SubElement(xml_greeting, "nominal").text = unicode(row.nominal)
            ET.SubElement(xml_greeting, "lalu").text = unicode(row.lalu)
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "logo").text = logo
            
        return self.root

#Register SPD 1
class b203r0034Generator(JasperGenerator):
    def __init__(self):
        super(b203r0034Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R2030034.jrxml')
        self.xpath = '/apbd/spd'
        self.root = ET.Element('apbd') 
    
    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spd')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "kode").text = row.kode
            ET.SubElement(xml_greeting, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "btl").text = unicode(row.btl)
            ET.SubElement(xml_greeting, "bl").text = unicode(row.bl)
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "logo").text = logo
        return self.root

#Register SPD 2
class b203r0035Generator(JasperGenerator):
    def __init__(self):
        super(b203r0035Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R2030035.jrxml')
        self.xpath = '/apbd/spd'
        self.root = ET.Element('apbd') 
    
    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spd')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "kode").text = row.kode
            ET.SubElement(xml_greeting, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "btl").text = unicode(row.btl)
            ET.SubElement(xml_greeting, "bl").text = unicode(row.bl)
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "logo").text = logo
        return self.root

#SP2D
class b203r001Generator(JasperGeneratorWithSubreport):
    def __init__(self):
        self.mainreport = get_rpath('apbd/tuppkd/R203001.jrxml')

        self.subreportlist = []
        self.subreportlist.append(get_rpath('apbd/tuppkd/R203001_subreport1.jrxml'))
        self.subreportlist.append(get_rpath('apbd/tuppkd/R203001_subreport2.jrxml'))

        self.xpath = '/apbd/sp2d'
        
        self.root = ET.Element('apbd')

    def generate_xml(self, tobegreeted):
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
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "logo").text = logo

            rows = DBSession.query(Rekening.kode, Rekening.nama, Unit.kode.label('unit_kd'),
               Kegiatan.kode.label('keg_kd'), Program.kode.label('prg_kd'),
               func.sum(APInvoiceItem.amount).label('jumlah')
               ).filter(Rekening.id==KegiatanItem.rekening_id, 
               KegiatanItem.id==APInvoiceItem.kegiatan_item_id,
               SppItem.ap_invoice_id==APInvoiceItem.ap_invoice_id,
               KegiatanSub.id==KegiatanItem.kegiatan_sub_id, KegiatanSub.unit_id==Unit.id, 
               Kegiatan.id==KegiatanSub.kegiatan_id, Program.id==Kegiatan.program_id,
               SppItem.ap_spp_id==row.spp_id, func.substr(Rekening.kode,1,1)=='5'
               ).group_by(Rekening.kode, Rekening.nama, Unit.kode, Kegiatan.kode, Program.kode
               ).order_by(Rekening.kode)
            for row2 in rows :
                xml_a = ET.SubElement(xml_greeting, "rekening")
                ET.SubElement(xml_a, "rek_kd").text =row2.kode
                ET.SubElement(xml_a, "rek_nm").text =row2.nama
                ET.SubElement(xml_a, "unit_kd").text =row2.unit_kd
                ET.SubElement(xml_a, "keg_kd").text =row2.keg_kd
                ET.SubElement(xml_a, "prg_kd").text =row2.prg_kd
                ET.SubElement(xml_a, "jumlah").text =unicode(row2.jumlah)
            
            rows1 = DBSession.query(Rekening.kode, Rekening.nama,
               (KegiatanItem.vol_4_1* KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jumlah')
               ).filter(Rekening.id==KegiatanItem.rekening_id, 
               KegiatanItem.id==APInvoiceItem.kegiatan_item_id,
               SppItem.ap_invoice_id==APInvoiceItem.ap_invoice_id,
               SppItem.ap_spp_id==row.spp_id, func.substr(Rekening.kode,1,1)=='7'
               ).order_by(Rekening.kode)
            for row3 in rows1 :
                xml_b = ET.SubElement(xml_greeting, "potongan")
                ET.SubElement(xml_b, "rek_kd").text =row3.kode
                ET.SubElement(xml_b, "rek_nm").text =row3.nama
                ET.SubElement(xml_b, "jumlah").text =unicode(row3.jumlah)

        return self.root

#GIRO
class b203r002Generator(JasperGenerator):
    def __init__(self):
        super(b203r002Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R203002.jrxml')
        self.xpath = '/apbd/spd'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spd')
            ET.SubElement(xml_greeting, "kode").text = row.kode
            ET.SubElement(xml_greeting, "nama").text = row.nama
            ET.SubElement(xml_greeting, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_greeting, "nominal").text = unicode(row.nominal)
            ET.SubElement(xml_greeting, "sp2d_kd").text = row.sp2d_kd
            ET.SubElement(xml_greeting, "spm_nm").text = row.spm_nm
            ET.SubElement(xml_greeting, "ap_bank").text = row.ap_bank
            ET.SubElement(xml_greeting, "ap_rekening").text = row.ap_rekening
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "logo").text = logo
        return self.root
        
# Register SP2D
class b204r0000Generator(JasperGenerator):
    def __init__(self):
        super(b204r0000Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R2040000.jrxml')
        self.xpath = '/apbd/spp'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spp')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_id").text = unicode(row.unit_id)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "jenis").text = unicode(row.jenis)
            ET.SubElement(xml_greeting, "sp2d_kd").text = row.sp2d_kd
            ET.SubElement(xml_greeting, "tgl_sp2d").text = unicode(row.tgl_sp2d)
            ET.SubElement(xml_greeting, "sp2d_nm").text = row.sp2d_nm
            ET.SubElement(xml_greeting, "bud_nip").text = row.bud_nip
            ET.SubElement(xml_greeting, "bud_nama").text = row.bud_nama
            ET.SubElement(xml_greeting, "ap_nama").text = row.ap_nama
            ET.SubElement(xml_greeting, "spp_nm").text = row.spp_nm
            ET.SubElement(xml_greeting, "nominal_gj").text = unicode(row.nominal_gj)
            ET.SubElement(xml_greeting, "nominal").text = unicode(row.nominal)
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "logo").text = logo
            rows = DBSession.query(Pegawai.nama.label('pa_nama'), Pegawai.kode.label('pa_nip')
               ).filter(Pejabat.pegawai_id==Pegawai.id, Pejabat.jabatan_id==Jabatan.id, 
               Pejabat.unit_id==row.unit_id, Jabatan.id==7)
            for row2 in rows :
               ET.SubElement(xml_greeting, "pa_nama").text = row2.pa_nama
               ET.SubElement(xml_greeting, "pa_nip").text = row2.pa_nip
        return self.root

class b204r0001Generator(JasperGenerator):
    def __init__(self):
        super(b204r0001Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R2040001.jrxml')
        self.xpath = '/apbd/spp'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spp')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_id").text = unicode(row.unit_id)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "spp_nm").text = row.spp_nm
            ET.SubElement(xml_greeting, "jenis").text = unicode(row.jenis)
            ET.SubElement(xml_greeting, "ap_nama").text = row.ap_nama
            ET.SubElement(xml_greeting, "sp2d_kd").text = row.sp2d_kd
            ET.SubElement(xml_greeting, "tgl_sp2d").text = unicode(row.tgl_sp2d)
            ET.SubElement(xml_greeting, "sp2d_nm").text = row.sp2d_nm
            ET.SubElement(xml_greeting, "bud_nip").text = row.bud_nip
            ET.SubElement(xml_greeting, "bud_nama").text = row.bud_nama
            ET.SubElement(xml_greeting, "UP").text = unicode(row.UP)
            ET.SubElement(xml_greeting, "GU").text = unicode(row.GU)
            ET.SubElement(xml_greeting, "TU").text = unicode(row.TU)
            ET.SubElement(xml_greeting, "LS_GJ").text = unicode(row.LS_GJ)
            ET.SubElement(xml_greeting, "LS").text = unicode(row.LS)
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "logo").text = logo
            rows = DBSession.query(Pegawai.nama.label('pa_nama'), Pegawai.kode.label('pa_nip')
               ).filter(Pejabat.pegawai_id==Pegawai.id, Pejabat.jabatan_id==Jabatan.id, 
               Pejabat.unit_id==row.unit_id, Jabatan.id==7)
            for row2 in rows :
               ET.SubElement(xml_greeting, "pa_nama").text = row2.pa_nama
               ET.SubElement(xml_greeting, "pa_nip").text = row2.pa_nip
        return self.root

# Register SP2D SKPD
class b204r0002Generator(JasperGenerator):
    def __init__(self):
        super(b204r0002Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R2040002.jrxml')
        self.xpath = '/apbd/spp'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spp')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_id").text = unicode(row.unit_id)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "jenis").text = unicode(row.jenis)
            ET.SubElement(xml_greeting, "sp2d_kd").text = row.sp2d_kd
            ET.SubElement(xml_greeting, "tgl_sp2d").text = unicode(row.tgl_sp2d)
            ET.SubElement(xml_greeting, "sp2d_nm").text = row.sp2d_nm
            ET.SubElement(xml_greeting, "bud_nip").text = row.bud_nip
            ET.SubElement(xml_greeting, "bud_nama").text = row.bud_nama
            ET.SubElement(xml_greeting, "ap_nama").text = row.ap_nama
            ET.SubElement(xml_greeting, "spp_nm").text = row.spp_nm
            ET.SubElement(xml_greeting, "nominal_gj").text = unicode(row.nominal_gj)
            ET.SubElement(xml_greeting, "nominal").text = unicode(row.nominal)
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "logo").text = logo
            rows = DBSession.query(Pegawai.nama.label('pa_nama'), Pegawai.kode.label('pa_nip')
               ).filter(Pejabat.pegawai_id==Pegawai.id, Pejabat.jabatan_id==Jabatan.id, 
               Pejabat.unit_id==row.unit_id, Jabatan.id==7)
            for row2 in rows :
               ET.SubElement(xml_greeting, "pa_nama").text = row2.pa_nama
               ET.SubElement(xml_greeting, "pa_nip").text = row2.pa_nip
        return self.root

# Register SP2D SKPD
class b204r0003Generator(JasperGenerator):
    def __init__(self):
        super(b204r0003Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R2040003.jrxml')
        self.xpath = '/apbd/spp'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spp')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_id").text = unicode(row.unit_id)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "spp_nm").text = row.spp_nm
            ET.SubElement(xml_greeting, "jenis").text = unicode(row.jenis)
            ET.SubElement(xml_greeting, "ap_nama").text = row.ap_nama
            ET.SubElement(xml_greeting, "spm_id").text = unicode(row.spm_id)
            ET.SubElement(xml_greeting, "sp2d_kd").text = row.sp2d_kd
            ET.SubElement(xml_greeting, "tgl_sp2d").text = unicode(row.tgl_sp2d)
            ET.SubElement(xml_greeting, "sp2d_nm").text = row.sp2d_nm
            ET.SubElement(xml_greeting, "bud_nip").text = row.bud_nip
            ET.SubElement(xml_greeting, "bud_nama").text = row.bud_nama
            ET.SubElement(xml_greeting, "nominal").text = unicode(row.nominal)
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "logo").text = logo
            rows = DBSession.query(Pegawai.nama.label('pa_nama'), Pegawai.kode.label('pa_nip')
               ).filter(Pejabat.pegawai_id==Pegawai.id, Pejabat.jabatan_id==Jabatan.id, 
               Pejabat.unit_id==row.unit_id, Jabatan.id==7)
            for row2 in rows :
               ET.SubElement(xml_greeting, "pa_nama").text = row2.pa_nama
               ET.SubElement(xml_greeting, "pa_nip").text = row2.pa_nip
            
            rows1 = DBSession.query(func.coalesce(func.sum(SpmPotongan.nilai),0).label('iwp')
               ).filter(SpmPotongan.ap_spm_id==row.spm_id, Rekening.id==SpmPotongan.rekening_id,
               Rekening.kode=="7.1.1.01.01")
            for row3 in rows1 :
               ET.SubElement(xml_greeting, "iwp").text = unicode(row3.iwp)

            rows2 = DBSession.query(func.coalesce(func.sum(SpmPotongan.nilai),0).label('pph')
               ).filter(SpmPotongan.ap_spm_id==row.spm_id, Rekening.id==SpmPotongan.rekening_id,
               Rekening.kode=="7.1.1.01.03")
            for row4 in rows2 :
               ET.SubElement(xml_greeting, "pph").text = unicode(row4.pph)

            rows3 = DBSession.query(func.coalesce(func.sum(SpmPotongan.nilai),0).label('taperum')
               ).filter(SpmPotongan.ap_spm_id==row.spm_id, Rekening.id==SpmPotongan.rekening_id,
               Rekening.kode=="7.1.1.01.05")
            for row5 in rows3 :
               ET.SubElement(xml_greeting, "taperum").text = unicode(row5.taperum)
               
            rows4 = DBSession.query(func.coalesce(func.sum(SpmPotongan.nilai),0).label('askes')
               ).filter(SpmPotongan.ap_spm_id==row.spm_id, Rekening.id==SpmPotongan.rekening_id,
               Rekening.kode=="7.1.1.01.02")
            for row6 in rows4 :
               ET.SubElement(xml_greeting, "askes").text = unicode(row6.askes)
               
        return self.root

# Register PPN PPH
class b204r0004Generator(JasperGenerator):
    def __init__(self):
        super(b204r0004Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R2040004.jrxml')
        self.xpath = '/apbd/spp'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'spp')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unit_id").text = unicode(row.unit_id)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "jenis").text = unicode(row.jenis)
            ET.SubElement(xml_greeting, "sp2d_kd").text = row.sp2d_kd
            ET.SubElement(xml_greeting, "tgl_sp2d").text = unicode(row.tgl_sp2d)
            ET.SubElement(xml_greeting, "sp2d_nm").text = row.sp2d_nm
            ET.SubElement(xml_greeting, "bud_nip").text = row.bud_nip
            ET.SubElement(xml_greeting, "bud_nama").text = row.bud_nama
            ET.SubElement(xml_greeting, "ap_nama").text = row.ap_nama
            ET.SubElement(xml_greeting, "spp_nm").text = row.spp_nm
            ET.SubElement(xml_greeting, "nominal_gj").text = unicode(row.nominal_gj)
            ET.SubElement(xml_greeting, "nominal").text = unicode(row.nominal)
            ET.SubElement(xml_greeting, "ppn").text = unicode(row.ppn)
            ET.SubElement(xml_greeting, "pph").text = unicode(row.pph)
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "logo").text = logo
            rows = DBSession.query(Pegawai.nama.label('pa_nama'), Pegawai.kode.label('pa_nip')
               ).filter(Pejabat.pegawai_id==Pegawai.id, Pejabat.jabatan_id==Jabatan.id, 
               Pejabat.unit_id==row.unit_id, Jabatan.id==7)
            for row2 in rows :
               ET.SubElement(xml_greeting, "pa_nama").text = row2.pa_nama
               ET.SubElement(xml_greeting, "pa_nip").text = row2.pa_nip
        return self.root

#Realisasi
class b204r100Generator(JasperGenerator):
    def __init__(self):
        super(b204r100Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R204100.jrxml')
        self.xpath = '/apbd/realisasi'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
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
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "logo").text = logo
        return self.root

#Realisasi SKPD Kegiatan
class b204r200Generator(JasperGenerator):
    def __init__(self):
        super(b204r200Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R204200.jrxml')
        self.xpath = '/apbd/realisasi'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
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
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "logo").text = logo
        return self.root

#Realisasi SKPD
class b204r300Generator(JasperGenerator):
    def __init__(self):
        super(b204r300Generator, self).__init__()
        self.reportname = get_rpath('apbd/tuppkd/R204300.jrxml')
        self.xpath = '/apbd/realisasi'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'realisasi')
            #ET.SubElement(xml_greeting, "unit_nm").text = unit_nama
            ET.SubElement(xml_greeting, "bulan").text = unicode(bln)
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_greeting, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_greeting, "jumlah").text = unicode(row.jumlah)
            ET.SubElement(xml_greeting, "realisasi").text = unicode(row.realisasi)
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "logo").text = logo
        return self.root

