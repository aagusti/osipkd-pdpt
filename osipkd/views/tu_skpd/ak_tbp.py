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
from osipkd.models.apbd import ARPaymentItem
from osipkd.models.pemda_model import Unit, Rekening, Sap, RekeningSap
from osipkd.models.apbd_tu import AkJurnal, AkJurnalItem
from osipkd.models.apbd_anggaran import Kegiatan, KegiatanSub, KegiatanItem
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews
    

SESS_ADD_FAILED = 'Tambah ak-tbp gagal'
SESS_EDIT_FAILED = 'Edit ak-tbp gagal'

def deferred_sumber_id(node, kw):
    values = kw.get('sumber_id', [])
    return widget.SelectWidget(values=values)
    
SUMBER_ID = (
    (1, 'Manual'),
    (2, 'PBB'),
    (3, 'BPHTB'),
    (4, 'PADL'))
    
class view_ar_payment_item(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='ak-tbp', renderer='templates/ak-tbp/list.pt',
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
    @view_config(route_name='ak-tbp-act', renderer='json',
                 permission='read')
    def ar_payment_item_act(self):
        ses = self.request.session
        req = self.request
        params   = req.params
        url_dict = req.matchdict
        
        kegiatan_sub_id = 'kegiatan_sub_id' in params and params['kegiatan_sub_id'] or 0
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('kode'))
            columns.append(ColumnDT('nama'))
            columns.append(ColumnDT('ref_kode'))
            columns.append(ColumnDT('ref_nama'))
            columns.append(ColumnDT('tanggal', filter=self._DTstrftime))
            columns.append(ColumnDT('amount',  filter=self._number_format))
            columns.append(ColumnDT('posted'))           
            query = DBSession.query(ARPaymentItem).filter(ARPaymentItem.tahun == ses['tahun'],
                                                          ARPaymentItem.unit_id == ses['unit_id'],
                                                          ARPaymentItem.tanggal == ses['tanggal'],
                                                          )
            rowTable = DataTables(req, ARPaymentItem, query, columns)
            return rowTable.output_result()
        
    def route_list(self):
        return HTTPFound(location=self.request.route_url('ak-tbp') )
        
    def session_failed(self, session_name):
        del self.session[session_name]
        
    def query_id(self):
        return DBSession.query(ARPaymentItem).filter_by(id=self.request.matchdict['id'])
        
    def id_not_found(self):    
        msg = 'TBP ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()
        
    ###########
    # Posting #
    ###########     
    def save_request2(self, row=None):
        row = ARPaymentItem()
        self.request.session.flash('TBP sudah diposting dan dibuat Jurnalnya.')
        return row
        
    @view_config(route_name='ak-tbp-posting', renderer='templates/ak-tbp/posting.pt',
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
                
                row = AkJurnal()
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
                    ji = AkJurnalItem()
                    
                    ji.ak_jurnal_id = "%d" % jui
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
                    ji2 = AkJurnalItem()
                    
                    ji2.ak_jurnal_id = "%d" % jui
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
                
                row = AkJurnal()
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
                    ji3 = AkJurnalItem()
                    
                    ji3.ak_jurnal_id = "%d" % jui
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
                    ji4 = AkJurnalItem()
                    
                    ji4.ak_jurnal_id = "%d" % jui
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
        
    @view_config(route_name='ak-tbp-unposting', renderer='templates/ak-tbp/unposting.pt',
                 permission='unposting') 
    def view_edit_unposting(self):
        request = self.request
        row     = self.query_id().first()
        kode    = row.ref_kode
        
        if not row:
            return id_not_found(request)
        if not row.posted:
            request.session.flash('Data tidak dapat di Unposting jurnal, karena belum diposting jurnal.', 'error')
            return self.route_list()
        if row.disabled:
            request.session.flash('Data jurnal TBP sudah diposting.', 'error')
            return self.route_list()
            
        form = Form(colander.Schema(), buttons=('un-jurnal','cancel'))
        
        if request.POST:
            if 'un-jurnal' in request.POST: 
            
                #Update status posted pada TBP
                row.posted=0
                self.save_request4(row)
                
                r = DBSession.query(AkJurnal.id.label('di')).filter(AkJurnal.source_no==row.ref_kode,AkJurnal.source=='TBP').all()
                for row in r:
                    #Menghapus Item Jurnal
                    DBSession.query(AkJurnalItem).filter(AkJurnalItem.ak_jurnal_id==row.di).delete()
                    DBSession.flush()
                
                #Menghapus TBP yang sudah menjadi jurnal
                DBSession.query(AkJurnal).filter(AkJurnal.source_no==kode,AkJurnal.source=='TBP').delete()
                DBSession.flush()
                
            return self.route_list()
        return dict(row=row, form=form.render())    

