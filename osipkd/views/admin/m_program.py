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
from osipkd.models.pemda_model import Urusan
from osipkd.models.apbd_anggaran import Program


from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah program gagal'
SESS_EDIT_FAILED = 'Edit program gagal'

class AddSchema(colander.Schema):
    urusan_widget = widget.AutocompleteInputWidget(
                        size=60,
                        values = '/urusan/act/headofnama',
                        min_length=1)
    urusan_nm   = colander.SchemaNode(
                    colander.String(),
                    widget=urusan_widget,
                    oid = "urusan_nm",
                    title="Urusan")
    urusan_id   = colander.SchemaNode(
                    colander.Integer(),
                    widget=widget.HiddenWidget(),
                    oid = "urusan_id")
    kode        = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=32),
                    title="Kode Program")
    nama        = colander.SchemaNode(
                    colander.String(),
                    title="Nama Program")
    disabled    = colander.SchemaNode(
                    colander.Boolean())
                    
class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))
            
class view_program(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='program', renderer='templates/program/list.pt',
                 permission='read')
    def view_list(self):
        return dict(a={})
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='program-act', renderer='json',
                 permission='view')
    def view_act(self):
        ses = self.request.session
        req = self.request
        params   = req.params
        url_dict = req.matchdict
        
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('kode'))
            columns.append(ColumnDT('nama'))
            columns.append(ColumnDT('disabled'))
            
            query = DBSession.query(Program)
            
            rowTable = DataTables(req, Program, query, columns)
            return rowTable.output_result()
            
        elif url_dict['act']=='headofnama':
            term = 'term' in params and params['term'] or '' 
            rows = DBSession.query(Program.id, Program.kode, Program.nama
                      ).filter(
                      Program.nama.ilike('%%%s%%' % term) ).all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[2]
                d['kode']        = k[1]
                d['nama']        = k[2]
                r.append(d)
            return r
            
        elif url_dict['act']=='headofkode':
            term = 'term' in params and params['term'] or '' 
            rows = DBSession.query(Program.id, Program.kode, Program.nama
                      ).filter(
                      Program.kode.ilike('%%%s%%' % term) ).all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[1]
                d['kode']        = k[1]
                d['nama']        = k[2]
                r.append(d)
            return r
            
    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(Program).filter_by(id=uid)
            program = q.first()
        else:
            program = None
            
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind()
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, user, row=None):
        if not row:
            row = Program()
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
        self.request.session.flash('Program sudah disimpan.')
        
    def route_list(self):
        return HTTPFound(location=self.request.route_url('program'))
        
    def session_failed(self, session_name):
        r = dict(form=self.session[session_name])
        del self.session[session_name]
        return r
        
    @view_config(route_name='program-add', renderer='templates/program/add.pt',
                 permission='add')
    def view_add(self):
        req = self.request
        ses = self.session
        
        form = self.get_form(AddSchema)
        if req.POST:
            if 'simpan' in req.POST:
                controls = req.POST.items()

                #Cek Kode Sama ato tidak
                a = form.validate(controls)
                b = a['kode']
                c = "%s" % b
                cek  = DBSession.query(Program).filter(Program.kode==c).first()
                if cek :
                    self.request.session.flash('Kode sudah ada.', 'error')
                    return HTTPFound(location=self.request.route_url('program-add'))
                                
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    req.session[SESS_ADD_FAILED] = e.render()               
                    return HTTPFound(location=req.route_url('program-add'))
                self.save_request(dict(controls))
            return self.route_list()
        elif SESS_ADD_FAILED in req.session:
            return self.session_failed(SESS_ADD_FAILED)
        return dict(form=form.render())
        
    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(Program).filter_by(id=self.request.matchdict['id'])
    
    def id_not_found(self):    
        msg = 'Program ID %s tidak ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()
        
    @view_config(route_name='program-edit', renderer='templates/program/edit.pt',
                 permission='edit')
    def view_edit(self):
        request = self.request
        row     = self.query_id().first()
        uid     = row.id
        kode    = row.kode
        
        if not row:
            return id_not_found(request)
            
        form = self.get_form(EditSchema)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                
                #Cek Kode Sama ato tidak
                a = form.validate(controls)
                b = a['kode']
                c = "%s" % b
                cek = DBSession.query(Program).filter(Program.kode==c).first()
                if cek:
                    kode1 = DBSession.query(Program).filter(Program.id==uid).first()
                    d     = kode1.kode
                    if d!=c:
                        self.request.session.flash('Data sudah ada', 'error')
                        return HTTPFound(location=request.route_url('program-edit',id=row.id))

                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    request.session[SESS_EDIT_FAILED] = e.render()               
                    return HTTPFound(location=request.route_url('program-edit',
                                      id=row.id))
                self.save_request(dict(controls), row)
            return self.route_list()
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)
        values = row.to_dict()
        values['urusan_nm'] = row.urusans.nama
        return dict(form=form.render(appstruct=values))
        
        
    ##########
    # Delete #
    ##########    
    @view_config(route_name='program-delete', renderer='templates/program/delete.pt',
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
                msg = 'Program ID %d %s sudah dihapus.' % (row.id, row.nama)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'Program ID %d %s tidak dapat dihapus.' % (row.id, row.nama)
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row, form=form.render())
                     
                     