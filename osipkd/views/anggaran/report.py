import os
import unittest
import os.path
import uuid

from osipkd.tools import row2dict, xls_reader

from datetime import datetime
#from sqlalchemy import not_, func
from sqlalchemy import *
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from osipkd.models import DBSession, User, Group, Route, GroupRoutePermission
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

"""
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
from osipkd.views.base_view import *
from datetime import datetime
from pyramid.renderers import render_to_response

#from anggaran import AnggaranBaseViews
"""
def get_rpath(filename):
    a = AssetResolver('osipkd')
    resolver = a.resolve(''.join(['reports/',filename]))
    return resolver.abspath()
    
angka = {1:'satu',2:'dua',3:'tiga',4:'empat',5:'lima',6:'enam',7:'tujuh',\
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
            return Terbilang(p)
        else:
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

class ViewAnggaranLap(BaseViews):
    def __init__(self, context, request):
        global customer
        global logo
        BaseViews.__init__(self, context, request)
        self.app = 'anggaran'

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

        self.cust_nm = 'cust_nm' in self.session and self.session['cust_nm'] or 'PEMERINTAH KABUPATEN TANGERANG'
        customer = self.cust_nm
        logo = self.request.static_url('osipkd:static/img/logo.png')
        
    @view_config(route_name="anggaran_r000", renderer="templates/ag-report/r000.pt", permission="read")
    def anggaran_r000(self):
        params = self.request.params
        return dict(datas=self.datas)
  
    @view_config(route_name="anggaran_r000_act")
    def anggaran_r000_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if url_dict['act']=='r001' :
            query = DBSession.query(Urusan.kode, Urusan.nama).order_by(Urusan.kode).all()
            generator = r001Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        elif url_dict['act']=='r002' :
            query = DBSession.query(Urusan.kode.label("urusankd"), Unit.kode, Unit.nama, 
                func.coalesce(Unit.kategori,"").label("kategori"), func.coalesce(Unit.singkat,"").label("singkat")).\
                    filter(Unit.urusan_id==Urusan.id).order_by(Urusan.kode,Unit.kode).all()
            generator = r002Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        elif url_dict['act']=='r003' :
            query = DBSession.query(Urusan.kode, Urusan.nama, Program.kode.label("programkd"), Program.nama.label("programnm")).\
                    filter(Urusan.id==Program.urusan_id).order_by(Urusan.kode,Program.kode).all()
            generator = r003Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        elif url_dict['act']=='r041' :
            query = DBSession.query(Rekening.kode, Rekening.nama, Rekening.level_id).order_by(Rekening.kode).all()
            generator = r041Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        elif url_dict['act']=='r042' :
            query = DBSession.query(Rekening.kode, Rekening.nama, Rekening.level_id).order_by(Rekening.kode).all()
            generator = r042Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        elif url_dict['act']=='r005' :
            query = DBSession.query(Pegawai.kode, Pegawai.nama).order_by(Pegawai.kode).all()
            generator = r005Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        elif url_dict['act']=='r006' :
            query = DBSession.query(Program.kode, Program.nama, Kegiatan.kode.label("kegiatankd"), Kegiatan.nama.label("kegiatannm")).\
                    filter(Program.id==Kegiatan.program_id).order_by(Program.kode,Kegiatan.kode).all()
            generator = r006Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        elif url_dict['act']=='r007' :
            query = DBSession.query(User.user_name.label('username'), User.email, User.status, User.last_login_date.label('last_login'), User.registered_date).\
                    order_by(User.user_name).all()
            generator = r007Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        elif url_dict['act']=='r008' :
            query = DBSession.query(Group.group_name.label('kode'), Group.description.label('nama')).order_by(Group.group_name).all()
            generator = r008Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        elif url_dict['act']=='r009' :
            query = DBSession.query(Fungsi.kode, Fungsi.nama).order_by(Fungsi.kode).all()
            generator = r009Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        elif url_dict['act']=='r010' :
            query = DBSession.query(Jabatan.kode, Jabatan.nama).order_by(Jabatan.kode).all()
            generator = r010Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)   
            return response
        elif url_dict['act']=='r011' :
            query = DBSession.query(Pegawai.kode, Pegawai.nama, Jabatan.nama.label('jabatan'), Unit.nama.label('skpd'), Pejabat.mulai, Pejabat.selesai
                  ).filter(Pejabat.pegawai_id==Pegawai.id, Pejabat.unit_id==Unit.id, Pejabat.jabatan_id==Jabatan.id
                  ).order_by(Pegawai.kode).all()
            generator = r011Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        elif url_dict['act']=='r012' :
            query = DBSession.query(Tahun.tahun, Tahun.status_apbd, Tahun.tanggal_1, Tahun.tanggal_2, Tahun.tanggal_3, Tahun.tanggal_4
                  ).order_by(Tahun.tahun).all()
            generator = r012Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        elif url_dict['act']=='r013' :
            query = DBSession.query(App.kode,App.nama,App.disabled,App.tahun).order_by(App.kode).all()
            generator = r013Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        elif url_dict['act']=='r014' :
            query = DBSession.query(Route.kode,Route.nama,Route.path,Route.perm_name,Route.disabled).order_by(Route.kode).all()
            generator = r014Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        elif url_dict['act']=='r015' :
            query = DBSession.query(Rekening.kode,Rekening.nama.label('rek_nm'),DasarHukum.no_urut,DasarHukum.nama.label('dsrhkm_nm')).filter(DasarHukum.rekening_id==Rekening.id).order_by(Rekening.kode,DasarHukum.no_urut).all()
            generator = r015Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        elif url_dict['act']=='r016' :
            query = DBSession.query(User.email,User.user_name,User.status,Unit.nama, UserUnit.sub_unit
               ).outerjoin(UserUnit
               ).outerjoin(Unit
               ).order_by(User.user_name).all()
            generator = r016Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        elif url_dict['act']=='r017' :
            query = DBSession.query(Group.group_name.label('grup_nm'),Route.nama.label('route_nm'),Route.path
               ).filter(GroupRoutePermission.group_id==Group.id, GroupRoutePermission.route_id==Route.id
               ).order_by(Group.group_name,Route.nama).all()
            generator = r017Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        elif url_dict['act']=='r018' :
            query = DBSession.query(Urusan.nama.label('urusan_nm'),Fungsi.nama.label('fungsi_nm'),FungsiUrusan.nama
               ).filter(Urusan.id==FungsiUrusan.urusan_id, Fungsi.id==FungsiUrusan.fungsi_id
               ).order_by(Fungsi.nama,Urusan.nama,FungsiUrusan.nama).all()
            generator = r018Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        elif url_dict['act']=='r019' :
            query = DBSession.query(Sap.kode, Sap.nama, Sap.level_id).order_by(Sap.kode).all()
            generator = r019Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
        else:
            return HTTPNotFound() #TODO: Warning Hak Akses 

    ######## RKA
    @view_config(route_name="anggaran_r100", renderer="templates/ag-report/r100.pt", permission="read")
    def anggaran_r100(self):
        params = self.request.params
        return dict(datas=self.datas)
        #, row=KegiatanSub.get_header(self.unit_id, self.keg_id),

    @view_config(route_name="anggaran_r100_act", renderer="json")
    def anggaran_r100_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict
        pk_id = 'id' in params and params['id'] and int(params['id']) or 0
        if url_dict['act']=='grid' :
            # defining columns
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('tipe'))
            columns.append(ColumnDT('no_urut'))
            columns.append(ColumnDT("".join(['tolok_ukur_',str(self.status_apbd)])))
            columns.append(ColumnDT("".join(['volume_',str(self.status_apbd)])))
            columns.append(ColumnDT("".join(['satuan_',str(self.status_apbd)])))

            query = DBSession.query(KegiatanIndikator)\
                .join(KegiatanSub)\
                .filter(KegiatanSub.id==keg_id,
                        KegiatanSub.unit_id==self.session['unit_id'])
            rowTable = DataTables(req, KegiatanIndikator, query, columns)
            return rowTable.output_result()

        elif url_dict['act']=='grid2' :
            # defining columns
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('kegiatans.kode'))
            columns.append(ColumnDT('kegiatans.nama'))
            columns.append(ColumnDT('kegiatans.programs.nama'))

            query = DBSession.query(KegiatanSub)\
                .join(Kegiatan).join(Program)\
                .filter(KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        not_(Kegiatan.kode.in_(('0.00.00.10','0.00.00.21','0.00.00.31','0.00.00.41','0.00.00.99'))))
            rowTable = DataTables(req, KegiatanSub, query, columns)
            return rowTable.output_result()

        ## Ringkasan RKA
        elif url_dict['act']=='0' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                (KegiatanItem.vol_1_1* KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('jml1'),
                KegiatanSub.tahun_id.label('tahun'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'))\
                .filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                        KegiatanItem.rekening_id==Rekening.id,
                        KegiatanSub.unit_id==Unit.id,
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'])\
                .subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, 
                func.sum(subq1.c.jml1).label('jumlah1'))\
                .filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode))
                ,Rekening.level_id<6).group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun)\
                .order_by(Rekening.kode).all()                    

            generator = r100Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
            
        ## Pendapatan RKA
        elif url_dict['act']=='1' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'), Rekening.level_id.label('lev'),
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.id.label('kegiatan_sub_id'),
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), Tahun.tanggal_1.label('tanggal'),
                (KegiatanItem.vol_1_1* KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('jml1'),
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan).join(Tahun
                ).filter(
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode=='0.00.00.10'
                ).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.tanggal,
                func.sum(subq1.c.jml1).label('jumlah1'),
                func.max(subq1.c.lev).label('maxlevel')
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode))
                )\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.tanggal,
                ).order_by(Rekening.kode).all()                    

            generator = r101Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Pendapatan Lampiran
        elif url_dict['act']=='11' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), KegiatanItem.vol_1_1.label('volume1'), KegiatanItem.sat_1_1.label('satuan1'), 
                 KegiatanItem.vol_1_2.label('volume2'), KegiatanItem.sat_1_2.label('satuan2'), KegiatanItem.hsat_1.label('harga'), 
                 Tahun.tanggal_1.label('tanggal'),                 
                 (KegiatanItem.vol_1_1*KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('anggaran')
                 ).join(Unit).join(Kegiatan).join(Tahun).join(Urusan).join(KegiatanItem).join(Rekening
                 ).filter(Rekening.id==KegiatanItem.rekening_id, KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   Kegiatan.kode=='0.00.00.10'
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r1011Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## BTL RKA
        elif url_dict['act']=='21' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'), Rekening.level_id.label('lev'),
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.id.label('kegiatan_sub_id'),
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), Tahun.tanggal_1.label('tanggal'),
                (KegiatanItem.vol_1_1* KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('jml1'),
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan).join(Tahun
                ).filter(
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode=='0.00.00.21'
                ).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.tanggal,
                func.sum(subq1.c.jml1).label('jumlah1')
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode))
                )\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.tanggal,
                ).order_by(Rekening.kode).all()                    

            generator = r102Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## BTL RKA Lampiran
        elif url_dict['act']=='211' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), KegiatanItem.vol_1_1.label('volume1'), KegiatanItem.sat_1_1.label('satuan1'), 
                 KegiatanItem.vol_1_2.label('volume2'), KegiatanItem.sat_1_2.label('satuan2'), KegiatanItem.hsat_1.label('harga'), 
                 Tahun.tanggal_1.label('tanggal'),                 
                 (KegiatanItem.vol_1_1*KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('anggaran')
                 ).join(Unit).join(Kegiatan).join(Tahun).join(Urusan).join(KegiatanItem).join(Rekening
                 ).filter(Rekening.id==KegiatanItem.rekening_id, KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   Kegiatan.kode=='0.00.00.21'
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r1011Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## ProgKeg RKA
        elif url_dict['act']=='22' :
            query = DBSession.query(KegiatanItem
                  ).join(Rekening).join(KegiatanSub).join(Kegiatan
                  ).filter(KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'],
                   not_(Kegiatan.kode.in_(('0.00.00.10', '0.00.00.21', '0.00.00.31','0.00.00.32'))))
                  
            generator = r103Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## BL RKA
        elif url_dict['act']=='221' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), 
                 Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Program.kode.label('program_kd'), Program.nama.label('program_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.lokasi, KegiatanSub.target, KegiatanSub.sasaran, 
                 KegiatanSub.amt_lalu, KegiatanSub.amt_yad, KegiatanSub.id,
                 func.sum(KegiatanItem.vol_1_1*KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('anggaran')
                 ).join(Unit).join(Kegiatan).join(Program).join(Urusan).join(KegiatanItem)\
                 .filter(KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   KegiatanSub.id==self.request.params['id']
                 ).group_by(KegiatanSub.tahun_id, Urusan.kode, Urusan.nama, 
                 Unit.kode, Unit.nama,
                 Program.kode, Program.nama,
                 Kegiatan.kode, Kegiatan.nama,
                 KegiatanSub.lokasi, KegiatanSub.target, KegiatanSub.sasaran, 
                 KegiatanSub.amt_lalu, KegiatanSub.amt_yad, KegiatanSub.id)
                   
            generator = r104Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
            
        ## BL RKA Ikhtisar
        elif url_dict['act']=='2211' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Program.kode.label('program_kd'), Program.nama.label('program_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.lokasi, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), KegiatanItem.vol_1_1.label('volume1'), KegiatanItem.sat_1_1.label('satuan1'), 
                 KegiatanItem.vol_1_2.label('volume2'), KegiatanItem.sat_1_2.label('satuan2'), KegiatanItem.hsat_1.label('harga'), 
                 Tahun.tanggal_1.label('tanggal'),                 
                 (KegiatanItem.vol_1_1*KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('anggaran')
                 ).filter(KegiatanSub.unit_id==Unit.id, Kegiatan.id==KegiatanSub.kegiatan_id, KegiatanSub.id==KegiatanItem.kegiatan_sub_id, 
                   Rekening.id==KegiatanItem.rekening_id, Unit.urusan_id==Urusan.id, Program.id==Kegiatan.program_id, Tahun.id==KegiatanSub.tahun_id,
                   KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   KegiatanSub.id==self.request.params['id']
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Program.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r1041Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
		
        ## Biaya RKA
        elif url_dict['act']=='3' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                (KegiatanItem.vol_1_1* KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('jml1'),
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'),
                KegiatanSub.tahun_id.label('tahun')
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan
                ).filter(Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode.in_(('0.00.00.31', '0.00.00.32')))\
                .subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                func.substr(Rekening.kode,1,1).label('rek_kd1'),func.substr(Rekening.kode,1,3).label('rek_kd2'),
                func.substr(Rekening.kode,1,5).label('rek_kd3'),func.substr(Rekening.kode,1,8).label('rek_kd4'),
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, 
                func.sum(subq1.c.jml1).label('jumlah1'))\
                .filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)))\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                func.substr(Rekening.kode,1,1),func.substr(Rekening.kode,1,3),
                func.substr(Rekening.kode,1,5),func.substr(Rekening.kode,1,8),
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun)\
                .order_by(Rekening.kode).all()                    

            generator = r105Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Biaya Terima RKA
        elif url_dict['act']=='31' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'), Rekening.level_id.label('lev'),
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.id.label('kegiatan_sub_id'),
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), Tahun.tanggal_1.label('tanggal'),
                (KegiatanItem.vol_1_1* KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('jml1'),
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan).join(Tahun
                ).filter(
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode=='0.00.00.31'
                ).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.tanggal,
                func.sum(subq1.c.jml1).label('jumlah1'),
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)), Rekening.level_id>1
                )\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.tanggal,
                ).order_by(Rekening.kode).all()                    

            generator = r106Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Biaya Terima RKA Lampiran
        elif url_dict['act']=='311' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), KegiatanItem.vol_1_1.label('volume1'), KegiatanItem.sat_1_1.label('satuan1'), 
                 KegiatanItem.vol_1_2.label('volume2'), KegiatanItem.sat_1_2.label('satuan2'), KegiatanItem.hsat_1.label('harga'), 
                 Tahun.tanggal_1.label('tanggal'),                 
                 (KegiatanItem.vol_1_1*KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('anggaran')
                 ).join(Unit).join(Kegiatan).join(Tahun).join(Urusan).join(KegiatanItem).join(Rekening
                 ).filter(Rekening.id==KegiatanItem.rekening_id, KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   Kegiatan.kode=='0.00.00.31'
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r1011Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Biaya Keluar RKA
        elif url_dict['act']=='32' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'), Rekening.level_id.label('lev'),
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.id.label('kegiatan_sub_id'),
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), Tahun.tanggal_1.label('tanggal'),
                (KegiatanItem.vol_1_1* KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('jml1'),
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan).join(Tahun
                ).filter(
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode=='0.00.00.32'
                ).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.tanggal,
                func.sum(subq1.c.jml1).label('jumlah1')
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)), Rekening.level_id>1
                )\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.tanggal,
                ).order_by(Rekening.kode).all()                    

            generator = r107Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Biaya Keluar RKA Lampiran
        elif url_dict['act']=='321' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), KegiatanItem.vol_1_1.label('volume1'), KegiatanItem.sat_1_1.label('satuan1'), 
                 KegiatanItem.vol_1_2.label('volume2'), KegiatanItem.sat_1_2.label('satuan2'), KegiatanItem.hsat_1.label('harga'), 
                 Tahun.tanggal_1.label('tanggal'),                 
                 (KegiatanItem.vol_1_1*KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('anggaran')
                 ).join(Unit).join(Kegiatan).join(Tahun).join(Urusan).join(KegiatanItem).join(Rekening
                 ).filter(Rekening.id==KegiatanItem.rekening_id, KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   Kegiatan.kode=='0.00.00.32'
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r1011Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

    ######## DPA
    @view_config(route_name="anggaran_r200", renderer="templates/ag-report/r200.pt", permission="read")
    def anggaran_r200(self):
        params = self.request.params
        return dict(datas=self.datas) 
        #row=KegiatanSub.get_header(self.unit_id, self.keg_id),)

    @view_config(route_name="anggaran_r200_act", renderer="json", permission="read")
    def anggaran_r200_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict
        pk_id = 'id' in params and params['id'] and int(params['id']) or 0
#            keg_id = self.session['keg_id']
        if url_dict['act']=='grid' :
            # defining columns
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('tipe'))
            columns.append(ColumnDT('no_urut'))
            columns.append(ColumnDT("".join(['tolok_ukur_',str(self.status_apbd)])))
            columns.append(ColumnDT("".join(['volume_',str(self.status_apbd)])))
            columns.append(ColumnDT("".join(['satuan_',str(self.status_apbd)])))

            query = DBSession.query(KegiatanIndikator)\
                .join(KegiatanSub)\
                .filter(KegiatanSub.id==keg_id,
                        KegiatanSub.unit_id==self.session['unit_id'])
            rowTable = DataTables(req, KegiatanIndikator, query, columns)
            return rowTable.output_result()

        elif url_dict['act']=='grid2' :
            # defining columns
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('kegiatans.kode'))
            columns.append(ColumnDT('kegiatans.nama'))
            columns.append(ColumnDT('kegiatans.programs.nama'))

            query = DBSession.query(KegiatanSub)\
                .join(Kegiatan).join(Program)\
                .filter(KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        not_(Kegiatan.kode.in_(('0.00.00.10','0.00.00.21','0.00.00.31','0.00.00.41','0.00.00.99'))))
            rowTable = DataTables(req, KegiatanSub, query, columns)
            return rowTable.output_result()

        ## Ringkasan DPA
        elif url_dict['act']=='0' :
            query = DBSession.query(KegiatanSub.tahun_id,Urusan.kode.label('urusan_kd'),
               Urusan.nama.label('urusan_nm'),Unit.id.label('unit_id'),Unit.kode.label('unit_kd'),
               Unit.nama.label('unit_nm'))\
               .filter(KegiatanSub.unit_id==Unit.id,Unit.urusan_id==Urusan.id,
               KegiatanSub.tahun_id==self.session['tahun'],KegiatanSub.unit_id==self.session['unit_id'])\
               .group_by(KegiatanSub.tahun_id,Urusan.kode,Urusan.nama,Unit.id,Unit.kode,
               Unit.nama)

            generator = r200Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
            
        ## Pendapatan DPA
        elif url_dict['act']=='1' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'), Rekening.level_id.label('lev'),
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.id.label('kegiatan_sub_id'),
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), Tahun.tanggal_2.label('tanggal'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml1'),
                (KegiatanItem.bln01+KegiatanItem.bln02+KegiatanItem.bln03).label('trw1'),
                (KegiatanItem.bln04+KegiatanItem.bln05+KegiatanItem.bln06).label('trw2'),
                (KegiatanItem.bln07+KegiatanItem.bln08+KegiatanItem.bln09).label('trw3'),
                (KegiatanItem.bln10+KegiatanItem.bln11+KegiatanItem.bln12).label('trw4')
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan).join(Tahun
                ).filter(
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode=='0.00.00.10'
                ).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.tanggal,
                func.sum(subq1.c.jml1).label('jumlah1'),
                func.sum(subq1.c.trw1).label('trw1'), func.sum(subq1.c.trw2).label('trw2'),
                func.sum(subq1.c.trw3).label('trw3'), func.sum(subq1.c.trw4).label('trw4'),
                func.max(subq1.c.lev).label('maxlevel')
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode))
                )\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.tanggal,
                ).order_by(Rekening.kode).all()                    

            generator = r201Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Pendapatan DPA Lampiran
        elif url_dict['act']=='11' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), KegiatanItem.vol_2_1.label('volume1'), KegiatanItem.sat_2_1.label('satuan1'), 
                 KegiatanItem.vol_2_2.label('volume2'), KegiatanItem.sat_2_2.label('satuan2'), KegiatanItem.hsat_2.label('harga'), 
                 Tahun.tanggal_2.label('tanggal'),                 
                 (KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('anggaran')
                 ).join(Unit).join(Kegiatan).join(Tahun).join(Urusan).join(KegiatanItem).join(Rekening
                 ).filter(Rekening.id==KegiatanItem.rekening_id, KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   Kegiatan.kode=='0.00.00.10'
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r2011Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
			
        ## BTL DPA
        elif url_dict['act']=='21' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'), Rekening.level_id.label('lev'),
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.id.label('kegiatan_sub_id'),
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), Tahun.tanggal_2.label('tanggal'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml1'),
                (KegiatanItem.bln01+KegiatanItem.bln02+KegiatanItem.bln03).label('trw1'),
                (KegiatanItem.bln04+KegiatanItem.bln05+KegiatanItem.bln06).label('trw2'),
                (KegiatanItem.bln07+KegiatanItem.bln08+KegiatanItem.bln09).label('trw3'),
                (KegiatanItem.bln10+KegiatanItem.bln11+KegiatanItem.bln12).label('trw4')
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan).join(Tahun
                ).filter(
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode=='0.00.00.21'
                ).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.tanggal,
                func.sum(subq1.c.jml1).label('jumlah1'),
                func.sum(subq1.c.trw1).label('trw1'), func.sum(subq1.c.trw2).label('trw2'),
                func.sum(subq1.c.trw3).label('trw3'), func.sum(subq1.c.trw4).label('trw4'),
                func.max(subq1.c.lev).label('maxlevel')
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode))
                )\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.tanggal,
                ).order_by(Rekening.kode).all()                    

            generator = r202Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## BTL DPA Lampiran
        elif url_dict['act']=='211' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), KegiatanItem.vol_2_1.label('volume1'), KegiatanItem.sat_2_1.label('satuan1'), 
                 KegiatanItem.vol_2_2.label('volume2'), KegiatanItem.sat_2_2.label('satuan2'), KegiatanItem.hsat_2.label('harga'), 
                 Tahun.tanggal_2.label('tanggal'),                 
                 (KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('anggaran')
                 ).join(Unit).join(Kegiatan).join(Tahun).join(Urusan).join(KegiatanItem).join(Rekening
                 ).filter(Rekening.id==KegiatanItem.rekening_id, KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   Kegiatan.kode=='0.00.00.21'
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r2011Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## ProgKeg DPA
        elif url_dict['act']=='22' :
            query = DBSession.query(KegiatanSub.tahun_id.label('tahun'), Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'),
                  Unit.id.label('unit_id'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                  Program.kode.label('program_kd'), Program.nama.label('program_nm'), 
                  Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'), 
                  KegiatanSub.lokasi.label('lokasi'), KegiatanSub.target.label('target'), 
                  func.sum(KegiatanItem.bln01+KegiatanItem.bln02+KegiatanItem.bln03).label('trw1'), 
                  func.sum(KegiatanItem.bln04+KegiatanItem.bln05+KegiatanItem.bln06).label('trw2'), 
                  func.sum(KegiatanItem.bln07+KegiatanItem.bln08+KegiatanItem.bln09).label('trw3'), 
                  func.sum(KegiatanItem.bln10+KegiatanItem.bln11+KegiatanItem.bln12).label('trw4')
                  ).join(KegiatanItem).join(Kegiatan).join(Program).join(Unit).join(Urusan
                  ).filter(Urusan.id==Unit.urusan_id, 
                     KegiatanSub.tahun_id==self.session['tahun'],
                     KegiatanSub.unit_id==self.session['unit_id'],
                     not_(Kegiatan.kode.in_(('0.00.00.10', '0.00.00.21', '0.00.00.31','0.00.00.32')))
                  ).group_by(KegiatanSub.tahun_id, Urusan.kode, Urusan.nama,
                     Unit.id, Unit.kode, Unit.nama, Program.kode, Program.nama, 
                     Kegiatan.kode, Kegiatan.nama, KegiatanSub.lokasi, KegiatanSub.target
                  ).order_by(Urusan.kode, Unit.kode, Program.kode, Kegiatan.kode).all()

            generator = r203Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## BL DPA
        elif url_dict['act']=='221' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), 
                 Unit.id.label('unit_id'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Program.kode.label('program_kd'), Program.nama.label('program_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.lokasi, KegiatanSub.sasaran, KegiatanSub.sdana, KegiatanSub.id, Tahun.tanggal_2.label('tanggal'),
                 func.sum(KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('anggaran')
                 ).join(Tahun).join(Unit).join(Kegiatan).join(Program).join(Urusan).join(KegiatanItem)\
                 .filter(KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   KegiatanSub.id==self.request.params['id']
                 ).group_by(KegiatanSub.tahun_id, Urusan.kode, Urusan.nama, 
                 Unit.id, Unit.kode, Unit.nama,
                 Program.kode, Program.nama,
                 Kegiatan.kode, Kegiatan.nama,
                 KegiatanSub.lokasi, KegiatanSub.sasaran, KegiatanSub.sdana, KegiatanSub.id, Tahun.tanggal_2)

            generator = r204Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

         ## BL DPA Ikhtisar
        elif url_dict['act']=='2211' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Program.kode.label('program_kd'), Program.nama.label('program_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.lokasi, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), KegiatanItem.vol_2_1.label('volume1'), KegiatanItem.sat_2_1.label('satuan1'), 
                 KegiatanItem.vol_2_2.label('volume2'), KegiatanItem.sat_2_2.label('satuan2'), KegiatanItem.hsat_2.label('harga'), 
                 Tahun.tanggal_2.label('tanggal'),                 
                 (KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('anggaran')
                 ).filter(Program.id==Kegiatan.program_id, Kegiatan.id==KegiatanSub.kegiatan_id, KegiatanSub.unit_id==Unit.id, 
                   Unit.urusan_id==Urusan.id, KegiatanSub.id==KegiatanItem.kegiatan_sub_id, Rekening.id==KegiatanItem.rekening_id, 
                   Tahun.id==KegiatanSub.tahun_id,
                   KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   KegiatanSub.id==self.request.params['id']
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Program.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r2041Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

       ## Biaya DPA
        elif url_dict['act']=='3' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml2'),
                (KegiatanItem.bln01+KegiatanItem.bln02+KegiatanItem.bln03).label('trw1'),
                (KegiatanItem.bln04+KegiatanItem.bln05+KegiatanItem.bln06).label('trw2'),
                (KegiatanItem.bln07+KegiatanItem.bln08+KegiatanItem.bln09).label('trw3'),
                (KegiatanItem.bln10+KegiatanItem.bln11+KegiatanItem.bln12).label('trw4'),
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'),
                KegiatanSub.tahun_id.label('tahun')
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan
                ).filter(Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode.in_(('0.00.00.31', '0.00.00.32'))).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, 
                func.sum(subq1.c.jml2).label('jumlah2'),
                func.sum(subq1.c.trw1).label('trw1'),func.sum(subq1.c.trw2).label('trw2'),
                func.sum(subq1.c.trw3).label('trw3'),func.sum(subq1.c.trw4).label('trw4'))\
                .filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)))\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun)\
                .order_by(Rekening.kode).all()                    

            generator = r205Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Biaya Terima DPA
        elif url_dict['act']=='31' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'), Rekening.level_id.label('lev'),
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.id.label('kegiatan_sub_id'),
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), Tahun.tanggal_2.label('tanggal'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml1'),
                (KegiatanItem.bln01+KegiatanItem.bln02+KegiatanItem.bln03).label('trw1'),
                (KegiatanItem.bln04+KegiatanItem.bln05+KegiatanItem.bln06).label('trw2'),
                (KegiatanItem.bln07+KegiatanItem.bln08+KegiatanItem.bln09).label('trw3'),
                (KegiatanItem.bln10+KegiatanItem.bln11+KegiatanItem.bln12).label('trw4')
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan).join(Tahun
                ).filter(
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode=='0.00.00.31'
                ).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.tanggal,
                func.sum(subq1.c.jml1).label('jumlah1'),
                func.sum(subq1.c.trw1).label('trw1'), func.sum(subq1.c.trw2).label('trw2'),
                func.sum(subq1.c.trw3).label('trw3'), func.sum(subq1.c.trw4).label('trw4')
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)), Rekening.level_id>1
                )\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.tanggal,
                ).order_by(Rekening.kode).all()                    

            generator = r206Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Biaya Terima DPA Lampiran
        elif url_dict['act']=='311' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), KegiatanItem.vol_2_1.label('volume1'), KegiatanItem.sat_2_1.label('satuan1'), 
                 KegiatanItem.vol_2_2.label('volume2'), KegiatanItem.sat_2_2.label('satuan2'), KegiatanItem.hsat_2.label('harga'), 
                 Tahun.tanggal_2.label('tanggal'),                 
                 (KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('anggaran')
                 ).join(Unit).join(Kegiatan).join(Tahun).join(Urusan).join(KegiatanItem).join(Rekening
                 ).filter(Rekening.id==KegiatanItem.rekening_id, KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   Kegiatan.kode=='0.00.00.31'
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r2011Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Biaya Keluar DPA
        elif url_dict['act']=='32' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'), Rekening.level_id.label('lev'),
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.id.label('kegiatan_sub_id'),
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), Tahun.tanggal_2.label('tanggal'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml1'),
                (KegiatanItem.bln01+KegiatanItem.bln02+KegiatanItem.bln03).label('trw1'),
                (KegiatanItem.bln04+KegiatanItem.bln05+KegiatanItem.bln06).label('trw2'),
                (KegiatanItem.bln07+KegiatanItem.bln08+KegiatanItem.bln09).label('trw3'),
                (KegiatanItem.bln10+KegiatanItem.bln11+KegiatanItem.bln12).label('trw4')
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan).join(Tahun
                ).filter(
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode=='0.00.00.32'
                ).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.tanggal,
                func.sum(subq1.c.jml1).label('jumlah1'),
                func.sum(subq1.c.trw1).label('trw1'), func.sum(subq1.c.trw2).label('trw2'),
                func.sum(subq1.c.trw3).label('trw3'), func.sum(subq1.c.trw4).label('trw4')
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)), Rekening.level_id>1
                )\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.tanggal,
                ).order_by(Rekening.kode).all()                    

            generator = r207Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Biaya Keluar DPA Lampiran
        elif url_dict['act']=='321' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), KegiatanItem.vol_2_1.label('volume1'), KegiatanItem.sat_2_1.label('satuan1'), 
                 KegiatanItem.vol_2_2.label('volume2'), KegiatanItem.sat_2_2.label('satuan2'), KegiatanItem.hsat_2.label('harga'), 
                 Tahun.tanggal_2.label('tanggal'),                 
                 (KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('anggaran')
                 ).join(Unit).join(Kegiatan).join(Tahun).join(Urusan).join(KegiatanItem).join(Rekening
                 ).filter(Rekening.id==KegiatanItem.rekening_id, KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   Kegiatan.kode=='0.00.00.32'
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r2011Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

    ######## RPKA
    @view_config(route_name="anggaran_r300", renderer="templates/ag-report/r300.pt", permission="read")
    def anggaran_r300(self):
        params = self.request.params
        return dict(datas=self.datas) 
        #row=KegiatanSub.get_header(self.unit_id, self.keg_id),)

    @view_config(route_name="anggaran_r300_act", renderer="json", permission="read")
    def anggaran_r300_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict
        pk_id = 'id' in params and params['id'] and int(params['id']) or 0
#            keg_id = self.session['keg_id']
        if url_dict['act']=='grid' :
            # defining columns
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('tipe'))
            columns.append(ColumnDT('no_urut'))
            columns.append(ColumnDT("".join(['tolok_ukur_',str(self.status_apbd)])))
            columns.append(ColumnDT("".join(['volume_',str(self.status_apbd)])))
            columns.append(ColumnDT("".join(['satuan_',str(self.status_apbd)])))

            query = DBSession.query(KegiatanIndikator)\
                .join(KegiatanSub)\
                .filter(KegiatanSub.id==keg_id,
                        KegiatanSub.unit_id==self.session['unit_id'])
            rowTable = DataTables(req, KegiatanIndikator, query, columns)
            return rowTable.output_result()

        elif url_dict['act']=='grid2' :
            # defining columns
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('kegiatans.kode'))
            columns.append(ColumnDT('kegiatans.nama'))
            columns.append(ColumnDT('kegiatans.programs.nama'))

            query = DBSession.query(KegiatanSub)\
                .join(Kegiatan).join(Program)\
                .filter(KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        not_(Kegiatan.kode.in_(('0.00.00.10','0.00.00.21','0.00.00.31','0.00.00.41','0.00.00.99'))))
            rowTable = DataTables(req, KegiatanSub, query, columns)
            return rowTable.output_result()

        ## Ringkasan RPKA
        elif url_dict['act']=='0' :
            query = DBSession.query(KegiatanSub.tahun_id,Urusan.kode.label('urusan_kd'),
               Urusan.nama.label('urusan_nm'),Unit.id.label('unit_id'),Unit.kode.label('unit_kd'),
               Unit.nama.label('unit_nm'))\
               .filter(KegiatanSub.unit_id==Unit.id,Unit.urusan_id==Urusan.id,
               KegiatanSub.tahun_id==self.session['tahun'],KegiatanSub.unit_id==self.session['unit_id'])\
               .group_by(KegiatanSub.tahun_id,Urusan.kode,Urusan.nama,Unit.id,Unit.kode,
               Unit.nama)

            generator = r300Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Pendapatan RPKA
        elif url_dict['act']=='1' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'), Rekening.level_id.label('lev'),
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.id.label('kegiatan_sub_id'), KegiatanSub.perubahan,
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), Tahun.tanggal_3.label('tanggal'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml1'),
                (KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml2'),
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan).join(Tahun
                ).filter(
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode=='0.00.00.10'
                ).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.perubahan, subq1.c.tanggal,
                func.sum(subq1.c.jml1).label('jumlah1'),
                func.sum(subq1.c.jml2).label('jumlah2')
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode))
                )\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.perubahan, subq1.c.tanggal,
                ).order_by(Rekening.kode).all()                    

            generator = r301Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Pendapatan RPKA Lampiran
        elif url_dict['act']=='11' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), 
                 Tahun.tanggal_3.label('tanggal'),                 
                 KegiatanItem.vol_2_1.label('volume11'), KegiatanItem.sat_2_1.label('satuan11'), 
                 KegiatanItem.vol_2_2.label('volume12'), KegiatanItem.sat_2_2.label('satuan12'), KegiatanItem.hsat_2.label('harga1'), 
                 (KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('anggaran1'),
                 KegiatanItem.vol_3_1.label('volume21'), KegiatanItem.sat_3_1.label('satuan21'), 
                 KegiatanItem.vol_3_2.label('volume22'), KegiatanItem.sat_3_2.label('satuan22'), KegiatanItem.hsat_3.label('harga2'), 
                 (KegiatanItem.vol_3_1*KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('anggaran2')
                 ).join(Unit).join(Kegiatan).join(Tahun).join(Urusan).join(KegiatanItem).join(Rekening
                 ).filter(Rekening.id==KegiatanItem.rekening_id, KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   Kegiatan.kode=='0.00.00.10'
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r3011Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## BTL RPKA
        elif url_dict['act']=='21' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'), Rekening.level_id.label('lev'),
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.id.label('kegiatan_sub_id'), KegiatanSub.perubahan,
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), Tahun.tanggal_3.label('tanggal'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml1'),
                (KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml2'),
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan).join(Tahun
                ).filter(
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode=='0.00.00.21'
                ).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.perubahan, subq1.c.tanggal,
                func.sum(subq1.c.jml1).label('jumlah1'),
                func.sum(subq1.c.jml2).label('jumlah2')
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode))
                )\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.perubahan, subq1.c.tanggal,
                ).order_by(Rekening.kode).all()                    

            generator = r302Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## BTL RPKA Lampiran
        elif url_dict['act']=='211' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), 
                 Tahun.tanggal_3.label('tanggal'),                 
                 KegiatanItem.vol_2_1.label('volume11'), KegiatanItem.sat_2_1.label('satuan11'), 
                 KegiatanItem.vol_2_2.label('volume12'), KegiatanItem.sat_2_2.label('satuan12'), KegiatanItem.hsat_2.label('harga1'), 
                 (KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('anggaran1'),
                 KegiatanItem.vol_3_1.label('volume21'), KegiatanItem.sat_3_1.label('satuan21'), 
                 KegiatanItem.vol_3_2.label('volume22'), KegiatanItem.sat_3_2.label('satuan22'), KegiatanItem.hsat_3.label('harga2'), 
                 (KegiatanItem.vol_3_1*KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('anggaran2')
                 ).join(Unit).join(Kegiatan).join(Tahun).join(Urusan).join(KegiatanItem).join(Rekening
                 ).filter(Rekening.id==KegiatanItem.rekening_id, KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   Kegiatan.kode=='0.00.00.21'
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r3011Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## ProgKeg RPKA
        elif url_dict['act']=='22' :
            query = DBSession.query(KegiatanSub.tahun_id.label('tahun'), Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'),
                  Unit.id.label('unit_id'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                  Program.kode.label('program_kd'), Program.nama.label('program_nm'), 
                  Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'), 
                  KegiatanSub.lokasi.label('lokasi'), KegiatanSub.target.label('target'), 
                  func.sum(KegiatanItem.vol_1_1*KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('jumlah1'), 
                  func.sum(KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jumlah2'), 
                  func.sum(KegiatanItem.vol_3_1*KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jumlah3'), 
                  func.sum(KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jumlah4')
                  ).join(KegiatanItem).join(Kegiatan).join(Program).join(Unit).join(Urusan
                  ).filter(Urusan.id==Unit.urusan_id, 
                     KegiatanSub.tahun_id==self.session['tahun'],
                     KegiatanSub.unit_id==self.session['unit_id'],
                     not_(Kegiatan.kode.in_(('0.00.00.10', '0.00.00.21', '0.00.00.31','0.00.00.32')))
                  ).group_by(KegiatanSub.tahun_id, Urusan.kode, Urusan.nama,
                  Unit.id, Unit.kode, Unit.nama, Program.kode, Program.nama, 
                  Kegiatan.kode, Kegiatan.nama, KegiatanSub.lokasi, KegiatanSub.target)\
                  .order_by(Urusan.kode, Unit.kode, Program.kode, Kegiatan.kode).all()

            generator = r303Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## BL RPKA
        elif url_dict['act']=='221' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), 
                 Unit.id.label('unit_id'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Program.kode.label('program_kd'), Program.nama.label('program_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.lokasi, KegiatanSub.sasaran, KegiatanSub.sdana, KegiatanSub.id, Tahun.tanggal_3.label('tanggal'),
                 func.sum(KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('anggaran1'),
                 func.sum(KegiatanItem.vol_3_1*KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('anggaran2')
                 ).join(Tahun).join(Unit).join(Kegiatan).join(Program).join(Urusan).join(KegiatanItem)\
                 .filter(KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   KegiatanSub.id==self.request.params['id']
                 ).group_by(KegiatanSub.tahun_id, Urusan.kode, Urusan.nama, 
                 Unit.id, Unit.kode, Unit.nama,
                 Program.kode, Program.nama,
                 Kegiatan.kode, Kegiatan.nama,
                 KegiatanSub.lokasi, KegiatanSub.sasaran, KegiatanSub.sdana, KegiatanSub.id, Tahun.tanggal_3)

            generator = r304Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## BL RPKA Lampiran
        elif url_dict['act']=='2211' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Program.kode.label('program_kd'), Program.nama.label('program_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.lokasi, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), 
                 Tahun.tanggal_3.label('tanggal'),                 
                 KegiatanItem.vol_2_1.label('volume11'), KegiatanItem.sat_2_1.label('satuan11'), 
                 KegiatanItem.vol_2_2.label('volume12'), KegiatanItem.sat_2_2.label('satuan12'), KegiatanItem.hsat_2.label('harga1'), 
                 (KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('anggaran1'),
                 KegiatanItem.vol_3_1.label('volume21'), KegiatanItem.sat_3_1.label('satuan21'), 
                 KegiatanItem.vol_3_2.label('volume22'), KegiatanItem.sat_3_2.label('satuan22'), KegiatanItem.hsat_3.label('harga2'), 
                 (KegiatanItem.vol_3_1*KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('anggaran2')
                 ).filter(Program.id==Kegiatan.program_id, Kegiatan.id==KegiatanSub.kegiatan_id, KegiatanSub.unit_id==Unit.id, 
                   Unit.urusan_id==Urusan.id, KegiatanSub.id==KegiatanItem.kegiatan_sub_id, Rekening.id==KegiatanItem.rekening_id, 
                   Tahun.id==KegiatanSub.tahun_id, KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   KegiatanSub.id==self.request.params['id']
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Program.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r3041Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Biaya RPKA
        elif url_dict['act']=='3' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml2'),
                (KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml3'),
                (KegiatanItem.bln01+KegiatanItem.bln02+KegiatanItem.bln03).label('trw1'),
                (KegiatanItem.bln04+KegiatanItem.bln05+KegiatanItem.bln06).label('trw2'),
                (KegiatanItem.bln07+KegiatanItem.bln08+KegiatanItem.bln09).label('trw3'),
                (KegiatanItem.bln10+KegiatanItem.bln11+KegiatanItem.bln12).label('trw4'),
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'),
                KegiatanSub.perubahan, KegiatanSub.tahun_id.label('tahun')
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan
                ).filter(Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode.in_(('0.00.00.31', '0.00.00.32'))).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.perubahan, 
                func.sum(subq1.c.jml2).label('jumlah2'),
                func.sum(subq1.c.jml3).label('jumlah3'),
                func.sum(subq1.c.trw1).label('trw1'),func.sum(subq1.c.trw2).label('trw2'),
                func.sum(subq1.c.trw3).label('trw3'),func.sum(subq1.c.trw4).label('trw4')
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode))
                ).group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.perubahan)\
                .order_by(Rekening.kode).all()                    

            generator = r305Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Biaya Terima RPKA
        elif url_dict['act']=='31' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'), Rekening.level_id.label('lev'),
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.id.label('kegiatan_sub_id'), KegiatanSub.perubahan,
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), Tahun.tanggal_3.label('tanggal'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml1'),
                (KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml2'),
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan).join(Tahun
                ).filter(
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode=='0.00.00.31'
                ).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.perubahan, subq1.c.tanggal,
                func.sum(subq1.c.jml1).label('jumlah1'),
                func.sum(subq1.c.jml2).label('jumlah2')
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)), Rekening.level_id>1
                )\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.perubahan, subq1.c.tanggal,
                ).order_by(Rekening.kode).all()                    

            generator = r306Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            
            return response

        ## Biaya Terima RPKA Lampiran
        elif url_dict['act']=='311' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), 
                 Tahun.tanggal_3.label('tanggal'),                 
                 KegiatanItem.vol_2_1.label('volume11'), KegiatanItem.sat_2_1.label('satuan11'), 
                 KegiatanItem.vol_2_2.label('volume12'), KegiatanItem.sat_2_2.label('satuan12'), KegiatanItem.hsat_2.label('harga1'), 
                 (KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('anggaran1'),
                 KegiatanItem.vol_3_1.label('volume21'), KegiatanItem.sat_3_1.label('satuan21'), 
                 KegiatanItem.vol_3_2.label('volume22'), KegiatanItem.sat_3_2.label('satuan22'), KegiatanItem.hsat_3.label('harga2'), 
                 (KegiatanItem.vol_3_1*KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('anggaran2')
                 ).join(Unit).join(Kegiatan).join(Tahun).join(Urusan).join(KegiatanItem).join(Rekening
                 ).filter(Rekening.id==KegiatanItem.rekening_id, KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   Kegiatan.kode=='0.00.00.31'
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r3011Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
             
        ## Biaya Keluar
        elif url_dict['act']=='32' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'), Rekening.level_id.label('lev'),
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.id.label('kegiatan_sub_id'), KegiatanSub.perubahan,
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), Tahun.tanggal_3.label('tanggal'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml1'),
                (KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml2'),
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan).join(Tahun
                ).filter(
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode=='0.00.00.32'
                ).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.perubahan, subq1.c.tanggal,
                func.sum(subq1.c.jml1).label('jumlah1'),
                func.sum(subq1.c.jml2).label('jumlah2')
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)), Rekening.level_id>1
                )\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.perubahan, subq1.c.tanggal,
                ).order_by(Rekening.kode).all()                    

            generator = r307Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Biaya Keluar Lampiran
        elif url_dict['act']=='321' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), 
                 Tahun.tanggal_3.label('tanggal'),                 
                 KegiatanItem.vol_2_1.label('volume11'), KegiatanItem.sat_2_1.label('satuan11'), 
                 KegiatanItem.vol_2_2.label('volume12'), KegiatanItem.sat_2_2.label('satuan12'), KegiatanItem.hsat_2.label('harga1'), 
                 (KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('anggaran1'),
                 KegiatanItem.vol_3_1.label('volume21'), KegiatanItem.sat_3_1.label('satuan21'), 
                 KegiatanItem.vol_3_2.label('volume22'), KegiatanItem.sat_3_2.label('satuan22'), KegiatanItem.hsat_3.label('harga2'), 
                 (KegiatanItem.vol_3_1*KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('anggaran2')
                 ).join(Unit).join(Kegiatan).join(Tahun).join(Urusan).join(KegiatanItem).join(Rekening
                 ).filter(Rekening.id==KegiatanItem.rekening_id, KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   Kegiatan.kode=='0.00.00.32'
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r3011Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

    ###### DPPA            
    @view_config(route_name="anggaran_r400", renderer="templates/ag-report/r400.pt", permission="read")
    def anggaran_r400(self):
        params = self.request.params
        return dict(datas=self.datas) 
        #row=KegiatanSub.get_header(self.unit_id, self.keg_id),)

    @view_config(route_name="anggaran_r400_act", renderer="json", permission="read")
    def anggaran_r400_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict
        pk_id = 'id' in params and params['id'] and int(params['id']) or 0
#            keg_id = self.session['keg_id']
        if url_dict['act']=='grid' :
            # defining columns
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('tipe'))
            columns.append(ColumnDT('no_urut'))
            columns.append(ColumnDT("".join(['tolok_ukur_',str(self.status_apbd)])))
            columns.append(ColumnDT("".join(['volume_',str(self.status_apbd)])))
            columns.append(ColumnDT("".join(['satuan_',str(self.status_apbd)])))

            query = DBSession.query(KegiatanIndikator)\
                .join(KegiatanSub)\
                .filter(KegiatanSub.id==keg_id,
                        KegiatanSub.unit_id==self.session['unit_id'])
            rowTable = DataTables(req, KegiatanIndikator, query, columns)
            return rowTable.output_result()

        elif url_dict['act']=='grid2' :
            # defining columns
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('kegiatans.kode'))
            columns.append(ColumnDT('kegiatans.nama'))
            columns.append(ColumnDT('kegiatans.programs.nama'))

            query = DBSession.query(KegiatanSub)\
                .join(Kegiatan).join(Program)\
                .filter(KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        not_(Kegiatan.kode.in_(('0.00.00.10','0.00.00.21','0.00.00.31','0.00.00.41','0.00.00.99'))))
            rowTable = DataTables(req, KegiatanSub, query, columns)
            return rowTable.output_result()

        ## Ringkasan DPPA
        elif url_dict['act']=='0' :
            query = DBSession.query(KegiatanSub.tahun_id,Urusan.kode.label('urusan_kd'),
               Urusan.nama.label('urusan_nm'),Unit.id.label('unit_id'),Unit.kode.label('unit_kd'),
               Unit.nama.label('unit_nm'))\
               .filter(KegiatanSub.unit_id==Unit.id,Unit.urusan_id==Urusan.id,
               KegiatanSub.tahun_id==self.session['tahun'],KegiatanSub.unit_id==self.session['unit_id'])\
               .group_by(KegiatanSub.tahun_id,Urusan.kode,Urusan.nama,Unit.id,Unit.kode,
               Unit.nama)

            generator = r400Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Pendapatan DPPA
        elif url_dict['act']=='1' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'), Rekening.level_id.label('lev'),
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.id.label('kegiatan_sub_id'), KegiatanSub.perubahan,
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), Tahun.tanggal_4.label('tanggal'),
                (KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml1'),
                (KegiatanItem.vol_4_1* KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jml2'),
                (KegiatanItem.bln01+KegiatanItem.bln02+KegiatanItem.bln03).label('trw1'),
                (KegiatanItem.bln04+KegiatanItem.bln05+KegiatanItem.bln06).label('trw2'),
                (KegiatanItem.bln07+KegiatanItem.bln08+KegiatanItem.bln09).label('trw3'),
                (KegiatanItem.bln10+KegiatanItem.bln11+KegiatanItem.bln12).label('trw4')
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan).join(Tahun
                ).filter(
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode=='0.00.00.10'
                ).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.perubahan, subq1.c.tanggal,
                func.sum(subq1.c.jml1).label('jumlah1'),
                func.sum(subq1.c.jml2).label('jumlah2'),
                func.sum(subq1.c.trw1).label('trw1'), func.sum(subq1.c.trw2).label('trw2'),
                func.sum(subq1.c.trw3).label('trw3'), func.sum(subq1.c.trw4).label('trw4'),
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode))
                )\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.perubahan, subq1.c.tanggal,
                ).order_by(Rekening.kode).all()                    

            generator = r401Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Pendapatan DPPA Lampiran
        elif url_dict['act']=='11' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), 
                 Tahun.tanggal_4.label('tanggal'),                 
                 KegiatanItem.vol_3_1.label('volume11'), KegiatanItem.sat_3_1.label('satuan11'), 
                 KegiatanItem.vol_3_2.label('volume12'), KegiatanItem.sat_3_2.label('satuan12'), KegiatanItem.hsat_3.label('harga1'), 
                 (KegiatanItem.vol_3_1*KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('anggaran1'),
                 KegiatanItem.vol_4_1.label('volume21'), KegiatanItem.sat_4_1.label('satuan21'), 
                 KegiatanItem.vol_4_2.label('volume22'), KegiatanItem.sat_4_2.label('satuan22'), KegiatanItem.hsat_4.label('harga2'), 
                 (KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('anggaran2')
                 ).join(Unit).join(Kegiatan).join(Tahun).join(Urusan).join(KegiatanItem).join(Rekening
                 ).filter(Rekening.id==KegiatanItem.rekening_id, KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   Kegiatan.kode=='0.00.00.10'
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r4011Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## BTL DPPA
        elif url_dict['act']=='21' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'), Rekening.level_id.label('lev'),
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.id.label('kegiatan_sub_id'), KegiatanSub.perubahan,
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), Tahun.tanggal_4.label('tanggal'),
                (KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml1'),
                (KegiatanItem.vol_4_1* KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jml2'),
                (KegiatanItem.bln01+KegiatanItem.bln02+KegiatanItem.bln03).label('trw1'),
                (KegiatanItem.bln04+KegiatanItem.bln05+KegiatanItem.bln06).label('trw2'),
                (KegiatanItem.bln07+KegiatanItem.bln08+KegiatanItem.bln09).label('trw3'),
                (KegiatanItem.bln10+KegiatanItem.bln11+KegiatanItem.bln12).label('trw4')
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan).join(Tahun
                ).filter(
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode=='0.00.00.21'
                ).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.perubahan, subq1.c.tanggal,
                func.sum(subq1.c.jml1).label('jumlah1'),
                func.sum(subq1.c.jml2).label('jumlah2'),
                func.sum(subq1.c.trw1).label('trw1'), func.sum(subq1.c.trw2).label('trw2'),
                func.sum(subq1.c.trw3).label('trw3'), func.sum(subq1.c.trw4).label('trw4'),
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode))
                )\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.perubahan, subq1.c.tanggal,
                ).order_by(Rekening.kode).all()                    

            generator = r402Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## BTL DPPA Lampiran
        elif url_dict['act']=='211' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), 
                 Tahun.tanggal_4.label('tanggal'),                 
                 KegiatanItem.vol_3_1.label('volume11'), KegiatanItem.sat_3_1.label('satuan11'), 
                 KegiatanItem.vol_3_2.label('volume12'), KegiatanItem.sat_3_2.label('satuan12'), KegiatanItem.hsat_3.label('harga1'), 
                 (KegiatanItem.vol_3_1*KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('anggaran1'),
                 KegiatanItem.vol_4_1.label('volume21'), KegiatanItem.sat_4_1.label('satuan21'), 
                 KegiatanItem.vol_4_2.label('volume22'), KegiatanItem.sat_4_2.label('satuan22'), KegiatanItem.hsat_4.label('harga2'), 
                 (KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('anggaran2')
                 ).join(Unit).join(Kegiatan).join(Tahun).join(Urusan).join(KegiatanItem).join(Rekening
                 ).filter(Rekening.id==KegiatanItem.rekening_id, KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   Kegiatan.kode=='0.00.00.21'
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r4011Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## ProgKeg DPPA
        elif url_dict['act']=='22' :
            query = DBSession.query(KegiatanSub.tahun_id.label('tahun'), Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'),
                  Unit.id.label('unit_id'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                  Program.kode.label('program_kd'), Program.nama.label('program_nm'), 
                  Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'), 
                  KegiatanSub.lokasi.label('lokasi'), KegiatanSub.target.label('target'), 
                  func.sum(KegiatanItem.vol_3_1*KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jumlah3'), 
                  func.sum(KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jumlah4')
                  ).join(KegiatanItem).join(Kegiatan).join(Program).join(Unit).join(Urusan
                  ).filter(Urusan.id==Unit.urusan_id, 
                     KegiatanSub.tahun_id==self.session['tahun'],
                     KegiatanSub.unit_id==self.session['unit_id'],
                     not_(Kegiatan.kode.in_(('0.00.00.10', '0.00.00.21', '0.00.00.31','0.00.00.32')))
                  ).group_by(KegiatanSub.tahun_id, Urusan.kode, Urusan.nama,
                  Unit.id, Unit.kode, Unit.nama, Program.kode, Program.nama, 
                  Kegiatan.kode, Kegiatan.nama, KegiatanSub.lokasi, KegiatanSub.target)\
                  .order_by(Urusan.kode, Unit.kode, Program.kode, Kegiatan.kode).all()

            generator = r403Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## BL DPPA
        elif url_dict['act']=='221' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), 
                 Unit.id.label('unit_id'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Program.kode.label('program_kd'), Program.nama.label('program_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.lokasi, KegiatanSub.sasaran, KegiatanSub.sdana, KegiatanSub.id, Tahun.tanggal_4.label('tanggal'),
                 func.sum(KegiatanItem.vol_3_1*KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('anggaran1'),
                 func.sum(KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('anggaran2')
                 ).join(Tahun).join(Unit).join(Kegiatan).join(Program).join(Urusan).join(KegiatanItem)\
                 .filter(KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   KegiatanSub.id==self.request.params['id']
                 ).group_by(KegiatanSub.tahun_id, Urusan.kode, Urusan.nama, 
                 Unit.id, Unit.kode, Unit.nama,
                 Program.kode, Program.nama,
                 Kegiatan.kode, Kegiatan.nama,
                 KegiatanSub.lokasi, KegiatanSub.sasaran, KegiatanSub.sdana, KegiatanSub.id, Tahun.tanggal_4)

            generator = r404Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## BL DPPA Lampiran
        elif url_dict['act']=='2211' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Program.kode.label('program_kd'), Program.nama.label('program_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.lokasi, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), 
                 Tahun.tanggal_4.label('tanggal'),                 
                 KegiatanItem.vol_3_1.label('volume11'), KegiatanItem.sat_3_1.label('satuan11'), 
                 KegiatanItem.vol_3_2.label('volume12'), KegiatanItem.sat_3_2.label('satuan12'), KegiatanItem.hsat_3.label('harga1'), 
                 (KegiatanItem.vol_3_1*KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('anggaran1'),
                 KegiatanItem.vol_4_1.label('volume21'), KegiatanItem.sat_4_1.label('satuan21'), 
                 KegiatanItem.vol_4_2.label('volume22'), KegiatanItem.sat_4_2.label('satuan22'), KegiatanItem.hsat_2.label('harga2'), 
                 (KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('anggaran2')
                 ).filter(Program.id==Kegiatan.program_id, Kegiatan.id==KegiatanSub.kegiatan_id, KegiatanSub.unit_id==Unit.id, 
                   Unit.urusan_id==Urusan.id, KegiatanSub.id==KegiatanItem.kegiatan_sub_id, Rekening.id==KegiatanItem.rekening_id, 
                   Tahun.id==KegiatanSub.tahun_id, KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   KegiatanSub.id==self.request.params['id']
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Program.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r4041Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Biaya DPPA
        elif url_dict['act']=='3' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                (KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml3'),
                (KegiatanItem.vol_4_1* KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jml4'),
                (KegiatanItem.bln01+KegiatanItem.bln02+KegiatanItem.bln03).label('trw1'),
                (KegiatanItem.bln04+KegiatanItem.bln05+KegiatanItem.bln06).label('trw2'),
                (KegiatanItem.bln07+KegiatanItem.bln08+KegiatanItem.bln09).label('trw3'),
                (KegiatanItem.bln10+KegiatanItem.bln11+KegiatanItem.bln12).label('trw4'),
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'),
                KegiatanSub.perubahan, KegiatanSub.tahun_id.label('tahun')
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan
                ).filter(Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode.in_(('0.00.00.31', '0.00.00.32'))).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.perubahan, 
                func.sum(subq1.c.jml3).label('jumlah3'),func.sum(subq1.c.jml4).label('jumlah4'),
                func.sum(subq1.c.trw1).label('trw1'),func.sum(subq1.c.trw2).label('trw2'),
                func.sum(subq1.c.trw3).label('trw3'),func.sum(subq1.c.trw4).label('trw4'))\
                .filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)))\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.perubahan)\
                .order_by(Rekening.kode).all()                    

            generator = r405Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Biaya Terima DPPA
        elif url_dict['act']=='31' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'), Rekening.level_id.label('lev'),
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.id.label('kegiatan_sub_id'), KegiatanSub.perubahan,
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), Tahun.tanggal_4.label('tanggal'),
                (KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml1'),
                (KegiatanItem.vol_4_1* KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jml2'),
                (KegiatanItem.bln01+KegiatanItem.bln02+KegiatanItem.bln03).label('trw1'),
                (KegiatanItem.bln04+KegiatanItem.bln05+KegiatanItem.bln06).label('trw2'),
                (KegiatanItem.bln07+KegiatanItem.bln08+KegiatanItem.bln09).label('trw3'),
                (KegiatanItem.bln10+KegiatanItem.bln11+KegiatanItem.bln12).label('trw4')
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan).join(Tahun
                ).filter(
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode=='0.00.00.31'
                ).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.perubahan, subq1.c.tanggal,
                func.sum(subq1.c.jml1).label('jumlah1'),
                func.sum(subq1.c.jml2).label('jumlah2'),
                func.sum(subq1.c.trw1).label('trw1'), func.sum(subq1.c.trw2).label('trw2'),
                func.sum(subq1.c.trw3).label('trw3'), func.sum(subq1.c.trw4).label('trw4'),
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)), Rekening.level_id>1
                )\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.perubahan, subq1.c.tanggal,
                ).order_by(Rekening.kode).all()                    

            generator = r406Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Biaya Terima DPPA Lampiran
        elif url_dict['act']=='311' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), 
                 Tahun.tanggal_4.label('tanggal'),                 
                 KegiatanItem.vol_3_1.label('volume11'), KegiatanItem.sat_3_1.label('satuan11'), 
                 KegiatanItem.vol_3_2.label('volume12'), KegiatanItem.sat_3_2.label('satuan12'), KegiatanItem.hsat_3.label('harga1'), 
                 (KegiatanItem.vol_3_1*KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('anggaran1'),
                 KegiatanItem.vol_4_1.label('volume21'), KegiatanItem.sat_4_1.label('satuan21'), 
                 KegiatanItem.vol_4_2.label('volume22'), KegiatanItem.sat_4_2.label('satuan22'), KegiatanItem.hsat_4.label('harga2'), 
                 (KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('anggaran2')
                 ).join(Unit).join(Kegiatan).join(Tahun).join(Urusan).join(KegiatanItem).join(Rekening
                 ).filter(Rekening.id==KegiatanItem.rekening_id, KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   Kegiatan.kode=='0.00.00.31'
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r4011Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Biaya Keluar DPPA
        elif url_dict['act']=='32' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'), Rekening.level_id.label('lev'),
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.id.label('kegiatan_sub_id'), KegiatanSub.perubahan,
                Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), Tahun.tanggal_4.label('tanggal'),
                (KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml1'),
                (KegiatanItem.vol_4_1* KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jml2'),
                (KegiatanItem.bln01+KegiatanItem.bln02+KegiatanItem.bln03).label('trw1'),
                (KegiatanItem.bln04+KegiatanItem.bln05+KegiatanItem.bln06).label('trw2'),
                (KegiatanItem.bln07+KegiatanItem.bln08+KegiatanItem.bln09).label('trw3'),
                (KegiatanItem.bln10+KegiatanItem.bln11+KegiatanItem.bln12).label('trw4')
                ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan).join(Unit).join(Urusan).join(Tahun
                ).filter(
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'],
                        Kegiatan.kode=='0.00.00.32'
                ).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.perubahan, subq1.c.tanggal,
                func.sum(subq1.c.jml1).label('jumlah1'),
                func.sum(subq1.c.jml2).label('jumlah2'),
                func.sum(subq1.c.trw1).label('trw1'), func.sum(subq1.c.trw2).label('trw2'),
                func.sum(subq1.c.trw3).label('trw3'), func.sum(subq1.c.trw4).label('trw4'),
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)), Rekening.level_id>1
                )\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.urusan_kd, subq1.c.urusan_nm,
                subq1.c.unit_kd, subq1.c.unit_nm, subq1.c.tahun, subq1.c.kegiatan_sub_id, subq1.c.perubahan, subq1.c.tanggal,
                ).order_by(Rekening.kode).all()                    

            generator = r407Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Biaya Keluar DPPA Lampiran
        elif url_dict['act']=='321' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
                 Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                 Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                 KegiatanSub.sdana, KegiatanSub.id,
                 Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                 KegiatanItem.no_urut, KegiatanItem.nama.label('item_nm'), 
                 Tahun.tanggal_4.label('tanggal'),                 
                 KegiatanItem.vol_3_1.label('volume11'), KegiatanItem.sat_3_1.label('satuan11'), 
                 KegiatanItem.vol_3_2.label('volume12'), KegiatanItem.sat_3_2.label('satuan12'), KegiatanItem.hsat_3.label('harga1'), 
                 (KegiatanItem.vol_3_1*KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('anggaran1'),
                 KegiatanItem.vol_4_1.label('volume21'), KegiatanItem.sat_4_1.label('satuan21'), 
                 KegiatanItem.vol_4_2.label('volume22'), KegiatanItem.sat_4_2.label('satuan22'), KegiatanItem.hsat_4.label('harga2'), 
                 (KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('anggaran2')
                 ).join(Unit).join(Kegiatan).join(Tahun).join(Urusan).join(KegiatanItem).join(Rekening
                 ).filter(Rekening.id==KegiatanItem.rekening_id, KegiatanSub.tahun_id==self.session['tahun'],
                   KegiatanSub.unit_id==self.session['unit_id'], 
                   Kegiatan.kode=='0.00.00.32'
                 ).order_by(KegiatanSub.tahun_id, Urusan.kode, Unit.kode, Kegiatan.kode, KegiatanSub.id, Rekening.kode, KegiatanItem.no_urut)

            generator = r4011Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

    ###### APBD            
    @view_config(route_name="anggaran_r500", renderer="templates/ag-report/r500.pt", permission="read")
    def anggaran_r500(self):
        params = self.request.params
        return dict(datas=self.datas,)

    @view_config(route_name="anggaran_r500_act")
    def anggaran_r500_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        ## Ringkasan APBD
        if url_dict['act']=='r511' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                KegiatanSub.tahun_id,
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml2')
                ).filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                        KegiatanItem.rekening_id==Rekening.id,
                        KegiatanSub.tahun_id==self.session['tahun']).subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.tahun_id, 
                func.sum(subq1.c.jml2).label('jumlah2')
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)),
                Rekening.level_id<4
                ).group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.tahun_id
                ).order_by(Rekening.kode).all()                    

            generator = r500Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
           
        ## Ringkasan DPPA (Rincian Objek)
        elif url_dict['act']=='r5111' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                KegiatanSub.tahun_id,
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml2')
                ).filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                        KegiatanItem.rekening_id==Rekening.id,
                        KegiatanSub.tahun_id==self.session['tahun'])\
                .subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.tahun_id, 
                func.sum(subq1.c.jml2).label('jumlah2')
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode))
                ).group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.tahun_id)\
                .order_by(Rekening.kode).all()                    

            generator = r5001Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Rekap per SKPD
        elif url_dict['act']=='r512' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
               Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
               Kegiatan.kode.label('jenis_kd'), 
               (KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jumlah2')
               ).join(Unit).join(Urusan).join(KegiatanItem).join(Kegiatan).join(Program
               ).filter(Unit.urusan_id==Urusan.id, not_(Kegiatan.kode.in_(('0.00.00.31','0.00.00.32'))),
               KegiatanSub.tahun_id==self.session['tahun'])      

            generator = r501Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Rincian APBD
        elif url_dict['act']=='r513' :
            subq = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml2'),
                Unit.id.label('unit_id'),Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), 
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.lokasi, KegiatanSub.sdana, 
                Program.kode.label('program_kd'), Program.nama.label('program_nm'), 
                Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                KegiatanItem.kegiatan_sub_id, KegiatanSub.kegiatan_id )\
                .filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                        KegiatanItem.rekening_id==Rekening.id,
                        KegiatanSub.unit_id==Unit.id,
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.kegiatan_id==Kegiatan.id,
                        Kegiatan.program_id==Program.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'])\
                .subquery()
                
            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, Rekening.id.label('rekening_id'),
                subq.c.unit_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.urusan_kd, subq.c.urusan_nm, 
                subq.c.tahun, subq.c.lokasi, subq.c.sdana,
                subq.c.program_kd, subq.c.program_nm, subq.c.kegiatan_kd, subq.c.kegiatan_nm, 
                subq.c.kegiatan_sub_id,  subq.c.kegiatan_id, 
                case([(subq.c.kegiatan_kd=='0.00.00.10',1),(subq.c.kegiatan_kd=='0.00.00.21',2),
                (subq.c.kegiatan_kd=='0.00.00.31',4),(subq.c.kegiatan_kd=='0.00.00.32',5)], 
                else_=3).label('jenis'),                    
                func.sum(subq.c.jml2).label('jumlah2')                
                ).filter(Rekening.kode==func.left(subq.c.subrek_kd, func.length(Rekening.kode))
                ).group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, Rekening.id, 
                subq.c.unit_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.urusan_kd, subq.c.urusan_nm, subq.c.tahun,
                subq.c.lokasi, subq.c.sdana, subq.c.program_kd, subq.c.program_nm, subq.c.kegiatan_kd, subq.c.kegiatan_nm,
                subq.c.kegiatan_sub_id, subq.c.kegiatan_id,
                case([(subq.c.kegiatan_kd=='0.00.00.10',1),(subq.c.kegiatan_kd=='0.00.00.21',2),
                (subq.c.kegiatan_kd=='0.00.00.31',4),(subq.c.kegiatan_kd=='0.00.00.32',5)], 
                else_=3)
                ).order_by(case([(subq.c.kegiatan_kd=='0.00.00.10',1),(subq.c.kegiatan_kd=='0.00.00.21',2),
                (subq.c.kegiatan_kd=='0.00.00.31',4),(subq.c.kegiatan_kd=='0.00.00.32',5)], 
                else_=3), subq.c.urusan_kd, subq.c.unit_kd, subq.c.program_kd, subq.c.kegiatan_kd, Rekening.kode).all() 
                
            generator = r502Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
            
        ## ProgKeg APBD
        elif url_dict['act']=='r514' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
               Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
               Program.kode.label('program_kd'), Program.nama.label('program_nm'), 
               Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
               func.substr(Rekening.kode,0,6).label('kode'),
               func.sum(KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jumlah')
               ).filter(KegiatanItem.rekening_id==Rekening.id, KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                KegiatanSub.unit_id==Unit.id, Unit.urusan_id==Urusan.id, 
                KegiatanSub.kegiatan_id==Kegiatan.id,
                Kegiatan.program_id==Program.id,
                KegiatanSub.tahun_id==self.session['tahun'],
                not_(Kegiatan.kode.in_(('0.00.00.10','0.00.00.21','0.00.00.31','0.00.00.32')))
               ).group_by(KegiatanSub.tahun_id, Urusan.kode, Urusan.nama, 
               Unit.kode, Unit.nama, Program.kode, Program.nama, 
               Kegiatan.kode, Kegiatan.nama,func.substr(Rekening.kode,0,6))                    
                
            generator = r503Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Urusan Fungsi APBD
        elif url_dict['act']=='r515' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
               Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
               Program.kode.label('program_kd'), Program.nama.label('program_nm'),
               Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
               func.sum(case([(func.substr(Rekening.kode,1,5)=='5.1.1',(KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2))], else_=0)).label('jml_btlpeg'),
               func.sum(case([(and_(func.substr(Rekening.kode,1,3)=='5.1',func.substr(Rekening.kode,1,5)!='5.1.1'),(KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2))], else_=0)).label('jml_btlnonpeg'),
               func.sum(case([(func.substr(Rekening.kode,1,5)=='5.2.1',(KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2))], else_=0)).label('jml_blpeg'),
               func.sum(case([(func.substr(Rekening.kode,1,5)=='5.2.2',(KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2))], else_=0)).label('jml_bljasa'),
               func.sum(case([(func.substr(Rekening.kode,1,5)=='5.2.3',(KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2))], else_=0)).label('jml_blmodal')
               ).filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                   KegiatanSub.kegiatan_id==Kegiatan.id, Kegiatan.program_id==Program.id,
                   Program.urusan_id==Urusan.id, KegiatanSub.unit_id==Unit.id, 
                   KegiatanItem.rekening_id==Rekening.id,
                   KegiatanSub.tahun_id==self.session['tahun']
               ).group_by(KegiatanSub.tahun_id, Urusan.kode,
               Urusan.nama, Unit.kode, Unit.nama,
               Program.kode, Program.nama,
               Kegiatan.kode, Kegiatan.nama)

            generator = r504Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Ringkasan Perda APBD
        elif url_dict['act']=='r521' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                KegiatanSub.tahun_id,
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml2')
                ).filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                        KegiatanItem.rekening_id==Rekening.id,
                        KegiatanSub.tahun_id==self.session['tahun'])\
                .subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.tahun_id, 
                func.sum(subq1.c.jml2).label('jumlah2')
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)),
                Rekening.level_id<4)\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.tahun_id)\
                .order_by(Rekening.kode).all()                    

            generator = r521Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Ringkasan Perda APBD (Rincian Objek)
        elif url_dict['act']=='r5211' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                KegiatanSub.tahun_id,
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml2')
                ).filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                        KegiatanItem.rekening_id==Rekening.id,
                        KegiatanSub.tahun_id==self.session['tahun'])\
                .subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.tahun_id, 
                func.sum(subq1.c.jml2).label('jumlah2')
                ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)))\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.tahun_id)\
                .order_by(Rekening.kode).all()                    

            generator = r5211Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Rincian Perda APBD 
        elif url_dict['act']=='r522' :
            subq = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml2'),
                Unit.id.label('unit_id'),Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), 
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.lokasi, KegiatanSub.sdana, 
                Program.kode.label('program_kd'), Program.nama.label('program_nm'), 
                Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                KegiatanItem.kegiatan_sub_id, KegiatanSub.kegiatan_id )\
                .filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                        KegiatanItem.rekening_id==Rekening.id,
                        KegiatanSub.unit_id==Unit.id,
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.kegiatan_id==Kegiatan.id,
                        Kegiatan.program_id==Program.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'])\
                .subquery()
                
            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, Rekening.id.label('rekening_id'),
                subq.c.unit_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.urusan_kd, subq.c.urusan_nm, 
                subq.c.tahun, subq.c.lokasi, subq.c.sdana,
                subq.c.program_kd, subq.c.program_nm, subq.c.kegiatan_kd, subq.c.kegiatan_nm, 
                subq.c.kegiatan_sub_id,  subq.c.kegiatan_id,
                case([(subq.c.kegiatan_kd=='0.00.00.10',1),(subq.c.kegiatan_kd=='0.00.00.21',2),
                (subq.c.kegiatan_kd=='0.00.00.31',4),(subq.c.kegiatan_kd=='0.00.00.32',5)], 
                else_=3).label('jenis'),                    
                func.sum(subq.c.jml2).label('jumlah2')
                ).filter(Rekening.kode==func.left(subq.c.subrek_kd, func.length(Rekening.kode)))\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, Rekening.id, 
                subq.c.unit_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.urusan_kd, subq.c.urusan_nm, subq.c.tahun,
                subq.c.lokasi, subq.c.sdana, subq.c.program_kd, subq.c.program_nm, subq.c.kegiatan_kd, subq.c.kegiatan_nm,
                subq.c.kegiatan_sub_id, subq.c.kegiatan_id,
                case([(subq.c.kegiatan_kd=='0.00.00.10',1),(subq.c.kegiatan_kd=='0.00.00.21',2),
                (subq.c.kegiatan_kd=='0.00.00.31',4),(subq.c.kegiatan_kd=='0.00.00.32',5)], 
                else_=3))\
                .order_by(case([(subq.c.kegiatan_kd=='0.00.00.10',1),(subq.c.kegiatan_kd=='0.00.00.21',2),
                (subq.c.kegiatan_kd=='0.00.00.31',4),(subq.c.kegiatan_kd=='0.00.00.32',5)], 
                else_=3),subq.c.urusan_kd, subq.c.unit_kd, subq.c.program_kd, subq.c.kegiatan_kd, Rekening.kode).all() 
                
            generator = r522Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

    ###### PERUBAHAN APBD            
    @view_config(route_name="anggaran_r600", renderer="templates/ag-report/r600.pt", permission="read")
    def anggaran_r600(self):
        params = self.request.params
        return dict(datas=self.datas,)

    @view_config(route_name="anggaran_r600_act")
    def anggaran_r600_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        ## Ringkasan Perubahan APBD 
        if url_dict['act']=='r611' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                KegiatanSub.tahun_id,
                (KegiatanItem.vol_1_1* KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('jml1'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml2'),
                (KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml3'),
                (KegiatanItem.vol_4_1* KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jml4'))\
                .filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                        KegiatanItem.rekening_id==Rekening.id,
                        KegiatanSub.tahun_id==self.session['tahun'])\
                .subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.tahun_id, 
                func.sum(subq1.c.jml1).label('jumlah1'),func.sum(subq1.c.jml2).label('jumlah2'),
                func.sum(subq1.c.jml3).label('jumlah3'),func.sum(subq1.c.jml4).label('jumlah4'))\
                .filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)),
                Rekening.level_id<4)\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.tahun_id)\
                .order_by(Rekening.kode).all()                    

            generator = r600Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
           
        ## Ringkasan Perubahan APBD (Rincian Objek)
        elif url_dict['act']=='r6111' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                KegiatanSub.tahun_id,
                (KegiatanItem.vol_1_1* KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('jml1'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml2'),
                (KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml3'),
                (KegiatanItem.vol_4_1* KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jml4'))\
                .filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                        KegiatanItem.rekening_id==Rekening.id,
                        KegiatanSub.tahun_id==self.session['tahun'])\
                .subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.tahun_id, 
                func.sum(subq1.c.jml1).label('jumlah1'),func.sum(subq1.c.jml2).label('jumlah2'),
                func.sum(subq1.c.jml3).label('jumlah3'),func.sum(subq1.c.jml4).label('jumlah4'))\
                .filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)))\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.tahun_id)\
                .order_by(Rekening.kode).all()                    

            generator = r6001Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Rekap per SKPD Perubahan APBD 
        elif url_dict['act']=='r612' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
               Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
               KegiatanSub.kegiatan_id.label('jenis_kd'), 
               (KegiatanItem.vol_1_1*KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('jumlah1'),
               (KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jumlah2'),
               (KegiatanItem.vol_3_1*KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jumlah3'),
               (KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jumlah4'))\
               .filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                   KegiatanSub.kegiatan_id==Kegiatan.id, Kegiatan.program_id==Program.id,
                   Program.urusan_id==Urusan.id, KegiatanSub.unit_id==Unit.id,
                   KegiatanSub.tahun_id==self.session['tahun'])      

            generator = r601Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Rincian Perubahan APBD 
        elif url_dict['act']=='r613' :
            subq = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                (KegiatanItem.vol_1_1* KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('jml1'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml2'),
                (KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml3'),
                (KegiatanItem.vol_4_1* KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jml4'),
                Unit.id.label('unit_id'),Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), 
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.lokasi, KegiatanSub.sdana, 
                Program.kode.label('program_kd'), Program.nama.label('program_nm'), 
                Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                KegiatanItem.kegiatan_sub_id, KegiatanSub.kegiatan_id )\
                .filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                        KegiatanItem.rekening_id==Rekening.id,
                        KegiatanSub.unit_id==Unit.id,
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.kegiatan_id==Kegiatan.id,
                        Kegiatan.program_id==Program.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'])\
                .subquery()
                
            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, Rekening.id.label('rekening_id'),
                subq.c.unit_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.urusan_kd, subq.c.urusan_nm, 
                subq.c.tahun, subq.c.lokasi, subq.c.sdana,
                subq.c.program_kd, subq.c.program_nm, subq.c.kegiatan_kd, subq.c.kegiatan_nm, 
                subq.c.kegiatan_sub_id,  subq.c.kegiatan_id,
                case([(subq.c.kegiatan_kd=='0.00.00.10',1),(subq.c.kegiatan_kd=='0.00.00.21',2),
                (subq.c.kegiatan_kd=='0.00.00.31',4),(subq.c.kegiatan_kd=='0.00.00.32',5)], 
                else_=3).label('jenis'),                    
                func.sum(subq.c.jml1).label('jumlah1'),func.sum(subq.c.jml2).label('jumlah2'),
                func.sum(subq.c.jml3).label('jumlah3'),func.sum(subq.c.jml4).label('jumlah4'))\
                .filter(Rekening.kode==func.left(subq.c.subrek_kd, func.length(Rekening.kode)))\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, Rekening.id, 
                subq.c.unit_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.urusan_kd, subq.c.urusan_nm, subq.c.tahun,
                subq.c.lokasi, subq.c.sdana, subq.c.program_kd, subq.c.program_nm, subq.c.kegiatan_kd, subq.c.kegiatan_nm,
                subq.c.kegiatan_sub_id, subq.c.kegiatan_id,
                case([(subq.c.kegiatan_kd=='0.00.00.10',1),(subq.c.kegiatan_kd=='0.00.00.21',2),
                (subq.c.kegiatan_kd=='0.00.00.31',4),(subq.c.kegiatan_kd=='0.00.00.32',5)], 
                else_=3))\
                .order_by(case([(subq.c.kegiatan_kd=='0.00.00.10',1),(subq.c.kegiatan_kd=='0.00.00.21',2),
                (subq.c.kegiatan_kd=='0.00.00.31',4),(subq.c.kegiatan_kd=='0.00.00.32',5)], 
                else_=3),subq.c.urusan_kd, subq.c.unit_kd, subq.c.program_kd, subq.c.kegiatan_kd, Rekening.kode).all() 
                
            generator = r602Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## ProgKeg Perubahan APBD 
        elif url_dict['act']=='r614' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
               Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
               Program.kode.label('program_kd'), Program.nama.label('program_nm'), 
               Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
               func.sum(case([(func.substr(Rekening.kode,0,6)=='5.2.1',
               KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2)], else_=0)).label('pegawai1'),
               func.sum(case([(func.substr(Rekening.kode,0,6)=='5.2.2',
               KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2)], else_=0)).label('jasa1'),
               func.sum(case([(func.substr(Rekening.kode,0,6)=='5.2.3',
               KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2)], else_=0)).label('modal1'),
               func.sum(case([(func.substr(Rekening.kode,0,6)=='5.2.1',
               KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4)], else_=0)).label('pegawai2'),
               func.sum(case([(func.substr(Rekening.kode,0,6)=='5.2.2',
               KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4)], else_=0)).label('jasa2'),
               func.sum(case([(func.substr(Rekening.kode,0,6)=='5.2.3',
               KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4)], else_=0)).label('modal2'))\
               .filter(KegiatanItem.rekening_id==Rekening.id, KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                KegiatanSub.unit_id==Unit.id, Unit.urusan_id==Urusan.id, 
                KegiatanSub.kegiatan_id==Kegiatan.id,
                Kegiatan.program_id==Program.id,
                KegiatanSub.tahun_id==self.session['tahun'],
                not_(Kegiatan.kode.in_(('0.00.00.10','0.00.00.21','0.00.00.31','0.00.00.32')))
               ).group_by(KegiatanSub.tahun_id, Urusan.kode, Urusan.nama, 
               Unit.kode, Unit.nama, Program.kode, Program.nama, 
               Kegiatan.kode, Kegiatan.nama)                    
                
            generator = r603Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Urusan Fungsi Perubahan APBD 
        elif url_dict['act']=='r615' :
            query = DBSession.query(KegiatanSub.tahun_id, Urusan.kode.label('urusan_kd'),
               Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
               Program.kode.label('program_kd'), Program.nama.label('program_nm'),
               Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
               func.sum(case([(func.substr(Rekening.kode,1,5)=='5.1.1',(KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2))], else_=0)).label('jml_btlpeg1'),
               func.sum(case([(and_(func.substr(Rekening.kode,1,3)=='5.1',func.substr(Rekening.kode,1,5)!='5.1.1'),(KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2))], else_=0)).label('jml_btlnonpeg1'),
               func.sum(case([(func.substr(Rekening.kode,1,5)=='5.2.1',(KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2))], else_=0)).label('jml_blpeg1'),
               func.sum(case([(func.substr(Rekening.kode,1,5)=='5.2.2',(KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2))], else_=0)).label('jml_bljasa1'),
               func.sum(case([(func.substr(Rekening.kode,1,5)=='5.2.3',(KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2))], else_=0)).label('jml_blmodal1'),
               func.sum(case([(func.substr(Rekening.kode,1,5)=='5.1.1',(KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4))], else_=0)).label('jml_btlpeg2'),
               func.sum(case([(and_(func.substr(Rekening.kode,1,3)=='5.1',func.substr(Rekening.kode,1,5)!='5.1.1'),(KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4))], else_=0)).label('jml_btlnonpeg2'),
               func.sum(case([(func.substr(Rekening.kode,1,5)=='5.2.1',(KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4))], else_=0)).label('jml_blpeg2'),
               func.sum(case([(func.substr(Rekening.kode,1,5)=='5.2.2',(KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4))], else_=0)).label('jml_bljasa2'),
               func.sum(case([(func.substr(Rekening.kode,1,5)=='5.2.3',(KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4))], else_=0)).label('jml_blmodal2')
               ).filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                   KegiatanSub.kegiatan_id==Kegiatan.id, Kegiatan.program_id==Program.id,
                   Program.urusan_id==Urusan.id, KegiatanSub.unit_id==Unit.id, 
                   KegiatanItem.rekening_id==Rekening.id,
                   KegiatanSub.tahun_id==self.session['tahun']
               ).group_by(KegiatanSub.tahun_id, Urusan.kode,
               Urusan.nama, Unit.kode, Unit.nama,
               Program.kode, Program.nama,
               Kegiatan.kode, Kegiatan.nama)

            generator = r604Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Ringkasan Perda Perubahan APBD 
        elif url_dict['act']=='r621' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                KegiatanSub.tahun_id,
                (KegiatanItem.vol_1_1* KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('jml1'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml2'),
                (KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml3'),
                (KegiatanItem.vol_4_1* KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jml4'))\
                .filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                        KegiatanItem.rekening_id==Rekening.id,
                        KegiatanSub.tahun_id==self.session['tahun'])\
                .subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.tahun_id, 
                func.sum(subq1.c.jml1).label('jumlah1'),func.sum(subq1.c.jml2).label('jumlah2'),
                func.sum(subq1.c.jml3).label('jumlah3'),func.sum(subq1.c.jml4).label('jumlah4'))\
                .filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)),
                Rekening.level_id<4)\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.tahun_id)\
                .order_by(Rekening.kode).all()                    

            generator = r621Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Ringkasan Perda Perubahan APBD (rincian Objek)
        elif url_dict['act']=='r6211' :
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                KegiatanSub.tahun_id,
                (KegiatanItem.vol_1_1* KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('jml1'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml2'),
                (KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml3'),
                (KegiatanItem.vol_4_1* KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jml4'))\
                .filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                        KegiatanItem.rekening_id==Rekening.id,
                        KegiatanSub.tahun_id==self.session['tahun'])\
                .subquery()

            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, subq1.c.tahun_id, 
                func.sum(subq1.c.jml1).label('jumlah1'),func.sum(subq1.c.jml2).label('jumlah2'),
                func.sum(subq1.c.jml3).label('jumlah3'),func.sum(subq1.c.jml4).label('jumlah4'))\
                .filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)))\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, subq1.c.tahun_id)\
                .order_by(Rekening.kode).all()                    

            generator = r6211Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

        ## Rincian Perda Perubahan APBD 
        elif url_dict['act']=='r622' :
            subq = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                (KegiatanItem.vol_1_1* KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('jml1'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml2'),
                (KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml3'),
                (KegiatanItem.vol_4_1* KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jml4'),
                Unit.id.label('unit_id'),Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), 
                KegiatanSub.tahun_id.label('tahun'), KegiatanSub.lokasi, KegiatanSub.sdana, 
                Program.kode.label('program_kd'), Program.nama.label('program_nm'), 
                Kegiatan.kode.label('kegiatan_kd'), Kegiatan.nama.label('kegiatan_nm'),
                KegiatanItem.kegiatan_sub_id, KegiatanSub.kegiatan_id )\
                .filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                        KegiatanItem.rekening_id==Rekening.id,
                        KegiatanSub.unit_id==Unit.id,
                        Unit.urusan_id==Urusan.id,
                        KegiatanSub.kegiatan_id==Kegiatan.id,
                        Kegiatan.program_id==Program.id,
                        KegiatanSub.tahun_id==self.session['tahun'],
                        KegiatanSub.unit_id==self.session['unit_id'])\
                .subquery()
                
            query = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, Rekening.id.label('rekening_id'),
                subq.c.unit_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.urusan_kd, subq.c.urusan_nm, 
                subq.c.tahun, subq.c.lokasi, subq.c.sdana,
                subq.c.program_kd, subq.c.program_nm, subq.c.kegiatan_kd, subq.c.kegiatan_nm, 
                subq.c.kegiatan_sub_id,  subq.c.kegiatan_id,
                case([(subq.c.kegiatan_kd=='0.00.00.10',1),(subq.c.kegiatan_kd=='0.00.00.21',2),
                (subq.c.kegiatan_kd=='0.00.00.31',4),(subq.c.kegiatan_kd=='0.00.00.32',5)], 
                else_=3).label('jenis'),                    
                func.sum(subq.c.jml1).label('jumlah1'),func.sum(subq.c.jml2).label('jumlah2'),
                func.sum(subq.c.jml3).label('jumlah3'),func.sum(subq.c.jml4).label('jumlah4'))\
                .filter(Rekening.kode==func.left(subq.c.subrek_kd, func.length(Rekening.kode)))\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign, Rekening.id, 
                subq.c.unit_id, subq.c.unit_kd, subq.c.unit_nm, subq.c.urusan_kd, subq.c.urusan_nm, subq.c.tahun,
                subq.c.lokasi, subq.c.sdana, subq.c.program_kd, subq.c.program_nm, subq.c.kegiatan_kd, subq.c.kegiatan_nm,
                subq.c.kegiatan_sub_id, subq.c.kegiatan_id,
                case([(subq.c.kegiatan_kd=='0.00.00.10',1),(subq.c.kegiatan_kd=='0.00.00.21',2),
                (subq.c.kegiatan_kd=='0.00.00.31',4),(subq.c.kegiatan_kd=='0.00.00.32',5)], 
                else_=3))\
                .order_by(case([(subq.c.kegiatan_kd=='0.00.00.10',1),(subq.c.kegiatan_kd=='0.00.00.21',2),
                (subq.c.kegiatan_kd=='0.00.00.31',4),(subq.c.kegiatan_kd=='0.00.00.32',5)], 
                else_=3),subq.c.urusan_kd, subq.c.unit_kd, subq.c.program_kd, subq.c.kegiatan_kd, Rekening.kode).all() 
                
            generator = r622Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

    ###### KAS BUDGET
    @view_config(route_name="anggaran_r700", renderer="templates/ag-report/r700.pt", permission="read")
    def anggaran_r700(self):
        params = self.request.params
        return dict(datas=self.datas)

    @view_config(route_name="anggaran_r700_act", renderer="json", permission="read")
    def anggaran_r700_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        ## SKPD All 
        if url_dict['act']=='r711' :
            query = DBSession.query(KegiatanSub.tahun_id,
                case([(Kegiatan.kode.in_(["0.00.00.10","0.00.00.31"]),"1 Pendapatan")], 
                else_="2 Belanja").label('urut1'),                    
                case([(Kegiatan.kode.in_(["0.00.00.10","0.00.00.31"]),1)], 
                else_=-1).label('defsign'),                    
                case([(Kegiatan.kode.in_(["0.00.00.10","0.00.00.31"]),"1 Pendapatan dan Penerimaan"),
                (Kegiatan.kode.in_(["0.00.00.21","0.00.00.32"]),"2 Belanja Tidak Langsung dan Pengeluaran")], 
                else_="3 Belanja Langsung").label('urut2'),
                Program.kode.label('program_kd'), Program.nama.label('program_nm'), Kegiatan.kode.label('keg_kd'), Kegiatan.nama.label('keg_nm'),
                func.sum(KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('anggaran'),
                func.sum(KegiatanItem.bln01).label('bln01'), func.sum(KegiatanItem.bln02).label('bln02'), func.sum(KegiatanItem.bln03).label('bln03'),
                func.sum(KegiatanItem.bln04).label('bln04'), func.sum(KegiatanItem.bln05).label('bln05'), func.sum(KegiatanItem.bln06).label('bln06'),
                func.sum(KegiatanItem.bln07).label('bln07'), func.sum(KegiatanItem.bln08).label('bln08'), func.sum(KegiatanItem.bln09).label('bln09'),
                func.sum(KegiatanItem.bln10).label('bln10'), func.sum(KegiatanItem.bln11).label('bln11'), func.sum(KegiatanItem.bln12).label('bln12')
                ).join(KegiatanItem).join(Kegiatan).join(Program
                ).filter(KegiatanSub.tahun_id==self.session['tahun']
                ).group_by(KegiatanSub.tahun_id,
                case([(Kegiatan.kode.in_(["0.00.00.10","0.00.00.31"]),"1 Pendapatan")], 
                else_="2 Belanja"), case([(Kegiatan.kode.in_(["0.00.00.10","0.00.00.31"]),1)], 
                else_=-1),                   
                case([(Kegiatan.kode.in_(["0.00.00.10","0.00.00.31"]),"1 Pendapatan dan Penerimaan"),
                (Kegiatan.kode.in_(["0.00.00.21","0.00.00.32"]),"2 Belanja Tidak Langsung dan Pengeluaran")], 
                else_="3 Belanja Langsung"),
                Program.kode, Program.nama, Kegiatan.kode, Kegiatan.nama
                ).order_by(case([(Kegiatan.kode.in_(["0.00.00.10","0.00.00.31"]),"1 Pendapatan")], 
                else_="2 Belanja"),case([(Kegiatan.kode.in_(["0.00.00.10","0.00.00.31"]),"1 Pendapatan dan Penerimaan"),
                (Kegiatan.kode.in_(["0.00.00.21","0.00.00.32"]),"2 Belanja Tidak Langsung dan Pengeluaran")], 
                else_="3 Belanja Langsung"), Program.kode, Kegiatan.kode
                )

            generator = r700Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
            
        ## Per SKPD 
        if url_dict['act']=='r712' :
            query = DBSession.query(KegiatanSub.tahun_id,
                case([(Kegiatan.kode.in_(["0.00.00.10","0.00.00.31"]),"1 Pendapatan")], 
                else_="2 Belanja").label('urut1'),                    
                case([(Kegiatan.kode.in_(["0.00.00.10","0.00.00.31"]),1)], 
                else_=-1).label('defsign'),                    
                case([(Kegiatan.kode.in_(["0.00.00.10","0.00.00.31"]),"1 Pendapatan dan Penerimaan"),
                (Kegiatan.kode.in_(["0.00.00.21","0.00.00.32"]),"2 Belanja Tidak Langsung dan Pengeluaran")], 
                else_="3 Belanja Langsung").label('urut2'),
                Urusan.kode.label('urusan_kd'), Urusan.nama.label('urusan_nm'), Unit.kode.label('unit_kd'), Unit.nama.label('unit_nm'), 
                Program.kode.label('program_kd'), Program.nama.label('program_nm'), Kegiatan.kode.label('keg_kd'), Kegiatan.nama.label('keg_nm'),
                func.sum(KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('anggaran'),
                func.sum(KegiatanItem.bln01).label('bln01'), func.sum(KegiatanItem.bln02).label('bln02'), func.sum(KegiatanItem.bln03).label('bln03'),
                func.sum(KegiatanItem.bln04).label('bln04'), func.sum(KegiatanItem.bln05).label('bln05'), func.sum(KegiatanItem.bln06).label('bln06'),
                func.sum(KegiatanItem.bln07).label('bln07'), func.sum(KegiatanItem.bln08).label('bln08'), func.sum(KegiatanItem.bln09).label('bln09'),
                func.sum(KegiatanItem.bln10).label('bln10'), func.sum(KegiatanItem.bln11).label('bln11'), func.sum(KegiatanItem.bln12).label('bln12')
                ).join(Unit).join(Urusan).join(KegiatanItem).join(Kegiatan).join(Program
                ).filter(KegiatanSub.tahun_id==self.session['tahun'], KegiatanSub.unit_id==self.session['unit_id']
                ).group_by(KegiatanSub.tahun_id,
                case([(Kegiatan.kode.in_(["0.00.00.10","0.00.00.31"]),"1 Pendapatan")], 
                else_="2 Belanja"), case([(Kegiatan.kode.in_(["0.00.00.10","0.00.00.31"]),1)], 
                else_=-1),                   
                case([(Kegiatan.kode.in_(["0.00.00.10","0.00.00.31"]),"1 Pendapatan dan Penerimaan"),
                (Kegiatan.kode.in_(["0.00.00.21","0.00.00.32"]),"2 Belanja Tidak Langsung dan Pengeluaran")], 
                else_="3 Belanja Langsung"),
                Urusan.kode, Urusan.nama, Unit.kode, Unit.nama, 
                Program.kode, Program.nama, Kegiatan.kode, Kegiatan.nama
                ).order_by(case([(Kegiatan.kode.in_(["0.00.00.10","0.00.00.31"]),"1 Pendapatan")], 
                else_="2 Belanja"),case([(Kegiatan.kode.in_(["0.00.00.10","0.00.00.31"]),"1 Pendapatan dan Penerimaan"),
                (Kegiatan.kode.in_(["0.00.00.21","0.00.00.32"]),"2 Belanja Tidak Langsung dan Pengeluaran")], 
                else_="3 Belanja Langsung"), Program.kode, Kegiatan.kode
                )

            generator = r701Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response

class r001Generator(JasperGenerator):
    def __init__(self):
        super(r001Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0001.jrxml')
        self.xpath = '/apbd/master/urusan'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for kode, uraian in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'urusan')
            ET.SubElement(xml_greeting, "kode").text = unicode(kode)
            ET.SubElement(xml_greeting, "uraian").text = unicode(uraian)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r002Generator(JasperGenerator):
    def __init__(self):
        super(r002Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0002.jrxml')
        self.xpath = '/apbd/master/unit'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for urusankd, kode, uraian, kategori, singkat in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'unit')
            ET.SubElement(xml_greeting, "urusankd").text = unicode(urusankd)
            ET.SubElement(xml_greeting, "kode").text = unicode(kode)
            ET.SubElement(xml_greeting, "uraian").text = unicode(uraian)
            ET.SubElement(xml_greeting, "kategori").text = unicode(kategori)
            ET.SubElement(xml_greeting, "singkat").text = unicode(singkat)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r003Generator(JasperGenerator):
    def __init__(self):
        super(r003Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0003.jrxml')
        self.xpath = '/apbd/master/program'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for kode, nama, programkd, programnm in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'program')
            ET.SubElement(xml_greeting, "kode").text = unicode(kode)
            ET.SubElement(xml_greeting, "nama").text = unicode(nama)
            ET.SubElement(xml_greeting, "programkd").text = unicode(programkd)
            ET.SubElement(xml_greeting, "programnm").text = unicode(programnm)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r041Generator(JasperGenerator):
    def __init__(self):
        super(r041Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0041.jrxml')
        self.xpath = '/apbd/master/rekaset'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for kode, uraian, level_id in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'rekaset')
            ET.SubElement(xml_greeting, "kode").text = unicode(kode)
            ET.SubElement(xml_greeting, "uraian").text = unicode(uraian)
            ET.SubElement(xml_greeting, "level_id").text = unicode(level_id)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r042Generator(JasperGenerator):
    def __init__(self):
        super(r042Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0042.jrxml')
        self.xpath = '/apbd/master/rekangg'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for kode, uraian, level_id in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'rekangg')
            ET.SubElement(xml_greeting, "kode").text = unicode(kode)
            ET.SubElement(xml_greeting, "uraian").text = unicode(uraian)
            ET.SubElement(xml_greeting, "level_id").text = unicode(level_id)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r005Generator(JasperGenerator):
    def __init__(self):
        super(r005Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0005.jrxml')
        self.xpath = '/apbd/master/pegawai'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for kode, uraian in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'pegawai')
            ET.SubElement(xml_greeting, "kode").text = unicode(kode)
            ET.SubElement(xml_greeting, "uraian").text = unicode(uraian)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root
        
class r006Generator(JasperGenerator):
    def __init__(self):
        super(r006Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0006.jrxml')
        self.xpath = '/apbd/master/program'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for kode, nama, kegiatankd, kegiatannm in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'program')
            ET.SubElement(xml_greeting, "kode").text = unicode(kode)
            ET.SubElement(xml_greeting, "nama").text = unicode(nama)
            ET.SubElement(xml_greeting, "kegiatankd").text = unicode(kegiatankd)
            ET.SubElement(xml_greeting, "kegiatannm").text = unicode(kegiatannm)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r007Generator(JasperGenerator):
    def __init__(self):
        super(r007Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0007.jrxml')
        self.xpath = '/apbd/master/tahun'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for username, email, status, last_login, registered_date in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'tahun')
            ET.SubElement(xml_greeting, "username").text = unicode(username)
            ET.SubElement(xml_greeting, "email").text = unicode(email)
            ET.SubElement(xml_greeting, "status").text = unicode(status)
            ET.SubElement(xml_greeting, "last_login").text = unicode(last_login)
            ET.SubElement(xml_greeting, "registered_date").text = unicode(registered_date)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r008Generator(JasperGenerator):
    def __init__(self):
        super(r008Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0008.jrxml')
        self.xpath = '/apbd/master/urusan'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for kode, uraian in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'urusan')
            ET.SubElement(xml_greeting, "kode").text = unicode(kode)
            ET.SubElement(xml_greeting, "uraian").text = unicode(uraian)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r009Generator(JasperGenerator):
    def __init__(self):
        super(r009Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0009.jrxml')
        self.xpath = '/apbd/master/fungsi'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for kode, uraian in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'fungsi')
            ET.SubElement(xml_greeting, "kode").text = unicode(kode)
            ET.SubElement(xml_greeting, "uraian").text = unicode(uraian)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r010Generator(JasperGenerator):
    def __init__(self):
        super(r010Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0010.jrxml')
        self.xpath = '/apbd/master/jabatan'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for kode, uraian in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'jabatan')
            ET.SubElement(xml_greeting, "kode").text = unicode(kode)
            ET.SubElement(xml_greeting, "uraian").text = unicode(uraian)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r011Generator(JasperGenerator):
    def __init__(self):
        super(r011Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0011.jrxml')
        self.xpath = '/apbd/master/pejabat'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for kode, uraian, jabatan, skpd, mulai, selesai in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'pejabat')
            ET.SubElement(xml_greeting, "kode").text = unicode(kode)
            ET.SubElement(xml_greeting, "uraian").text = unicode(uraian)
            ET.SubElement(xml_greeting, "jabatan").text = unicode(jabatan)
            ET.SubElement(xml_greeting, "skpd").text = unicode(skpd)
            ET.SubElement(xml_greeting, "mulai").text = unicode(mulai)
            ET.SubElement(xml_greeting, "selesai").text = unicode(selesai)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root
        
class r012Generator(JasperGenerator):
    def __init__(self):
        super(r012Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0012.jrxml')
        self.xpath = '/apbd/master/tahun'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for tahun, status_apbd, tanggal_1, tanggal_2, tanggal_3, tanggal_4 in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'tahun')
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "status_apbd").text = unicode(status_apbd)
            ET.SubElement(xml_greeting, "tanggal_1").text = unicode(tanggal_1)
            ET.SubElement(xml_greeting, "tanggal_2").text = unicode(tanggal_2)
            ET.SubElement(xml_greeting, "tanggal_3").text = unicode(tanggal_3)
            ET.SubElement(xml_greeting, "tanggal_4").text = unicode(tanggal_4)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root  

class r013Generator(JasperGenerator):
    def __init__(self):
        super(r013Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0013.jrxml')
        self.xpath = '/apbd/master/tahun'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for kode, nama, disable, tahun in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'tahun')
            ET.SubElement(xml_greeting, "kode").text = unicode(kode)
            ET.SubElement(xml_greeting, "nama").text = unicode(nama)
            ET.SubElement(xml_greeting, "disable").text = unicode(disable)
            ET.SubElement(xml_greeting, "tahun").text = unicode(tahun)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root  

class r014Generator(JasperGenerator):
    def __init__(self):
        super(r014Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0014.jrxml')
        self.xpath = '/apbd/master/tahun'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for kode, nama, path, perm_name, disabled in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'tahun')
            ET.SubElement(xml_greeting, "kode").text = unicode(kode)
            ET.SubElement(xml_greeting, "nama").text = unicode(nama)
            ET.SubElement(xml_greeting, "path").text = unicode(path)
            ET.SubElement(xml_greeting, "perm_name").text = unicode(perm_name)
            ET.SubElement(xml_greeting, "disabled").text = unicode(disabled)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root  

class r015Generator(JasperGenerator):
    def __init__(self):
        super(r015Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0015.jrxml')
        self.xpath = '/apbd/master/tahun'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'tahun')
            ET.SubElement(xml_greeting, "kode").text = row.kode
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "no_urut").text = unicode(row.no_urut)
            ET.SubElement(xml_greeting, "dsrhkm_nm").text = row.dsrhkm_nm
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root  

class r016Generator(JasperGenerator):
    def __init__(self):
        super(r016Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0016.jrxml')
        self.xpath = '/apbd/master/tahun'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'tahun')
            ET.SubElement(xml_greeting, "email").text = row.email
            ET.SubElement(xml_greeting, "user_name").text = row.user_name
            ET.SubElement(xml_greeting, "status").text = unicode(row.status)
            ET.SubElement(xml_greeting, "nama").text = row.nama
            ET.SubElement(xml_greeting, "sub_unit").text = unicode(row.sub_unit)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root  

class r017Generator(JasperGenerator):
    def __init__(self):
        super(r017Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0017.jrxml')
        self.xpath = '/apbd/master/tahun'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'tahun')
            ET.SubElement(xml_greeting, "grup_nm").text = row.grup_nm
            ET.SubElement(xml_greeting, "route_nm").text = row.route_nm
            ET.SubElement(xml_greeting, "path").text = row.path
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root  

class r018Generator(JasperGenerator):
    def __init__(self):
        super(r018Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0018.jrxml')
        self.xpath = '/apbd/master/tahun'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'tahun')
            ET.SubElement(xml_greeting, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_greeting, "fungsi_nm").text = row.fungsi_nm
            ET.SubElement(xml_greeting, "nama").text = row.nama
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root  

class r019Generator(JasperGenerator):
    def __init__(self):
        super(r019Generator, self).__init__()
        self.reportname = get_rpath('apbd/R0019.jrxml')
        self.xpath = '/apbd/master/rekangg'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for kode, uraian, level_id in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'rekangg')
            ET.SubElement(xml_greeting, "kode").text = unicode(kode)
            ET.SubElement(xml_greeting, "uraian").text = unicode(uraian)
            ET.SubElement(xml_greeting, "level_id").text = unicode(level_id)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r100Generator(JasperGenerator):
    def __init__(self):
        super(r100Generator, self).__init__()
        self.reportname = get_rpath('apbd/R1000.jrxml')
        self.xpath = '/apbd/rka/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'rka')

        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'rekening')
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_greeting, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_greeting, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_greeting, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r101Generator(JasperGeneratorWithSubreport):
    def __init__(self):
        self.mainreport = get_rpath('apbd/R1100.jrxml')

        self.subreportlist = []
        #self.subreportlist.append(get_rpath('apbd/R1100_subreport1.jrxml'))

        self.xpath = '/apbd/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'rekening')
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.kegiatan_sub_id)
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_a, "maxlevel").text = unicode(row.maxlevel)
            ET.SubElement(xml_a, "customer").text = customer
        return self.root

class r1011Generator(JasperGeneratorWithSubreport):
    def __init__(self):
        self.mainreport = get_rpath('apbd/R1100_1.jrxml')

        self.subreportlist = []
        #self.subreportlist.append(get_rpath('apbd/R1221_1_subreport1.jrxml'))

        self.xpath = '/apbd/kegiatan'
        
        self.root = ET.Element('apbd')

    def generate_xml(self, tobegreeted):
        
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'kegiatan')
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "kegiatan_kd").text = row.kegiatan_kd
            ET.SubElement(xml_a, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_a, "sdana").text = row.sdana
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.id)
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "no_urut").text = unicode(row.no_urut)
            ET.SubElement(xml_a, "item_nm").text = row.item_nm
            ET.SubElement(xml_a, "volume1").text = unicode(row.volume1)
            ET.SubElement(xml_a, "satuan1").text = row.satuan1
            ET.SubElement(xml_a, "volume2").text = unicode(row.volume2)
            ET.SubElement(xml_a, "satuan2").text = row.satuan2
            ET.SubElement(xml_a, "harga").text = unicode(row.harga)
            ET.SubElement(xml_a, "anggaran").text = unicode(row.anggaran)            
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)            
            ET.SubElement(xml_a, "customer").text = customer
        return self.root

class r102Generator(JasperGenerator):
    def __init__(self):
        super(r102Generator, self).__init__()
        self.reportname = get_rpath('apbd/R1210.jrxml')
        self.xpath = '/apbd/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'rekening')
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.kegiatan_sub_id)
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_a, "customer").text = customer
        return self.root

class r103Generator(JasperGenerator):
    def __init__(self):
        super(r103Generator, self).__init__()
        self.reportname = get_rpath('apbd/R1220.jrxml')
        self.xpath = '/apbd/master/rka'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'master')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'rka')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.kegiatan_subs.tahun_id)
            ET.SubElement(xml_greeting, "urusan_kd").text = row.kegiatan_subs.kegiatans.programs.urusans.kode
            ET.SubElement(xml_greeting, "urusan_nm").text = row.kegiatan_subs.kegiatans.programs.urusans.nama
            ET.SubElement(xml_greeting, "unit_id").text = unicode(row.kegiatan_subs.units.id)
            ET.SubElement(xml_greeting, "unit_kd").text = row.kegiatan_subs.units.kode
            ET.SubElement(xml_greeting, "unit_nm").text = row.kegiatan_subs.units.nama
            ET.SubElement(xml_greeting, "program_kd").text = row.kegiatan_subs.kegiatans.programs.kode
            ET.SubElement(xml_greeting, "program_nm").text = row.kegiatan_subs.kegiatans.programs.nama
            ET.SubElement(xml_greeting, "kegiatan_kd").text = row.kegiatan_subs.kegiatans.kode
            ET.SubElement(xml_greeting, "kegiatan_nm").text = row.kegiatan_subs.kegiatans.nama
            ET.SubElement(xml_greeting, "lokasi").text = row.kegiatan_subs.lokasi
            ET.SubElement(xml_greeting, "target").text = row.kegiatan_subs.target
            ET.SubElement(xml_greeting, "rek_kd").text = row.rekenings.kode
            ET.SubElement(xml_greeting, "jumlah1").text = unicode(row.vol_1_1*row.vol_1_2*row.hsat_1)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r104Generator(JasperGeneratorWithSubreport):
    def __init__(self):

        self.mainreport = get_rpath('apbd/R1221.jrxml')

        self.subreportlist = []
        self.subreportlist.append(get_rpath('apbd/R1221_subreport1.jrxml'))
        self.subreportlist.append(get_rpath('apbd/R1221_subreport2.jrxml'))

        self.xpath = '/apbd/kegiatan'
        
        self.root = ET.Element('apbd')

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'kegiatan')
        
        for row in tobegreeted:
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "program_kd").text = row.program_kd
            ET.SubElement(xml_a, "program_nm").text = row.program_nm
            ET.SubElement(xml_a, "kegiatan_kd").text = row.kegiatan_kd
            ET.SubElement(xml_a, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_a, "lokasi").text = row.lokasi
            ET.SubElement(xml_a, "target").text = row.target
            ET.SubElement(xml_a, "sasaran").text = row.sasaran
            ET.SubElement(xml_a, "amt_lalu").text = unicode(row.amt_lalu)
            ET.SubElement(xml_a, "amt_yad").text = unicode(row.amt_yad)
            ET.SubElement(xml_a, "anggaran").text = unicode(row.anggaran)
            
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.id)
            ET.SubElement(xml_a, "customer").text = customer
            rows = DBSession.query(KegiatanIndikator)\
              .filter(KegiatanIndikator.kegiatan_sub_id==row.id)\
              .order_by(KegiatanIndikator.tipe,KegiatanIndikator.no_urut)
            for row2 in rows :
                xml_b = ET.SubElement(xml_a, "indikator")
                ET.SubElement(xml_b, "tipe").text =unicode(row2.tipe)
                ET.SubElement(xml_b, "no_urut").text =unicode(row2.no_urut)
                ET.SubElement(xml_b, "tolok_ukur_1").text =row2.tolok_ukur_1
                ET.SubElement(xml_b, "volume_1").text =unicode(row2.volume_1)
                ET.SubElement(xml_b, "satuan_1").text =row2.satuan_1
            
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                    Kegiatan.nama.label('keg_nm'),
                    func.sum(KegiatanItem.vol_1_1* KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('jml1')
                    ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan
                    ).filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                            KegiatanItem.rekening_id==Rekening.id,
                            KegiatanItem.kegiatan_sub_id==row.id
                    ).group_by(Rekening.kode,Rekening.nama,Kegiatan.nama
                    ).subquery()

            rowitems = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),Rekening.level_id,
                    subq1.c.keg_nm,
                    func.sum(subq1.c.jml1).label('jumlah1'))\
                    .filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)))\
                    .group_by(Rekening.kode, Rekening.nama, subq1.c.keg_nm, Rekening.level_id)\
                    .order_by(Rekening.kode).all()                    

            for row3 in rowitems :
                xml_c = ET.SubElement(xml_a, "item")
                ET.SubElement(xml_c, "rek_kd").text =row3.rek_kd
                ET.SubElement(xml_c, "rek_nm").text =row3.rek_nm
                ET.SubElement(xml_c, "keg_nm").text =row3.keg_nm
                ET.SubElement(xml_c, "level_id").text =unicode(row3.level_id)
                ET.SubElement(xml_c, "jumlah1").text =unicode(row3.jumlah1)
        return self.root

class r1041Generator(JasperGeneratorWithSubreport):
    def __init__(self):
        self.mainreport = get_rpath('apbd/R1221_1.jrxml')

        self.subreportlist = []
        #self.subreportlist.append(get_rpath('apbd/R1221_1_subreport1.jrxml'))

        self.xpath = '/apbd/kegiatan'
        
        self.root = ET.Element('apbd')

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'kegiatan')
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "program_kd").text = row.program_kd
            ET.SubElement(xml_a, "program_nm").text = row.program_nm
            ET.SubElement(xml_a, "kegiatan_kd").text = row.kegiatan_kd
            ET.SubElement(xml_a, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_a, "sdana").text = row.sdana
            ET.SubElement(xml_a, "lokasi").text = row.lokasi
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.id)
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "no_urut").text = unicode(row.no_urut)
            ET.SubElement(xml_a, "item_nm").text = row.item_nm
            ET.SubElement(xml_a, "volume1").text = unicode(row.volume1)
            ET.SubElement(xml_a, "satuan1").text = row.satuan1
            ET.SubElement(xml_a, "volume2").text = unicode(row.volume2)
            ET.SubElement(xml_a, "satuan2").text = row.satuan2
            ET.SubElement(xml_a, "harga").text = unicode(row.harga)
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "anggaran").text = unicode(row.anggaran)            
            ET.SubElement(xml_a, "customer").text = customer
        return self.root

class r105Generator(JasperGenerator):
    def __init__(self):
        super(r105Generator, self).__init__()
        self.reportname = get_rpath('apbd/R1300.jrxml')
        self.xpath = '/apbd/rka/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'rka')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'rekening')
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_greeting, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_greeting, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_greeting, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_greeting, "rek_kd1").text = row.rek_kd1
            ET.SubElement(xml_greeting, "rek_kd2").text = row.rek_kd2
            ET.SubElement(xml_greeting, "rek_kd3").text = row.rek_kd3
            ET.SubElement(xml_greeting, "rek_kd4").text = row.rek_kd4
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r106Generator(JasperGenerator):
    def __init__(self):
        super(r106Generator, self).__init__()
        self.reportname = get_rpath('apbd/R1310.jrxml')
        self.xpath = '/apbd/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'rekening')
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.kegiatan_sub_id)
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_a, "customer").text = customer
        return self.root

class r107Generator(JasperGenerator):
    def __init__(self):
        super(r107Generator, self).__init__()
        self.reportname = get_rpath('apbd/R1320.jrxml')
        self.xpath = '/apbd/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'rekening')
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.kegiatan_sub_id)
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_a, "customer").text = customer
        return self.root
        
class r200Generator(JasperGeneratorWithSubreport):
    def __init__(self):

        self.mainreport = get_rpath('apbd/R2000.jrxml')
        self.subreportlist = []
        self.subreportlist.append(get_rpath('apbd/R2000_subreport1.jrxml'))
        self.subreportlist.append(get_rpath('apbd/R2000_subreport2.jrxml'))
        print self.mainreport,self.subreportlist
        self.xpath = '/apbd/unit'
        
        self.root = ET.Element('apbd')

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'unit')

        for row in tobegreeted:
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_id").text = unicode(row.unit_id)
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "customer").text = customer

            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml2'))\
                .filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                    KegiatanItem.rekening_id==Rekening.id,
                    KegiatanSub.tahun_id==row.tahun_id,
                    KegiatanSub.unit_id==row.unit_id)\
                .subquery()

            rowrek = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, 
                func.sum(subq1.c.jml2).label('jumlah2'))\
                .filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)))\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign)\
                .order_by(Rekening.kode).all()

            for row2 in rowrek :
                xml_b = ET.SubElement(xml_a, "rekening")
                ET.SubElement(xml_b, "rek_kd").text =row2.rek_kd
                ET.SubElement(xml_b, "rek_nm").text =row2.rek_nm
                ET.SubElement(xml_b, "level_id").text =unicode(row2.level_id)
                ET.SubElement(xml_b, "defsign").text =unicode(row2.defsign)
                ET.SubElement(xml_b, "jumlah2").text =unicode(row2.jumlah2)
                
            rowtrw = DBSession.query(Kegiatan.kode.label('kode'),
                 func.sum(KegiatanItem.bln01+KegiatanItem.bln02+KegiatanItem.bln03).label('trw1'),
                 func.sum(KegiatanItem.bln04+KegiatanItem.bln05+KegiatanItem.bln06).label('trw2'),
                 func.sum(KegiatanItem.bln07+KegiatanItem.bln08+KegiatanItem.bln09).label('trw3'),
                 func.sum(KegiatanItem.bln10+KegiatanItem.bln11+KegiatanItem.bln12).label('trw4')
                 ).filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                    KegiatanSub.kegiatan_id==Kegiatan.id,
                    KegiatanSub.tahun_id==row.tahun_id,
                    KegiatanSub.unit_id==row.unit_id
                 ).group_by(Kegiatan.kode
                 ).order_by(Kegiatan.kode)
            
            for row3 in rowtrw :
                xml_c = ET.SubElement(xml_a, "twl")
                ET.SubElement(xml_c, "kode").text =row3.kode
                ET.SubElement(xml_c, "trw1").text =unicode(row3.trw1)
                ET.SubElement(xml_c, "trw2").text =unicode(row3.trw2)
                ET.SubElement(xml_c, "trw3").text =unicode(row3.trw3)
                ET.SubElement(xml_c, "trw4").text =unicode(row3.trw4)
                
        return self.root

class r201Generator(JasperGenerator):
    def __init__(self):
        super(r201Generator, self).__init__()
        self.reportname = get_rpath('apbd/R2100.jrxml')
        self.xpath = '/apbd/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'rekening')
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.kegiatan_sub_id)
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_a, "maxlevel").text = unicode(row.maxlevel)
            ET.SubElement(xml_a, "trw1").text = unicode(row.trw1)
            ET.SubElement(xml_a, "trw2").text = unicode(row.trw2)
            ET.SubElement(xml_a, "trw3").text = unicode(row.trw3)
            ET.SubElement(xml_a, "trw4").text = unicode(row.trw4)
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "customer").text = customer
            ET.SubElement(xml_a, "logo").text = logo
        return self.root

class r2011Generator(JasperGeneratorWithSubreport):
    def __init__(self):
        self.mainreport = get_rpath('apbd/R2100_1.jrxml')

        self.subreportlist = []
        #self.subreportlist.append(get_rpath('apbd/R1221_2_subreport1.jrxml'))

        print self.mainreport,self.subreportlist
        self.xpath = '/apbd/kegiatan'
        
        self.root = ET.Element('apbd')

    def generate_xml(self, tobegreeted):
        
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'kegiatan')
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "kegiatan_kd").text = row.kegiatan_kd
            ET.SubElement(xml_a, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_a, "sdana").text = row.sdana
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.id)
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "no_urut").text = unicode(row.no_urut)
            ET.SubElement(xml_a, "item_nm").text = row.item_nm
            ET.SubElement(xml_a, "volume1").text = unicode(row.volume1)
            ET.SubElement(xml_a, "satuan1").text = row.satuan1
            ET.SubElement(xml_a, "volume2").text = unicode(row.volume2)
            ET.SubElement(xml_a, "satuan2").text = row.satuan2
            ET.SubElement(xml_a, "harga").text = unicode(row.harga)
            ET.SubElement(xml_a, "anggaran").text = unicode(row.anggaran)            
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)            
            ET.SubElement(xml_a, "customer").text = customer
        return self.root

class r202Generator(JasperGenerator):
    def __init__(self):
        super(r202Generator, self).__init__()
        self.reportname = get_rpath('apbd/R2210.jrxml')
        self.xpath = '/apbd/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'rekening')
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.kegiatan_sub_id)
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_a, "maxlevel").text = unicode(row.maxlevel)
            ET.SubElement(xml_a, "trw1").text = unicode(row.trw1)
            ET.SubElement(xml_a, "trw2").text = unicode(row.trw2)
            ET.SubElement(xml_a, "trw3").text = unicode(row.trw3)
            ET.SubElement(xml_a, "trw4").text = unicode(row.trw4)
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "customer").text = customer
            ET.SubElement(xml_a, "logo").text = logo
        return self.root

class r203Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r203Generator, self).__init__()
        self.reportname = get_rpath('apbd/R2220.jrxml')
        self.xpath = '/apbd/unit/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        xml_a  =  ET.SubElement(self.root, 'unit')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'rekening')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_greeting, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_greeting, "unit_id").text = unicode(row.unit_id)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "program_kd").text = row.program_kd
            ET.SubElement(xml_greeting, "program_nm").text = row.program_nm
            ET.SubElement(xml_greeting, "kegiatan_kd").text = row.kegiatan_kd
            ET.SubElement(xml_greeting, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_greeting, "lokasi").text = row.lokasi
            ET.SubElement(xml_greeting, "target").text = row.target
            ET.SubElement(xml_greeting, "trw1").text = unicode(row.trw1)
            ET.SubElement(xml_greeting, "trw2").text = unicode(row.trw2)
            ET.SubElement(xml_greeting, "trw3").text = unicode(row.trw3)
            ET.SubElement(xml_greeting, "trw4").text = unicode(row.trw4)
            ET.SubElement(xml_greeting, "customer").text = customer
            print row.trw1
        return self.root

class r204Generator(JasperGeneratorWithSubreport):
    def __init__(self):
        self.mainreport = get_rpath('apbd/R2221.jrxml')

        self.subreportlist = []
        self.subreportlist.append(get_rpath('apbd/R2221_subreport1.jrxml'))
        self.subreportlist.append(get_rpath('apbd/R2221_subreport2.jrxml'))
        self.subreportlist.append(get_rpath('apbd/R2221_subreport3.jrxml'))

        print self.mainreport,self.subreportlist
        self.xpath = '/apbd/kegiatan'
        
        self.root = ET.Element('apbd')

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'kegiatan')
        
        for row in tobegreeted:
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun_id)
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
            ET.SubElement(xml_a, "sasaran").text = row.sasaran
            ET.SubElement(xml_a, "sdana").text = row.sdana
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.id)
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "anggaran").text = unicode(row.anggaran)
            ET.SubElement(xml_a, "logo").text = logo
            
            ET.SubElement(xml_a, "customer").text = customer
            rows = DBSession.query(KegiatanIndikator)\
              .filter(KegiatanIndikator.kegiatan_sub_id==row.id)\
              .order_by(KegiatanIndikator.tipe,KegiatanIndikator.no_urut)
            for row2 in rows :
                xml_b = ET.SubElement(xml_a, "indikator")
                ET.SubElement(xml_b, "tipe").text =unicode(row2.tipe)
                ET.SubElement(xml_b, "no_urut").text =unicode(row2.no_urut)
                ET.SubElement(xml_b, "tolok_ukur_1").text =row2.tolok_ukur_2
                ET.SubElement(xml_b, "volume_1").text =unicode(row2.volume_2)
                ET.SubElement(xml_b, "satuan_1").text =row2.satuan_2
            
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                    Kegiatan.nama.label('keg_nm'),
                    func.sum(KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml1')
                    ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan
                    ).filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                            KegiatanItem.rekening_id==Rekening.id,
                            KegiatanItem.kegiatan_sub_id==row.id
                    ).group_by(Rekening.kode,Rekening.nama,Kegiatan.nama
                    ).subquery()

            rowitems = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),Rekening.level_id,
                    subq1.c.keg_nm,
                    func.sum(subq1.c.jml1).label('jumlah1'))\
                    .filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)))\
                    .group_by(Rekening.kode, Rekening.nama, subq1.c.keg_nm, Rekening.level_id)\
                    .order_by(Rekening.kode).all()                    

            for row3 in rowitems :
                xml_c = ET.SubElement(xml_a, "item")
                ET.SubElement(xml_c, "rek_kd").text =row3.rek_kd
                ET.SubElement(xml_c, "rek_nm").text =row3.rek_nm
                ET.SubElement(xml_c, "keg_nm").text =row3.keg_nm
                ET.SubElement(xml_c, "level_id").text =unicode(row3.level_id)
                ET.SubElement(xml_c, "jumlah1").text =unicode(row3.jumlah1)

            rowtrw = DBSession.query(func.sum(KegiatanItem.bln01+KegiatanItem.bln02+KegiatanItem.bln03).label('jmltrw1'),
                    func.sum(KegiatanItem.bln04+KegiatanItem.bln05+KegiatanItem.bln06).label('jmltrw2'),
                    func.sum(KegiatanItem.bln07+KegiatanItem.bln08+KegiatanItem.bln09).label('jmltrw3'),
                    func.sum(KegiatanItem.bln10+KegiatanItem.bln11+KegiatanItem.bln12).label('jmltrw4'))\
                    .filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                            KegiatanSub.unit_id==row.unit_id,
                            KegiatanSub.tahun_id==row.tahun_id,
                            KegiatanItem.kegiatan_sub_id==row.id)\

            for row4 in rowtrw :
                xml_d = ET.SubElement(xml_a, "trw")
                ET.SubElement(xml_d, "jmltrw1").text =unicode(row4.jmltrw1)
                ET.SubElement(xml_d, "jmltrw2").text =unicode(row4.jmltrw2)
                ET.SubElement(xml_d, "jmltrw3").text =unicode(row4.jmltrw3)
                ET.SubElement(xml_d, "jmltrw4").text =unicode(row4.jmltrw4)
            
        return self.root

class r2041Generator(JasperGeneratorWithSubreport):
    def __init__(self):
        self.mainreport = get_rpath('apbd/R2221_1.jrxml')

        self.subreportlist = []
        #self.subreportlist.append(get_rpath('apbd/R1221_1_subreport1.jrxml'))

        self.xpath = '/apbd/kegiatan'
        
        self.root = ET.Element('apbd')

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'kegiatan')
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "program_kd").text = row.program_kd
            ET.SubElement(xml_a, "program_nm").text = row.program_nm
            ET.SubElement(xml_a, "kegiatan_kd").text = row.kegiatan_kd
            ET.SubElement(xml_a, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_a, "sdana").text = row.sdana
            ET.SubElement(xml_a, "lokasi").text = row.lokasi
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.id)
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "no_urut").text = unicode(row.no_urut)
            ET.SubElement(xml_a, "item_nm").text = row.item_nm
            ET.SubElement(xml_a, "volume1").text = unicode(row.volume1)
            ET.SubElement(xml_a, "satuan1").text = row.satuan1
            ET.SubElement(xml_a, "volume2").text = unicode(row.volume2)
            ET.SubElement(xml_a, "satuan2").text = row.satuan2
            ET.SubElement(xml_a, "harga").text = unicode(row.harga)
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "anggaran").text = unicode(row.anggaran)            
            ET.SubElement(xml_a, "customer").text = customer
        return self.root

class r205Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r205Generator, self).__init__()
        self.reportname = get_rpath('apbd/R2300.jrxml')
        self.xpath = '/apbd/unit/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        xml_a  =  ET.SubElement(self.root, 'unit')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'rekening')
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_greeting, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_greeting, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_greeting, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_greeting, "trw1").text = unicode(row.trw1)
            ET.SubElement(xml_greeting, "trw2").text = unicode(row.trw2)
            ET.SubElement(xml_greeting, "trw3").text = unicode(row.trw3)
            ET.SubElement(xml_greeting, "trw4").text = unicode(row.trw4)            
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r206Generator(JasperGenerator):
    def __init__(self):
        super(r206Generator, self).__init__()
        self.reportname = get_rpath('apbd/R2310.jrxml')
        self.xpath = '/apbd/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'rekening')
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.kegiatan_sub_id)
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_a, "trw1").text = unicode(row.trw1)
            ET.SubElement(xml_a, "trw2").text = unicode(row.trw2)
            ET.SubElement(xml_a, "trw3").text = unicode(row.trw3)
            ET.SubElement(xml_a, "trw4").text = unicode(row.trw4)
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "customer").text = customer
            ET.SubElement(xml_a, "logo").text = logo
        return self.root

class r207Generator(JasperGenerator):
    def __init__(self):
        super(r207Generator, self).__init__()
        self.reportname = get_rpath('apbd/R2320.jrxml')
        self.xpath = '/apbd/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'rekening')
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.kegiatan_sub_id)
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_a, "trw1").text = unicode(row.trw1)
            ET.SubElement(xml_a, "trw2").text = unicode(row.trw2)
            ET.SubElement(xml_a, "trw3").text = unicode(row.trw3)
            ET.SubElement(xml_a, "trw4").text = unicode(row.trw4)
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "customer").text = customer
            ET.SubElement(xml_a, "logo").text = logo
        return self.root

class r300Generator(JasperGeneratorWithSubreport):
    def __init__(self):

        self.mainreport = get_rpath('apbd/R3000.jrxml')
        self.subreportlist = []
        self.subreportlist.append(get_rpath('apbd/R3000_subreport1.jrxml'))
        self.subreportlist.append(get_rpath('apbd/R3000_subreport2.jrxml'))
        print self.mainreport,self.subreportlist
        self.xpath = '/apbd/unit'
        
        self.root = ET.Element('apbd')

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'unit')

        for row in tobegreeted:
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_id").text = unicode(row.unit_id)
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "customer").text = customer

            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                (KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml2'),
                (KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml3'))\
                .filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                    KegiatanItem.rekening_id==Rekening.id,
                    KegiatanSub.tahun_id==row.tahun_id,
                    KegiatanSub.unit_id==row.unit_id)\
                .subquery()

            rowrek = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, 
                func.sum(subq1.c.jml2).label('jumlah2'),func.sum(subq1.c.jml3).label('jumlah3'))\
                .filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)))\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign)\
                .order_by(Rekening.kode).all()

            for row2 in rowrek :
                xml_b = ET.SubElement(xml_a, "rekening")
                ET.SubElement(xml_b, "rek_kd").text =row2.rek_kd
                ET.SubElement(xml_b, "rek_nm").text =row2.rek_nm
                ET.SubElement(xml_b, "level_id").text =unicode(row2.level_id)
                ET.SubElement(xml_b, "defsign").text =unicode(row2.defsign)
                ET.SubElement(xml_b, "jumlah2").text =unicode(row2.jumlah2)
                ET.SubElement(xml_b, "jumlah3").text =unicode(row2.jumlah3)
                
            rowtrw = DBSession.query(Kegiatan.kode.label('kode'),
                 func.sum(KegiatanItem.bln01+KegiatanItem.bln02+KegiatanItem.bln03).label('trw1'),
                 func.sum(KegiatanItem.bln04+KegiatanItem.bln05+KegiatanItem.bln06).label('trw2'),
                 func.sum(KegiatanItem.bln07+KegiatanItem.bln08+KegiatanItem.bln09).label('trw3'),
                 func.sum(KegiatanItem.bln10+KegiatanItem.bln11+KegiatanItem.bln12).label('trw4')
                 ).filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                    KegiatanSub.kegiatan_id==Kegiatan.id,
                    KegiatanSub.tahun_id==row.tahun_id,
                    KegiatanSub.unit_id==row.unit_id
                 ).group_by(Kegiatan.kode
                 ).order_by(Kegiatan.kode)

            for row3 in rowtrw :
                xml_c = ET.SubElement(xml_a, "twl")
                ET.SubElement(xml_c, "kode").text =unicode(row3.kode)
                ET.SubElement(xml_c, "trw1").text =unicode(row3.trw1)
                ET.SubElement(xml_c, "trw2").text =unicode(row3.trw2)
                ET.SubElement(xml_c, "trw3").text =unicode(row3.trw3)
                ET.SubElement(xml_c, "trw4").text =unicode(row3.trw4)
                
        return self.root

class r301Generator(JasperGenerator):
    def __init__(self):
        super(r301Generator, self).__init__()
        self.reportname = get_rpath('apbd/R3100.jrxml')
        self.xpath = '/apbd/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'rekening')
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.kegiatan_sub_id)
            ET.SubElement(xml_a, "perubahan").text = row.perubahan
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_a, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_a, "selisih").text = unicode(row.jumlah2-row.jumlah1)
            ET.SubElement(xml_a, "persen").text = unicode((row.jumlah2-row.jumlah1)*100/row.jumlah1)
            ET.SubElement(xml_a, "customer").text = customer
        return self.root

class r3011Generator(JasperGeneratorWithSubreport):
    def __init__(self):
        self.mainreport = get_rpath('apbd/R3100_1.jrxml')

        self.subreportlist = []
        #self.subreportlist.append(get_rpath('apbd/R3_1_subreport1.jrxml'))

        self.xpath = '/apbd/kegiatan'
        self.root = ET.Element('apbd')

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'kegiatan')
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "kegiatan_kd").text = row.kegiatan_kd
            ET.SubElement(xml_a, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_a, "sdana").text = row.sdana
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.id)
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "no_urut").text = unicode(row.no_urut)
            ET.SubElement(xml_a, "item_nm").text = row.item_nm
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)            
            ET.SubElement(xml_a, "volume11").text = unicode(row.volume11)
            ET.SubElement(xml_a, "satuan11").text = row.satuan11
            ET.SubElement(xml_a, "volume12").text = unicode(row.volume12)
            ET.SubElement(xml_a, "satuan12").text = row.satuan12
            ET.SubElement(xml_a, "harga1").text = unicode(row.harga1)
            ET.SubElement(xml_a, "anggaran1").text = unicode(row.anggaran1)            
            ET.SubElement(xml_a, "volume21").text = unicode(row.volume21)
            ET.SubElement(xml_a, "satuan21").text = row.satuan21
            ET.SubElement(xml_a, "volume22").text = unicode(row.volume22)
            ET.SubElement(xml_a, "satuan22").text = row.satuan22
            ET.SubElement(xml_a, "harga2").text = unicode(row.harga2)
            ET.SubElement(xml_a, "anggaran2").text = unicode(row.anggaran2)            
            ET.SubElement(xml_a, "customer").text = customer
        return self.root

class r302Generator(JasperGenerator):
    def __init__(self):
        super(r302Generator, self).__init__()
        self.reportname = get_rpath('apbd/R3210.jrxml')
        self.xpath = '/apbd/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'rekening')
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.kegiatan_sub_id)
            ET.SubElement(xml_a, "perubahan").text = row.perubahan
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_a, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_a, "selisih").text = unicode(row.jumlah2-row.jumlah1)
            ET.SubElement(xml_a, "persen").text = unicode((row.jumlah2-row.jumlah1)*100/row.jumlah1)
            ET.SubElement(xml_a, "customer").text = customer
        return self.root

class r303Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r303Generator, self).__init__()
        self.reportname = get_rpath('apbd/R3220.jrxml')
        self.xpath = '/apbd/unit/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        xml_a  =  ET.SubElement(self.root, 'unit')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'rekening')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_greeting, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_greeting, "unit_id").text = unicode(row.unit_id)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "program_kd").text = row.program_kd
            ET.SubElement(xml_greeting, "program_nm").text = row.program_nm
            ET.SubElement(xml_greeting, "kegiatan_kd").text = row.kegiatan_kd
            ET.SubElement(xml_greeting, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_greeting, "lokasi").text = row.lokasi
            ET.SubElement(xml_greeting, "target").text = row.target
            ET.SubElement(xml_greeting, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_greeting, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_greeting, "jumlah3").text = unicode(row.jumlah3)
            ET.SubElement(xml_greeting, "jumlah4").text = unicode(row.jumlah4)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r304Generator(JasperGeneratorWithSubreport):
    def __init__(self):
        self.mainreport = get_rpath('apbd/R3221.jrxml')

        self.subreportlist = []
        self.subreportlist.append(get_rpath('apbd/R3221_subreport1.jrxml'))
        self.subreportlist.append(get_rpath('apbd/R3221_subreport2.jrxml'))
        self.subreportlist.append(get_rpath('apbd/R3221_subreport3.jrxml'))

        print self.mainreport,self.subreportlist
        self.xpath = '/apbd/kegiatan'
        
        self.root = ET.Element('apbd')

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'kegiatan')
        
        for row in tobegreeted:
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun_id)
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
            ET.SubElement(xml_a, "sasaran").text = row.sasaran
            ET.SubElement(xml_a, "sdana").text = row.sdana
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.id)
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "anggaran1").text = unicode(row.anggaran1)
            ET.SubElement(xml_a, "anggaran2").text = unicode(row.anggaran2)
            
            ET.SubElement(xml_a, "customer").text = customer
            rows = DBSession.query(KegiatanIndikator)\
              .filter(KegiatanIndikator.kegiatan_sub_id==row.id)\
              .order_by(KegiatanIndikator.tipe,KegiatanIndikator.no_urut)
            for row2 in rows :
                xml_b = ET.SubElement(xml_a, "indikator")
                ET.SubElement(xml_b, "tipe").text =unicode(row2.tipe)
                ET.SubElement(xml_b, "no_urut").text =unicode(row2.no_urut)
                ET.SubElement(xml_b, "tolok_ukur_1").text =row2.tolok_ukur_2
                ET.SubElement(xml_b, "volume_1").text =unicode(row2.volume_2)
                ET.SubElement(xml_b, "satuan_1").text =row2.satuan_2
                ET.SubElement(xml_b, "tolok_ukur_2").text =row2.tolok_ukur_3
                ET.SubElement(xml_b, "volume_2").text =unicode(row2.volume_3)
                ET.SubElement(xml_b, "satuan_2").text =row2.satuan_3
            
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                    Kegiatan.nama.label('keg_nm'),
                    func.sum(KegiatanItem.vol_2_1* KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('jml1'),
                    func.sum(KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml2')
                    ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan
                    ).filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                            KegiatanItem.rekening_id==Rekening.id,
                            KegiatanItem.kegiatan_sub_id==row.id
                    ).group_by(Rekening.kode,Rekening.nama,Kegiatan.nama
                    ).subquery()

            rowitems = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),Rekening.level_id,
                    subq1.c.keg_nm,
                    func.sum(subq1.c.jml1).label('jumlah1'),
                    func.sum(subq1.c.jml2).label('jumlah2'),
                    ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)))\
                    .group_by(Rekening.kode, Rekening.nama, subq1.c.keg_nm, Rekening.level_id)\
                    .order_by(Rekening.kode).all()                    

            for row3 in rowitems :
                xml_c = ET.SubElement(xml_a, "item")
                ET.SubElement(xml_c, "rek_kd").text =row3.rek_kd
                ET.SubElement(xml_c, "rek_nm").text =row3.rek_nm
                ET.SubElement(xml_c, "keg_nm").text =row3.keg_nm
                ET.SubElement(xml_c, "level_id").text =unicode(row3.level_id)
                ET.SubElement(xml_c, "jumlah1").text =unicode(row3.jumlah1)
                ET.SubElement(xml_c, "jumlah2").text =unicode(row3.jumlah2)
        return self.root

class r3041Generator(JasperGeneratorWithSubreport):
    def __init__(self):
        self.mainreport = get_rpath('apbd/R3221_1.jrxml')

        self.subreportlist = []
        #self.subreportlist.append(get_rpath('apbd/R1221_3_subreport1.jrxml'))

        print self.mainreport,self.subreportlist
        self.xpath = '/apbd/kegiatan'
        
        self.root = ET.Element('apbd')

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'kegiatan')
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "program_kd").text = row.program_kd
            ET.SubElement(xml_a, "program_nm").text = row.program_nm
            ET.SubElement(xml_a, "kegiatan_kd").text = row.kegiatan_kd
            ET.SubElement(xml_a, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_a, "sdana").text = row.sdana
            ET.SubElement(xml_a, "lokasi").text = row.lokasi
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.id)
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "no_urut").text = unicode(row.no_urut)
            ET.SubElement(xml_a, "item_nm").text = row.item_nm
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "volume11").text = unicode(row.volume11)
            ET.SubElement(xml_a, "satuan11").text = row.satuan11
            ET.SubElement(xml_a, "volume12").text = unicode(row.volume12)
            ET.SubElement(xml_a, "satuan12").text = row.satuan12
            ET.SubElement(xml_a, "harga1").text = unicode(row.harga1)
            ET.SubElement(xml_a, "anggaran1").text = unicode(row.anggaran1)            
            ET.SubElement(xml_a, "volume21").text = unicode(row.volume21)
            ET.SubElement(xml_a, "satuan21").text = row.satuan21
            ET.SubElement(xml_a, "volume22").text = unicode(row.volume22)
            ET.SubElement(xml_a, "satuan22").text = row.satuan22
            ET.SubElement(xml_a, "harga2").text = unicode(row.harga2)
            ET.SubElement(xml_a, "anggaran2").text = unicode(row.anggaran2)            
            ET.SubElement(xml_a, "customer").text = customer
        return self.root
	
class r305Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r305Generator, self).__init__()
        self.reportname = get_rpath('apbd/R3300.jrxml')
        self.xpath = '/apbd/unit/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        xml_a  =  ET.SubElement(self.root, 'unit')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'rekening')
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_greeting, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_greeting, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_greeting, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "perubahan").text = row.perubahan
            ET.SubElement(xml_greeting, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_greeting, "jumlah3").text = unicode(row.jumlah3)
            ET.SubElement(xml_greeting, "trw1").text = unicode(row.trw1)
            ET.SubElement(xml_greeting, "trw2").text = unicode(row.trw2)
            ET.SubElement(xml_greeting, "trw3").text = unicode(row.trw3)
            ET.SubElement(xml_greeting, "trw4").text = unicode(row.trw4)            
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r306Generator(JasperGenerator):
    def __init__(self):
        super(r306Generator, self).__init__()
        self.reportname = get_rpath('apbd/R3310.jrxml')
        self.xpath = '/apbd/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'rekening')
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.kegiatan_sub_id)
            ET.SubElement(xml_a, "perubahan").text = row.perubahan
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_a, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_a, "selisih").text = unicode(row.jumlah2-row.jumlah1)
            ET.SubElement(xml_a, "persen").text = unicode((row.jumlah2-row.jumlah1)*100/row.jumlah1)
            ET.SubElement(xml_a, "customer").text = customer
        return self.root

class r307Generator(JasperGenerator):
    def __init__(self):
        super(r307Generator, self).__init__()
        self.reportname = get_rpath('apbd/R3320.jrxml')
        self.xpath = '/apbd/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'rekening')
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.kegiatan_sub_id)
            ET.SubElement(xml_a, "perubahan").text = row.perubahan
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_a, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_a, "selisih").text = unicode(row.jumlah2-row.jumlah1)
            ET.SubElement(xml_a, "persen").text = unicode((row.jumlah2-row.jumlah1)*100/row.jumlah1)
            ET.SubElement(xml_a, "customer").text = customer
        return self.root

class r400Generator(JasperGeneratorWithSubreport):
    def __init__(self):

        self.mainreport = get_rpath('apbd/R4000.jrxml')
        self.subreportlist = []
        self.subreportlist.append(get_rpath('apbd/R4000_subreport1.jrxml'))
        self.subreportlist.append(get_rpath('apbd/R4000_subreport2.jrxml'))
        print self.mainreport,self.subreportlist
        self.xpath = '/apbd/unit'
        
        self.root = ET.Element('apbd')

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'unit')

        for row in tobegreeted:
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_id").text = unicode(row.unit_id)
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "customer").text = customer

            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                (KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml3'),
                (KegiatanItem.vol_4_1* KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jml4'))\
                .filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                    KegiatanItem.rekening_id==Rekening.id,
                    KegiatanSub.tahun_id==row.tahun_id,
                    KegiatanSub.unit_id==row.unit_id)\
                .subquery()

            rowrek = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),
                Rekening.level_id, Rekening.defsign, 
                func.sum(subq1.c.jml3).label('jumlah3'),func.sum(subq1.c.jml4).label('jumlah4'))\
                .filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)))\
                .group_by(Rekening.kode, Rekening.nama,
                Rekening.level_id, Rekening.defsign)\
                .order_by(Rekening.kode).all()

            for row2 in rowrek :
                xml_b = ET.SubElement(xml_a, "rekening")
                ET.SubElement(xml_b, "rek_kd").text =row2.rek_kd
                ET.SubElement(xml_b, "rek_nm").text =row2.rek_nm
                ET.SubElement(xml_b, "level_id").text =unicode(row2.level_id)
                ET.SubElement(xml_b, "defsign").text =unicode(row2.defsign)
                ET.SubElement(xml_b, "jumlah3").text =unicode(row2.jumlah3)
                ET.SubElement(xml_b, "jumlah4").text =unicode(row2.jumlah4)
                
            rowtrw = DBSession.query(Kegiatan.kode.label('kode'),
                 func.sum(KegiatanItem.bln01+KegiatanItem.bln02+KegiatanItem.bln03).label('trw1'),
                 func.sum(KegiatanItem.bln04+KegiatanItem.bln05+KegiatanItem.bln06).label('trw2'),
                 func.sum(KegiatanItem.bln07+KegiatanItem.bln08+KegiatanItem.bln09).label('trw3'),
                 func.sum(KegiatanItem.bln10+KegiatanItem.bln11+KegiatanItem.bln12).label('trw4')
                 ).filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                    KegiatanSub.kegiatan_id==Kegiatan.id,
                    KegiatanSub.tahun_id==row.tahun_id,
                    KegiatanSub.unit_id==row.unit_id
                 ).group_by(Kegiatan.kode
                 ).order_by(Kegiatan.kode)

            for row3 in rowtrw :
                xml_c = ET.SubElement(xml_a, "twl")
                ET.SubElement(xml_c, "kode").text =unicode(row3.kode)
                ET.SubElement(xml_c, "trw1").text =unicode(row3.trw1)
                ET.SubElement(xml_c, "trw2").text =unicode(row3.trw2)
                ET.SubElement(xml_c, "trw3").text =unicode(row3.trw3)
                ET.SubElement(xml_c, "trw4").text =unicode(row3.trw4)
                
        return self.root

class r401Generator(JasperGenerator):
    def __init__(self):
        super(r401Generator, self).__init__()
        self.reportname = get_rpath('apbd/R4100.jrxml')
        self.xpath = '/apbd/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'rekening')
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.kegiatan_sub_id)
            ET.SubElement(xml_a, "perubahan").text = row.perubahan
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_a, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_a, "selisih").text = unicode(row.jumlah2-row.jumlah1)
            ET.SubElement(xml_a, "persen").text = unicode((row.jumlah2-row.jumlah1)*100/row.jumlah1)
            ET.SubElement(xml_a, "trw1").text = unicode(row.trw1)
            ET.SubElement(xml_a, "trw2").text = unicode(row.trw2)
            ET.SubElement(xml_a, "trw3").text = unicode(row.trw3)
            ET.SubElement(xml_a, "trw4").text = unicode(row.trw4)
            ET.SubElement(xml_a, "customer").text = customer
            ET.SubElement(xml_a, "logo").text = logo
        return self.root

class r4011Generator(JasperGeneratorWithSubreport):
    def __init__(self):
        self.mainreport = get_rpath('apbd/R4100_1.jrxml')

        self.subreportlist = []
        #self.subreportlist.append(get_rpath('apbd/R3_1_subreport1.jrxml'))

        self.xpath = '/apbd/kegiatan'
        self.root = ET.Element('apbd')

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'kegiatan')
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "kegiatan_kd").text = row.kegiatan_kd
            ET.SubElement(xml_a, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_a, "sdana").text = row.sdana
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.id)
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "no_urut").text = unicode(row.no_urut)
            ET.SubElement(xml_a, "item_nm").text = row.item_nm
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)            
            ET.SubElement(xml_a, "volume11").text = unicode(row.volume11)
            ET.SubElement(xml_a, "satuan11").text = row.satuan11
            ET.SubElement(xml_a, "volume12").text = unicode(row.volume12)
            ET.SubElement(xml_a, "satuan12").text = row.satuan12
            ET.SubElement(xml_a, "harga1").text = unicode(row.harga1)
            ET.SubElement(xml_a, "anggaran1").text = unicode(row.anggaran1)            
            ET.SubElement(xml_a, "volume21").text = unicode(row.volume21)
            ET.SubElement(xml_a, "satuan21").text = row.satuan21
            ET.SubElement(xml_a, "volume22").text = unicode(row.volume22)
            ET.SubElement(xml_a, "satuan22").text = row.satuan22
            ET.SubElement(xml_a, "harga2").text = unicode(row.harga2)
            ET.SubElement(xml_a, "anggaran2").text = unicode(row.anggaran2)            
            ET.SubElement(xml_a, "customer").text = customer
        return self.root

class r402Generator(JasperGenerator):
    def __init__(self):
        super(r402Generator, self).__init__()
        self.reportname = get_rpath('apbd/R4210.jrxml')
        self.xpath = '/apbd/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'rekening')
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.kegiatan_sub_id)
            ET.SubElement(xml_a, "perubahan").text = row.perubahan
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_a, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_a, "selisih").text = unicode(row.jumlah2-row.jumlah1)
            ET.SubElement(xml_a, "persen").text = unicode((row.jumlah2-row.jumlah1)*100/row.jumlah1)
            ET.SubElement(xml_a, "trw1").text = unicode(row.trw1)
            ET.SubElement(xml_a, "trw2").text = unicode(row.trw2)
            ET.SubElement(xml_a, "trw3").text = unicode(row.trw3)
            ET.SubElement(xml_a, "trw4").text = unicode(row.trw4)
            ET.SubElement(xml_a, "customer").text = customer
            ET.SubElement(xml_a, "logo").text = logo
        return self.root

class r403Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r403Generator, self).__init__()
        self.reportname = get_rpath('apbd/R4220.jrxml')
        self.xpath = '/apbd/unit/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        xml_a  =  ET.SubElement(self.root, 'unit')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'rekening')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_greeting, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_greeting, "unit_id").text = unicode(row.unit_id)
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "program_kd").text = row.program_kd
            ET.SubElement(xml_greeting, "program_nm").text = row.program_nm
            ET.SubElement(xml_greeting, "kegiatan_kd").text = row.kegiatan_kd
            ET.SubElement(xml_greeting, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_greeting, "lokasi").text = row.lokasi
            ET.SubElement(xml_greeting, "target").text = row.target
            ET.SubElement(xml_greeting, "jumlah3").text = unicode(row.jumlah3)
            ET.SubElement(xml_greeting, "jumlah4").text = unicode(row.jumlah4)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r404Generator(JasperGeneratorWithSubreport):
    def __init__(self):
        self.mainreport = get_rpath('apbd/R4221.jrxml')

        self.subreportlist = []
        self.subreportlist.append(get_rpath('apbd/R4221_subreport1.jrxml'))
        self.subreportlist.append(get_rpath('apbd/R4221_subreport2.jrxml'))
        self.subreportlist.append(get_rpath('apbd/R4221_subreport3.jrxml'))

        print self.mainreport,self.subreportlist
        self.xpath = '/apbd/kegiatan'
        
        self.root = ET.Element('apbd')

    def generate_xml(self, tobegreeted):
        xml_a  =  ET.SubElement(self.root, 'kegiatan')
        
        for row in tobegreeted:
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun_id)
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
            ET.SubElement(xml_a, "sasaran").text = row.sasaran
            ET.SubElement(xml_a, "sdana").text = row.sdana
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.id)
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "anggaran1").text = unicode(row.anggaran1)
            ET.SubElement(xml_a, "anggaran2").text = unicode(row.anggaran2)
            ET.SubElement(xml_a, "logo").text = logo
            
            ET.SubElement(xml_a, "customer").text = customer
            rows = DBSession.query(KegiatanIndikator)\
              .filter(KegiatanIndikator.kegiatan_sub_id==row.id)\
              .order_by(KegiatanIndikator.tipe,KegiatanIndikator.no_urut)
            for row2 in rows :
                xml_b = ET.SubElement(xml_a, "indikator")
                ET.SubElement(xml_b, "tipe").text =unicode(row2.tipe)
                ET.SubElement(xml_b, "no_urut").text =unicode(row2.no_urut)
                ET.SubElement(xml_b, "tolok_ukur_1").text =row2.tolok_ukur_3
                ET.SubElement(xml_b, "volume_1").text =unicode(row2.volume_3)
                ET.SubElement(xml_b, "satuan_1").text =row2.satuan_3
                ET.SubElement(xml_b, "tolok_ukur_2").text =row2.tolok_ukur_4
                ET.SubElement(xml_b, "volume_2").text =unicode(row2.volume_4)
                ET.SubElement(xml_b, "satuan_2").text =row2.satuan_4
            
            subq1 = DBSession.query(Rekening.kode.label('subrek_kd'),Rekening.nama.label('subrek_nm'),
                    Kegiatan.nama.label('keg_nm'),
                    func.sum(KegiatanItem.vol_3_1* KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('jml1'),
                    func.sum(KegiatanItem.vol_4_1* KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('jml2'),
                    ).join(KegiatanItem).join(KegiatanSub).join(Kegiatan
                    ).filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                            KegiatanItem.rekening_id==Rekening.id,
                            KegiatanItem.kegiatan_sub_id==row.id
                    ).group_by(Rekening.kode,Rekening.nama,Kegiatan.nama
                    ).subquery()

            rowitems = DBSession.query(Rekening.kode.label('rek_kd'), Rekening.nama.label('rek_nm'),Rekening.level_id,
                    subq1.c.keg_nm,
                    func.sum(subq1.c.jml1).label('jumlah1'),
                    func.sum(subq1.c.jml2).label('jumlah2'),
                    ).filter(Rekening.kode==func.left(subq1.c.subrek_kd, func.length(Rekening.kode)))\
                    .group_by(Rekening.kode, Rekening.nama, subq1.c.keg_nm, Rekening.level_id)\
                    .order_by(Rekening.kode).all()                    

            for row3 in rowitems :
                xml_c = ET.SubElement(xml_a, "item")
                ET.SubElement(xml_c, "rek_kd").text =row3.rek_kd
                ET.SubElement(xml_c, "rek_nm").text =row3.rek_nm
                ET.SubElement(xml_c, "keg_nm").text =row3.keg_nm
                ET.SubElement(xml_c, "level_id").text =unicode(row3.level_id)
                ET.SubElement(xml_c, "jumlah1").text =unicode(row3.jumlah1)
                ET.SubElement(xml_c, "jumlah2").text =unicode(row3.jumlah2)

            rowtrw = DBSession.query(func.sum(KegiatanItem.bln01+KegiatanItem.bln02+KegiatanItem.bln03).label('jmltrw1'),
                    func.sum(KegiatanItem.bln04+KegiatanItem.bln05+KegiatanItem.bln06).label('jmltrw2'),
                    func.sum(KegiatanItem.bln07+KegiatanItem.bln08+KegiatanItem.bln09).label('jmltrw3'),
                    func.sum(KegiatanItem.bln10+KegiatanItem.bln11+KegiatanItem.bln12).label('jmltrw4'))\
                    .filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                            KegiatanSub.unit_id==row.unit_id,
                            KegiatanSub.tahun_id==row.tahun_id,
                            KegiatanItem.kegiatan_sub_id==row.id)\

            for row4 in rowtrw :
                xml_d = ET.SubElement(xml_a, "trw")
                ET.SubElement(xml_d, "jmltrw1").text =unicode(row4.jmltrw1)
                ET.SubElement(xml_d, "jmltrw2").text =unicode(row4.jmltrw2)
                ET.SubElement(xml_d, "jmltrw3").text =unicode(row4.jmltrw3)
                ET.SubElement(xml_d, "jmltrw4").text =unicode(row4.jmltrw4)

        return self.root

class r4041Generator(JasperGeneratorWithSubreport):
    def __init__(self):
        self.mainreport = get_rpath('apbd/R4221_1.jrxml')

        self.subreportlist = []
        #self.subreportlist.append(get_rpath('apbd/R1221_4_subreport1.jrxml'))

        print self.mainreport,self.subreportlist
        self.xpath = '/apbd/kegiatan'
        
        self.root = ET.Element('apbd')

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'kegiatan')
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "program_kd").text = row.program_kd
            ET.SubElement(xml_a, "program_nm").text = row.program_nm
            ET.SubElement(xml_a, "kegiatan_kd").text = row.kegiatan_kd
            ET.SubElement(xml_a, "kegiatan_nm").text = row.kegiatan_nm
            ET.SubElement(xml_a, "sdana").text = row.sdana
            ET.SubElement(xml_a, "lokasi").text = row.lokasi
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.id)
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "no_urut").text = unicode(row.no_urut)
            ET.SubElement(xml_a, "item_nm").text = row.item_nm
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "volume11").text = unicode(row.volume11)
            ET.SubElement(xml_a, "satuan11").text = row.satuan11
            ET.SubElement(xml_a, "volume12").text = unicode(row.volume12)
            ET.SubElement(xml_a, "satuan12").text = row.satuan12
            ET.SubElement(xml_a, "harga1").text = unicode(row.harga1)
            ET.SubElement(xml_a, "anggaran1").text = unicode(row.anggaran1)            
            ET.SubElement(xml_a, "volume21").text = unicode(row.volume21)
            ET.SubElement(xml_a, "satuan21").text = row.satuan21
            ET.SubElement(xml_a, "volume22").text = unicode(row.volume22)
            ET.SubElement(xml_a, "satuan22").text = row.satuan22
            ET.SubElement(xml_a, "harga2").text = unicode(row.harga2)
            ET.SubElement(xml_a, "anggaran2").text = unicode(row.anggaran2)            
            ET.SubElement(xml_a, "customer").text = customer
        return self.root

class r405Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r405Generator, self).__init__()
        self.reportname = get_rpath('apbd/R4300.jrxml')
        self.xpath = '/apbd/unit/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        xml_a  =  ET.SubElement(self.root, 'unit')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(xml_a, 'rekening')
            ET.SubElement(xml_greeting, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_greeting, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_greeting, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_greeting, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_greeting, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_greeting, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_greeting, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_greeting, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_greeting, "perubahan").text = row.perubahan
            ET.SubElement(xml_greeting, "jumlah3").text = unicode(row.jumlah3)
            ET.SubElement(xml_greeting, "jumlah4").text = unicode(row.jumlah4)
            ET.SubElement(xml_greeting, "trw1").text = unicode(row.trw1)
            ET.SubElement(xml_greeting, "trw2").text = unicode(row.trw2)
            ET.SubElement(xml_greeting, "trw3").text = unicode(row.trw3)
            ET.SubElement(xml_greeting, "trw4").text = unicode(row.trw4)            
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r406Generator(JasperGenerator):
    def __init__(self):
        super(r406Generator, self).__init__()
        self.reportname = get_rpath('apbd/R4310.jrxml')
        self.xpath = '/apbd/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'rekening')
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.kegiatan_sub_id)
            ET.SubElement(xml_a, "perubahan").text = row.perubahan
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_a, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_a, "selisih").text = unicode(row.jumlah2-row.jumlah1)
            ET.SubElement(xml_a, "persen").text = unicode((row.jumlah2-row.jumlah1)*100/row.jumlah1)
            ET.SubElement(xml_a, "trw1").text = unicode(row.trw1)
            ET.SubElement(xml_a, "trw2").text = unicode(row.trw2)
            ET.SubElement(xml_a, "trw3").text = unicode(row.trw3)
            ET.SubElement(xml_a, "trw4").text = unicode(row.trw4)
            ET.SubElement(xml_a, "customer").text = customer
            ET.SubElement(xml_a, "logo").text = logo
        return self.root

class r407Generator(JasperGenerator):
    def __init__(self):
        super(r407Generator, self).__init__()
        self.reportname = get_rpath('apbd/R4320.jrxml')
        self.xpath = '/apbd/rekening'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'rekening')
            ET.SubElement(xml_a, "rek_kd").text = row.rek_kd
            ET.SubElement(xml_a, "rek_nm").text = row.rek_nm
            ET.SubElement(xml_a, "level_id").text = unicode(row.level_id)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun)
            ET.SubElement(xml_a, "kegiatan_sub_id").text = unicode(row.kegiatan_sub_id)
            ET.SubElement(xml_a, "perubahan").text = row.perubahan
            ET.SubElement(xml_a, "tanggal").text = unicode(row.tanggal)
            ET.SubElement(xml_a, "jumlah1").text = unicode(row.jumlah1)
            ET.SubElement(xml_a, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_a, "selisih").text = unicode(row.jumlah2-row.jumlah1)
            ET.SubElement(xml_a, "persen").text = unicode((row.jumlah2-row.jumlah1)*100/row.jumlah1)
            ET.SubElement(xml_a, "trw1").text = unicode(row.trw1)
            ET.SubElement(xml_a, "trw2").text = unicode(row.trw2)
            ET.SubElement(xml_a, "trw3").text = unicode(row.trw3)
            ET.SubElement(xml_a, "trw4").text = unicode(row.trw4)
            ET.SubElement(xml_a, "customer").text = customer
            ET.SubElement(xml_a, "logo").text = logo
        return self.root

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
            ET.SubElement(xml_greeting, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_greeting, "customer").text = customer
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
            ET.SubElement(xml_greeting, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_greeting, "customer").text = customer
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
            ET.SubElement(xml_greeting, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_greeting, "customer").text = customer
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
            ET.SubElement(xml_a, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_a, "customer").text = customer
            
            rows = DBSession.query(KegiatanIndikator)\
              .filter(KegiatanIndikator.kegiatan_sub_id==row.kegiatan_sub_id,
              KegiatanIndikator.tipe==4)\
              .order_by(KegiatanIndikator.tipe,KegiatanIndikator.no_urut)
            for row2 in rows :
                xml_b = ET.SubElement(xml_a, "indikator")
                ET.SubElement(xml_b, "tipe").text =unicode(row2.tipe)
                ET.SubElement(xml_b, "no_urut").text =unicode(row2.no_urut)
                ET.SubElement(xml_b, "tolok_ukur_1").text =row2.tolok_ukur_2
                ET.SubElement(xml_b, "volume_1").text =unicode(row2.volume_2)
                ET.SubElement(xml_b, "satuan_1").text =row2.satuan_2
            
            rowhkm = DBSession.query(DasarHukum.no_urut,DasarHukum.nama)\
               .filter(DasarHukum.rekening_id==row.rekening_id)\
               .order_by(DasarHukum.no_urut)
                
            for row3 in rowhkm :
                xml_c = ET.SubElement(xml_a, "hukum")
                ET.SubElement(xml_c, "no_urut").text =unicode(row3.no_urut)
                ET.SubElement(xml_c, "uraian").text =row3.nama
                #print "XXXXX"+row3.nama

            rowitem = DBSession.query(KegiatanItem.kode.label('item_kd'), KegiatanItem.nama.label('item_nm'),
               (KegiatanItem.vol_1_1*KegiatanItem.vol_1_2).label('volume1'),
               (KegiatanItem.vol_2_1*KegiatanItem.vol_2_2).label('volume2'),
               (KegiatanItem.vol_3_1*KegiatanItem.vol_3_2).label('volume3'),
               (KegiatanItem.vol_4_1*KegiatanItem.vol_4_2).label('volume4'),
               KegiatanItem.hsat_1.label('harga1'),KegiatanItem.hsat_2.label('harga2'),
               KegiatanItem.hsat_3.label('harga3'),KegiatanItem.hsat_4.label('harga4'),
               KegiatanItem.sat_1_1.label('satuan11'),KegiatanItem.sat_1_2.label('satuan12'),
               KegiatanItem.sat_2_1.label('satuan21'),KegiatanItem.sat_2_2.label('satuan22'),
               KegiatanItem.sat_3_1.label('satuan31'),KegiatanItem.sat_3_2.label('satuan32'),
               KegiatanItem.sat_4_1.label('satuan41'),KegiatanItem.sat_4_2.label('satuan42'))\
               .filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                   KegiatanItem.rekening_id==Rekening.id,
                   KegiatanItem.rekening_id==row.rekening_id,
                   KegiatanSub.tahun_id==row.tahun,
                   KegiatanSub.unit_id==row.unit_id)\
               .order_by(KegiatanItem.kode)
            
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
            ET.SubElement(xml_greeting, "kode").text = row.kode
            ET.SubElement(xml_greeting, "jumlah").text = unicode(row.jumlah)
            ET.SubElement(xml_greeting, "customer").text = customer
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
            ET.SubElement(xml_greeting, "jml_btlpeg").text = unicode(row.jml_btlpeg)
            ET.SubElement(xml_greeting, "jml_btlnonpeg").text = unicode(row.jml_btlnonpeg)
            ET.SubElement(xml_greeting, "jml_blpeg").text = unicode(row.jml_blpeg)
            ET.SubElement(xml_greeting, "jml_bljasa").text = unicode(row.jml_bljasa)
            ET.SubElement(xml_greeting, "jml_blmodal").text = unicode(row.jml_blmodal)
            ET.SubElement(xml_greeting, "customer").text = customer
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
            ET.SubElement(xml_greeting, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_greeting, "customer").text = customer
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
            ET.SubElement(xml_greeting, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_greeting, "customer").text = customer
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
            ET.SubElement(xml_a, "jumlah2").text = unicode(row.jumlah2)
            ET.SubElement(xml_a, "customer").text = customer
            
            rows = DBSession.query(KegiatanIndikator)\
              .filter(KegiatanIndikator.kegiatan_sub_id==row.kegiatan_sub_id,
              KegiatanIndikator.tipe==4)\
              .order_by(KegiatanIndikator.tipe,KegiatanIndikator.no_urut)
            for row2 in rows :
                xml_b = ET.SubElement(xml_a, "indikator")
                ET.SubElement(xml_b, "tipe").text =unicode(row2.tipe)
                ET.SubElement(xml_b, "no_urut").text =unicode(row2.no_urut)
                ET.SubElement(xml_b, "tolok_ukur_1").text =row2.tolok_ukur_2
                ET.SubElement(xml_b, "volume_1").text =unicode(row2.volume_2)
                ET.SubElement(xml_b, "satuan_1").text =row2.satuan_2
            
            rowhkm = DBSession.query(DasarHukum.no_urut,DasarHukum.nama)\
               .filter(DasarHukum.rekening_id==row.rekening_id)\
               .order_by(DasarHukum.no_urut)
                
            for row3 in rowhkm :
                xml_c = ET.SubElement(xml_a, "hukum")
                ET.SubElement(xml_c, "no_urut").text =unicode(row3.no_urut)
                ET.SubElement(xml_c, "uraian").text =row3.nama
                #print "XXXXX"+row3.nama

            rowitem = DBSession.query(KegiatanItem.kode.label('item_kd'), KegiatanItem.nama.label('item_nm'),
               (KegiatanItem.vol_1_1*KegiatanItem.vol_1_2).label('volume1'),
               (KegiatanItem.vol_2_1*KegiatanItem.vol_2_2).label('volume2'),
               (KegiatanItem.vol_3_1*KegiatanItem.vol_3_2).label('volume3'),
               (KegiatanItem.vol_4_1*KegiatanItem.vol_4_2).label('volume4'),
               KegiatanItem.hsat_1.label('harga1'),KegiatanItem.hsat_2.label('harga2'),
               KegiatanItem.hsat_3.label('harga3'),KegiatanItem.hsat_4.label('harga4'),
               KegiatanItem.sat_1_1.label('satuan11'),KegiatanItem.sat_1_2.label('satuan12'),
               KegiatanItem.sat_2_1.label('satuan21'),KegiatanItem.sat_2_2.label('satuan22'),
               KegiatanItem.sat_3_1.label('satuan31'),KegiatanItem.sat_3_2.label('satuan32'),
               KegiatanItem.sat_4_1.label('satuan41'),KegiatanItem.sat_4_2.label('satuan42'))\
               .filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                   KegiatanItem.rekening_id==Rekening.id,
                   KegiatanItem.rekening_id==row.rekening_id,
                   KegiatanSub.tahun_id==row.tahun,
                   KegiatanSub.unit_id==row.unit_id)\
               .order_by(KegiatanItem.kode)
            
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

class r600Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r600Generator, self).__init__()
        self.reportname = get_rpath('apbd/R6000.jrxml')
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
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r6001Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r6001Generator, self).__init__()
        self.reportname = get_rpath('apbd/R60001.jrxml')
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
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r601Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r601Generator, self).__init__()
        self.reportname = get_rpath('apbd/R6001.jrxml')
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
            ET.SubElement(xml_greeting, "customer").text = customer
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

class r602Generator(JasperGeneratorWithSubreport):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        self.mainreport = get_rpath('apbd/R6002.jrxml')
        self.subreportlist = []
        self.subreportlist.append(get_rpath('apbd/R6002_subreport1.jrxml'))
        self.subreportlist.append(get_rpath('apbd/R6002_subreport2.jrxml'))
        self.subreportlist.append(get_rpath('apbd/R6002_subreport3.jrxml'))
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
            ET.SubElement(xml_a, "customer").text = customer
            
            rows = DBSession.query(KegiatanIndikator)\
              .filter(KegiatanIndikator.kegiatan_sub_id==row.kegiatan_sub_id,
              KegiatanIndikator.tipe==4)\
              .order_by(KegiatanIndikator.tipe,KegiatanIndikator.no_urut)
            for row2 in rows :
                xml_b = ET.SubElement(xml_a, "indikator")
                ET.SubElement(xml_b, "tipe").text =unicode(row2.tipe)
                ET.SubElement(xml_b, "no_urut").text =unicode(row2.no_urut)
                ET.SubElement(xml_b, "tolok_ukur_1").text =row2.tolok_ukur_4
                ET.SubElement(xml_b, "volume_1").text =unicode(row2.volume_4)
                ET.SubElement(xml_b, "satuan_1").text =row2.satuan_4
            
            rowhkm = DBSession.query(DasarHukum.no_urut,DasarHukum.nama)\
               .filter(DasarHukum.rekening_id==row.rekening_id)\
               .order_by(DasarHukum.no_urut)
                
            for row3 in rowhkm :
                xml_c = ET.SubElement(xml_a, "hukum")
                ET.SubElement(xml_c, "no_urut").text =unicode(row3.no_urut)
                ET.SubElement(xml_c, "uraian").text =row3.nama
                #print "XXXXX"+row3.nama

            rowitem = DBSession.query(KegiatanItem.kode.label('item_kd'), KegiatanItem.nama.label('item_nm'),
               (KegiatanItem.vol_1_1*KegiatanItem.vol_1_2).label('volume1'),
               (KegiatanItem.vol_2_1*KegiatanItem.vol_2_2).label('volume2'),
               (KegiatanItem.vol_3_1*KegiatanItem.vol_3_2).label('volume3'),
               (KegiatanItem.vol_4_1*KegiatanItem.vol_4_2).label('volume4'),
               KegiatanItem.hsat_1.label('harga1'),KegiatanItem.hsat_2.label('harga2'),
               KegiatanItem.hsat_3.label('harga3'),KegiatanItem.hsat_4.label('harga4'),
               KegiatanItem.sat_1_1.label('satuan11'),KegiatanItem.sat_1_2.label('satuan12'),
               KegiatanItem.sat_2_1.label('satuan21'),KegiatanItem.sat_2_2.label('satuan22'),
               KegiatanItem.sat_3_1.label('satuan31'),KegiatanItem.sat_3_2.label('satuan32'),
               KegiatanItem.sat_4_1.label('satuan41'),KegiatanItem.sat_4_2.label('satuan42'))\
               .filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                   KegiatanItem.rekening_id==Rekening.id,
                   KegiatanItem.rekening_id==row.rekening_id,
                   KegiatanSub.tahun_id==row.tahun,
                   KegiatanSub.unit_id==row.unit_id)\
               .order_by(KegiatanItem.kode)
            
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

class r603Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r603Generator, self).__init__()
        self.reportname = get_rpath('apbd/R6003.jrxml')
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
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r604Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r604Generator, self).__init__()
        self.reportname = get_rpath('apbd/R6004.jrxml')
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
            ET.SubElement(xml_greeting, "jml_btlpeg1").text = unicode(row.jml_btlpeg1)
            ET.SubElement(xml_greeting, "jml_btlnonpeg1").text = unicode(row.jml_btlnonpeg1)
            ET.SubElement(xml_greeting, "jml_blpeg1").text = unicode(row.jml_blpeg1)
            ET.SubElement(xml_greeting, "jml_bljasa1").text = unicode(row.jml_bljasa1)
            ET.SubElement(xml_greeting, "jml_blmodal1").text = unicode(row.jml_blmodal1)
            ET.SubElement(xml_greeting, "jml_btlpeg2").text = unicode(row.jml_btlpeg2)
            ET.SubElement(xml_greeting, "jml_btlnonpeg2").text = unicode(row.jml_btlnonpeg2)
            ET.SubElement(xml_greeting, "jml_blpeg2").text = unicode(row.jml_blpeg2)
            ET.SubElement(xml_greeting, "jml_bljasa2").text = unicode(row.jml_bljasa2)
            ET.SubElement(xml_greeting, "jml_blmodal2").text = unicode(row.jml_blmodal2)
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r621Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r621Generator, self).__init__()
        self.reportname = get_rpath('apbd/R6005.jrxml')
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
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r6211Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r6211Generator, self).__init__()
        self.reportname = get_rpath('apbd/R60051.jrxml')
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
            ET.SubElement(xml_greeting, "customer").text = customer
        return self.root

class r622Generator(JasperGeneratorWithSubreport):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        self.mainreport = get_rpath('apbd/R6006.jrxml')
        self.subreportlist = []
        self.subreportlist.append(get_rpath('apbd/R6006_subreport1.jrxml'))
        self.subreportlist.append(get_rpath('apbd/R6006_subreport2.jrxml'))
        self.subreportlist.append(get_rpath('apbd/R6006_subreport3.jrxml'))
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
            ET.SubElement(xml_a, "customer").text = customer
            
            rows = DBSession.query(KegiatanIndikator)\
              .filter(KegiatanIndikator.kegiatan_sub_id==row.kegiatan_sub_id,
              KegiatanIndikator.tipe==4)\
              .order_by(KegiatanIndikator.tipe,KegiatanIndikator.no_urut)
            for row2 in rows :
                xml_b = ET.SubElement(xml_a, "indikator")
                ET.SubElement(xml_b, "tipe").text =unicode(row2.tipe)
                ET.SubElement(xml_b, "no_urut").text =unicode(row2.no_urut)
                ET.SubElement(xml_b, "tolok_ukur_1").text =row2.tolok_ukur_2
                ET.SubElement(xml_b, "volume_1").text =unicode(row2.volume_2)
                ET.SubElement(xml_b, "satuan_1").text =row2.satuan_2
            
            rowhkm = DBSession.query(DasarHukum.no_urut,DasarHukum.nama)\
               .filter(DasarHukum.rekening_id==row.rekening_id)\
               .order_by(DasarHukum.no_urut)
                
            for row3 in rowhkm :
                xml_c = ET.SubElement(xml_a, "hukum")
                ET.SubElement(xml_c, "no_urut").text =unicode(row3.no_urut)
                ET.SubElement(xml_c, "uraian").text =row3.nama
                #print "XXXXX"+row3.nama

            rowitem = DBSession.query(KegiatanItem.kode.label('item_kd'), KegiatanItem.nama.label('item_nm'),
               (KegiatanItem.vol_1_1*KegiatanItem.vol_1_2).label('volume1'),
               (KegiatanItem.vol_2_1*KegiatanItem.vol_2_2).label('volume2'),
               (KegiatanItem.vol_3_1*KegiatanItem.vol_3_2).label('volume3'),
               (KegiatanItem.vol_4_1*KegiatanItem.vol_4_2).label('volume4'),
               KegiatanItem.hsat_1.label('harga1'),KegiatanItem.hsat_2.label('harga2'),
               KegiatanItem.hsat_3.label('harga3'),KegiatanItem.hsat_4.label('harga4'),
               KegiatanItem.sat_1_1.label('satuan11'),KegiatanItem.sat_1_2.label('satuan12'),
               KegiatanItem.sat_2_1.label('satuan21'),KegiatanItem.sat_2_2.label('satuan22'),
               KegiatanItem.sat_3_1.label('satuan31'),KegiatanItem.sat_3_2.label('satuan32'),
               KegiatanItem.sat_4_1.label('satuan41'),KegiatanItem.sat_4_2.label('satuan42'))\
               .filter(KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                   KegiatanItem.rekening_id==Rekening.id,
                   KegiatanItem.rekening_id==row.rekening_id,
                   KegiatanSub.tahun_id==row.tahun,
                   KegiatanSub.unit_id==row.unit_id)\
               .order_by(KegiatanItem.kode)
            
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

class r700Generator(JasperGenerator):
    def __init__(self):
        super(r700Generator, self).__init__()
        self.reportname = get_rpath('apbd/R7000.jrxml')
        self.xpath = '/apbd/budget'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'budget')
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_a, "urut1").text = unicode(row.urut1)
            ET.SubElement(xml_a, "urut2").text = unicode(row.urut2)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "program_kd").text = row.program_kd
            ET.SubElement(xml_a, "program_nm").text = row.program_nm
            ET.SubElement(xml_a, "keg_kd").text = row.keg_kd
            ET.SubElement(xml_a, "keg_nm").text = row.keg_nm
            ET.SubElement(xml_a, "anggaran").text = unicode(row.anggaran)
            ET.SubElement(xml_a, "bln01").text = unicode(row.bln01)
            ET.SubElement(xml_a, "bln02").text = unicode(row.bln02)
            ET.SubElement(xml_a, "bln03").text = unicode(row.bln03)
            ET.SubElement(xml_a, "bln04").text = unicode(row.bln04)
            ET.SubElement(xml_a, "bln05").text = unicode(row.bln05)
            ET.SubElement(xml_a, "bln06").text = unicode(row.bln06)
            ET.SubElement(xml_a, "bln07").text = unicode(row.bln07)
            ET.SubElement(xml_a, "bln08").text = unicode(row.bln08)
            ET.SubElement(xml_a, "bln09").text = unicode(row.bln09)
            ET.SubElement(xml_a, "bln10").text = unicode(row.bln10)
            ET.SubElement(xml_a, "bln11").text = unicode(row.bln11)
            ET.SubElement(xml_a, "bln12").text = unicode(row.bln12)
            ET.SubElement(xml_a, "customer").text = customer
        return self.root

class r701Generator(JasperGenerator):
    def __init__(self):
        super(r701Generator, self).__init__()
        self.reportname = get_rpath('apbd/R7001.jrxml')
        self.xpath = '/apbd/budget'
        self.root = ET.Element('apbd') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_a  =  ET.SubElement(self.root, 'budget')
            ET.SubElement(xml_a, "tahun").text = unicode(row.tahun_id)
            ET.SubElement(xml_a, "urut1").text = unicode(row.urut1)
            ET.SubElement(xml_a, "urut2").text = unicode(row.urut2)
            ET.SubElement(xml_a, "defsign").text = unicode(row.defsign)
            ET.SubElement(xml_a, "urusan_kd").text = row.urusan_kd
            ET.SubElement(xml_a, "urusan_nm").text = row.urusan_nm
            ET.SubElement(xml_a, "unit_kd").text = row.unit_kd
            ET.SubElement(xml_a, "unit_nm").text = row.unit_nm
            ET.SubElement(xml_a, "program_kd").text = row.program_kd
            ET.SubElement(xml_a, "program_nm").text = row.program_nm
            ET.SubElement(xml_a, "keg_kd").text = row.keg_kd
            ET.SubElement(xml_a, "keg_nm").text = row.keg_nm
            ET.SubElement(xml_a, "anggaran").text = unicode(row.anggaran)
            ET.SubElement(xml_a, "bln01").text = unicode(row.bln01)
            ET.SubElement(xml_a, "bln02").text = unicode(row.bln02)
            ET.SubElement(xml_a, "bln03").text = unicode(row.bln03)
            ET.SubElement(xml_a, "bln04").text = unicode(row.bln04)
            ET.SubElement(xml_a, "bln05").text = unicode(row.bln05)
            ET.SubElement(xml_a, "bln06").text = unicode(row.bln06)
            ET.SubElement(xml_a, "bln07").text = unicode(row.bln07)
            ET.SubElement(xml_a, "bln08").text = unicode(row.bln08)
            ET.SubElement(xml_a, "bln09").text = unicode(row.bln09)
            ET.SubElement(xml_a, "bln10").text = unicode(row.bln10)
            ET.SubElement(xml_a, "bln11").text = unicode(row.bln11)
            ET.SubElement(xml_a, "bln12").text = unicode(row.bln12)
            ET.SubElement(xml_a, "customer").text = customer
        return self.root

if __name__ == '__main__':
        generator = r001Generator()

        generator.generate([('1','2')])
