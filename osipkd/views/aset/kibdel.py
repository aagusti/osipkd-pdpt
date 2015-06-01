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
from osipkd.models.aset_models import AsetRuang, AsetDel, AsetDelItem
from osipkd.models.pemda_model import Unit
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews
    

SESS_ADD_FAILED = 'Tambah aset-kibdel gagal'
SESS_EDIT_FAILED = 'Edit aset-kibdel gagal'

def deferred_kondisi(node, kw):
    values = kw.get('alasan', [])
    return widget.SelectWidget(values=values)
    
alasan = (
    ('Dihapuskan', 'Dihapuskan'),
    ('Dihibahkan', 'Dihibahkan'),
    ('Mutasi', 'Mutasi'),
    ('Barang habis pakai', 'Barang habis pakai'),
    ('Belum diketahui', 'Belum diketahui'),
    ('Double', 'Double'),
    ('Reklas', 'Reklas'),
    ('Lainnya', 'Lainnya'),
    )
    
class AddSchema(colander.Schema):
    unit_id         = colander.SchemaNode(
                          colander.String(),
                          oid = "unit_id")
    kode            = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="Kode")
    uraian          = colander.SchemaNode(
                          colander.String(),
                          title = "Uraian")
    tanggal         = colander.SchemaNode(
                          colander.Date(),
                          title = "Tanggal")
    alasan          = colander.SchemaNode(
                          colander.String(),
                          widget=widget.SelectWidget(values=alasan),
                          title = "Alasan")

class EditSchema(AddSchema):
    id             = colander.SchemaNode(
                          colander.Integer(),
                          oid="id")
                     
class view_aset_kibdel(BaseViews):

    @view_config(route_name="aset-kibdel", renderer="templates/kibdel/list.pt")
    def view_list(self):
        ses = self.request.session
        req = self.request
        params   = req.params
        url_dict = req.matchdict
        return dict(project='EIS',
        )
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='aset-kibdel-act', renderer='json',
                 permission='read')
    def view_act(self):
        ses = self.request.session
        req = self.request
        params   = req.params
        url_dict = req.matchdict
        
        pk_id = 'id' in params and params['id'] and int(params['id']) or 0
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('kode'))
            columns.append(ColumnDT('tanggal', filter=self._DTstrftime))
            columns.append(ColumnDT('uraian'))
            columns.append(ColumnDT('alasan'))
            
            query = DBSession.query(AsetDel.id,
                                    AsetDel.kode,
                                    AsetDel.tanggal,
                                    AsetDel.uraian,
                                    AsetDel.alasan,
                    ).filter(AsetDel.unit_id==ses['unit_id']
                    )
                       
            rowTable = DataTables(req, AsetDel, query, columns)
            return rowTable.output_result()
                     
    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        def err_kegiatan():
            raise colander.Invalid(form,
                'Penghapusan dengan no urut tersebut sudah ada')
                    
    def get_form(self, class_form):
        schema = class_form(validator=self.form_validator)
        schema.request = self.request
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, row=None):
        if not row:
            row = AsetDel()
            row.created    = datetime.now()
            row.create_uid = self.request.user.id
        row.from_dict(values)
        row.updated    = datetime.now()
        row.update_uid = self.request.user.id
        row.disabled   = 'disabled' in values and 1 or 0     

        if not row.kode:
            tahun    = self.session['tahun']
            unit_kd  = self.session['unit_kd']
            no_urut  = AsetDel.get_norut(row.id)+1
            no       = "0000%d" % no_urut
            nomor    = no[-5:]
            row.kode = "KIBDel%s" % tahun + "-%s" % unit_kd + "-%s" % nomor
            
        DBSession.add(row)
        DBSession.flush()
        return row
                                          
    def save_request(self, values, row=None):
        if 'id' in self.request.matchdict:
            values['id'] = self.request.matchdict['id']
        row = self.save(values, row)
        self.request.session.flash('Penghapusan sudah disimpan.')
        return row
            
    def route_list(self):
        return HTTPFound(location=self.request.route_url('aset-kibdel'))
        
    def session_failed(request, session_name):
        r = dict(form=request.session[session_name])
        del request.session[session_name]
        return r
        
    @view_config(route_name='aset-kibdel-add', renderer='templates/kibdel/add.pt',
                 permission='add')
    def view_add(self):
        request = self.request
        
        form = self.get_form(AddSchema)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                controls_dicted = dict(controls)
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form)
                row = self.save_request(controls_dicted)
            return HTTPFound(location=request.route_url('aset-kibdel-edit',id=row.id))
            return self.route_list()
        elif SESS_ADD_FAILED in request.session:
            del request.session[SESS_ADD_FAILED]
        return dict(form=form)

    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(AsetDel).filter(AsetDel.id==self.request.matchdict['id'])
        
    def id_not_found(request):    
        msg = 'User ID %s not found.' % request.matchdict['id']
        request.session.flash(msg, 'error')
        return self.route_list()

    @view_config(route_name='aset-kibdel-edit', renderer='templates/kibdel/add.pt',
                 permission='edit')
    def view_edit(self):
        request = self.request
        row     = self.query_id().first()
        
        if not row:
            return id_not_found(request)
            
        form = self.get_form(EditSchema)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form)
                self.save_request(dict(controls), row)
            return self.route_list()
        elif SESS_EDIT_FAILED in request.session:
            del request.session[SESS_EDIT_FAILED]
            return dict(form=form)
        values = row.to_dict()
        form.set_appstruct(values) 
        return dict(form=form)

    ##########
    # Delete #
    ##########    
    @view_config(route_name='aset-kibdel-delete', renderer='templates/kibdel/delete.pt',
                 permission='delete')
    def view_delete(self):
        request = self.request
        q       = self.query_id()
        row     = q.first()
        
        if not row:
            return id_not_found(request)
            
        i = DBSession.query(AsetDelItem).filter(AsetDelItem.delete_id==row.id).first()    
        if i:
            request.session.flash('Hapus dulu KIB didalam daftar item', 'error')
            return self.route_list()
        form = Form(colander.Schema(), buttons=('hapus','cancel'))
        values= {}
        if request.POST:
            if 'hapus' in request.POST:
                msg = '%s dengan kode %s telah berhasil.' % (request.title, row.kode)
                DBSession.query(AsetDel).filter(AsetDel.id==request.matchdict['id']).delete()
                DBSession.flush()
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row,form=form.render())

