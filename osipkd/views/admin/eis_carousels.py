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
    DBSession
    )
from osipkd.models.eis import (
    Eis
    )
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews
    

SESS_ADD_FAILED = 'Tambah carousel gagal'
SESS_EDIT_FAILED = 'Edit carousel gagal'

rek_widget = widget.AutocompleteInputWidget(
        size=60,
        values = '/rekening/act/headof',
        min_length=1)

class Amount(colander.Schema):
    amt_tahun = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    missing = 0)
                    
    amt_bulan = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    missing = 0)
                
    amt_minggu = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    missing = 0)
                
    amt_hari   = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    missing = 0)
                
class AddSchema(colander.Schema):
    tahun = colander.SchemaNode(
                    colander.Integer())
            
    kode  = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=18),
                    oid='kode')
                    
    uraian = colander.SchemaNode(
                    colander.String(),
                    widget =  rek_widget,
                    validator=colander.Length(max=128),
                    oid = 'uraian')
                    
    order_id   = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    missing = 0)
                
    is_aktif   = colander.SchemaNode(
                    colander.Boolean())
    amount     = Amount()                

class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))
            
class view_carousel(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='carousel', renderer='templates/eis-carousel/list.pt',
                 permission='read')
    def view_list(self):
        return dict(a={})
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='carousel-act', renderer='json',
                 permission='read')
    def carousel_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('tahun'))
            columns.append(ColumnDT('kode'))
            columns.append(ColumnDT('uraian'))
            columns.append(ColumnDT('amt_tahun',  filter=self._number_format))
            columns.append(ColumnDT('amt_bulan',  filter=self._number_format))
            columns.append(ColumnDT('amt_minggu',  filter=self._number_format))
            columns.append(ColumnDT('amt_hari',  filter=self._number_format))
            columns.append(ColumnDT('order_id',  filter=self._number_format))
            columns.append(ColumnDT('is_aktif',  filter=self._number_format))
            
            query = DBSession.query(Eis)
            rowTable = DataTables(req, Eis, query, columns)
            return rowTable.output_result()
        
    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(Eis).filter_by(id=uid)
            row = q.first()
        else:
            row = None
                
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind()
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, user, row=None):
        if not row:
            row = Eis()
            row.created = datetime.now()
            row.create_uid = user.id
        row.from_dict(values)
        row.updated = datetime.now()
        row.update_uid = user.id
        row.is_aktif = 'is_aktif' in values and values['is_aktif'] and 1 or 0
        DBSession.add(row)
        DBSession.flush()
        return row
        
    def save_request(self, values, row=None):
        if 'id' in self.request.matchdict:
            values['id'] = self.request.matchdict['id']
        row = self.save(values, self.request.user, row)
        self.request.session.flash('Carousel sudah disimpan.')
            
    def route_list(self):
        return HTTPFound(location=self.request.route_url('carousel'))
        
    def session_failed(self, session_name):
            
        #r = dict(form=self.session[session_name])
        del self.session[session_name]
        #return r
        
    @view_config(route_name='carousel-add', renderer='templates/eis-carousel/add.pt',
                 permission='add')
    def view_carousel_add(self):
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
                    #return HTTPFound(location=req.route_url('carousel-add'))
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
        return DBSession.query(Eis).filter_by(id=self.request.matchdict['id'])
        
    def id_not_found(self):    
        msg = 'Carousel ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()

    @view_config(route_name='carousel-edit', renderer='templates/eis-carousel/add.pt',
                 permission='edit')
    def view_carousel_edit(self):
        request = self.request
        row = self.query_id().first()
        if not row:
            return id_not_found(request)
        #values = row.to_dict()
        rowd={}
        rowd['id']          = row.id
        rowd['tahun']       = row.tahun
        rowd['kode']        = row.kode
        rowd['uraian']        = row.uraian
        rowd['order_id']    = row.order_id
        rowd['is_aktif']    = row.is_aktif
        rowd['amount']        = {}
        rowd['amount']['amt_tahun']  = row.amt_tahun
        rowd['amount']['amt_bulan']  = row.amt_bulan
        rowd['amount']['amt_minggu'] = row.amt_minggu
        rowd['amount']['amt_hari']   = row.amt_hari
        
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
                    #return HTTPFound(location=request.route_url('carousel-edit',
                    #                  id=row.id))
                self.save_request(dict(controls), row)
            return self.route_list()
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)
        return dict(form=form)

    ##########
    # Delete #
    ##########    
    @view_config(route_name='carousel-delete', renderer='templates/eis-carousel/delete.pt',
                 permission='delete')
    def view_carousel_delete(self):
        request = self.request
        q = self.query_id()
        row = q.first()
        
        if not row:
            return self.id_not_found(request)
        form = Form(colander.Schema(), buttons=('hapus','batal'))
        if request.POST:
            if 'hapus' in request.POST:
                msg = 'Carousel ID %d %s sudah dihapus.' % (row.id, row.uraian)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'Carousel ID %d %s tidak dapat dihapus.' % (row.id, row.uraian)
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row,
                     form=form.render())

