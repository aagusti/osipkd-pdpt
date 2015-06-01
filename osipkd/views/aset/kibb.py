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
from kibs import KibSchema    
from osipkd.models.aset_models import AsetKategori, AsetKib
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews
    

SESS_ADD_FAILED = 'Tambah kibb gagal'
SESS_EDIT_FAILED = 'Edit kibb gagal'
KAT_PREFIX = '02'

kat_widget = widget.AutocompleteInputWidget(
        size=60,
        values = '/aset/kibb/headofnama/act',
        min_length=1)
                
class AddSchema(KibSchema):
    ruang_nm_widget  = widget.AutocompleteInputWidget(
                      size=60,
                      values = '/aset-ruang/headofnama/act',
                      min_length=1)
    kib             = colander.SchemaNode(
                          colander.String(),
                          default='B',
                          title="KIB",
                          oid="kib")
    b_kd_ruang       = colander.SchemaNode(
                          colander.Integer(),
                          oid = "b_kd_ruang")
    b_nm_ruang       = colander.SchemaNode(
                          colander.String(),
                          title="Ruang",
                          oid = "b_nm_ruang")
    b_merk           = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="Merk")
    b_type           = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="Type")
    b_cc             = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="CC")
    b_bahan          = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="Bahan")
    b_nomor_pabrik   = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="No. Pabrik")
    b_nomor_rangka   = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="No. Rangka")
    b_nomor_mesin    = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="No. Mesin")
    b_nomor_polisi   = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="No. Polisi")
    b_nomor_bpkb     = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="No. BPKB")
    b_ukuran         = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="Ukuran")
    b_warna          = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="Warna")
    b_thbuat         = colander.SchemaNode(
                          colander.Integer(),
                          #missing=colander.drop,
                          title="Th. Buat")
                    
class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))
            
class view_aset_kibb(BaseViews):
    # MASTER
    @view_config(route_name="aset-kibb", renderer="templates/kibs/list.pt",
                 permission="read")
    def aset_kibb(self):
        params = self.request.params
        return dict(kib='kibb')
        
    @view_config(route_name="aset-kibb-act", renderer="json",
                 permission="read")
    def aset_kibb_act(self):
        ses      = self.request.session
        req      = self.request
        params   = req.params
        url_dict = req.matchdict

        pk_id = 'id' in params and int(params['id']) or 0
        if url_dict['act']=='grid':
            # defining columns
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('units.kode'))
            columns.append(ColumnDT('kats.kode'))
            columns.append(ColumnDT('no_register'))
            columns.append(ColumnDT('uraian'))
            columns.append(ColumnDT('tahun'))
            columns.append(ColumnDT('th_beli'))
            columns.append(ColumnDT('harga'))
            columns.append(ColumnDT('kondisi'))
            query = DBSession.query(AsetKib).\
                    join(AsetKategori).\
                    filter(AsetKib.unit_id == ses['unit_id'], 
                           AsetKib.kategori_id==AsetKategori.id,
                           AsetKib.kib=='B')
            rowTable = DataTables(req, AsetKib, query, columns)
            return rowTable.output_result()

    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(AsetKib).filter_by(id=uid)
            kebijakan = q.first()
        else:
            kebijakan = None
                
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind()
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, user, row=None):
        if not row:
            row = AsetKib()
            row.created    = datetime.now()
            row.create_uid = user.id
        row.from_dict(values)
        row.updated    = datetime.now()
        row.update_uid = user.id
        row.disabled   = 'disabled' in values and values['disabled'] and 1 or 0
        
        a = row.tahun
        b = row.unit_id
        c = row.kategori_id
        if not row.no_register:
            row.no_register = AsetKib.get_no_register(a,b,c)+1;
                
        DBSession.add(row)
        DBSession.flush()
        return row
        
    def save_request(self, values, row=None):
        if 'id' in self.request.matchdict:
            values['id'] = self.request.matchdict['id']
        row = self.save(values, self.request.user, row)
        self.request.session.flash('KIB sudah disimpan.')
            
    def route_list(self):
        return HTTPFound(location=self.request.route_url('aset-kibb'))
        
    def session_failed(self, session_name):
        r = dict(form=self.session[session_name])
        del self.session[session_name]
        return r
        
    @view_config(route_name='aset-kibb-add', renderer='templates/kibs/add_kibb.pt',
                 permission='add')
    def view_kebijakan_add(self):
        req  = self.request
        ses  = self.session
        
        form = self.get_form(AddSchema)
        if req.POST:
            if 'simpan' in req.POST:
                controls = req.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form, kat_prefix=KAT_PREFIX)
                self.save_request(dict(controls))
            return self.route_list()
        elif SESS_ADD_FAILED in req.session:
            return self.session_failed(SESS_ADD_FAILED)
        return dict(form=form, kat_prefix=KAT_PREFIX)
        
    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(AsetKib).filter_by(id=self.request.matchdict['id'])
        
    def id_not_found(self):    
        msg = 'KIB ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()

    @view_config(route_name='aset-kibb-edit', renderer='templates/kibs/add_kibb.pt',
                 permission='edit')
    def view_kebijakan_edit(self):
        request = self.request
        row     = self.query_id().first()
        
        if not row:
            return id_not_found(request)

        rowd={}
        rowd['id']              = row.id
        rowd['unit_id']         = row.units.id
        rowd['unit_nm']         = row.units.nama
        rowd['unit_kd']         = row.units.kode
        rowd['kategori_id']     = row.kats.id
        rowd['kategori_kd']     = row.kats.kode
        rowd['kategori_nm']     = row.kats.uraian
        rowd['no_register']     = row.no_register
        rowd['pemilik_id']      = row.pemiliks.id
        rowd['pemilik_nm']      = row.pemiliks.uraian
        rowd['uraian']          = row.uraian
        rowd['tgl_perolehan']   = row.tgl_perolehan
        rowd['cara_perolehan']  = row.cara_perolehan
        rowd['th_beli']         = row.th_beli
        rowd['asal_usul']       = row.asal_usul
        rowd['harga']           = row.harga
        rowd['jumlah']          = row.jumlah
        rowd['satuan']          = row.satuan
        rowd['kondisi']         = row.kondisi
        rowd['keterangan']      = row.keterangan

        rowd['kib']             = row.kib
        rowd['b_kd_ruang']      = row.b_kd_ruang
        rowd['b_nm_ruang']      = row.ruangs.uraian 
        rowd['b_merk']          = row.b_merk
        rowd['b_type']          = row.b_type
        rowd['b_cc']            = row.b_cc
        rowd['b_bahan']         = row.b_bahan
        rowd['b_nomor_pabrik']  = row.b_nomor_pabrik
        rowd['b_nomor_rangka']  = row.b_nomor_rangka
        rowd['b_nomor_mesin']   = row.b_nomor_mesin
        rowd['b_nomor_polisi']  = row.b_nomor_polisi
        rowd['b_nomor_bpkb']    = row.b_nomor_bpkb
        rowd['b_ukuran']        = row.b_ukuran
        rowd['b_warna']         = row.b_warna
        rowd['b_thbuat']        = row.b_thbuat

        form = self.get_form(EditSchema)
        form.set_appstruct(rowd)
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
            return self.session_failed(SESS_EDIT_FAILED)
        return dict(form=form)

    ##########
    # Delete #
    ##########    
    @view_config(route_name='aset-kibb-delete', renderer='templates/kibs/delete.pt',
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
                msg = 'KIB ID %d %s sudah dihapus.' % (row.id, row.uraian)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'KIB ID %d %s tidak dapat dihapus.' % (row.id, row.uraian)
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row, form=form.render())
        