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
from osipkd.models.pemda_model import Unit, Rekening, RekeningSap, Sap
from osipkd.models.apbd_tu import Sts, StsItem
from osipkd.models.apbd import Jurnal, JurnalItem
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah STS gagal'
SESS_EDIT_FAILED = 'Edit STS gagal'

def deferred_jenis_id(node, kw):
    values = kw.get('jenis_id', [])
    return widget.SelectWidget(values=values)
    
JENIS_ID = (
    (1, 'Pendapatan'),
    (2, 'Kontra Pos'),
    (3, 'Lainnya'))
               
class AddSchema(colander.Schema):
    unit_kd_widget = widget.AutocompleteInputWidget(
            values = '/unit/act/headofkode',
            min_length=1)
  
    unit_nm_widget = widget.AutocompleteInputWidget(
            values = '/unit/act/headofnama',
            min_length=1)
            

    tahun_id = colander.SchemaNode(
                          colander.String(),
                          oid = "tahun_id",
                          title="Tahun")
    unit_id  = colander.SchemaNode(
                    colander.Integer(),
                    oid='unit_id',
                    title="SKPD")
    unit_kd  = colander.SchemaNode(
                    colander.String(),
                    oid='unit_kd',
                    title="SKPD",
                    widget = unit_kd_widget,)
    unit_nm  = colander.SchemaNode(
                    colander.String(),
                    oid='unit_nm',
                    title="SKPD",
                    widget = unit_nm_widget)

    no_urut  = colander.SchemaNode(
                   colander.Integer(),
                   missing=colander.drop,
                   )
    kode     = colander.SchemaNode(
                   colander.String(),
                   missing=colander.drop,
                   title = "No. STS"
                   )
    nama     = colander.SchemaNode(
                   colander.String(),
                   title = "Uraian"
                          )
    jenis    =  colander.SchemaNode(
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
    bank_nama      = colander.SchemaNode(
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
                       title="Tgl.Validasi")
    no_validasi   = colander.SchemaNode(
                          colander.String(),
                          default = 0,
                          title = "No.validasi"
                          )

class EditSchema(AddSchema):
    id             = colander.SchemaNode(
                          colander.Integer(),
                          oid="id")

class view_ar_payment_sts(BaseViews):
    @view_config(route_name="ar-payment-sts", renderer="templates/ar-sts/list.pt")
    def view_list(self):
        ses = self.request.session
        req = self.request
        params   = req.params
        url_dict = req.matchdict
        return dict(project='EIS', #row = row
        )
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='ar-payment-sts-act', renderer='json',
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
                
    def get_form(self, class_form):
        schema = class_form(validator=form_validator)
        schema = schema.bind(jenis_id=JENIS_ID)
        schema.request = self.request
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, row=None):
        if not row:
            row = Sts()
        row.created = datetime.now()
        row.from_dict(values)
        row.updated = datetime.now()
        
        if not row.no_urut:
            row.no_urut = Sts.max_no_urut(row.tahun_id,row.unit_id)+1;
        
        if not row.kode:
            tahun    = self.session['tahun']
            unit_kd  = self.session['unit_kd']
            no_urut  = row.no_urut
            no       = "0000%d" % no_urut
            nomor    = no[-5:]     
            row.kode = "%d" % tahun + "-%s" % unit_kd + "-%s" % nomor
            
        DBSession.add(row)
        DBSession.flush()
        return row
                                          
    def save_request(self, values, row=None):
        request = self.request
        if 'id' in request.matchdict:
            values['id'] = self.request.matchdict['id']
        values["nominal"]=values["nominal"].replace('.','')  
        row = self.save(values, row)
        request.session.flash('STS sudah disimpan.')
        return row
            
    def route_list(self):
        return HTTPFound(location=self.request.route_url('ar-payment-sts'))
        
    def session_failed(self, session_name):
        r = dict(form=self.request.session[session_name])
        del self.request.session[session_name]
        return r
        
    @view_config(route_name='ar-payment-sts-add', renderer='templates/ar-sts/add.pt',
                 permission='add')
    def view_add(self):
        request = self.request
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
                    cek  = DBSession.query(Sts).filter(Sts.kode==c).first()
                    if cek :
                        request.session.flash('Kode Sts sudah ada.', 'error')
                        return HTTPFound(location=request.route_url('ar-payment-sts-add'))

                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form)
                row = self.save_request(controls_dicted)
                return HTTPFound(location=request.route_url('ar-payment-sts-edit', 
                                          id=row.id))
            return self.route_list()
        elif SESS_ADD_FAILED in request.session:
            del request.session[SESS_ADD_FAILED]
        return dict(form=form)

    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(Sts).filter(Sts.id==self.request.matchdict['id'])
        
    def id_not_found(self):    
        msg = 'User ID %s not found.' % self.request.matchdict['id']
        self.request.session.flash(msg, 'error')
        return self.route_list()

    @view_config(route_name='ar-payment-sts-edit', renderer='templates/ar-sts/add.pt',
                 permission='edit')
    def view_edit(self):
        request = self.request
        row = self.query_id().first()
        uid     = row.id
        kode    = row.kode
        
        if not row:
            return id_not_found(request)
        if row.posted:
            request.session.flash('Data sudah diposting', 'error')
            return self.route_list()

        form = self.get_form(EditSchema)
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
                        return HTTPFound(location=request.route_url('ar-payment-sts-edit',id=row.id))

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
    @view_config(route_name='ar-payment-sts-delete', renderer='templates/ar-sts/delete.pt',
                 permission='delete')
    def view_delete(self):
        request = self.request
        q = self.query_id()
        row = q.first()
        
        if not row:
            return id_not_found(request)
        if row.posted:
            request.session.flash('Data sudah diposting', 'error')
            return self.route_list()
        if row.nominal:
            request.session.flash('Data tidak bisa dihapus, karena memiliki data items', 'error')
            return self.route_list()
      
        form = Form(colander.Schema(), buttons=('hapus','cancel'))
        values= {}
        if request.POST:
            if 'hapus' in request.POST:
                msg = 'STS ID %d %s sudah dihapus.' % (row.id, row.nama)
                DBSession.query(Sts).filter(Sts.id==request.matchdict['id']).delete()
                DBSession.flush()
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row,form=form.render())

    ###########
    # Posting #
    ###########     
    def save_request2(self, row=None):
        row = Sts()
        self.request.session.flash('STS sudah diposting dan dibuat Jurnalnya.')
        return row
        
    @view_config(route_name='ar-payment-sts-posting', renderer='templates/ar-sts/posting.pt',
                 permission='posting')
    def view_edit_posting(self):
        request = self.request
        row    = self.query_id().first()
        id_sts = row.id
        gi     = row.jenis
        g      = '%s' % gi
        nam    = row.nama
        kod    = row.kode
        tgl    = row.tgl_sts
        
        if not row:
            return id_not_found(request)
        if not row.tgl_validasi:
            self.request.session.flash('Data tidak dapat diposting jurnal, karena belum divalidasi.', 'error')
            return self.route_list()
        if not row.nominal:
            self.request.session.flash('Data tidak dapat diposting jurnal, karena bernilai 0.', 'error')
            return self.route_list()
        if row.posted:
            self.request.session.flash('Data sudah diposting jurnal', 'error')
            return self.route_list()
            
        form = Form(colander.Schema(), buttons=('jurnal','cancel'))
        
        if request.POST:
            if 'jurnal' in request.POST: 
                #Update posted pada STS
                row.posted=1
                self.save_request2(row)
                
                if g == '1':
                    #Tambah ke Jurnal PPKD
                    nama    = nam
                    kode    = kod
                    tanggal = tgl
                    tipe    = Sts.get_tipe(row.id)
                    periode = Sts.get_periode(row.id)
                    
                    row = Jurnal()
                    row.created    = datetime.now()
                    row.create_uid = self.request.user.id
                    row.updated    = datetime.now()
                    row.update_uid = self.request.user.id
                    row.tahun_id   = self.session['tahun']
                    row.unit_id    = self.session['unit_id']
                    row.nama       = "Diterima STS %s" % tipe + " %s" % nama
                    row.notes      = nama
                    row.periode    = periode
                    row.posted     = 0
                    row.disabled   = 0
                    row.is_skpd    = 0
                    row.jv_type    = 1
                    row.source     = "STS-%s" % tipe
                    row.source_no  = kode
                    row.tgl_source = tanggal
                    row.tanggal    = datetime.now()
                    row.tgl_transaksi = datetime.now()
                    
                    if not row.kode:
                        tahun    = self.session['tahun']
                        unit_kd  = self.session['unit_kd']
                        is_skpd  = row.is_skpd
                        tipe     = Jurnal.get_tipe(row.jv_type)
                        no_urut  = Jurnal.get_norut(row.tahun_id,row.unit_id)+1
                        no       = "0000%d" % no_urut
                        nomor    = no[-5:]     
                        row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                    
                    DBSession.add(row)
                    DBSession.flush()
                    
                    #Tambah ke Item Jurnal SKPD
                    jui   = row.id
                    print 'XOXOXOX----------',jui
                    rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Sts.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).join(Rekening
                                        ).outerjoin(KegiatanItem,RekeningSap,KegiatanSub,
                                        ).filter(Sts.id==id_sts,
                                               StsItem.ar_sts_id==Sts.id,
                                               StsItem.kegiatan_item_id==KegiatanItem.id,
                                               KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                               KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                               RekeningSap.rekening_id==Rekening.id,
                                               RekeningSap.db_lra_sap_id==Sap.id
                                        ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Sts.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).first()
                        
                    ji1 = JurnalItem()
                    ji1.jurnal_id = "%d" % jui
                    ji1.kegiatan_sub_id = 0
                    ji1.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.1.01.01').first()
                    ji1.sap_id       = s
                    ji1.amount       = rows.nilai1
                    ji1.notes        = ""
                    DBSession.add(ji1)
                    DBSession.flush()
                    
                    ji2 = JurnalItem()
                    ji2.jurnal_id = "%d" % jui
                    ji2.kegiatan_sub_id = 0
                    ji2.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.8.01.01').first()
                    ji2.sap_id       = s
                    n = rows.nilai1
                    ji2.amount       = n * -1
                    ji2.notes        = ""
                    DBSession.add(ji2)
                    DBSession.flush()
                    
                    #Tambah ke Jurnal SKPD
                    nama    = nam
                    kode    = kod
                    tanggal = tgl
                    tipe    = Sts.get_tipe(id_sts)
                    periode = Sts.get_periode(id_sts)
                    
                    row = Jurnal()
                    row.created    = datetime.now()
                    row.create_uid = self.request.user.id
                    row.updated    = datetime.now()
                    row.update_uid = self.request.user.id
                    row.tahun_id   = self.session['tahun']
                    row.unit_id    = self.session['unit_id']
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
                        tahun    = self.session['tahun']
                        unit_kd  = self.session['unit_kd']
                        is_skpd  = row.is_skpd
                        tipe     = Jurnal.get_tipe(row.jv_type)
                        no_urut  = Jurnal.get_norut(row.tahun_id,row.unit_id)+1
                        no       = "0000%d" % no_urut
                        nomor    = no[-5:]     
                        row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                    
                    DBSession.add(row)
                    DBSession.flush()
                    
                    #Tambah ke Item Jurnal SKPD
                    jui   = row.id
                    rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Sts.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).join(Rekening
                                        ).outerjoin(KegiatanItem,RekeningSap,KegiatanSub,
                                        ).filter(Sts.id==id_sts,
                                               StsItem.ar_sts_id==Sts.id,
                                               StsItem.kegiatan_item_id==KegiatanItem.id,
                                               KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                               KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                               RekeningSap.rekening_id==Rekening.id,
                                               RekeningSap.db_lra_sap_id==Sap.id
                                        ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Sts.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).first()
                        
                    ji3 = JurnalItem()
                    ji3.jurnal_id = "%d" % jui
                    ji3.kegiatan_sub_id = 0
                    ji3.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='3.1.3.01.01').first()
                    ji3.sap_id       = s
                    ji3.amount       = rows.nilai1
                    ji3.notes        = ""
                    DBSession.add(ji3)
                    DBSession.flush()
                    
                    ji4 = JurnalItem()
                    ji4.jurnal_id = "%d" % jui
                    ji4.kegiatan_sub_id = 0
                    ji4.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.1.02.01').first()
                    ji4.sap_id       = s
                    n = rows.nilai1
                    ji4.amount       = n * -1
                    ji4.notes        = ""
                    DBSession.add(ji4)
                    DBSession.flush()
                
                elif g == '2':
                    re = DBSession.query(func.substr(Rekening.kode,1,1)
                                 ).filter(Sts.id==id_sts,
                                          StsItem.ar_sts_id==Sts.id,
                                          StsItem.kegiatan_item_id==KegiatanItem.id,
                                          KegiatanItem.rekening_id==Rekening.id,
                                          func.substr(Rekening.kode,1,1)=='5',
                                 ).first()
                    rek = '%s' % re
                    print 'XOI------------------------------',rek
                    if rek == '5':
                        #Tambah ke Jurnal PPKD
                        nama    = nam
                        kode    = kod
                        tanggal = tgl
                        tipe    = Sts.get_tipe(row.id)
                        periode = Sts.get_periode(row.id)
                        
                        row = Jurnal()
                        row.created    = datetime.now()
                        row.create_uid = self.request.user.id
                        row.updated    = datetime.now()
                        row.update_uid = self.request.user.id
                        row.tahun_id   = self.session['tahun']
                        row.unit_id    = self.session['unit_id']
                        row.nama       = "Diterima STS %s" % tipe + " %s" % nama
                        row.notes      = nama
                        row.periode    = periode
                        row.posted     = 0
                        row.disabled   = 0
                        row.is_skpd    = 0
                        row.jv_type    = 1
                        row.source     = "STS-%s" % tipe
                        row.source_no  = kode
                        row.tgl_source = tanggal
                        row.tanggal    = datetime.now()
                        row.tgl_transaksi = datetime.now()
                        
                        if not row.kode:
                            tahun    = self.session['tahun']
                            unit_kd  = self.session['unit_kd']
                            is_skpd  = row.is_skpd
                            tipe     = Jurnal.get_tipe(row.jv_type)
                            no_urut  = Jurnal.get_norut(row.tahun_id,row.unit_id)+1
                            no       = "0000%d" % no_urut
                            nomor    = no[-5:]     
                            row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                        
                        DBSession.add(row)
                        DBSession.flush()
                        
                        #Tambah ke Item Jurnal
                        jui   = row.id
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   Sts.nominal.label('nilai1'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).join(Rekening
                                            ).outerjoin(KegiatanItem,RekeningSap,KegiatanSub,
                                            ).filter(Sts.id==id_sts,
                                                   StsItem.ar_sts_id==Sts.id,
                                                   StsItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.db_lra_sap_id==Sap.id,
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   Sts.nominal.label('nilai1'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).first()
                            
                        ji1 = JurnalItem()
                        ji1.jurnal_id = "%d" % jui
                        ji1.kegiatan_sub_id = 0
                        ji1.rekening_id  = 0
                        s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.1.01.01').first()
                        ji1.sap_id       = s
                        ji1.amount       = rows.nilai1
                        ji1.notes        = ""
                        DBSession.add(ji1)
                        DBSession.flush()
                        
                        ji2 = JurnalItem()
                        ji2.jurnal_id = "%d" % jui
                        ji2.kegiatan_sub_id = 0
                        ji2.rekening_id  = 0
                        s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.8.01.01').first()
                        ji2.sap_id       = s
                        n = rows.nilai1
                        ji2.amount       = n * -1
                        ji2.notes        = ""
                        DBSession.add(ji2)
                        DBSession.flush()
                        
                        #Tambah ke Jurnal SKPD
                        nama    = nam
                        kode    = kod
                        tanggal = tgl
                        tipe    = Sts.get_tipe(id_sts)
                        periode = Sts.get_periode(id_sts)
                        
                        row = Jurnal()
                        row.created    = datetime.now()
                        row.create_uid = self.request.user.id
                        row.updated    = datetime.now()
                        row.update_uid = self.request.user.id
                        row.tahun_id   = self.session['tahun']
                        row.unit_id    = self.session['unit_id']
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
                            tahun    = self.session['tahun']
                            unit_kd  = self.session['unit_kd']
                            is_skpd  = row.is_skpd
                            tipe     = Jurnal.get_tipe(row.jv_type)
                            no_urut  = Jurnal.get_norut(row.tahun_id,row.unit_id)+1
                            no       = "0000%d" % no_urut
                            nomor    = no[-5:]     
                            row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                        
                        DBSession.add(row)
                        DBSession.flush()
                        
                        #Tambah ke Item Jurnal
                        jui   = row.id
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Sts.nominal.label('nilai1'),
                                                   StsItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).join(Rekening
                                            ).outerjoin(KegiatanItem,RekeningSap,KegiatanSub,
                                            ).filter(Sts.id==id_sts,
                                                   StsItem.ar_sts_id==Sts.id,
                                                   StsItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.db_lra_sap_id==Sap.id
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Sts.nominal.label('nilai1'),
                                                   StsItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).first()
                            
                        ji3 = JurnalItem()
                        ji3.jurnal_id = "%d" % jui
                        ji3.kegiatan_sub_id = 0
                        ji3.rekening_id  = 0
                        s=DBSession.query(Sap.id).filter(Sap.kode=='3.1.3.01.01').first()
                        ji3.sap_id       = s
                        ji3.amount       = rows.nilai1
                        ji3.notes        = ""
                        DBSession.add(ji3)
                        DBSession.flush()
                        
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Sts.nominal.label('nilai1'),
                                                   StsItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lo_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).join(Rekening
                                            ).outerjoin(KegiatanItem,RekeningSap,KegiatanSub,
                                            ).filter(Sts.id==id_sts,
                                                   StsItem.ar_sts_id==Sts.id,
                                                   StsItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.kr_lo_sap_id==Sap.id
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Sts.nominal.label('nilai1'),
                                                   StsItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lo_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).all()
                            
                        for row in rows:
                            ji4 = JurnalItem()
                            ji4.jurnal_id = "%d" % jui
                            ji4.kegiatan_sub_id = row.kegiatan_sub_id1
                            ji4.rekening_id  = row.rek
                            ji4.sap_id       = row.sap2
                            n = row.nilai2
                            ji4.amount       = n * -1
                            ji4.notes        = ""
                            DBSession.add(ji4)
                            DBSession.flush()
                        
                        
                        #Tambah ke Jurnal SKPD 2
                        nama    = nam
                        kode    = kod
                        tanggal = tgl
                        tipe    = Sts.get_tipe(id_sts)
                        periode = Sts.get_periode(id_sts)
                        
                        row = Jurnal()
                        row.created    = datetime.now()
                        row.create_uid = self.request.user.id
                        row.updated    = datetime.now()
                        row.update_uid = self.request.user.id
                        row.tahun_id   = self.session['tahun']
                        row.unit_id    = self.session['unit_id']
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
                            tahun    = self.session['tahun']
                            unit_kd  = self.session['unit_kd']
                            is_skpd  = row.is_skpd
                            tipe     = Jurnal.get_tipe(row.jv_type)
                            no_urut  = Jurnal.get_norut(row.tahun_id,row.unit_id)+1
                            no       = "0000%d" % no_urut
                            nomor    = no[-5:]     
                            row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                        
                        DBSession.add(row)
                        DBSession.flush()
                        
                        #Tambah ke Item Jurnal
                        jui   = row.id
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Sts.nominal.label('nilai1'),
                                                   StsItem.amount.label('nilai2'),
                                                   RekeningSap.db_lo_sap_id.label('sap1'),
                                                   RekeningSap.kr_lo_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).join(Rekening
                                            ).outerjoin(KegiatanItem,RekeningSap,KegiatanSub,
                                            ).filter(Sts.id==id_sts,
                                                   StsItem.ar_sts_id==Sts.id,
                                                   StsItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.db_lo_sap_id==Sap.id
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Sts.nominal.label('nilai1'),
                                                   StsItem.amount.label('nilai2'),
                                                   RekeningSap.db_lo_sap_id.label('sap1'),
                                                   RekeningSap.kr_lo_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).first()
                            
                        ji3 = JurnalItem()
                        ji3.jurnal_id = "%d" % jui
                        ji3.kegiatan_sub_id = 0
                        ji3.rekening_id  = 0
                        s=DBSession.query(Sap.id).filter(Sap.kode=='0.0.0.00.00').first()
                        ji3.sap_id       = s
                        ji3.amount       = rows.nilai1
                        ji3.notes        = ""
                        DBSession.add(ji3)
                        DBSession.flush()
                        
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Sts.nominal.label('nilai1'),
                                                   StsItem.amount.label('nilai2'),
                                                   RekeningSap.db_lo_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).join(Rekening
                                            ).outerjoin(KegiatanItem,RekeningSap,KegiatanSub,
                                            ).filter(Sts.id==id_sts,
                                                   StsItem.ar_sts_id==Sts.id,
                                                   StsItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.kr_lra_sap_id==Sap.id
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Sts.nominal.label('nilai1'),
                                                   StsItem.amount.label('nilai2'),
                                                   RekeningSap.db_lo_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).all()
                        
                        for row in rows:
                            ji4 = JurnalItem()
                            ji4.jurnal_id = "%d" % jui
                            ji4.kegiatan_sub_id = row.kegiatan_sub_id1
                            ji4.rekening_id  = row.rek
                            ji4.sap_id       = row.sap2
                            n = row.nilai2
                            ji4.amount       = n * -1
                            ji4.notes        = ""
                            DBSession.add(ji4)
                            DBSession.flush()
                
                    else:
                        #Tambah ke Jurnal PPKD
                        nama    = nam
                        kode    = kod
                        tanggal = tgl
                        tipe    = Sts.get_tipe(row.id)
                        periode = Sts.get_periode(row.id)
                        
                        row = Jurnal()
                        row.created    = datetime.now()
                        row.create_uid = self.request.user.id
                        row.updated    = datetime.now()
                        row.update_uid = self.request.user.id
                        row.tahun_id   = self.session['tahun']
                        row.unit_id    = self.session['unit_id']
                        row.nama       = "Diterima STS %s" % tipe + " %s" % nama
                        row.notes      = nama
                        row.periode    = periode
                        row.posted     = 0
                        row.disabled   = 0
                        row.is_skpd    = 0
                        row.jv_type    = 1
                        row.source     = "STS-%s" % tipe
                        row.source_no  = kode
                        row.tgl_source = tanggal
                        row.tanggal    = datetime.now()
                        row.tgl_transaksi = datetime.now()
                        
                        if not row.kode:
                            tahun    = self.session['tahun']
                            unit_kd  = self.session['unit_kd']
                            is_skpd  = row.is_skpd
                            tipe     = Jurnal.get_tipe(row.jv_type)
                            no_urut  = Jurnal.get_norut(row.tahun_id,row.unit_id)+1
                            no       = "0000%d" % no_urut
                            nomor    = no[-5:]     
                            row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                        
                        DBSession.add(row)
                        DBSession.flush()
                        
                        #Tambah ke Item Jurnal
                        jui   = row.id
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Sts.nominal.label('nilai1'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).join(Rekening
                                            ).outerjoin(KegiatanItem,RekeningSap,KegiatanSub,
                                            ).filter(Sts.id==id_sts,
                                                   StsItem.ar_sts_id==Sts.id,
                                                   StsItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.db_lra_sap_id==Sap.id
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Sts.nominal.label('nilai1'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).first()
                            
                        ji1 = JurnalItem()
                        ji1.jurnal_id = "%d" % jui
                        ji1.kegiatan_sub_id = 0
                        ji1.rekening_id  = 0
                        s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.1.01.01').first()
                        ji1.sap_id       = s
                        ji1.amount       = rows.nilai1
                        ji1.notes        = ""
                        DBSession.add(ji1)
                        DBSession.flush()
                        
                        ji2 = JurnalItem()
                        ji2.jurnal_id = "%d" % jui
                        ji2.kegiatan_sub_id = 0
                        ji2.rekening_id  = 0
                        s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.8.01.01').first()
                        ji2.sap_id       = s
                        n = rows.nilai1
                        ji2.amount       = n * -1
                        ji2.notes        = ""
                        DBSession.add(ji2)
                        DBSession.flush()
                        
                        #Tambah ke Jurnal SKPD
                        nama    = nam
                        kode    = kod
                        tanggal = tgl
                        tipe    = Sts.get_tipe(id_sts)
                        periode = Sts.get_periode(id_sts)
                        
                        row = Jurnal()
                        row.created    = datetime.now()
                        row.create_uid = self.request.user.id
                        row.updated    = datetime.now()
                        row.update_uid = self.request.user.id
                        row.tahun_id   = self.session['tahun']
                        row.unit_id    = self.session['unit_id']
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
                            tahun    = self.session['tahun']
                            unit_kd  = self.session['unit_kd']
                            is_skpd  = row.is_skpd
                            tipe     = Jurnal.get_tipe(row.jv_type)
                            no_urut  = Jurnal.get_norut(row.tahun_id,row.unit_id)+1
                            no       = "0000%d" % no_urut
                            nomor    = no[-5:]     
                            row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                        
                        DBSession.add(row)
                        DBSession.flush()
                        
                        #Tambah ke Item Jurnal
                        jui   = row.id
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Sts.nominal.label('nilai1'),
                                                   StsItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).join(Rekening
                                            ).outerjoin(KegiatanItem,RekeningSap,KegiatanSub,
                                            ).filter(Sts.id==id_sts,
                                                   StsItem.ar_sts_id==Sts.id,
                                                   StsItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.db_lra_sap_id==Sap.id
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Sts.nominal.label('nilai1'),
                                                   StsItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).first()
                            
                        ji3 = JurnalItem()
                        ji3.jurnal_id = "%d" % jui
                        ji3.kegiatan_sub_id = 0
                        ji3.rekening_id  = 0
                        s=DBSession.query(Sap.id).filter(Sap.kode=='0.0.0.00.00').first()
                        ji3.sap_id       = s
                        ji3.amount       = rows.nilai1
                        ji3.notes        = ""
                        DBSession.add(ji3)
                        DBSession.flush()
                        
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Sts.nominal.label('nilai1'),
                                                   StsItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).join(Rekening
                                            ).outerjoin(KegiatanItem,RekeningSap,KegiatanSub,
                                            ).filter(Sts.id==id_sts,
                                                   StsItem.ar_sts_id==Sts.id,
                                                   StsItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.db_lra_sap_id==Sap.id
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Sts.nominal.label('nilai1'),
                                                   StsItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).all()
                            
                        for row in rows:
                            ji4 = JurnalItem()
                            ji4.jurnal_id = "%d" % jui
                            ji4.kegiatan_sub_id = row.kegiatan_sub_id1
                            ji4.rekening_id  = row.rek
                            ji4.sap_id       = row.sap2
                            n = row.nilai2
                            ji4.amount       = n * -1
                            ji4.notes        = ""
                            DBSession.add(ji4)
                            DBSession.flush()
                        
                        
                        #Tambah ke Jurnal SKPD 2
                        nama    = nam
                        kode    = kod
                        tanggal = tgl
                        tipe    = Sts.get_tipe(id_sts)
                        periode = Sts.get_periode(id_sts)
                        
                        row = Jurnal()
                        row.created    = datetime.now()
                        row.create_uid = self.request.user.id
                        row.updated    = datetime.now()
                        row.update_uid = self.request.user.id
                        row.tahun_id   = self.session['tahun']
                        row.unit_id    = self.session['unit_id']
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
                            tahun    = self.session['tahun']
                            unit_kd  = self.session['unit_kd']
                            is_skpd  = row.is_skpd
                            tipe     = Jurnal.get_tipe(row.jv_type)
                            no_urut  = Jurnal.get_norut(row.tahun_id,row.unit_id)+1
                            no       = "0000%d" % no_urut
                            nomor    = no[-5:]     
                            row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                        
                        DBSession.add(row)
                        DBSession.flush()
                        
                        #Tambah ke Item Jurnal
                        jui   = row.id
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Sts.nominal.label('nilai1'),
                                                   StsItem.amount.label('nilai2'),
                                                   RekeningSap.db_lo_sap_id.label('sap1'),
                                                   RekeningSap.kr_lo_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).join(Rekening
                                            ).outerjoin(KegiatanItem,RekeningSap,KegiatanSub,
                                            ).filter(Sts.id==id_sts,
                                                   StsItem.ar_sts_id==Sts.id,
                                                   StsItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.db_lo_sap_id==Sap.id
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Sts.nominal.label('nilai1'),
                                                   StsItem.amount.label('nilai2'),
                                                   RekeningSap.db_lo_sap_id.label('sap1'),
                                                   RekeningSap.kr_lo_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).first()
                            
                        ji3 = JurnalItem()
                        ji3.jurnal_id = "%d" % jui
                        ji3.kegiatan_sub_id = 0
                        ji3.rekening_id  = 0
                        s=DBSession.query(Sap.id).filter(Sap.kode=='3.1.3.01.01').first()
                        ji3.sap_id       = s
                        ji3.amount       = rows.nilai1
                        ji3.notes        = ""
                        DBSession.add(ji3)
                        DBSession.flush()
                        
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Sts.nominal.label('nilai1'),
                                                   StsItem.amount.label('nilai2'),
                                                   RekeningSap.db_lo_sap_id.label('sap1'),
                                                   RekeningSap.kr_lo_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).join(Rekening
                                            ).outerjoin(KegiatanItem,RekeningSap,KegiatanSub,
                                            ).filter(Sts.id==id_sts,
                                                   StsItem.ar_sts_id==Sts.id,
                                                   StsItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.db_lo_sap_id==Sap.id
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Sts.nominal.label('nilai1'),
                                                   StsItem.amount.label('nilai2'),
                                                   RekeningSap.db_lo_sap_id.label('sap1'),
                                                   RekeningSap.kr_lo_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).all()
                        
                        for row in rows:
                            ji4 = JurnalItem()
                            ji4.jurnal_id = "%d" % jui
                            ji4.kegiatan_sub_id = row.kegiatan_sub_id1
                            ji4.rekening_id  = row.rek
                            ji4.sap_id       = row.sap2
                            n = row.nilai2
                            ji4.amount       = n * -1
                            ji4.notes        = ""
                            DBSession.add(ji4)
                            DBSession.flush()
                
                else:
                    #Tambah ke Jurnal PPKD
                    nama    = nam
                    kode    = kod
                    tanggal = tgl
                    tipe    = Sts.get_tipe(row.id)
                    periode = Sts.get_periode(row.id)
                    
                    row = Jurnal()
                    row.created    = datetime.now()
                    row.create_uid = self.request.user.id
                    row.updated    = datetime.now()
                    row.update_uid = self.request.user.id
                    row.tahun_id   = self.session['tahun']
                    row.unit_id    = self.session['unit_id']
                    row.nama       = "Diterima STS %s" % tipe + " %s" % nama
                    row.notes      = nama
                    row.periode    = periode
                    row.posted     = 0
                    row.disabled   = 0
                    row.is_skpd    = 0
                    row.jv_type    = 1
                    row.source     = "STS-%s" % tipe
                    row.source_no  = kode
                    row.tgl_source = tanggal
                    row.tanggal    = datetime.now()
                    row.tgl_transaksi = datetime.now()
                    
                    if not row.kode:
                        tahun    = self.session['tahun']
                        unit_kd  = self.session['unit_kd']
                        is_skpd  = row.is_skpd
                        tipe     = Jurnal.get_tipe(row.jv_type)
                        no_urut  = Jurnal.get_norut(row.tahun_id,row.unit_id)+1
                        no       = "0000%d" % no_urut
                        nomor    = no[-5:]     
                        row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                    
                    DBSession.add(row)
                    DBSession.flush()
                    
                    #Tambah ke Item Jurnal SKPD
                    jui   = row.id
                    rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Sts.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).join(Rekening
                                        ).outerjoin(KegiatanItem,RekeningSap,KegiatanSub,
                                        ).filter(Sts.id==id_sts,
                                               StsItem.ar_sts_id==Sts.id,
                                               StsItem.kegiatan_item_id==KegiatanItem.id,
                                               KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                               KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                               RekeningSap.rekening_id==Rekening.id,
                                               RekeningSap.db_lra_sap_id==Sap.id
                                        ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Sts.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).first()
                        
                    ji1 = JurnalItem()
                    ji1.jurnal_id = "%d" % jui
                    ji1.kegiatan_sub_id = 0
                    ji1.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.1.01.01').first()
                    ji1.sap_id       = s
                    ji1.amount       = rows.nilai1
                    ji1.notes        = ""
                    DBSession.add(ji1)
                    DBSession.flush()
                    
                    ji2 = JurnalItem()
                    ji2.jurnal_id = "%d" % jui
                    ji2.kegiatan_sub_id = 0
                    ji2.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.8.01.01').first()
                    ji2.sap_id       = s
                    n = rows.nilai1
                    ji2.amount       = n * -1
                    ji2.notes        = ""
                    DBSession.add(ji2)
                    DBSession.flush()
                    
                    #Tambah ke Jurnal SKPD
                    nama    = nam
                    kode    = kod
                    tanggal = tgl
                    tipe    = Sts.get_tipe(id_sts)
                    periode = Sts.get_periode(id_sts)
                    
                    row = Jurnal()
                    row.created    = datetime.now()
                    row.create_uid = self.request.user.id
                    row.updated    = datetime.now()
                    row.update_uid = self.request.user.id
                    row.tahun_id   = self.session['tahun']
                    row.unit_id    = self.session['unit_id']
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
                        tahun    = self.session['tahun']
                        unit_kd  = self.session['unit_kd']
                        is_skpd  = row.is_skpd
                        tipe     = Jurnal.get_tipe(row.jv_type)
                        no_urut  = Jurnal.get_norut(row.tahun_id,row.unit_id)+1
                        no       = "0000%d" % no_urut
                        nomor    = no[-5:]     
                        row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                    
                    DBSession.add(row)
                    DBSession.flush()
                    
                    #Tambah ke Item Jurnal SKPD
                    jui   = row.id
                    rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Sts.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).join(Rekening
                                        ).outerjoin(KegiatanItem,RekeningSap,KegiatanSub,
                                        ).filter(Sts.id==id_sts,
                                               StsItem.ar_sts_id==Sts.id,
                                               StsItem.kegiatan_item_id==KegiatanItem.id,
                                               KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                               KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                               RekeningSap.rekening_id==Rekening.id,
                                               RekeningSap.db_lra_sap_id==Sap.id
                                        ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Sts.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).first()
                        
                    ji3 = JurnalItem()
                    ji3.jurnal_id = "%d" % jui
                    ji3.kegiatan_sub_id = 0
                    ji3.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='3.1.3.01.01').first()
                    ji3.sap_id       = s
                    ji3.amount       = rows.nilai1
                    ji3.notes        = ""
                    DBSession.add(ji3)
                    DBSession.flush()
                    
                    ji4 = JurnalItem()
                    ji4.jurnal_id = "%d" % jui
                    ji4.kegiatan_sub_id = 0
                    ji4.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.1.03.01').first()
                    ji4.sap_id       = s
                    n = rows.nilai1
                    ji4.amount       = n * -1
                    ji4.notes        = ""
                    DBSession.add(ji4)
                    DBSession.flush()
                            
            return self.route_list()
        return dict(row=row, form=form.render())       

    #############
    # UnPosting #
    #############   
    def save_request3(self, row=None):
        row = Sts()
        self.request.session.flash('STS sudah di Unposting jurnal.')
        return row
        
    @view_config(route_name='ar-payment-sts-unposting', renderer='templates/ar-sts/unposting.pt',
                 permission='unposting') 
    def view_edit_unposting(self):
        request = self.request
        row     = self.query_id().first()
        
        if not row:
            return id_not_found(request)
        if not row.posted:
            self.request.session.flash('Data tidak dapat di Unposting jurnal, karena belum diposting jurnal.', 'error')
            return self.route_list()
        if row.disabled:
            self.request.session.flash('Data jurnal STS sudah diposting.', 'error')
            return self.route_list()
            
        form = Form(colander.Schema(), buttons=('un-jurnal','cancel'))
        
        if request.POST:
            if 'un-jurnal' in request.POST: 
            
                #Update status posted pada STS
                row.posted=0
                self.save_request3(row)
                
                kode = row.kode
                ji   = row.jenis
                j    = '%s' % ji
                
                if j=='1':
                    s='P'
                    x='STS-%s' % s
                if j=='2':
                    s='CP'
                    x='STS-%s' % s
                if j=='3':
                    s='L'
                    x='STS-%s' % s
                    
                r = DBSession.query(Jurnal.id.label('di')).filter(Jurnal.source_no==kode,Jurnal.source==x).all()
                for row in r:
                    #Menghapus Item Jurnal
                    DBSession.query(JurnalItem).filter(JurnalItem.jurnal_id==row.di).delete()
                    DBSession.flush()
                
                #Menghapus STS yang sudah menjadi jurnal
                DBSession.query(Jurnal).filter(Jurnal.source_no==kode, Jurnal.source==x).delete()
                DBSession.flush()
                
            return self.route_list()
        return dict(row=row, form=form.render()) 
       
#######    
# Add #
#######
def form_validator(form, value):
    def err_kegiatan():
        raise colander.Invalid(form,
            'Kegiatan dengan no urut tersebut sudah ada')      
 