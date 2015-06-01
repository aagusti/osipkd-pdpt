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
from osipkd.models.apbd_tu import APInvoice, Spp, SppItem
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah ap-spp-item gagal'
SESS_EDIT_FAILED = 'Edit ap-spp-item gagal'

class view_ap_spp_item(BaseViews):
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='ap-spp-item-act', renderer='json',
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
                ap_spp_id = url_dict['ap_spp_id'].isdigit() and url_dict['ap_spp_id'] or 0
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('ap_invoice_id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('jenis'))
                columns.append(ColumnDT('tanggal'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('amount',filter=self._number_format))
                columns.append(ColumnDT('nbku'))
                columns.append(ColumnDT('tbku'))
                
                query = DBSession.query(SppItem.id,
                                        SppItem.ap_invoice_id,
                                        APInvoice.kode.label('kode'),
                                        APInvoice.jenis.label('jenis'),
                                        APInvoice.tanggal.label('tanggal'),
                                        APInvoice.nama.label('nama'),
                                        APInvoice.amount.label('amount'),
                                        APInvoice.no_bku.label('nbku'),
                                        APInvoice.tgl_bku.label('tbku'),
                          ).join(APInvoice
                          ).filter(SppItem.ap_spp_id==ap_spp_id
                          ).group_by(SppItem.id, 
                                     SppItem.ap_invoice_id,
                                     APInvoice.kode.label('kode'),
                                     APInvoice.jenis.label('jenis'),
                                     APInvoice.tanggal.label('tanggal'),
                                     APInvoice.nama.label('nama'),
                                     APInvoice.amount.label('amount'),
                                     APInvoice.no_bku.label('nbku'),
                                     APInvoice.tgl_bku.label('tbku'))
                rowTable = DataTables(req, SppItem, query, columns)
                return rowTable.output_result()
#######    
# Add #
#######
def save_request2(row=None):
    row = APInvoice()
    return row

def route_list(request):
    return HTTPFound(location=request.route_url('ap-spp'))
        
@view_config(route_name='ap-spp-item-add', renderer='json',
             permission='add')
def view_add(request):
    req = request
    ses = req.session
    params = req.params
    url_dict = req.matchdict
    ap_spp_id = 'ap_spp_id' in url_dict and url_dict['ap_spp_id'] or 0
    controls = dict(request.POST.items())
    
    ap_spp_item_id = 'ap_spp_item_id' in controls and controls['ap_spp_item_id'] or 0
    #Cek dulu ada penyusup gak dengan mengecek sessionnya
    ap_spp = DBSession.query(Spp)\
                  .filter(Spp.unit_id==ses['unit_id'],
                          Spp.id==ap_spp_id).first()
    if not ap_spp:
        return {"success": False, 'msg':'SPP tidak ditemukan'}
    
    #Cek lagi ditakutkan skpd ada yang iseng inject script
    if ap_spp_item_id:
        row = DBSession.query(SppItem)\
                  .join(Spp)\
                  .filter(SppItem.id==ap_spp_item_id,
                          Spp.unit_id==ses['unit_id'],
                          SppItem.ap_spp_id==ap_spp_id).first()
        if not row:
            return {"success": False, 'msg':'SPP tidak ditemukan'}
    else:
        row = SppItem()
            
    row.ap_spp_id    = ap_spp_id
    row.ap_invoice_id = controls['ap_invoice_id']

    DBSession.add(row)
    DBSession.flush()
    
    amount = "%d" % Spp.get_nilai(row.ap_spp_id) 
    
    #Untuk update status posted dan status_spp pada APInvoice
    row = DBSession.query(APInvoice).filter(APInvoice.id==controls['ap_invoice_id']).first()   
    #row.disabled=1
    row.status_spp=1
    save_request2(row)

    return {"success": True, 'id': row.id, "msg":'Success Tambah Invoice', 'jml_total':amount}

########
# Edit #
########
def query_id(request):
    return DBSession.query(SppItem).filter(SppItem.id==request.matchdict['id'],
                                           SppItem.ap_spp_id==request.matchdict['ap_spp_id'])
    
def id_not_found(request):    
    msg = 'User ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

@view_config(route_name='ap-spp-item-edit', renderer='json',
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
    form.set_appstruct(values) 
    return dict(form=form)

##########
# Delete #
##########    
@view_config(route_name='ap-spp-item-delete', renderer='json',
             permission='delete')
def view_delete(request):
    q = query_id(request)
    row = q.first()
    if not row:
        return {'success':False, "msg":self.id_not_found()}

    msg = 'Data sudah dihapus'
    query_id(request).delete()
    DBSession.flush()

    amount = "%s" % Spp.get_nilai(row.ap_spp_id)

    #Untuk update status posted dan status_spp pada APInvoice    
    row = DBSession.query(APInvoice).filter(APInvoice.id==row.ap_invoice_id).first()   
    #row.disabled=0
    row.status_spp=0
    save_request2(row)
    
    return {'success':True, "msg":msg, 'jml_total':amount}\
    