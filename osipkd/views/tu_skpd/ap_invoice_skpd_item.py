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
from osipkd.models.apbd_tu import APInvoice, APInvoiceItem 
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah ap-invoice-skpd-item gagal'
SESS_EDIT_FAILED = 'Edit ap-invoice-skpd-item gagal'

class view_ap_invoice_skpd_item(BaseViews):
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='ap-invoice-skpd-item-act', renderer='json',
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
                ap_invoice_id = url_dict['ap_invoice_id'].isdigit() and url_dict['ap_invoice_id'] or 0
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('kode_rek'))
                columns.append(ColumnDT('amount',filter=self._number_format))
                columns.append(ColumnDT('ppn',filter=self._number_format))
                columns.append(ColumnDT('pph',filter=self._number_format))
                columns.append(ColumnDT('vol_1'))
                columns.append(ColumnDT('vol_2'))
                columns.append(ColumnDT('harga'))
                columns.append(ColumnDT('nama_kegiatan'))
                columns.append(ColumnDT('kegiatan_item_id'))
                columns.append(ColumnDT('nilai'))
                
                query = DBSession.query(APInvoiceItem.id,
                                        APInvoiceItem.no_urut,
                                        APInvoiceItem.nama,
                                        Rekening.kode.label('kode_rek'),
                                        APInvoiceItem.amount,
                                        APInvoiceItem.ppn,
                                        APInvoiceItem.pph,
                                        APInvoiceItem.vol_1,
                                        APInvoiceItem.vol_2,
                                        APInvoiceItem.harga,
                                        KegiatanItem.nama.label('nama_kegiatan'),
                                        APInvoiceItem.kegiatan_item_id,
                                        cast(KegiatanItem.hsat_4*KegiatanItem.vol_4_1*KegiatanItem.vol_4_2,BigInteger).label('nilai')).\
                                  join(KegiatanItem).\
                                  outerjoin(Rekening).\
                                  filter(APInvoiceItem.ap_invoice_id==ap_invoice_id)
                rowTable = DataTables(req, APInvoiceItem, query, columns)
                return rowTable.output_result()
#######    
# Add #
#######
@view_config(route_name='ap-invoice-skpd-item-add', renderer='json',
             permission='add')
def view_add(request):
    req = request
    ses = req.session
    params = req.params
    url_dict = req.matchdict
    ap_invoice_id = 'ap_invoice_id' in url_dict and url_dict['ap_invoice_id'] or 0
    controls = dict(request.POST.items())
    
    ap_invoice_item_id = 'ap_invoice_item_id' in controls and controls['ap_invoice_item_id'] or 0
    #Cek dulu ada penyusup gak dengan mengecek sessionnya
    ap_invoice = DBSession.query(APInvoice)\
                  .filter(APInvoice.unit_id==ses['unit_id'],
                          APInvoice.id==ap_invoice_id).first()
    if not ap_invoice:
        return {"success": False, 'msg':'Invoice tidak ditemukan'}
    
    #Cek lagi ditakutkan skpd ada yang iseng inject script
    if ap_invoice_item_id:
        row = DBSession.query(APInvoiceItem)\
                  .join(APInvoice)\
                  .filter(APInvoiceItem.id==ap_invoice_item_id,
                          APInvoice.unit_id==ses['unit_id'],
                          APInvoiceItem.ap_invoice_id==ap_invoice_id).first()
        if not row:
            return {"success": False, 'msg':'Invoice tidak ditemukan'}
    else:
        row = APInvoiceItem()
            
    row.ap_invoice_id    = ap_invoice_id
    row.kegiatan_item_id = controls['kegiatan_item_id']
    if not controls['no_urut1'] or controls['no_urut1'].split()=='':
        controls['no_urut1'] = APInvoiceItem.max_no_urut(ap_invoice_id)+1
    row.no_urut          = controls['no_urut1']
    row.nama             = controls['nama']
    row.vol_1            = controls['vol_1'].replace('.','')
    row.vol_2            = controls['vol_2'].replace('.','')
    row.harga            = controls['harga'].replace('.','')
    row.ppn              = controls['ppn'].replace('.','')
    row.pph              = controls['pph'].replace('.','')
    row.amount           = float(controls['vol_1'].replace('.',''))*float(controls['vol_2'].replace('.',''))*float(controls['harga'].replace('.',''))
    
    DBSession.add(row)
    DBSession.flush()
    amount = "%d" % APInvoice.get_nilai(row.ap_invoice_id) 
    return {"success": True, 'id': row.id, "msg":'Success Tambah Item Invoice', 'jml_total':amount}

########
# Edit #
########
def route_list(request):
    return HTTPFound(location=request.route_url('ap-invoice-skpd'))
    
def query_id(request):
    return DBSession.query(APInvoiceItem).filter(APInvoiceItem.id==request.matchdict['id'],
                                                 APInvoiceItem.ap_invoice_id==request.matchdict['ap_invoice_id'])
    
def id_not_found(request):    
    msg = 'User ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

@view_config(route_name='ap-invoice-skpd-item-edit', renderer='json',
             permission='edit')
def view_edit(request):
    row = query_id(request).first()
    if not row:
        return id_not_found(request)
    form = get_form(request, EditSchema)
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items()
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
    values['kegiatan_nm']=row.kegiatan_subs.nama
    values['kegiatan_kd']=row.kegiatan_subs.kode
    form.set_appstruct(values) 
    return dict(form=form)

##########
# Delete #
##########    
@view_config(route_name='ap-invoice-skpd-item-delete', renderer='json',
             permission='delete')
def view_delete(request):
    q = query_id(request)
    row = q.first()
    
    if not row:
        return {'success':False, "msg":self.id_not_found()}

    msg = 'Data sudah dihapus'
    query_id(request).delete()
    DBSession.flush()
    
    amount = "%s" % APInvoice.get_nilai(row.ap_invoice_id) 
    return {'success':True, "msg":msg, 'jml_total':amount}