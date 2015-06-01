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
from osipkd.models.apbd import ARInvoiceItem as ARItem, Jurnal, JurnalItem
from osipkd.models.pemda_model import Unit, Rekening, Sap, RekeningSap
from osipkd.models.apbd_anggaran import Kegiatan, KegiatanSub, KegiatanItem
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews
    

SESS_ADD_FAILED = 'Tambah ar-invoice-item gagal'
SESS_EDIT_FAILED = 'Edit ar-invoice-item gagal'

def deferred_sumber_id(node, kw):
    values = kw.get('sumber_id', [])
    return widget.SelectWidget(values=values)
    
SUMBER_ID = (
    (1, 'Manual'),
    (2, 'PBB'),
    (3, 'BPHTB'),
    (4, 'PADL'))


@colander.deferred
def deferred_unit_kd(node, kw):
    def validate_unit_kd(node, value):
        request = kw.get('request')
        unit_kd = request.session['unit_kd']
        if value != unit_kd:
            raise ValueError('Kode Error ')
    return validate_csrf
            
class AddSchema(colander.Schema):
    unit_kd_widget = widget.AutocompleteInputWidget(
            values = '/unit/act/headofkode',
            min_length=1)
  
    unit_nm_widget = widget.AutocompleteInputWidget(
            values = '/unit/act/headofnama',
            min_length=1)
            
                    
    rekening_nm_widget = widget.AutocompleteInputWidget(
            size=60,
            values = '/rekening/act/headofnama11',
            min_length=1)
  
    rekening_kd_widget = widget.AutocompleteInputWidget(
            size=60,
            values = '/rekening/act/headofkode11',
            min_length=1)
    
    unit_id  = colander.SchemaNode(
                    colander.Integer(),
                    oid='unit_id',
                    title="SKPD")

    unit_kd  = colander.SchemaNode(
                    colander.String(),
                    oid='unit_kd',
                    title="SKPD",
                    widget = unit_kd_widget)

    unit_nm  = colander.SchemaNode(
                    colander.String(),
                    oid='unit_nm',
                    title="SKPD",
                    widget = unit_nm_widget)


    rekening_id  = colander.SchemaNode(
                    colander.Integer(),
                    oid='rekening_id')
    kode  = colander.SchemaNode(
                    colander.String(),
                    widget = rekening_kd_widget,                    
                    oid='kode',
                    title='Rekening',
                    #javascript='test'
                    )
                    
    nama = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=128),
                    widget = rekening_nm_widget,
                    oid = 'nama')
    ref_kode = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=32),
                    title = "Referensi"
                    )
    ref_nama = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=64),
                    )
    
    tanggal = colander.SchemaNode(
                colander.Date(),
                )
                
    amount = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=32),
                    default = 0,
                    title = "Nilai"
                    )

    sumber_id  =  colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=32),
                    widget=widget.SelectWidget(values=SUMBER_ID),
                    title = "Sumber") # deferred_source_type)
    ############## DI DROP DULU                
    kecamatan_kd = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=32),
                    missing=colander.drop)
    kecamatan_nm = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=64),
                    missing=colander.drop)

    kelurahan_kd = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=32),
                    missing=colander.drop
                    )
    kelurahan_nm = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=64),
                    missing=colander.drop)
    is_kota  = colander.SchemaNode(
                    colander.Boolean(),
                    missing = colander.drop
                    ) # deferred_source_type)
               
    disabled = colander.SchemaNode(
                    colander.Boolean(),
                    missing = colander.drop
                    ) # deferred_source_type)
                    
class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))
            
class view_ar_invoice_item(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='ar-invoice-item', renderer='templates/ar-invoice-item/list.pt',
                 permission='read')
    def view_list(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        row = {}
        row['kegiatan_kd']='0.00.00.10'
        row['kegiatan_nm']='PENDAPATAN'
        return dict(project='EIS', row=row)
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='ar-invoice-item-act', renderer='json',
                 permission='read')
    def ar_invoice_item_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('units.kode'))
            columns.append(ColumnDT('kode'))
            columns.append(ColumnDT('nama'))
            columns.append(ColumnDT('ref_kode'))
            columns.append(ColumnDT('ref_nama'))
            columns.append(ColumnDT('tanggal', filter=self._DTstrftime))
            columns.append(ColumnDT('amount',  filter=self._number_format))
            columns.append(ColumnDT('posted'))
            
            query = DBSession.query(ARItem).filter(ARItem.tahun==ses['tahun'],
                      ARItem.unit_id==ses['unit_id'],
                      ARItem.tanggal == ses['tanggal'])
            rowTable = DataTables(req, ARItem, query, columns)
            return rowTable.output_result()
        
    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(ARItem).filter_by(id=uid)
            row = q.first()
        else:
            row = None
                
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind(sumber_id=SUMBER_ID)
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, user, row=None):
        if not row:
            row = ARItem()
            row.created    = datetime.now()
            row.create_uid = user.id
        row.from_dict(values)
        row.updated    = datetime.now()
        row.update_uid = user.id
        tanggal    = datetime.strptime(values['tanggal'], '%Y-%m-%d') 
        row.tahun  = tanggal.year
        row.bulan  = tanggal.month
        row.hari   = tanggal.day
        row.minggu = tanggal.isocalendar()[1]
        row.disable   = 'disable' in values and values['disable'] and 1 or 0
        row.is_kota   = 'is_kota' in values and values['is_kota'] and 1 or 0

        DBSession.add(row)
        DBSession.flush()
        return row
        
    def save_request(self, values, row=None):
        if 'id' in self.request.matchdict:
            values['id'] = self.request.matchdict['id']
        row = self.save(values, self.request.user, row)
        self.request.session.flash('Penetapan / Tagihan sudah disimpan.')
            
    def route_list(self):
        return HTTPFound(location=self.request.route_url('ar-invoice-item') )
        
    def session_failed(self, session_name):
            
        #r = dict(form=self.session[session_name])
        del self.session[session_name]
        #return r
        
    @view_config(route_name='ar-invoice-item-add', renderer='templates/ar-invoice-item/add.pt',
                 permission='add')
    def view_ar_invoice_item_add(self):
        req = self.request
        ses = self.session
        
        form = self.get_form(AddSchema)
        if req.POST:
            if 'simpan' in req.POST:
                controls = req.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    #req.session[SESS_ADD_FAILED] = e.render()     
                    #form.set_appstruct(rowd)
                    return dict(form=form)
                    #return HTTPFound(location=req.route_url('ar-invoice-item-add'))
                self.save_request(dict(controls))
            return self.route_list()
        elif SESS_ADD_FAILED in req.session:
            return dict(form=form)
        rowd={}
        rowd['unit_id']     = ses['unit_id']
        rowd['unit_nm']     = ses['unit_nm']
        rowd['unit_kd']     = ses['unit_kd']
        form.set_appstruct(rowd)                  
        return dict(form=form)

        
    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(ARItem).filter_by(id=self.request.matchdict['id'])
        
    def id_not_found(self):    
        msg = 'Penetapan / Tagihan ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()

    @view_config(route_name='ar-invoice-item-edit', renderer='templates/ar-invoice-item/add.pt',
                 permission='edit')
    def view_ar_invoice_item_edit(self):
        request = self.request
        row     = self.query_id().first()
        
        if not row:
            return id_not_found(request)
        if row.posted:
            request.session.flash('Data sudah diposting', 'error')
            return self.route_list()
            
        form = self.get_form(EditSchema)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                print controls
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form)
                self.save_request(dict(controls), row)
            return self.route_list()
        #values = row.to_dict()
        rowd={}
        rowd['id']          = row.id
        rowd['unit_id']     = row.unit_id
        rowd['unit_nm']     = row.units.nama
        rowd['unit_kd']     = row.units.kode
        rowd['rekening_id'] = row.rekening_id
        rowd['kode']        = row.kode
        rowd['nama']        = row.nama
        rowd['ref_kode']    = row.ref_kode
        rowd['ref_nama']    = row.ref_nama
        rowd['tanggal']    = row.tanggal
        rowd['amount']     = row.amount
        rowd['kecamatan_kd']    = row.kecamatan_kd
        rowd['kecamatan_nm']    = row.kecamatan_nm
        rowd['kelurahan_kd']    = row.kelurahan_kd
        rowd['kelurahan_nm']    = row.kelurahan_nm
        rowd['is_kota']         = row.is_kota
        rowd['disabled']    = row.disabled
        rowd['sumber_id']    = row.sumber_id
        form.set_appstruct(rowd)                  
        return dict(form=form)

    ##########
    # Delete #
    ##########    
    @view_config(route_name='ar-invoice-item-delete', renderer='templates/ar-invoice-item/delete.pt',
                 permission='delete')
    def view_ar_invoice_item_delete(self):
        request = self.request
        q = self.query_id()
        row = q.first()
        
        if not row:
            return self.id_not_found(request)
        if row.posted:
            request.session.flash('Data sudah diposting', 'error')
            return self.route_list()
            
        form = Form(colander.Schema(), buttons=('hapus','batal'))
        if request.POST:
            if 'hapus' in request.POST:
                msg = 'Penetapan / Tagihan ID %d %s sudah dihapus.' % (row.id, row.nama)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'Penetapan / Tagihan ID %d %s tidak dapat dihapus.' % (row.id, row.nama)
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row,
                     form=form.render())

    ###########
    # Posting #
    ###########     
    def save_request2(self, row=None):
        row = ARItem()
        self.request.session.flash('Penetapan/Tagihan sudah diposting dan dibuat Jurnalnya.')
        return row
        
    @view_config(route_name='ar-invoice-item-posting', renderer='templates/ar-invoice-item/posting.pt',
                 permission='posting')
    def view_edit_posting(self):
        request = self.request
        row     = self.query_id().first()
        id_inv  = row.id
        
        if not row:
            return id_not_found(request)
        if not row.amount:
            self.request.session.flash('Data tidak dapat di jurnal, karena bernilai 0.', 'error')
            return self.route_list()
        if row.posted:
            self.request.session.flash('Data sudah dibuat jurnal', 'error')
            return self.route_list()
            
        form = Form(colander.Schema(), buttons=('jurnal','cancel'))
        
        if request.POST:
            if 'jurnal' in request.POST: 
                #Update posted pada ARInvoice
                row.posted=1
                self.save_request2(row)
                
                #Tambah ke Jurnal SKPD
                nama    = row.ref_nama
                kode    = row.ref_kode
                tanggal = row.tanggal
                #tipe    = ARInvoice.get_tipe(row.id)
                periode = ARItem.get_periode(row.id)
                
                row = Jurnal()
                row.created    = datetime.now()
                row.create_uid = self.request.user.id
                row.updated    = datetime.now()
                row.update_uid = self.request.user.id
                row.tahun_id   = self.session['tahun']
                row.unit_id    = self.session['unit_id']
                row.nama       = "Diterima Penetapan/Tagihan %s" % nama
                row.notes      = nama
                row.periode    = periode
                row.posted     = 0
                row.disabled   = 0
                row.is_skpd    = 1
                row.jv_type    = 1
                row.source     = "Penetapan"
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
                rows = DBSession.query(ARItem.rekening_id.label('rekening_id1'),
                                       Sap.nama.label('nama1'),
                                       KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                       ARItem.amount.label('nilai1'),
                                       RekeningSap.db_lo_sap_id.label('sap1'),
                                       RekeningSap.kr_lo_sap_id.label('sap2'),
                                       Rekening.id.label('rek'),
                                ).join(Rekening
                                #).outerjoin(KegiatanSub, KegiatanItem, RekeningSap 
                                ).filter(ARItem.id==id_inv,
                                         ARItem.rekening_id==KegiatanItem.rekening_id,
                                         KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                         KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                         RekeningSap.rekening_id==Rekening.id,
                                         RekeningSap.kr_lo_sap_id==Sap.id
                                ).group_by(ARItem.rekening_id.label('rekening_id1'),
                                           Sap.nama.label('nama1'),
                                           KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                           ARItem.amount.label('nilai1'),
                                           RekeningSap.db_lo_sap_id.label('sap1'),
                                           RekeningSap.kr_lo_sap_id.label('sap2'),
                                           Rekening.id.label('rek'),
                                ).all()
                
                for row in rows:
                    ji = JurnalItem()
                    
                    ji.jurnal_id = "%d" % jui
                    ji.kegiatan_sub_id = row.kegiatan_sub_id1
                    ji.rekening_id  = row.rek
                    ji.sap_id       = row.sap1
                    ji.notes        = ""
                    ji.amount       = row.nilai1
                    
                    DBSession.add(ji)
                    DBSession.flush()
                
                n=0
                for row in rows:
                    ji2 = JurnalItem()
                    
                    ji2.jurnal_id = "%d" % jui
                    ji2.kegiatan_sub_id = row.kegiatan_sub_id1
                    ji2.rekening_id  = row.rek
                    ji2.sap_id       = row.sap2
                    n = row.nilai1
                    ji2.amount       = n * -1
                    ji2.notes        = ""
                    n = n + 1
                    
                    DBSession.add(ji2)
                    DBSession.flush()
                
            return self.route_list()
        return dict(row=row, form=form.render())    

    #############
    # UnPosting #
    #############   
    def save_request3(self, row=None):
        row = ARItem()
        self.request.session.flash('Penetapan/Tagihan sudah di Un-Jurnal.')
        return row
        
    @view_config(route_name='ar-invoice-item-unposting', renderer='templates/ar-invoice-item/unposting.pt',
                 permission='unposting') 
    def view_edit_unposting(self):
        request = self.request
        row     = self.query_id().first()
        
        if not row:
            return id_not_found(request)
        if not row.posted:
            self.request.session.flash('Data tidak dapat di Un-Jurnal, karena belum dibuat jurnal.', 'error')
            return self.route_list()
        if row.disabled:
            self.request.session.flash('Data jurnal Penetapan/Tagihan sudah diposting.', 'error')
            return self.route_list()
            
        form = Form(colander.Schema(), buttons=('un-jurnal','cancel'))
        
        if request.POST:
            if 'un-jurnal' in request.POST: 
            
                #Update status posted pada PIUTANG
                row.posted=0
                self.save_request3(row)
                
                r = DBSession.query(Jurnal.id).filter(Jurnal.source_no==row.ref_kode,Jurnal.source=='Penetapan').first()
                #Menghapus Item Jurnal
                DBSession.query(JurnalItem).filter(JurnalItem.jurnal_id==r).delete()
                DBSession.flush()
                    
                #Menghapus PIUTANG yang sudah menjadi jurnal
                DBSession.query(Jurnal).filter(Jurnal.source_no==row.ref_kode,Jurnal.source=='Penetapan').delete()
                DBSession.flush()
                
            return self.route_list()
        return dict(row=row, form=form.render())
            