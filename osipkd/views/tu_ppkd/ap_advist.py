import os
import uuid
from osipkd.tools import row2dict, xls_reader
from datetime import datetime,date
from sqlalchemy import not_, func
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from osipkd.models import DBSession
from osipkd.models.apbd_anggaran import Kegiatan, KegiatanSub, KegiatanItem
from osipkd.models.pemda_model import Unit
from osipkd.models.apbd_tu import Sp2d, Advist
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah ap-advist gagal'
SESS_EDIT_FAILED = 'Edit ap-advist gagal'

class view_ap_advist_ppkd(BaseViews):

    @view_config(route_name="ap-advist", renderer="templates/ap-advist/list.pt")
    def view_list(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        return dict(project='EIS',
        )
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='ap-advist-act', renderer='json',
                 permission='read')
    def view_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        if url_dict['act']=='grid':
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if url_dict['act']=='grid':
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('tanggal', filter=self._DTstrftime))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nominal'))
                query = DBSession.query(Advist
                        ).filter(Advist.tahun_id==ses['tahun'],
                                 Advist.unit_id==ses['unit_id'] ,
                        ).order_by(Advist.kode.asc())
                           
                rowTable = DataTables(req, Advist, query, columns)
                return rowTable.output_result()
                     
    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        def err_kegiatan():
            raise colander.Invalid(form,
                'Kegiatan dengan no urut tersebut sudah ada')
                    
    def get_form(self, class_form):
        schema = class_form(validator=self.form_validator)
        schema.request = self.request
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, row=None):
        if not row:
            row = Advist()
            row.created = datetime.now()
            row.create_uid = self.request.user.id
        row.from_dict(values)
        row.updated = datetime.now()
        row.update_uid = self.request.user.id
        row.posted=0
        row.disabled = 'disabled' in values and 1 or 0     

        if not row.kode:
            tahun    = self.session['tahun']
            unit_kd  = self.session['unit_kd']
            unit_id  = self.session['unit_id']
            no_urut  = Advist.get_norut(tahun, unit_id)+1
            no       = "0000%d" % no_urut
            nomor    = no[-5:]
            row.kode = "%d" % tahun + "-%s" % unit_kd + "-BUD-%s" % nomor
            
        DBSession.add(row)
        DBSession.flush()
        return row
                                          
    def save_request(self, values, row=None):
        if 'id' in self.request.matchdict:
            values['id'] = self.request.matchdict['id']
        values["nominal"]=values["nominal"].replace('.','')
        row = self.save(values, row)
        self.request.session.flash('Advist sudah disimpan.')
        return row
            
    def route_list(self):
        return HTTPFound(location=self.request.route_url('ap-advist'))
        
    def session_failed(request, session_name):
        r = dict(form=request.session[session_name])
        del request.session[session_name]
        return r
        
    @view_config(route_name='ap-advist-add', renderer='templates/ap-advist/add.pt',
                 permission='add')
    def view_add(self):
        request=self.request
        form = self.get_form(AddSchema)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                controls_dicted = dict(controls)

                #Cek Kode Sama ato tidak
                if not controls_dicted['kode']=='':
                    a = form.validate(controls)
                    b = a['kode']
                    c = "%s" % b
                    cek  = DBSession.query(Advist).filter(Advist.kode==c).first()
                    if cek :
                        self.request.session.flash('Kode advist sudah ada.', 'error')
                        return HTTPFound(location=self.request.route_url('ap-advist-add'))

                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form)
                row = self.save_request(controls_dicted)
                return HTTPFound(location=request.route_url('ap-advist-edit',id=row.id))
            return self.route_list()
        elif SESS_ADD_FAILED in request.session:
            del request.session[SESS_ADD_FAILED]
        return dict(form=form)

    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(Advist).filter(Advist.id==self.request.matchdict['id'])
        
    def id_not_found(request):    
        msg = 'User ID %s not found.' % request.matchdict['id']
        request.session.flash(msg, 'error')
        return self.route_list()

    @view_config(route_name='ap-advist-edit', renderer='templates/ap-advist/add.pt',
                 permission='edit')
    def view_edit(self):
        request = self.request
        row = self.query_id().first()
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
                cek = DBSession.query(Advist).filter(Advist.kode==c).first()
                if cek:
                    kode1 = DBSession.query(Advist).filter(Advist.id==uid).first()
                    d     = kode1.kode
                    if d!=c:
                        self.request.session.flash('Kode advist sudah ada', 'error')
                        return HTTPFound(location=request.route_url('ap-advist-edit',id=row.id))

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
    @view_config(route_name='ap-advist-delete', renderer='templates/ap-advist/delete.pt',
                 permission='delete')
    def view_delete(self):
        q = self.query_id()
        row = q.first()
        request=self.request
        
        if not row:
            return id_not_found(request)
        if row.nominal:
            request.session.flash('Data tidak dapat dihapus, karena masih memiliki items', 'error')
            return self.route_list()
            
        form = Form(colander.Schema(), buttons=('hapus','cancel'))
        values= {}
        if request.POST:
            if 'hapus' in request.POST:
                msg = '%s dengan kode %s telah berhasil.' % (request.title, row.kode)
                DBSession.query(Advist).filter(Advist.id==request.matchdict['id']).delete()
                DBSession.flush()
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row, form=form.render())

class AddSchema(colander.Schema):
    unit_id          = colander.SchemaNode(
                          colander.String(),
                          oid = "unit_id")
    tahun_id         = colander.SchemaNode(
                          colander.Integer(),
                          title="Tahun",
                          oid = "tahun_id")
    kode       = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="No. Advist")
    nama            = colander.SchemaNode(
                          colander.String(),
                          title = "Bank/Tujuan"
                          )
    tanggal         = colander.SchemaNode(
                          colander.Date(),
                          title = "Tanggal"
                          )
    nominal         = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          oid="jml_total",
                          title="Nominal"
                          )

class EditSchema(AddSchema):
    id             = colander.SchemaNode(
                          colander.Integer(),
                          oid="id")
                     