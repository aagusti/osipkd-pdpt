import os
import uuid
from osipkd.tools import row2dict, xls_reader
from datetime import datetime
from sqlalchemy import not_, func
from pyramid.view import (
    view_config,
    )
from pyramid.httpexceptions import (
    HTTPFound,
    )
import colander
from deform import (
    Form,
    widget,
    ValidationFailure,
    )
from osipkd.models import (
    DBSession,
    Group
    )
from osipkd.models.aset_models import AsetKategori

from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews
    

SESS_ADD_FAILED = 'Tambah kategori gagal'
SESS_EDIT_FAILED = 'Edit kategori gagal'

kat_widget = widget.AutocompleteInputWidget(
        size=60,
        values = '/aset/kategori/headofnama/act',
        min_length=1)
                
class AddSchema(colander.Schema):
    parent_id   = colander.SchemaNode(
                    colander.String(),
                    widget = widget.HiddenWidget(),
                    missing = colander.drop,
                    oid = "parent_id")
    parent_nm   = colander.SchemaNode(
                    colander.String(),
                    widget = kat_widget,
                    missing = colander.drop,
                    oid = "parent_nm",
                    title = "Header")
    kode        = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=18))
    uraian      = colander.SchemaNode(
                    colander.String())
    disabled    = colander.SchemaNode(
                    colander.Boolean())
                    
class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))
            
class view_kategori(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='aset-kategori', renderer='templates/kategori/list.pt',
                 permission='read')
    def view_list(self):
        return dict(a={})
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='aset-kategori-act', renderer='json',
                 permission='read')
    def view_act(self):
        ses = self.request.session
        req = self.request
        params   = req.params
        url_dict = req.matchdict
        
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('kode'))
            columns.append(ColumnDT('uraian'))
            columns.append(ColumnDT('parent_id'))
            columns.append(ColumnDT('level_id'))
            columns.append(ColumnDT('disabled'))
            
            query = DBSession.query(AsetKategori)
            rowTable = DataTables(req, AsetKategori, query, columns)
            return rowTable.output_result()
            
        elif url_dict['act']=='headofkode':
            term   = 'term'   in params and params['term']   or '' 
            prefix = 'prefix' in params and params['prefix'] or '' 
            q = DBSession.query(AsetKategori.id,AsetKategori.kode,AsetKategori.uraian).\
                    filter(AsetKategori.kode.ilike('%%%s%%' % term)).\
                    filter(AsetKategori.kode.ilike('%s%%' % prefix)).\
                    order_by(AsetKategori.kode)
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[1]
                d['kode']        = k[1]
                d['uraian']      = k[2]
                r.append(d)    
            return r
            
        elif url_dict['act']=='headofnama':
            term   = 'term'   in params and params['term']   or '' 
            prefix = 'prefix' in params and params['prefix'] or '' 
            q = DBSession.query(AsetKategori.id,AsetKategori.kode,AsetKategori.uraian).\
                    filter(AsetKategori.uraian.ilike('%%%s%%' % term)).\
                    filter(AsetKategori.kode.ilike('%s%%' % prefix)).\
                    order_by(AsetKategori.uraian)
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[2]
                d['kode']        = k[1]
                d['uraian']        = k[2]
                r.append(d)    
            return r
            
        elif url_dict['act']=='changeid':
            row = AsetKategori.get_by_id('kategori_id' in params and params['kategori_id'] or 0)
            if row:
                ses['kategori_id']=row.id
                ses['kategori_kd']=row.kode
                ses['kategori_nm']=row.uraian
                return {'success':True}
                
            

    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(AsetKategori).filter_by(id=uid)
            kategori = q.first()
        else:
            kategori = None
                
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind()
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, user, row=None):
        if not row:
            row = AsetKategori()
            row.created    = datetime.now()
            row.create_uid = user.id
        row.from_dict(values)
        row.updated    = datetime.now()
        row.update_uid = user.id
        row.disabled = 'disabled' in values and values['disabled'] and 1 or 0
        row.level_id =  AsetKategori.get_next_level(row.parent_id) or 1
        
        DBSession.add(row)
        DBSession.flush()
        return row
        
    def save_request(self, values, row=None):
        if 'id' in self.request.matchdict:
            values['id'] = self.request.matchdict['id']
        row = self.save(values, self.request.user, row)
        self.request.session.flash('Kategori sudah disimpan.')
            
    def route_list(self):
        return HTTPFound(location=self.request.route_url('aset-kategori'))
        
    def session_failed(self, session_name):
        r = dict(form=self.session[session_name])
        del self.session[session_name]
        return r
        
    @view_config(route_name='aset-kategori-add', renderer='templates/kategori/add.pt',
                 permission='add')
    def view_kategori_add(self):
        req  = self.request
        ses  = self.session
        form = self.get_form(AddSchema)
        if req.POST:
            if 'simpan' in req.POST:
                controls = req.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    req.session[SESS_ADD_FAILED] = e.render()               
                    return HTTPFound(location=req.route_url('kategori-add'))
                self.save_request(dict(controls))
            return self.route_list()
        elif SESS_ADD_FAILED in req.session:
            return self.session_failed(SESS_ADD_FAILED)
        return dict(form=form.render())

        
    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(AsetKategori).filter_by(id=self.request.matchdict['id'])
        
    def id_not_found(self):    
        msg = 'Kategori ID %s tidak ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()

    @view_config(route_name='aset-kategori-edit', renderer='templates/kategori/edit.pt',
                 permission='edit')
    def view_kategori_edit(self):
        request = self.request
        row     = self.query_id().first()
        
        if not row:
            return id_not_found(request)
            
        form = self.get_form(EditSchema)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                print controls
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    request.session[SESS_EDIT_FAILED] = e.render()               
                    return HTTPFound(location=request.route_url('kategori-edit', id=row.id))
                self.save_request(dict(controls), row)
            return self.route_list()
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)
        values = row.to_dict()
        values['parent_nm']= row.parent and row.parent.uraian or ""
        return dict(form=form.render(appstruct=values))

    ##########
    # Delete #
    ##########    
    @view_config(route_name='aset-kategori-delete', renderer='templates/kategori/delete.pt',
                 permission='delete')
    def view_delete(self):
        request = self.request
        q       = self.query_id()
        row     = q.first()
        
        if not row:
            return self.id_not_found(request)
            
        form = Form(colander.Schema(), buttons=('hapus','batal'))
        if request.POST:
            if 'hapus' in request.POST:
                msg = 'Kategori ID %d %s sudah dihapus.' % (row.id, row.uraian)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'Kategori ID %d %s tidak dapat dihapus.' % (row.id, row.uraian)
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row, form=form.render())
                     
"""
    @view_config(route_name="aset-kategori", renderer="templates/aset/kategori.pt")
    def aset_kategori(self):
        params = self.request.params
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="aset-kategori-add", renderer="templates/aset/kategori_frm.pt")
    def aset_kategori_frm(self):
        req = self.request
        params = req.params
        url_dict = req.matchdict
        if self.logged and self.is_akses_mod('aset_kategori'):
            self.datas['id'] = 'id' in url_dict and int(url_dict['id']) or 0
            row = AsetKategoriModel.get_by_id(self.datas['id'])
            if row:
                rows = AsetKategoriModel.row2dict(row)
                return dict(datas=self.datas, rows=rows)
            else:
                if self.datas['id']>0:
                    return HTTPNotFound()
            return dict(datas=self.datas,rows='')
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            
    @view_config(route_name="aset-kategori-act", renderer="json")
    def aset_kategori_act(self):
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
                columns.append(ColumnDT('uraian'))
                #columns.append(ColumnDT('parent_id'))
                columns.append(ColumnDT('uraian2'  or None))
                columns.append(ColumnDT('level_id'))
                columns.append(ColumnDT('disabled'))
                AliasAset = aliased(AsetKategoriModel)
                query = DBSession.query(AsetKategoriModel.id, 
                                        AsetKategoriModel.kode,
                                        AsetKategoriModel.uraian,
                                        #AsetKategoriModel.parent_id,
                                        AliasAset.uraian.label('uraian2'),
                                        AsetKategoriModel.level_id,
                                        AsetKategoriModel.disabled)\
                        .outerjoin(AliasAset)
                row = query.first()
                
                rowTable = DataTables(req, AsetKategoriModel, query, columns)
                return rowTable.output_result()

            elif url_dict['act']=='save':
                p = params.copy()
                if 'disabled' not in p:
                    p['disabled']=0
                else:
                    p['disabled']=1

                if pk_id and self.is_akses_mod('edit'): #update
                    p['update_uid'] = self.session['user_id']
                    rows = AsetKategoriModel.update(p)
                elif self.is_akses_mod('insert'): #insert
                    p['create_uid'] = self.session['user_id']
                    p['update_uid'] = self.session['user_id']
                    
                    rows = AsetKategoriModel.tambah(p)
                else:
                    rows=0
                
                if rows:
                    self.d['msg']='Sukses Simpan Data'
                    self.d['success']=True
                    self.d['id'] = rows
                else:
                    self.d['msg']='Gagal Simpan Data'
                
                return self.d
                
            elif url_dict['act']=='delete' and self.is_akses_mod('delete'):
                d={}
                d['id'] = pk_id
                rows = AsetKategoriModel.hapus(d)
                if rows:
                    self.d['msg']='Sukses Hapus Data'
                    self.d['success']=True
                return self.d
                
            else:
                HTTPNotFound()            
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
"""            