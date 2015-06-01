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
from osipkd.models.efiling_models import FilingKategori

from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews
    

SESS_ADD_FAILED = 'Tambah kategori gagal'
SESS_EDIT_FAILED = 'Edit kategori gagal'

kat_widget = widget.AutocompleteInputWidget(
        size=60,
        values = '/efiling/kategori/headofnama/act',
        min_length=1)
                
class AddSchema(colander.Schema):
    parent_id  = colander.SchemaNode(
                    colander.String(),
                    widget = widget.HiddenWidget(),
                    missing = colander.drop,
                    oid = "parent_id"
                    )
    parent_nm = colander.SchemaNode(
                    colander.String(),
                    widget = kat_widget,
                    missing = colander.drop,
                    oid = "parent_nm",
                    title = "Header"
                    )
    kode = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=18))
                    
    nama = colander.SchemaNode(
                    colander.String())
    disabled = colander.SchemaNode(
                    colander.Boolean())
                    
class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))
            
class view_kategori(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='efiling-kategori', renderer='templates/kategori/list.pt',
                 permission='read')
    def view_list(self):
        return dict(a={})
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='efiling-kategori-act', renderer='json',
                 permission='read')
    def view_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('kode'))
            columns.append(ColumnDT('nama'))
            columns.append(ColumnDT('parent.kode'))
            columns.append(ColumnDT('level_id'))
            columns.append(ColumnDT('disabled'))
            
            query = DBSession.query(FilingKategori)
            rowTable = DataTables(req, FilingKategori, query, columns)
            return rowTable.output_result()
            
        elif url_dict['act']=='headofkode':
            term = 'term' in params and params['term'] or '' 
            prefix = 'prefix' in params and params['prefix'] or '' 
            q = DBSession.query(FilingKategori.id,FilingKategori.kode,FilingKategori.nama).\
                    filter(FilingKategori.kode.ilike('%%%s%%' % term)).\
                    filter(FilingKategori.kode.ilike('%s%%' % prefix)).\
                    order_by(FilingKategori.kode)
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[1]
                d['kode']        = k[1]
                d['nama']      = k[2]
                r.append(d)    
            return r
            
        elif url_dict['act']=='headofnama':
            term = 'term' in params and params['term'] or '' 
            prefix = 'prefix' in params and params['prefix'] or '' 
            q = DBSession.query(FilingKategori.id,FilingKategori.kode,FilingKategori.nama).\
                    filter(FilingKategori.nama.ilike('%%%s%%' % term)).\
                    filter(FilingKategori.kode.ilike('%s%%' % prefix)).\
                    order_by(FilingKategori.nama)
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[2]
                d['kode']        = k[1]
                d['nama']        = k[2]
                r.append(d)    
            return r
            
        elif url_dict['act']=='changeid':
            row = FilingKategori.get_by_id('kategori_id' in params and params['kategori_id'] or 0)
            if row:
                ses['kategori_id']=row.id
                ses['kategori_kd']=row.kode
                ses['kategori_nm']=row.nama
                return {'success':True}
                
            

    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(FilingKategori).filter_by(id=uid)
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
            row = FilingKategori()
            row.created = datetime.now()
            row.create_uid = user.id
        row.from_dict(values)
        row.updated = datetime.now()
        row.update_uid = user.id
        row.disabled = 'disabled' in values and values['disabled'] and 1 or 0
        row.level_id =  FilingKategori.get_next_level(row.parent_id) or 1
        DBSession.add(row)
        DBSession.flush()
        return row
        
    def save_request(self, values, row=None):
        if 'id' in self.request.matchdict:
            values['id'] = self.request.matchdict['id']
        row = self.save(values, self.request.user, row)
        self.request.session.flash('kategori sudah disimpan.')
            
    def route_list(self):
        return HTTPFound(location=self.request.route_url('efiling-kategori'))
        
    def session_failed(self, session_name):
        r = dict(form=self.session[session_name])
        del self.session[session_name]
        return r
        
    @view_config(route_name='efiling-kategori-add', renderer='templates/kategori/add.pt',
                 permission='add')
    def view_kategori_add(self):
        req = self.request
        ses = self.session
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
        return DBSession.query(FilingKategori).filter_by(id=self.request.matchdict['id'])
        
    def id_not_found(self):    
        msg = 'kategori ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()

    @view_config(route_name='efiling-kategori-edit', renderer='templates/kategori/edit.pt',
                 permission='edit')
    def view_kategori_edit(self):
        request = self.request
        row = self.query_id().first()
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
                    return HTTPFound(location=request.route_url('kategori-edit',
                                      id=row.id))
                self.save_request(dict(controls), row)
            return self.route_list()
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)
        values = row.to_dict()
        values['parent_nm']= row.parent and row.parent.nama or ""
        return dict(form=form.render(appstruct=values))

    ##########
    # Delete #
    ##########    
    @view_config(route_name='efiling-kategori-delete', renderer='templates/kategori/delete.pt',
                 permission='delete')
    def view_delete(self):
        request = self.request
        q = self.query_id()
        row = q.first()
        
        if not row:
            return self.id_not_found(request)
        form = Form(colander.Schema(), buttons=('hapus','batal'))
        if request.POST:
            if 'hapus' in request.POST:
                msg = 'kategori ID %d %s sudah dihapus.' % (row.id, row.nama)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'kategori ID %d %s tidak dapat dihapus.' % (row.id, row.nama)
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row,
                     form=form.render())
 