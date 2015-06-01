import os
import uuid
from osipkd.tools import row2dict, xls_reader
from datetime import datetime
from sqlalchemy import not_, func, or_
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
from osipkd.models.pemda_model import Rekening, DasarHukum


from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah dasar hukum gagal'
SESS_EDIT_FAILED = 'Edit dasar hukum gagal'

class AddSchema(colander.Schema):
    rek_widget = widget.AutocompleteInputWidget(
            size=60,
            values = '/rekening/act/headofnama',
            min_length=1)
                  
    rekening_nm = colander.SchemaNode(
                    colander.String(),
                    widget=rek_widget,
                    oid = "rekening_nm")
                    
    rekening_id = colander.SchemaNode(
                    colander.Integer(),
                    widget=widget.HiddenWidget(),
                    oid = "rekening_id")
                    
    no_urut = colander.SchemaNode(
                    colander.Integer(),
                    title="No Urut")
                    
    nama = colander.SchemaNode(
                    colander.String(),
                    title="Uraian")

class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))

class view_dasarhukum(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='dasarhukum', renderer='templates/dasarhukum/list.pt',
                 permission='read')
    def view_list(self):
        return dict(a={})
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='dasarhukum-act', renderer='json',
                 permission='view')
    def view_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('rkode'))
            columns.append(ColumnDT('rnama'))
            columns.append(ColumnDT('no_urut'))
            columns.append(ColumnDT('nama'))
            
            query = DBSession.query(DasarHukum.id,
                                    Rekening.kode.label('rkode'),
                                    Rekening.nama.label('rnama'),
                                    DasarHukum.no_urut,
                                    DasarHukum.nama,
                            ).filter(DasarHukum.rekening_id==Rekening.id,
                            )
            rowTable = DataTables(req, DasarHukum, query, columns)
            return rowTable.output_result()
            
        elif url_dict['act']=='grid1':
            cari = 'cari' in params and params['cari'] or ''
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('rkode'))
            columns.append(ColumnDT('rnama'))
            columns.append(ColumnDT('no_urut'))
            columns.append(ColumnDT('nama'))
            
            query = DBSession.query(DasarHukum.id,
                                    Rekening.kode.label('rkode'),
                                    Rekening.nama.label('rnama'),
                                    DasarHukum.no_urut,
                                    DasarHukum.nama,
                            ).filter(DasarHukum.rekening_id==Rekening.id,
                                     or_(Rekening.kode.ilike('%%%s%%' % cari),
                                     Rekening.nama.ilike('%%%s%%' % cari),
                                     DasarHukum.nama.ilike('%%%s%%' % cari))
                            )
            rowTable = DataTables(req, DasarHukum, query, columns)
            return rowTable.output_result()
            
    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(DasarHukum).filter_by(id=uid)
            dasarhukum = q.first()
        else:
            dasarhukum = None
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind()
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
    def save(self, values, user, row=None):
        if not row:
            row = DasarHukum()
            #row.created = datetime.now()
            #row.create_uid = user.id
        row.from_dict(values)
        #row.updated = datetime.now()
        #row.update_uid = user.id
        #row.disabled = 'disabled' in values and values['disabled'] and 1 or 0
        DBSession.add(row)
        DBSession.flush()
        return row
    def save_request(self, values, row=None):
        if 'id' in self.request.matchdict:
            values['id'] = self.request.matchdict['id']
        row = self.save(values, self.request.user, row)
        self.request.session.flash('Dasar Hukum sudah disimpan.')
    def route_list(self):
        return HTTPFound(location=self.request.route_url('dasarhukum'))
    def session_failed(self, session_name):
        r = dict(form=self.session[session_name])
        del self.session[session_name]
        return r
    @view_config(route_name='dasarhukum-add', renderer='templates/dasarhukum/add.pt',
                 permission='add')
    def view_add(self):
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
                    return HTTPFound(location=req.route_url('dasarhukum-add'))
                self.save_request(dict(controls))
            return self.route_list()
        elif SESS_ADD_FAILED in req.session:
            return self.session_failed(SESS_ADD_FAILED)
        return dict(form=form.render())
        
    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(DasarHukum).filter_by(id=self.request.matchdict['id'])
    def id_not_found(self):    
        msg = 'Dasar Hukum ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()
    @view_config(route_name='dasarhukum-edit', renderer='templates/dasarhukum/edit.pt',
                 permission='edit')
    def view_edit(self):
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
                    return HTTPFound(location=request.route_url('dasarhukum-edit',
                                      id=row.id))
                self.save_request(dict(controls), row)
            return self.route_list()
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)
        values = row.to_dict()
        values['rekening_nm'] = row.rekenings.nama
        
        return dict(form=form.render(appstruct=values))
    ##########
    # Delete #
    ##########    
    @view_config(route_name='dasarhukum-delete', renderer='templates/dasarhukum/delete.pt',
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
                msg = 'Dasar Hukum ID %d %s sudah dihapus.' % (row.id, row.nama)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'Dasar Hukum ID %d %s tidak dapat dihapus.' % (row.id, row.nama)
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row,
                     form=form.render())