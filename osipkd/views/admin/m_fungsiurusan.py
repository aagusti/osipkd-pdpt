import os
import uuid
from osipkd.tools import row2dict, xls_reader
from datetime import datetime
from sqlalchemy import not_, func, or_
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
from osipkd.models.apbd_anggaran import Fungsi, Program, FungsiUrusan

from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews
    

SESS_ADD_FAILED = 'Tambah fungsi urusan gagal'
SESS_EDIT_FAILED = 'Edit fungsi urusan gagal'

class AddSchema(colander.Schema):
    fungsi_widget = widget.AutocompleteInputWidget(
                     size=60,
                     values = '/fungsi/act/headofnama',
                     min_length=1)
    urusan_widget = widget.AutocompleteInputWidget(
                     size=60,
                     values = '/urusan/act/headofnama',
                     min_length=1)
    fungsi_nm   = colander.SchemaNode(
                    colander.String(),
                    widget=fungsi_widget,
                    oid = "fungsi_nm",
                    title="Fungsi")
    fungsi_id   = colander.SchemaNode(
                    colander.Integer(),
                    widget=widget.HiddenWidget(),
                    oid = "fungsi_id")
    urusan_nm   = colander.SchemaNode(
                    colander.String(),
                    widget=urusan_widget,
                    oid = "urusan_nm",
                    title="Urusan")
    urusan_id   = colander.SchemaNode(
                    colander.Integer(),
                    widget=widget.HiddenWidget(),
                    oid = "urusan_id")
    nama        = colander.SchemaNode(
                    colander.String(),
                    title="Nama Fungsi Urusan")
                    
class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))
            
class view_fungsi_urusan(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='fungsiurusan', renderer='templates/fungsiurusan/list.pt',
                 permission='read')
    def view_list(self):
        return dict(a={})
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='fungsiurusan-act', renderer='json',
                 permission='read')
    def gaji_fungsi_urusan_act(self):
        ses = self.request.session
        req = self.request
        params   = req.params
        url_dict = req.matchdict
        
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('fnama'))
            columns.append(ColumnDT('unama'))
            columns.append(ColumnDT('nama'))
            
            query = DBSession.query(FungsiUrusan.id,
                                    Fungsi.nama.label('fnama'),
                                    Urusan.nama.label('unama'),
                                    FungsiUrusan.nama,
                            ).filter(FungsiUrusan.fungsi_id==Fungsi.id,
                                     FungsiUrusan.urusan_id==Urusan.id,
                            )
            
            rowTable = DataTables(req, FungsiUrusan, query, columns)
            return rowTable.output_result()

        elif url_dict['act']=='grid1':
            cari = 'cari' in params and params['cari'] or ''
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('fnama'))
            columns.append(ColumnDT('unama'))
            columns.append(ColumnDT('nama'))
            
            query = DBSession.query(FungsiUrusan.id,
                                    Fungsi.nama.label('fnama'),
                                    Urusan.nama.label('unama'),
                                    FungsiUrusan.nama,
                            ).filter(FungsiUrusan.fungsi_id==Fungsi.id,
                                     FungsiUrusan.urusan_id==Urusan.id,
                                     or_(Fungsi.nama.ilike('%%%s%%' % cari),
                                         Urusan.nama.ilike('%%%s%%' % cari),
                                         FungsiUrusan.nama.ilike('%%%s%%' % cari))
                            )
            
            rowTable = DataTables(req, FungsiUrusan, query, columns)
            return rowTable.output_result()
            
        elif url_dict['act']=='changeid':
            row = FungsiUrusan.get_by_id('fungsi_urusan_id' in params and params['fungsi_urusan_id'] or 0)
            if row:
                ses['fungsi_urusan_id']=row.id
                ses['fungsi_urusan_kd']=row.kode
                ses['fungsi_urusan_nm']=row.nama
                return {'success':True}

    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(FungsiUrusan).filter_by(id=uid)
            fungsiurusan = q.first()
        else:
            fungsiurusan = None
                
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind()
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, user, row=None):
        if not row:
            row = FungsiUrusan()
        row.from_dict(values)
     
        DBSession.add(row)
        DBSession.flush()
        return row
        
    def save_request(self, values, row=None):
        if 'id' in self.request.matchdict:
            values['id'] = self.request.matchdict['id']
        row = self.save(values, self.request.user, row)
        self.request.session.flash('Fungsi Urusan sudah disimpan.')
            
    def route_list(self):
        return HTTPFound(location=self.request.route_url('fungsiurusan'))
        
    def session_failed(self, session_name):
        r = dict(form=self.session[session_name])
        del self.session[session_name]
        return r
        
    @view_config(route_name='fungsiurusan-add', renderer='templates/fungsiurusan/add.pt',
                 permission='add')
    def view_fungsi_urusan_add(self):
        req = self.request
        ses = self.session
        
        form = self.get_form(AddSchema)
        if req.POST:
            if 'simpan' in req.POST:
                controls = req.POST.items()
                
                """#Cek Kode Sama ato tidak
                a = form.validate(controls)
                b = a['kode']
                c = "%s" % b
                cek  = DBSession.query(FungsiUrusan).filter(Fungsi.kode==c).first()
                if cek :
                    self.request.session.flash('Kode sudah ada.', 'error')
                    return HTTPFound(location=self.request.route_url('fungsi-add'))
                """
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    req.session[SESS_ADD_FAILED] = e.render()               
                    return HTTPFound(location=req.route_url('fungsiurusan-add'))
                self.save_request(dict(controls))
            return self.route_list()
        elif SESS_ADD_FAILED in req.session:
            return self.session_failed(SESS_ADD_FAILED)
        return dict(form=form.render())
        
    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(FungsiUrusan).filter_by(id=self.request.matchdict['id'])
        
    def id_not_found(self):    
        msg = 'Fungsi Urusan ID %s tidak ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()

    @view_config(route_name='fungsiurusan-edit', renderer='templates/fungsiurusan/edit.pt',
                 permission='edit')
    def view_fungsi_urusan_edit(self):
        request = self.request
        row     = self.query_id().first()
        #uid     = row.id
        #kode    = row.kode

        if not row:
            return id_not_found(request)
            
        form = self.get_form(EditSchema)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                print controls
                
                """#Cek Kode Sama ato tidak
                a = form.validate(controls)
                b = a['kode']
                c = "%s" % b
                cek = DBSession.query(Fungsi).filter(Fungsi.kode==c).first()
                if cek:
                    kode1 = DBSession.query(Fungsi).filter(Fungsi.id==uid).first()
                    d     = kode1.kode
                    if d!=c:
                        self.request.session.flash('Data sudah ada', 'error')
                        return HTTPFound(location=request.route_url('fungsi-edit',id=row.id))
                """
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    request.session[SESS_EDIT_FAILED] = e.render()               
                    return HTTPFound(location=request.route_url('fungsiurusan-edit',id=row.id))
                self.save_request(dict(controls), row)
            return self.route_list()
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)
        values = row.to_dict()
        values['urusan_nm'] = row.urusans.nama
        values['fungsi_nm'] = row.fungsis.nama
        return dict(form=form.render(appstruct=values))

    ##########
    # Delete #
    ##########    
    @view_config(route_name='fungsiurusan-delete', renderer='templates/fungsiurusan/delete.pt',
                 permission='delete')
    def view_fungsi_urusan_delete(self):
        request = self.request
        q       = self.query_id()
        row     = q.first()
        
        if not row:
            return self.id_not_found(request)
            
        form = Form(colander.Schema(), buttons=('hapus','batal'))
        if request.POST:
            if 'hapus' in request.POST:
                msg = 'Fungsi Urusan ID %d %s sudah dihapus.' % (row.id, row.nama)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'Fungsi Urusan ID %d %s tidak dapat dihapus.' % (row.id, row.nama)
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row, form=form.render())

