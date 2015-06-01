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
from osipkd.models.eis import ARPaymentDetail as AR
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews
    

SESS_ADD_FAILED = 'Tambah eis-item gagal'
SESS_EDIT_FAILED = 'Edit eis-item gagal'

def deferred_sumber_id(node, kw):
    values = kw.get('sumber_id', [])
    return widget.SelectWidget(values=values)
    
SUMBER_ID = (
    (1, 'Manual'),
    (2, 'PBB'),
    (3, 'BPHTB'),
    (4, 'PADL'),
    )
    
class AddSchema(colander.Schema):
  
    kode  = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=18),
                    oid='kode')
                    
    nama = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=128),
                    oid = 'nama')
    ref_kode = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=32),
                    )
    ref_nama = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=64),
                    )
    
    tanggal = colander.SchemaNode(
                colander.Date(),
                )
                
    amount = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=32),
                    default = 0
                    )

    kecamatan_kd = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=32),
                    missing=colander.drop)
    kecamatan_nm = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=64),
                    missing=colander.drop)

    kelurahan_kd = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=32),
                    missing=colander.drop
                    )
    kelurahan_nm = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=64),
                    missing=colander.drop)
    is_kota  = colander.SchemaNode(
                    colander.Boolean(),
                    ) # deferred_source_type)
               
    disabled = colander.SchemaNode(
                    colander.Boolean(),
                    ) # deferred_source_type)
    sumber_id  =  colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=32),
                    widget=widget.SelectWidget(values=SUMBER_ID)) # deferred_source_type)
class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))
            
class view_eis_item(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='eis-item', renderer='templates/eis-item/list.pt',
                 permission='read')
    def view_list(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        return dict(project='EIS')
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='eis-item-act', renderer='json',
                 permission='read')
    def eis_item_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('kode'))
            columns.append(ColumnDT('nama'))
            columns.append(ColumnDT('ref_kode'))
            columns.append(ColumnDT('ref_nama'))
            columns.append(ColumnDT('tanggal', filter=self._DTstrftime))
            columns.append(ColumnDT('amount',  filter=self._number_format))
            
            query = DBSession.query(AR)
            rowTable = DataTables(req, AR, query, columns)
            return rowTable.output_result()
        
    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(AR).filter_by(id=uid)
            row = q.first()
        else:
            row = None
                
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind(sumber_id=SUMBER_ID)
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, user, row=None):
        if not row:
            row = AR()
            row.created = datetime.now()
            row.create_uid = user.id
        row.from_dict(values)
        row.updated = datetime.now()
        row.update_uid = user.id
        row.disable   = 'disable' in values and values['disable'] and 1 or 0
        row.is_kota   = 'is_kota' in values and values['is_kota'] and 1 or 0
        DBSession.add(row)
        DBSession.flush()
        return row
        
    def save_request(self, values, row=None):
        if 'id' in self.request.matchdict:
            values['id'] = self.request.matchdict['id']
        row = self.save(values, self.request.user, row)
        self.request.session.flash('AR sudah disimpan.')
            
    def route_list(self):
        return HTTPFound(location=self.request.route_url('eis-item') )
        
    def session_failed(self, session_name):
            
        #r = dict(form=self.session[session_name])
        del self.session[session_name]
        #return r
        
    @view_config(route_name='eis-item-add', renderer='templates/eis-item/add.pt',
                 permission='add')
    def view_eis_item_add(self):
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
                    #return HTTPFound(location=req.route_url('eis-item-add'))
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
        return DBSession.query(AR).filter_by(id=self.request.matchdict['id'])
        
    def id_not_found(self):    
        msg = 'AR ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()

    @view_config(route_name='eis-item-edit', renderer='templates/eis-item/add.pt',
                 permission='edit')
    def view_eis_item_edit(self):
        request = self.request
        row = self.query_id().first()
        if not row:
            return id_not_found(request)
        #values = row.to_dict()
        rowd={}
        rowd['id']          = row.id
        rowd['kode']        = row.kode
        rowd['nama']        = row.nama
        rowd['ref_kode']    = row.ref_kode
        rowd['ref_nama']    = row.ref_nama
        rowd['tanggal']    = row.tanggal
        rowd['amount']     = row.amount
        rowd['kecamatan_kd']    = row.kecamatan_kd
        rowd['kecamatan_nm']    = row.kecamatan_nm
        rowd['kelurahan_kd']    = row.kelurahan_kd
        rowd['kelurahan_nm']    = row.kelurahan_nm
        rowd['is_kota']         = row.is_kota
        rowd['disabled']    = row.disabled
        rowd['sumber_id']    = row.sumber_id
        
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
                    #return HTTPFound(location=request.route_url('eis-item-edit',
                    #                  id=row.id))
                self.save_request(dict(controls), row)
            return self.route_list()
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)
        return dict(form=form)

    ##########
    # Delete #
    ##########    
    @view_config(route_name='eis-item-delete', renderer='templates/eis-item/delete.pt',
                 permission='delete')
    def view_eis_item_delete(self):
        request = self.request
        q = self.query_id()
        row = q.first()
        
        if not row:
            return self.id_not_found(request)
        form = Form(colander.Schema(), buttons=('hapus','batal'))
        if request.POST:
            if 'hapus' in request.POST:
                msg = 'AR ID %d %s sudah dihapus.' % (row.id, row.nama)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'AR ID %d %s tidak dapat dihapus.' % (row.id, row.nama)
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row,
                     form=form.render())

