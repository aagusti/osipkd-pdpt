from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from pyramid.security import remember
from pyramid.security import forget
from pyramid.security import has_permission
from pyramid.renderers import render_to_response

from sqlalchemy import *
from sqlalchemy import distinct
from sqlalchemy.sql.functions import concat
from sqlalchemy.exc import DBAPIError

from osipkd.models.model_base import *
from osipkd.models.apbd_rka_models import (KegiatanSubModel, KegiatanItemModel
     )
from osipkd.models.apbd_admin_models import (TahunModel, RekeningModel
     #UserApbdModel,Unit,
     #Urusan, RekeningModel, ProgramModel, KegiatanModel, TapdModel, JabatanModel
     )
from osipkd.models.apbd_tu_models import (APInvoiceModel, APInvoiceItemModel, SppModel, SppItemModel, SpmModel, Sp2dModel,KetetapanModel,ARInvoiceModel, ARInvoiceItemModel, StsModel, StsItemModel
     )
from osipkd.models.apbd_ak_models import (JurnalModel, JurnalItemModel)
from osipkd.views.views import (BaseViews, TuBaseViews)

from datetime import datetime

class AKPPKDBaseViews(TuBaseViews):
    def __init__(self, context, request):
        self.app = 'c200'
        TuBaseViews.__init__(self, context, request)
        
    @view_config(route_name="c200", renderer="../../templates/apbd/akppkd/home.pt")
    def c200(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#Jurnal Penerimaan           
class C202001View(TuBaseViews):
    def __init__(self, context, request):
        TuBaseViews.__init__(self, context, request)
        self.session['mod'] = 'C202001'

    @view_config(route_name="c202_001", renderer="../../templates/apbd/akppkd/C202001.pt")
    def c202_001(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="c202_001_frm", renderer="../../templates/apbd/akppkd/C202001_frm.pt")
    def c202_001_frm(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        self.datas['jurnal_item_id'] = 'jurnal_item_id' in params and int(params['jurnal_item_id']) or 0

        self.datas['grid2'] = ""        
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = JurnalModel.get_by_id(self.datas['id'])
                if row:
                    self.datas['grid2'] = "".join(["grid2?kid=",str(row.id)])
                    return dict(datas=self.datas, rows=row)
                else:
                    if self.datas['id']>0:
                        return HTTPNotFound() #TODO: Warning Data Not Found
                return dict(datas=self.datas,rows='')
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="c202_001_act", renderer="json")
    def c202_001_act(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        
        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('tanggal', filter=self._DTstrftime))
                columns.append(ColumnDT('jv_type'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('source'))
                columns.append(ColumnDT('sourceno'))
                
                query = DBSession.query(JurnalModel.id,
                          JurnalModel.kode,
                          JurnalModel.tanggal,
                          JurnalModel.jv_type,
                          case([(JurnalModel.jv_type==1,"JT"),(JurnalModel.jv_type==2,"JK"),
                          (JurnalModel.jv_type==3,"JU"),(JurnalModel.jv_type==4,"KR"),(JurnalModel.jv_type==5,"CL")], else_="").label('jv_type'),
                          JurnalModel.nama,
                          JurnalModel.source,
                          JurnalModel.sourceno,
                        ).filter(JurnalModel.tahun_id==self.tahun,
                              JurnalModel.unit_id==self.unit_id,
                              JurnalModel.jv_type==1,
                              JurnalModel.is_skpd==1,
                        ).order_by(JurnalModel.no_urut.desc()
                        )

                rowTable = DataTables(req, JurnalModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='grid2'and self.is_akses_mod('read'):
                # defining columns
                pk_id = 'kid' in params and int(params['kid']) or 0
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('debet'))
                columns.append(ColumnDT('kredit'))
                columns.append(ColumnDT('notes'))
                columns.append(ColumnDT('rekening_kode'))
                
                query = DBSession.query(JurnalItemModel.id,
                          JurnalItemModel.kode,
                          JurnalItemModel.nama,
                          JurnalItemModel.debet,
                          JurnalItemModel.kredit,
                          JurnalItemModel.notes,
                          RekeningModel.kode.label('rekening_kode'),
                        ).join(RekeningModel, JurnalModel,
                        ).filter(JurnalItemModel.jurnal_id==JurnalModel.id,
                                 JurnalModel.id==pk_id,
                                 JurnalModel.unit_id==self.unit_id,
                        )

                rowTable = DataTables(req, JurnalItemModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                rows={}

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    #p['kode'] = p['kode'] or JurnalModel.get_kode(p)
                    try:
                        rows = JurnalModel.update(p)
                    except:
                        pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['posted_by']  = self.session['user_id']
                    p['jv_type']  = 1
                    p['no_urut'] = p['no_urut'] or JurnalModel.get_no_urut(p)
                    #p['kode'] = p['kode'] or JurnalModel.get_kode(p)
                    #try:
                    rows = JurnalModel.tambah(p)
                    #except:
                        #pass
                else:
                    rows={}
                
                if rows:
                    self.d['msg']='Sukses Simpan Data'
                    self.d['success']=True
                else:
                    self.d['msg']='Gagal Simpan Data'
                
                return self.d
                
            elif url_dict['act']=='saveitem':
                p = params.copy()
                rows={}
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = JurnalItemModel.update(p)
                    
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']

                    rows = JurnalItemModel.tambah(p)
                    
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
                rows = JurnalModel.hapus(d)
                
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d

            elif url_dict['act']=='delitem' and self.is_akses_mod('delete'):
                d={}
                d['id'] = pk_id
                rows = JurnalItemModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d                
                 
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#Jurnal Pengeluaran           
class C202002View(TuBaseViews):
    def __init__(self, context, request):
        TuBaseViews.__init__(self, context, request)
        self.session['mod'] = 'C202002'

    @view_config(route_name="c202_002", renderer="../../templates/apbd/akppkd/C202002.pt")
    def c202_002(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="c202_002_frm", renderer="../../templates/apbd/akppkd/C202002_frm.pt")
    def c202_002_frm(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        self.datas['jurnal_item_id'] = 'jurnal_item_id' in params and int(params['jurnal_item_id']) or 0

        self.datas['grid2'] = ""        
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = JurnalModel.get_by_id(self.datas['id'])
                if row:
                    self.datas['grid2'] = "".join(["grid2?kid=",str(row.id)])
                    return dict(datas=self.datas, rows=row)
                else:
                    if self.datas['id']>0:
                        return HTTPNotFound() #TODO: Warning Data Not Found
                return dict(datas=self.datas,rows='')
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="c202_002_act", renderer="json")
    def c202_002_act(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        
        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('tanggal', filter=self._DTstrftime))
                columns.append(ColumnDT('jv_type'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('source'))
                columns.append(ColumnDT('sourceno'))
                
                query = DBSession.query(JurnalModel.id,
                          JurnalModel.kode,
                          JurnalModel.tanggal,
                          JurnalModel.jv_type,
                          case([(JurnalModel.jv_type==1,"JT"),(JurnalModel.jv_type==2,"JK"),
                          (JurnalModel.jv_type==3,"JU"),(JurnalModel.jv_type==4,"KR"),(JurnalModel.jv_type==5,"CL")], else_="").label('jv_type'),
                          JurnalModel.nama,
                          JurnalModel.source,
                          JurnalModel.sourceno,
                        ).filter(JurnalModel.tahun_id==self.tahun,
                              JurnalModel.unit_id==self.unit_id,
                              JurnalModel.jv_type==2,
                              JurnalModel.is_skpd==1,
                        ).order_by(JurnalModel.no_urut.desc()
                        )

                rowTable = DataTables(req, JurnalModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='grid2'and self.is_akses_mod('read'):
                # defining columns
                pk_id = 'kid' in params and int(params['kid']) or 0
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('debet'))
                columns.append(ColumnDT('kredit'))
                columns.append(ColumnDT('notes'))
                columns.append(ColumnDT('rekening_kode'))
                
                query = DBSession.query(JurnalItemModel.id,
                          JurnalItemModel.kode,
                          JurnalItemModel.nama,
                          JurnalItemModel.debet,
                          JurnalItemModel.kredit,
                          JurnalItemModel.notes,
                          RekeningModel.kode.label('rekening_kode'),
                        ).join(RekeningModel, JurnalModel,
                        ).filter(JurnalItemModel.jurnal_id==JurnalModel.id,
                                 JurnalModel.id==pk_id,
                                 JurnalModel.unit_id==self.unit_id,
                        )

                rowTable = DataTables(req, JurnalItemModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                rows={}

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    #p['nominal'] = JurnalModel.get_nominal(p)
                    #p['kode'] = p['kode'] or JurnalModel.get_kode(p)
                    try:
                        rows = JurnalModel.update(p)
                    except:
                        pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['posted_by']  = self.session['user_id']
                    p['jv_type']  = 2
                    p['no_urut'] = p['no_urut'] or JurnalModel.get_no_urut(p)
                    
                    #try:
                    rows = JurnalModel.tambah(p)
                    #except:
                        #pass
                else:
                    rows={}
                
                if rows:
                    self.d['msg']='Sukses Simpan Data'
                    self.d['success']=True
                else:
                    self.d['msg']='Gagal Simpan Data'
                
                return self.d
                
            elif url_dict['act']=='saveitem':
                p = params.copy()
                rows={}
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = JurnalItemModel.update(p)
                    
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']

                    rows = JurnalItemModel.tambah(p)
                    
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
                rows = JurnalModel.hapus(d)
                
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d

            elif url_dict['act']=='delitem' and self.is_akses_mod('delete'):
                d={}
                d['id'] = pk_id
                rows = JurnalItemModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d                
                 
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#Jurnal Umum           
class C202003View(TuBaseViews):
    def __init__(self, context, request):
        TuBaseViews.__init__(self, context, request)
        self.session['mod'] = 'C202003'

    @view_config(route_name="c202_003", renderer="../../templates/apbd/akppkd/C202003.pt")
    def c202_003(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="c202_003_frm", renderer="../../templates/apbd/akppkd/C202003_frm.pt")
    def c202_003_frm(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        self.datas['jurnal_item_id'] = 'jurnal_item_id' in params and int(params['jurnal_item_id']) or 0

        self.datas['grid2'] = ""        
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = JurnalModel.get_by_id(self.datas['id'])
                if row:
                    self.datas['grid2'] = "".join(["grid2?kid=",str(row.id)])
                    return dict(datas=self.datas, rows=row)
                else:
                    if self.datas['id']>0:
                        return HTTPNotFound() #TODO: Warning Data Not Found
                return dict(datas=self.datas,rows='')
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="c202_003_act", renderer="json")
    def c202_003_act(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        
        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('tanggal', filter=self._DTstrftime))
                columns.append(ColumnDT('jv_type'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('source'))
                columns.append(ColumnDT('sourceno'))
                
                query = DBSession.query(JurnalModel.id,
                          JurnalModel.kode,
                          JurnalModel.tanggal,
                          JurnalModel.jv_type,
                          case([(JurnalModel.jv_type==1,"JT"),(JurnalModel.jv_type==2,"JK"),
                          (JurnalModel.jv_type==3,"JU"),(JurnalModel.jv_type==4,"KR"),(JurnalModel.jv_type==5,"CL")], else_="").label('jv_type'),
                          JurnalModel.nama,
                          JurnalModel.source,
                          JurnalModel.sourceno,
                        ).filter(JurnalModel.tahun_id==self.tahun,
                              JurnalModel.unit_id==self.unit_id,
                              JurnalModel.jv_type==3,
                              JurnalModel.is_skpd==1,
                        ).order_by(JurnalModel.no_urut.desc()
                        )

                rowTable = DataTables(req, JurnalModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='grid2'and self.is_akses_mod('read'):
                # defining columns
                pk_id = 'kid' in params and int(params['kid']) or 0
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('debet'))
                columns.append(ColumnDT('kredit'))
                columns.append(ColumnDT('notes'))
                columns.append(ColumnDT('rekening_kode'))
                
                query = DBSession.query(JurnalItemModel.id,
                          JurnalItemModel.kode,
                          JurnalItemModel.nama,
                          JurnalItemModel.debet,
                          JurnalItemModel.kredit,
                          JurnalItemModel.notes,
                          RekeningModel.kode.label('rekening_kode'),
                        ).join(RekeningModel, JurnalModel,
                        ).filter(JurnalItemModel.jurnal_id==JurnalModel.id,
                                 JurnalModel.id==pk_id,
                                 JurnalModel.unit_id==self.unit_id,
                        )

                rowTable = DataTables(req, JurnalItemModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                rows={}

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    #p['nominal'] = JurnalModel.get_nominal(p)
                    #p['kode'] = p['kode'] or JurnalModel.get_kode(p)
                    try:
                        rows = JurnalModel.update(p)
                    except:
                        pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['posted_by']  = self.session['user_id']
                    p['jv_type']  = 3
                    p['no_urut'] = p['no_urut'] or JurnalModel.get_no_urut(p)
                    
                    #try:
                    rows = JurnalModel.tambah(p)
                    #except:
                        #pass
                else:
                    rows={}
                
                if rows:
                    self.d['msg']='Sukses Simpan Data'
                    self.d['success']=True
                else:
                    self.d['msg']='Gagal Simpan Data'
                
                return self.d
                
            elif url_dict['act']=='saveitem':
                p = params.copy()
                rows={}
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = JurnalItemModel.update(p)
                    
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']

                    rows = JurnalItemModel.tambah(p)
                    
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
                rows = JurnalModel.hapus(d)
                
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d

            elif url_dict['act']=='delitem' and self.is_akses_mod('delete'):
                d={}
                d['id'] = pk_id
                rows = JurnalItemModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d                
                 
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#Jurnal Koreksi           
class C202004View(TuBaseViews):
    def __init__(self, context, request):
        TuBaseViews.__init__(self, context, request)
        self.session['mod'] = 'C202004'

    @view_config(route_name="c202_004", renderer="../../templates/apbd/akppkd/C202004.pt")
    def c202_004(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="c202_004_frm", renderer="../../templates/apbd/akppkd/C202004_frm.pt")
    def c202_004_frm(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        self.datas['jurnal_item_id'] = 'jurnal_item_id' in params and int(params['jurnal_item_id']) or 0

        self.datas['grid2'] = ""        
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = JurnalModel.get_by_id(self.datas['id'])
                if row:
                    self.datas['grid2'] = "".join(["grid2?kid=",str(row.id)])
                    return dict(datas=self.datas, rows=row)
                else:
                    if self.datas['id']>0:
                        return HTTPNotFound() #TODO: Warning Data Not Found
                return dict(datas=self.datas,rows='')
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="c202_004_act", renderer="json")
    def c202_004_act(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        
        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('tanggal', filter=self._DTstrftime))
                columns.append(ColumnDT('jv_type'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('source'))
                columns.append(ColumnDT('sourceno'))
                
                query = DBSession.query(JurnalModel.id,
                          JurnalModel.kode,
                          JurnalModel.tanggal,
                          JurnalModel.jv_type,
                          case([(JurnalModel.jv_type==1,"JT"),(JurnalModel.jv_type==2,"JK"),
                          (JurnalModel.jv_type==3,"JU"),(JurnalModel.jv_type==4,"KR"),(JurnalModel.jv_type==5,"CL")], else_="").label('jv_type'),
                          JurnalModel.nama,
                          JurnalModel.source,
                          JurnalModel.sourceno,
                        ).filter(JurnalModel.tahun_id==self.tahun,
                              JurnalModel.unit_id==self.unit_id,
                              JurnalModel.jv_type==4,
                              JurnalModel.is_skpd==1,
                        ).order_by(JurnalModel.no_urut.desc()
                        )

                rowTable = DataTables(req, JurnalModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='grid2'and self.is_akses_mod('read'):
                # defining columns
                pk_id = 'kid' in params and int(params['kid']) or 0
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('debet'))
                columns.append(ColumnDT('kredit'))
                columns.append(ColumnDT('notes'))
                columns.append(ColumnDT('rekening_kode'))
                
                query = DBSession.query(JurnalItemModel.id,
                          JurnalItemModel.kode,
                          JurnalItemModel.nama,
                          JurnalItemModel.debet,
                          JurnalItemModel.kredit,
                          JurnalItemModel.notes,
                          RekeningModel.kode.label('rekening_kode'),
                        ).join(RekeningModel, JurnalModel,
                        ).filter(JurnalItemModel.jurnal_id==JurnalModel.id,
                                 JurnalModel.id==pk_id,
                                 JurnalModel.unit_id==self.unit_id,
                        )

                rowTable = DataTables(req, JurnalItemModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                rows={}

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    #p['nominal'] = JurnalModel.get_nominal(p)
                    #p['kode'] = p['kode'] or JurnalModel.get_kode(p)
                    try:
                        rows = JurnalModel.update(p)
                    except:
                        pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['posted_by']  = self.session['user_id']
                    p['jv_type']  = 4
                    p['no_urut'] = p['no_urut'] or JurnalModel.get_no_urut(p)
                    
                    #try:
                    rows = JurnalModel.tambah(p)
                    #except:
                        #pass
                else:
                    rows={}
                
                if rows:
                    self.d['msg']='Sukses Simpan Data'
                    self.d['success']=True
                else:
                    self.d['msg']='Gagal Simpan Data'
                
                return self.d
                
            elif url_dict['act']=='saveitem':
                p = params.copy()
                rows={}
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = JurnalItemModel.update(p)
                    
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']

                    rows = JurnalItemModel.tambah(p)
                    
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
                rows = JurnalModel.hapus(d)
                
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d

            elif url_dict['act']=='delitem' and self.is_akses_mod('delete'):
                d={}
                d['id'] = pk_id
                rows = JurnalItemModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d                
                 
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#Jurnal Penutup           
class C202005View(TuBaseViews):
    def __init__(self, context, request):
        TuBaseViews.__init__(self, context, request)
        self.session['mod'] = 'C202005'

    @view_config(route_name="c202_005", renderer="../../templates/apbd/akppkd/C202005.pt")
    def c202_005(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="c202_005_frm", renderer="../../templates/apbd/akppkd/C202005_frm.pt")
    def c202_005_frm(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        self.datas['jurnal_item_id'] = 'jurnal_item_id' in params and int(params['jurnal_item_id']) or 0

        self.datas['grid2'] = ""        
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = JurnalModel.get_by_id(self.datas['id'])
                if row:
                    self.datas['grid2'] = "".join(["grid2?kid=",str(row.id)])
                    return dict(datas=self.datas, rows=row)
                else:
                    if self.datas['id']>0:
                        return HTTPNotFound() #TODO: Warning Data Not Found
                return dict(datas=self.datas,rows='')
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="c202_005_act", renderer="json")
    def c202_005_act(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        
        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('tanggal', filter=self._DTstrftime))
                columns.append(ColumnDT('jv_type'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('source'))
                columns.append(ColumnDT('sourceno'))
                
                query = DBSession.query(JurnalModel.id,
                          JurnalModel.kode,
                          JurnalModel.tanggal,
                          JurnalModel.jv_type,
                          case([(JurnalModel.jv_type==1,"JT"),(JurnalModel.jv_type==2,"JK"),
                          (JurnalModel.jv_type==3,"JU"),(JurnalModel.jv_type==4,"KR"),(JurnalModel.jv_type==5,"CL")], else_="").label('jv_type'),
                          JurnalModel.nama,
                          JurnalModel.source,
                          JurnalModel.sourceno,
                        ).filter(JurnalModel.tahun_id==self.tahun,
                              JurnalModel.unit_id==self.unit_id,
                              JurnalModel.jv_type==5,
                              JurnalModel.is_skpd==1,
                        ).order_by(JurnalModel.no_urut.desc()
                        )

                rowTable = DataTables(req, JurnalModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='grid2'and self.is_akses_mod('read'):
                # defining columns
                pk_id = 'kid' in params and int(params['kid']) or 0
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('debet'))
                columns.append(ColumnDT('kredit'))
                columns.append(ColumnDT('notes'))
                columns.append(ColumnDT('rekening_kode'))
                
                query = DBSession.query(JurnalItemModel.id,
                          JurnalItemModel.kode,
                          JurnalItemModel.nama,
                          JurnalItemModel.debet,
                          JurnalItemModel.kredit,
                          JurnalItemModel.notes,
                          RekeningModel.kode.label('rekening_kode'),
                        ).join(RekeningModel, JurnalModel,
                        ).filter(JurnalItemModel.jurnal_id==JurnalModel.id,
                                 JurnalModel.id==pk_id,
                                 JurnalModel.unit_id==self.unit_id,
                        )

                rowTable = DataTables(req, JurnalItemModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                rows={}

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    #p['nominal'] = JurnalModel.get_nominal(p)
                    #p['kode'] = p['kode'] or JurnalModel.get_kode(p)
                    try:
                        rows = JurnalModel.update(p)
                    except:
                        pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['posted_by']  = self.session['user_id']
                    p['jv_type']=5
                    p['no_urut'] = p['no_urut'] or JurnalModel.get_no_urut(p)
                    
                    #try:
                    rows = JurnalModel.tambah(p)
                    #except:
                        #pass
                else:
                    rows={}
                
                if rows:
                    self.d['msg']='Sukses Simpan Data'
                    self.d['success']=True
                else:
                    self.d['msg']='Gagal Simpan Data'
                
                return self.d
                
            elif url_dict['act']=='saveitem':
                p = params.copy()
                rows={}
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = JurnalItemModel.update(p)
                    
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']

                    rows = JurnalItemModel.tambah(p)
                    
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
                rows = JurnalModel.hapus(d)
                
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d

            elif url_dict['act']=='delitem' and self.is_akses_mod('delete'):
                d={}
                d['id'] = pk_id
                rows = JurnalItemModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d                
                 
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#Jurnal Item
class C202997View(TuBaseViews):
    @view_config(route_name="c202_997", renderer="../../templates/apbd/akppkd/C202997.pt")
    def c202_997(self):
        params = self.request.params
        self.jurnal_id = 'jurnal_id' in params and params['jurnal_id'] and int(params['jurnal_id']) or 0
        if self.jurnal_id or not 'jurnal_id' in self.session:
            self.session['jurnal_id'] = self.jurnal_id
        self.jurnal_id = self.session['jurnal_id']
        self.session['menu'] = "".join(['997?jurnal_id=', str(self.jurnal_id)])
        
        if self.logged and self.is_akses_mod('read'):
            return dict(datas=self.datas, row=JurnalModel.get_header(self.unit_id, self.jurnal_id))
        else:
            if not self.logged:
                headers=forget(self.request)
                return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            else:
                headers=forget(self.request)
                return HTTPFound(location='/c200', headers=headers)

    @view_config(route_name="c202_997_frm", renderer="../../templates/apbd/akppkd/C202997_frm.pt")
    def c202_997_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        self.datas['jurnal_id'] = 'jurnal_id' in params and int(params['jurnal_id']) or 0
        self.datas['kegiatan_sub_id'] = 'kegiatan_sub_id' in params and int(params['kegiatan_sub_id']) or 0
        self.datas['grid2'] = ""
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = JurnalItemModel.get_by_id(self.datas['id'])
                if row:
                    #self.datas['grid2'] = "".join(["grid2?kid=",str(row.JurnalItemModel.kegiatan_sub_id)])
                    return dict(datas=self.datas, rows=row)
                else:
                    if self.datas['id']>0:
                        return HTTPNotFound() #TODO: Warning Data Not Found
                return dict(datas=self.datas,rows='')
            else:
                return HTTPNotFound() #TODO: Warning Hak Akses 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="c202_997_act", renderer="json")
    def c202_997_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict
        
        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
                
            if url_dict['act']=='save':
                p = params.copy()       
                rows={}

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    print '**********',p
                    rows = JurnalItemModel.update(p)

                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['id'] = p['id'] or JurnalItemModel.get_jurnal_item_id(p)

                    rows = JurnalItemModel.tambah(p)

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
                rows = JurnalItemModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#Posting STS           
class C201001View(TuBaseViews):
    def __init__(self, context, request):
        TuBaseViews.__init__(self, context, request)
        self.session['mod'] = 'C201001'

    @view_config(route_name="c201_001", renderer="../../templates/apbd/akppkd/C201001.pt")
    def c201_001(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="c201_001_act", renderer="json")
    def c201_001_act(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        
        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('jenis'))
                columns.append(ColumnDT('tgl_sts', filter=self._DTstrftime))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nominal'))
                columns.append(ColumnDT('posted'))
                
                query = DBSession.query(StsModel.id,
                          StsModel.no_urut,
                          StsModel.kode,
                          StsModel.tgl_sts,
                          case([(StsModel.jenis==1,"P"),(StsModel.jenis==2,"CP"),
                          (StsModel.jenis==3,"L")], else_="").label('jenis'),
                          StsModel.nama,
                          StsModel.nominal,
                          case([(StsModel.posted==0,"N"),(StsModel.posted==1,"Y")], else_="").label('posted'),
                          #StsModel.posted
                        ).filter(StsModel.tahun_id==self.tahun,
                              StsModel.unit_id==self.unit_id,
                        ).order_by(StsModel.no_urut.desc()
                        )

                rowTable = DataTables(req, StsModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='posting' and self.is_akses_mod('posting'):
                d={}
                d['id'] = pk_id
                d['update_uid'] = self.session['user_id']
                d['posted'] = 1
                rows = StsModel.update(d)
                if rows:
                    self.d['msg']='Sukses Posting Data'
                    self.d['success']=True
                return self.d

            elif url_dict['act']=='unposting' and self.is_akses_mod('unposting'):
                d={}
                d['id'] = pk_id
                d['update_uid'] = self.session['user_id']
                d['posted'] = 0
                rows = StsModel.update(d)
                if rows:
                    self.d['msg']='Sukses UnPosting Data'
                    self.d['success']=True
                return self.d    

            elif url_dict['act']=='posting_all' and self.is_akses_mod('posting_all'):
                d={}
                d['id'] = pk_id
                d['update_uid'] = self.session['user_id']
                d['posted'] = 1
                rows = StsModel.update(d)
                if rows:
                    self.d['msg']='Sukses Posting Data'
                    self.d['success']=True
                return self.d

            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#Posting SP2D           
class C201002View(TuBaseViews):
    def __init__(self, context, request):
        TuBaseViews.__init__(self, context, request)
        self.session['mod'] = 'C201002'

    @view_config(route_name="c201_002", renderer="../../templates/apbd/akppkd/C201002.pt")
    def c201_002(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="c201_002_act", renderer="json")
    def c201_002_act(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        
        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('tanggal', filter=self._DTstrftime))
                columns.append(ColumnDT('nama1'))
                columns.append(ColumnDT('nominal1'))
                columns.append(ColumnDT('posted'))
                query = DBSession.query(Sp2dModel.id, 
                                        Sp2dModel.kode, 
                                        Sp2dModel.tanggal,
                                        SpmModel.nama.label('nama1'), 
                                        SppModel.nominal.label('nominal1'),
                                        case([(Sp2dModel.posted==0,"N"),(Sp2dModel.posted==1,"Y")], else_="").label('posted'),

                        ).join(SpmModel 
                        ).outerjoin(SppModel
                        ).filter(SppModel.tahun_id==self.tahun,
                                 SppModel.unit_id==self.unit_id,
                                 Sp2dModel.spm_id==SpmModel.id,
                        )
                rowTable = DataTables(req, Sp2dModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                rows={}

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    #p['nominal'] = JurnalModel.get_nominal(p)
                    #p['kode'] = p['kode'] or JurnalModel.get_kode(p)
                    try:
                        rows = JurnalModel.update(p)
                    except:
                        pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['posted_by']  = self.session['user_id']
                    p['no_urut'] = p['no_urut'] or JurnalModel.get_no_urut(p)
                    
                    #try:
                    rows = JurnalModel.tambah(p)
                    #except:
                        #pass
                else:
                    rows={}
                
                if rows:
                    self.d['msg']='Sukses Simpan Data'
                    self.d['success']=True
                else:
                    self.d['msg']='Gagal Simpan Data'
                
                return self.d

#Posting Apinvoice           
class C201003View(TuBaseViews):
    def __init__(self, context, request):
        TuBaseViews.__init__(self, context, request)
        self.session['mod'] = 'C201003'

    @view_config(route_name="c201_003", renderer="../../templates/apbd/akppkd/C201003.pt")
    def c201_003(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="c201_003_act", renderer="json")
    def c201_003_act(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        
        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('jenis'))
                columns.append(ColumnDT('ap_tanggal', filter=self._DTstrftime))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('jml_tagihan'))
                columns.append(ColumnDT('posted'))
                query = DBSession.query(APInvoiceModel.id,
                          APInvoiceModel.no_urut,
                          case([(APInvoiceModel.jenis==1,"UP"),(APInvoiceModel.jenis==2,"TU"),
                          (APInvoiceModel.jenis==3,"GU"),(APInvoiceModel.jenis==4,"LS")], else_="").label('jenis'),
                          APInvoiceModel.ap_tanggal,
                          APInvoiceModel.nama,
                          APInvoiceModel.jml_tagihan,
                         case([(APInvoiceModel.posted==0,"N"),(APInvoiceModel.posted==1,"Y")], else_="").label('posted'),
                        ).outerjoin(APInvoiceItemModel
                        ).filter(APInvoiceModel.tahun_id==self.tahun,
                              APInvoiceModel.unit_id==self.unit_id,
                              APInvoiceModel.kegiatan_sub_id==KegiatanSubModel.id,
                        ).order_by(APInvoiceModel.no_urut.desc()
                        ).group_by(APInvoiceModel.id,
                          APInvoiceModel.no_urut,
                          APInvoiceModel.jenis,
                          APInvoiceModel.ap_tanggal,
                          KegiatanSubModel.nama.label('kegiatan_sub_nm'),
                          APInvoiceModel.nama,
                        )
                rowTable = DataTables(req, APInvoiceModel, query, columns)
                return rowTable.output_result()
            elif url_dict['act']=='save':
                p = params.copy()
                rows={}

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    #p['nominal'] = JurnalModel.get_nominal(p)
                    #p['kode'] = p['kode'] or JurnalModel.get_kode(p)
                    try:
                        rows = JurnalModel.update(p)
                    except:
                        pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['posted_by']  = self.session['user_id']
                    p['no_urut'] = p['no_urut'] or JurnalModel.get_no_urut(p)
                    
                    #try:
                    rows = JurnalModel.tambah(p)
                    #except:
                        #pass
                else:
                    rows={}
                
                if rows:
                    self.d['msg']='Sukses Simpan Data'
                    self.d['success']=True
                else:
                    self.d['msg']='Gagal Simpan Data'
                
                return self.d

#Posting Arinvoice           
class C201004View(TuBaseViews):
    def __init__(self, context, request):
        TuBaseViews.__init__(self, context, request)
        self.session['mod'] = 'C201004'

    @view_config(route_name="c201_004", renderer="../../templates/apbd/akppkd/C201004.pt")
    def c201_004(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="c201_004_act", renderer="json")
    def c201_004_act(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        
        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('tgl_terima', filter=self._DTstrftime))
                columns.append(ColumnDT('bendahara_nm'))
                columns.append(ColumnDT('penyetor'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nilai'))
                columns.append(ColumnDT('posted'))
                query = DBSession.query(ARInvoiceModel.id,
                          ARInvoiceModel.kode,
                          ARInvoiceModel.tgl_terima,
                          ARInvoiceModel.bendahara_nm,
                          ARInvoiceModel.penyetor,
                          ARInvoiceModel.nama,
                          ARInvoiceModel.nilai,
                          case([(ARInvoiceModel.posted==0,"N"),(ARInvoiceModel.posted==1,"Y")], else_="").label('posted'),
                        ).filter(ARInvoiceModel.tahun_id==self.tahun,
                              ARInvoiceModel.unit_id==self.unit_id,
                        ).order_by(ARInvoiceModel.id.asc()
                        )
                rowTable = DataTables(req, ARInvoiceModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                rows={}

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    #p['nominal'] = JurnalModel.get_nominal(p)
                    #p['kode'] = p['kode'] or JurnalModel.get_kode(p)
                    try:
                        rows = JurnalModel.update(p)
                    except:
                        pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['posted_by']  = self.session['user_id']
                    p['no_urut'] = p['no_urut'] or JurnalModel.get_no_urut(p)
                    
                    #try:
                    rows = JurnalModel.tambah(p)
                    #except:
                        #pass
                else:
                    rows={}
                
                if rows:
                    self.d['msg']='Sukses Simpan Data'
                    self.d['success']=True
                else:
                    self.d['msg']='Gagal Simpan Data'
                
                return self.d