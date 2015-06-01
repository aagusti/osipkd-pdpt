import os
import uuid
from osipkd.tools import row2dict, xls_reader
from datetime import datetime
from sqlalchemy import not_, func, join, outerjoin
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from osipkd.models import DBSession
from osipkd.models.aset_models import AsetRuang, AsetDel, AsetDelItem, AsetKib, AsetKategori
from osipkd.models.pemda_model import Unit
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah aset-kibdel-item gagal'
SESS_EDIT_FAILED = 'Edit aset-kibdel-item gagal'

class view_aset_kibdel_item(BaseViews):
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='aset-kibdel-item-act', renderer='json',
                 permission='read')
    def view_act(self):
        ses = self.request.session
        req = self.request
        params   = req.params
        url_dict = req.matchdict

        pk_id = 'id' in params and params['id'] and int(params['id']) or 0
        if url_dict['act']=='grid':
            # defining columns
            delete_id = url_dict['delete_id'].isdigit() and url_dict['delete_id'] or 0
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('delete_id'))
            columns.append(ColumnDT('kib_id'))
            columns.append(ColumnDT('kd_kat'))
            columns.append(ColumnDT('nm_kat'))
            columns.append(ColumnDT('no_reg'))
            columns.append(ColumnDT('tanggal', filter=self._DTstrftime))
            columns.append(ColumnDT('asul'))
            columns.append(ColumnDT('urai'))
            columns.append(ColumnDT('harga',filter=self._number_format))
            columns.append(ColumnDT('alasan'))
            
            query = DBSession.query(AsetDelItem.id,
                                    AsetDelItem.delete_id,
                                    AsetDelItem.kib_id,
                                    AsetKategori.kode.label('kd_kat'),
                                    AsetKategori.uraian.label('nm_kat'),
                                    AsetKib.no_register.label('no_reg'),
                                    AsetDelItem.tanggal,
                                    AsetKib.asal_usul.label('asul'),
                                    AsetKib.uraian.label('urai'),
                                    AsetKib.harga.label('harga'),
                                    AsetDelItem.alasan,
                      ).join(AsetDel, AsetKib
                      ).outerjoin(AsetKategori
                      ).filter(AsetDelItem.delete_id==delete_id,
                               AsetDelItem.kib_id==AsetKib.id,
                               AsetKib.unit_id==Unit.id,
                               AsetKib.kategori_id==AsetKategori.id
                      ).group_by(AsetDelItem.id,
                                 AsetDelItem.delete_id,
                                 AsetDelItem.kib_id,
                                 AsetKategori.kode.label('kd_kat'),
                                 AsetKategori.uraian.label('nm_kat'),
                                 AsetKib.no_register.label('no_reg'),
                                 AsetDelItem.tanggal,
                                 AsetKib.asal_usul.label('asul'),
                                 AsetKib.uraian.label('urai'),
                                 AsetKib.harga.label('harga'),
                                 AsetDelItem.alasan,
                      )
                      
            rowTable = DataTables(req, AsetDelItem, query, columns)
            return rowTable.output_result()
            
#######    
# Add #
#######
def save_request2(row=None):
    row = AsetKib()
    return row
    
@view_config(route_name='aset-kibdel-item-add', renderer='json',
             permission='add')
def view_add(request):
    req = request
    ses = req.session
    params   = req.params
    url_dict = req.matchdict
    
    delete_id = 'delete_id' in url_dict and url_dict['delete_id'] or 0
    controls = dict(request.POST.items())
    
    kibdel_item_id = 'kibdel_item_id' in controls and controls['kibdel_item_id'] or 0
    #Cek dulu ada penyusup gak dengan mengecek sessionnya
    delete = DBSession.query(AsetDel)\
                  .filter(AsetDel.unit_id==ses['unit_id'],
                          AsetDel.id==delete_id).first()
    if not delete:
        return {"success": False, 'msg':'Penghapusan tidak ditemukan'}
    
    #Cek lagi ditakutkan skpd ada yang iseng inject script
    if kibdel_item_id:
        row = DBSession.query(AsetDelItem)\
                  .join(AsetDel)\
                  .filter(AsetDelItem.id==kibdel_item_id,
                          AsetDel.unit_id==ses['unit_id'],
                          AsetDelItem.delete_id==delete_id).first()
        if not row:
            return {"success": False, 'msg':'Penghapusan tidak ditemukan'}
    else:
        row = AsetDelItem()
            
    row.delete_id = delete_id
    row.kib_id    = controls['kib_id']
    row.tanggal   = controls['tanggal']
    row.alasan    = controls['alasan']

    DBSession.add(row)
    DBSession.flush()
    """
    nominal = "%d" % Giro.get_nilai(row.ap_giro_id) 
    
    #Untuk update status disabled pada SP2D
    row = DBSession.query(Sp2d).filter(Sp2d.id==controls['ap_sp2d_id']).first()   
    row.status_giro=1
    save_request2(row)
    """
    return {"success": True, 'id': row.id, "msg":'Success Tambah Penghapusan'} #, 'jml_total':nominal}

########
# Edit #
########
def query_id(request):
    return DBSession.query(AsetDelItem).filter(AsetDelItem.id==request.matchdict['id'],
                                               AsetDelItem.delete_id==request.matchdict['delete_id'])
    
def id_not_found(request):    
    msg = 'User ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

@view_config(route_name='aset-kibdel-item-edit', renderer='json',
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
@view_config(route_name='aset-kibdel-item-delete', renderer='json',
             permission='delete')
def view_delete(request):
    q   = query_id(request)
    row = q.first()
    
    if not row:
        return {'success':False, "msg":self.id_not_found()}

    msg = 'Data sudah dihapus'
    query_id(request).delete()
    DBSession.flush()
    """
    nominal = "%s" % Giro.get_nilai(row.ap_giro_id)
    
    #Untuk update status disabled pada SP2D
    row = DBSession.query(Sp2d).filter(Sp2d.id==row.ap_sp2d_id).first()   
    row.status_giro=0
    save_request2(row)
    """
    return {'success':True, "msg":msg} #, 'jml_total':nominal}
    