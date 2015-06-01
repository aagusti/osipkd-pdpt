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
from osipkd.models.apbd_rka_models import (KegiatanIndikatorModel, KegiatanSubModel, KegiatanItemModel)
from osipkd.models.apbd_admin_models import (TahunModel, UserApbdModel,Unit,
     Urusan, RekeningModel, ProgramModel, KegiatanModel, TapdModel, JabatanModel, PegawaiModel, PejabatModel)
from datetime import datetime
import os
from pyramid.renderers import render_to_response

class AnggaranBaseViews(BaseViews):
    def __init__(self, context, request):
        BaseViews.__init__(self, context, request)
        self.app = 'anggaran'
        #if 'app' in request.params and request.params['app'] == self.app and self.logged:
        row = DBSession.query(TahunModel.status_apbd).filter(TahunModel.tahun==self.tahun).first()
        self.session['status_apbd'] = row and row[0] or 0


        self.status_apbd =  'status_apbd' in self.session and self.session['status_apbd'] or 0        
        self.status_apbd_nm =  status_apbds[str(self.status_apbd)]        
        
        self.all_unit =  'all_unit' in self.session and self.session['all_unit'] or 0        
        self.unit_id  = 'unit_id' in self.session and self.session['unit_id'] or 0
        self.unit_kd  = 'unit_kd' in self.session and self.session['unit_kd'] or "X.XX.XX"
        self.unit_nm  = 'unit_nm' in self.session and self.session['unit_nm'] or "Pilih Unit"
        self.sub_keg_id  = 'sub_keg_id' in self.session and self.session['sub_keg_id'] or 0
        self.tipe     = 'tipe' in self.session and self.session['tipe'] or 0
        
        self.datas['status_apbd'] = self.status_apbd 
        self.datas['status_apbd_nm'] = self.status_apbd_nm
        self.datas['all_unit'] = self.all_unit
        self.datas['unit_kd'] = self.unit_kd
        self.datas['unit_nm'] = self.unit_nm
        self.datas['unit_id'] = self.unit_id
        
class AnggaranViews(AnggaranBaseViews):        

    @view_config(route_name="admin_change_unit", renderer="json")
    def admin_change_unit(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict
        if self.logged and self.session['all_unit']:
            unit_id = 'unit_id' in params and int(params['unit_id']) or 0
            if unit_id > 0:
                self.session['unit_id'] = unit_id
                row = DBSession.query(Unit).join(Urusan)\
                      .filter(Unit.urusan_id==Urusan.id, \
                              Unit.id==self.session['unit_id']).first()
                self.session['unit_kd'] = row and ''.join([row.urusans.kode,'.',row.kode]) or ""
                self.session['unit_nm'] = row and row.nama or ""
                self.d['msg']='Sukses Ubah Unit'
                self.d['success']=True
            else:
                self.d['msg']='Gagal Ubah Unit'
            return self.d
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            
    @view_config(route_name="admin_get_subkegid", renderer="json")
    def admin_get_subkegid(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict
        if self.logged:
            programkd = "programkd" in  params and params['programkd'] or None
            kegiatankd = "kegiatankd" in  params and params['kegiatankd'] or None
            if programkd and kegiatankd:
                row = DBSession.query(KegiatanSubModel).join(KegiatanModel)\
                      .join(ProgramModel)\
                      .filter(KegiatanSubModel.unit_id==self.unit_id, 
                              KegiatanModel.kode==kegiatankd,
                              ProgramModel.kode==programkd).first()
                if row:
                    self.session['sub_keg_id'] = row.id
                    self.d['success']= True
                    self.d['sub_keg_id'] = row.id
                    self.d['sub_keg_no'] = row.no_urut
                    self.d['sub_keg_nm'] = row.nama
                else:
                    self.d['msg']='Data Pendapatan Tidak Ditemukan'
            else:
                self.session['sub_keg_id'] = 0
                self.d['msg']='Salah parameter'
            return self.d
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_set_subkegid", renderer="json")
    def admin_set_subkegid(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict
        if self.logged:
            programkd = "programkd" in  params and params['programkd'] or None
            kegiatankd = "kegiatankd" in  params and params['kegiatankd'] or None
            urusankd = "urusankd" in  params and params['urusankd'] or None
            if programkd and kegiatankd:
                row = DBSession.query(KegiatanModel.id, KegiatanModel.nama)\
                      .join(ProgramModel)\
                      .join(Urusan)\
                      .filter(Urusan.kode==urusankd,
                              KegiatanModel.kode==kegiatankd,
                              ProgramModel.kode==programkd).first()
                if row:
                    data = {}
                    data['kegiatan_id']= row.id
                    data['kode']       = "".join([urusankd,programkd,kegiatankd])
                    data['nama']       = row.nama 
                    data['id']         = 0
                    data['tahun_id']   = self.tahun
                    data['unit_id']    = self.unit_id
                    data['no_urut']    = KegiatanSubModel.get_no_urut(data)
                    data['create_uid'] = self.user_id
                    data['update_uid'] = self.user_id
                    row_id = KegiatanSubModel.tambah(data)
                    
                    if row_id:
                        self.session['sub_keg_id'] = row_id
                        self.d['success']   = True
                        self.d['sub_keg_id']= row_id
                        self.d['sub_keg_no']= data['no_urut']
                        self.d['sub_keg_nm']= data['nama']
                        self.d['msg']       ='Sukses'
                    else:
                        self.d['msg']       ='Salah parameter'
                else:
                    self.d['msg']='Data Pendapatan Tidak Ditemukan'
                    
            else:
                self.session['sub_keg_id'] = 0
                self.d['msg']='Salah parameter'
            return self.d
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

            
    @view_config(route_name="anggaran", renderer="../../templates/apbd/anggaran/home.pt")
    def anggaran(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

class ViewAnggaran001(AnggaranBaseViews):
    def __init__(self, context, request):
        AnggaranBaseViews.__init__(self, context, request)
        self.session['mod'] = 'A0101'
        
    @view_config(route_name="anggaran_001", renderer="../../templates/apbd/anggaran/001.pt")
    def anggaran_001(self):
        params = self.request.params
        if self.logged and self.is_akses_mod('read'):
            return dict(datas=self.datas)
        else:
            if not self.logged:
                headers=forget(self.request)
                return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            else:
                headers=forget(self.request)
                return HTTPFound(location='/anggaran', headers=headers)

    @view_config(route_name="anggaran_001_frm", renderer="../../templates/apbd/anggaran/001_frm.pt")
    def anggaran_001_frm(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = TahunModel.get_by_id(self.datas['id'])
                if row:
                    rows = TahunModel.row2dict(row)
                    return dict(datas=self.datas, rows=rows)
                else:
                    if self.datas['id']>0:
                        return HTTPNotFound() #TODO: Warning Data Not Found
                return dict(datas=self.datas,rows='')
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="anggaran_001_act", renderer="json")
    def anggaran_001_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('tahun'))
                columns.append(ColumnDT('status_apbd'))
                columns.append(ColumnDT('tgl_entry', filter=self._DTstrftime))
                columns.append(ColumnDT('tgl_evaluasi', filter=self._DTstrftime))
                query = DBSession.query(TahunModel)
                rowTable = DataTables(req, TahunModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    try:
                        rows = TahunModel.update(p)
                    except:
                        pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    try:
                        rows = TahunModel.tambah(p)
                    except:
                        pass
                else:
                    rows={}
                
                if rows:
                    self.d['msg']='Sukses Simpan Data'
                    self.d['success']=True
                else:
                    self.d['msg']='Gagal Simpan Data'
                
                return self.d
                
            elif url_dict['act']=='delete' and self.is_akses_mod('delete'):
                d={}
                d['id'] = pk_id
                rows = TahunModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

            
class ViewAnggaran010(AnggaranBaseViews):
    def __init__(self, context, request):
        AnggaranBaseViews.__init__(self, context, request)
        self.session['mod'] = 'A0201'
        self.session['menu'] = '010'
        
    @view_config(route_name="anggaran_010", renderer="../../templates/apbd/anggaran/010.pt")
    def anggaran_010(self):
        ursKd = "0.00"
        prgKd = "00"
        kegKd = "10"
        params = self.request.params
        self.datas["mod"] = self.session["mod"]
        self.datas["kegiatanKd"] = "urusankd=%s&programkd=%s&kegiatankd=%s" %(ursKd, prgKd,kegKd)
        if self.logged and self.is_akses_mod('read'):
            self.datas['kegiatan'] = DBSession.query(KegiatanModel).\
                       join(ProgramModel).join(Urusan).filter(
                            Urusan.kode==ursKd,
                            ProgramModel.kode==prgKd,
                            KegiatanModel.kode==kegKd 
                            ).first()
            row = DBSession.query(KegiatanSubModel
                      ).filter(KegiatanSubModel.tahun_id == self.tahun,
                               KegiatanSubModel.unit_id == self.unit_id,
                               KegiatanSubModel.kegiatan_id==self.datas['kegiatan'].id
                               ).first()
            if row:
                self.datas['subkegiatan'] = row
                self.session["sub_keg_id"]=row.id
            else:
                self.datas['subkegiatan'] = ""
                self.session["sub_keg_id"]=0
            return dict(datas=self.datas)
        else:
            if not self.logged:
                headers=forget(self.request)
                return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            else:
                headers=forget(self.request)
                return HTTPFound(location='/anggaran', headers=headers)

class ViewAnggaran021(AnggaranBaseViews):
    def __init__(self, context, request):
        AnggaranBaseViews.__init__(self, context, request)
        self.session['mod'] = 'A0202'
        self.session['menu'] = '021'
        print 'MOOOOOOOOOOOOOOOOOOOOOD:',self.session['mod']
        

    @view_config(route_name="anggaran_021", renderer="../../templates/apbd/anggaran/010.pt")
    def anggaran_021(self):
        ursKd = "0.00"
        prgKd = "00"
        kegKd = "21"
        params = self.request.params
        self.datas["mod"] = self.session["mod"]
        self.datas["kegiatanKd"] = "urusankd=%s&programkd=%s&kegiatankd=%s" %(ursKd, prgKd,kegKd)
        
        if self.logged and self.is_akses_mod('read'):
            self.datas['kegiatan'] = DBSession.query(KegiatanModel).\
                       join(ProgramModel).join(Urusan).filter(
                            Urusan.kode==ursKd,
                            ProgramModel.kode==prgKd,
                            KegiatanModel.kode==kegKd 
                            ).first()
            row = DBSession.query(KegiatanSubModel
                      ).filter(KegiatanSubModel.tahun_id == self.tahun,
                               KegiatanSubModel.unit_id == self.unit_id,
                               KegiatanSubModel.kegiatan_id==self.datas['kegiatan'].id
                               ).first()
            if row:
                self.datas['subkegiatan'] = row
                self.session["sub_keg_id"]=row.id
            else:
                self.datas['subkegiatan'] = ""
                self.session["sub_keg_id"]=0
            return dict(datas=self.datas)
        else:
            if not self.logged:
                headers=forget(self.request)
                return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            else:
                headers=forget(self.request)
                return HTTPFound(location='/anggaran', headers=headers)
            
class ViewAnggaran031(AnggaranBaseViews):
    def __init__(self, context, request):
        AnggaranBaseViews.__init__(self, context, request)
        self.session['mod'] = 'A0204'
        self.session['menu'] = '031'

    @view_config(route_name="anggaran_031", renderer="../../templates/apbd/anggaran/010.pt")
    def anggaran_031(self):
        ursKd = "0.00"
        prgKd = "00"
        kegKd = "31"
        params = self.request.params

        self.datas["mod"] = self.session["mod"]
        self.datas["kegiatanKd"] = "urusankd=%s&programkd=%s&kegiatankd=%s" %(ursKd, prgKd,kegKd)
        
        if self.logged and self.is_akses_mod('read'):
            self.datas['kegiatan'] = DBSession.query(KegiatanModel).\
                       join(ProgramModel).join(Urusan).filter(
                            Urusan.kode==ursKd,
                            ProgramModel.kode==prgKd,
                            KegiatanModel.kode==kegKd 
                            ).first()
            row = DBSession.query(KegiatanSubModel
                      ).filter(KegiatanSubModel.tahun_id == self.tahun,
                               KegiatanSubModel.unit_id == self.unit_id,
                               KegiatanSubModel.kegiatan_id==self.datas['kegiatan'].id
                               ).first()
            if row:
                self.datas['subkegiatan'] = row
                self.session["sub_keg_id"]=row.id
            else:
                self.datas['subkegiatan'] = ""
                self.session["sub_keg_id"]=0
            return dict(datas=self.datas)
        else:
            if not self.logged:
                headers=forget(self.request)
                return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            else:
                headers=forget(self.request)
                return HTTPFound(location='/anggaran', headers=headers)
            
class ViewAnggaran032(AnggaranBaseViews):
    def __init__(self, context, request):
        AnggaranBaseViews.__init__(self, context, request)
        self.session['mod'] = 'A0205'
        self.session['menu'] = '032'

    @view_config(route_name="anggaran_032", renderer="../../templates/apbd/anggaran/010.pt")
    def anggaran_032(self):
        ursKd = "0.00"
        prgKd = "00"
        kegKd = "32"
        params = self.request.params

        self.datas["mod"] = self.session["mod"]
        self.datas["kegiatanKd"] = "urusankd=%s&programkd=%s&kegiatankd=%s" %(ursKd, prgKd,kegKd)
        
        if self.logged and self.is_akses_mod('read'):
            self.datas['kegiatan'] = DBSession.query(KegiatanModel).\
                       join(ProgramModel).join(Urusan).filter(
                            Urusan.kode==ursKd,
                            ProgramModel.kode==prgKd,
                            KegiatanModel.kode==kegKd 
                            ).first()
            row = DBSession.query(KegiatanSubModel
                      ).filter(KegiatanSubModel.tahun_id == self.tahun,
                               KegiatanSubModel.unit_id == self.unit_id,
                               KegiatanSubModel.kegiatan_id==self.datas['kegiatan'].id
                               ).first()
            if row:
                self.datas['subkegiatan'] = row
                self.session["sub_keg_id"]=row.id
            else:
                self.datas['subkegiatan'] = ""
                self.session["sub_keg_id"]=0
            return dict(datas=self.datas)
        else:
            if not self.logged:
                headers=forget(self.request)
                return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            else:
                headers=forget(self.request)
                return HTTPFound(location='/anggaran', headers=headers)
           
class ViewAnggaran022(AnggaranBaseViews):
    def __init__(self, context, request):
        AnggaranBaseViews.__init__(self, context, request)
        self.session['mod'] = 'A0203'

    @view_config(route_name="anggaran_022", renderer="../../templates/apbd/anggaran/022.pt")
    def anggaran_022(self):
        params = self.request.params
        if self.logged and self.is_akses_mod('read'):
            return dict(datas=self.datas)
        else:
            if not self.logged:
                headers=forget(self.request)
                return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            else:
                headers=forget(self.request)
                return HTTPFound(location='/anggaran', headers=headers)

    @view_config(route_name="anggaran_022_frm", renderer="../../templates/apbd/anggaran/022_frm.pt")
    def anggaran_022_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        self.datas['pegawai_nama'] = 'pegawai_nama' in params and int(params['pegawai_nama']) or 0
        
        if self.logged and self.is_akses_mod('read'):
            if (not self.datas['id'] and self.is_akses_mod('add'))\
                or (self.datas['id'] and self.is_akses_mod('edit')):
                #row = KegiatanSubModel.get_by_id(self.datas['id'])
                row = DBSession.query(KegiatanSubModel).filter(KegiatanSubModel.id==self.datas['id']).first()
                if row:
                    rows = KegiatanSubModel.row2dict(row)
                    rows['unit_nm'] = row.units.nama
                    rows['kegiatan_nm'] = row.kegiatans.nama
                    return dict(datas=self.datas, rows=rows)
                else:
                    if self.datas['id']>0:
                        return HTTPNotFound() #TODO: Warning Data Not Found
                rows = {}
                #rows['tahun_id'] = self.datas['tahun']
                return dict(datas = self.datas,rows = '')
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            if not self.logged:
                headers=forget(self.request)
                return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            else:
                headers=forget(self.request)
                return HTTPFound(location='/anggaran', headers=headers)
            
    @view_config(route_name="anggaran_022_act", renderer="json")
    def anggaran_022_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged:
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('prg_nm'))
                columns.append(ColumnDT('rka'))
                columns.append(ColumnDT('dpa'))
                columns.append(ColumnDT('rpka'))
                columns.append(ColumnDT('dppa'))
                columns.append(ColumnDT('pegawai_nama'))

                query = DBSession.query(KegiatanSubModel.id,
                          KegiatanSubModel.kode,
                          KegiatanSubModel.no_urut,
                        KegiatanSubModel.nama,
                        PegawaiModel.nama.label('pegawai_nama'),
                        ProgramModel.nama.label('prg_nm'),
                    func.sum(KegiatanItemModel.vol_1_1*KegiatanItemModel.vol_1_2*
                             KegiatanItemModel.hsat_1).label('rka'),       
                    func.sum(KegiatanItemModel.vol_2_1*KegiatanItemModel.vol_2_2*
                             KegiatanItemModel.hsat_2).label('dpa'),                      
                    func.sum(KegiatanItemModel.vol_3_1*KegiatanItemModel.vol_3_2*
                             KegiatanItemModel.hsat_3).label('rpka'),                      
                    func.sum(KegiatanItemModel.vol_4_1*KegiatanItemModel.vol_4_2*
                             KegiatanItemModel.hsat_4).label('dppa'))\
                    .join(KegiatanModel)\
                    .join(ProgramModel)\
                    .join(Urusan)\
                    .outerjoin(KegiatanItemModel)\
                    .filter(
                            KegiatanSubModel.unit_id==self.unit_id,
                            KegiatanSubModel.tahun_id==self.tahun,
                            KegiatanSubModel.tahun_id==self.tahun,
                            KegiatanSubModel.ttd1nip==PegawaiModel.kode,
                            ProgramModel.kode<>'00')\
                    .group_by(KegiatanSubModel.id,
                            KegiatanSubModel.no_urut,
                            KegiatanSubModel.nama,
                            ProgramModel.kode, ProgramModel.nama,
                            KegiatanModel.kode, Urusan.kode, PegawaiModel.kode, PegawaiModel.nama
                            )
                rowTable = DataTables(req, KegiatanSubModel, query, columns)
                # returns what is needed by DataTable
                #session.query(Table.column, func.count(Table.column)).group_by(Table.column).all()
                return rowTable.output_result()
                
                
            elif url_dict['act']=='save':
                p = params.copy()
                if 'disabled' not in p:
                    p['disabled']='0'
                else:
                    p['disabled']='1'
                if 'tgl_bahas_1' in p:
                    p['tgl_bahas_1'] = 'tgl_bahas_1' in p and p['tgl_bahas_1'] or None
                if 'tgl_bahas_2' in p:
                    p['tgl_bahas_2'] = 'tgl_bahas_2' in p and p['tgl_bahas_2'] or None
                if 'tgl_bahas_3' in p:
                    p['tgl_bahas_3'] = 'tgl_bahas_3' in p and p['tgl_bahas_3'] or None
                if 'tgl_bahas_4' in p:
                    p['tgl_bahas_4'] = 'tgl_bahas_4' in p and p['tgl_bahas_4'] or None
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = KegiatanSubModel.update(p)
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    
                    if 'no_urut' not in p or not p['no_urut']:
                        p['no_urut'] = KegiatanSubModel.get_no_urut(p)
                        
                    rows = KegiatanSubModel.tambah(p)
                else:
                    rows={}
                
                if rows:
                    self.d['msg']='Sukses Simpan Data'
                    self.d['success']=True
                else:
                    self.d['msg']='Gagal Simpan Data'
                
                return self.d
                
            elif url_dict['act']=='delete' and self.is_akses_mod('delete'):
                d={}
                d['id'] = pk_id
                rows = KegiatanSubModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
    
class ViewAnggaran001Other(AnggaranBaseViews):
    ################################################################################################
    ###### ITEM KEGIATAN
    ################################################################################################   
    @view_config(route_name="anggaran_999", renderer="../../templates/apbd/anggaran/999.pt")
    def anggaran_999(self):
        params = self.request.params
        self.sub_keg_id = 'kid' in params and params['kid'] and int(params['kid']) or 0
        if self.sub_keg_id or not 'sub_keg_id' in self.session:
            self.session['sub_keg_id'] = self.sub_keg_id
        self.sub_keg_id = self.session['sub_keg_id']
        self.session['menu'] = "".join(['999?kid=', str(self.sub_keg_id)])
        
        if self.logged and self.is_akses_mod('read'):
            return dict(datas=self.datas, row=KegiatanSubModel.get_header(self.unit_id, self.sub_keg_id))
        else:
            if not self.logged:
                headers=forget(self.request)
                return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            else:
                headers=forget(self.request)
                return HTTPFound(location='/anggaran', headers=headers)

    @view_config(route_name="anggaran_999_frm", renderer="../../templates/apbd/anggaran/999_frm.pt")
    def anggaran_999_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        self.datas["mod"] = self.session["menu"]        
        if self.logged and self.is_akses_mod('read'):
            heads = KegiatanSubModel.get_by_id(self.sub_keg_id)
            if (not self.datas['id'] and self.is_akses_mod('add'))\
                or (self.datas['id'] and self.is_akses_mod('edit')):
                row = KegiatanItemModel.get_by_id(self.datas['id'])
                if row:
                    return dict(datas=self.datas, rows=row, heads=heads)
                else:
                    if self.datas['id']>0:
                        return HTTPNotFound() #TODO: Warning Data Not Found
                #rows['tahun_id'] = self.datas['tahun']
                return dict(datas = self.datas,rows = "", heads=heads)
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            
    @view_config(route_name="anggaran_999_act", renderer="json")
    def anggaran_999_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            rek_id = 'rek_id' in params and params['rek_id'] and int(params['rek_id']) or 0
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('rek_kd'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT(''.join(['vol_',str(self.status_apbd),'_1'])))
                columns.append(ColumnDT(''.join(['sat_',str(self.status_apbd),'_1'])))
                columns.append(ColumnDT(''.join(['vol_',str(self.status_apbd),'_2'])))
                columns.append(ColumnDT(''.join(['sat_',str(self.status_apbd),'_2'])))
                columns.append(ColumnDT(''.join(['hsat_',str(self.status_apbd)])))
                columns.append(ColumnDT(''.join(['jml_',str(self.status_apbd)])))
                
                query = DBSession.query(KegiatanItemModel.no_urut,
                    KegiatanItemModel.id,
                    KegiatanItemModel.kode, KegiatanItemModel.nama,
                    
                    KegiatanItemModel.vol_1_1, KegiatanItemModel.vol_1_2,
                    KegiatanItemModel.sat_1_1, KegiatanItemModel.sat_1_2,
                    KegiatanItemModel.hsat_1,
                    (KegiatanItemModel.vol_1_1* KegiatanItemModel.vol_1_2*
                     KegiatanItemModel.hsat_1).label('jml_1'),
                    
                    KegiatanItemModel.vol_2_1, KegiatanItemModel.vol_2_2,
                    KegiatanItemModel.sat_2_1, KegiatanItemModel.sat_2_2,
                    KegiatanItemModel.hsat_2, 
                    (KegiatanItemModel.vol_2_1* KegiatanItemModel.vol_2_2*
                     KegiatanItemModel.hsat_2).label('jml_2'),
                    
                    KegiatanItemModel.vol_3_1, KegiatanItemModel.vol_3_2,
                    KegiatanItemModel.sat_3_1, KegiatanItemModel.sat_3_2,
                    KegiatanItemModel.hsat_3,
                    (KegiatanItemModel.vol_3_1* KegiatanItemModel.vol_3_2*
                     KegiatanItemModel.hsat_3).label('jml_3'),
                    
                    KegiatanItemModel.vol_4_1, KegiatanItemModel.vol_4_2,
                    KegiatanItemModel.sat_4_1, KegiatanItemModel.sat_4_2,
                    KegiatanItemModel.hsat_4,
                    (KegiatanItemModel.vol_4_1* KegiatanItemModel.vol_4_2*
                     KegiatanItemModel.hsat_4).label('jml_4'),
                    
                    RekeningModel.kode.label('rek_kd'))\
                      .join(RekeningModel)\
                      .join(KegiatanSubModel)\
                      .filter(KegiatanSubModel.id==self.sub_keg_id,
                              KegiatanSubModel.unit_id==self.unit_id,
                              KegiatanSubModel.tahun_id==self.tahun)
                rowTable = DataTables(req, KegiatanItemModel, query, columns)
                return rowTable.output_result()
            elif url_dict['act']=='save':
                p = params.copy()
                for  i in range(self.status_apbd,4):
                    p["".join(['vol_',str(i+1),'_1'])] = p["".join(['vol_',str(i),'_1'])]
                    p["".join(['sat_',str(i+1),'_1'])] = p["".join(['sat_',str(i),'_1'])]
                    p["".join(['vol_',str(i+1),'_2'])] = p["".join(['vol_',str(i),'_2'])]
                    p["".join(['sat_',str(i+1),'_2'])] = p["".join(['sat_',str(i),'_2'])]
                    p["".join(['hsat_',str(i+1)])] = p["".join(['hsat_',str(i)])]

                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = KegiatanItemModel.update(p)
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    if 'no_urut' not in p or not p['no_urut']:
                        p['no_urut'] = KegiatanItemModel.get_no_urut(p)
                    rows = KegiatanItemModel.tambah(p)
                else:
                    rows={}
                
                if rows:
                    self.d['msg']='Sukses Simpan Data'
                    self.d['success']=True
                else:
                    self.d['msg']='Gagal Simpan Data'
                
                return self.d
                
            elif url_dict['act']=='delete' and self.is_akses_mod('delete'):
                d={}
                d['id'] = pk_id
                rows = KegiatanItemModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

                     ############################################
                           ###    INDIKATOR KEGIATAN    ###
                           ###  KegiatanIndikatorModel  ###
                     ############################################   
    @view_config(route_name="anggaran_998", renderer="../../templates/apbd/anggaran/998.pt")
    def anggaran_998(self):
        params = self.request.params
        self.sub_keg_id = 'kid' in params and params['kid'] and int(params['kid']) or 0
        if self.sub_keg_id or not 'sub_keg_id' in self.session:
            self.session['sub_keg_id'] = self.sub_keg_id
        self.sub_keg_id = self.session['sub_keg_id']
        
        if self.logged and self.is_akses_mod('read'):
            return dict(datas=self.datas, 
                   row=KegiatanSubModel.get_header(self.unit_id, self.sub_keg_id),)
        else:
            if not self.logged:
                headers=forget(self.request)
                return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            else:
                headers=forget(self.request)
                return HTTPFound(location='/anggaran', headers=headers)

    @view_config(route_name="anggaran_998_frm", renderer="../../templates/apbd/anggaran/998_frm.pt")
    def anggaran_998_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        self.datas["mod"] = self.session["mod"][1:]
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        
        if self.logged:
            if (not self.datas['id'] and self.is_akses_mod('add'))\
                or (self.datas['id'] and self.is_akses_mod('edit')):
                row = KegiatanIndikatorModel.get_by_id(self.datas['id'])
                if row:
                    return dict(datas=self.datas, 
                           heads=KegiatanSubModel.get_header(self.unit_id,self.sub_keg_id), 
                           rows=row)
                else:
                    if self.datas['id']>0:
                        return HTTPNotFound() #TODO: Warning Data Not Found
                rows = {}
                return dict(datas = self.datas,
                            heads=KegiatanSubModel.get_header(self.unit_id,self.sub_keg_id), 
                            rows = '')
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            
    @view_config(route_name="anggaran_998_act", renderer="json")
    def anggaran_998_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            tipe  = 'tipe' in params and params['tipe'] and int(params['tipe']) or 0
            
            sub_keg_id = self.session['sub_keg_id']
            unit_id    = self.session['unit_id']
            
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('tipe'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT("".join(['tolok_ukur_',str(self.status_apbd)])))
                columns.append(ColumnDT("".join(['volume_',str(self.status_apbd)])))
                columns.append(ColumnDT("".join(['satuan_',str(self.status_apbd)])))
				
                query = DBSession.query(KegiatanIndikatorModel)\
                    .join(KegiatanSubModel)\
                    .filter(KegiatanSubModel.id==sub_keg_id,
                            KegiatanSubModel.unit_id==unit_id)
                rowTable = DataTables(req, KegiatanIndikatorModel, query, columns)
                return rowTable.output_result()
                
            elif url_dict['act']=='save':
                p = params.copy()
                for  i in range(self.status_apbd,4):
                    p["".join(['tolok_ukur_',str(i+1)])] = p["".join(['tolok_ukur_',str(i)])]
                    p["".join(['volume_',str(i+1)])] = p["".join(['volume_',str(i)])]
                    p["".join(['satuan_',str(i+1)])] = p["".join(['satuan_',str(i)])]
					
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = KegiatanIndikatorModel.update(p)
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    rows = KegiatanIndikatorModel.tambah(p)
                else:
                    rows={}
                
                if rows:
                    self.d['msg']='Sukses Simpan Data'
                    self.d['success']=True
                else:
                    self.d['msg']='Gagal Simpan Data'
                
                return self.d
                
            elif url_dict['act']=='delete' and self.is_akses_mod('delete'):
                d={}
                d['id'] = pk_id
                rows = KegiatanIndikatorModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

class ViewAnggaran003(AnggaranBaseViews):
    def __init__(self, context, request):
        AnggaranBaseViews.__init__(self, context, request)
        self.session['mod'] = 'A0103'

    @view_config(route_name="anggaran_003", renderer="../../templates/apbd/anggaran/003.pt")
    def anggaran_003(self):
        params = self.request.params
        if self.logged and self.is_akses_mod('read'):
            pegawais = PegawaiModel.get_enabled()
            jabatans = JabatanModel.get_enabled()
            return dict(datas=self.datas, jabatans=jabatans, pegawais=pegawais)
        else:
            if not self.logged:
                headers=forget(self.request)
                return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            else:
                headers=forget(self.request)
                return HTTPFound(location='/anggaran', headers=headers)

    @view_config(route_name="anggaran_003_frm", renderer="../../templates/apbd/anggaran/003_frm.pt")
    def anggaran_003_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                #row  = TapdModel.get_by_id(self.datas['id'])
                #jabs = JabatanModel.get_tapd()
                row = DBSession.query(PejabatModel).filter(PejabatModel.id==self.datas['id']).first()
				
                if row:
                    #rows = TapdModel.row2dict(row)
                    print '*****',row.id
                    return dict(datas=self.datas, rows=row) 
					#, jabs=jabs)
                else:
                    if self.datas['id']>0:
                        return HTTPNotFound() #TODO: Warning Data Not Found
                return dict(datas=self.datas,rows='') 
				#, jabs=jabs)
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="anggaran_003_act", renderer="json")
    def anggaran_003_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict
        ses     = self.session
        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('pegawais.kode'))
                columns.append(ColumnDT('pegawais.nama'))
                columns.append(ColumnDT('jabatans.nama'))
                columns.append(ColumnDT('mulai', filter=self._DTstrftime))
                columns.append(ColumnDT('selesai', filter=self._DTstrftime))
				
                query = DBSession.query(TapdModel)
                rowTable = DataTables(req, TapdModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                #if 'disabled' not in p:
                #    p['disabled']=0
                #else:
                #    p['disabled']=1
                rows={}
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    #try:
                    rows = TapdModel.update(p)
                    #except:
                        #pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    try:
                      rows = TapdModel.tambah(p)
                    except:
                        pass
                else:
                    rows={}
                
                if rows:
                    self.d['msg']='Sukses Simpan Data'
                    self.d['success']=True
                else:
                    self.d['msg']='Gagal Simpan Data'
                
                return self.d
                
            elif url_dict['act']=='delete' and self.is_akses_mod('delete'):
                d={}
                d['id'] = pk_id
                rows = TapdModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
