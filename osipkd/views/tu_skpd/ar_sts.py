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
from osipkd.models.apbd_anggaran import Kegiatan, KegiatanSub, KegiatanItem
from osipkd.models.pemda_model import Unit
from osipkd.models.apbd_tu import Sts, StsItem, AkJurnal, AkJurnalItem
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah ar-sts gagal'
SESS_EDIT_FAILED = 'Edit ar-sts gagal'

def deferred_jenis_id(node, kw):
    values = kw.get('jenis_id', [])
    return widget.SelectWidget(values=values)
    
JENIS_ID = (
    (1, 'Pendapatan'),
    (2, 'Kontra Pos'),
    (3, 'Lainnya'))
    
class view_ar_sts(BaseViews):

    @view_config(route_name="ar-sts", renderer="templates/ar-sts/list.pt")
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
    @view_config(route_name='ar-sts-act', renderer='json',
                 permission='read')
    def view_act(self):
        ses = self.request.session
        req = self.request
        params   = req.params
        url_dict = req.matchdict

        if url_dict['act']=='grid':
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if url_dict['act']=='grid':
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('tgl_sts', filter=self._DTstrftime))
                columns.append(ColumnDT('tgl_validasi', filter=self._DTstrftime))
                columns.append(ColumnDT('jenis'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nominal'))
                columns.append(ColumnDT('posted'))
                
                query = DBSession.query(Sts).filter(
                          Sts.tahun_id == ses['tahun'],
                          Sts.unit_id == ses['unit_id']
                          )
                rowTable = DataTables(req, Sts, query, columns)
                return rowTable.output_result()
                
  
#######    
# Add #
#######
def form_validator(form, value):
    def err_kegiatan():
        raise colander.Invalid(form,
            'Kegiatan dengan no urut tersebut sudah ada')      
                
class AddSchema(colander.Schema):
    unit_kd_widget = widget.AutocompleteInputWidget(
            values = '/unit/act/headofkode',
            min_length=1)
  
    unit_nm_widget = widget.AutocompleteInputWidget(
            values = '/unit/act/headofnama',
            min_length=1)
            

    tahun_id      = colander.SchemaNode(
                          colander.String(),
                          oid = "tahun_id",
                          title="Tahun")
    unit_id       = colander.SchemaNode(
                          colander.Integer(),
                          oid='unit_id',
                          title="SKPD")
    unit_kd       = colander.SchemaNode(
                          colander.String(),
                          oid='unit_kd',
                          title="SKPD",
                          widget = unit_kd_widget,)
    unit_nm       = colander.SchemaNode(
                          colander.String(),
                          oid='unit_nm',
                          title="SKPD",
                          widget = unit_nm_widget)

    no_urut       = colander.SchemaNode(
                          colander.Integer(),
                          missing=colander.drop,
                          )
    kode          = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title = "No. STS"
                          )
    nama          = colander.SchemaNode(
                          colander.String(),
                          title = "Uraian"
                          )
    jenis         =  colander.SchemaNode(
                          colander.String(),
                          validator=colander.Length(max=32),
                          widget=widget.SelectWidget(values=JENIS_ID)) 
                    
    nominal       = colander.SchemaNode(
                          colander.String(),
                          default = 0,
                          oid="jml_total",
                          title="Nominal"
                          )
    ttd_uid       = colander.SchemaNode(
                          colander.Integer(),
                          missing=colander.drop,
                          oid="ttd_uid"
                          )
    ttd_nip       = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          oid="ttd_nip",
                          title="Bendahara"
                          )
    ttd_nama      = colander.SchemaNode(
                          colander.String(),
                          #missing=colander.drop,
                          oid="ttd_nama",
                          title="Nama")
    ttd_jab       = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          oid="ttd_jab",
                          title="Jabatan")
    bank_nama     = colander.SchemaNode(
                          colander.String(),
                          title="Bank"
                          )
    bank_account  = colander.SchemaNode(
                          colander.String(),
                          title="Rekening"
                          )
    tgl_sts       = colander.SchemaNode(
                          colander.Date(),
                          title="Tgl.STS")
    tgl_validasi  = colander.SchemaNode(
                          colander.Date(),
                          missing=colander.drop,
                          oid="tgl_validasi",
                          title="Tgl.Validasi")
    no_validasi   = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          oid="no_validasi",
                          title = "No.validasi"
                          )

class EditSchema(AddSchema):
    id             = colander.SchemaNode(
                          colander.Integer(),
                          oid="id")

def get_form(request, class_form):
    schema = class_form(validator=form_validator)
    schema = schema.bind(jenis_id=JENIS_ID)
    schema.request = request
    return Form(schema, buttons=('simpan','batal'))
    
def save(request, values, row=None):
    if not row:
        row = Sts()
    row.created = datetime.now()
    row.from_dict(values)
    row.updated = datetime.now()
    
    if not row.no_urut:
        row.no_urut = Sts.max_no_urut(row.tahun_id,row.unit_id)+1;
    
    if not row.kode:
        tahun    = request.session['tahun']
        unit_kd  = request.session['unit_kd']
        no_urut  = row.no_urut
        no       = "0000%d" % no_urut
        nomor    = no[-5:]     
        row.kode = "%d" % tahun + "-%s" % unit_kd + "-%s" % nomor
            
    DBSession.add(row)
    DBSession.flush()
    return row
                                      
def save_request(values, request, row=None):
    if 'id' in request.matchdict:
        values['id'] = request.matchdict['id']
    values["nominal"]=values["nominal"].replace('.','')  
    row = save(request, values, row)
    request.session.flash('STS sudah disimpan.')
    return row
        
def route_list(request):
    return HTTPFound(location=request.route_url('ar-sts'))
    
def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r
    
@view_config(route_name='ar-sts-add', renderer='templates/ar-sts/add.pt',
             permission='add')
def view_add(request):
    form = get_form(request, AddSchema)
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items() 
            controls_dicted = dict(controls)

            #Cek Kode Sama ato tidak
            if not controls_dicted['kode']=='':
                a = form.validate(controls)
                b = a['kode']
                c = "%s" % b
                cek  = DBSession.query(Sts).filter(Sts.kode==c).first()
                if cek :
                    request.session.flash('Kode Sts sudah ada.', 'error')
                    return HTTPFound(location=request.route_url('ar-sts-add'))

            try:
                c = form.validate(controls)
            except ValidationFailure, e:
                return dict(form=form)
            row = save_request(controls_dicted, request)
            return HTTPFound(location=request.route_url('ar-sts-edit',id=row.id))
        return route_list(request)
    elif SESS_ADD_FAILED in request.session:
        del request.session[SESS_ADD_FAILED]
    return dict(form=form)

########
# Edit #
########
def query_id(request):
    return DBSession.query(Sts).filter(Sts.id==request.matchdict['id'])
    
def id_not_found(request):    
    msg = 'User ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

@view_config(route_name='ar-sts-edit', renderer='templates/ar-sts/add.pt',
             permission='edit')
def view_edit(request):
    row = query_id(request).first()
    uid     = row.id
    kode    = row.kode
    
    if not row:
        return id_not_found(request)
    if row.posted:
        request.session.flash('Data sudah diposting', 'error')
        return route_list(request)

    form = get_form(request, EditSchema)
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items()

            #Cek Kode Sama ato tidak
            a = form.validate(controls)
            b = a['kode']
            c = "%s" % b
            cek = DBSession.query(Sts).filter(Sts.kode==c).first()
            if cek:
                kode1 = DBSession.query(Sts).filter(Sts.id==uid).first()
                d     = kode1.kode
                if d!=c:
                    request.session.flash('Kode Sts sudah ada', 'error')
                    return HTTPFound(location=request.route_url('ar-sts-edit',id=row.id))

            try:
                c = form.validate(controls)
            except ValidationFailure, e:
                return dict(form=form)
            save_request(dict(controls), request, row)
        return route_list(request)
    elif SESS_EDIT_FAILED in request.session:
        del request.session[SESS_EDIT_FAILED]
        return dict(form=form)
    values = row.to_dict() 
    form.set_appstruct(values) 
    return dict(form=form)

##########
# Delete #
##########    
@view_config(route_name='ar-sts-delete', renderer='templates/ar-sts/delete.pt',
             permission='delete')
def view_delete(request):
    q = query_id(request)
    row = q.first()
    
    if not row:
        return id_not_found(request)
    if row.posted:
        request.session.flash('Data sudah diposting', 'error')
        return route_list(request)
    if row.nominal:
        request.session.flash('Data tidak bisa dihapus, karena memiliki data items', 'error')
        return route_list(request)
            
    form = Form(colander.Schema(), buttons=('hapus','cancel'))
    values= {}
    if request.POST:
        if 'hapus' in request.POST:
            msg = '%s dengan kode %s telah berhasil.' % (request.title, row.kode)
            DBSession.query(Sts).filter(Sts.id==request.matchdict['id']).delete()
            DBSession.flush()
            request.session.flash(msg)
        return route_list(request)
    return dict(row=row, form=form.render())
   
###########
# Posting #
###########     
def save_request2(request, row=None):
    row = Sts()
    request.session.flash('STS sudah diposting dan dibuat Jurnalnya.')
    return row
    
@view_config(route_name='ar-sts-posting', renderer='templates/ar-sts/posting.pt',
             permission='posting')
def view_edit_posting(request):
    row    = query_id(request).first()
    id_inv = row.id
    
    if not row:
        return id_not_found(request)
    if not row.nominal:
        request.session.flash('Data tidak dapat diposting, karena bernilai 0.', 'error')
        return route_list(request)
    if row.posted:
        request.session.flash('Data sudah diposting', 'error')
        return route_list(request)
        
    form = Form(colander.Schema(), buttons=('posting','cancel'))
    
    if request.POST:
        if 'posting' in request.POST: 
            #Update posted pada STS
            row.posted=1
            save_request2(request, row)
            
            #Tambah ke Jurnal SKPD
            nama    = row.nama
            kode    = row.kode
            tanggal = row.tgl_sts
            tipe    = Sts.get_tipe(row.id)
            periode = Sts.get_periode(row.id)
            
            row = AkJurnal()
            row.created    = datetime.now()
            row.create_uid = request.user.id
            row.updated    = datetime.now()
            row.update_uid = request.user.id
            row.tahun_id   = request.session['tahun']
            row.unit_id    = request.session['unit_id']
            row.nama       = "Diterima STS %s" % tipe + " %s" % nama
            row.notes      = nama
            row.periode    = periode
            row.posted     = 0
            row.disabled   = 0
            row.is_skpd    = 1
            row.jv_type    = 1
            row.source     = "STS-%s" % tipe
            row.source_no  = kode
            row.tgl_source = tanggal
            row.tanggal    = datetime.now()
            row.tgl_transaksi = datetime.now()
            
            if not row.kode:
                tahun    = request.session['tahun']
                unit_kd  = request.session['unit_kd']
                is_skpd  = row.is_skpd
                tipe     = AkJurnal.get_tipe(row.jv_type)
                no_urut  = AkJurnal.get_norut(row.id)+1
                no       = "0000%d" % no_urut
                nomor    = no[-5:]     
                row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
            
            DBSession.add(row)
            DBSession.flush()
            
            #Tambah ke Item Jurnal SKPD
            jui   = row.id
            sub   = "%d" % Sts.get_sub(id_inv)
            rek   = "%d" % Sts.get_rek(id_inv)
            mon   = "%d" % Sts.get_mon(id_inv)
            note  = "%s" % Sts.get_note(id_inv)
            
            row = AkJurnalItem()
            row.ak_jurnal_id    = "%d" % jui
            row.kegiatan_sub_id = sub
            row.rekening_id     = rek
            row.amount          = mon
            row.notes           = note
            
            DBSession.add(row)
            DBSession.flush()
            
        return route_list(request)
    return dict(row=row, form=form.render())       

#############
# UnPosting #
#############   
def save_request3(request, row=None):
    row = Sts()
    request.session.flash('STS sudah di UnPosting.')
    return row
    
@view_config(route_name='ar-sts-unposting', renderer='templates/ar-sts/unposting.pt',
             permission='unposting') 
def view_edit_unposting(request):
    row = query_id(request).first()
    
    if not row:
        return id_not_found(request)
    if not row.posted:
        request.session.flash('Data tidak dapat di Unposting, karena belum diposting.', 'error')
        return route_list(request)
    if row.disabled:
        request.session.flash('Data jurnal STS sudah diposting.', 'error')
        return route_list(request)
        
    form = Form(colander.Schema(), buttons=('unposting','cancel'))
    
    if request.POST:
        if 'unposting' in request.POST: 
        
            #Update status posted pada STS
            row.posted=0
            save_request3(request, row)
            
            r = DBSession.query(AkJurnal.id).filter(AkJurnal.source_no==row.kode).first()
            #Menghapus Item Jurnal
            DBSession.query(AkJurnalItem).filter(AkJurnalItem.ak_jurnal_id==r).delete()
            DBSession.flush()
            
            #Menghapus STS yang sudah menjadi jurnal
            DBSession.query(AkJurnal).filter(AkJurnal.source_no==row.kode).delete()
            DBSession.flush()
            
        return route_list(request)
    return dict(row=row, form=form.render()) 
    