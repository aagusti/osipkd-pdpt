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
    

SESS_ADD_FAILED = 'Tambah kibf gagal'
SESS_EDIT_FAILED = 'Edit kibf gagal'
KAT_PREFIX = '06'

kat_widget = widget.AutocompleteInputWidget(
        size=60,
        values = '/aset/kibf/headofnama/act',
        min_length=1)
                
class AddSchema(KibSchema):
    kib             = colander.SchemaNode(
                          colander.String(),
                          default='F',
                          title="KIB",
                          oid="kib")
    f_bertingkat_tidak = colander.SchemaNode(
                          colander.Boolean(),
                          title="Bertingkat")
    f_beton_tidak      = colander.SchemaNode(
                          colander.Boolean(),
                          title="Beton")
    f_panjang          = colander.SchemaNode(
                          colander.Integer(),
                          title="Panjang")
    f_lebar            = colander.SchemaNode(
                          colander.Integer(),
                          title="Lebar")
    f_luas_lantai      = colander.SchemaNode(
                          colander.Integer(),
                          title="L. Lantai")
    f_lokasi           = colander.SchemaNode(
                          colander.String(),
                          title="Lokasi")
    f_dokumen_tanggal  = colander.SchemaNode(
                          colander.Date(),
                          title="Tgl. Dok")
    f_dokumen_nomor    = colander.SchemaNode(
                          colander.String(),
                          title="No. Dok")
    f_status_tanah     = colander.SchemaNode(
                          colander.String(),
                          title="Sts. Tanah")
    f_kode_tanah       = colander.SchemaNode(
                          colander.String(),
                          title="Kd. Tanah")                      
    f_luas_bangunan    = colander.SchemaNode(
                          colander.Integer(),
                          title="Luas Bng")
            
class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))
            
class view_aset_kibf(BaseViews):
    # MASTER
    @view_config(route_name="aset-kibf", renderer="templates/kibs/list.pt",
                 permission="read")
    def aset_kibf(self):
        params = self.request.params
        return dict(kib='kibf')
        
    @view_config(route_name="aset-kibf-act", renderer="json",
                 permission="read")
    def aset_kibf_act(self):
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
                           AsetKib.kib=='F')
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
        return HTTPFound(location=self.request.route_url('aset-kibf'))
        
    def session_failed(self, session_name):
        r = dict(form=self.session[session_name])
        del self.session[session_name]
        return r
        
    @view_config(route_name='aset-kibf-add', renderer='templates/kibs/add_kibf.pt',
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

    @view_config(route_name='aset-kibf-edit', renderer='templates/kibs/add_kibf.pt',
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

        rowd['kib']                  = row.kib
        rowd['f_bertingkat_tidak']   = row.f_bertingkat_tidak
        rowd['f_beton_tidak']        = row.f_beton_tidak
        rowd['f_panjang']            = row.f_panjang
        rowd['f_lebar']              = row.f_lebar
        rowd['f_luas_lantai']        = row.f_luas_lantai
        rowd['f_lokasi']             = row.f_lokasi
        rowd['f_dokumen_tanggal']    = row.f_dokumen_tanggal
        rowd['f_dokumen_nomor']      = row.f_dokumen_nomor
        rowd['f_status_tanah']       = row.f_status_tanah
        rowd['f_kode_tanah']         = row.f_kode_tanah
        rowd['f_luas_bangunan']      = row.f_luas_bangunan

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
    @view_config(route_name='aset-kibf-delete', renderer='templates/kibs/delete.pt',
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
        return dict(row=row,form=form.render())
        