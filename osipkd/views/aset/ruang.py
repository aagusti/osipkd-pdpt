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
from osipkd.models.aset_models import AsetRuang

from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews
    

SESS_ADD_FAILED = 'Tambah ruang gagal'
SESS_EDIT_FAILED = 'Edit ruang gagal'

class AddSchema(colander.Schema):
    unit_nm_widget  = widget.AutocompleteInputWidget(
                      values = '/unit/act/headofnama',
                      min_length=1)
    ruang_widget    = widget.AutocompleteInputWidget(
                      size=60,
                      values = '/aset/ruang/act/headofnama',
                      min_length=1)
    unit_id     = colander.SchemaNode(
                    colander.Integer(),
                    widget = widget.HiddenWidget(),
                    oid = "unit_id")
    unit_nm     = colander.SchemaNode(
                    colander.String(),
                    widget = unit_nm_widget,
                    oid = "unit_nm",
                    title = "SKPD")
    ruang_id    = colander.SchemaNode(
                    colander.String(),
                    widget = widget.HiddenWidget(),
                    missing = colander.drop,
                    oid = "ruang_id")
    ruang_nm    = colander.SchemaNode(
                    colander.String(),
                    widget = ruang_widget,
                    missing = colander.drop,
                    oid = "ruang_nm",
                    title = "Ruang")
    kode        = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=18))        
    uraian      = colander.SchemaNode(
                    colander.String())
    disabled    = colander.SchemaNode(
                    colander.Boolean())
                    
class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))
            
class view_ruang(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='aset-ruang', renderer='templates/ruang/list.pt',
                 permission='read')
    def view_list(self):
        return dict(a={})
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='aset-ruang-act', renderer='json',
                 permission='read')
    def view_act(self):
        ses = self.request.session
        req = self.request
        params   = req.params
        url_dict = req.matchdict
        
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('kode'))
            columns.append(ColumnDT('uraian'))
            columns.append(ColumnDT('units.nama'))
            columns.append(ColumnDT('disabled'))
            
            query = DBSession.query(AsetRuang)
            rowTable = DataTables(req, AsetRuang, query, columns)
            return rowTable.output_result()
            
        elif url_dict['act']=='headofnama':
            term   = 'term'   in params and params['term']   or '' 
            q = DBSession.query(AsetRuang.id,AsetRuang.kode,AsetRuang.uraian).\
                    filter(#AsetRuang.unit_id == ses['unit_id'],
                           AsetRuang.uraian.ilike('%%%s%%' % term)).\
                    order_by(AsetRuang.uraian)
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[2]
                d['kode']        = k[1]
                d['uraian']      = k[2]
                r.append(d)    
            return r

    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(AsetRuang).filter_by(id=uid)
            ruang = q.first()
        else:
            ruang = None
                
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind()
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, user, row=None):
        if not row:
            row = AsetRuang()
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
        self.request.session.flash('Ruang sudah disimpan.')
            
    def route_list(self):
        return HTTPFound(location=self.request.route_url('aset-ruang'))
        
    def session_failed(self, session_name):
        r = dict(form=self.session[session_name])
        del self.session[session_name]
        return r
        
    @view_config(route_name='aset-ruang-add', renderer='templates/ruang/add.pt',
                 permission='add')
    def view_ruang_add(self):
        req  = self.request
        ses  = self.session

        form = self.get_form(AddSchema)
        if req.POST:
            if 'simpan' in req.POST:
                controls = req.POST.items()

                #Cek Kode Sama ato tidak
                a = form.validate(controls)
                b = a['kode']
                c = "%s" % b
                cek  = DBSession.query(AsetRuang).filter(AsetRuang.kode==c).first()
                if cek :
                    self.request.session.flash('Kode sudah ada.', 'error')
                    return HTTPFound(location=self.request.route_url('aset-ruang-add'))

                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    req.session[SESS_ADD_FAILED] = e.render()               
                    return HTTPFound(location=req.route_url('aset-ruang-add'))
                self.save_request(dict(controls))
            return self.route_list()
        elif SESS_ADD_FAILED in req.session:
            return self.session_failed(SESS_ADD_FAILED)
        return dict(form=form.render())
 
    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(AsetRuang).filter_by(id=self.request.matchdict['id'])
        
    def id_not_found(self):    
        msg = 'Ruang ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()

    @view_config(route_name='aset-ruang-edit', renderer='templates/ruang/edit.pt',
                 permission='edit')
    def view_ruang_edit(self):
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
                cek = DBSession.query(AsetRuang).filter(AsetRuang.kode==c).first()
                if cek:
                    kode1 = DBSession.query(AsetRuang).filter(AsetRuang.id==uid).first()
                    d     = kode1.kode
                    if d!=c:
                        self.request.session.flash('Data sudah ada', 'error')
                        return HTTPFound(location=request.route_url('aset-ruang-edit',id=row.id))
                
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    request.session[SESS_EDIT_FAILED] = e.render()               
                    return HTTPFound(location=request.route_url('aset-ruang-edit',id=row.id))
                self.save_request(dict(controls), row)
            return self.route_list()
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)
        values = row.to_dict()
        values['unit_nm'] = row.units.nama
        values['ruang_nm']= row.ruang.uraian if values['ruang_id'] else ""
        return dict(form=form.render(appstruct=values))

    ##########
    # Delete #
    ##########    
    @view_config(route_name='aset-ruang-delete', renderer='templates/ruang/delete.pt',
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
                msg = 'Ruang ID %d %s sudah dihapus.' % (row.id, row.uraian)
                q.delete()
                DBSession.flush()
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row, form=form.render())
