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
from osipkd.models.apbd import Jurnal, JurnalItem, ARPaymentItem
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews
    

SESS_ADD_FAILED = 'Tambah ar-payment-item gagal'
SESS_EDIT_FAILED = 'Edit ar-payment-item gagal'

def deferred_sumber_id(node, kw):
    values = kw.get('sumber_id', [])
    return widget.SelectWidget(values=values)
    
SUMBER_ID = (
    (1, 'Manual'),
    (2, 'PBB'),
    (3, 'BPHTB'),
    (4, 'PADL'))
    
class AddSchema(colander.Schema):
    unit_kd_widget = widget.AutocompleteInputWidget(
            values = '/unit/act/headofkode',
            min_length=1)
  
    unit_nm_widget = widget.AutocompleteInputWidget(
            values = '/unit/act/headofnama',
            min_length=1)
            
                    
    kegiatan_nm_widget = widget.AutocompleteInputWidget(
            size=60,
            values = '/ag-kegiatan-sub/act/headofnama',
            min_length=1)
  
    kegiatan_kd_widget = widget.AutocompleteInputWidget(
            size=60,
            values = '/ag-kegiatan-sub/act/headofkode',
            min_length=1)

    rekening_nm_widget = widget.AutocompleteInputWidget(
            size=60,
            values = '/rekening/act/headofnama11',
            min_length=1)
  
    rekening_kd_widget = widget.AutocompleteInputWidget(
            size=60,
            values = '/rekening/act/headofkode11',
            min_length=1,
            )
            
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

    """kegiatan_sub_id  = colander.SchemaNode(
                    colander.Integer(),
                    oid='kegiatan_sub_id',
                    title="SKPD")

    kegiatan_sub_kd  = colander.SchemaNode(
                    colander.String(),
                    oid='kegiatan_sub_kd',
                    title="Kegiatan",
                    widget = kegiatan_kd_widget,)

    kegiatan_sub_nm  = colander.SchemaNode(
                    colander.String(),
                    oid='kegiatan_sub_nm',
                    widget = kegiatan_nm_widget)
    """
    rekening_id  = colander.SchemaNode(
                    colander.Integer(),
                    oid='rekening_id')
    kode  = colander.SchemaNode(
                    colander.String(),
                    widget = rekening_kd_widget,                    
                    oid='kode',
                    title='Rekening',
                    )
                    
    nama = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=128),
                    widget = rekening_nm_widget,
                    oid = 'nama')
    ref_kode = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=32),
                    title = "No Bank"
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
                    title = "Sumber") 
                    # deferred_source_type)

    bud_uid    = colander.SchemaNode(
                          colander.Integer(),
                          oid="bud_uid",
                          missing=colander.drop,
                          title="Bendahara") 
    bud_nip    = colander.SchemaNode(
                          colander.String(),
                          oid="bud_nip",
                          missing=colander.drop,
                          title="Bendahara")                          
    bud_nama     = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          oid="bud_nama")
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
            
class view_ar_payment_item(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='ar-payment-item', renderer='templates/ar-payment-item/list.pt',
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
    @view_config(route_name='ar-payment-item-act', renderer='json',
                 permission='read')
    def ar_payment_item_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        kegiatan_sub_id = 'kegiatan_sub_id' in params and params['kegiatan_sub_id'] or 0
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            #columns.append(ColumnDT('kegiatan_subs.kegiatans.kode'))
            #columns.append(ColumnDT('kegiatan_subs.no_urut'))
            columns.append(ColumnDT('kode'))
            columns.append(ColumnDT('nama'))
            columns.append(ColumnDT('ref_kode'))
            columns.append(ColumnDT('ref_nama'))
            columns.append(ColumnDT('tanggal', filter=self._DTstrftime))
            columns.append(ColumnDT('amount',  filter=self._number_format))
            columns.append(ColumnDT('posted'))           
            query = DBSession.query(ARPaymentItem).filter(
                      ARPaymentItem.tahun == ses['tahun'],
                      ARPaymentItem.unit_id == ses['unit_id'],
                      ARPaymentItem.tanggal == ses['tanggal'],
                      
                      )
            rowTable = DataTables(req, ARPaymentItem, query, columns)
            return rowTable.output_result()
        
    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(ARPaymentItem).filter_by(id=uid)
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
            row = ARPaymentItem()
            row.created    = datetime.now()
            row.create_uid = user.id
        row.from_dict(values)
        row.updated    = datetime.now()
        row.update_uid = user.id
        tanggal     = datetime.strptime(values['tanggal'], '%Y-%m-%d')
        row.tahun   = tanggal.year
        row.bulan   = tanggal.month
        row.hari    = tanggal.day
        row.minggu  = tanggal.isocalendar()[1]
        row.disable = 'disable' in values and values['disable'] and 1 or 0
        row.is_kota = 'is_kota' in values and values['is_kota'] and 1 or 0
        
        DBSession.add(row)
        DBSession.flush()
        return row
        
    def save_request(self, values, row=None):
        if 'id' in self.request.matchdict:
            values['id'] = self.request.matchdict['id']
        row = self.save(values, self.request.user, row)
        self.request.session.flash('Realisasi / STS sudah disimpan.')
            
    def route_list(self):
        return HTTPFound(location=self.request.route_url('ar-payment-item') )
        
    def session_failed(self, session_name):
            
        #r = dict(form=self.session[session_name])
        del self.session[session_name]
        #return r
        
    @view_config(route_name='ar-payment-item-add', renderer='templates/ar-payment-item/add.pt',
                 permission='add')
    def view_ar_payment_item_add(self):
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
                    #return HTTPFound(location=req.route_url('ar-payment-item-add'))
                self.save_request(dict(controls))
            return self.route_list()
        elif SESS_ADD_FAILED in req.session:
            return dict(form=form)
        
            #return self.session_failed(SESS_ADD_FAILED)
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
        return DBSession.query(ARPaymentItem).filter_by(id=self.request.matchdict['id'])
        
    def id_not_found(self):    
        msg = 'Realisasi / STS ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()

    @view_config(route_name='ar-payment-item-edit', renderer='templates/ar-payment-item/add.pt',
                 permission='edit')
    def view_ar_payment_item_edit(self):
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
                    #request.session[SESS_EDIT_FAILED] = e.render()               
                    #return HTTPFound(location=request.route_url('ar-payment-item-edit',
                    #                  id=row.id))
                self.save_request(dict(controls), row)
            return self.route_list()
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)
        rowd = row.to_dict()
        #rowd={}
        #rowd['id']          = row.id
        #rowd['unit_id']     = row.unit_id
        rowd['unit_nm']     = row.units.nama
        rowd['unit_kd']     = row.units.kode
        #rowd['kegiatan_sub_id'] =row.kegiatan_sub_id
        #rowd['kegiatan_sub_kd'] ="".join([row.kegiatan_subs.kegiatans.kode,'-',str(row.kegiatan_subs.no_urut)])
        #rowd['kegiatan_sub_nm'] =row.kegiatan_subs.nama
        #rowd['rekening_id'] = row.rekening_id
        #rowd['kode']        = row.kode
        #rowd['nama']        = row.nama
        #rowd['ref_kode']    = row.ref_kode
        #rowd['ref_nama']    = row.ref_nama
        #rowd['tanggal']    = row.tanggal
        #rowd['amount']     = row.amount
        #rowd['kecamatan_kd']    = row.kecamatan_kd
        #rowd['kecamatan_nm']    = row.kecamatan_nm
        #rowd['kelurahan_kd']    = row.kelurahan_kd
        #rowd['kelurahan_nm']    = row.kelurahan_nm
        #rowd['is_kota']         = row.is_kota
        #rowd['disabled']      = row.disabled
        #rowd['sumber_id']    = row.sumber_id
        form.set_appstruct(rowd)
        return dict(form=form)

    ##########
    # Delete #
    ##########    
    @view_config(route_name='ar-payment-item-delete', renderer='templates/ar-payment-item/delete.pt',
                 permission='delete')
    def view_ar_payment_item_delete(self):
        request = self.request
        q       = self.query_id()
        row     = q.first()
        
        if not row:
            return self.id_not_found(request)
        if row.posted:
            request.session.flash('Data sudah diposting', 'error')
            return self.route_list()
            
        form = Form(colander.Schema(), buttons=('hapus','batal'))
        if request.POST:
            if 'hapus' in request.POST:
                msg = 'Realisasi / STS ID %d %s sudah dihapus.' % (row.id, row.nama)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'Realisasi / STS ID %d %s tidak dapat dihapus.' % (row.id, row.nama)
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row,
                     form=form.render())

    ###########
    # Posting #
    ###########     
    def save_request2(self, row=None):
        row = ARPaymentItem()
        self.request.session.flash('TBP sudah diposting dan dibuat Jurnalnya.')
        return row
        
    @view_config(route_name='ar-payment-item-posting', renderer='templates/ar-payment-item/posting.pt',
                 permission='posting')
    def view_edit_posting(self):
        request = self.request
        row     = self.query_id().first()
        id_tbp  = row.id
        nama    = row.ref_nama
        kode    = row.ref_kode
        tanggal = row.tanggal
        
        if not row:
            return id_not_found(request)
        if not row.amount:
           request.session.flash('Data tidak dapat diposting jurnal, karena bernilai 0.', 'error')
           return route_list()
        if row.posted:
            request.session.flash('Data sudah diposting jurnal.', 'error')
            return self.route_list()
            
        form = Form(colander.Schema(), buttons=('jurnal','cancel'))
        
        if request.POST:
            if 'jurnal' in request.POST: 
                #Update posted pada TBP
                row.posted=1
                self.save_request2(row)
                
                #Tambah ke Jurnal LO SKPD
                periode = ARPaymentItem.get_periode(row.id)
                
                row = Jurnal()
                row.created    = datetime.now()
                row.create_uid = self.request.user.id
                row.updated    = datetime.now()
                row.update_uid = self.request.user.id
                row.tahun_id   = self.session['tahun']
                row.unit_id    = self.session['unit_id']
                row.nama       = "Diterima TBP %s" % nama
                row.notes      = nama
                row.periode    = periode
                row.posted     = 0
                row.disabled   = 0
                row.is_skpd    = 1
                row.jv_type    = 1
                row.source     = "TBP"
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
                
                jui   = row.id
                rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                       Sap.nama.label('nama1'),
                                       KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                       ARPaymentItem.amount.label('nilai1'),
                                       RekeningSap.db_lo_sap_id.label('sap1'),
                                       Rekening.id.label('rek'),
                                ).join(Rekening
                                ).outerjoin(KegiatanItem,RekeningSap,KegiatanSub,
                                ).filter(ARPaymentItem.id==id_tbp,
                                       ARPaymentItem.rekening_id==KegiatanItem.rekening_id,
                                       KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                       KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                       RekeningSap.rekening_id==Rekening.id,
                                       RekeningSap.db_lo_sap_id==Sap.id
                                ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                       Sap.nama.label('nama1'),
                                       KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                       ARPaymentItem.amount.label('nilai1'),
                                       RekeningSap.db_lo_sap_id.label('sap1'),
                                       Rekening.id.label('rek'),
                                ).all()
                
                n=0
                for row in rows:
                    ji = JurnalItem()
                    
                    ji.jurnal_id = "%d" % jui
                    ji.kegiatan_sub_id = row.kegiatan_sub_id1
                    ji.rekening_id  = 0
                    x=DBSession.query(Sap.id).filter(Sap.kode=='1.1.1.02.01').first()
                    ji.sap_id       = x
                    ji.amount       = row.nilai1
                    ji.notes        = ""
                    n = n + 1
                    
                    DBSession.add(ji)
                    DBSession.flush()
                    
                n=0
                for row in rows:
                    ji2 = JurnalItem()
                    
                    ji2.jurnal_id = "%d" % jui
                    ji2.kegiatan_sub_id = row.kegiatan_sub_id1
                    ji2.rekening_id  = row.rek
                    ji2.sap_id       = row.sap1
                    n = row.nilai1
                    ji2.amount       = n * -1
                    ji2.notes        = ""
                    n = n + 1
                    
                    DBSession.add(ji2)
                    DBSession.flush()
                
                #Tambah ke Jurnal LRA SKPD
                periode2 = ARPaymentItem.get_periode2(id_tbp)
                
                row = Jurnal()
                row.created    = datetime.now()
                row.create_uid = self.request.user.id
                row.updated    = datetime.now()
                row.update_uid = self.request.user.id
                row.tahun_id   = self.session['tahun']
                row.unit_id    = self.session['unit_id']
                row.nama       = "Diterima TBP %s" % nama
                row.notes      = nama
                row.periode    = periode2
                row.posted     = 0
                row.disabled   = 0
                row.is_skpd    = 1
                row.jv_type    = 1
                row.source     = "TBP"
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
                
                jui   = row.id
                rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                       Sap.nama.label('nama1'),
                                       KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                       ARPaymentItem.amount.label('nilai1'),
                                       RekeningSap.db_lra_sap_id.label('sap1'),
                                       RekeningSap.kr_lra_sap_id.label('sap2'),
                                       Rekening.id.label('rek'),
                                ).join(Rekening
                                ).outerjoin(KegiatanItem,RekeningSap,KegiatanSub,
                                ).filter(ARPaymentItem.id==id_tbp,
                                       ARPaymentItem.rekening_id==KegiatanItem.rekening_id,
                                       KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                       KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                       RekeningSap.rekening_id==Rekening.id,
                                       RekeningSap.db_lra_sap_id==Sap.id
                                ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                       Sap.nama.label('nama1'),
                                       KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                       ARPaymentItem.amount.label('nilai1'),
                                       RekeningSap.db_lra_sap_id.label('sap1'),
                                       RekeningSap.kr_lra_sap_id.label('sap2'),
                                       Rekening.id.label('rek'),
                                ).all()
                
                n=0
                for row in rows:
                    ji3 = JurnalItem()
                    
                    ji3.jurnal_id = "%d" % jui
                    ji3.kegiatan_sub_id = row.kegiatan_sub_id1
                    ji3.rekening_id  = 0
                    ji3.sap_id       = row.sap1
                    ji3.amount       = row.nilai1
                    ji3.notes        = ""
                    n = n + 1
                    
                    DBSession.add(ji3)
                    DBSession.flush()
                    
                n=0
                for row in rows:
                    ji4 = JurnalItem()
                    
                    ji4.jurnal_id = "%d" % jui
                    ji4.kegiatan_sub_id = row.kegiatan_sub_id1
                    ji4.rekening_id  = row.rek
                    ji4.sap_id       = row.sap2
                    n = row.nilai1
                    ji4.amount       = n * -1
                    ji4.notes        = ""
                    n = n + 1
                    
                    DBSession.add(ji4)
                    DBSession.flush()
                    
            return self.route_list()
        return dict(row=row, form=form.render()) 

    #############
    # UnPosting #
    #############   
    def save_request4(self, row=None):
        row = ARPaymentItem()
        self.request.session.flash('TBP sudah di Unposting jurnal.')
        return row
        
    @view_config(route_name='ar-payment-item-unposting', renderer='templates/ar-payment-item/unposting.pt',
                 permission='unposting') 
    def view_edit_unposting(self):
        request = self.request
        row     = self.query_id().first()
        kode    = row.ref_kode
        
        if not row:
            return id_not_found(request)
        if not row.posted:
            self.request.session.flash('Data tidak dapat di Unposting jurnal, karena belum diposting jurnal.', 'error')
            return self.route_list()
        if row.disabled:
            self.request.session.flash('Data jurnal TBP sudah diposting.', 'error')
            return self.route_list()
            
        form = Form(colander.Schema(), buttons=('un-jurnal','cancel'))
        
        if request.POST:
            if 'un-jurnal' in request.POST: 
            
                #Update status posted pada TBP
                row.posted=0
                self.save_request4(row)
                
                r = DBSession.query(Jurnal.id.label('di')).filter(Jurnal.source_no==row.ref_kode,Jurnal.source=='TBP').all()
                for row in r:
                    #Menghapus Item Jurnal
                    DBSession.query(JurnalItem).filter(JurnalItem.jurnal_id==row.di).delete()
                    DBSession.flush()
                
                #Menghapus TBP yang sudah menjadi jurnal
                DBSession.query(Jurnal).filter(Jurnal.source_no==kode,Jurnal.source=='TBP').delete()
                DBSession.flush()
                
            return self.route_list()
        return dict(row=row, form=form.render())    