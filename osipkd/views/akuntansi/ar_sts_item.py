import os
import uuid
from osipkd.tools import row2dict, xls_reader
from datetime import datetime
from sqlalchemy import not_, func, cast, BigInteger
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from osipkd.models import DBSession
from osipkd.models.apbd_anggaran import Kegiatan, KegiatanSub, KegiatanItem
from osipkd.models.pemda_model import Unit, Rekening
from osipkd.models.apbd_tu import Sts, StsItem
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah Item gagal'
SESS_EDIT_FAILED = 'Edit Item gagal'

class view_ar_sts_item(BaseViews):     
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='ar-payment-sts-item-act', renderer='json',
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
                ar_sts_id = url_dict['ar_sts_id'].isdigit() and url_dict['ar_sts_id'] or 0
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kegiatan_item_id'))
                columns.append(ColumnDT('kode1'))
                columns.append(ColumnDT('no_urut1'))
                columns.append(ColumnDT('kode_rek'))
                columns.append(ColumnDT('nama_rek'))
                columns.append(ColumnDT('amount'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nilai1'))

                query = DBSession.query(StsItem.id,
                                        StsItem.kegiatan_item_id,
                                        Kegiatan.kode.label('kode1'),
                                        KegiatanSub.no_urut.label('no_urut1'),
                                        Rekening.kode.label('kode_rek'),
                                        Rekening.nama.label('nama_rek'),
                                        StsItem.amount.label('amount'),
                                        KegiatanSub.nama.label('nama'),
                                        cast(KegiatanItem.hsat_4*KegiatanItem.vol_4_1*KegiatanItem.vol_4_2,BigInteger).label('nilai1'),
                          ).join(KegiatanItem
                          ).outerjoin(KegiatanSub, Rekening, Kegiatan
                          ).filter(StsItem.ar_sts_id==ar_sts_id,
                                   StsItem.kegiatan_item_id==KegiatanItem.id,
                                   KegiatanItem.kegiatan_sub_id==KegiatanSub.id,
                                   KegiatanItem.rekening_id==Rekening.id,
                                   KegiatanSub.kegiatan_id==Kegiatan.id,
                          ).group_by(StsItem.id,
                                     StsItem.kegiatan_item_id,
                                     Kegiatan.kode.label('kode1'),
                                     KegiatanSub.no_urut.label('no_urut1'),
                                     Rekening.kode.label('kode_rek'),
                                     Rekening.nama.label('nama_rek'),
                                     StsItem.amount.label('amount'),
                                     KegiatanSub.nama.label('nama'),
                                     cast(KegiatanItem.hsat_4*KegiatanItem.vol_4_1*KegiatanItem.vol_4_2,BigInteger).label('nilai1'))
                rowTable = DataTables(req, StsItem, query, columns)
                return rowTable.output_result()
                
    #######    
    # Add #
    #######
    @view_config(route_name='ar-payment-sts-item-add', renderer='json',
                 permission='add')
    def view_add_update(self):
        req = self.request
        ses = req.session
        params   = req.params
        url_dict = req.matchdict
        ar_sts_id = 'ar_sts_id' in url_dict and url_dict['ar_sts_id'] or 0
        controls = dict(req.POST.items())
        
        #Cek dulu ada penyusup gak dengan mengecek sessionnya
        ar_sts = DBSession.query(Sts)\
                      .filter(Sts.unit_id==ses['unit_id'],
                              Sts.id==ar_sts_id).first()
        if not ar_sts:
            return {"success": False, 'msg':'STS tidak ditemukan'}
        
        ar_sts_item_id = 'ar_sts_item_id' in controls and controls['ar_sts_item_id'] or 0
        #JIKA ar_sts_item_id = None maka tambah
        if ar_sts_item_id:
            #Cek lagi ditakutkan skpd ada yang iseng inject script
            row = DBSession.query(StsItem)\
                      .join(Sts)\
                      .filter(StsItem.id==ar_sts_item_id,
                              Sts.unit_id==ses['unit_id'],
                              StsItem.ar_sts_id==ar_sts_id).first()
            if not row:
                return {"success": False, 'msg':'STS tidak ditemukan'}
        else:
            row = StsItem()
                
        row.ar_sts_id        = ar_sts_id
        row.kegiatan_item_id = controls['kegiatan_item_id']
        row.amount           = controls['amount'].replace('.','')
        
        DBSession.add(row)
        DBSession.flush()
        nilai = "%d" % Sts.get_nilai(row.ar_sts_id) 
        return {"success": True, 'id': row.id, "msg":'Success Tambah Item STS', 'jml_total':nilai}

    ########
    # Edit #
    ########
    def query_id(self):
        request = self.request
        return DBSession.query(StsItem).\
                   filter(StsItem.id==request.matchdict['id'],
                          StsItem.ar_sts_id==request.matchdict['ar_sts_id'])
        
    def id_not_found(self):
        request = self.request
        msg = 'User ID %s not found.' % request.matchdict['id']
        request.session.flash(msg, 'error')
        return self.route_list()
    ##########
    # Delete #
    ##########    
    @view_config(route_name='ar-payment-sts-item-delete', renderer='json',
                 permission='delete')
    def view_delete(self):
        request = self.request
        q = self.query_id()
        row = q.first()
        if not row:
            return {'success':False, "msg":self.id_not_found()}

        msg = 'Data sudah dihapus'
        self.query_id().delete()
        DBSession.flush()
        nilai = "%s" % Sts.get_nilai(row.ar_sts_id) 
        return {'success':True, "msg":msg, 'jml_total':nilai}