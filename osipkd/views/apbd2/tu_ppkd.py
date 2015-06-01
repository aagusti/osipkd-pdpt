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
from osipkd.models.apbd_admin_models import (TahunModel, Unit,
     )
from osipkd.models.apbd_tu_models import (SpdModel, SpdItemModel, Sp2dModel,SpmModel, SppModel, GiroModel, GiroItemModel
     )

from osipkd.views.views import (BaseViews, TuBaseViews, triwulans)

from datetime import datetime

class TuPpkdBaseViews(TuBaseViews):
    def __init__(self, context, request):
        self.app = 'b200'
        TuBaseViews.__init__(self, context, request)
        
    @view_config(route_name="b200", renderer="../../templates/apbd/tuppkd/home.pt")
    def b200(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#SPD
class B203003View(TuBaseViews):
    def __init__(self, context, request):
        TuBaseViews.__init__(self, context, request)
        self.session['mod'] = 'B203003'

    @view_config(route_name="b203_003", renderer="../../templates/apbd/tuppkd/B203003.pt")
    def b203_003(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b203_003_frm", renderer="../../templates/apbd/tuppkd/B203003_frm.pt")
    def b203_003_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        self.datas['triwulans'] = triwulans
        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = SpdModel.get_by_id(self.datas['id'])
                
                if row:
                    #TuBaseViews.__init__(self, self.context, self.request)
                    #self.datas['grid2'] = "".join(["grid2?kid=",str(row.kegiatan_sub_id)])
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

    @view_config(route_name="b203_003_act", renderer="json")
    def b203_003_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            spd_id = 'spd_id' in params and int(params['spd_id']) or 0
                    
            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('unit_nm'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('triwulan_id'))
                columns.append(ColumnDT('nominal'))
                query = DBSession.query(SpdModel.id, SpdModel.kode,
                          SpdModel.nama, SpdModel.triwulan_id, SpdModel.units,
                          Unit.nama.label('unit_nm'),
                         func.sum(SpdItemModel.nominal).label('nominal')
                        ).join(Unit
                        ).outerjoin(SpdItemModel
                        ).filter(SpdModel.tahun_id==self.tahun,
                                 SpdModel.unit_id==self.unit_id,
                        ).group_by(SpdModel.id, SpdModel.kode,
                          SpdModel.nama, SpdModel.triwulan_id,
                          Unit.id, Unit.nama)
                rowTable = DataTables(req, SpdModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='grid2' and self.is_akses_mod('read'):
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kegiatansubs.kode'))
                columns.append(ColumnDT('kegiatansubs.nama'))
                columns.append(ColumnDT('anggaran'))
                columns.append(ColumnDT('lalu'))
                columns.append(ColumnDT('nominal'))
                columns.append(ColumnDT('nominal'))
                columns.append(ColumnDT('nominal'))
                
                query = DBSession.query(SpdItemModel
                        ).filter(SpdItemModel.spd_id==spd_id,
                        )
                rowTable = DataTables(req, SpdItemModel, query, columns)
                return rowTable.output_result()

            
            elif url_dict['act']=='save':
                p = params.copy()
                rows={}
                if 'is_bl' not in p:
                    p['is_bl']=0
                else:
                    p['is_bl']=1
                
                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    p['kode'] = p['kode'] or SpdModel.get_kode(p)
                    rows = SpdModel.update(p)
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['kode'] = p['kode'] or SpdModel.get_kode(p)
                    rows = SpdModel.tambah(p)
                else:
                    rows=0
                
                if rows:
                    self.d['msg']='Sukses Simpan Data'
                    self.d['id']=rows or 0
                    self.d['kode']=p['kode']
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
                    rows = SpdItemModel.update(p)
                    
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    rows  = DBSession.query(
                              func.sum(KegiatanItemModel.vol_4_1*KegiatanItemModel.vol_4_2*KegiatanItemModel.hsat_4).label('anggaran'),
                              func.sum(KegiatanItemModel.bln01+KegiatanItemModel.bln02*KegiatanItemModel.bln03).label('trw1'),
                              func.sum(KegiatanItemModel.bln04+KegiatanItemModel.bln05*KegiatanItemModel.bln06).label('trw2'),
                              func.sum(KegiatanItemModel.bln07+KegiatanItemModel.bln08*KegiatanItemModel.bln09).label('trw3'),
                              func.sum(KegiatanItemModel.bln10+KegiatanItemModel.bln11*KegiatanItemModel.bln12).label('trw4')
                            ).filter(KegiatanItemModel.kegiatan_sub_id==p['kegiatan_sub_id']).first()
                    
                    spds  = DBSession.query(SpdModel).filter(SpdModel.id==p['spd_id']).first()
                    spd_tanggal = spds.tanggal
                    rows2 =  DBSession.query(
                              func.sum(SpdItemModel.nominal).label('lalu')
                            ).join(SpdModel
                            ).filter(SpdItemModel.kegiatan_sub_id==p['kegiatan_sub_id'],
                                     SpdModel.tanggal<=spd_tanggal).first()
                    
                    p['anggaran'] = rows.anggaran
                    p['lalu'] = rows2.lalu or 0
                    
                    p['nominal'] = spds.triwulan_id==1 and rows.trw1 or\
                                spds.triwulan_id==2 and rows.trw2 or\
                                spds.triwulan_id==3 and rows.trw3 or\
                                spds.triwulan_id==4 and rows.trw4 
                    if p['nominal']==0:
                        p['nominal'] = p['anggaran'] // 4
                           
                    if p['anggaran'] - p['lalu'] - p['nominal']<0:
                        p['nominal'] = p['anggaran'] - p['lalu']
                    try:
                        rows = SpdItemModel.tambah(p)
                        print p
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
                rows = SpdModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            elif url_dict['act']=='delitem' and self.is_akses_mod('delete'):
                d={}
                d['id'] = pk_id
                rows = SpdItemModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
#SP2D
class B203001View(TuBaseViews): 
    def __init__(self, context, request):
     TuBaseViews.__init__(self, context, request)
     self.session['mod'] = 'B203001'

    @view_config(route_name="b203_001", renderer="../../templates/apbd/tuppkd/B203001.pt")
    def b203_001(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b203_001_frm", renderer="../../templates/apbd/tuppkd/B203001_frm.pt")
    def b203_001_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        self.datas['spm_id'] = 'spm_id' in params and int(params['spm_id']) or 0

        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = Sp2dModel.get_by_id(self.datas['id'])
                pk_id = 'id' in params and int(params['id']) or 0
                if row:
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

    @view_config(route_name="b203_001_act", renderer="json")
    def b203_001_act(self):
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
                        )
                rowTable = DataTables(req, Sp2dModel, query, columns)
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
                    rows = Sp2dModel.update(p)
                    #except:
                    #    pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    p['posted']=0
                    #try:
                    rows = Sp2dModel.tambah(p)
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
    
            elif url_dict['act']=='delete' and self.is_akses_mod('delete'):
                d={}
                d['id'] = pk_id
                rows = Sp2dModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
                              
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

#GIRO
class B203002View(TuBaseViews): 
    def __init__(self, context, request):
     TuBaseViews.__init__(self, context, request)
     self.session['mod'] = 'B203002'

    @view_config(route_name="b203_002", renderer="../../templates/apbd/tuppkd/B203002.pt")
    def b203_002(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="b203_002_frm", renderer="../../templates/apbd/tuppkd/B203002_frm.pt")
    def b203_001_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
        self.datas['giro_id'] = 'giro_id' in params and int(params['giro_id']) or 0

        if self.logged:
            if not self.datas['id'] and self.is_akses_mod('add')\
                or self.datas['id'] and self.is_akses_mod('edit'):
                row = GiroModel.get_by_id(self.datas['id'])
                #row = Sp2dModel.get_by_id(self.datas['id'])
                if row:
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

    @view_config(route_name="b203_002_act", renderer="json")
    def b203_002_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if self.logged :
            pk_id = 'id' in params and int(params['id']) or 0
            giro_id = 'giro_id' in params and int(params['giro_id']) or 0    

            if url_dict['act']=='grid' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('tanggal', filter=self._DTstrftime))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nominal'))
                query = DBSession.query(GiroModel
                        ).join(Sp2dModel
                        ).filter(GiroModel.tahun_id==self.tahun,
                                 GiroModel.unit_id==self.unit_id ,
                                 GiroModel.sp2d_id==Sp2dModel.id,
                        ).order_by(GiroModel.kode.asc())
                rowTable = DataTables(req, GiroModel, query, columns) 
                return rowTable.output_result()

            elif url_dict['act']=='grid2' and self.is_akses_mod('read'):
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('giro_id'))
                columns.append(ColumnDT('sp2d_id'))
                columns.append(ColumnDT('sp2ds.kode'))
                columns.append(ColumnDT('sp2ds.tanggal', filter=self._DTstrftime))
                columns.append(ColumnDT('sp2ds.spms.nama'))
                columns.append(ColumnDT('sp2ds.spms.spps.nominal'))

                query = DBSession.query(GiroItemModel
                        ).join(GiroModel, Sp2dModel, SpmModel,SppModel,
                        ).filter(GiroItemModel.giro_id==giro_id,
                                 GiroItemModel.sp2d_id==Sp2dModel.id,
                                 Sp2dModel.spm_id==SpmModel.id,
                                 SpmModel.spp_id==SppModel.id,
                        )
                rowTable = DataTables(req, GiroItemModel, query, columns) 
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
                    rows = GiroModel.update(p)
                    #except:
                    #    pass
                elif self.is_akses_mod('insert'): #insert
                    p['created'] = datetime.now
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    
                    try:
                        rows = GiroModel.tambah(p)
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
                rows = GiroModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
                              
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
