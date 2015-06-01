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
from osipkd.models.pemda_model import Unit, Rekening
from osipkd.models.apbd_tu import APInvoice, Spp, SppItem, Spm, SpmPotongan
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah ap-spm-potongan gagal'
SESS_EDIT_FAILED = 'Edit ap-spm-potongan gagal'

class view_ap_spm_potongan(BaseViews):
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='ap-spm-potongan-act', renderer='json',
                 permission='read')
    def view_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict

        if url_dict['act']=='grid':
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if url_dict['act']=='grid':
                ap_spm_id = url_dict['ap_spm_id'].isdigit() and url_dict['ap_spm_id'] or 0
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('ap_spm_id'))
                columns.append(ColumnDT('rekening_id'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('kode_rek'))
                columns.append(ColumnDT('nama_rek'))
                columns.append(ColumnDT('nilai'))
                query = DBSession.query(SpmPotongan.id,
                                        SpmPotongan.ap_spm_id,
                                        SpmPotongan.rekening_id,
                                        SpmPotongan.no_urut,
                                        Rekening.kode.label('kode_rek'),
                                        Rekening.nama.label('nama_rek'),
                                        SpmPotongan.nilai,
                            ).join(Spm, Rekening,
                            ).filter(SpmPotongan.ap_spm_id==Spm.id,
                                     SpmPotongan.ap_spm_id==ap_spm_id,
                                     SpmPotongan.rekening_id==Rekening.id,
                            ).group_by(SpmPotongan.id,
                                        SpmPotongan.ap_spm_id,
                                        SpmPotongan.rekening_id,
                                        SpmPotongan.no_urut,
                                        Rekening.kode.label('kode_rek'),
                                        Rekening.nama.label('nama_rek'),
                                        SpmPotongan.nilai)
                            
                rowTable = DataTables(req, SpmPotongan, query, columns)
                return rowTable.output_result()
#######    
# Add #
#######
@view_config(route_name='ap-spm-potongan-add', renderer='json',
             permission='add')
def view_add(request):
    req = request
    ses = req.session
    params = req.params
    url_dict = req.matchdict
    ap_spm_id = 'ap_spm_id' in url_dict and url_dict['ap_spm_id'] or 0
    controls = dict(request.POST.items())
    
    ap_spm_potongan_id = 'ap_spm_potongan_id' in controls and controls['ap_spm_potongan_id'] or 0
    #Cek dulu ada penyusup gak dengan mengecek sessionnya
    ap_spm = DBSession.query(Spm)\
                  .join(Spp)\
                  .filter(Spm.ap_spp_id==Spp.id,
                          Spp.unit_id==ses['unit_id'],
                          Spm.id==ap_spm_id).first()
    if not ap_spm:
        return {"success": False, 'msg':'SPM tidak ditemukan'}
    
    if ap_spm_potongan_id:
    #Cek lagi ditakutkan skpd ada yang iseng inject script
        row = DBSession.query(SpmPotongan)\
                  .join(Spm)\
                  .outerjoin(Spp)\
                  .filter(SpmPotongan.id==ap_spm_potongan_id,
                          SpmPotongan.ap_spm_id==Spm.id,
                          SpmPotongan.ap_spm_id==ap_spm_id,
                          Spm.ap_spp_id==Spp.id,
                          Spp.unit_id==ses['unit_id']).first()
        if not row:
            return {"success": False, 'msg':'SPM tidak ditemukan'}
    else:
        row = SpmPotongan()
            
    row.ap_spm_id   = ap_spm_id
    row.rekening_id = controls['rekening_id']
    if not controls['no_urut'] or controls['no_urut'].split()=='':
        controls['no_urut'] = SpmPotongan.max_no_urut(ap_spm_id)+1
    row.no_urut     = controls['no_urut']  
    row.nilai       = controls['nilai'].replace('.','')    

    DBSession.add(row)
    DBSession.flush()
    return {"success": True, 'id': row.id, "msg":'Success Tambah Rekening'}#, 'jml_total':amount}



########
# Edit #
########
def query_id(request):
    return DBSession.query(SpmPotongan).filter(SpmPotongan.id==request.matchdict['id'],
                                               SpmPotongan.ap_spm_id==request.matchdict['ap_spm_id'])
    
def id_not_found(request):    
    msg = 'User ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

@view_config(route_name='ap-spm-potongan-edit', renderer='json',
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
@view_config(route_name='ap-spm-potongan-delete', renderer='json',
             permission='delete')
def view_delete(request):
    q = query_id(request)
    row = q.first()
    
    if not row:
        return {'success':False, "msg":self.id_not_found()}

    msg = 'Data sudah dihapus'
    query_id(request).delete()
    DBSession.flush()
    return {'success':True, "msg":msg}
    