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
from osipkd.models.aset_models import AsetKategori, AsetKebijakan

from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews
    

SESS_ADD_FAILED = 'Tambah kategori gagal'
SESS_EDIT_FAILED = 'Edit kategori gagal'

kat_widget = widget.AutocompleteInputWidget(
        size=60,
        values = '/aset/kategori/headofnama/act',
        min_length=1)
                
class AddSchema(colander.Schema):
    tahun       = colander.SchemaNode(
                    colander.Integer())
    kategori_id = colander.SchemaNode(
                    colander.String(),
                    widget = widget.HiddenWidget(),
                    oid = "kategori_id")
    kategori_nm = colander.SchemaNode(
                    colander.String(),
                    widget = kat_widget,
                    oid = "kategori_nm",
                    title = "Kategori")
    masa_guna   = colander.SchemaNode(
                    colander.Integer())
    minimum     = colander.SchemaNode(
                    colander.Integer())
    disabled    = colander.SchemaNode(
                    colander.Boolean())
                    
class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))
            
class view_aset_kebijakan(BaseViews):
    # MASTER
    @view_config(route_name="aset-kebijakan", renderer="templates/kebijakan/list.pt",
                 permission="read")
    def aset_kebijakan(self):
        params = self.request.params
        return {}
        
    @view_config(route_name="aset-kebijakan-act", renderer="json",
                 permission="read")
    def aset_kebijakan_act(self):
        req      = self.request
        params   = req.params
        url_dict = req.matchdict

        pk_id = 'id' in params and int(params['id']) or 0
        if url_dict['act']=='grid':
            # defining columns
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('tahun'))
            columns.append(ColumnDT('kategoris.kode'))
            columns.append(ColumnDT('kategoris.uraian'))
            columns.append(ColumnDT('masa_guna'))
            columns.append(ColumnDT('minimum'))
            columns.append(ColumnDT('disabled'))
            
            query = DBSession.query(AsetKebijakan).\
                    join(AsetKategori).\
                    filter(AsetKebijakan.kategori_id==AsetKategori.id)

            rowTable = DataTables(req, AsetKebijakan, query, columns)
            return rowTable.output_result()

    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(AsetKebijakan).filter_by(id=uid)
            kebijakan = q.first()
        else:
            kebijakan = None
                
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind()
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, user, row=None):
        if not row:
            row = AsetKebijakan()
            row.created    = datetime.now()
            row.create_uid = user.id
        row.from_dict(values)
        row.updated    = datetime.now()
        row.update_uid = user.id
        row.disabled   = 'disabled' in values and values['disabled'] and 1 or 0
        DBSession.add(row)
        DBSession.flush()
        return row
        
    def save_request(self, values, row=None):
        if 'id' in self.request.matchdict:
            values['id'] = self.request.matchdict['id']
        row = self.save(values, self.request.user, row)
        self.request.session.flash('Kebijakan sudah disimpan.')
            
    def route_list(self):
        return HTTPFound(location=self.request.route_url('aset-kebijakan'))
        
    def session_failed(self, session_name):
        r = dict(form=self.session[session_name])
        del self.session[session_name]
        return r
        
    @view_config(route_name='aset-kebijakan-add', renderer='templates/kebijakan/add.pt',
                 permission='add')
    def view_kebijakan_add(self):
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
                    return HTTPFound(location=req.route_url('kebijakan-add'))
                self.save_request(dict(controls))
            return self.route_list()
        elif SESS_ADD_FAILED in req.session:
            return self.session_failed(SESS_ADD_FAILED)
        return dict(form=form.render())

        
    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(AsetKebijakan).filter_by(id=self.request.matchdict['id'])
        
    def id_not_found(self):    
        msg = 'Kebijakan ID %s tidak ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()

    @view_config(route_name='aset-kebijakan-edit', renderer='templates/kebijakan/edit.pt',
                 permission='edit')
    def view_kebijakan_edit(self):
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
                    return HTTPFound(location=request.route_url('kebijakan-edit',
                                      id=row.id))
                self.save_request(dict(controls), row)
            return self.route_list()
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)
        values = row.to_dict()
        values['kategori_nm']= row.kategoris and row.kategoris.uraian or ""
        return dict(form=form.render(appstruct=values))

    ##########
    # Delete #
    ##########    
    @view_config(route_name='aset-kebijakan-delete', renderer='templates/kebijakan/delete.pt',
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
                msg = 'Kebijakan ID %d sudah dihapus.' % (row.id)
                q.delete()
                DBSession.flush()
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row, form=form.render())
                        
