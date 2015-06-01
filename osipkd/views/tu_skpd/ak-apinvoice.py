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
from osipkd.models.apbd_tu import APInvoice, APInvoiceItem, SppItem, Spp, AkJurnal, AkJurnalItem
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah ak-apinvoice gagal'
SESS_EDIT_FAILED = 'Edit ak-apinvoice gagal'

def deferred_ap_type(node, kw):
    values = kw.get('ap_type', [])
    return widget.SelectWidget(values=values)
    
AP_TYPE = (
    ('1', 'UP'),
    ('2', 'TU'),
    ('3', 'GU'),
    ('4', 'LS'),
    )

def deferred_kontrak_type(node, kw):
    values = kw.get('kontrak_type', [])
    return widget.SelectWidget(values=values)
    
KONTRAK_TYPE = (
    ('1', 'PT / NV'),
    ('2', 'CV'),
    ('3', 'FIRMA'),
    ('4', 'Lain-lain'),
    )
    
class view_ap_invoice_skpd(BaseViews):

    @view_config(route_name="ak-apinvoice", renderer="templates/ak-apinvoice/list.pt")
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
    @view_config(route_name='ak-apinvoice-act', renderer='json',
                 permission='read')
    def view_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        if url_dict['act']=='grid':
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if url_dict['act']=='grid':
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('jenis'))
                columns.append(ColumnDT('tanggal', filter=self._DTstrftime))
                columns.append(ColumnDT('kegiatan_sub_nm'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('amount'))
                columns.append(ColumnDT('posted'))
                columns.append(ColumnDT('status_spp'))

                query = DBSession.query(APInvoice.id,
                          APInvoice.kode,
                          APInvoice.jenis,                          
                          APInvoice.tanggal,
                          KegiatanSub.nama.label('kegiatan_sub_nm'),
                          APInvoice.nama,
                          APInvoice.amount,
                          APInvoice.posted,
                          APInvoice.status_spp,
                        ).outerjoin(APInvoiceItem
                        ).filter(APInvoice.tahun_id==ses['tahun'],
                              APInvoice.unit_id==ses['unit_id'],
                              APInvoice.kegiatan_sub_id==KegiatanSub.id,
                        ).order_by(APInvoice.no_urut.desc()
                        ).group_by(APInvoice.id,
                          APInvoice.kode,
                          APInvoice.jenis,
                          APInvoice.tanggal,
                          KegiatanSub.nama.label('kegiatan_sub_nm'),
                          APInvoice.nama,
                          APInvoice.amount,
                          APInvoice.posted,
                          APInvoice.status_spp,
                        )
                rowTable = DataTables(req, APInvoice, query, columns)
                return rowTable.output_result()
        
def route_list(request):
    return HTTPFound(location=request.route_url('ak-apinvoice'))
    
def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r
    
def query_id(request):
    return DBSession.query(APInvoice).filter(APInvoice.id==request.matchdict['id'])
    
def id_not_found(request):    
    msg = 'User ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

###########
# Posting #
###########     
def save_request2(request, row=None):
    row = APInvoice()
    request.session.flash('Tagihan sudah diposting dan dibuat Jurnalnya.')
    return row
    
@view_config(route_name='ak-apinvoice-posting', renderer='templates/ak-apinvoice/posting.pt',
             permission='posting')
def view_edit_posting(request):
    row    = query_id(request).first()
    id_inv = row.id
    gi     = row.jenis
    g      = '%s' % gi
    keg    = row.kegiatan_sub_id
    nam    = row.nama
    kod    = row.kode
    tgl    = row.tanggal
    
    if not row:
        return id_not_found(request)
    if g == 1: 
        request.session.flash('Data tidak dapat diposting, karena bukan tipe GU / LS.', 'error')
        return route_list(request)
    if g == 2: 
        request.session.flash('Data tidak dapat diposting, karena bukan tipe GU / LS.', 'error')
        return route_list(request)
    if not row.amount:
        request.session.flash('Data tidak dapat diposting, karena bernilai 0.', 'error')
        return route_list(request)
    if row.posted:
        request.session.flash('Data sudah diposting jurnal', 'error')
        return route_list(request)
        
    form = Form(colander.Schema(), buttons=('jurnal','cancel'))
    
    if request.POST:
        if 'jurnal' in request.POST: 
            #Update posted pada APInvoice
            row.posted=1
            save_request2(request, row)
            
            gi = row.jenis
            g  = '%s' % gi
            if g == '4':
                xa1 = DBSession.query(Kegiatan.id).filter(KegiatanSub.id==keg,KegiatanSub.kegiatan_id==Kegiatan.id,).first()
                xa  = '%s' % xa1 
                if xa == '2':
                    #Tambah LS Gaji ke Jurnal SKPD
                    nama    = nam
                    kode    = kod
                    tanggal = tgl
                    tipe    = APInvoice.get_tipe(id_inv)
                    periode = APInvoice.get_periode(id_inv)
                    
                    row = AkJurnal()
                    row.created    = datetime.now()
                    row.create_uid = request.user.id
                    row.updated    = datetime.now()
                    row.update_uid = request.user.id
                    row.tahun_id   = request.session['tahun']
                    row.unit_id    = request.session['unit_id']
                    row.nama       = "Dibayar Tagihan %s" % tipe + " %s" % nama
                    row.notes      = nama
                    row.periode    = periode
                    row.posted     = 0
                    row.disabled   = 0
                    row.is_skpd    = 1
                    row.jv_type    = 2
                    row.source     = "Tagihan-%s" % tipe
                    row.source_no  = kode
                    row.tgl_source = tanggal
                    row.tanggal    = datetime.now()
                    row.tgl_transaksi = datetime.now()
                    
                    if not row.kode:
                        tahun    = request.session['tahun']
                        unit_kd  = request.session['unit_kd']
                        is_skpd  = row.is_skpd
                        tipe     = AkJurnal.get_tipe(row.jv_type)
                        no_urut  = AkJurnal.get_norut(row.tahun_id,row.unit_id)+1
                        no       = "0000%d" % no_urut
                        nomor    = no[-5:]     
                        row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                    
                    DBSession.add(row)
                    DBSession.flush()
                    
                    jui   = row.id
                    rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                           Sap.nama.label('nama1'),
                                           KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                           APInvoiceItem.amount.label('nilai1'),
                                           APInvoiceItem.ap_invoice_id.label('inv'),
                                           RekeningSap.db_lo_sap_id.label('sap1'),
                                           Rekening.id.label('rek'),
                                    ).join(KegiatanSub, APInvoiceItem 
                                    ).filter(APInvoice.id==id_inv,
                                             APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                             APInvoiceItem.ap_invoice_id==APInvoice.id,
                                             APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                             KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                             KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                             RekeningSap.rekening_id==Rekening.id,
                                             RekeningSap.db_lo_sap_id==Sap.id
                                    ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               APInvoiceItem.amount.label('nilai1'),
                                               APInvoiceItem.ap_invoice_id.label('inv'),
                                               RekeningSap.db_lo_sap_id.label('sap1'),
                                               Rekening.id.label('rek'),
                                    ).all()
                    
                    n=0
                    for row in rows:
                        ji = AkJurnalItem()
                        
                        ji.ak_jurnal_id = "%d" % jui
                        ji.kegiatan_sub_id = row.kegiatan_sub_id1
                        ji.rekening_id  = row.rek
                        ji.sap_id       = row.sap1
                        ji.amount       = row.nilai1
                        ji.notes        = ""
                        n = n + 1
                        
                        DBSession.add(ji)
                        DBSession.flush()
                    
                    rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                           Sap.nama.label('nama1'),
                                           KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                           APInvoice.amount.label('nilai1'),
                                           RekeningSap.kr_lo_sap_id.label('sap2'),
                                    ).join(KegiatanSub, APInvoiceItem 
                                    ).filter(APInvoice.id==id_inv,
                                             APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                             APInvoiceItem.ap_invoice_id==APInvoice.id,
                                             APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                             KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                             KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                             RekeningSap.rekening_id==Rekening.id,
                                             RekeningSap.kr_lo_sap_id==Sap.id
                                    ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                               Sap.nama.label('nama1'),
                                               KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                               APInvoice.amount.label('nilai1'),
                                               APInvoiceItem.ap_invoice_id.label('inv'),
                                               RekeningSap.kr_lo_sap_id.label('sap2'),
                                    ).first()
                                    
                    ji2 = AkJurnalItem()
                    
                    ji2.ak_jurnal_id = "%d" % jui
                    ji2.kegiatan_sub_id = 0
                    ji2.rekening_id  = 0
                    ji2.notes        = ""
                    
                    x=rows.nilai1
                    ji2.amount       = x * -1
                    
                    s=DBSession.query(Sap.id).filter(Sap.kode=='3.1.3.01.01').first()
                    ji2.sap_id       = s
                    
                    DBSession.add(ji2)
                    DBSession.flush()
                            
            else:      
                #Tambah ke Jurnal SKPD
                nama    = nam
                kode    = kod
                tanggal = tgl
                tipe    = APInvoice.get_tipe(id_inv)
                periode = APInvoice.get_periode(id_inv)
                
                row = AkJurnal()
                row.created    = datetime.now()
                row.create_uid = request.user.id
                row.updated    = datetime.now()
                row.update_uid = request.user.id
                row.tahun_id   = request.session['tahun']
                row.unit_id    = request.session['unit_id']
                row.nama       = "Dibayar Tagihan %s" % tipe + " %s" % nama
                row.notes      = nama
                row.periode    = periode
                row.posted     = 0
                row.disabled   = 0
                row.is_skpd    = 1
                row.jv_type    = 2
                row.source     = "Tagihan-%s" % tipe
                row.source_no  = kode
                row.tgl_source = tanggal
                row.tanggal    = datetime.now()
                row.tgl_transaksi = datetime.now()
                
                if not row.kode:
                    tahun    = request.session['tahun']
                    unit_kd  = request.session['unit_kd']
                    is_skpd  = row.is_skpd
                    tipe     = AkJurnal.get_tipe(row.jv_type)
                    no_urut  = AkJurnal.get_norut(row.tahun_id,row.unit_id)+1
                    no       = "0000%d" % no_urut
                    nomor    = no[-5:]     
                    row.kode = "%d" % tahun + "-%s" % is_skpd + "-%s" % unit_kd + "-%s" % tipe + "-%s" % nomor
                
                DBSession.add(row)
                DBSession.flush()
                
                jui   = row.id
                rows = DBSession.query(KegiatanItem.rekening_id.label('rekening_id1'),
                                       Sap.nama.label('nama1'),
                                       KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                       APInvoiceItem.amount.label('nilai1'),
                                       APInvoiceItem.ap_invoice_id.label('inv'),
                                       RekeningSap.kr_lo_sap_id.label('sap2'),
                                       RekeningSap.db_lo_sap_id.label('sap1'),
                                       Rekening.id.label('rek'),
                                ).join(KegiatanSub, APInvoiceItem 
                                ).filter(APInvoice.id==id_inv,
                                         APInvoice.kegiatan_sub_id==KegiatanSub.id,
                                         APInvoiceItem.ap_invoice_id==APInvoice.id,
                                         APInvoiceItem.kegiatan_item_id==KegiatanItem.id,
                                         KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                         KegiatanItem.rekening_id==RekeningSap.rekening_id,
                                         RekeningSap.rekening_id==Rekening.id,
                                         RekeningSap.db_lo_sap_id==Sap.id
                                ).group_by(KegiatanItem.rekening_id.label('rekening_id1'),
                                           Sap.nama.label('nama1'),
                                           KegiatanItem.kegiatan_sub_id.label('kegiatan_sub_id1'),
                                           APInvoiceItem.amount.label('nilai1'),
                                           APInvoiceItem.ap_invoice_id.label('inv'),
                                           RekeningSap.kr_lo_sap_id.label('sap2'),
                                           RekeningSap.db_lo_sap_id.label('sap1'),
                                           Rekening.id.label('rek'),
                                ).all()
                
                n=0
                for row in rows:
                    ji = AkJurnalItem()
                    
                    ji.ak_jurnal_id = "%d" % jui
                    ji.kegiatan_sub_id = row.kegiatan_sub_id1
                    ji.rekening_id  = row.rek
                    ji.sap_id       = row.sap1
                    ji.amount       = row.nilai1
                    ji.notes        = ""
                    n = n + 1
                    
                    DBSession.add(ji)
                    DBSession.flush()
                
                for row in rows:
                    ji2 = AkJurnalItem()
                    ji2.ak_jurnal_id = "%d" % jui
                    ji2.kegiatan_sub_id = row.kegiatan_sub_id1
                    ji2.rekening_id  = row.rek
                    ji2.sap_id       = row.sap2
                    ji2.notes        = ""
                    x1=row.nilai1
                    ji2.amount       = x1 * -1
                    DBSession.add(ji2)
                    DBSession.flush()
                    
        return route_list(request)
    return dict(row=row, form=form.render())    
    
#############
# UnPosting #
#############   
def save_request3(request, row=None):
    row = APInvoice()
    request.session.flash('Tagihan sudah di Unposting jurnal.')
    return row
    
@view_config(route_name='ak-apinvoice-unposting', renderer='templates/ak-apinvoice/unposting.pt',
             permission='unposting') 
def view_edit_unposting(request):
    row = query_id(request).first()
    
    if not row:
        return id_not_found(request)
    if not row.posted:
        request.session.flash('Data tidak dapat di Unposting jurnal, karena belum diposting jurnal.', 'error')
        return route_list(request)
    if row.disabled:
        request.session.flash('Data jurnal Tagihan sudah diposting jurnal.', 'error')
        return route_list(request)
        
    form = Form(colander.Schema(), buttons=('un-jurnal','cancel'))
    
    if request.POST:
        if 'un-jurnal' in request.POST: 
        
            #Update status posted pada UTANG
            row.posted=0
            save_request3(request, row)
            
            ji = row.jenis
            j  = '%s' % ji
            if j=='3':
                s='GU'
                x='Tagihan-%s' % s
            if j=='4':
                s='LS'
                x='Tagihan-%s' % s
                
            r = DBSession.query(AkJurnal.id).filter(AkJurnal.source_no==row.kode,AkJurnal.source==x).first()
            #Menghapus Item Jurnal
            DBSession.query(AkJurnalItem).filter(AkJurnalItem.ak_jurnal_id==r).delete()
            DBSession.flush()
                
            #Menghapus UTANG yang sudah menjadi jurnal
            DBSession.query(AkJurnal).filter(AkJurnal.source_no==row.kode,AkJurnal.source==x).delete()
            DBSession.flush()
            
        return route_list(request)
    return dict(row=row, form=form.render())
    
      