import os
import uuid
from osipkd.tools import row2dict, xls_reader
from datetime import datetime
from sqlalchemy import not_, func
from sqlalchemy.sql.expression import and_
from ziggurat_foundations.models import groupfinder
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
from osipkd.models.apbd_anggaran import Tahun
from osipkd.models.pemda_model import  STATUS_APBD
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah Tahun gagal'
SESS_EDIT_FAILED = 'Edit Tahun gagal'
@colander.deferred
def deferred_status_apbd(node, kw):
    values = kw.get('status_apbd', [])
    return widget.SelectWidget(values=values)

class AddSchema(colander.Schema):
    tahun           =  colander.SchemaNode(
                        colander.Integer(),
                        ) 
    status_apbd     =  colander.SchemaNode(
                        colander.Integer(),
                        widget = deferred_status_apbd)
    tgl_entry       = colander.SchemaNode(
                        colander.Date(),
                        missing = colander.drop)
    tgl_evaluasi    = colander.SchemaNode(
                        colander.Date(),
                        missing = colander.drop)
    tanggal_1       = colander.SchemaNode(
                        colander.Date(),
                        missing = colander.drop)
    tanggal_2       = colander.SchemaNode(
                        colander.Date(),
                        missing = colander.drop)
    tanggal_3       = colander.SchemaNode(
                        colander.Date(),
                        missing = colander.drop) 
    tanggal_4       = colander.SchemaNode(
                        colander.Date(),
                        missing = colander.drop) 
    no_perda        = colander.SchemaNode(
                        colander.String(),
                        missing = colander.drop)
    tgl_perda       = colander.SchemaNode(
                        colander.Date(),
                        missing = colander.drop)
                        
    no_perkdh       = colander.SchemaNode(
                        colander.String(),
                        missing = colander.drop)
    tgl_perkdh      = colander.SchemaNode(
                        colander.Date(),
                        missing = colander.drop) 
    no_perda_rev    = colander.SchemaNode(
                        colander.String(),
                        missing = colander.drop)
    tgl_perda_rev   = colander.SchemaNode(
                        colander.Date(),
                        missing = colander.drop)
    no_perkdh_rev   = colander.SchemaNode(
                        colander.String(),
                        missing = colander.drop) 
    tgl_perkdh_rev  = colander.SchemaNode(
                        colander.Date(),
                        missing = colander.drop)
                        
    no_lpj          = colander.SchemaNode(
                        colander.String(),
                        missing = colander.drop)        
    tgl_lpj         = colander.SchemaNode(
                        colander.Date(),
                        missing = colander.drop)
class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))
class view_tahun(BaseViews):
    ########                    
    # List #
    ########    
            
    @view_config(route_name='apbd-tahun', renderer='templates/apbd-tahun/list.pt',
                 permission='read')
    def view_list(self):
        return dict(a={})
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='apbd-tahun-act', renderer='json',
                 permission='view')
    def gaji_tahun_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('tahun'))
            columns.append(ColumnDT('status_apbd', filter = self._StatusAPBD))
            columns.append(ColumnDT('tgl_entry'))
            columns.append(ColumnDT('tgl_evaluasi'))
            query = DBSession.query(Tahun)
            rowTable = DataTables(req, Tahun, query, columns)
            return rowTable.output_result()
            
                
                  
    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(Tahun).filter_by(id=uid)
            tahun = q.first()
        else:
            tahun = None
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind(status_apbd=STATUS_APBD)
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
    def save(self, values, user, row=None):
        if not row:
            row = Tahun()
            row.created = datetime.now()
            row.create_uid = user.id
            row.id = values['tahun']
        row.from_dict(values)
        row.updated = datetime.now()
        row.update_uid = user.id
        row.disabled = 'disabled' in values and values['disabled'] and 1 or 0
        DBSession.add(row)
        DBSession.flush()
        return row
    def save_request(self, values, row=None):
        if 'id' in self.request.matchdict:
            values['id'] = self.request.matchdict['id']
        row = self.save(values, self.request.user, row)
        self.request.session.flash('tahun sudah disimpan.')
    def route_list(self):
        return HTTPFound(location=self.request.route_url('apbd-tahun'))
    def session_failed(self, session_name):
        r = dict(form=self.session[session_name])
        del self.session[session_name]
        return r
    @view_config(route_name='apbd-tahun-add', renderer='templates/apbd-tahun/add.pt',
                 permission='add')
    def view_tahun_add(self):
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
                    return HTTPFound(location=req.route_url('tahun-add'))
                self.save_request(dict(controls))
            return self.route_list()
        elif SESS_ADD_FAILED in req.session:
            return self.session_failed(SESS_ADD_FAILED)
        return dict(form=form)
    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(Tahun).filter_by(id=self.request.matchdict['id'])
    def id_not_found(self):    
        msg = 'Tahun ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()
    @view_config(route_name='apbd-tahun-edit', renderer='templates/apbd-tahun/edit.pt',
                 permission='edit')
    def view_tahun_edit(self):
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
                    return HTTPFound(location=request.route_url('tahun-edit',
                                      id=row.id))
                self.save_request(dict(controls), row)
            return self.route_list()
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)
        values = row.to_dict()
        return dict(form=form.render(appstruct=values))
    ##########
    # Delete #
    ##########    
    @view_config(route_name='apbd-tahun-delete', renderer='templates/apbd-tahun/delete.pt',
                 permission='delete')
    def view_tahun_delete(self):
        request = self.request
        q = self.query_id()
        row = q.first()
        if not row:
            return self.id_not_found(request)
        form = Form(colander.Schema(), buttons=('hapus','batal'))
        if request.POST:
            if 'hapus' in request.POST:
                msg = 'Tahun %d %s sudah dihapus.' % (row.id, row.status_apbd)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'Tahun %d %s tidak dapat dihapus.' % (row.id, row.status_apbd)
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row,
                     form=form.render())