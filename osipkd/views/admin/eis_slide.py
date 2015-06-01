import os
import uuid
from osipkd.tools import row2dict, xls_reader
from datetime import datetime
from sqlalchemy import not_, func
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from osipkd.models import DBSession
from osipkd.models.eis import Slide
from sqlalchemy.sql.expression import update
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews
    

SESS_ADD_FAILED = 'Tambah eis-slide gagal'
SESS_EDIT_FAILED = 'Edit eis-slide gagal'

@colander.deferred
def deferred_slide_type(node, kw):
    values = kw.get('slide_type', [])
    return widget.SelectWidget(values=values)
    
SLIDE_TYPE = (('image','Gambar'),
           ('grid','Grid'),
           ('chart-line','Chart Garis'),
           ('chart-bar','Chart-Bar'),
           ('chart-pie', 'Chart-Pie'))
           
class AddSchema(colander.Schema):
    kode  = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=18),
                    oid='kode')
                    
    nama = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=128),
                    oid = 'nama')
    source_type = colander.SchemaNode(
                    colander.String(),
                    widget=deferred_slide_type)
                                    
    source_id  = colander.SchemaNode(
                    colander.String(),
                    missing = colander.drop)
                    
    order_id   = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    missing = 0)
                
    is_aktif   = colander.SchemaNode(
                    colander.Boolean())
    disabled   = colander.SchemaNode(
                    colander.Boolean())

class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))
            
class view_eis_slide(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='eis-slide', renderer='templates/eis-slide/list.pt',
                 permission='read')
    def view_list(self):
        return dict(a={})
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='eis-slide-act', renderer='json',
                 permission='read')
    def eis_slide_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('kode'))
            columns.append(ColumnDT('nama'))
            columns.append(ColumnDT('source_type'))
            columns.append(ColumnDT('source_id'))
            columns.append(ColumnDT('order_id'))
            columns.append(ColumnDT('is_aktif'))
            columns.append(ColumnDT('disabled'))
            query = DBSession.query(Slide)
            rowTable = DataTables(req, Slide, query, columns)
            return rowTable.output_result()
        
    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(Slide).filter_by(id=uid)
            row = q.first()
        else:
            row = None
                
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind(slide_type=SLIDE_TYPE)
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, user, row=None):
        if not row:
            row = Slide()
            row.created = datetime.now()
            row.create_uid = user.id
        row.from_dict(values)
        row.updated = datetime.now()
        row.update_uid = user.id
        row.is_aktif = 'is_aktif' in values and values['is_aktif'] and 1 or 0
        row.disabled = 'disabled' in values and values['disabled'] and 1 or 0
        DBSession.add(row)
        DBSession.flush()
        if 'is_aktif' in values and values['is_aktif']:
            stmt = update(Slide).where(Slide.id!=row.id).\
                   values(is_aktif=0)
            DBSession.execute(stmt)
            DBSession.flush()
         
        return row
        
    def save_request(self, values, row=None):
        if 'id' in self.request.matchdict:
            values['id'] = self.request.matchdict['id']
        row = self.save(values, self.request.user, row)
        self.request.session.flash('Slide sudah disimpan.')
            
    def route_list(self):
        return HTTPFound(location=self.request.route_url('eis-slide'))
        
    def session_failed(self, session_name):
            
        #r = dict(form=self.session[session_name])
        del self.session[session_name]
        #return r
        
    @view_config(route_name='eis-slide-add', renderer='templates/eis-slide/add.pt',
                 permission='add')
    def view_eis_slide_add(self):
        req = self.request
        ses = self.session
        form = self.get_form(AddSchema)
        if req.POST:
            if 'simpan' in req.POST:
                controls = req.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    #req.session[SESS_ADD_FAILED] = e.render()     
                    #form.set_appstruct(rowd)
                    return dict(form=form)
                    #return HTTPFound(location=req.route_url('eis-slide-add'))
                self.save_request(dict(controls))
            return self.route_list()
        elif SESS_ADD_FAILED in req.session:
            return dict(form=form)
        
            #return self.session_failed(SESS_ADD_FAILED)
        return dict(form=form)

        
    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(Slide).filter_by(id=self.request.matchdict['id'])
        
    def id_not_found(self):    
        msg = 'Slide ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()

    @view_config(route_name='eis-slide-edit', renderer='templates/eis-slide/add.pt',
                 permission='edit')
    def view_eis_slide_edit(self):
        request = self.request
        row = self.query_id().first()
        if not row:
            return id_not_found(request)
        #values = row.to_dict()
        rowd={}
        rowd['id']          = row.id
        rowd['kode']        = row.kode
        rowd['nama']        = row.nama
        rowd['source_type']    = row.source_type
        rowd['source_id']    = row.source_id
        rowd['order_id']    = row.order_id
        rowd['is_aktif']    = row.is_aktif
        rowd['disabled']    = row.disabled
        
        form = self.get_form(EditSchema)
        form.set_appstruct(rowd)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                print controls
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form)
                    #request.session[SESS_EDIT_FAILED] = e.render()               
                    #return HTTPFound(location=request.route_url('eis-slide-edit',
                    #                  id=row.id))
                self.save_request(dict(controls), row)
            return self.route_list()
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)
        return dict(form=form)

    ##########
    # Delete #
    ##########    
    @view_config(route_name='eis-slide-delete', renderer='templates/eis-slide/delete.pt',
                 permission='delete')
    def view_eis_slide_delete(self):
        request = self.request
        q = self.query_id()
        row = q.first()
        
        if not row:
            return self.id_not_found(request)
        form = Form(colander.Schema(), buttons=('hapus','batal'))
        if request.POST:
            if 'hapus' in request.POST:
                msg = 'Slide ID %d %s sudah dihapus.' % (row.id, row.nama)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'Slide ID %d %s tidak dapat dihapus.' % (row.id, row.nama)
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row,
                     form=form.render())

