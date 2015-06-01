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
from osipkd.models.pemda_model import Unit, Rekening, RekeningSap, Sap
from osipkd.models.apbd_tu import Sp2d, Spm, Spp, AkJurnal, AkJurnalItem, SppItem, APInvoice, APInvoiceItem
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews
from array import *

SESS_ADD_FAILED = 'Tambah ak-sp2d gagal'
SESS_EDIT_FAILED = 'Edit ak-sp2d gagal'

class view_ak_sp2d_ppkd(BaseViews):

    @view_config(route_name="ak-sp2d", renderer="templates/ak-sp2d/list.pt")
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
    @view_config(route_name='ak-sp2d-act', renderer='json',
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
                columns.append(ColumnDT('no_validasi'))
                columns.append(ColumnDT('kode1'))
                columns.append(ColumnDT('nominal1'))
                columns.append(ColumnDT('posted'))
                query = DBSession.query(Sp2d.id, 
                                        Sp2d.kode, 
                                        Sp2d.tanggal,
                                        Sp2d.nama, 
                                        Sp2d.no_validasi, 
                                        Spm.kode.label('kode1'), 
                                        Spp.nominal.label('nominal1'),
                                        Sp2d.posted,
                        ).join(Spm 
                        ).outerjoin(Spp
                        ).filter(Spp.tahun_id==ses['tahun'],
                                 Spp.unit_id==ses['unit_id'],
                                 Sp2d.ap_spm_id==Spm.id,
                        )
                           
                rowTable = DataTables(req, Sp2d, query, columns)
                return rowTable.output_result()
            
    def route_list(self):
        return HTTPFound(location=self.request.route_url('ak-sp2d'))
        
    def session_failed(request, session_name):
        r = dict(form=request.session[session_name])
        del request.session[session_name]
        return r
        
    def query_id(self):
        return DBSession.query(Sp2d).filter(Sp2d.id==self.request.matchdict['id'])
        
    def id_not_found(request):    
        msg = 'User ID %s not found.' % request.matchdict['id']
        request.session.flash(msg, 'error')
        return self.route_list()

    def save_request3(self, row=None):
        row = Spm()
        return row

    ###########
    # Posting #
    ###########     
    def save_request2(self, row=None):
        row = Sp2d()
        self.request.session.flash('SP2D sudah diposting dan dibuat Jurnalnya.')
        return row
        
    @view_config(route_name='ak-sp2d-posting', renderer='templates/ak-sp2d/posting.pt',
                 permission='posting')
    def view_edit_posting(self):
        request = self.request
        row     = self.query_id().first()
        id_sp2d = row.id
        nam     = row.nama
        kod     = row.kode
        tgl     = row.tanggal
        gi      = DBSession.query(Spp.jenis.label('jenis'))\
                           .filter(Sp2d.id==id_sp2d,
                                   Sp2d.ap_spm_id==Spm.id,
                                   Spm.ap_spp_id==Spp.id,
                           ).first()
        g = '%s' % gi        
        
        if not row:
            return id_not_found(request)
        if row.posted:
            request.session.flash('Data sudah diposting jurnal', 'error')
            return self.route_list()
            
        form = Form(colander.Schema(), buttons=('jurnal','cancel'))
        if request.POST:
            if 'jurnal' in request.POST: 
                #Update posted pada SP2D
                row.posted=1
                self.save_request2(row)
                
                if g == '1':
                    #Tambah ke Jurnal PPKD
                    nama    = nam
                    kode    = kod
                    tanggal = tgl
                    tipe    = Sp2d.get_tipe(id_sp2d)
                    periode = Sp2d.get_periode(id_sp2d)
                    
                    row = AkJurnal()
                    row.created    = datetime.now()
                    row.create_uid = self.request.user.id
                    row.updated    = datetime.now()
                    row.update_uid = self.request.user.id
                    row.tahun_id   = self.session['tahun']
                    row.unit_id    = self.session['unit_id']
                    row.nama       = "Dibayar SP2D %s" % tipe + " %s" % nama
                    row.notes      = nama
                    row.periode    = periode
                    row.posted     = 0
                    row.disabled   = 0
                    row.is_skpd    = 0
                    row.jv_type    = 2
                    row.source     = "SP2D-%s" % tipe
                    row.source_no  = kode
                    row.tgl_source = tanggal
                    row.tanggal    = datetime.now()
                    row.tgl_transaksi = datetime.now()
                    
                    if not row.kode:
                        tahun    = self.session['tahun']
                        unit_kd  = self.session['unit_kd']
                        is_skpd  = row.is_skpd
                        tipe     = AkJurnal.get_tipe(row.jv_type)
                        no_urut  = AkJurnal.get_norut(row.tahun_id,row.unit_id)+1
                        no       = "0000%d" % no_urut
                        nomor    = no[-5:]     
                        row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                    
                    DBSession.add(row)
                    DBSession.flush()
                    
                    #Tambah ke Item Jurnal PPKD
                    jui   = row.id
                    rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Spp.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).filter(Sp2d.id==id_sp2d,
                                               Spm.id==Sp2d.ap_spm_id,
                                               Spp.id==Spm.ap_spp_id,
                                               SppItem.ap_spp_id==Spp.id,
                                               SppItem.ap_invoice_id==APInvoice.id,
                                               APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                               APInvoiceItem.ap_invoice_id==APInvoice.id,
                                               APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                               KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                               KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                               RekeningSap.rekening_id==Rekening.id,
                                               RekeningSap.db_lra_sap_id==Sap.id
                                        ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Spp.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).first()
                        
                    ji1 = AkJurnalItem()
                    ji1.ak_jurnal_id = "%d" % jui
                    ji1.kegiatan_sub_id = 0
                    ji1.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.8.01.01').first()
                    ji1.sap_id       = s
                    ji1.amount       = rows.nilai1
                    ji1.notes        = ""
                    DBSession.add(ji1)
                    DBSession.flush()
                    
                    ji2 = AkJurnalItem()
                    ji2.ak_jurnal_id = "%d" % jui
                    ji2.kegiatan_sub_id = 0
                    ji2.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.1.01.01').first()
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
                    tipe    = Sp2d.get_tipe(id_sp2d)
                    periode = Sp2d.get_periode(id_sp2d)
                    
                    row = AkJurnal()
                    row.created    = datetime.now()
                    row.create_uid = self.request.user.id
                    row.updated    = datetime.now()
                    row.update_uid = self.request.user.id
                    row.tahun_id   = self.session['tahun']
                    row.unit_id    = self.session['unit_id']
                    row.nama       = "Dibayar SP2D %s" % tipe + " %s" % nama
                    row.notes      = nama
                    row.periode    = periode
                    row.posted     = 0
                    row.disabled   = 0
                    row.is_skpd    = 1
                    row.jv_type    = 2
                    row.source     = "SP2D-%s" % tipe
                    row.source_no  = kode
                    row.tgl_source = tanggal
                    row.tanggal    = datetime.now()
                    row.tgl_transaksi = datetime.now()
                    
                    if not row.kode:
                        tahun    = self.session['tahun']
                        unit_kd  = self.session['unit_kd']
                        is_skpd  = row.is_skpd
                        tipe     = AkJurnal.get_tipe(row.jv_type)
                        no_urut  = AkJurnal.get_norut(row.tahun_id,row.unit_id)+1
                        no       = "0000%d" % no_urut
                        nomor    = no[-5:]     
                        row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                    
                    DBSession.add(row)
                    DBSession.flush()
                    
                    #Tambah ke Item Jurnal PPKD
                    jui   = row.id
                    rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Spp.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).filter(Sp2d.id==id_sp2d,
                                               Spm.id==Sp2d.ap_spm_id,
                                               Spp.id==Spm.ap_spp_id,
                                               SppItem.ap_spp_id==Spp.id,
                                               SppItem.ap_invoice_id==APInvoice.id,
                                               APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                               APInvoiceItem.ap_invoice_id==APInvoice.id,
                                               APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                               KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                               KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                               RekeningSap.rekening_id==Rekening.id,
                                               RekeningSap.db_lra_sap_id==Sap.id
                                        ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Spp.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).first()
                        
                    ji1 = AkJurnalItem()
                    ji1.ak_jurnal_id = "%d" % jui
                    ji1.kegiatan_sub_id = 0
                    ji1.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.1.03.01').first()
                    ji1.sap_id       = s
                    ji1.amount       = rows.nilai1
                    ji1.notes        = ""
                    DBSession.add(ji1)
                    DBSession.flush()
                    
                    ji2 = AkJurnalItem()
                    ji2.ak_jurnal_id = "%d" % jui
                    ji2.kegiatan_sub_id = 0
                    ji2.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='3.1.3.01.01').first()
                    ji2.sap_id       = s
                    n = rows.nilai1
                    ji2.amount       = n * -1
                    ji2.notes        = ""
                    DBSession.add(ji2)
                    DBSession.flush()
                
                elif g == '2':
                    #Tambah ke Jurnal PPKD
                    nama    = nam
                    kode    = kod
                    tanggal = tgl
                    tipe    = Sp2d.get_tipe(id_sp2d)
                    periode = Sp2d.get_periode(id_sp2d)
                    
                    row = AkJurnal()
                    row.created    = datetime.now()
                    row.create_uid = self.request.user.id
                    row.updated    = datetime.now()
                    row.update_uid = self.request.user.id
                    row.tahun_id   = self.session['tahun']
                    row.unit_id    = self.session['unit_id']
                    row.nama       = "Dibayar SP2D %s" % tipe + " %s" % nama
                    row.notes      = nama
                    row.periode    = periode
                    row.posted     = 0
                    row.disabled   = 0
                    row.is_skpd    = 0
                    row.jv_type    = 2
                    row.source     = "SP2D-%s" % tipe
                    row.source_no  = kode
                    row.tgl_source = tanggal
                    row.tanggal    = datetime.now()
                    row.tgl_transaksi = datetime.now()
                    
                    if not row.kode:
                        tahun    = self.session['tahun']
                        unit_kd  = self.session['unit_kd']
                        is_skpd  = row.is_skpd
                        tipe     = AkJurnal.get_tipe(row.jv_type)
                        no_urut  = AkJurnal.get_norut(row.tahun_id,row.unit_id)+1
                        no       = "0000%d" % no_urut
                        nomor    = no[-5:]     
                        row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                    
                    DBSession.add(row)
                    DBSession.flush()
                    
                    #Tambah ke Item Jurnal PPKD
                    jui   = row.id
                    rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Spp.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).filter(Sp2d.id==id_sp2d,
                                               Spm.id==Sp2d.ap_spm_id,
                                               Spp.id==Spm.ap_spp_id,
                                               SppItem.ap_spp_id==Spp.id,
                                               SppItem.ap_invoice_id==APInvoice.id,
                                               APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                               APInvoiceItem.ap_invoice_id==APInvoice.id,
                                               APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                               KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                               KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                               RekeningSap.rekening_id==Rekening.id,
                                               RekeningSap.db_lra_sap_id==Sap.id
                                        ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Spp.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).first()
                        
                    ji1 = AkJurnalItem()
                    ji1.ak_jurnal_id = "%d" % jui
                    ji1.kegiatan_sub_id = 0
                    ji1.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.8.01.01').first()
                    ji1.sap_id       = s
                    ji1.amount       = rows.nilai1
                    ji1.notes        = ""
                    DBSession.add(ji1)
                    DBSession.flush()
                    
                    ji2 = AkJurnalItem()
                    ji2.ak_jurnal_id = "%d" % jui
                    ji2.kegiatan_sub_id = 0
                    ji2.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.1.01.01').first()
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
                    tipe    = Sp2d.get_tipe(id_sp2d)
                    periode = Sp2d.get_periode(id_sp2d)
                    
                    row = AkJurnal()
                    row.created    = datetime.now()
                    row.create_uid = self.request.user.id
                    row.updated    = datetime.now()
                    row.update_uid = self.request.user.id
                    row.tahun_id   = self.session['tahun']
                    row.unit_id    = self.session['unit_id']
                    row.nama       = "Dibayar SP2D %s" % tipe + " %s" % nama
                    row.notes      = nama
                    row.periode    = periode
                    row.posted     = 0
                    row.disabled   = 0
                    row.is_skpd    = 1
                    row.jv_type    = 2
                    row.source     = "SP2D-%s" % tipe
                    row.source_no  = kode
                    row.tgl_source = tanggal
                    row.tanggal    = datetime.now()
                    row.tgl_transaksi = datetime.now()
                    
                    if not row.kode:
                        tahun    = self.session['tahun']
                        unit_kd  = self.session['unit_kd']
                        is_skpd  = row.is_skpd
                        tipe     = AkJurnal.get_tipe(row.jv_type)
                        no_urut  = AkJurnal.get_norut(row.tahun_id,row.unit_id)+1
                        no       = "0000%d" % no_urut
                        nomor    = no[-5:]     
                        row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                    
                    DBSession.add(row)
                    DBSession.flush()
                    
                    #Tambah ke Item Jurnal PPKD
                    jui   = row.id
                    rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Spp.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).filter(Sp2d.id==id_sp2d,
                                               Spm.id==Sp2d.ap_spm_id,
                                               Spp.id==Spm.ap_spp_id,
                                               SppItem.ap_spp_id==Spp.id,
                                               SppItem.ap_invoice_id==APInvoice.id,
                                               APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                               APInvoiceItem.ap_invoice_id==APInvoice.id,
                                               APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                               KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                               KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                               RekeningSap.rekening_id==Rekening.id,
                                               RekeningSap.db_lra_sap_id==Sap.id
                                        ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Spp.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).first()
                        
                    ji1 = AkJurnalItem()
                    ji1.ak_jurnal_id = "%d" % jui
                    ji1.kegiatan_sub_id = 0
                    ji1.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.1.03.01').first()
                    ji1.sap_id       = s
                    ji1.amount       = rows.nilai1
                    ji1.notes        = ""
                    DBSession.add(ji1)
                    DBSession.flush()
                    
                    ji2 = AkJurnalItem()
                    ji2.ak_jurnal_id = "%d" % jui
                    ji2.kegiatan_sub_id = 0
                    ji2.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='3.1.3.01.01').first()
                    ji2.sap_id       = s
                    n = rows.nilai1
                    ji2.amount       = n * -1
                    ji2.notes        = ""
                    DBSession.add(ji2)
                    DBSession.flush()
                
                elif g == '3':
                    x = DBSession.query(APInvoice.id).filter(Sp2d.id==id_sp2d,
                                                             Spm.id==Sp2d.ap_spm_id,
                                                             Spp.id==Spm.ap_spp_id,
                                                             SppItem.ap_spp_id==Spp.id,
                                                             SppItem.ap_invoice_id==APInvoice.id,
                                                             APInvoice.is_bayar==1,
                                                             APInvoiceItem.ap_invoice_id==APInvoice.id,
                                                    ).first()
                    if x:
                        #Tambah ke Jurnal SKPD
                        nama    = nam
                        kode    = kod
                        tanggal = tgl
                        tipe    = Sp2d.get_tipe(id_sp2d)
                        periode = Sp2d.get_periode(id_sp2d)
                        
                        row = AkJurnal()
                        row.created    = datetime.now()
                        row.create_uid = self.request.user.id
                        row.updated    = datetime.now()
                        row.update_uid = self.request.user.id
                        row.tahun_id   = self.session['tahun']
                        row.unit_id    = self.session['unit_id']
                        row.nama       = "Dibayar SP2D %s" % tipe + " %s" % nama
                        row.notes      = nama
                        row.periode    = periode
                        row.posted     = 0
                        row.disabled   = 0
                        row.is_skpd    = 1
                        row.jv_type    = 2
                        row.source     = "SP2D-%s" % tipe
                        row.source_no  = kode
                        row.tgl_source = tanggal
                        row.tanggal    = datetime.now()
                        row.tgl_transaksi = datetime.now()
                        
                        if not row.kode:
                            tahun    = self.session['tahun']
                            unit_kd  = self.session['unit_kd']
                            is_skpd  = row.is_skpd
                            tipe     = AkJurnal.get_tipe(row.jv_type)
                            no_urut  = AkJurnal.get_norut(row.tahun_id,row.unit_id)+1
                            no       = "0000%d" % no_urut
                            nomor    = no[-5:]     
                            row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                        
                        DBSession.add(row)
                        DBSession.flush()
                        
                        #Tambah ke Item Jurnal PPKD
                        jui   = row.id
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   APInvoiceItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lo_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).filter(Sp2d.id==id_sp2d,
                                                   Spm.id==Sp2d.ap_spm_id,
                                                   Spp.id==Spm.ap_spp_id,
                                                   SppItem.ap_spp_id==Spp.id,
                                                   SppItem.ap_invoice_id==APInvoice.id,
                                                   APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                                   APInvoice.is_bayar==1,
                                                   APInvoiceItem.ap_invoice_id==APInvoice.id,
                                                   APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.db_lra_sap_id==Sap.id
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   APInvoiceItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lo_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).all()
                        
                        for row in rows:                    
                            ji1 = AkJurnalItem()
                            ji1.ak_jurnal_id = "%d" % jui
                            ji1.kegiatan_sub_id = row.kegiatan_sub_id1
                            ji1.rekening_id  = row.rek
                            ji1.sap_id       = row.sap2
                            ji1.amount       = row.nilai2
                            ji1.notes        = ""
                            DBSession.add(ji1)
                            DBSession.flush()
                        
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   APInvoice.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).filter(Sp2d.id==id_sp2d,
                                                   Spm.id==Sp2d.ap_spm_id,
                                                   Spp.id==Spm.ap_spp_id,
                                                   SppItem.ap_spp_id==Spp.id,
                                                   SppItem.ap_invoice_id==APInvoice.id,
                                                   APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                                   APInvoice.is_bayar==1,
                                                   APInvoiceItem.ap_invoice_id==APInvoice.id,
                                                   APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.db_lra_sap_id==Sap.id
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   APInvoice.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).first()
                        
                        ji2 = AkJurnalItem()
                        ji2.ak_jurnal_id = "%d" % jui
                        ji2.kegiatan_sub_id = 0
                        ji2.rekening_id  = 0
                        ji2.notes        = ""
                        
                        s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.1.03.01').first()
                        ji2.sap_id       = s
                        
                        n = DBSession.query(func.sum(APInvoiceItem.amount).label('nilai3')).filter(Sp2d.id==id_sp2d,
                                                                                                  Spm.id==Sp2d.ap_spm_id,
                                                                                                  Spp.id==Spm.ap_spp_id,
                                                                                                  SppItem.ap_spp_id==Spp.id,
                                                                                                  SppItem.ap_invoice_id==APInvoice.id,
                                                                                                  APInvoice.is_bayar==1,
                                                                                                  APInvoiceItem.ap_invoice_id==APInvoice.id,
                                                                                        ).all()
                        for row in n:                                                                
                            ni = row.nilai3
                        ji2.amount       = ni * -1
                        DBSession.add(ji2)
                        DBSession.flush()
                    
                    #Tambah ke Jurnal SKPD
                    nama    = nam
                    kode    = kod
                    tanggal = tgl
                    tipe    = Sp2d.get_tipe(id_sp2d)
                    periode = Sp2d.get_periode(id_sp2d)
                    
                    row = AkJurnal()
                    row.created    = datetime.now()
                    row.create_uid = self.request.user.id
                    row.updated    = datetime.now()
                    row.update_uid = self.request.user.id
                    row.tahun_id   = self.session['tahun']
                    row.unit_id    = self.session['unit_id']
                    row.nama       = "Dibayar SP2D %s" % tipe + " %s" % nama
                    row.notes      = nama
                    row.periode    = periode
                    row.posted     = 0
                    row.disabled   = 0
                    row.is_skpd    = 1
                    row.jv_type    = 2
                    row.source     = "SP2D-%s" % tipe
                    row.source_no  = kode
                    row.tgl_source = tanggal
                    row.tanggal    = datetime.now()
                    row.tgl_transaksi = datetime.now()
                    
                    if not row.kode:
                        tahun    = self.session['tahun']
                        unit_kd  = self.session['unit_kd']
                        is_skpd  = row.is_skpd
                        tipe     = AkJurnal.get_tipe(row.jv_type)
                        no_urut  = AkJurnal.get_norut(row.tahun_id,row.unit_id)+1
                        no       = "0000%d" % no_urut
                        nomor    = no[-5:]     
                        row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                    
                    DBSession.add(row)
                    DBSession.flush()
                    
                    #Tambah ke Item Jurnal PPKD
                    jui   = row.id
                    rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Spp.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).filter(Sp2d.id==id_sp2d,
                                               Spm.id==Sp2d.ap_spm_id,
                                               Spp.id==Spm.ap_spp_id,
                                               SppItem.ap_spp_id==Spp.id,
                                               SppItem.ap_invoice_id==APInvoice.id,
                                               APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                               APInvoiceItem.ap_invoice_id==APInvoice.id,
                                               APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                               KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                               KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                               RekeningSap.rekening_id==Rekening.id,
                                               RekeningSap.db_lra_sap_id==Sap.id
                                        ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Spp.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).first()
                        
                    ji1 = AkJurnalItem()
                    ji1.ak_jurnal_id = "%d" % jui
                    ji1.kegiatan_sub_id = 0
                    ji1.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.1.03.01').first()
                    ji1.sap_id       = s
                    ji1.amount       = rows.nilai1
                    ji1.notes        = ""
                    DBSession.add(ji1)
                    DBSession.flush()
                    
                    ji2 = AkJurnalItem()
                    ji2.ak_jurnal_id = "%d" % jui
                    ji2.kegiatan_sub_id = 0
                    ji2.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='3.1.3.01.01').first()
                    ji2.sap_id       = s
                    n = rows.nilai1
                    ji2.amount       = n * -1
                    ji2.notes        = ""
                    DBSession.add(ji2)
                    DBSession.flush()
                    
                    #Tambah ke Jurnal PPKD
                    nama    = nam
                    kode    = kod
                    tanggal = tgl
                    tipe    = Sp2d.get_tipe(id_sp2d)
                    periode = Sp2d.get_periode(id_sp2d)
                    
                    row = AkJurnal()
                    row.created    = datetime.now()
                    row.create_uid = self.request.user.id
                    row.updated    = datetime.now()
                    row.update_uid = self.request.user.id
                    row.tahun_id   = self.session['tahun']
                    row.unit_id    = self.session['unit_id']
                    row.nama       = "Dibayar SP2D %s" % tipe + " %s" % nama
                    row.notes      = nama
                    row.periode    = periode
                    row.posted     = 0
                    row.disabled   = 0
                    row.is_skpd    = 0
                    row.jv_type    = 2
                    row.source     = "SP2D-%s" % tipe
                    row.source_no  = kode
                    row.tgl_source = tanggal
                    row.tanggal    = datetime.now()
                    row.tgl_transaksi = datetime.now()
                    
                    if not row.kode:
                        tahun    = self.session['tahun']
                        unit_kd  = self.session['unit_kd']
                        is_skpd  = row.is_skpd
                        tipe     = AkJurnal.get_tipe(row.jv_type)
                        no_urut  = AkJurnal.get_norut(row.tahun_id,row.unit_id)+1
                        no       = "0000%d" % no_urut
                        nomor    = no[-5:]     
                        row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                    
                    DBSession.add(row)
                    DBSession.flush()
                    
                    #Tambah ke Item Jurnal PPKD
                    jui   = row.id
                    rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Spp.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).filter(Sp2d.id==id_sp2d,
                                               Spm.id==Sp2d.ap_spm_id,
                                               Spp.id==Spm.ap_spp_id,
                                               SppItem.ap_spp_id==Spp.id,
                                               SppItem.ap_invoice_id==APInvoice.id,
                                               APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                               APInvoiceItem.ap_invoice_id==APInvoice.id,
                                               APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                               KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                               KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                               RekeningSap.rekening_id==Rekening.id,
                                               RekeningSap.db_lra_sap_id==Sap.id
                                        ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Spp.nominal.label('nilai1'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).first()
                        
                    ji1 = AkJurnalItem()
                    ji1.ak_jurnal_id = "%d" % jui
                    ji1.kegiatan_sub_id = 0
                    ji1.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.8.01.01').first()
                    ji1.sap_id       = s
                    ji1.amount       = rows.nilai1
                    ji1.notes        = ""
                    DBSession.add(ji1)
                    DBSession.flush()
                    
                    ji2 = AkJurnalItem()
                    ji2.ak_jurnal_id = "%d" % jui
                    ji2.kegiatan_sub_id = 0
                    ji2.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.1.01.01').first()
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
                    tipe    = Sp2d.get_tipe(id_sp2d)
                    periode = Sp2d.get_periode(id_sp2d)
                    
                    row = AkJurnal()
                    row.created    = datetime.now()
                    row.create_uid = self.request.user.id
                    row.updated    = datetime.now()
                    row.update_uid = self.request.user.id
                    row.tahun_id   = self.session['tahun']
                    row.unit_id    = self.session['unit_id']
                    row.nama       = "Dibayar SP2D %s" % tipe + " %s" % nama
                    row.notes      = nama
                    row.periode    = periode
                    row.posted     = 0
                    row.disabled   = 0
                    row.is_skpd    = 1
                    row.jv_type    = 2
                    row.source     = "SP2D-%s" % tipe
                    row.source_no  = kode
                    row.tgl_source = tanggal
                    row.tanggal    = datetime.now()
                    row.tgl_transaksi = datetime.now()
                    
                    if not row.kode:
                        tahun    = self.session['tahun']
                        unit_kd  = self.session['unit_kd']
                        is_skpd  = row.is_skpd
                        tipe     = AkJurnal.get_tipe(row.jv_type)
                        no_urut  = AkJurnal.get_norut(row.tahun_id,row.unit_id)+1
                        no       = "0000%d" % no_urut
                        nomor    = no[-5:]     
                        row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                    
                    DBSession.add(row)
                    DBSession.flush()
                    
                    #Tambah ke Item Jurnal PPKD
                    jui   = row.id
                    rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Spp.nominal.label('nilai1'),
                                               APInvoiceItem.amount.label('nilai2'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).filter(Sp2d.id==id_sp2d,
                                               Spm.id==Sp2d.ap_spm_id,
                                               Spp.id==Spm.ap_spp_id,
                                               SppItem.ap_spp_id==Spp.id,
                                               SppItem.ap_invoice_id==APInvoice.id,
                                               APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                               APInvoiceItem.ap_invoice_id==APInvoice.id,
                                               APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                               KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                               KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                               RekeningSap.rekening_id==Rekening.id,
                                               RekeningSap.db_lra_sap_id==Sap.id
                                        ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Spp.nominal.label('nilai1'),
                                               APInvoiceItem.amount.label('nilai2'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).all()
                    
                    for row in rows:                    
                        ji1 = AkJurnalItem()
                        ji1.ak_jurnal_id = "%d" % jui
                        ji1.kegiatan_sub_id = row.kegiatan_sub_id1
                        ji1.rekening_id  = row.rek
                        ji1.sap_id       = row.sap1
                        ji1.amount       = row.nilai2
                        ji1.notes        = ""
                        DBSession.add(ji1)
                        DBSession.flush()
                    
                    rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Spp.nominal.label('nilai1'),
                                               APInvoiceItem.amount.label('nilai2'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).filter(Sp2d.id==id_sp2d,
                                               Spm.id==Sp2d.ap_spm_id,
                                               Spp.id==Spm.ap_spp_id,
                                               SppItem.ap_spp_id==Spp.id,
                                               SppItem.ap_invoice_id==APInvoice.id,
                                               APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                               APInvoiceItem.ap_invoice_id==APInvoice.id,
                                               APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                               KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                               KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                               RekeningSap.rekening_id==Rekening.id,
                                               RekeningSap.db_lra_sap_id==Sap.id
                                        ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               Spp.nominal.label('nilai1'),
                                               APInvoiceItem.amount.label('nilai2'),
                                               RekeningSap.db_lra_sap_id.label('sap1'),
                                               RekeningSap.kr_lra_sap_id.label('sap2'),
                                               Rekening.id.label('rek'),
                                        ).first()
                    
                    ji2 = AkJurnalItem()
                    ji2.ak_jurnal_id = "%d" % jui
                    ji2.kegiatan_sub_id = 0
                    ji2.rekening_id  = 0
                    s=DBSession.query(Sap.id).filter(Sap.kode=='0.0.0.00.00').first()
                    ji2.sap_id       = s
                    n = rows.nilai1
                    ji2.amount       = n * -1
                    ji2.notes        = ""
                    DBSession.add(ji2)
                    DBSession.flush()
                    
                else:
                    xa1=DBSession.query(Kegiatan.id
                               ).filter(Sp2d.id==id_sp2d,
                                       Spm.id==Sp2d.ap_spm_id,
                                       Spp.id==Spm.ap_spp_id,
                                       SppItem.ap_spp_id==Spp.id,
                                       SppItem.ap_invoice_id==APInvoice.id,
                                       APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                       APInvoiceItem.ap_invoice_id==APInvoice.id,
                                       APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                       KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                       KegiatanSub.kegiatan_id==Kegiatan.id,
                               ).first()
                    xa = '%s' % xa1
                    if xa == '2':
                        #Tambah ke Jurnal PPKD
                        nama    = nam
                        kode    = kod
                        tanggal = tgl
                        tipe    = Sp2d.get_tipe(id_sp2d)
                        periode = Sp2d.get_periode(id_sp2d)
                        
                        row = AkJurnal()
                        row.created    = datetime.now()
                        row.create_uid = self.request.user.id
                        row.updated    = datetime.now()
                        row.update_uid = self.request.user.id
                        row.tahun_id   = self.session['tahun']
                        row.unit_id    = self.session['unit_id']
                        row.nama       = "Dibayar SP2D %s" % tipe + " %s" % nama
                        row.notes      = nama
                        row.periode    = periode
                        row.posted     = 0
                        row.disabled   = 0
                        row.is_skpd    = 0
                        row.jv_type    = 2
                        row.source     = "SP2D-%s" % tipe
                        row.source_no  = kode
                        row.tgl_source = tanggal
                        row.tanggal    = datetime.now()
                        row.tgl_transaksi = datetime.now()
                        
                        if not row.kode:
                            tahun    = self.session['tahun']
                            unit_kd  = self.session['unit_kd']
                            is_skpd  = row.is_skpd
                            tipe     = AkJurnal.get_tipe(row.jv_type)
                            no_urut  = AkJurnal.get_norut(row.tahun_id,row.unit_id)+1
                            no       = "0000%d" % no_urut
                            nomor    = no[-5:]     
                            row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                        
                        DBSession.add(row)
                        DBSession.flush()
                        
                        #Tambah ke Item Jurnal PPKD
                        jui   = row.id
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).filter(Sp2d.id==id_sp2d,
                                                   Spm.id==Sp2d.ap_spm_id,
                                                   Spp.id==Spm.ap_spp_id,
                                                   SppItem.ap_spp_id==Spp.id,
                                                   SppItem.ap_invoice_id==APInvoice.id,
                                                   APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                                   APInvoiceItem.ap_invoice_id==APInvoice.id,
                                                   APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.db_lra_sap_id==Sap.id
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).first()
                            
                        ji1 = AkJurnalItem()
                        ji1.ak_jurnal_id = "%d" % jui
                        ji1.kegiatan_sub_id = 0
                        ji1.rekening_id  = 0
                        s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.8.01.01').first()
                        ji1.sap_id       = s
                        ji1.amount       = rows.nilai1
                        ji1.notes        = ""
                        DBSession.add(ji1)
                        DBSession.flush()
                        
                        ji2 = AkJurnalItem()
                        ji2.ak_jurnal_id = "%d" % jui
                        ji2.kegiatan_sub_id = 0
                        ji2.rekening_id  = 0
                        s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.1.01.01').first()
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
                        tipe    = Sp2d.get_tipe(id_sp2d)
                        periode = Sp2d.get_periode(id_sp2d)
                        
                        row = AkJurnal()
                        row.created    = datetime.now()
                        row.create_uid = self.request.user.id
                        row.updated    = datetime.now()
                        row.update_uid = self.request.user.id
                        row.tahun_id   = self.session['tahun']
                        row.unit_id    = self.session['unit_id']
                        row.nama       = "Dibayar SP2D %s" % tipe + " %s" % nama
                        row.notes      = nama
                        row.periode    = periode
                        row.posted     = 0
                        row.disabled   = 0
                        row.is_skpd    = 1
                        row.jv_type    = 2
                        row.source     = "SP2D-%s" % tipe
                        row.source_no  = kode
                        row.tgl_source = tanggal
                        row.tanggal    = datetime.now()
                        row.tgl_transaksi = datetime.now()
                        
                        if not row.kode:
                            tahun    = self.session['tahun']
                            unit_kd  = self.session['unit_kd']
                            is_skpd  = row.is_skpd
                            tipe     = AkJurnal.get_tipe(row.jv_type)
                            no_urut  = AkJurnal.get_norut(row.tahun_id,row.unit_id)+1
                            no       = "0000%d" % no_urut
                            nomor    = no[-5:]     
                            row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                        
                        DBSession.add(row)
                        DBSession.flush()
                        
                        #Tambah ke Item Jurnal PPKD
                        jui   = row.id
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   APInvoiceItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).filter(Sp2d.id==id_sp2d,
                                                   Spm.id==Sp2d.ap_spm_id,
                                                   Spp.id==Spm.ap_spp_id,
                                                   SppItem.ap_spp_id==Spp.id,
                                                   SppItem.ap_invoice_id==APInvoice.id,
                                                   APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                                   APInvoiceItem.ap_invoice_id==APInvoice.id,
                                                   APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.db_lra_sap_id==Sap.id
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   APInvoiceItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).all()
                        
                        for row in rows:                    
                            ji1 = AkJurnalItem()
                            ji1.ak_jurnal_id = "%d" % jui
                            ji1.kegiatan_sub_id = row.kegiatan_sub_id1
                            ji1.rekening_id  = row.rek
                            ji1.sap_id       = row.sap1
                            ji1.amount       = row.nilai2
                            ji1.notes        = ""
                            DBSession.add(ji1)
                            DBSession.flush()
                        
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   APInvoiceItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).filter(Sp2d.id==id_sp2d,
                                                   Spm.id==Sp2d.ap_spm_id,
                                                   Spp.id==Spm.ap_spp_id,
                                                   SppItem.ap_spp_id==Spp.id,
                                                   SppItem.ap_invoice_id==APInvoice.id,
                                                   APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                                   APInvoiceItem.ap_invoice_id==APInvoice.id,
                                                   APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.db_lra_sap_id==Sap.id
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   APInvoiceItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).first()
                        
                        ji2 = AkJurnalItem()
                        ji2.ak_jurnal_id = "%d" % jui
                        ji2.kegiatan_sub_id = 0
                        ji2.rekening_id  = 0
                        s=DBSession.query(Sap.id).filter(Sap.kode=='0.0.0.00.00').first()
                        ji2.sap_id       = s
                        n = rows.nilai1
                        ji2.amount       = n * -1
                        ji2.notes        = ""
                        DBSession.add(ji2)
                        DBSession.flush()
                
                    else:                    
                        #Tambah ke Jurnal PPKD
                        nama    = nam
                        kode    = kod
                        tanggal = tgl
                        tipe    = Sp2d.get_tipe(id_sp2d)
                        periode = Sp2d.get_periode(id_sp2d)
                        
                        row = AkJurnal()
                        row.created    = datetime.now()
                        row.create_uid = self.request.user.id
                        row.updated    = datetime.now()
                        row.update_uid = self.request.user.id
                        row.tahun_id   = self.session['tahun']
                        row.unit_id    = self.session['unit_id']
                        row.nama       = "Dibayar SP2D %s" % tipe + " %s" % nama
                        row.notes      = nama
                        row.periode    = periode
                        row.posted     = 0
                        row.disabled   = 0
                        row.is_skpd    = 0
                        row.jv_type    = 2
                        row.source     = "SP2D-%s" % tipe
                        row.source_no  = kode
                        row.tgl_source = tanggal
                        row.tanggal    = datetime.now()
                        row.tgl_transaksi = datetime.now()
                        
                        if not row.kode:
                            tahun    = self.session['tahun']
                            unit_kd  = self.session['unit_kd']
                            is_skpd  = row.is_skpd
                            tipe     = AkJurnal.get_tipe(row.jv_type)
                            no_urut  = AkJurnal.get_norut(row.tahun_id,row.unit_id)+1
                            no       = "0000%d" % no_urut
                            nomor    = no[-5:]     
                            row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                        
                        DBSession.add(row)
                        DBSession.flush()
                        
                        #Tambah ke Item Jurnal PPKD
                        jui   = row.id
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).filter(Sp2d.id==id_sp2d,
                                                   Spm.id==Sp2d.ap_spm_id,
                                                   Spp.id==Spm.ap_spp_id,
                                                   SppItem.ap_spp_id==Spp.id,
                                                   SppItem.ap_invoice_id==APInvoice.id,
                                                   APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                                   APInvoiceItem.ap_invoice_id==APInvoice.id,
                                                   APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.db_lra_sap_id==Sap.id
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).first()
                            
                        ji1 = AkJurnalItem()
                        ji1.ak_jurnal_id = "%d" % jui
                        ji1.kegiatan_sub_id = 0
                        ji1.rekening_id  = 0
                        s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.8.01.01').first()
                        ji1.sap_id       = s
                        ji1.amount       = rows.nilai1
                        ji1.notes        = ""
                        DBSession.add(ji1)
                        DBSession.flush()
                        
                        ji2 = AkJurnalItem()
                        ji2.ak_jurnal_id = "%d" % jui
                        ji2.kegiatan_sub_id = 0
                        ji2.rekening_id  = 0
                        s=DBSession.query(Sap.id).filter(Sap.kode=='1.1.1.01.01').first()
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
                        tipe    = Sp2d.get_tipe(id_sp2d)
                        periode = Sp2d.get_periode(id_sp2d)
                        
                        row = AkJurnal()
                        row.created    = datetime.now()
                        row.create_uid = self.request.user.id
                        row.updated    = datetime.now()
                        row.update_uid = self.request.user.id
                        row.tahun_id   = self.session['tahun']
                        row.unit_id    = self.session['unit_id']
                        row.nama       = "Dibayar SP2D %s" % tipe + " %s" % nama
                        row.notes      = nama
                        row.periode    = periode
                        row.posted     = 0
                        row.disabled   = 0
                        row.is_skpd    = 1
                        row.jv_type    = 2
                        row.source     = "SP2D-%s" % tipe
                        row.source_no  = kode
                        row.tgl_source = tanggal
                        row.tanggal    = datetime.now()
                        row.tgl_transaksi = datetime.now()
                        
                        if not row.kode:
                            tahun    = self.session['tahun']
                            unit_kd  = self.session['unit_kd']
                            is_skpd  = row.is_skpd
                            tipe     = AkJurnal.get_tipe(row.jv_type)
                            no_urut  = AkJurnal.get_norut(row.tahun_id,row.unit_id)+1
                            no       = "0000%d" % no_urut
                            nomor    = no[-5:]     
                            row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                        
                        DBSession.add(row)
                        DBSession.flush()
                        
                        #Tambah ke Item Jurnal PPKD
                        jui   = row.id
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   APInvoiceItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lo_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).filter(Sp2d.id==id_sp2d,
                                                   Spm.id==Sp2d.ap_spm_id,
                                                   Spp.id==Spm.ap_spp_id,
                                                   SppItem.ap_spp_id==Spp.id,
                                                   SppItem.ap_invoice_id==APInvoice.id,
                                                   APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                                   APInvoiceItem.ap_invoice_id==APInvoice.id,
                                                   APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.db_lra_sap_id==Sap.id
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   APInvoiceItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lo_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).all()
                        
                        for row in rows:                    
                            ji1 = AkJurnalItem()
                            ji1.ak_jurnal_id = "%d" % jui
                            ji1.kegiatan_sub_id = row.kegiatan_sub_id1
                            ji1.rekening_id  = row.rek
                            ji1.sap_id       = row.sap2
                            ji1.amount       = row.nilai2
                            ji1.notes        = ""
                            DBSession.add(ji1)
                            DBSession.flush()
                        
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   APInvoiceItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).filter(Sp2d.id==id_sp2d,
                                                   Spm.id==Sp2d.ap_spm_id,
                                                   Spp.id==Spm.ap_spp_id,
                                                   SppItem.ap_spp_id==Spp.id,
                                                   SppItem.ap_invoice_id==APInvoice.id,
                                                   APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                                   APInvoiceItem.ap_invoice_id==APInvoice.id,
                                                   APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.db_lra_sap_id==Sap.id
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   APInvoiceItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).first()
                        
                        ji2 = AkJurnalItem()
                        ji2.ak_jurnal_id = "%d" % jui
                        ji2.kegiatan_sub_id = 0
                        ji2.rekening_id  = 0
                        s=DBSession.query(Sap.id).filter(Sap.kode=='3.1.3.01.01').first()
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
                        tipe    = Sp2d.get_tipe(id_sp2d)
                        periode = Sp2d.get_periode(id_sp2d)
                        
                        row = AkJurnal()
                        row.created    = datetime.now()
                        row.create_uid = self.request.user.id
                        row.updated    = datetime.now()
                        row.update_uid = self.request.user.id
                        row.tahun_id   = self.session['tahun']
                        row.unit_id    = self.session['unit_id']
                        row.nama       = "Dibayar SP2D %s" % tipe + " %s" % nama
                        row.notes      = nama
                        row.periode    = periode
                        row.posted     = 0
                        row.disabled   = 0
                        row.is_skpd    = 1
                        row.jv_type    = 2
                        row.source     = "SP2D-%s" % tipe
                        row.source_no  = kode
                        row.tgl_source = tanggal
                        row.tanggal    = datetime.now()
                        row.tgl_transaksi = datetime.now()
                        
                        if not row.kode:
                            tahun    = self.session['tahun']
                            unit_kd  = self.session['unit_kd']
                            is_skpd  = row.is_skpd
                            tipe     = AkJurnal.get_tipe(row.jv_type)
                            no_urut  = AkJurnal.get_norut(row.tahun_id,row.unit_id)+1
                            no       = "0000%d" % no_urut
                            nomor    = no[-5:]     
                            row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                        
                        DBSession.add(row)
                        DBSession.flush()
                        
                        #Tambah ke Item Jurnal PPKD
                        jui   = row.id
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   APInvoiceItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).filter(Sp2d.id==id_sp2d,
                                                   Spm.id==Sp2d.ap_spm_id,
                                                   Spp.id==Spm.ap_spp_id,
                                                   SppItem.ap_spp_id==Spp.id,
                                                   SppItem.ap_invoice_id==APInvoice.id,
                                                   APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                                   APInvoiceItem.ap_invoice_id==APInvoice.id,
                                                   APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.db_lra_sap_id==Sap.id
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   APInvoiceItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).all()
                        
                        for row in rows:                    
                            ji1 = AkJurnalItem()
                            ji1.ak_jurnal_id = "%d" % jui
                            ji1.kegiatan_sub_id = row.kegiatan_sub_id1
                            ji1.rekening_id  = row.rek
                            ji1.sap_id       = row.sap1
                            ji1.amount       = row.nilai2
                            ji1.notes        = ""
                            DBSession.add(ji1)
                            DBSession.flush()
                        
                        rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   APInvoiceItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).filter(Sp2d.id==id_sp2d,
                                                   Spm.id==Sp2d.ap_spm_id,
                                                   Spp.id==Spm.ap_spp_id,
                                                   SppItem.ap_spp_id==Spp.id,
                                                   SppItem.ap_invoice_id==APInvoice.id,
                                                   APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                                   APInvoiceItem.ap_invoice_id==APInvoice.id,
                                                   APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                                   KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                                   RekeningSap.rekening_id==Rekening.id,
                                                   RekeningSap.db_lra_sap_id==Sap.id
                                            ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                                   Sap.nama.label('nama1'),
                                                   KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                                   Spp.nominal.label('nilai1'),
                                                   APInvoiceItem.amount.label('nilai2'),
                                                   RekeningSap.db_lra_sap_id.label('sap1'),
                                                   RekeningSap.kr_lra_sap_id.label('sap2'),
                                                   Rekening.id.label('rek'),
                                            ).first()
                        
                        ji2 = AkJurnalItem()
                        ji2.ak_jurnal_id = "%d" % jui
                        ji2.kegiatan_sub_id = 0
                        ji2.rekening_id  = 0
                        s=DBSession.query(Sap.id).filter(Sap.kode=='0.0.0.00.00').first()
                        ji2.sap_id       = s
                        n = rows.nilai1
                        ji2.amount       = n * -1
                        ji2.notes        = ""
                        DBSession.add(ji2)
                        DBSession.flush()
                
            return self.route_list()
        return dict(row=row, form=form.render()) 

    #############
    # UnPosting #
    #############   
    def save_request4(self, row=None):
        row = Sp2d()
        self.request.session.flash('SP2D sudah di Unposting jurnal.')
        return row
        
    @view_config(route_name='ak-sp2d-unposting', renderer='templates/ak-sp2d/unposting.pt',
                 permission='unposting') 
    def view_edit_unposting(self):
        request = self.request
        row     = self.query_id().first()
        id_sp2d = row.id
        kode    = row.kode
        
        if not row:
            return id_not_found(request)
        if not row.posted:
            request.session.flash('Data tidak dapat di Unposting jurnal, karena belum diposting jurnal.', 'error')
            return self.route_list()
        if row.disabled:
            request.session.flash('Data jurnal SP2D sudah diposting.', 'error')
            return self.route_list()
            
        form = Form(colander.Schema(), buttons=('un-jurnal','cancel'))
        
        if request.POST:
            if 'un-jurnal' in request.POST: 
            
                #Update status posted pada SP2D
                row.posted=0
                self.save_request4(row)
                
                ji = DBSession.query(Spp.jenis.label('jenis'))\
                             .filter(Sp2d.id==id_sp2d,
                                     Sp2d.ap_spm_id==Spm.id,
                                     Spm.ap_spp_id==Spp.id,
                             ).first()
                j = '%s' % ji
                if j=='1':
                    s='UP'
                    x='SP2D-%s' % s
                elif j=='2':
                    s='TU'
                    x='SP2D-%s' % s
                elif j=='3':
                    s='GU'
                    x='SP2D-%s' % s
                else:
                    s='LS'
                    x='SP2D-%s' % s
                    
                r = DBSession.query(AkJurnal.id.label('di')).filter(AkJurnal.source_no==kode, AkJurnal.source==x).all()
                for row in r:
                    #Menghapus Item Jurnal
                    DBSession.query(AkJurnalItem).filter(AkJurnalItem.ak_jurnal_id==row.di).delete()
                    DBSession.flush()
                
                #Menghapus SP2D yang sudah menjadi jurnal
                DBSession.query(AkJurnal).filter(AkJurnal.source_no==kode,AkJurnal.source==x).delete()
                DBSession.flush()
                
            return self.route_list()
        return dict(row=row, form=form.render())    
