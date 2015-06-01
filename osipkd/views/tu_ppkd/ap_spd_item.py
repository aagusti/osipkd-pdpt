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
from osipkd.models.apbd_tu import Spd, SpdItem
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah ap-spd-item gagal'
SESS_EDIT_FAILED = 'Edit ap-spd-item gagal'

class view_ap_spd_item(BaseViews):
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='ap-spd-item-act', renderer='json',
                 permission='read')
    def view_act(self):
        ses = self.request.session
        req = self.request
        params   = req.params
        url_dict = req.matchdict
        
        pk_id = 'id' in params and params['id'] and int(params['id']) or 0
        if url_dict['act']=='grid':
            # defining columns
            ap_spd_id = url_dict['ap_spd_id'].isdigit() and url_dict['ap_spd_id'] or 0
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('kode'))
            columns.append(ColumnDT('nama'))
            columns.append(ColumnDT('anggaran',filter=self._number_format))
            columns.append(ColumnDT('lalu',filter=self._number_format))
            columns.append(ColumnDT('nominal',filter=self._number_format))
            columns.append(ColumnDT('jumlah',filter=self._number_format))
            columns.append(ColumnDT('sisa',filter=self._number_format))
            
            query = DBSession.query(SpdItem.id,
                                    Kegiatan.kode.label('kode'),
                                    KegiatanSub.nama.label('nama'),
                                    SpdItem.anggaran,
                                    SpdItem.lalu,
                                    SpdItem.nominal,
                                    func.sum(SpdItem.nominal+SpdItem.lalu).label('jumlah'),
                                    func.sum(SpdItem.anggaran-SpdItem.nominal-SpdItem.lalu).label('sisa'),
                    ).join(Spd, KegiatanSub, Kegiatan
                    ).filter(SpdItem.ap_spd_id==Spd.id,
                             SpdItem.ap_spd_id==ap_spd_id,
                             SpdItem.kegiatan_sub_id==KegiatanSub.id,
                             KegiatanSub.kegiatan_id==Kegiatan.id,
                    ).group_by(SpdItem.id,
                               Kegiatan.kode.label('kode'),
                               KegiatanSub.nama.label('nama'),
                               SpdItem.anggaran,
                               SpdItem.lalu,
                               SpdItem.nominal,
                               SpdItem.nominal,
                               SpdItem.nominal,
                    )
            rowTable = DataTables(req, SpdItem, query, columns)
            return rowTable.output_result()
            
#######    
# Add #
#######
@view_config(route_name='ap-spd-item-add', renderer='json',
             permission='add')
def view_add(request):
    req = request
    ses = req.session
    params = req.params
    url_dict = req.matchdict
    ap_spd_id = 'ap_spd_id' in url_dict and url_dict['ap_spd_id'] or 0
    controls = dict(req.POST.items())
      
    ap_spd_item_id = 'ap_spd_item_id' in controls and controls['ap_spd_item_id'] or 0        
    #Cek dulu ada penyusup gak dengan mengecek sessionnya
    ap_spd = DBSession.query(Spd)\
                  .filter(Spd.unit_id==ses['unit_id'],
                          Spd.id==ap_spd_id).first()
    if not ap_spd:
        return {"success": False, 'msg':'SPD tidak ditemukan'}
    
    #Cek lagi ditakutkan skpd ada yang iseng inject script
    
    if ap_spd_item_id:
        row = DBSession.query(SpdItem)\
                  .join(Spd)\
                  .filter(SpdItem.id==ap_spd_item_id,
                          Spd.unit_id==ses['unit_id'],
                          SpdItem.ap_spd_id==ap_spd_id).first()
        if not row:
            return {"success": False, 'msg':'Invoice tidak ditemukan'}
    else:
        row = SpdItem()

    row.ap_spd_id       = ap_spd_id
    row.kegiatan_sub_id = controls['kegiatan_sub_id']
    row.anggaran = controls['anggaran'].replace('.','')
    row.lalu     = controls['lalu'].replace('.','')
    row.nominal  = controls['nominal'].replace('.','')

    DBSession.add(row)
    DBSession.flush()
    
    r = DBSession.query(SpdItem)\
                   .join(KegiatanSub)\
                   .outerjoin(Kegiatan)\
                   .filter(SpdItem.kegiatan_sub_id==controls['kegiatan_sub_id'],
                           SpdItem.kegiatan_sub_id==KegiatanSub.id,
                           KegiatanSub.kegiatan_id==Kegiatan.id,
                           Kegiatan.kode=='0.00.00.21')\
                   .first()   
    if r:
        bl  = "%s" % Spd.get_nilai1(row.ap_spd_id) 
        btl = "%s" % Spd.get_nilai2(row.ap_spd_id) 
    else:
        bl  = "%s" % Spd.get_nilai1(row.ap_spd_id) 
        btl = "%s" % Spd.get_nilai2(row.ap_spd_id) 
        
    return {"success": True, 'id': row.id, "msg":'Success Tambah SPD', 'jml_total1':bl, 'jml_total2':btl}

########
# Edit #
########
def query_id(request):
    return DBSession.query(SpdItem).filter(SpdItem.id==request.matchdict['id'],
                                           SpdItem.ap_spd_id==request.matchdict['ap_spd_id'])
def id_not_found(request):    
    msg = 'Item ID %s not found.' % request.matchdict['id']
    return msg

##########
# Delete #
##########    
@view_config(route_name='ap-spd-item-delete', renderer='json',
             permission='delete')
def view_delete(request):
    q   = query_id(request)
    row = q.first()
    
    if not row:
        return self.id_not_found()
        
    query_id(request).delete()
    DBSession.flush()
    
    r = DBSession.query(SpdItem)\
                   .join(KegiatanSub)\
                   .outerjoin(Kegiatan)\
                   .filter(SpdItem.kegiatan_sub_id==row.kegiatan_sub_id,
                           SpdItem.kegiatan_sub_id==KegiatanSub.id,
                           KegiatanSub.kegiatan_id==Kegiatan.id,
                           Kegiatan.kode=='0.00.00.21')\
                   .first()   
    if r:
        bl  = "%s" % Spd.get_nilai1(row.ap_spd_id) 
        btl = "%s" % Spd.get_nilai2(row.ap_spd_id) 
    else:
        bl  = "%s" % Spd.get_nilai1(row.ap_spd_id) 
        btl = "%s" % Spd.get_nilai2(row.ap_spd_id) 
        
    return {'success': True, 'msg':'Sukses Hapus Data', 'jml_total1':bl, 'jml_total2':btl}
