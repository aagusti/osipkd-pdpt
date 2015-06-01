from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from pyramid.security import remember
from pyramid.security import forget
from pyramid.security import has_permission
from pyramid.renderers import render_to_response
from osipkd.models.apbd_admin_models import *
from osipkd.views.views import *
from osipkd.models.apbd_rka_models import (KegiatanSubModel, KegiatanItemModel, KegiatanModel)
from osipkd.models.apbd_tu_models import (APInvoiceModel, APInvoiceItemModel, SppModel, SpmModel, SppItemModel, ARInvoiceModel, StsModel, StsItemModel, SpdModel, SpdItemModel,Sp2dModel)
import os
from datetime import datetime

class ViewAPBDAdmin(BaseViews):
    def __init__(self, context, request):
        BaseViews.__init__(self, context, request)
        self.tahun = 'tahun' in self.session and self.session['tahun'] or\
                     datetime.strftime(datetime.now(),'%Y')
        self.unit_id  = 'unit_id' in self.session and self.session['unit_id'] or 0
        self.kegiatan_sub_id = 'kegiatan_sub_id' in self.session and self.session['kegiatan_sub_id'] or 0
        
    @view_config(route_name="admin_rekening", renderer="../../templates/apbd/rekening.pt")
    def admin_rekening(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_rekening_frm", renderer="../../templates/apbd/rekening_frm.pt")
    def admin_rekening_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = RekeningModel.get_by_id(self.datas['id'])
                if row:
                    rows = RekeningModel.row2dict(row)
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
            
    @view_config(route_name="admin_rekening_act", renderer="json")
    def admin_rekening_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('level_id'))
                columns.append(ColumnDT('defsign'))
                columns.append(ColumnDT('header_id'))
                columns.append(ColumnDT('disabled'))

                query = DBSession.query(RekeningModel)
                rowTable = DataTables(req, RekeningModel, query, columns)
                # returns what is needed by DataTable
                return rowTable.output_result()


            elif url_dict['act']=='save':
                p = params.copy()
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = RekeningModel.update(p)
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    rows = RekeningModel.tambah(p)
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
                rows = RekeningModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_urusan", renderer="../../templates/apbd/urusan.pt")
    def admin_urusan(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_urusan_frm", renderer="../../templates/apbd/urusan_frm.pt")
    def admin_urusan_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = Urusan.get_by_id(self.datas['id'])
                if row:
                    rows = Urusan.row2dict(row)
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

    @view_config(route_name="admin_urusan_act", renderer="json")
    def admin_urusan_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('disabled'))

                query = DBSession.query(Urusan)
                rowTable = DataTables(req, Urusan, query, columns)
                # returns what is needed by DataTable
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = Urusan.update(p)
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    rows = Urusan.tambah(p)
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
                rows = Urusan.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
            elif url_dict['act']=='print' and self.is_akses_mod('read'):
                pass
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_unit", renderer="../../templates/apbd/unit.pt")
    def admin_unit(self):
        params = self.request.params
        if self.logged:
            urusans = Urusan.get_enabled()
            return dict(datas=self.datas, urusans=urusans)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_unit_frm", renderer="../../templates/apbd/unit_frm.pt")
    def admin_unit_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        urusans = Urusan.get_enabled()
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = Unit.get_by_id(self.datas['id'])
                if row:
                    rows = Unit.row2dict(row)
                    return dict(datas=self.datas, rows=rows, urusans=urusans)
                else:
                    if self.datas['id']>0:
                        return HTTPNotFound() #TODO: Warning Data Not Found
                return dict(datas=self.datas,rows='', urusans=urusans)
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_unit_act", renderer="json")
    def admin_unit_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('urusans.kode'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('singkat'))
                columns.append(ColumnDT('kategori'))
                columns.append(ColumnDT('urusans.nama'))
                columns.append(ColumnDT('disabled'))

                query = DBSession.query(Unit).\
                        join(Urusan).\
                        filter(Unit.urusan_id==Urusan.id)
                rowTable = DataTables(req, Unit, query, columns)
                # returns what is needed by DataTable
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = Unit.update(p)
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    rows = Unit.tambah(p)
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
                rows = Unit.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
			
    @view_config(route_name="admin_program", renderer="../../templates/apbd/program.pt")
    def admin_program(self):
        params = self.request.params
        if self.logged:
            urusans = Urusan.get_enabled()
            return dict(datas=self.datas, urusans=urusans)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_program_frm", renderer="../../templates/apbd/program_frm.pt")
    def admin_program_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        urusans = Urusan.get_enabled()
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = ProgramModel.get_by_id(self.datas['id'])
                if row:
                    rows = ProgramModel.row2dict(row)
                    return dict(datas=self.datas, rows=rows, urusans=urusans)
                else:
                    if self.datas['id']>0:
                        return HTTPNotFound() #TODO: Warning Data Not Found
                return dict(datas=self.datas,rows='', urusans=urusans)
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_program_act", renderer="json")
    def admin_program_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('urusans.kode'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('sasaran'))
                columns.append(ColumnDT('agenda_id'))
                columns.append(ColumnDT('urusans.nama'))
                columns.append(ColumnDT('fungsi_id'))
                columns.append(ColumnDT('disabled'))

                query = DBSession.query(ProgramModel).\
                        join(Urusan).\
                        filter(ProgramModel.urusan_id==Urusan.id)
                rowTable = DataTables(req, ProgramModel, query, columns)
                # returns what is needed by DataTable
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = ProgramModel.update(p)
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    rows = ProgramModel.tambah(p)
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
                rows = ProgramModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            
    @view_config(route_name="admin_pejabat", renderer="../../templates/apbd/pejabat.pt")
    def admin_pejabat(self):
        params = self.request.params
        if self.logged:
            units = Unit.get_enabled()
            pegawais = PegawaiModel.get_enabled()
            jabatans = JabatanModel.get_enabled()
            return dict(datas=self.datas, units=units, jabatans=jabatans, pegawais=pegawais)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_pejabat_frm", renderer="../../templates/apbd/pejabat_frm.pt")
    def admin_pejabat_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        #pegawais = PegawaiModel.get_enabled()
        #jabatans = JabatanModel.get_enabled()
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                #row = PejabatModel.get_by_id(self.datas['id'])
                row = DBSession.query(PejabatModel).filter(PejabatModel.id==self.datas['id']).first()
                if row:
                    #rows = PejabatModel.row2dict(row)
                    print '*****',row.id
                    return dict(datas=self.datas, rows=row)  
                                #pegawais=pegawais, jabatans=jabatans)
                else:
                    if self.datas['id']>0:
                        return HTTPNotFound() #TODO: Warning Data Not Found
                return dict(datas=self.datas,rows='') 
                            #pegawais=pegawais, jabatans=jabatans)
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
           
    @view_config(route_name="admin_pejabat_act", renderer="json")
    def admin_pejabat_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('pegawais.kode'))
                columns.append(ColumnDT('pegawais.nama'))
                columns.append(ColumnDT('jabatans.nama'))
                columns.append(ColumnDT('units.nama'))
                columns.append(ColumnDT('mulai', filter=self._DTstrftime))
                columns.append(ColumnDT('selesai', filter=self._DTstrftime))
            

                query = DBSession.query(PejabatModel)
                rowTable = DataTables(req, PejabatModel, query, columns)
                # returns what is needed by DataTable
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = PejabatModel.update(p)
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    rows = PejabatModel.tambah(p)
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
                rows = PejabatModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            
    @view_config(route_name="admin_pegawai_jabatan", renderer="../templates/apbd/pegawai_jabatan.pt")
    def admin_pegawai_jabatan(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_pegawai_jabatan_frm", renderer="../templates/apbd/pegawai_jabatan_frm.pt")
    def admin_pegawai_jabatan_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        
        if self.logged and self.is_akses_mod(url_dict['act']):
            self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
            row = UserModel.get_by_id(self.datas['id'])
            if row:
                rows = UserModel.row2dict(row)
                return dict(datas=self.datas, rows=rows)
            else:
                if self.datas['id']>0:
                    return HTTPNotFound()
            return dict(datas=self.datas,rows='')
            
            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            
    @view_config(route_name="admin_pegawai_jabatan_act", renderer="json")
    def admin_pegawai_jabatan_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('apps.nama'))
                columns.append(ColumnDT('disabled'))

                query = DBSession.query(pegawai_jabatanModel).\
                        join(AppModel).\
                        filter(pegawai_jabatanModel.app_id==AppModel.id).order_by(pegawai_jabatanModel.kode)
                rowTable = DataTables(req, pegawai_jabatanModel, query, columns)
                # returns what is needed by DataTable
                return rowTable.output_result()

            if url_dict['act']=='grp' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('groups.nama'))
                query = DBSession.query(UserGroupModel).\
                       filter(UserGroupModel.user_id == pk_id).\
                       order_by(UserGroupModel.kode)
                rowTable = DataTables(req, UserGroupModel, query, columns)
                return rowTable.output_result()
            elif url_dict['act']=='save':
                p = params.copy()
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = UserModel.update(p)
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    rows = UserModel.tambah(p)
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
                rows = UserModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            
    @view_config(route_name="admin_fungsi", renderer="../../templates/apbd/fungsi.pt")
    def admin_fungsi(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_fungsi_frm", renderer="../../templates/apbd/fungsi_frm.pt")
    def admin_fungsi_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = FungsiModel.get_by_id(self.datas['id'])
                if row:
                    rows = FungsiModel.row2dict(row)
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

    @view_config(route_name="admin_fungsi_act", renderer="json")
    def admin_fungsi_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('disabled'))

                query = DBSession.query(FungsiModel)
                rowTable = DataTables(req, FungsiModel, query, columns)
                # returns what is needed by DataTable
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = FungsiModel.update(p)
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    rows = FungsiModel.tambah(p)
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
                rows = FungsiModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_tahun", renderer="../../templates/apbd/tahun.pt")
    def admin_tahun(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_tahun_frm", renderer="../../templates/apbd/tahun_frm.pt")
    def admin_tahun_frm(self):
        req = self.request
        params = req.params
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

    @view_config(route_name="admin_tahun_act", renderer="json")
    def admin_tahun_act(self):
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
                columns.append(ColumnDT('tanggal_1'))
                columns.append(ColumnDT('tanggal_2'))
                columns.append(ColumnDT('tanggal_3'))
                columns.append(ColumnDT('tanggal_4'))
                columns.append(ColumnDT('no_perda'))
                columns.append(ColumnDT('tgl_perda'))
                columns.append(ColumnDT('no_perkdh'))
                columns.append(ColumnDT('tgl_perkdh'))
                columns.append(ColumnDT('no_perda_rev'))
                columns.append(ColumnDT('tgl_perda_rev'))
                columns.append(ColumnDT('no_perkdh_rev'))
                columns.append(ColumnDT('tgl_perkdh_rev'))
                columns.append(ColumnDT('no_lpj'))
                columns.append(ColumnDT('tgl_lpj'))

                query = DBSession.query(TahunModel)
                rowTable = DataTables(req, TahunModel, query, columns)
                # returns what is needed by DataTable
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = TahunModel.update(p)
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    rows = TahunModel.tambah(p)
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

    @view_config(route_name="admin_kegiatan", renderer="../../templates/apbd/program.pt")
    def admin_kegiatan(self):
        params = self.request.params
        if self.logged:
            programs = ProgramModel.get_enabled()
            return dict(datas=self.datas, programs=programs)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_kegiatan_frm", renderer="../../templates/apbd/kegiatan_frm.pt")
    def admin_kegiatan_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        programs = ProgramModel.get_enabled()
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = KegiatanModel.get_by_id(self.datas['id'])
                if row:
                    rows = KegiatanModel.row2dict(row)
                    return dict(datas=self.datas, rows=rows, programs=programs)
                else:
                    if self.datas['id']>0:
                        return HTTPNotFound() #TODO: Warning Data Not Found
                return dict(datas=self.datas,rows='', programs=programs)
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_kegiatan_act", renderer="json")
    def admin_kegiatan_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('programs.kode'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('tmt'))
                columns.append(ColumnDT('programs.nama'))
                columns.append(ColumnDT('disabled'))

                query = DBSession.query(KegiatanModel).\
                        join(ProgramModel).\
                        filter(KegiatanModel.program_id==ProgramModel.id,
                               KegiatanModel.program_id==pk_id)
                rowTable = DataTables(req, KegiatanModel, query, columns)
                # returns what is needed by DataTable
                return rowTable.output_result()

            if url_dict['act']=='grid2' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('tmt'))
                columns.append(ColumnDT('disabled'))

                query = DBSession.query(KegiatanModel.id,KegiatanModel.kode,KegiatanModel.nama,KegiatanModel.tmt,KegiatanModel.disabled)      
                rowTable = DataTables(req, KegiatanModel, query, columns)
                # returns what is needed by DataTable
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = KegiatanModel.update(p)
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    rows = KegiatanModel.tambah(p)
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
                rows = KegiatanModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_dasarhukum", renderer="../../templates/apbd/rekening.pt")
    def admin_dasarhukum(self):
        params = self.request.params
        if self.logged:
            rekenings = RekeningModel.get_enabled()
            return dict(datas=self.datas, rekenings=rekenings)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_dasarhukum_frm", renderer="../../templates/apbd/dasarhukum_frm.pt")
    def admin_dasarhukum_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        rekenings = RekeningModel.get_enabled()
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = DasarHukumModel.get_by_id(self.datas['id'])
                if row:
                    rows = DasarHukumModel.row2dict(row)
                    return dict(datas=self.datas, rows=rows, rekenings=rekenings)
                else:
                    if self.datas['id']>0:
                        return HTTPNotFound() #TODO: Warning Data Not Found
                return dict(datas=self.datas,rows='', rekenings=rekenings)
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_dasarhukum_act", renderer="json")
    def admin_dasarhukum_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('rekenings.nama'))
                columns.append(ColumnDT('disabled'))

                query = DBSession.query(DasarHukumModel).\
                        join(RekeningModel).\
                        filter(DasarHukumModel.rekening_id==RekeningModel.id,
                               RekeningModel.id==pk_id)
                rowTable = DataTables(req, DasarHukumModel, query, columns)
                # returns what is needed by DataTable
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = DasarHukumModel.update(p)
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    rows = DasarHukumModel.tambah(p)
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
                rows = DasarHukumModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_pegawai", renderer="../../templates/apbd/pegawai.pt")
    def admin_pegawai(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_pegawai_frm", renderer="../../templates/apbd/pegawai_frm.pt")
    def admin_pegawai_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = PegawaiModel.get_by_id(self.datas['id'])
                if row:
                    rows = PegawaiModel.row2dict(row)
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

    @view_config(route_name="admin_pegawai_act", renderer="json")
    def admin_pegawai_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))

                query = DBSession.query(PegawaiModel)
                rowTable = DataTables(req, PegawaiModel, query, columns)
                # returns what is needed by DataTable
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = PegawaiModel.update(p)
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    rows = PegawaiModel.tambah(p)
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
                rows = PegawaiModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="apbd_dlg", renderer="json")
    def apbd_dlg(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict
        if self.logged :
 
            if url_dict['tbl']=='kegiatan' and self.is_akses_mod('read'):
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('programs.urusans.kode'))
                columns.append(ColumnDT('programs.kode'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('programs.nama'))
                columns.append(ColumnDT('programs.nama'))

                query = DBSession.query(KegiatanModel).join(ProgramModel
                          ).join(Urusan
                          ).filter(KegiatanModel.disabled==0,
                                   ProgramModel.kode!='00')
                rowTable = DataTables(req, KegiatanModel, query, columns)
                return rowTable.output_result()
 
            elif url_dict['tbl']=='kegiatanitem' and self.is_akses_mod('read'):
                pk_id = 'pk_id' in params and params['pk_id'] or 0
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('vol_4_1'))
                columns.append(ColumnDT('vol_4_2'))
                columns.append(ColumnDT('hsat_4'))
                columns.append(ColumnDT('jumlah'))
                columns.append(ColumnDT('realisasi'))
                columns.append(ColumnDT('sisa'))
                query = DBSession.query(KegiatanItemModel.id,
                            KegiatanItemModel.kode,
                            KegiatanItemModel.nama,
                            KegiatanItemModel.vol_4_1,
                            KegiatanItemModel.vol_4_2,
                            KegiatanItemModel.hsat_4,
                            (KegiatanItemModel.vol_4_1*
                             KegiatanItemModel.vol_4_2*
                             KegiatanItemModel.hsat_4).label('jumlah'),
                             func.sum(APInvoiceItemModel.nilai).label('realisasi'),
                            ((KegiatanItemModel.vol_4_1*
                             KegiatanItemModel.vol_4_2*
                             KegiatanItemModel.hsat_4)-func.sum(APInvoiceItemModel.nilai)).label('sisa')
                          ).outerjoin(APInvoiceItemModel
                          ).filter(KegiatanItemModel.kegiatan_sub_id==pk_id
                          ).group_by(KegiatanItemModel.id,
                            KegiatanItemModel.kode,
                            KegiatanItemModel.nama,
                            KegiatanItemModel.vol_4_1,
                            KegiatanItemModel.vol_4_2,
                            KegiatanItemModel.hsat_4)
                          
                rowTable = DataTables(req, KegiatanItemModel, query, columns)
                return rowTable.output_result()
                
            elif url_dict['tbl']=='rekening' and self.is_akses_mod('read'):
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                if self.session['mod']=='A0201':
                    query = DBSession.query(RekeningModel.id, RekeningModel.kode, 
                                RekeningModel.nama)\
                                .filter(RekeningModel.disabled==0)\
                                .filter(RekeningModel.kode.like('4.%'))
                elif self.session['mod']=='A0202':
                    query = DBSession.query(RekeningModel.id, RekeningModel.kode, 
                                RekeningModel.nama)\
                                .filter(RekeningModel.disabled==0)\
                                .filter(RekeningModel.kode.like('5.1.%'))
                elif self.session['mod']=='A0203':
                    query = DBSession.query(RekeningModel.id, RekeningModel.kode, 
                                RekeningModel.nama)\
                                .filter(RekeningModel.disabled==0)\
                                .filter(RekeningModel.kode.like('5.2.%'))
                elif self.session['mod']=='A0204':
                    query = DBSession.query(RekeningModel.id, RekeningModel.kode, 
                                RekeningModel.nama)\
                                .filter(RekeningModel.disabled==0)\
                                .filter(RekeningModel.kode.like('6.1.%'))
                elif self.session['mod']=='A0205':
                    query = DBSession.query(RekeningModel.id, RekeningModel.kode, 
                                RekeningModel.nama)\
                                .filter(RekeningModel.disabled==0)\
                                .filter(RekeningModel.kode.like('6.2.%'))
                rowTable = DataTables(req, RekeningModel, query, columns)
                return rowTable.output_result()

            elif url_dict['tbl']=='rekketetapan' and self.is_akses_mod('read'):
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                    
                query = DBSession.query(RekeningModel.id, RekeningModel.kode, 
                                RekeningModel.nama)\
                                .filter(RekeningModel.disabled==0)\
                                .filter(RekeningModel.kode.like('4.%'))
                
                rowTable = DataTables(req, RekeningModel, query, columns)
                return rowTable.output_result()
                
            elif url_dict['tbl']=='kegiatansub' and self.is_akses_mod('read'):
                pk_id = 'pk_id' in params and params['pk_id'] or self.unit_id
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('nama'))
                
                query = DBSession.query(KegiatanSubModel.id, KegiatanSubModel.no_urut, 
                                KegiatanSubModel.kode,
                                KegiatanSubModel.nama
                                ).filter(KegiatanSubModel.unit_id==pk_id,
                                         KegiatanSubModel.tahun_id==self.tahun,  
                                ).order_by(KegiatanSubModel.no_urut,) 
                                
                rowTable = DataTables(req, KegiatanSubModel, query, columns)
                return rowTable.output_result()

            elif url_dict['tbl']=='kegiatansub1' and self.is_akses_mod('read'):
                pk_id = 'pk_id' in params and params['pk_id'] or self.unit_id
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('nama'))
                
                query = DBSession.query(KegiatanSubModel.id, KegiatanSubModel.no_urut, 
                                KegiatanSubModel.kode,
                                KegiatanSubModel.nama
                                ).join(KegiatanModel
                                ).filter(KegiatanSubModel.kegiatan_id==KegiatanModel.id,
                                         KegiatanSubModel.unit_id==pk_id,
                                         KegiatanSubModel.tahun_id==self.tahun,  
                                         KegiatanModel.kode=='10',  
                                ).order_by(KegiatanSubModel.no_urut,) 
                                
                rowTable = DataTables(req, KegiatanSubModel, query, columns)
                return rowTable.output_result()

            elif url_dict['tbl']=='kegiatansub2' and self.is_akses_mod('read'):
                pk_id = 'pk_id' in params and params['pk_id'] or self.unit_id
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('nama'))
                
                query = DBSession.query(KegiatanSubModel.id, KegiatanSubModel.no_urut, 
                                KegiatanSubModel.kode,
                                KegiatanSubModel.nama
                                ).join(KegiatanModel
                                ).filter(KegiatanSubModel.kegiatan_id==KegiatanModel.id,
                                         KegiatanSubModel.unit_id==pk_id,
                                         KegiatanSubModel.tahun_id==self.tahun,  
                                         KegiatanModel.kode!='10',KegiatanModel.kode!='31',KegiatanModel.kode!='32',KegiatanModel.kode!='33'
                                ).order_by(KegiatanSubModel.no_urut,) 
                                
                rowTable = DataTables(req, KegiatanSubModel, query, columns)
                return rowTable.output_result()

            elif url_dict['tbl']=='kegiatansub3' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kegiatan_sub_id'))
                columns.append(ColumnDT('nama'))
                
                query = DBSession.query(KegiatanItemModel.no_urut,
                    KegiatanItemModel.id,
                    KegiatanItemModel.kegiatan_sub_id, KegiatanItemModel.nama,
                    RekeningModel.kode.label('rek_kd'))\
                      .join(RekeningModel)\
                      .join(KegiatanSubModel)\
                      .filter(KegiatanSubModel.id==KegiatanItemModel.kegiatan_sub_id,
                              KegiatanSubModel.unit_id==self.unit_id,
                              KegiatanSubModel.tahun_id==self.tahun)
                rowTable = DataTables(req, KegiatanItemModel, query, columns)
                return rowTable.output_result()

            elif url_dict['tbl']=='kegiatansub4' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('rek_kd'))
                columns.append(ColumnDT('rekening_nama'))
                columns.append(ColumnDT('dppa'))
                
                query = DBSession.query(KegiatanItemModel.id,
                    RekeningModel.kode.label('rek_kd'),
                    RekeningModel.nama.label('rekening_nama'),
                    KegiatanItemModel.nama,
                    func.sum(KegiatanItemModel.vol_4_1*KegiatanItemModel.vol_4_2*
                             KegiatanItemModel.hsat_4).label('dppa'))\
                      .join(RekeningModel)\
                      .join(KegiatanSubModel)\
                      .filter(KegiatanSubModel.id==KegiatanItemModel.kegiatan_sub_id,
                              KegiatanSubModel.unit_id==self.unit_id,
                              KegiatanSubModel.tahun_id==self.tahun,
                              KegiatanItemModel.rekening_id==RekeningModel.id)\
                      .group_by(KegiatanItemModel.id,
                              RekeningModel.kode,
                              RekeningModel.nama,
                              KegiatanItemModel.nama
                              )
                rowTable = DataTables(req, KegiatanItemModel, query, columns)
                return rowTable.output_result()

            elif url_dict['tbl']=='kegiatansub5' and self.is_akses_mod('read'):
                pk_id = 'pk_id' in params and params['pk_id'] or self.unit_id
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                
                query = DBSession.query(KegiatanSubModel.id, 
                                KegiatanSubModel.kode,
                                KegiatanSubModel.nama
                                ).filter(KegiatanSubModel.unit_id==pk_id,
                                         KegiatanSubModel.tahun_id==self.tahun)
                                
                rowTable = DataTables(req, KegiatanSubModel, query, columns)
                return rowTable.output_result()

            elif url_dict['tbl']=='kegiatanitem5' and self.is_akses_mod('read'):
                pk_id  = 'pk_id'  in params and params['pk_id']  or self.unit_id
                pk_id2 = 'kegiatan_sub_id' in params and params['kegiatan_sub_id'] or 0
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('rekening_kode'))
                columns.append(ColumnDT('rekening_nama'))
                columns.append(ColumnDT('hsat_4'))
                columns.append(ColumnDT('rekening_id'))
                columns.append(ColumnDT('sub_id'))
                columns.append(ColumnDT('sub_kode'))

                query = DBSession.query(KegiatanItemModel.id,
                                        RekeningModel.kode.label('rekening_kode'),
                                        RekeningModel.nama.label('rekening_nama'),
                                        KegiatanItemModel.hsat_4,
                                        RekeningModel.id.label('rekening_id'),
                                        KegiatanSubModel.id.label('sub_id'),
                                        KegiatanSubModel.kode.label('sub_kode')).\
                        join(RekeningModel, KegiatanSubModel,).\
                        filter(KegiatanItemModel.kegiatan_sub_id==KegiatanSubModel.id,
                               KegiatanItemModel.kegiatan_sub_id==pk_id2,
                               KegiatanSubModel.unit_id==pk_id,
                               KegiatanItemModel.rekening_id==RekeningModel.id,  
                               ).\
                        group_by(KegiatanItemModel.id,
                              RekeningModel.kode,
                              RekeningModel.nama,
                              KegiatanItemModel.hsat_4,
                              RekeningModel.id,
                              KegiatanSubModel.id,
                              KegiatanSubModel.kode,
                              )
                rowTable = DataTables(req, KegiatanItemModel, query, columns)
                return rowTable.output_result()

            elif url_dict['tbl']=='apinvoice' and self.is_akses_mod('read'):
                pk_id = 'pk_id' in params and params['pk_id'] or 0
                pk_id2 = 'pk_id2' in params and params['pk_id2'] or 0
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('jenis'))
                columns.append(ColumnDT('ap_tanggal', filter=self._DTstrftime))
                columns.append(ColumnDT('kegiatan_item_nm'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nilai'))

                query = DBSession.query(APInvoiceModel.id,
                          APInvoiceModel.no_urut, 
                          APInvoiceModel.jenis,
                          APInvoiceModel.ap_tanggal,
                          KegiatanItemModel.nama.label('kegiatan_item_nm'),
                          APInvoiceModel.nama,
                          func.sum(APInvoiceItemModel.nilai).label('nilai'),
                        ).filter(APInvoiceModel.id==APInvoiceItemModel.apinvoice_id,
                              APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                              APInvoiceModel.tahun_id==self.tahun,
                              APInvoiceModel.unit_id==pk_id,
                              APInvoiceModel.jenis==pk_id2,
                        ).order_by(APInvoiceModel.no_urut.desc()
                        ).group_by(APInvoiceModel.id,
                          APInvoiceModel.no_urut,
                          APInvoiceModel.jenis,
                          APInvoiceModel.ap_tanggal,
                          KegiatanItemModel.nama,
                          APInvoiceModel.nama,
                        )
                rowTable = DataTables(req, APInvoiceModel, query, columns)
                return rowTable.output_result()

            elif url_dict['tbl']=='spd' and self.is_akses_mod('read'):
                pk_id = 'pk_id' in params and params['pk_id'] or 0
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('triwulan_id'))
                columns.append(ColumnDT('nominal'))

                query = DBSession.query(SpdModel.id, 
                          SpdModel.nama, 
                          SpdModel.kode,
                          SpdModel.triwulan_id, 
                          func.sum(SpdItemModel.nominal).label('nominal')
                        ).outerjoin(SpdItemModel,
                        ).filter(SpdModel.tahun_id==self.tahun,
                                 SpdModel.unit_id==self.unit_id,
                        ).order_by(SpdModel.id.asc()
                        ).group_by(SpdModel.id, SpdModel.kode,
                          SpdModel.nama, SpdModel.triwulan_id,
                        )

                rowTable = DataTables(req, SpdModel, query, columns)
                return rowTable.output_result()

            elif url_dict['tbl']=='spp' and self.is_akses_mod('read'):
                pk_id = 'pk_id' in params and params['pk_id'] or 0
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('tanggal'))
                columns.append(ColumnDT('jenis'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nominal'))
                
                query = DBSession.query(SppModel.id,
                          SppModel.no_urut,
                          SppModel.tanggal,
                          SppModel.jenis,
                          SppModel.nama,
                          SppModel.nominal,
                          SppModel.ttd_uid,
                          SppModel.verified_uid
                        ).filter(SppModel.tahun_id==self.tahun,
                              SppModel.unit_id==self.unit_id,
                        ).order_by(SppModel.no_urut.desc()
                        )
 
                rowTable = DataTables(req, SppModel, query, columns)
                return rowTable.output_result()
            
            elif url_dict['tbl']=='ttd' and self.is_akses_mod('read'):
                pk_id = 'id' in params and int(params['id']) or 0
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('pegawais.id'))
                columns.append(ColumnDT('pegawais.kode'))
                columns.append(ColumnDT('pegawais.nama'))
                columns.append(ColumnDT('jabatans.nama'))
                columns.append(ColumnDT('units.nama'))
                columns.append(ColumnDT('mulai', filter=self._DTstrftime))
                columns.append(ColumnDT('selesai', filter=self._DTstrftime))

                query = DBSession.query(PejabatModel)
                rowTable = DataTables(req, PejabatModel, query, columns)
                # returns what is needed by DataTable
                return rowTable.output_result()

            elif url_dict['tbl']=='kasi' and self.is_akses_mod('read'):
                pk_id = 'id' in params and int(params['id']) or 0
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('pegawais.id'))
                columns.append(ColumnDT('pegawais.kode'))
                columns.append(ColumnDT('pegawais.nama'))
                columns.append(ColumnDT('jabatans.nama'))
                columns.append(ColumnDT('units.nama'))
                columns.append(ColumnDT('mulai', filter=self._DTstrftime))
                columns.append(ColumnDT('selesai', filter=self._DTstrftime))

                query = DBSession.query(PejabatModel)
                rowTable = DataTables(req, PejabatModel, query, columns)
                # returns what is needed by DataTable
                return rowTable.output_result()
                
            elif url_dict['tbl']=='pptk' and self.is_akses_mod('read'):
                pk_id = 'id' in params and int(params['id']) or 0
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('pegawais.id'))
                columns.append(ColumnDT('pegawais.kode'))
                columns.append(ColumnDT('pegawais.nama'))
                columns.append(ColumnDT('jabatans.nama'))
                columns.append(ColumnDT('units.nama'))
                columns.append(ColumnDT('mulai', filter=self._DTstrftime))
                columns.append(ColumnDT('selesai', filter=self._DTstrftime))

                query = DBSession.query(PejabatModel)
                rowTable = DataTables(req, PejabatModel, query, columns)
                # returns what is needed by DataTable
                return rowTable.output_result()

            elif url_dict['tbl']=='barang' and self.is_akses_mod('read'):
                pk_id = 'id' in params and int(params['id']) or 0
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('pegawais.id'))
                columns.append(ColumnDT('pegawais.kode'))
                columns.append(ColumnDT('pegawais.nama'))
                columns.append(ColumnDT('jabatans.nama'))
                columns.append(ColumnDT('units.nama'))
                columns.append(ColumnDT('mulai', filter=self._DTstrftime))
                columns.append(ColumnDT('selesai', filter=self._DTstrftime))

                query = DBSession.query(PejabatModel)
                rowTable = DataTables(req, PejabatModel, query, columns)
                # returns what is needed by DataTable
                return rowTable.output_result()
            
            elif url_dict['tbl']=='arinvoice' and self.is_akses_mod('read'):
                pk_id = 'id' in params and int(params['id']) or 0
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('tgl_terima', filter=self._DTstrftime))
                columns.append(ColumnDT('tgl_validasi', filter=self._DTstrftime))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nilai'))

                query = DBSession.query(ARInvoiceModel.id,
                          ARInvoiceModel.kode,
                          ARInvoiceModel.tgl_terima,
                          ARInvoiceModel.tgl_validasi,
                          ARInvoiceModel.nama,
                          ARInvoiceModel.nilai,
                        ).filter(ARInvoiceModel.tahun_id==self.tahun,
                              ARInvoiceModel.unit_id==self.unit_id,
                        ).order_by(ARInvoiceModel.id.asc()
                        ).group_by(ARInvoiceModel.id,
                          ARInvoiceModel.kode,
                          ARInvoiceModel.tgl_terima,
                          ARInvoiceModel.tgl_validasi,
                          ARInvoiceModel.nama,
                          ARInvoiceModel.nilai)
 
                rowTable = DataTables(req, ARInvoiceModel, query, columns)
                return rowTable.output_result()
 
            elif url_dict['tbl']=='bendaharatbp' and self.is_akses_mod('read'):
                pk_id = 'id' in params and int(params['id']) or 0
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('pegawais.id')) 
                columns.append(ColumnDT('pegawais.kode'))
                columns.append(ColumnDT('pegawais.nama'))
                columns.append(ColumnDT('jabatans.nama'))
                columns.append(ColumnDT('units.nama'))
                columns.append(ColumnDT('mulai', filter=self._DTstrftime))
                columns.append(ColumnDT('selesai', filter=self._DTstrftime))

                query = DBSession.query(PejabatModel
                        ).join(JabatanModel, PegawaiModel
                        ).filter(and_(JabatanModel.kode >= '230', JabatanModel.kode <= '235') #Sintak Between
                        ).filter(PejabatModel.unit_id==self.unit_id,
                          JabatanModel.id==PejabatModel.jabatan_id,
                          PegawaiModel.id==PejabatModel.pegawai_id )
                rowTable = DataTables(req, PejabatModel, query, columns)
                return rowTable.output_result()
 
            elif url_dict['tbl']=='spm' and self.is_akses_mod('read'):
                pk_id = 'id' in params and int(params['id']) or 0
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('tanggal', filter=self._DTstrftime))
                columns.append(ColumnDT('jenis'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nominal'))
                
                query = DBSession.query(SpmModel.id,
                          SpmModel.kode,
                          SpmModel.tanggal,
                          SppModel.jenis,
                          SpmModel.nama,
                          SppModel.nominal
                          ).filter(SpmModel.spp_id==SppModel.id,
                              SppModel.tahun_id==self.tahun,
                              SppModel.unit_id==self.unit_id
                          )                
                rowTable = DataTables(req, SpmModel, query, columns)
                return rowTable.output_result()

            elif url_dict['tbl']=='bendaharasp2d' and self.is_akses_mod('read'):
                pk_id = 'id' in params and int(params['id']) or 0
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('pegawais.id')) 
                columns.append(ColumnDT('pegawais.kode'))
                columns.append(ColumnDT('pegawais.nama'))
                columns.append(ColumnDT('jabatans.nama'))
                columns.append(ColumnDT('units.nama'))
                columns.append(ColumnDT('mulai', filter=self._DTstrftime))
                columns.append(ColumnDT('selesai', filter=self._DTstrftime))

                query = DBSession.query(PejabatModel
                        ).join(JabatanModel, PegawaiModel
                        ).filter(and_(JabatanModel.kode >= '230', JabatanModel.kode <= '239') #Sintak Between
                        ).filter(PejabatModel.unit_id==self.unit_id,
                          JabatanModel.id==PejabatModel.jabatan_id,
                          PegawaiModel.id==PejabatModel.pegawai_id )
                rowTable = DataTables(req, PejabatModel, query, columns)
                return rowTable.output_result()

            elif url_dict['tbl']=='sp2d1' and self.is_akses_mod('read'):
                pk_id = 'id' in params and int(params['id']) or 0
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('tanggal', filter=self._DTstrftime))
                columns.append(ColumnDT('kode1'))
                columns.append(ColumnDT('nama1'))
                columns.append(ColumnDT('nominal1'))
                query = DBSession.query(Sp2dModel.id, 
                                        Sp2dModel.kode, 
                                        Sp2dModel.tanggal,
                                        SpmModel.kode.label('kode1'), 
                                        SpmModel.nama.label('nama1'), 
                                        SppModel.nominal.label('nominal1'),
                        ).join(SpmModel 
                        ).outerjoin(SppModel
                        ).filter(SppModel.tahun_id==self.tahun,
                                 SppModel.unit_id==self.unit_id,
                                 Sp2dModel.spm_id==SpmModel.id,
                                 SpmModel.spp_id==SppModel.id,
                        )
                rowTable = DataTables(req, Sp2dModel, query, columns)
                return rowTable.output_result()

            elif url_dict['tbl']=='kegiatan' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('programs.kode'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('tmt'))
                columns.append(ColumnDT('programs.nama'))
                columns.append(ColumnDT('disabled'))

                query = DBSession.query(KegiatanModel).\
                        join(ProgramModel).\
                        filter(KegiatanModel.program_id==ProgramModel.id,
                               KegiatanModel.program_id==pk_id)
                rowTable = DataTables(req, KegiatanModel, query, columns)
                # returns what is needed by DataTable
                return rowTable.output_result()

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_jabatan", renderer="../../templates/apbd/jabatan.pt")
    def admin_jabatan(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="admin_jabatan_frm", renderer="../../templates/apbd/jabatan_frm.pt")
    def admin_jabatan_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = JabatanModel.get_by_id(self.datas['id'])
                if row:
                    rows = JabatanModel.row2dict(row)
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

    @view_config(route_name="admin_jabatan_act", renderer="json")
    def admin_jabatan_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))

                query = DBSession.query(JabatanModel)
                rowTable = DataTables(req, JabatanModel, query, columns)
                # returns what is needed by DataTable
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = JabatanModel.update(p)
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    rows = JabatanModel.tambah(p)
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
                rows = JabatanModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
            elif url_dict['act']=='print' and self.is_akses_mod('read'):
                pass
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)