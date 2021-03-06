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
from osipkd.models.apbd import Jurnal, JurnalItem, ARInvoiceItem, ARPaymentItem
from osipkd.models.apbd_tu import Sts, StsItem
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah ak-jurnal gagal'
SESS_EDIT_FAILED = 'Edit ak-jurnal gagal'

def deferred_jv_type(node, kw):
    values = kw.get('jv_type', [])
    return widget.SelectWidget(values=values)
    
JV_TYPE = (
    (1, 'Jurnal Pendapatan'),
    (2, 'Jurnal Pengeluaran'),
    (3, 'Jurnal Umum'),
    (4, 'Jurnal Koreksi'),
    (5, 'Jurnal Penutup'),
    (6, 'Jurnal LO'),
    )
    
def deferred_is_skpd(node, kw):
    values = kw.get('is_skpd', [])
    return widget.SelectWidget(values=values)
    
IS_SKPD = (
    (0, 'PPKD'),
    (1, 'SKPD'))      
    
class AddSchema(colander.Schema):
    unit_kd_widget = widget.AutocompleteInputWidget(
            values = '/unit/act/headofkode',
            min_length=1)
  
    unit_nm_widget = widget.AutocompleteInputWidget(
            values = '/unit/act/headofnama',
            min_length=1)
            
          
    tahun_id  = colander.SchemaNode(
                    colander.Integer(),
                    oid='tahun_id',
                    title="Tahun")

    unit_id  = colander.SchemaNode(
                    colander.Integer(),
                    oid='unit_id',
                    title="SKPD ID")

    unit_kd  = colander.SchemaNode(
                    colander.String(),
                    oid='unit_kd',
                    title="SKPD",
                    widget = unit_kd_widget,)

    unit_nm  = colander.SchemaNode(
                    colander.String(),
                    oid='unit_nm',
                    title="SKPD NM",
                    widget = unit_nm_widget)
    kode        = colander.SchemaNode(
                    colander.String(),
                    missing = colander.drop,
                    title="No. Jurnal"
                    )
                    
    nama        = colander.SchemaNode(
                    colander.String(),
                    title="Uraian"
                    )
    tanggal     = colander.SchemaNode(
                  colander.Date(),
                  )
               
    jv_type     = colander.SchemaNode(
                    colander.String(),
                    widget=widget.SelectWidget(values=JV_TYPE),
                    title="Tipe"
                    )
    source_no   = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=32),
                    title = "Referensi"
                    )
    source      = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=64),
                    )
    tgl_source  = colander.SchemaNode(
                    colander.Date(),
                    title = "Tgl. Ref"
                )
    
    notes       = colander.SchemaNode(
                    colander.String(),
                    missing = colander.drop
                    )
    is_skpd     = colander.SchemaNode(
                    colander.Integer(),
                    title="Jurnal",
                    oid = "is_skpd",
                    widget=widget.SelectWidget(values=IS_SKPD)
                  )
                    
                    
class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True),
            oid="id")
            
class view_ak_jurnal(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='ak-jurnal', renderer='templates/ak-jurnal/list.pt',
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
    @view_config(route_name='ak-jurnal-act', renderer='json',
                 permission='read')
    def ak_jurnal_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('tanggal', filter=self._DTstrftime))
            columns.append(ColumnDT('kode'))
            columns.append(ColumnDT('jv_type'))
            columns.append(ColumnDT('nama'))
            columns.append(ColumnDT('source'))
            columns.append(ColumnDT('source_no'))
            columns.append(ColumnDT('is_skpd'))
            columns.append(ColumnDT('posted'))
            
            query = DBSession.query(Jurnal.id, Jurnal.tanggal, Jurnal.kode, Jurnal.jv_type,
                      Jurnal.nama, Jurnal.source, Jurnal.source_no, Jurnal.is_skpd, Jurnal.posted).\
                    outerjoin(JurnalItem).\
                    group_by(Jurnal.id, Jurnal.tanggal, Jurnal.kode, Jurnal.jv_type,
                             Jurnal.nama, Jurnal.source, Jurnal.source_no, Jurnal.is_skpd, Jurnal.posted).\
                    filter(Jurnal.tahun_id == ses['tahun'],
                           Jurnal.unit_id == ses['unit_id'],)
                      
            rowTable = DataTables(req, Jurnal, query, columns)
            return rowTable.output_result()
        
    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(Jurnal).filter_by(id=uid)
            row = q.first()
        else:
            row = None
                
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind(jv_type=JV_TYPE, is_skpd=IS_SKPD)
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, user, row=None):
        if not row:
            row = Jurnal()
            row.created    = datetime.now()
            row.create_uid = user.id
        row.from_dict(values)
        tanggal           = datetime.strptime(values['tanggal'], '%Y-%m-%d')
        row.tahun_id      = tanggal.year
        row.periode       = tanggal.month
        row.updated       = datetime.now()
        row.update_uid    = user.id
        row.disabled      = 'disabled' in values and values['disabled'] and 1 or 0
        row.posted        = 'posted'  in values and values['posted']  and 1 or 0
        row.tgl_transaksi = datetime.now()
        
        if not row.kode:
            tahun    = self.session['tahun']
            unit_kd  = self.session['unit_kd']
            is_skpd  = row.is_skpd
            jv_type  = row.jv_type
            tipe     = Jurnal.get_tipe(jv_type)
            no_urut  = Jurnal.get_norut(row.tahun_id,row.unit_id)+1
            no       = "0000%d" % no_urut
            nomor    = no[-5:]     
            row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
        
        DBSession.add(row)
        DBSession.flush()
        return row
        
    def save_request(self, values, row=None):
        if 'id' in self.request.matchdict:
            values['id'] = self.request.matchdict['id']
        row = self.save(values, self.request.user, row)
        self.request.session.flash('Jurnal sudah disimpan.')
        return row
            
    def route_list(self):
        return HTTPFound(location=self.request.route_url('ak-jurnal'))
        
    def session_failed(self, session_name):
        del self.session[session_name]
        
    @view_config(route_name='ak-jurnal-add', renderer='templates/ak-jurnal/add.pt',
                 permission='add')
    def view_ak_jurnal_add(self):
        req = self.request
        ses = self.session
        form = self.get_form(AddSchema)
        if req.POST:
            if 'simpan' in req.POST:
                controls = req.POST.items()
                controls_dicted = dict(controls)
                
                #Cek Kode Sama ato tidak
                if not controls_dicted['kode']=='':
                    a = form.validate(controls)
                    b = a['kode']
                    c = "%s" % b
                    cek  = DBSession.query(Jurnal).filter(Jurnal.kode==c).first()
                    if cek :
                        self.request.session.flash('Kode Jurnal sudah ada.', 'error')
                        return HTTPFound(location=self.request.route_url('ak-jurnal-add'))

                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form)
                row = self.save_request(controls_dicted)
                return HTTPFound(location=req.route_url('ak-jurnal-edit',id=row.id))
            return self.route_list()  
        elif SESS_ADD_FAILED in req.session:
            return dict(form=form)
        return dict(form=form)

        
    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(Jurnal).filter_by(id=self.request.matchdict['id'])
        
    def id_not_found(self):    
        msg = 'Jurnal ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()

    @view_config(route_name='ak-jurnal-edit', renderer='templates/ak-jurnal/add.pt',
                 permission='edit')
    def view_ak_jurnal_edit(self):
        request = self.request
        row = self.query_id().first()
        uid     = row.id
        kode    = row.kode
        
        if not row:
            return id_not_found(request)
        if row.posted:
            request.session.flash('Data sudah diposting', 'error')
            return self.route_list()

        rowd={}
        rowd['id']            = row.id
        rowd['unit_id']       = row.unit_id
        rowd['unit_nm']       = row.units.nama
        rowd['unit_kd']       = row.units.kode
        rowd['kode']          = row.kode
        rowd['nama']          = row.nama
        rowd['source_no']     = row.source_no
        rowd['source']        = row.source
        rowd['tgl_source']    = row.tgl_source
        rowd['tanggal']       = row.tanggal
        rowd['jv_type']       = row.jv_type
        rowd['disabled']      = row.disabled
        rowd['notes']         = row.notes
        rowd['is_skpd']       = row.is_skpd
        
        form = self.get_form(EditSchema)
        form.set_appstruct(rowd)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                print controls

                #Cek Kode Sama ato tidak
                a = form.validate(controls)
                b = a['kode']
                c = "%s" % b
                cek = DBSession.query(Jurnal).filter(Jurnal.kode==c).first()
                if cek:
                    kode1 = DBSession.query(Jurnal).filter(Jurnal.id==uid).first()
                    d     = kode1.kode
                    if d!=c:
                        self.request.session.flash('Kode Jurnal sudah ada', 'error')
                        return HTTPFound(location=request.route_url('ak-jurnal-edit',id=row.id))

                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form)
                self.save_request(dict(controls),row)
            return self.route_list()
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)
        return dict(form=form)
    
    ##########
    # Delete #
    ##########    
    def save_request5(self, row=None):
        row = ARInvoiceItem()
        return row
    def save_request6(self, row=None):
        row = Sts()
        return row
    def save_request7(self, row=None):
        row = ARPaymentItem()
        return row
        
    @view_config(route_name='ak-jurnal-delete', renderer='templates/ak-jurnal/delete.pt',
                 permission='delete')
    def view_ak_jurnal_delete(self):
        request = self.request
        q       = self.query_id()
        row     = q.first()
        kode    = row.source_no
        
        if not row:
            return self.id_not_found(request)
        
        i = DBSession.query(JurnalItem).filter(JurnalItem.jurnal_id==row.id).first()         
        if i:
            request.session.flash('Hapus data item dahulu', 'error')
            return self.route_list()
            
        form = Form(colander.Schema(), buttons=('hapus','batal'))
        if request.POST:
            if 'hapus' in request.POST:
                #Untuk hapus jurnal 
                msg = '%s dengan kode %s telah berhasil.' % (request.title, row.kode)
                q.delete()
                DBSession.flush()
                request.session.flash(msg) 
                
                #Untuk update status disabled dan posted PIUTANG
                row = DBSession.query(ARInvoiceItem).filter(ARInvoiceItem.ref_kode==kode).first()
                if not row:  
                    #Untuk update status disabled dan posted STS
                    row = DBSession.query(Sts).filter(Sts.kode==kode).first()
                    if not row:
                        #Untuk update status disabled dan posted Tagihan
                        row = DBSession.query(ARPaymentItem).filter(ARPaymentItem.ref_kode==kode).first()
                        if not row:
                            return self.route_list()
                        row.disabled=0
                        row.posted=0
                        self.save_request7(row)
                    row.disabled=0
                    row.posted=0
                    self.save_request6(row)
                row.disabled=0
                row.posted=0
                self.save_request5(row)
                
            return self.route_list()
        return dict(row=row, form=form.render())

