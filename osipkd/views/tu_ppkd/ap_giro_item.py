import os
import uuid
from osipkd.tools import row2dict, xls_reader
from datetime import datetime
from sqlalchemy import not_, func, or_
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from osipkd.models import DBSession
from osipkd.models.apbd_anggaran import Kegiatan, KegiatanSub, KegiatanItem
from osipkd.models.pemda_model import Unit
from osipkd.models.apbd_tu import Giro, GiroItem, Sp2d, Spm, SpmPotongan, Spp
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah ap-giro-item gagal'
SESS_EDIT_FAILED = 'Edit ap-giro-item gagal'

class view_ap_giro_item(BaseViews):
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='ap-giro-item-act', renderer='json',
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
                ap_giro_id = url_dict['ap_giro_id'].isdigit() and url_dict['ap_giro_id'] or 0
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('ap_sp2d_id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('tanggal'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('nominal',filter=self._number_format))
                #columns.append(ColumnDT('nominal1',filter=self._number_format))
                columns.append(ColumnDT('no_validasi'))
                query = DBSession.query(GiroItem.id,
                                        GiroItem.ap_sp2d_id,
                                        Sp2d.kode.label('kode'),
                                        Sp2d.tanggal.label('tanggal'),
                                        Sp2d.nama.label('nama'),
                                        Spp.nominal.label('nominal'),
                                        #func.sum(SpmPotongan.nilai).label('nominal1'),
                                        Sp2d.no_validasi.label('no_validasi'),
                          ).join(Sp2d, Spm, Spp,
                          #).outerjoin(Spm, SpmPotongan.ap_spm_id==Spm.id
                          ).filter(GiroItem.ap_giro_id==ap_giro_id,
                                   GiroItem.ap_sp2d_id==Sp2d.id,
                                   Sp2d.ap_spm_id==Spm.id,
                                   Spm.ap_spp_id==Spp.id,
                          ).group_by(GiroItem.id, 
                                     GiroItem.ap_sp2d_id,
                                     Sp2d.kode.label('kode'),
                                     Sp2d.tanggal.label('tanggal'),
                                     Sp2d.nama.label('nama'),
                                     Spp.nominal.label('nominal'),
                                     Sp2d.no_validasi.label('no_validasi'),
                          )
                rowTable = DataTables(req, GiroItem, query, columns)
                return rowTable.output_result()

        elif url_dict['act']=='grid1':
            # defining columns
            ap_giro_id = url_dict['ap_giro_id'].isdigit() and url_dict['ap_giro_id'] or 0
            cari = 'cari' in params and params['cari'] or ''
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('ap_sp2d_id'))
            columns.append(ColumnDT('kode'))
            columns.append(ColumnDT('tanggal'))
            columns.append(ColumnDT('nama'))
            columns.append(ColumnDT('nominal',filter=self._number_format))
            #columns.append(ColumnDT('nominal1',filter=self._number_format))
            columns.append(ColumnDT('no_validasi'))
            query = DBSession.query(GiroItem.id,
                                    GiroItem.ap_sp2d_id,
                                    Sp2d.kode.label('kode'),
                                    Sp2d.tanggal.label('tanggal'),
                                    Sp2d.nama.label('nama'),
                                    Spp.nominal.label('nominal'),
                                    #func.sum(SpmPotongan.nilai).label('nominal1'),
                                    Sp2d.no_validasi.label('no_validasi'),
                      ).join(Sp2d, Spm, Spp,
                      #).outerjoin(Spm, SpmPotongan.ap_spm_id==Spm.id
                      ).group_by(GiroItem.id, 
                                 GiroItem.ap_sp2d_id,
                                 Sp2d.kode.label('kode'),
                                 Sp2d.tanggal.label('tanggal'),
                                 Sp2d.nama.label('nama'),
                                 Spp.nominal.label('nominal'),
                                 Sp2d.no_validasi.label('no_validasi'),
                      ).filter(GiroItem.ap_giro_id==ap_giro_id,
                               GiroItem.ap_sp2d_id==Sp2d.id,
                               Sp2d.ap_spm_id==Spm.id,
                               Spm.ap_spp_id==Spp.id,
                               or_(Sp2d.kode.ilike('%%%s%%' % cari),
                                   Sp2d.nama.ilike('%%%s%%' % cari))
                      )
            rowTable = DataTables(req, GiroItem, query, columns)
            return rowTable.output_result()

#######    
# Add #
#######
def save_request2(row=None):
    row = Sp2d()
    return row
    
@view_config(route_name='ap-giro-item-add', renderer='json',
             permission='add')
def view_add(request):
    req = request
    ses = req.session
    params = req.params
    url_dict = req.matchdict
    ap_giro_id = 'ap_giro_id' in url_dict and url_dict['ap_giro_id'] or 0
    controls = dict(request.POST.items())
    
    ap_giro_item_id = 'ap_giro_item_id' in controls and controls['ap_giro_item_id'] or 0
    #Cek dulu ada penyusup gak dengan mengecek sessionnya
    ap_giro = DBSession.query(Giro)\
                  .filter(Giro.unit_id==ses['unit_id'],
                          Giro.id==ap_giro_id).first()
    if not ap_giro:
        return {"success": False, 'msg':'Giro tidak ditemukan'}
    
    #Cek lagi ditakutkan skpd ada yang iseng inject script
    if ap_giro_item_id:
        row = DBSession.query(GiroItem)\
                  .join(Giro)\
                  .filter(GiroItem.id==ap_giro_item_id,
                          Giro.unit_id==ses['unit_id'],
                          GiroItem.ap_giro_id==ap_giro_id).first()
        if not row:
            return {"success": False, 'msg':'Giro tidak ditemukan'}
    else:
        row = GiroItem()
            
    row.ap_giro_id = ap_giro_id
    row.ap_sp2d_id = controls['ap_sp2d_id']

    DBSession.add(row)
    DBSession.flush()
    nominal = "%d" % Giro.get_nilai(row.ap_giro_id) 
    
    #Untuk update status disabled pada SP2D
    row = DBSession.query(Sp2d).filter(Sp2d.id==controls['ap_sp2d_id']).first()   
    row.status_giro = 1
    row.no_validasi = controls['no_validasi']
    save_request2(row)
    
    return {"success": True, 'id': row.id, "msg":'Success Tambah SP2D', 'jml_total':nominal}

########
# Edit #
########
def query_id(request):
    return DBSession.query(GiroItem).filter(GiroItem.id==request.matchdict['id'],
                                           GiroItem.ap_giro_id==request.matchdict['ap_giro_id'])
    
def id_not_found(request):    
    msg = 'User ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

@view_config(route_name='ap-giro-item-edit', renderer='json',
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
@view_config(route_name='ap-giro-item-delete', renderer='json',
             permission='delete')
def view_delete(request):
    q = query_id(request)
    row = q.first()
    
    if not row:
        return {'success':False, "msg":self.id_not_found()}

    msg = 'Data sudah dihapus'
    query_id(request).delete()
    DBSession.flush()

    nominal = "%s" % Giro.get_nilai(row.ap_giro_id)
    
    #Untuk update status disabled pada SP2D
    row = DBSession.query(Sp2d).filter(Sp2d.id==row.ap_sp2d_id).first()   
    row.status_giro=0
    save_request2(row)
    
    return {'success':True, "msg":msg, 'jml_total':nominal}
    