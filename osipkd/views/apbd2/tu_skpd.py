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
from osipkd.views.views import (BaseViews, TuBaseViews)
#from datetime import datetime

class TUSKPDBaseViews(TuBaseViews):
    def __init__(self, context, request):
        self.app = 'b100'
        TuBaseViews.__init__(self, context, request)
        
    @view_config(route_name="b100", renderer="../../templates/apbd/tuskpd/home.pt")
    def b100(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#SPJ            
class B103001View(TuBaseViews):
    def __init__(self, context, request):
        TuBaseViews.__init__(self, context, request)
        self.session['mod'] = 'B103001'

    @view_config(route_name="b103_001", renderer="../../templates/apbd/tuskpd/B103001.pt")
    def b103_001(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b103_001_frm", renderer="../../templates/apbd/tuskpd/B103001_frm.pt")
    def b103_001_frm(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        self.datas['apinvoice_item_id'] = 'apinvoice_item_id' in params and int(params['apinvoice_item_id']) or 0
        
        self.datas['grid2'] = ""
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = APInvoiceModel.get_by_id(self.datas['id'])
                if row:
                    self.datas['grid2'] = "".join(["grid2?kid=",str(row.kegiatan_sub_id)])
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

    @view_config(route_name="b103_001_act", renderer="json")
    def b103_001_act(self):
        req    = self.request
        params = req.params
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
                columns.append(ColumnDT('kegiatan_sub_nm'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('jml_tagihan'))

                query = DBSession.query(APInvoiceModel.id,
                          APInvoiceModel.no_urut,
                          case([(APInvoiceModel.jenis==1,"UP"),(APInvoiceModel.jenis==2,"TU"),
                          (APInvoiceModel.jenis==3,"GU"),(APInvoiceModel.jenis==4,"LS")], else_="").label('jenis'),
                          APInvoiceModel.ap_tanggal,
                          KegiatanSubModel.nama.label('kegiatan_sub_nm'),
                          APInvoiceModel.nama,
                          APInvoiceModel.jml_tagihan,
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

            if url_dict['act']=='grid2' and self.is_akses_mod('read'):
                # defining columns
                kid = 'kid' in params and params['kid'] or 0
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('kegiatanitems.rekenings.kode'))
                columns.append(ColumnDT('nama'))
                #columns.append(ColumnDT('vol_1'))
                #columns.append(ColumnDT('vol_2'))
                #columns.append(ColumnDT('harga'))
                columns.append(ColumnDT('nilai'))
                #columns.append(ColumnDT('ppn_prsn'))
                columns.append(ColumnDT('ppn'))
                #columns.append(ColumnDT('pph_prsn'))
                columns.append(ColumnDT('pph'))
                #columns.append(ColumnDT('pph_id'))
                
                query = DBSession.query(APInvoiceItemModel
                        ).join(APInvoiceModel
                        ).join(KegiatanItemModel
                        ).filter(APInvoiceModel.kegiatan_sub_id==kid,
                                 APInvoiceModel.unit_id==self.unit_id
                        ).order_by(APInvoiceItemModel.no_urut.asc())
                rowTable = DataTables(req, KegiatanItemModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                rows={}
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    p['jml_tagihan'] = APInvoiceModel.get_jml_tagihan(p)
                    #try:
                    rows = APInvoiceModel.update(p)
                    #except:
                    #    pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['no_urut'] = p['no_urut'] or APInvoiceModel.get_no_urut(p)
                    
                    try:
                        rows = APInvoiceModel.tambah(p)
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
            elif url_dict['act']=='saveitem':
                p = params.copy()
                p['no_urut'] = APInvoiceItemModel.get_no_urut(p)
                rows={}
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    #try:
                    rows = APInvoiceItemModel.update(p)
                    #except:
                    #    pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['no_urut'] = p['no_urut'] or APInvoiceItemModel.get_no_urut(p)
                    
                    try:
                        rows = APInvoiceItemModel.tambah(p)
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
                rows = APInvoiceModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            elif url_dict['act']=='delitem' and self.is_akses_mod('delete'):
                d={}
                d['id'] = pk_id
                rows = APInvoiceItemModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d                

            else:
                HTTPNotFound()            
      
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

class B103997View(TuBaseViews):
    @view_config(route_name="b103_997", renderer="../../templates/apbd/tuskpd/B103997.pt")
    def b103_997(self):
        params = self.request.params
        self.apinvoice_id = 'apinvoice_id' in params and params['apinvoice_id'] and int(params['apinvoice_id']) or 0
        if self.apinvoice_id or not 'apinvoice_id' in self.session:
            self.session['apinvoice_id'] = self.apinvoice_id
        self.apinvoice_id = self.session['apinvoice_id']
        self.session['menu'] = "".join(['997?apinvoice_id=', str(self.apinvoice_id)])
        
        if self.logged and self.is_akses_mod('read'):
            return dict(datas=self.datas, row=APInvoiceModel.get_header(self.unit_id, self.apinvoice_id))
        else:
            if not self.logged:
                headers=forget(self.request)
                return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            else:
                headers=forget(self.request)
                return HTTPFound(location='/b100', headers=headers)

    @view_config(route_name="b103_997_frm", renderer="../../templates/apbd/tuskpd/B103997_frm.pt")
    def b103_997_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        self.datas['apinvoice_id'] = 'apinvoice_id' in params and int(params['apinvoice_id']) or 0
        self.datas['kegiatan_sub_id'] = 'kegiatan_sub_id' in params and int(params['kegiatan_sub_id']) or 0
        self.datas['grid2'] = ""
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = APInvoiceItemModel.get_by_id(self.datas['id'])
                if row:
                    self.datas['grid2'] = "".join(["grid2?kid=",str(row.apinvoices.kegiatan_sub_id)])
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

    @view_config(route_name="b103_997_act", renderer="json")
    def b103_997_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict
        
        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            #self.apinvoice_id = 'kid' in params and params['kid'] and int(params['kid']) or 0
            #kid = 'kid' in params and params['kid'] or 0

            if url_dict['act']=='grid1' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kegiatanitems.rekenings.kode'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nilai'))
                columns.append(ColumnDT('ppn'))
                columns.append(ColumnDT('pph'))
                
                query = DBSession.query(APInvoiceItemModel
                        ).join(APInvoiceModel
                        ).join(KegiatanItemModel
                        ).filter(APInvoiceItemModel.apinvoice_id==APInvoiceModel.id,
                                 APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                                 APInvoiceModel.unit_id==self.unit_id,
                                 APInvoiceModel.kegiatan_sub_id==KegiatanItemModel.kegiatan_sub_id
                        )
                rowTable = DataTables(req, APInvoiceItemModel, query, columns)
                return rowTable.output_result()
                
            elif url_dict['act']=='save':
                p = params.copy()
                
                rows={}
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    #try:
                    print '**********',p
                    rows = APInvoiceItemModel.update(p)
                    #except:
                    #    pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['no_urut'] = APInvoiceItemModel.get_no_urut(p)
                    p['id'] = p['id'] or APInvoiceItemModel.get_apinvoice_item_id(p)
                    try:
                        rows = APInvoiceItemModel.tambah(p)
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
                
            elif url_dict['act']=='saveitem':
                p = params.copy()
                p['no_urut'] = APInvoiceItemModel.get_no_urut(p)
                print '****^^^^',p
                rows={}
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    #try:
                    rows = APInvoiceItemModel.update(p)
                    #except:
                    #    pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['no_urut'] = p['no_urut'] or APInvoiceItemModel.get_no_urut(p)
                    
                    try:
                        rows = APInvoiceItemModel.tambah(p)
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
                rows = APInvoiceItemModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#SPP            
class B103002View(TuBaseViews):
    def __init__(self, context, request):
        TuBaseViews.__init__(self, context, request)
        self.session['mod'] = 'B103002'

    @view_config(route_name="b103_002", renderer="../../templates/apbd/tuskpd/B103002.pt")
    def b103_002(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b103_002_frm", renderer="../../templates/apbd/tuskpd/B103002_frm.pt")
    def b103_002_frm(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        #self.datas['grid2'] = ""
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = SppModel.get_by_id(self.datas['id'])
                if row:
                    #self.datas['grid2'] = "".join(["grid2?kid=",str(row.kegiatan_sub_id)])
                    #rows=SppModel.rowdict(row)
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

    @view_config(route_name="b103_002_act", renderer="json")
    def b103_002_act(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            spp_id = 'spp_id' in params and int(params['spp_id']) or 0

            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('tanggal', filter=self._DTstrftime))
                columns.append(ColumnDT('jenis'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nominal'))
                
                query = DBSession.query(SppModel.id,
                          SppModel.kode,
                          SppModel.tanggal,
                          case([(SppModel.jenis==1,"UP"),(SppModel.jenis==2,"TU"),
                          (SppModel.jenis==3,"GU"),(SppModel.jenis==4,"LS")], else_="").label('jenis'),
                          SppModel.nama,
                          SppModel.nominal
                        ).filter(SppModel.tahun_id==self.tahun,
                              SppModel.unit_id==self.unit_id,
                        ).order_by(SppModel.no_urut.desc()
                        )

                rowTable = DataTables(req, SppModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='grid2' and self.is_akses_mod('read'):
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('jenis'))
                columns.append(ColumnDT('ap_tanggal', filter=self._DTstrftime))
                columns.append(ColumnDT('kegiatan_item_nm'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nilai'))

                query = DBSession.query(SppItemModel.id,
                          APInvoiceModel.no_urut, 
                          APInvoiceModel.jenis,
                          APInvoiceModel.ap_tanggal,
                          KegiatanItemModel.nama.label('kegiatan_item_nm'),
                          APInvoiceModel.nama,
                          func.sum(APInvoiceItemModel.nilai).label('nilai'),
                        ).filter(SppItemModel.apinvoice_id==APInvoiceModel.id,
                              APInvoiceModel.id==APInvoiceItemModel.apinvoice_id,
                              APInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                              APInvoiceModel.tahun_id==self.tahun,
                              APInvoiceModel.unit_id==self.unit_id,
                              SppItemModel.spp_id==spp_id
                        ).order_by(APInvoiceModel.no_urut.desc()
                        ).group_by(SppItemModel.id,
                          APInvoiceModel.no_urut,
                          APInvoiceModel.jenis,
                          APInvoiceModel.ap_tanggal,
                          KegiatanItemModel.nama,
                          APInvoiceModel.nama,
                        )

                rowTable = DataTables(req, SppItemModel, query, columns)
                return rowTable.output_result()
            
            elif url_dict['act']=='save':
                p = params.copy()
                rows={}
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    p['nominal'] = SppModel.get_nominal(p)
                    p['kode'] = p['kode'] or SppModel.get_kode(p)
                    #try:
                    rows = SppModel.update(p)
                    #except:
                    #    pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    #p['posted']  = self.session['user_id']
                    p['no_urut'] = p['no_urut'] or SppModel.get_no_urut(p)
                    
                    try:
                        rows = SppModel.tambah(p)
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
                
            elif url_dict['act']=='saveitem':
                p = params.copy()
                rows={}
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = SppItemModel.update(p)
                    
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']

                    rows = SppItemModel.tambah(p)
                    
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
                rows = SppModel.hapus(d)
                
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d

            elif url_dict['act']=='delitem' and self.is_akses_mod('delete'):
                d={}
                d['id'] = pk_id
                rows = SppItemModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d                
                 
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#SPM  
class B103003View(TuBaseViews):
    def __init__(self, context, request):
        TuBaseViews.__init__(self, context, request)
        self.session['mod'] = 'B103003'

    @view_config(route_name="b103_003", renderer="../../templates/apbd/tuskpd/B103003.pt")
    def b103_003(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b103_003_frm", renderer="../../templates/apbd/tuskpd/B103003_frm.pt")
    def b103_003_frm(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        #self.datas['grid2'] = ""
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = SpmModel.get_by_id(self.datas['id'])
                if row:
                    #self.datas['grid2'] = "".join(["grid2?kid=",str(row.kegiatan_sub_id)])
                    #rows=SppModel.rowdict(row)
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

    @view_config(route_name="b103_003_act", renderer="json")
    def b103_003_act(self):
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
                columns.append(ColumnDT('jenis'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nominal'))
                
                query = DBSession.query(SpmModel.id,
                          SpmModel.kode,
                          SpmModel.tanggal,
                          case([(SppModel.jenis==1,"UP"),(SppModel.jenis==2,"TU"),
                          (SppModel.jenis==3,"GU"),(SppModel.jenis==4,"LS")], else_="").label('jenis'),
                          SpmModel.nama,
                          SppModel.nominal
                          ).filter(SpmModel.spp_id==SppModel.id,
                              SppModel.tahun_id==self.tahun,
                              SppModel.unit_id==self.unit_id

                        ).order_by(SpmModel.kode.desc()
                        )

                rowTable = DataTables(req, SpmModel, query, columns)
                return rowTable.output_result()

            
            elif url_dict['act']=='save':
                p = params.copy()
                rows={}
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    #try:
                    del(p['unit_id'])
                    rows = SpmModel.update(p)
                    #except:
                    #    pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    #p['no_urut'] = p['no_urut'] or APInvoiceModel.get_no_urut(p)
                    
                    try:
                        rows = SpmModel.tambah(p)
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
                rows = SpmModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#Ketetapan          
class B102001View(TuBaseViews):
    def __init__(self, context, request):
        TuBaseViews.__init__(self, context, request)
        self.session['mod'] = 'B102001'

    @view_config(route_name="b102_001", renderer="../../templates/apbd/tuskpd/B102001.pt")
    def b102_001(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b102_001_frm", renderer="../../templates/apbd/tuskpd/B102001_frm.pt")
    def b102_001_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        self.datas['rekening_id'] = 'rekening_id' in params and int(params['rekening_id']) or 0
        
        self.datas['grid2'] = ""
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = KetetapanModel.get_by_id(self.datas['id'])
                if row:
                    self.datas['grid2'] = "".join(["grid2?kid=",str(row.rekening_id)])
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

    @view_config(route_name="b102_001_act", renderer="json")
    def b102_001_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('tgl_ketetapan', filter=self._DTstrftime))
                columns.append(ColumnDT('rekenings.kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('jumlah'))

                query = DBSession.query(KetetapanModel
                        ).join(RekeningModel
                        ).filter(KetetapanModel.tahun_id==self.tahun,
                              KetetapanModel.unit_id==self.unit_id,
                              KetetapanModel.rekening_id==RekeningModel.id,
                        ).order_by(KetetapanModel.id.asc()
                        )
                rowTable = DataTables(req, KetetapanModel, query, columns)
                return rowTable.output_result()

            if url_dict['act']=='grid2' and self.is_akses_mod('read'):
                # defining columns
                kid = 'kid' in params and params['kid'] or 0
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('kegiatanitems.rekenings.kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nilai'))
                columns.append(ColumnDT('ppn'))
                columns.append(ColumnDT('pph'))
                
                query = DBSession.query(APInvoiceItemModel
                        ).join(APInvoiceModel
                        ).join(KegiatanItemModel
                        ).filter(APInvoiceModel.kegiatan_sub_id==kid,
                                 APInvoiceModel.unit_id==self.unit_id
                        ).order_by(APInvoiceItemModel.no_urut.asc())
                rowTable = DataTables(req, KegiatanItemModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                rows={}
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    #try:
                    rows = KetetapanModel.update(p)
                    #except:
                    #    pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    
                    try:
                        rows = KetetapanModel.tambah(p)
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
                rows = KetetapanModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#TBP           
class B102002View(TuBaseViews):
    def __init__(self, context, request):
        TuBaseViews.__init__(self, context, request)
        self.session['mod'] = 'B102002'

    @view_config(route_name="b102_002", renderer="../../templates/apbd/tuskpd/B102002.pt")
    def b102_002(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b102_002_frm", renderer="../../templates/apbd/tuskpd/B102002_frm.pt")
    def b102_002_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        self.datas['arinvoice_item_id'] = 'arinvoice_item_id' in params and int(params['arinvoice_item_id']) or 0
        
        self.datas['grid2'] = ""
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = ARInvoiceModel.get_by_id(self.datas['id'])
                if row:
                    self.datas['grid2'] = "".join(["grid2?kid=",str(row.kegiatan_sub_id)])
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

    @view_config(route_name="b102_002_act", renderer="json") 
    def b102_002_act(self):
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
                columns.append(ColumnDT('tgl_terima', filter=self._DTstrftime))
                columns.append(ColumnDT('tgl_validasi', filter=self._DTstrftime))
                columns.append(ColumnDT('bendahara_nm'))
                columns.append(ColumnDT('penyetor'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nilai'))

                query = DBSession.query(ARInvoiceModel.id,
                          ARInvoiceModel.kode,
                          ARInvoiceModel.tgl_terima,
                          ARInvoiceModel.tgl_validasi,
                          ARInvoiceModel.bendahara_nm,
                          ARInvoiceModel.penyetor,
                          ARInvoiceModel.nama,
                          ARInvoiceModel.nilai,
                        ).filter(ARInvoiceModel.tahun_id==self.tahun,
                              ARInvoiceModel.unit_id==self.unit_id,
                        ).order_by(ARInvoiceModel.id.asc()
                        )
                rowTable = DataTables(req, ARInvoiceModel, query, columns)
                return rowTable.output_result()

            if url_dict['act']=='grid2' and self.is_akses_mod('read'):
                # defining columns
                kid = 'kid' in params and params['kid'] or 0
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('kegiatanitems.rekenings.kode'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nilai'))
                
                query = DBSession.query(ARInvoiceItemModel
                        ).join(ARInvoiceModel
                        ).join(KegiatanItemModel
                        ).filter(ARInvoiceModel.kegiatan_sub_id==kid,
                                 ARInvoiceModel.unit_id==self.unit_id
                        )
                rowTable = DataTables(req, KegiatanItemModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                rows={}
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1
                
                if pk_id and self.is_akses_mod('edit'): #update
                    
                    p['update_uid'] = self.session['user_id']
                    #try:
                    p['nilai'] = ARInvoiceModel.get_nilai(p)
                    rows = ARInvoiceModel.update(p)
                    #except:
                    #    pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['posted']=0
                    #p['kode'] = ARInvoiceModel.get_kode(p)
                    
                    #try:
                    rows = ARInvoiceModel.tambah(p)
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
                p['no_urut'] = ARInvoiceItemModel.get_no_urut(p)
                rows={}
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    #try:
                    rows = ARInvoiceItemModel.update(p)
                    #except:
                    #    pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['no_urut'] = p['no_urut'] or ARInvoiceItemModel.get_no_urut(p)
                    
                    try:
                        rows = ARInvoiceItemModel.tambah(p)
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
                rows = ARInvoiceModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            elif url_dict['act']=='delitem' and self.is_akses_mod('delete'):
                d={}
                d['id'] = pk_id
                rows = ARInvoiceItemModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d                

            else:
                HTTPNotFound()            
      
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
  
class B102996View(TuBaseViews):
    @view_config(route_name="b102_996", renderer="../../templates/apbd/tuskpd/B102996.pt")
    def b102_996(self):
        params = self.request.params
        self.arinvoice_id = 'arinvoice_id' in params and params['arinvoice_id'] and int(params['arinvoice_id']) or 0
        if self.arinvoice_id or not 'arinvoice_id' in self.session:
            self.session['arinvoice_id'] = self.arinvoice_id
        self.arinvoice_id = self.session['arinvoice_id']
        self.session['menu'] = "".join(['996?arinvoice_id=', str(self.arinvoice_id)])
        
        if self.logged and self.is_akses_mod('read'):
            return dict(datas=self.datas, row=ARInvoiceModel.get_header(self.unit_id, self.arinvoice_id))
        else:
            if not self.logged:
                headers=forget(self.request)
                return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            else:
                headers=forget(self.request)
                return HTTPFound(location='/b100', headers=headers)

    @view_config(route_name="b102_996_frm", renderer="../../templates/apbd/tuskpd/B102996_frm.pt")
    def b102_996_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        self.datas['arinvoice_id'] = 'arinvoice_id' in params and int(params['arinvoice_id']) or 0
        self.datas['kegiatan_sub_id'] = 'kegiatan_sub_id' in params and int(params['kegiatan_sub_id']) or 0
        self.datas['grid2'] = ""
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = ARInvoiceItemModel.get_by_id(self.datas['id'])
                if row:
                    self.datas['grid2'] = "".join(["grid2?kid=",str(row.arinvoices.kegiatan_sub_id)])
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

    @view_config(route_name="b102_996_act", renderer="json")
    def b102_996_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict
        
        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            #self.arinvoice_id = 'kid' in params and params['kid'] and int(params['kid']) or 0
            #kid = 'kid' in params and params['kid'] or 0

            if url_dict['act']=='grid1' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kegiatanitems.rekenings.kode'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nilai'))
                
                query = DBSession.query(ARInvoiceItemModel
                        ).join(ARInvoiceModel
                        ).join(KegiatanItemModel
                        ).filter(ARInvoiceItemModel.arinvoice_id==ARInvoiceModel.id,
                                 ARInvoiceItemModel.kegiatan_item_id==KegiatanItemModel.id,
                                 ARInvoiceModel.unit_id==self.unit_id,
                                 ARInvoiceModel.kegiatan_sub_id==KegiatanItemModel.kegiatan_sub_id
                        )
                rowTable = DataTables(req, ARInvoiceItemModel, query, columns)
                return rowTable.output_result()
                
            elif url_dict['act']=='save':
                p = params.copy()
                
                rows={}
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    #try:
                    print '**********',p
                    rows = ARInvoiceItemModel.update(p)
                    #except:
                    #    pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['no_urut'] = ARInvoiceItemModel.get_no_urut(p)
                    p['id'] = p['id'] or ARInvoiceItemModel.get_arinvoice_item_id(p)
                    try:
                        rows = ARInvoiceItemModel.tambah(p)
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
                
            elif url_dict['act']=='saveitem':
                p = params.copy()
                p['no_urut'] = ARInvoiceItemModel.get_no_urut(p)
                print '****^^^^',p
                rows={}
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    #try:
                    rows = ARInvoiceItemModel.update(p)
                    #except:
                    #    pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['no_urut'] = p['no_urut'] or ARInvoiceItemModel.get_no_urut(p)
                    
                    try:
                        rows = ARInvoiceItemModel.tambah(p)
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
                rows = ARInvoiceItemModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
  
#STS Bendahara Penerimaan
class B102003View(TuBaseViews):
    def __init__(self, context, request):
        TuBaseViews.__init__(self, context, request)
        self.session['mod'] = 'B102003'

    @view_config(route_name="b102_003", renderer="../../templates/apbd/tuskpd/B102003.pt")
    def b102_003(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b102_003_frm", renderer="../../templates/apbd/tuskpd/B102003_frm.pt")
    def b102_003_frm(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = StsModel.get_by_id(self.datas['id'])
                if row:
                    #rows=StsModel.rowdict(row)
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

    @view_config(route_name="b102_003_act", renderer="json")
    def b102_003_act(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            sts_id = 'sts_id' in params and int(params['sts_id']) or 0

            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('tgl_sts', filter=self._DTstrftime))
                columns.append(ColumnDT('tgl_validasi', filter=self._DTstrftime))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nominal'))
                
                query = DBSession.query(StsModel.id,
                          StsModel.no_urut,
                          StsModel.kode,
                          StsModel.tgl_sts,
                          StsModel.tgl_validasi,
                          StsModel.nama,
                          StsModel.nominal
                        ).filter(StsModel.tahun_id==self.tahun,
                                 StsModel.unit_id==self.unit_id,
                                 StsModel.jenis==1,
                        ).order_by(StsModel.no_urut.desc()
                        )

                rowTable = DataTables(req, StsModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='grid2' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('sts_id'))                
                columns.append(ColumnDT('arinvoice_id'))
                columns.append(ColumnDT('arinvoices.kode'))
                columns.append(ColumnDT('arinvoices.tgl_terima', filter=self._DTstrftime))
                columns.append(ColumnDT('arinvoices.tgl_validasi', filter=self._DTstrftime))
                columns.append(ColumnDT('arinvoices.bendahara_nm'))
                columns.append(ColumnDT('arinvoices.penyetor'))
                columns.append(ColumnDT('arinvoices.nama'))
                columns.append(ColumnDT('arinvoices.nilai'))

                query = DBSession.query(StsItemModel
                        ).join(StsModel, ARInvoiceModel
                        ).filter(StsItemModel.sts_id==sts_id,
                                 StsItemModel.arinvoice_id==ARInvoiceModel.id,
                        )
                rowTable = DataTables(req, StsItemModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                rows={}
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    p['nominal'] = StsModel.get_nominal(p)

                    rows = StsModel.update(p)

                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['jenis']=1
                    p['no_urut'] = p['no_urut'] or StsModel.get_no_urut(p)
                    
                    try:
                        rows = StsModel.tambah(p)
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
                
            elif url_dict['act']=='saveitem':
                p = params.copy()
                rows={}
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = StsItemModel.update(p)
                    
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    
                    #try:
                    rows = StsItemModel.tambah(p)

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
                rows = StsModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d

            elif url_dict['act']=='delitem' and self.is_akses_mod('delete'):
                d={}
                d['id'] = pk_id
                rows = StsItemModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d                
                 
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#STS Kontra Pos
class B102004View(TuBaseViews):
    def __init__(self, context, request):
        TuBaseViews.__init__(self, context, request)
        self.session['mod'] = 'B102004'

    @view_config(route_name="b102_004", renderer="../../templates/apbd/tuskpd/B102004.pt")
    def b102_004(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b102_004_frm", renderer="../../templates/apbd/tuskpd/B102004_frm.pt")
    def b102_004_frm(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = StsModel.get_by_id(self.datas['id'])
                if row:
                    #rows=StsModel.rowdict(row)
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

    @view_config(route_name="b102_004_act", renderer="json")
    def b102_004_act(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            sts_id = 'sts_id' in params and int(params['sts_id']) or 0

            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('tgl_sts', filter=self._DTstrftime))
                columns.append(ColumnDT('tgl_validasi', filter=self._DTstrftime))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nominal'))
                
                query = DBSession.query(StsModel.id,
                          StsModel.no_urut,
                          StsModel.kode,
                          StsModel.tgl_sts,
                          StsModel.tgl_validasi,
                          StsModel.nama,
                          StsModel.nominal
                        ).filter(StsModel.tahun_id==self.tahun,
                                 StsModel.unit_id==self.unit_id,
                                 StsModel.jenis==2,
                        ).order_by(StsModel.no_urut.desc()
                        )

                rowTable = DataTables(req, StsModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='grid2' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('sts_id'))                
                columns.append(ColumnDT('arinvoice_id'))
                columns.append(ColumnDT('arinvoices.kode'))
                columns.append(ColumnDT('arinvoices.tgl_terima', filter=self._DTstrftime))
                columns.append(ColumnDT('arinvoices.tgl_validasi', filter=self._DTstrftime))
                columns.append(ColumnDT('arinvoices.bendahara_nm'))
                columns.append(ColumnDT('arinvoices.penyetor'))
                columns.append(ColumnDT('arinvoices.nama'))
                columns.append(ColumnDT('arinvoices.nilai'))

                query = DBSession.query(StsItemModel
                        ).join(StsModel, ARInvoiceModel
                        ).filter(StsItemModel.sts_id==sts_id,
                                 StsItemModel.arinvoice_id==ARInvoiceModel.id,
                        )
                rowTable = DataTables(req, StsItemModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                rows={}
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    p['nominal'] = StsModel.get_nominal(p)

                    rows = StsModel.update(p)

                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['jenis']=2
                    p['no_urut'] = p['no_urut'] or StsModel.get_no_urut(p)
                    
                    try:
                        rows = StsModel.tambah(p)
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
                
            elif url_dict['act']=='saveitem':
                p = params.copy()
                rows={}
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = StsItemModel.update(p)
                    
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    
                    #try:
                    rows = StsItemModel.tambah(p)

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
                rows = StsModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d

            elif url_dict['act']=='delitem' and self.is_akses_mod('delete'):
                d={}
                d['id'] = pk_id
                rows = StsItemModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d                
                 
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#STS Lainnya
class B102005View(TuBaseViews):
    def __init__(self, context, request):
        TuBaseViews.__init__(self, context, request)
        self.session['mod'] = 'B102005'

    @view_config(route_name="b102_005", renderer="../../templates/apbd/tuskpd/B102005.pt")
    def b102_005(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b102_005_frm", renderer="../../templates/apbd/tuskpd/B102005_frm.pt")
    def b102_005_frm(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = StsModel.get_by_id(self.datas['id'])
                if row:
                    #rows=StsModel.rowdict(row)
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

    @view_config(route_name="b102_005_act", renderer="json")
    def b102_005_act(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            sts_id = 'sts_id' in params and int(params['sts_id']) or 0

            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('tgl_sts', filter=self._DTstrftime))
                columns.append(ColumnDT('tgl_validasi', filter=self._DTstrftime))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nominal'))
                
                query = DBSession.query(StsModel.id,
                          StsModel.no_urut,
                          StsModel.kode,
                          StsModel.tgl_sts,
                          StsModel.tgl_validasi,
                          StsModel.nama,
                          StsModel.nominal
                        ).filter(StsModel.tahun_id==self.tahun,
                                 StsModel.unit_id==self.unit_id,
                                 StsModel.jenis==3,
                        ).order_by(StsModel.no_urut.desc()
                        )

                rowTable = DataTables(req, StsModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='grid2' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('sts_id'))                
                columns.append(ColumnDT('arinvoice_id'))
                columns.append(ColumnDT('arinvoices.kode'))
                columns.append(ColumnDT('arinvoices.tgl_terima', filter=self._DTstrftime))
                columns.append(ColumnDT('arinvoices.tgl_validasi', filter=self._DTstrftime))
                columns.append(ColumnDT('arinvoices.bendahara_nm'))
                columns.append(ColumnDT('arinvoices.penyetor'))
                columns.append(ColumnDT('arinvoices.nama'))
                columns.append(ColumnDT('arinvoices.nilai'))

                query = DBSession.query(StsItemModel
                        ).join(StsModel, ARInvoiceModel
                        ).filter(StsItemModel.sts_id==sts_id,
                                 StsItemModel.arinvoice_id==ARInvoiceModel.id,
                        )
                rowTable = DataTables(req, StsItemModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                rows={}
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    p['nominal'] = StsModel.get_nominal(p)

                    rows = StsModel.update(p)

                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['jenis']=3
                    p['no_urut'] = p['no_urut'] or StsModel.get_no_urut(p)
                    
                    try:
                        rows = StsModel.tambah(p)
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
                
            elif url_dict['act']=='saveitem':
                p = params.copy()
                rows={}
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = StsItemModel.update(p)
                    
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    
                    #try:
                    rows = StsItemModel.tambah(p)

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
                rows = StsModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d

            elif url_dict['act']=='delitem' and self.is_akses_mod('delete'):
                d={}
                d['id'] = pk_id
                rows = StsItemModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d                
                 
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)


