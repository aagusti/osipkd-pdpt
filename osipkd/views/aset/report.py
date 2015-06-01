import os
import unittest
import os.path
import uuid

from osipkd.tools import row2dict, xls_reader

from datetime import datetime
#from sqlalchemy import not_, func, case
from sqlalchemy import *
from sqlalchemy.orm import aliased
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from osipkd.models import DBSession
#from osipkd.models.apbd_anggaran import Kegiatan, KegiatanSub, KegiatanItem
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

from pyjasper import (JasperGenerator)
from pyjasper import (JasperGeneratorWithSubreport)
import xml.etree.ElementTree as ET
from pyramid.path import AssetResolver

from osipkd.models.base_model import *
from osipkd.models.pemda_model import *
from osipkd.models.apbd import * 
#from osipkd.models.apbd_anggaran import * 
#from osipkd.models.apbd_tu import *
from osipkd.models.aset_models import *
from datetime import datetime

"""import unittest
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
"""

def get_rpath(filename):
    a = AssetResolver('osipkd')
    resolver = a.resolve(''.join(['reports/',filename]))
    return resolver.abspath()
    
class ViewAsetLap(BaseViews):
    def __init__(self, context, request):
        global customer, thn
        BaseViews.__init__(self, context, request)
        self.app = 'aset'

        #if 'app' in request.params and request.params['app'] == self.app and self.logged:
        #row = DBSession.query(Tahun.status_apbd).filter(Tahun.tahun==self.tahun).first()
        #self.session['status_apbd'] = row and row[0] or 0


        #self.status_apbd =  'status_apbd' in self.session and self.session['status_apbd'] or 0        
        #self.status_apbd_nm =  status_apbd[str(self.status_apbd)]        
        
        self.all_unit =  'all_unit' in self.session and self.session['all_unit'] or 0        
        self.unit_id  = 'unit_id' in self.session and self.session['unit_id'] or 0
        self.unit_kd  = 'unit_kd' in self.session and self.session['unit_kd'] or "X.XX.XX"
        self.unit_nm  = 'unit_nm' in self.session and self.session['unit_nm'] or "Pilih Unit"
        self.keg_id   = 'keg_id' in self.session and self.session['keg_id'] or 0
        
        #self.datas['status_apbd'] = self.status_apbd 
        #self.datas['status_apbd_nm'] = self.status_apbd_nm
        self.datas['all_unit'] = self.all_unit
        self.datas['unit_kd'] = self.unit_kd
        self.datas['unit_nm'] = self.unit_nm
        self.datas['unit_id'] = self.unit_id

        self.cust_nm = 'cust_nm' in self.session and self.session['cust_nm'] or ''
        customer = self.cust_nm
        thn = self.session['tahun']
        
    # REPORT
    @view_config(route_name="aset-lap01", renderer="templates/aset-report/lap01.pt", permission="read")
    def aset_lap01(self):
        params = self.request.params
        return dict(datas=self.datas,)
    
    @view_config(route_name="aset-lap01-act", renderer="json", permission="read")
    def aset_lap01_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        tipe = 'tipe' in params and params['tipe'] and int(params['tipe']) or 0
        mulai = 'mulai' in params and params['mulai'] or 0
        selesai = 'selesai' in params and params['selesai'] or 0

        ### Kategori
        if url_dict['act']=='1' :
            query = DBSession.query(AsetKategori.kode, AsetKategori.uraian, AsetKategori.disabled
                  ).order_by(AsetKategori.kode)
                  
            generator = asetr001Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
           
        ### Kebijakan
        elif url_dict['act']=='2' :
            query = DBSession.query(AsetKebijakan.tahun, AsetKategori.uraian, AsetKebijakan.masa_guna,
                  AsetKebijakan.minimum, AsetKebijakan.disabled
                  ).join(AsetKategori
                  ).order_by(AsetKategori.uraian
                  )
            generator = asetr002Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ### Pemilik
        elif url_dict['act']=='3' :
            query = DBSession.query(AsetPemilik.kode, AsetPemilik.uraian, AsetPemilik.disabled
                  ).order_by(AsetPemilik.kode
                  )
            generator = asetr003Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ### KIB A
        elif url_dict['act']=='kiba' :
            #pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(AsetKategori.uraian.label("katnm"), AsetKategori.kode.label("katkd"), AsetKib.no_register, AsetKib.a_luas_m2, 
                        AsetKib.th_beli, AsetKib.a_alamat, AsetKib.a_hak_tanah, AsetKib.a_sertifikat_tanggal, AsetKib.a_sertifikat_nomor, 
                        AsetKib.a_penggunaan, AsetKib.asal_usul, AsetKib.harga, AsetKib.keterangan,
                        AsetKib.tahun, Unit.kode.label("unitkd"), Unit.nama.label("unitnm"))\
                        .filter(AsetKib.kategori_id==AsetKategori.id, AsetKib.unit_id==Unit.id,\
                                 AsetKib.kib=="A",AsetKib.unit_id==self.session['unit_id'], AsetKib.tahun<=self.session['tahun'])\
                        .order_by(AsetKategori.kode).all()
                        
            generator = asetr004Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ### KIB B
        elif url_dict['act']=='kibb' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(AsetKategori.uraian.label("katnm"), AsetKategori.kode.label("katkd"), AsetKib.no_register, AsetKib.b_merk, 
                    AsetKib.b_type, AsetKib.b_cc, AsetKib.b_bahan, AsetKib.tahun, AsetKib.b_nomor_pabrik, 
                    AsetKib.b_nomor_rangka, AsetKib.b_nomor_mesin, AsetKib.b_nomor_polisi, AsetKib.b_nomor_bpkb, AsetKib.asal_usul, AsetKib.harga, AsetKib.keterangan,
                    AsetKib.tahun, Unit.kode.label("unitkd"), Unit.nama.label("unitnm"))\
                    .filter(AsetKib.kategori_id==AsetKategori.id, AsetKib.unit_id==Unit.id,
                             AsetKib.kib=="B",AsetKib.unit_id==self.session['unit_id'], AsetKib.tahun<=self.session['tahun'])\
                    .order_by(AsetKategori.kode).all()

            generator = asetr005Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ### KIB C
        elif url_dict['act']=='kibc' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(AsetKategori.uraian.label("katnm"), AsetKategori.kode.label("katkd"), AsetKib.no_register, AsetKib.kondisi, 
                        AsetKib.c_bertingkat_tidak, AsetKib.c_beton_tidak, AsetKib.c_luas_lantai, AsetKib.c_lokasi, AsetKib.c_dokumen_tanggal, 
                        AsetKib.c_dokumen_nomor, AsetKib.c_luas_bangunan, AsetKib.c_status_tanah, AsetKib.c_kode_tanah, AsetKib.asal_usul, AsetKib.harga, AsetKib.keterangan,
                        AsetKib.tahun, Unit.kode.label("unitkd"), Unit.nama.label("unitnm"))\
                        .filter(AsetKib.kategori_id==AsetKategori.id, AsetKib.unit_id==Unit.id,
                                 AsetKib.kib=="C",AsetKib.unit_id==self.session['unit_id'], AsetKib.tahun<=self.session['tahun'])\
                        .order_by(AsetKategori.kode).all()

            generator = asetr006Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ### KIB D
        elif url_dict['act']=='kibd' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(AsetKategori.uraian.label("katnm"), AsetKategori.kode.label("katkd"), AsetKib.no_register, AsetKib.d_konstruksi, 
                        AsetKib.d_panjang, AsetKib.d_lebar, AsetKib.d_luas, AsetKib.d_lokasi, AsetKib.d_dokumen_tanggal, 
                        AsetKib.d_dokumen_nomor, AsetKib.d_status_tanah, AsetKib.d_kode_tanah, AsetKib.asal_usul, AsetKib.harga, AsetKib.kondisi, AsetKib.keterangan,
                        AsetKib.tahun, Unit.kode.label("unitkd"), Unit.nama.label("unitnm"))\
                        .filter(AsetKib.kategori_id==AsetKategori.id, AsetKib.unit_id==Unit.id,
                                 AsetKib.kib=="D",AsetKib.unit_id==self.session['unit_id'], AsetKib.tahun<=self.session['tahun'])\
                        .order_by(AsetKategori.kode).all()

            generator = asetr007Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ### KIB E
        elif url_dict['act']=='kibe' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(AsetKategori.uraian.label("katnm"), AsetKategori.kode.label("katkd"), AsetKib.no_register,  
                    AsetKib.e_judul, AsetKib.e_spek, AsetKib.e_asal, AsetKib.e_pencipta, AsetKib.e_bahan, 
                    AsetKib.e_jenis, AsetKib.e_ukuran, AsetKib.jumlah, AsetKib.asal_usul, AsetKib.b_thbuat, AsetKib.harga, AsetKib.keterangan,
                    AsetKib.tahun, Unit.kode.label("unitkd"), Unit.nama.label("unitnm"))\
                    .filter(AsetKib.kategori_id==AsetKategori.id, AsetKib.unit_id==Unit.id,
                             AsetKib.kib=="E",AsetKib.unit_id==self.session['unit_id'], AsetKib.tahun<=self.session['tahun'])\
                    .order_by(AsetKategori.kode).all()
                    
            generator = asetr008Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ### KIB F
        elif url_dict['act']=='kibf' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(AsetKategori.uraian.label("katnm"), AsetKategori.kode.label("katkd"),  
                    AsetKib.kondisi, AsetKib.f_bertingkat_tidak, AsetKib.f_beton_tidak, AsetKib.f_luas_lantai, AsetKib.f_lokasi, 
                    AsetKib.f_dokumen_tanggal, AsetKib.f_dokumen_nomor, AsetKib.tgl_perolehan, AsetKib.f_status_tanah, AsetKib.f_kode_tanah, AsetKib.asal_usul, AsetKib.harga, AsetKib.keterangan,
                    AsetKib.tahun, Unit.kode.label("unitkd"), Unit.nama.label("unitnm"))\
                    .filter(AsetKib.kategori_id==AsetKategori.id, AsetKib.unit_id==Unit.id,
                             AsetKib.kib=="F",AsetKib.unit_id==self.session['unit_id'], AsetKib.tahun<=self.session['tahun'])\
                    .order_by(AsetKategori.kode).all()
                    
            generator = asetr009Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ### Rusak Berat
        elif url_dict['act']=='10' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(ARInvoice.tahun_id.label('tahun'), Unit.nama.label('unit_nm'),
                  ARInvoice.id.label('arinvoice_id'), ARInvoice.kode, ARInvoice.nama.label('arinvoice_nm'), 
                  ARInvoice.tgl_terima, ARInvoice.tgl_validasi, ARInvoice.bendahara_nm, 
                  ARInvoice.penyetor, ARInvoice.alamat, KegiatanSub.nama.label('kegiatan_nm'),
                  func.sum(ARInvoiceItem.nilai).label('nilai')
                  ).filter(ARInvoice.unit_id==Unit.id, ARInvoice.kegiatan_sub_id==KegiatanSub.id,
                  ARInvoiceItem.ar_invoice_id==ARInvoice.id, ARInvoice.unit_id==self.session['unit_id'],
                  ARInvoice.tahun_id==self.session['tahun'], ARInvoice.id==pk_id
                  ).group_by(ARInvoice.tahun_id, Unit.nama,
                  ARInvoice.id, ARInvoice.kode, ARInvoice.nama, 
                  ARInvoice.tgl_terima, ARInvoice.tgl_validasi, ARInvoice.bendahara_nm, 
                  ARInvoice.penyetor, ARInvoice.alamat, KegiatanSub.nama
                  )
            generator = b102r002Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
            
        ### Buku Inventaris
        elif url_dict['act']=='11' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), AsetKategori.kode.label('kat_kd'),
                  AsetKategori.uraian.label('kat_nm'), AsetKib.no_register, AsetKib.b_merk, AsetKib.b_type, AsetKib.a_sertifikat_nomor,
                  AsetKib.b_nomor_pabrik, AsetKib.b_nomor_rangka, AsetKib.b_nomor_mesin, AsetKib.b_bahan, AsetKib.asal_usul, AsetKib.th_beli,
                  AsetKib.e_ukuran, AsetKib.d_konstruksi, AsetKib.satuan, AsetKib.kondisi, AsetKib.jumlah, AsetKib.harga, AsetKib.keterangan
                  ).filter(AsetKib.unit_id==Unit.id, AsetKib.kategori_id==AsetKategori.id, 
                  AsetKib.unit_id==self.session['unit_id'], AsetKib.tahun<=self.session['tahun'], 
                  or_(AsetKib.tgl_perolehan==None,extract('year',AsetKib.tgl_perolehan)==self.session['tahun'])
                  ).order_by(Unit.kode, AsetKategori.kode, AsetKib.no_register)
                  

            generator = asetr011Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
 
        ### Penghapusan
        elif url_dict['act']=='12' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), AsetKategori.kode.label('kat_kd'),
                  AsetKategori.uraian.label('kat_nm'), AsetKib.no_register, AsetKib.b_merk, AsetKib.b_type, AsetKib.a_sertifikat_nomor,
                  AsetKib.b_nomor_pabrik, AsetKib.b_nomor_rangka, AsetKib.b_nomor_mesin, AsetKib.b_bahan, AsetKib.asal_usul, AsetKib.th_beli,
                  AsetKib.e_ukuran, AsetKib.d_konstruksi, AsetKib.satuan, AsetKib.kondisi, AsetKib.jumlah, AsetKib.harga, AsetKib.keterangan
                  ).filter(AsetKib.unit_id==Unit.id, AsetKib.kategori_id==AsetKategori.id, 
                  AsetDelItem.kib_id==AsetKib.id, AsetDel.id==AsetDelItem.delete_id,
                  AsetKib.unit_id==self.session['unit_id'], 
                  extract('year',AsetDel.tanggal)==self.session['tahun']
                  ).order_by(Unit.kode, AsetKategori.kode, AsetKib.no_register)
                  
            generator = asetr012Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
 
        ### Neraca
        elif url_dict['act']=='13' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            kategori_alias = aliased(AsetKategori)
            
            query1 = DBSession.query(kategori_alias.kode.label('kode'), kategori_alias.uraian.label('uraian'), 
                  Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), 
                  func.sum(AsetKib.harga*AsetKib.jumlah).label('nilai'), 
                  literal_column('1').label('detil')
                  ).outerjoin(AsetKebijakan
                  ).filter(AsetKategori.id==AsetKebijakan.kategori_id, AsetKebijakan==self.session['tahun'],
                  AsetKib.unit_id==Unit.id, AsetKib.kategori_id==kategori_alias.id,
                  func.substr(AsetKategori.kode,1,5)==kategori_alias.kode,
                  kategori_alias.level_id==1, 
                  AsetKib.harga>func.coalesce(AsetKebijakan.minimum,0),
                  AsetKib.tahun<=self.session['tahun'],
                  AsetKib.unit_id==self.session['unit_id'],
                  or_(AsetDel is None, extract('year',AsetDel.tanggal)>self.session['tahun'])
                  ).group_by(kategori_alias.kode, kategori_alias.uraian, Unit.kode, Unit.nama)

            query2 = DBSession.query(kategori_alias.kode.label('kode'), kategori_alias.uraian.label('uraian'), 
                  Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), 
                  func.sum(AsetKib.harga*AsetKib.jumlah).label('nilai'), 
                  literal_column('1').label('detil')
                  ).outerjoin(AsetKebijakan
                  ).filter(AsetKategori.id==AsetKebijakan.kategori_id, AsetKebijakan==self.session['tahun'],
                  AsetKib.unit_id==Unit.id, AsetKib.kategori_id==kategori_alias.id,
                  func.substr(AsetKategori.kode,1,2)==kategori_alias.kode,
                  kategori_alias.level_id==1, 
                  AsetKib.harga>func.coalesce(AsetKebijakan.minimum,0),
                  AsetKib.tahun<=self.session['tahun'],
                  AsetKib.unit_id==self.session['unit_id'],
                  or_(AsetDel is None, extract('year',AsetDel.tanggal)>self.session['tahun'])
                  ).group_by(kategori_alias.kode, kategori_alias.uraian, Unit.kode, Unit.nama)
                  
            """query1 = DBSession.query(kategori_alias.kode.label('kode'), kategori_alias.uraian.label('uraian'), 
                  Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), AsetKib.unit_id.label('unit_id'),
                  func.sum(AsetKib.harga*AsetKib.jumlah).label('nilai'), 
                  literal_column('1').label('detil')
                  ).outerjoin(AsetDelItem, AsetKib.id==AsetDelItem.kib_id
                  ).outerjoin(AsetDel, AsetDel.id==AsetDelItem.delete_id
                  ).outerjoin(AsetKebijakan, and_(AsetKategori.id==AsetKebijakan.kategori_id, AsetKebijakan==self.session['tahun'])
                  ).filter(AsetKib.unit_id==Unit.id, AsetKib.kategori_id==kategori_alias.id,
                  func.substr(AsetKategori.kode,1,5)==kategori_alias.kode,
                  kategori_alias.level_id==1, 
                  AsetKib.harga>func.coalesce(AsetKebijakan.minimum,0),
                  AsetKib.tahun<=self.session['tahun'],
                  or_(AsetDel==None,extract('year',AsetDel.tanggal)>self.session['tahun'])
                  ).group_by(kategori_alias.kode, kategori_alias.uraian, AsetKib.unit_id, Unit.kode, Unit.nama)
                  
            query2 = DBSession.query(kategori_alias.kode.label('kode'), kategori_alias.uraian.label('uraian'), 
                  Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                  func.sum(AsetKib.harga*AsetKib.jumlah).label('nilai'), AsetKib.unit_id.label('unit_id'), 
                  literal_column('0').label('detil')
                  ).outerjoin(AsetDelItem, AsetKib.id==AsetDelItem.kib_id
                  ).outerjoin(AsetDel, AsetDel.id==AsetDelItem.delete_id
                  ).outerjoin(AsetKebijakan, and_(AsetKategori.id==AsetKebijakan.kategori_id, AsetKebijakan==self.session['tahun'])
                  ).filter(AsetKib.unit_id==Unit.id, AsetKib.kategori_id==kategori_alias.id,
                  func.substr(AsetKategori.kode,1,2)==kategori_alias.kode,
                  AsetKib.harga>func.coalesce(AsetKebijakan.minimum,0),
                  AsetKib.tahun<=self.session['tahun'],
                  or_(AsetDel==None,extract('year',AsetDel.tanggal)>self.session['tahun'])
                  ).group_by(kategori_alias.kode, kategori_alias.uraian, AsetKib.unit_id, Unit.kode, Unit.nama)
            """
            subq = query1.union(query2).subquery()
            
            query = DBSession.query(subq.c.kode, subq.c.uraian, subq.c.unit_kd, subq.c.unit_nm, subq.c.nilai, subq.c.detil
                  ).order_by(subq.c.kode, subq.c.uraian)
            
            generator = asetr013Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
            
 
    # REPORT PPKD
    @view_config(route_name="aset-lap02", renderer="templates/aset-report/lap02.pt", permission="read")
    def aset_lap02(self):
        params = self.request.params
        return dict(datas=self.datas,)

    @view_config(route_name="aset-lap02-act", renderer="json", permission="read")
    def aset_lap02_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        tipe = 'tipe' in params and params['tipe'] and int(params['tipe']) or 0
        mulai = 'mulai' in params and params['mulai'] or 0
        selesai = 'selesai' in params and params['selesai'] or 0

        ### KIB A // PPKD
        if url_dict['act']=='kiba' :
            #pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(AsetKategori.uraian.label("katnm"), AsetKategori.kode.label("katkd"), AsetKib.no_register, AsetKib.a_luas_m2, 
                        AsetKib.th_beli, AsetKib.a_alamat, AsetKib.a_hak_tanah, AsetKib.a_sertifikat_tanggal, AsetKib.a_sertifikat_nomor, 
                        AsetKib.a_penggunaan, AsetKib.asal_usul, AsetKib.harga, AsetKib.keterangan,
                        AsetKib.tahun, Unit.kode.label("unitkd"), Unit.nama.label("unitnm"))\
                        .filter(AsetKib.kategori_id==AsetKategori.id, AsetKib.unit_id==Unit.id,\
                                 AsetKib.kib=="A", AsetKib.tahun<=self.session['tahun'])\
                        .order_by(AsetKategori.kode).all()
                        
            generator = asetr104Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ### KIB B
        elif url_dict['act']=='kibb' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(AsetKategori.uraian.label("katnm"), AsetKategori.kode.label("katkd"), AsetKib.no_register, AsetKib.b_merk, 
                    AsetKib.b_type, AsetKib.b_cc, AsetKib.b_bahan, AsetKib.tahun, AsetKib.b_nomor_pabrik, 
                    AsetKib.b_nomor_rangka, AsetKib.b_nomor_mesin, AsetKib.b_nomor_polisi, AsetKib.b_nomor_bpkb, AsetKib.asal_usul, AsetKib.harga, AsetKib.keterangan,
                    AsetKib.tahun, Unit.kode.label("unitkd"), Unit.nama.label("unitnm"))\
                    .filter(AsetKib.kategori_id==AsetKategori.id, AsetKib.unit_id==Unit.id,
                             AsetKib.kib=="B", AsetKib.tahun<=self.session['tahun'])\
                    .order_by(AsetKategori.kode).all()

            generator = asetr105Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ### KIB C
        elif url_dict['act']=='kibc' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(AsetKategori.uraian.label("katnm"), AsetKategori.kode.label("katkd"), AsetKib.no_register, AsetKib.kondisi, 
                        AsetKib.c_bertingkat_tidak, AsetKib.c_beton_tidak, AsetKib.c_luas_lantai, AsetKib.c_lokasi, AsetKib.c_dokumen_tanggal, 
                        AsetKib.c_dokumen_nomor, AsetKib.c_luas_bangunan, AsetKib.c_status_tanah, AsetKib.c_kode_tanah, AsetKib.asal_usul, AsetKib.harga, AsetKib.keterangan,
                        AsetKib.tahun, Unit.kode.label("unitkd"), Unit.nama.label("unitnm"))\
                        .filter(AsetKib.kategori_id==AsetKategori.id, AsetKib.unit_id==Unit.id,
                                 AsetKib.kib=="C", AsetKib.tahun<=self.session['tahun'])\
                        .order_by(AsetKategori.kode).all()

            generator = asetr106Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ### KIB D
        elif url_dict['act']=='kibd' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(AsetKategori.uraian.label("katnm"), AsetKategori.kode.label("katkd"), AsetKib.no_register, AsetKib.d_konstruksi, 
                        AsetKib.d_panjang, AsetKib.d_lebar, AsetKib.d_luas, AsetKib.d_lokasi, AsetKib.d_dokumen_tanggal, 
                        AsetKib.d_dokumen_nomor, AsetKib.d_status_tanah, AsetKib.d_kode_tanah, AsetKib.asal_usul, AsetKib.harga, AsetKib.kondisi, AsetKib.keterangan,
                        AsetKib.tahun, Unit.kode.label("unitkd"), Unit.nama.label("unitnm"))\
                        .filter(AsetKib.kategori_id==AsetKategori.id, AsetKib.unit_id==Unit.id,
                                 AsetKib.kib=="D", AsetKib.tahun<=self.session['tahun'])\
                        .order_by(AsetKategori.kode).all()

            generator = asetr107Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ### KIB E
        elif url_dict['act']=='kibe' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(AsetKategori.uraian.label("katnm"), AsetKategori.kode.label("katkd"), AsetKib.no_register,  
                    AsetKib.e_judul, AsetKib.e_spek, AsetKib.e_asal, AsetKib.e_pencipta, AsetKib.e_bahan, 
                    AsetKib.e_jenis, AsetKib.e_ukuran, AsetKib.jumlah, AsetKib.asal_usul, AsetKib.b_thbuat, AsetKib.harga, AsetKib.keterangan,
                    AsetKib.tahun, Unit.kode.label("unitkd"), Unit.nama.label("unitnm"))\
                    .filter(AsetKib.kategori_id==AsetKategori.id, AsetKib.unit_id==Unit.id,
                             AsetKib.kib=="E", AsetKib.tahun<=self.session['tahun'])\
                    .order_by(AsetKategori.kode).all()
                    
            generator = asetr108Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ### KIB F
        elif url_dict['act']=='kibf' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(AsetKategori.uraian.label("katnm"), AsetKategori.kode.label("katkd"),  
                    AsetKib.kondisi, AsetKib.f_bertingkat_tidak, AsetKib.f_beton_tidak, AsetKib.f_luas_lantai, AsetKib.f_lokasi, 
                    AsetKib.f_dokumen_tanggal, AsetKib.f_dokumen_nomor, AsetKib.tgl_perolehan, AsetKib.f_status_tanah, AsetKib.f_kode_tanah, AsetKib.asal_usul, AsetKib.harga, AsetKib.keterangan,
                    AsetKib.tahun, Unit.kode.label("unitkd"), Unit.nama.label("unitnm"))\
                    .filter(AsetKib.kategori_id==AsetKategori.id, AsetKib.unit_id==Unit.id,
                             AsetKib.kib=="F", AsetKib.tahun<=self.session['tahun'])\
                    .order_by(AsetKategori.kode).all()
                    
            generator = asetr109Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ### Buku Inventaris
        elif url_dict['act']=='11' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), AsetKategori.kode.label('kat_kd'),
                  AsetKategori.uraian.label('kat_nm'), AsetKib.no_register, AsetKib.b_merk, AsetKib.b_type, AsetKib.a_sertifikat_nomor,
                  AsetKib.b_nomor_pabrik, AsetKib.b_nomor_rangka, AsetKib.b_nomor_mesin, AsetKib.b_bahan, AsetKib.asal_usul, AsetKib.th_beli,
                  AsetKib.e_ukuran, AsetKib.d_konstruksi, AsetKib.satuan, AsetKib.kondisi, AsetKib.jumlah, AsetKib.harga, AsetKib.keterangan
                  ).filter(AsetKib.unit_id==Unit.id, AsetKib.kategori_id==AsetKategori.id, 
                  AsetKib.tahun<=self.session['tahun'], 
                  or_(AsetKib.tgl_perolehan==None,extract('year',AsetKib.tgl_perolehan)==self.session['tahun'])
                  ).order_by(Unit.kode, AsetKategori.kode, AsetKib.no_register)
                  

            generator = asetr111Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
 
        ### Penghapusan
        elif url_dict['act']=='12' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), AsetKategori.kode.label('kat_kd'),
                  AsetKategori.uraian.label('kat_nm'), AsetKib.no_register, AsetKib.b_merk, AsetKib.b_type, AsetKib.a_sertifikat_nomor,
                  AsetKib.b_nomor_pabrik, AsetKib.b_nomor_rangka, AsetKib.b_nomor_mesin, AsetKib.b_bahan, AsetKib.asal_usul, AsetKib.th_beli,
                  AsetKib.e_ukuran, AsetKib.d_konstruksi, AsetKib.satuan, AsetKib.kondisi, AsetKib.jumlah, AsetKib.harga, AsetKib.keterangan
                  ).filter(AsetKib.unit_id==Unit.id, AsetKib.kategori_id==AsetKategori.id, 
                  AsetDelItem.kib_id==AsetKib.id, AsetDel.id==AsetDelItem.delete_id,
                  extract('year',AsetDel.tanggal)==self.session['tahun']
                  ).order_by(Unit.kode, AsetKategori.kode, AsetKib.no_register)
                  
            generator = asetr112Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
 
       ### Neraca
        elif url_dict['act']=='13' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            kategori_alias = aliased(AsetKategori)
            
            query1 = DBSession.query(kategori_alias.kode.label('kode'), kategori_alias.uraian.label('uraian'), 
                  func.sum(AsetKib.harga*AsetKib.jumlah).label('nilai'), 
                  literal_column('1').label('detil')
                  ).outerjoin(AsetKebijakan
                  ).filter(AsetKategori.id==AsetKebijakan.kategori_id, AsetKebijakan==self.session['tahun'],
                  AsetKib.kategori_id==kategori_alias.id,
                  func.substr(AsetKategori.kode,1,5)==kategori_alias.kode,
                  kategori_alias.level_id==1, 
                  AsetKib.harga>func.coalesce(AsetKebijakan.minimum,0),
                  AsetKib.tahun<=self.session['tahun'],
                  or_(AsetDel is None, extract('year',AsetDel.tanggal)>self.session['tahun'])
                  ).group_by(kategori_alias.kode, kategori_alias.uraian)

            query2 = DBSession.query(kategori_alias.kode.label('kode'), kategori_alias.uraian.label('uraian'), 
                  func.sum(AsetKib.harga*AsetKib.jumlah).label('nilai'), 
                  literal_column('1').label('detil')
                  ).outerjoin(AsetKebijakan
                  ).filter(AsetKategori.id==AsetKebijakan.kategori_id, AsetKebijakan==self.session['tahun'],
                  AsetKib.kategori_id==kategori_alias.id,
                  func.substr(AsetKategori.kode,1,2)==kategori_alias.kode,
                  kategori_alias.level_id==1, 
                  AsetKib.harga>func.coalesce(AsetKebijakan.minimum,0),
                  AsetKib.tahun<=self.session['tahun'],
                  or_(AsetDel is None, extract('year',AsetDel.tanggal)>self.session['tahun'])
                  ).group_by(kategori_alias.kode, kategori_alias.uraian)

            subq = query1.union(query2).subquery()
            
            query = DBSession.query(subq.c.kode, subq.c.uraian, subq.c.nilai, subq.c.detil
                  ).order_by(subq.c.kode, subq.c.uraian)
            
            generator = asetr113Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
            
    # ASET SKPD
    """@view_config(route_name="aset-report-skpd", renderer="templates/aset-report/pendapatan.pt", permission="read")
    def aset_report_skpd(self):
        params = self.request.params
        return dict(datas=self.datas,)

    @view_config(route_name="aset-report-skpd-act", renderer="json", permission="read")
    def aset_report_skpd_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        tipe = 'tipe' in params and params['tipe'] and int(params['tipe']) or 0
        mulai = 'mulai' in params and params['mulai'] or 0
        selesai = 'selesai' in params and params['selesai'] or 0
        
        ### Aset SKPD 1
        if url_dict['act']=='1' :
            print XXXXXXXX
           
        ### Aset SKPD 2
        elif url_dict['act']=='2' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(ARInvoice.tahun_id.label('tahun'), Unit.nama.label('unit_nm'),
                  ARInvoice.id.label('arinvoice_id'), ARInvoice.kode, ARInvoice.nama.label('arinvoice_nm'), 
                  ARInvoice.tgl_terima, ARInvoice.tgl_validasi, ARInvoice.bendahara_nm, 
                  ARInvoice.penyetor, ARInvoice.alamat, KegiatanSub.nama.label('kegiatan_nm'),
                  func.sum(ARInvoiceItem.nilai).label('nilai')
                  ).filter(ARInvoice.unit_id==Unit.id, ARInvoice.kegiatan_sub_id==KegiatanSub.id,
                  ARInvoiceItem.ar_invoice_id==ARInvoice.id, ARInvoice.unit_id==self.session['unit_id'],
                  ARInvoice.tahun_id==self.session['tahun'], ARInvoice.id==pk_id
                  ).group_by(ARInvoice.tahun_id, Unit.nama,
                  ARInvoice.id, ARInvoice.kode, ARInvoice.nama, 
                  ARInvoice.tgl_terima, ARInvoice.tgl_validasi, ARInvoice.bendahara_nm, 
                  ARInvoice.penyetor, ARInvoice.alamat, KegiatanSub.nama
                  )
            generator = b102r002Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

    # ASET PPKD
    @view_config(route_name="aset-report-ppkd", renderer="templates/aset-report/pendapatan.pt", permission="read")
    def aset_report_ppkd(self):
        params = self.request.params
        return dict(datas=self.datas,)

    @view_config(route_name="aset-report-ppkd-act", renderer="json", permission="read")
    def aset_report_ppkd_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        tipe = 'tipe' in params and params['tipe'] and int(params['tipe']) or 0
        mulai = 'mulai' in params and params['mulai'] or 0
        selesai = 'selesai' in params and params['selesai'] or 0
        
        ### Aset PPKD 1
        if url_dict['act']=='1' :
            print XXXXXXXX
           
        ### Aset PPKD 2
        elif url_dict['act']=='2' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(ARInvoice.tahun_id.label('tahun'), Unit.nama.label('unit_nm'),
                  ARInvoice.id.label('arinvoice_id'), ARInvoice.kode, ARInvoice.nama.label('arinvoice_nm'), 
                  ARInvoice.tgl_terima, ARInvoice.tgl_validasi, ARInvoice.bendahara_nm, 
                  ARInvoice.penyetor, ARInvoice.alamat, KegiatanSub.nama.label('kegiatan_nm'),
                  func.sum(ARInvoiceItem.nilai).label('nilai')
                  ).filter(ARInvoice.unit_id==Unit.id, ARInvoice.kegiatan_sub_id==KegiatanSub.id,
                  ARInvoiceItem.ar_invoice_id==ARInvoice.id, ARInvoice.unit_id==self.session['unit_id'],
                  ARInvoice.tahun_id==self.session['tahun'], ARInvoice.id==pk_id
                  ).group_by(ARInvoice.tahun_id, Unit.nama,
                  ARInvoice.id, ARInvoice.kode, ARInvoice.nama, 
                  ARInvoice.tgl_terima, ARInvoice.tgl_validasi, ARInvoice.bendahara_nm, 
                  ARInvoice.penyetor, ARInvoice.alamat, KegiatanSub.nama
                  )
            generator = b102r002Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

    # ANALISA
    @view_config(route_name="aset-report-analisa", renderer="templates/aset-report/pendapatan.pt", permission="read")
    def aset_report_analisa(self):
        params = self.request.params
        return dict(datas=self.datas,)

    @view_config(route_name="aset-report-analisa-act", renderer="json", permission="read")
    def aset_report_analisa_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        tipe = 'tipe' in params and params['tipe'] and int(params['tipe']) or 0
        mulai = 'mulai' in params and params['mulai'] or 0
        selesai = 'selesai' in params and params['selesai'] or 0
        
        ### Analisa 1
        if url_dict['act']=='1' :
            print XXXXXXXX
           
        ### Analisa 2
        elif url_dict['act']=='2' :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            query = DBSession.query(ARInvoice.tahun_id.label('tahun'), Unit.nama.label('unit_nm'),
                  ARInvoice.id.label('arinvoice_id'), ARInvoice.kode, ARInvoice.nama.label('arinvoice_nm'), 
                  ARInvoice.tgl_terima, ARInvoice.tgl_validasi, ARInvoice.bendahara_nm, 
                  ARInvoice.penyetor, ARInvoice.alamat, KegiatanSub.nama.label('kegiatan_nm'),
                  func.sum(ARInvoiceItem.nilai).label('nilai')
                  ).filter(ARInvoice.unit_id==Unit.id, ARInvoice.kegiatan_sub_id==KegiatanSub.id,
                  ARInvoiceItem.ar_invoice_id==ARInvoice.id, ARInvoice.unit_id==self.session['unit_id'],
                  ARInvoice.tahun_id==self.session['tahun'], ARInvoice.id==pk_id
                  ).group_by(ARInvoice.tahun_id, Unit.nama,
                  ARInvoice.id, ARInvoice.kode, ARInvoice.nama, 
                  ARInvoice.tgl_terima, ARInvoice.tgl_validasi, ARInvoice.bendahara_nm, 
                  ARInvoice.penyetor, ARInvoice.alamat, KegiatanSub.nama
                  )
            generator = b102r002Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
    """
    
#Kategori
class asetr001Generator(JasperGenerator):
    def __init__(self):
        super(asetr001Generator, self).__init__()
        self.reportname = get_rpath('aset/R0001.jrxml')
        self.xpath = '/aset/kategori'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kategori')
            ET.SubElement(xml_greeting, "kode").text = row.kode
            ET.SubElement(xml_greeting, "uraian").text = row.uraian
            ET.SubElement(xml_greeting, "disabled").text = unicode(row.disabled)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root
       
#Kebijakan
class asetr002Generator(JasperGenerator):
    def __init__(self):
        super(asetr002Generator, self).__init__()
        self.reportname = get_rpath('aset/R0002.jrxml')
        self.xpath = '/aset/kebijakan'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kebijakan')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "uraian").text = row.uraian
            ET.SubElement(xml_greeting, "minimum").text = unicode(row.minimum)
            ET.SubElement(xml_greeting, "masa_guna").text = unicode(row.masa_guna)
            ET.SubElement(xml_greeting, "disabled").text = unicode(row.disabled)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root
       
#Pemilik
class asetr003Generator(JasperGenerator):
    def __init__(self):
        super(asetr003Generator, self).__init__()
        self.reportname = get_rpath('aset/R0003.jrxml')
        self.xpath = '/aset/pemilik'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'pemilik')
            ET.SubElement(xml_greeting, "kode").text = row.kode
            ET.SubElement(xml_greeting, "uraian").text = row.uraian
            ET.SubElement(xml_greeting, "disabled").text = unicode(row.disabled)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

#KIB A
class asetr004Generator(JasperGenerator):
    def __init__(self):
        super(asetr004Generator, self).__init__()
        self.reportname = get_rpath('aset/R0004.jrxml')
        self.xpath = '/aset/kib'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kib')
            ET.SubElement(xml_greeting, "katnm").text = row.katnm
            ET.SubElement(xml_greeting, "katkd").text = row.katkd
            ET.SubElement(xml_greeting, "no_register").text = unicode(row.no_register)
            ET.SubElement(xml_greeting, "a_luas_m2").text = unicode(row.a_luas_m2)
            ET.SubElement(xml_greeting, "th_beli").text = unicode(row.th_beli)
            ET.SubElement(xml_greeting, "a_alamat").text = row.a_alamat
            ET.SubElement(xml_greeting, "a_hak_tanah").text = row.a_hak_tanah
            ET.SubElement(xml_greeting, "a_sertifikat_tgl").text = unicode(row.a_sertifikat_tanggal)
            ET.SubElement(xml_greeting, "a_sertifikat_no").text = row.a_sertifikat_nomor
            ET.SubElement(xml_greeting, "a_penggunaan").text = row.a_penggunaan
            ET.SubElement(xml_greeting, "asal_usul").text = row.asal_usul
            ET.SubElement(xml_greeting, "harga").text = unicode(row.harga)
            ET.SubElement(xml_greeting, "keterangan").text = row.keterangan
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unitkd").text = row.unitkd
            ET.SubElement(xml_greeting, "unitnm").text = row.unitnm
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root
        
#KIB B
class asetr005Generator(JasperGenerator):
    def __init__(self):
        super(asetr005Generator, self).__init__()
        self.reportname = get_rpath('aset/R0005.jrxml')
        self.xpath = '/aset/kib'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kib')
            ET.SubElement(xml_greeting, "katnm").text = row.katnm
            ET.SubElement(xml_greeting, "katkd").text = row.katkd
            ET.SubElement(xml_greeting, "no_register").text = unicode(row.no_register)
            ET.SubElement(xml_greeting, "b_merk").text = row.b_merk
            ET.SubElement(xml_greeting, "b_type").text = row.b_type
            ET.SubElement(xml_greeting, "b_cc").text = row.b_cc
            ET.SubElement(xml_greeting, "b_bahan").text = row.b_bahan
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "b_nomor_pabrik").text = row.b_nomor_pabrik
            ET.SubElement(xml_greeting, "b_nomor_rangka").text = row.b_nomor_rangka
            ET.SubElement(xml_greeting, "b_nomor_mesin").text = row.b_nomor_mesin
            ET.SubElement(xml_greeting, "b_nomor_polisi").text = row.b_nomor_polisi
            ET.SubElement(xml_greeting, "b_nomor_bpkb").text = row.b_nomor_bpkb
            ET.SubElement(xml_greeting, "asal_usul").text = row.asal_usul
            ET.SubElement(xml_greeting, "harga").text = row.harga
            ET.SubElement(xml_greeting, "keterangan").text = row.keterangan
            ET.SubElement(xml_greeting, "tahun").text = row.tahun
            ET.SubElement(xml_greeting, "unitkd").text = row.unitkd
            ET.SubElement(xml_greeting, "unitnm").text = row.unitnm
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

#KIB C
class asetr006Generator(JasperGenerator):
    def __init__(self):
        super(asetr006Generator, self).__init__()
        self.reportname = get_rpath('aset/R0006.jrxml')
        self.xpath = '/aset/kib'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kib')
            ET.SubElement(xml_greeting, "katnm").text = row.katnm
            ET.SubElement(xml_greeting, "katkd").text = row.katkd
            ET.SubElement(xml_greeting, "no_register").text = unicode(row.no_register)
            ET.SubElement(xml_greeting, "kondisi").text = row.kondisi
            ET.SubElement(xml_greeting, "c_bertingkat_tidak").text = row.c_bertingkat_tidak
            ET.SubElement(xml_greeting, "c_beton_tidak").text = row.c_beton_tidak
            ET.SubElement(xml_greeting, "c_luas_lantai").text = row.c_luas_lantai
            ET.SubElement(xml_greeting, "c_lokasi").text = row.c_lokasi
            ET.SubElement(xml_greeting, "c_dokumen_tanggal").text = unicode(row.c_dokumen_tanggal)
            ET.SubElement(xml_greeting, "c_dokumen_nomor").text = row.c_dokumen_nomor
            ET.SubElement(xml_greeting, "c_luas_bangunan").text =  unicode(row.c_luas_bangunan)
            ET.SubElement(xml_greeting, "c_status_tanah").text = row.c_status_tanah
            ET.SubElement(xml_greeting, "c_kode_tanah").text = unicode(row.c_kode_tanah)
            ET.SubElement(xml_greeting, "asal_usul").text = row.asal_usul
            ET.SubElement(xml_greeting, "harga").text = unicode(row.harga)
            ET.SubElement(xml_greeting, "keterangan").text = row.keterangan
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unitkd").text = row.unitkd
            ET.SubElement(xml_greeting, "unitnm").text = row.unitnm
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

#KIB D
class asetr007Generator(JasperGenerator):
    def __init__(self):
        super(asetr007Generator, self).__init__()
        self.reportname = get_rpath('aset/R0007.jrxml')
        self.xpath = '/aset/kib'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kib')
            ET.SubElement(xml_greeting, "katnm").text = row.katnm
            ET.SubElement(xml_greeting, "katkd").text = row.katkd
            ET.SubElement(xml_greeting, "no_register").text = unicode(row.no_register)
            ET.SubElement(xml_greeting, "d_konstruksi").text = row.d_konstruksi
            ET.SubElement(xml_greeting, "d_panjang").text = unicode(row.d_panjang)
            ET.SubElement(xml_greeting, "d_lebar").text = unicode(row.d_lebar)
            ET.SubElement(xml_greeting, "d_luas").text = unicode(row.d_luas)
            ET.SubElement(xml_greeting, "d_lokasi").text = row.d_lokasi
            ET.SubElement(xml_greeting, "d_dokumen_tanggal").text = unicode(row.d_dokumen_tanggal)
            ET.SubElement(xml_greeting, "d_dokumen_nomor").text = row.d_dokumen_nomor
            ET.SubElement(xml_greeting, "d_status_tanah").text = row.d_status_tanah
            ET.SubElement(xml_greeting, "d_kode_tanah").text = unicode(row.d_kode_tanah)
            ET.SubElement(xml_greeting, "asal_usul").text = row.asal_usul
            ET.SubElement(xml_greeting, "harga").text = unicode(row.harga)
            ET.SubElement(xml_greeting, "kondisi").text = row.kondisi
            ET.SubElement(xml_greeting, "keterangan").text = row.keterangan
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unitkd").text = row.unitkd
            ET.SubElement(xml_greeting, "unitnm").text = row.unitnm
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

#KIB E
class asetr008Generator(JasperGenerator):
    def __init__(self):
        super(asetr008Generator, self).__init__()
        self.reportname = get_rpath('aset/R0008.jrxml')
        self.xpath = '/aset/kib'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kib')
            ET.SubElement(xml_greeting, "katnm").text = row.katnm
            ET.SubElement(xml_greeting, "katkd").text = row.katkd
            ET.SubElement(xml_greeting, "no_register").text = unicode(row.no_register)
            ET.SubElement(xml_greeting, "e_judul").text = row.e_judul
            ET.SubElement(xml_greeting, "e_spek").text = row.e_spek
            ET.SubElement(xml_greeting, "e_asal").text = row.e_asal
            ET.SubElement(xml_greeting, "e_pencipta").text = row.e_pencipta
            ET.SubElement(xml_greeting, "e_bahan").text = row.e_bahan
            ET.SubElement(xml_greeting, "e_jenis").text = row.e_jenis
            ET.SubElement(xml_greeting, "e_ukuran").text = unicode(row.e_ukuran)
            ET.SubElement(xml_greeting, "jumlah").text = unicode(row.jumlah)
            ET.SubElement(xml_greeting, "asal_usul").text = row.asal_usul
            ET.SubElement(xml_greeting, "b_thbuat").text = row.b_thbuat
            ET.SubElement(xml_greeting, "harga").text = unicode(row.harga)
            ET.SubElement(xml_greeting, "keterangan").text = row.keterangan
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unitkd").text = row.unitkd
            ET.SubElement(xml_greeting, "unitnm").text = row.unitnm
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

#KIB F
class asetr009Generator(JasperGenerator):
    def __init__(self):
        super(asetr009Generator, self).__init__()
        self.reportname = get_rpath('aset/R0009.jrxml')
        self.xpath = '/aset/kib'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kib')
            ET.SubElement(xml_greeting, "katnm").text = row.katnm
            ET.SubElement(xml_greeting, "katkd").text = row.katkd
            ET.SubElement(xml_greeting, "kondisi").text = row.kondisi
            ET.SubElement(xml_greeting, "f_bertingkat_tidak").text = row.f_bertingkat_tidak
            ET.SubElement(xml_greeting, "f_beton_tidak").text = row.f_beton_tidak
            ET.SubElement(xml_greeting, "f_luas_lantai").text = unicode(row.f_luas_lantai)
            ET.SubElement(xml_greeting, "f_lokasi").text = row.f_lokasi
            ET.SubElement(xml_greeting, "f_dokumen_tanggal").text = unicode(row.f_dokumen_tanggal)
            ET.SubElement(xml_greeting, "f_dokumen_nomor").text = row.f_dokumen_nomor
            ET.SubElement(xml_greeting, "tgl_perolehan").text = unicode(row.tgl_perolehan)
            ET.SubElement(xml_greeting, "f_status_tanah").text = row.f_status_tanah
            ET.SubElement(xml_greeting, "f_kode_tanah").text = unicode(row.f_kode_tanah)
            ET.SubElement(xml_greeting, "asal_usul").text = row.asal_usul
            ET.SubElement(xml_greeting, "harga").text = unicode(row.harga)
            ET.SubElement(xml_greeting, "keterangan").text = row.keterangan
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unitkd").text = row.unitkd
            ET.SubElement(xml_greeting, "unitnm").text = row.unitnm
        return self.root

#Inventaris
class asetr011Generator(JasperGenerator):
    def __init__(self):
        super(asetr011Generator, self).__init__()
        self.reportname = get_rpath('aset/R0011.jrxml')
        self.xpath = '/aset/kib'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kib')
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "kat_kd").text = row.kat_kd
            ET.SubElement(xml_greeting, "kat_nm").text = row.kat_nm
            ET.SubElement(xml_greeting, "no_register").text = unicode(row.no_register)
            ET.SubElement(xml_greeting, "b_merk").text = row.b_merk
            ET.SubElement(xml_greeting, "b_type").text = row.b_type
            ET.SubElement(xml_greeting, "a_sertifikat_nomor").text = row.a_sertifikat_nomor
            ET.SubElement(xml_greeting, "b_nomor_pabrik").text = row.b_nomor_pabrik
            ET.SubElement(xml_greeting, "b_nomor_rangka").text = row.b_nomor_rangka
            ET.SubElement(xml_greeting, "b_nomor_mesin").text = row.b_nomor_mesin
            ET.SubElement(xml_greeting, "b_bahan").text = row.b_bahan
            ET.SubElement(xml_greeting, "asal_usul").text = row.asal_usul
            ET.SubElement(xml_greeting, "th_beli").text = unicode(row.th_beli)
            ET.SubElement(xml_greeting, "e_ukuran").text = unicode(row.e_ukuran)
            ET.SubElement(xml_greeting, "d_konstruksi").text = row.d_konstruksi
            ET.SubElement(xml_greeting, "satuan").text = row.satuan
            ET.SubElement(xml_greeting, "kondisi").text = row.kondisi
            ET.SubElement(xml_greeting, "jumlah").text = unicode(row.jumlah)
            ET.SubElement(xml_greeting, "harga").text = unicode(row.harga)
            ET.SubElement(xml_greeting, "keterangan").text = row.keterangan
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "tahun").text = unicode(thn)
        return self.root

#Penghapusan
class asetr012Generator(JasperGenerator):
    def __init__(self):
        super(asetr012Generator, self).__init__()
        self.reportname = get_rpath('aset/R0012.jrxml')
        self.xpath = '/aset/kib'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kib')
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "kat_kd").text = row.kat_kd
            ET.SubElement(xml_greeting, "kat_nm").text = row.kat_nm
            ET.SubElement(xml_greeting, "no_register").text = unicode(row.no_register)
            ET.SubElement(xml_greeting, "b_merk").text = row.b_merk
            ET.SubElement(xml_greeting, "b_type").text = row.b_type
            ET.SubElement(xml_greeting, "a_sertifikat_nomor").text = row.a_sertifikat_nomor
            ET.SubElement(xml_greeting, "b_nomor_pabrik").text = row.b_nomor_pabrik
            ET.SubElement(xml_greeting, "b_nomor_rangka").text = row.b_nomor_rangka
            ET.SubElement(xml_greeting, "b_nomor_mesin").text = row.b_nomor_mesin
            ET.SubElement(xml_greeting, "b_bahan").text = row.b_bahan
            ET.SubElement(xml_greeting, "asal_usul").text = row.asal_usul
            ET.SubElement(xml_greeting, "th_beli").text = unicode(row.th_beli)
            ET.SubElement(xml_greeting, "e_ukuran").text = unicode(row.e_ukuran)
            ET.SubElement(xml_greeting, "d_konstruksi").text = row.d_konstruksi
            ET.SubElement(xml_greeting, "satuan").text = row.satuan
            ET.SubElement(xml_greeting, "kondisi").text = row.kondisi
            ET.SubElement(xml_greeting, "jumlah").text = unicode(row.jumlah)
            ET.SubElement(xml_greeting, "harga").text = unicode(row.harga)
            ET.SubElement(xml_greeting, "keterangan").text = row.keterangan
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "tahun").text = unicode(thn)
        return self.root

#Neraca
class asetr013Generator(JasperGenerator):
    def __init__(self):
        super(asetr013Generator, self).__init__()
        self.reportname = get_rpath('aset/R0013.jrxml')
        self.xpath = '/aset/kib'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kib')
            ET.SubElement(xml_greeting, "kode").text = row.kode
            ET.SubElement(xml_greeting, "uraian").text = row.uraian
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "nilai").text = unicode(row.nilai)
            ET.SubElement(xml_greeting, "detil").text = unicode(row.detil)
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "tahun").text = unicode(thn)
        return self.root

#KIB A // PPKD
class asetr104Generator(JasperGenerator):
    def __init__(self):
        super(asetr104Generator, self).__init__()
        self.reportname = get_rpath('aset/R1004.jrxml')
        self.xpath = '/aset/kib'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kib')
            ET.SubElement(xml_greeting, "katnm").text = row.katnm
            ET.SubElement(xml_greeting, "katkd").text = row.katkd
            ET.SubElement(xml_greeting, "no_register").text = unicode(row.no_register)
            ET.SubElement(xml_greeting, "a_luas_m2").text = unicode(row.a_luas_m2)
            ET.SubElement(xml_greeting, "th_beli").text = unicode(row.th_beli)
            ET.SubElement(xml_greeting, "a_alamat").text = row.a_alamat
            ET.SubElement(xml_greeting, "a_hak_tanah").text = row.a_hak_tanah
            ET.SubElement(xml_greeting, "a_sertifikat_tgl").text = unicode(row.a_sertifikat_tanggal)
            ET.SubElement(xml_greeting, "a_sertifikat_no").text = row.a_sertifikat_nomor
            ET.SubElement(xml_greeting, "a_penggunaan").text = row.a_penggunaan
            ET.SubElement(xml_greeting, "asal_usul").text = row.asal_usul
            ET.SubElement(xml_greeting, "harga").text = unicode(row.harga)
            ET.SubElement(xml_greeting, "keterangan").text = row.keterangan
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unitkd").text = row.unitkd
            ET.SubElement(xml_greeting, "unitnm").text = row.unitnm
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

#KIB B // PPKD
class asetr105Generator(JasperGenerator):
    def __init__(self):
        super(asetr105Generator, self).__init__()
        self.reportname = get_rpath('aset/R1005.jrxml')
        self.xpath = '/aset/kib'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kib')
            ET.SubElement(xml_greeting, "katnm").text = row.katnm
            ET.SubElement(xml_greeting, "katkd").text = row.katkd
            ET.SubElement(xml_greeting, "no_register").text = unicode(row.no_register)
            ET.SubElement(xml_greeting, "b_merk").text = row.b_merk
            ET.SubElement(xml_greeting, "b_type").text = row.b_type
            ET.SubElement(xml_greeting, "b_cc").text = row.b_cc
            ET.SubElement(xml_greeting, "b_bahan").text = row.b_bahan
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "b_nomor_pabrik").text = row.b_nomor_pabrik
            ET.SubElement(xml_greeting, "b_nomor_rangka").text = row.b_nomor_rangka
            ET.SubElement(xml_greeting, "b_nomor_mesin").text = row.b_nomor_mesin
            ET.SubElement(xml_greeting, "b_nomor_polisi").text = row.b_nomor_polisi
            ET.SubElement(xml_greeting, "b_nomor_bpkb").text = row.b_nomor_bpkb
            ET.SubElement(xml_greeting, "asal_usul").text = row.asal_usul
            ET.SubElement(xml_greeting, "harga").text = row.harga
            ET.SubElement(xml_greeting, "keterangan").text = row.keterangan
            ET.SubElement(xml_greeting, "tahun").text = row.tahun
            ET.SubElement(xml_greeting, "unitkd").text = row.unitkd
            ET.SubElement(xml_greeting, "unitnm").text = row.unitnm
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

#KIB C // PPKD
class asetr106Generator(JasperGenerator):
    def __init__(self):
        super(asetr106Generator, self).__init__()
        self.reportname = get_rpath('aset/R1006.jrxml')
        self.xpath = '/aset/kib'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kib')
            ET.SubElement(xml_greeting, "katnm").text = row.katnm
            ET.SubElement(xml_greeting, "katkd").text = row.katkd
            ET.SubElement(xml_greeting, "no_register").text = unicode(row.no_register)
            ET.SubElement(xml_greeting, "kondisi").text = row.kondisi
            ET.SubElement(xml_greeting, "c_bertingkat_tidak").text = row.c_bertingkat_tidak
            ET.SubElement(xml_greeting, "c_beton_tidak").text = row.c_beton_tidak
            ET.SubElement(xml_greeting, "c_luas_lantai").text = row.c_luas_lantai
            ET.SubElement(xml_greeting, "c_lokasi").text = row.c_lokasi
            ET.SubElement(xml_greeting, "c_dokumen_tanggal").text = unicode(row.c_dokumen_tanggal)
            ET.SubElement(xml_greeting, "c_dokumen_nomor").text = row.c_dokumen_nomor
            ET.SubElement(xml_greeting, "c_luas_bangunan").text =  unicode(row.c_luas_bangunan)
            ET.SubElement(xml_greeting, "c_status_tanah").text = row.c_status_tanah
            ET.SubElement(xml_greeting, "c_kode_tanah").text = unicode(row.c_kode_tanah)
            ET.SubElement(xml_greeting, "asal_usul").text = row.asal_usul
            ET.SubElement(xml_greeting, "harga").text = unicode(row.harga)
            ET.SubElement(xml_greeting, "keterangan").text = row.keterangan
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unitkd").text = row.unitkd
            ET.SubElement(xml_greeting, "unitnm").text = row.unitnm
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

#KIB D // PPKD
class asetr107Generator(JasperGenerator):
    def __init__(self):
        super(asetr107Generator, self).__init__()
        self.reportname = get_rpath('aset/R1007.jrxml')
        self.xpath = '/aset/kib'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kib')
            ET.SubElement(xml_greeting, "katnm").text = row.katnm
            ET.SubElement(xml_greeting, "katkd").text = row.katkd
            ET.SubElement(xml_greeting, "no_register").text = unicode(row.no_register)
            ET.SubElement(xml_greeting, "d_konstruksi").text = row.d_konstruksi
            ET.SubElement(xml_greeting, "d_panjang").text = unicode(row.d_panjang)
            ET.SubElement(xml_greeting, "d_lebar").text = unicode(row.d_lebar)
            ET.SubElement(xml_greeting, "d_luas").text = unicode(row.d_luas)
            ET.SubElement(xml_greeting, "d_lokasi").text = row.d_lokasi
            ET.SubElement(xml_greeting, "d_dokumen_tanggal").text = unicode(row.d_dokumen_tanggal)
            ET.SubElement(xml_greeting, "d_dokumen_nomor").text = row.d_dokumen_nomor
            ET.SubElement(xml_greeting, "d_status_tanah").text = row.d_status_tanah
            ET.SubElement(xml_greeting, "d_kode_tanah").text = unicode(row.d_kode_tanah)
            ET.SubElement(xml_greeting, "asal_usul").text = row.asal_usul
            ET.SubElement(xml_greeting, "harga").text = unicode(row.harga)
            ET.SubElement(xml_greeting, "kondisi").text = row.kondisi
            ET.SubElement(xml_greeting, "keterangan").text = row.keterangan
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unitkd").text = row.unitkd
            ET.SubElement(xml_greeting, "unitnm").text = row.unitnm
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

#KIB E // PPKD
class asetr108Generator(JasperGenerator):
    def __init__(self):
        super(asetr108Generator, self).__init__()
        self.reportname = get_rpath('aset/R1008.jrxml')
        self.xpath = '/aset/kib'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kib')
            ET.SubElement(xml_greeting, "katnm").text = row.katnm
            ET.SubElement(xml_greeting, "katkd").text = row.katkd
            ET.SubElement(xml_greeting, "no_register").text = unicode(row.no_register)
            ET.SubElement(xml_greeting, "e_judul").text = row.e_judul
            ET.SubElement(xml_greeting, "e_spek").text = row.e_spek
            ET.SubElement(xml_greeting, "e_asal").text = row.e_asal
            ET.SubElement(xml_greeting, "e_pencipta").text = row.e_pencipta
            ET.SubElement(xml_greeting, "e_bahan").text = row.e_bahan
            ET.SubElement(xml_greeting, "e_jenis").text = row.e_jenis
            ET.SubElement(xml_greeting, "e_ukuran").text = unicode(row.e_ukuran)
            ET.SubElement(xml_greeting, "jumlah").text = unicode(row.jumlah)
            ET.SubElement(xml_greeting, "asal_usul").text = row.asal_usul
            ET.SubElement(xml_greeting, "b_thbuat").text = row.b_thbuat
            ET.SubElement(xml_greeting, "harga").text = unicode(row.harga)
            ET.SubElement(xml_greeting, "keterangan").text = row.keterangan
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unitkd").text = row.unitkd
            ET.SubElement(xml_greeting, "unitnm").text = row.unitnm
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

#KIB F // PPKD
class asetr109Generator(JasperGenerator):
    def __init__(self):
        super(asetr109Generator, self).__init__()
        self.reportname = get_rpath('aset/R1009.jrxml')
        self.xpath = '/aset/kib'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kib')
            ET.SubElement(xml_greeting, "katnm").text = row.katnm
            ET.SubElement(xml_greeting, "katkd").text = row.katkd
            ET.SubElement(xml_greeting, "kondisi").text = row.kondisi
            ET.SubElement(xml_greeting, "f_bertingkat_tidak").text = row.f_bertingkat_tidak
            ET.SubElement(xml_greeting, "f_beton_tidak").text = row.f_beton_tidak
            ET.SubElement(xml_greeting, "f_luas_lantai").text = unicode(row.f_luas_lantai)
            ET.SubElement(xml_greeting, "f_lokasi").text = row.f_lokasi
            ET.SubElement(xml_greeting, "f_dokumen_tanggal").text = unicode(row.f_dokumen_tanggal)
            ET.SubElement(xml_greeting, "f_dokumen_nomor").text = row.f_dokumen_nomor
            ET.SubElement(xml_greeting, "tgl_perolehan").text = unicode(row.tgl_perolehan)
            ET.SubElement(xml_greeting, "f_status_tanah").text = row.f_status_tanah
            ET.SubElement(xml_greeting, "f_kode_tanah").text = unicode(row.f_kode_tanah)
            ET.SubElement(xml_greeting, "asal_usul").text = row.asal_usul
            ET.SubElement(xml_greeting, "harga").text = unicode(row.harga)
            ET.SubElement(xml_greeting, "keterangan").text = row.keterangan
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "unitkd").text = row.unitkd
            ET.SubElement(xml_greeting, "unitnm").text = row.unitnm
        return self.root
        
#Inventaris
class asetr111Generator(JasperGenerator):
    def __init__(self):
        super(asetr111Generator, self).__init__()
        self.reportname = get_rpath('aset/R1011.jrxml')
        self.xpath = '/aset/kib'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kib')
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "kat_kd").text = row.kat_kd
            ET.SubElement(xml_greeting, "kat_nm").text = row.kat_nm
            ET.SubElement(xml_greeting, "no_register").text = unicode(row.no_register)
            ET.SubElement(xml_greeting, "b_merk").text = row.b_merk
            ET.SubElement(xml_greeting, "b_type").text = row.b_type
            ET.SubElement(xml_greeting, "a_sertifikat_nomor").text = row.a_sertifikat_nomor
            ET.SubElement(xml_greeting, "b_nomor_pabrik").text = row.b_nomor_pabrik
            ET.SubElement(xml_greeting, "b_nomor_rangka").text = row.b_nomor_rangka
            ET.SubElement(xml_greeting, "b_nomor_mesin").text = row.b_nomor_mesin
            ET.SubElement(xml_greeting, "b_bahan").text = row.b_bahan
            ET.SubElement(xml_greeting, "asal_usul").text = row.asal_usul
            ET.SubElement(xml_greeting, "th_beli").text = unicode(row.th_beli)
            ET.SubElement(xml_greeting, "e_ukuran").text = unicode(row.e_ukuran)
            ET.SubElement(xml_greeting, "d_konstruksi").text = row.d_konstruksi
            ET.SubElement(xml_greeting, "satuan").text = row.satuan
            ET.SubElement(xml_greeting, "kondisi").text = row.kondisi
            ET.SubElement(xml_greeting, "jumlah").text = unicode(row.jumlah)
            ET.SubElement(xml_greeting, "harga").text = unicode(row.harga)
            ET.SubElement(xml_greeting, "keterangan").text = row.keterangan
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "tahun").text = unicode(thn)
        return self.root
        
#Penghapusan
class asetr112Generator(JasperGenerator):
    def __init__(self):
        super(asetr112Generator, self).__init__()
        self.reportname = get_rpath('aset/R1012.jrxml')
        self.xpath = '/aset/kib'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kib')
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "kat_kd").text = row.kat_kd
            ET.SubElement(xml_greeting, "kat_nm").text = row.kat_nm
            ET.SubElement(xml_greeting, "no_register").text = unicode(row.no_register)
            ET.SubElement(xml_greeting, "b_merk").text = row.b_merk
            ET.SubElement(xml_greeting, "b_type").text = row.b_type
            ET.SubElement(xml_greeting, "a_sertifikat_nomor").text = row.a_sertifikat_nomor
            ET.SubElement(xml_greeting, "b_nomor_pabrik").text = row.b_nomor_pabrik
            ET.SubElement(xml_greeting, "b_nomor_rangka").text = row.b_nomor_rangka
            ET.SubElement(xml_greeting, "b_nomor_mesin").text = row.b_nomor_mesin
            ET.SubElement(xml_greeting, "b_bahan").text = row.b_bahan
            ET.SubElement(xml_greeting, "asal_usul").text = row.asal_usul
            ET.SubElement(xml_greeting, "th_beli").text = unicode(row.th_beli)
            ET.SubElement(xml_greeting, "e_ukuran").text = unicode(row.e_ukuran)
            ET.SubElement(xml_greeting, "d_konstruksi").text = row.d_konstruksi
            ET.SubElement(xml_greeting, "satuan").text = row.satuan
            ET.SubElement(xml_greeting, "kondisi").text = row.kondisi
            ET.SubElement(xml_greeting, "jumlah").text = unicode(row.jumlah)
            ET.SubElement(xml_greeting, "harga").text = unicode(row.harga)
            ET.SubElement(xml_greeting, "keterangan").text = row.keterangan
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "tahun").text = unicode(thn)
        return self.root

#Neraca
class asetr113Generator(JasperGenerator):
    def __init__(self):
        super(asetr113Generator, self).__init__()
        self.reportname = get_rpath('aset/R1013.jrxml')
        self.xpath = '/aset/kib'
        self.root = ET.Element('aset') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kib')
            ET.SubElement(xml_greeting, "kode").text = row.kode
            ET.SubElement(xml_greeting, "uraian").text = row.uraian
            ET.SubElement(xml_greeting, "nilai").text = unicode(row.nilai)
            ET.SubElement(xml_greeting, "detil").text = unicode(row.detil)
            ET.SubElement(xml_greeting, "customer").text = customer
            ET.SubElement(xml_greeting, "tahun").text = unicode(thn)
        return self.root

