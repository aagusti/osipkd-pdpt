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

SESS_ADD_FAILED = 'Tambah ar-sts-ppkd-item gagal'
SESS_EDIT_FAILED = 'Edit ar-sts-ppkd-item gagal'

class view_ar_sts_ppkd_item(BaseViews):     
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='ar-sts-ppkd-item-act', renderer='json',
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
