import os
import uuid
from osipkd.tools import row2dict, xls_reader
from datetime import datetime
from sqlalchemy import not_, func
from sqlalchemy.orm import aliased
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from osipkd.models import DBSession
from osipkd.models.apbd import Jurnal, JurnalItem
from osipkd.models.pemda_model import Rekening, Sap, RekeningSap
from osipkd.models.apbd_anggaran import KegiatanSub, Kegiatan, KegiatanItem
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah ak-jurnal-item gagal'
SESS_EDIT_FAILED = 'Edit ak-jurnal-item gagal'
            
class view_ak_jurnal_item(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='ak-jurnal-item', renderer='templates/ak-jurnal-item/list.pt',
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
    @view_config(route_name='ak-jurnal-item-act', renderer='json',
                 permission='read')
    def ak_jurnal_item_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        pk_id = 'id' in params and params['id'] and int(params['id']) or 0
        
        if url_dict['act']=='grid':
            jurnal_id = url_dict['jurnal_id'].isdigit() and url_dict['jurnal_id'] or 0
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('sapkd'))
            columns.append(ColumnDT('sapnm'))
            columns.append(ColumnDT('amount',  filter=self._number_format))
            columns.append(ColumnDT('notes'))
            columns.append(ColumnDT('rekkd'))
            columns.append(ColumnDT('reknm'))
            columns.append(ColumnDT('kegiatan_sub_id'))
            columns.append(ColumnDT('rekening_id'))
            columns.append(ColumnDT('jurnal_id'))
            columns.append(ColumnDT('subkd'))
            columns.append(ColumnDT('subnm'))
            
            rek = aliased(Rekening)
            sap = aliased(Sap)
            sub = aliased(KegiatanSub)
            
            query = DBSession.query(JurnalItem.id,
                                    sap.kode.label('sapkd'),
                                    sap.nama.label('sapnm'),
                                    JurnalItem.amount,
                                    JurnalItem.notes,
                                    rek.kode.label('rekkd'),
                                    rek.nama.label('reknm'),
                                    JurnalItem.kegiatan_sub_id,
                                    JurnalItem.rekening_id,
                                    JurnalItem.jurnal_id,
                                    sub.kode.label('subkd'),
                                    sub.nama.label('subnm'),
                                ).join(Jurnal, 
                                ).outerjoin(rek, JurnalItem.rekening_id == rek.id
                                ).outerjoin(sap, JurnalItem.sap_id == sap.id
                                ).outerjoin(sub, JurnalItem.kegiatan_sub_id  == sub.id
                                ).filter(JurnalItem.jurnal_id==jurnal_id,
                                         JurnalItem.jurnal_id==Jurnal.id,
                                ).group_by(JurnalItem.id,
                                           sap.kode.label('sapkd'),
                                           sap.nama.label('sapnm'),
                                           JurnalItem.amount,
                                           JurnalItem.notes,
                                           rek.kode.label('rekkd'),
                                           rek.nama.label('reknm'),
                                           JurnalItem.kegiatan_sub_id,
                                           JurnalItem.rekening_id,
                                           JurnalItem.jurnal_id,
                                           sub.kode.label('subkd'),
                                           sub.nama.label('subnm'),
                                )
            rowTable = DataTables(req, JurnalItem, query, columns)
            return rowTable.output_result()
        
    ################                    
    # Tambah  Cepat#
    ################    
    @view_config(route_name='ak-jurnal-item-add', renderer='json',
                 permission='add')
    def view_add(self):
        ses = self.request.session
        req = self.request
        params   = req.params
        url_dict = req.matchdict
        jurnal_id = 'jurnal_id' in url_dict and url_dict['jurnal_id'] or 0
        controls = dict(req.POST.items())
        
        jurnal_item_id = 'jurnal_item_id' in controls and controls['jurnal_item_id'] or 0        
        
        if jurnal_item_id:
            row = DBSession.query(JurnalItem)\
                      .join(Jurnal)\
                      .filter(JurnalItem.id==jurnal_item_id,
                              Jurnal.unit_id==ses['unit_id'],
                              JurnalItem.jurnal_id==jurnal_id).first()
            if not row:
                return {"success": False, 'msg':'Jurnal tidak ditemukan'}
        else:
            row = JurnalItem()
            
        row.jurnal_id       = jurnal_id
        row.kegiatan_sub_id = controls['kegiatan_sub_id'] or 0
        row.rekening_id     = controls['rekening_id'] or 0
        row.sap_id          = controls['sap_id'] or 0
        row.amount          = controls['amount'].replace('.','')
        row.notes           = controls['notes']
        
        DBSession.add(row)
        DBSession.flush()
        return {"success": True, 'id': row.id, "msg":'Success Tambah Data'}
        
        try:
          pass
        except:
            return {'success':False, 'msg':'Gagal Tambah Data'}       
            
    def query_id(self):
        return DBSession.query(JurnalItem).filter(JurnalItem.id==self.request.matchdict['id'],
                                                  JurnalItem.jurnal_id==self.request.matchdict['jurnal_id'])
        
    def id_not_found(self):    
        msg = 'Jurnal Item ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        return {'success': False, 'msg':msg}
        
    ########
    # Edit #
    ########
    @view_config(route_name='ak-jurnal-item-edit', renderer='json',
             permission='edit')
    def view_edit(self):
        request = self.request
        row     = self.query_id().first()
        
        if not row:
            return id_not_found(request)
            
        form = self.get_form(EditSchema)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form)
                save_request(dict(controls), row)
            return route_list()
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)
            
        values = row.to_dict() 
        r=DBSession.query(Rekening).filter(Rekening.id==row.rekening_id).first()
        if r:
            values['rekening_kd'] = r.kode
            values['rekening_nm'] = r.nama
        else:
            values['rekening_id'] = 0
            values['rekening_kd'] = ""
            values['rekening_nm'] = ""

        a=DBSession.query(KegiatanSub).filter(KegiatanSub.id==row.kegiatan_sub_id).first()
        if a:
            values['kegiatan_sub_kd'] = a.kode
            values['kegiatan_sub_nm'] = a.nama
        else:
            values['kegiatan_sub_id'] = 0
            values['kegiatan_sub_kd'] = ""
            values['kegiatan_sub_nm'] = ""

        aa=DBSession.query(Sap).filter(Sap.id==row.sap_id).first()
        if aa:
            values['sap_kd'] = aa.kode
            values['sap_nm'] = aa.nama
        else:
            values['sap_id'] = 0
            values['sap_kd'] = ""
            values['sap_nm'] = ""

        form.set_appstruct(values) 
        return dict(form=form)
    
    ##########
    # Delete #
    ##########    
    @view_config(route_name='ak-jurnal-item-delete', renderer='json',
                 permission='delete')
    def view_delete(self):
        request = self.request
        ses     = self.session
        
        q = self.query_id().join(Jurnal).filter(Jurnal.unit_id==ses['unit_id'])
        row = q.first()
        if not row:
            return self.id_not_found()
        q = self.query_id()
        q.delete()
        DBSession.flush()
        return {'success': True, 'msg':'Sukses Hapus Data'}
