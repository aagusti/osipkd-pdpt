import os
import uuid
from osipkd.tools import row2dict, xls_reader
from datetime import datetime
from sqlalchemy import not_, func, or_, cast, BigInteger
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from osipkd.models import DBSession
from osipkd.models.apbd_anggaran import Kegiatan, KegiatanSub, KegiatanItem, KegiatanIndikator
from osipkd.models.pemda_model import Rekening
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah ag-indikator gagal'
SESS_EDIT_FAILED = 'Edit ag-indikator gagal'

def deferred_tipe(node, kw):
    values = kw.get('tipe', [])
    return widget.SelectWidget(values=values)
    
TIPE = (
    (1, 'Capaian Program'),
    (2, 'Masukan'),
    (3, 'Keluaran'),
    (4, 'Hasil'),
    )

class view_ag_indikator(BaseViews):
    @view_config(route_name="ag-indikator", renderer="templates/ag-indikator/list.pt")
    def view_list(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        kegiatan_sub_id =  url_dict['kegiatan_sub_id']
        row = KegiatanSub.query_id(kegiatan_sub_id).filter(KegiatanSub.unit_id==ses['unit_id']).first()
        #rek_head = 5
        return dict(project='OSIPKD', row = row)#, rek_head=rek_head)
        
    ##########                    
    # Action #
    ##########    
    #def get_row_item(self):
    #    return DBSession.query(KegiatanItem.id, KegiatanItem.rekening_id, 
    #              Rekening.kode.label('rekening_kd'), Rekening.nama.label('rekening_nm'), 
    #              KegiatanItem.nama, KegiatanItem.no_urut,
    #              (KegiatanItem.vol_1_1*KegiatanItem.vol_1_2*KegiatanItem.hsat_1).label('amount_1'),
    #              (KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*KegiatanItem.hsat_2).label('amount_2'),
    #              (KegiatanItem.vol_3_1*KegiatanItem.vol_3_2*KegiatanItem.hsat_3).label('amount_3'),
    #              (KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('amount_4')).join(Rekening)
                  
    @view_config(route_name='ag-indikator-act', renderer='json',
                 permission='read')
    def ag_indikator_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        if url_dict['act']=='grid':
            ag_step_id  = ses['ag_step_id']
            kegiatan_sub_id = 'kegiatan_sub_id' in params and params['kegiatan_sub_id'] or 0
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('tipe'))
            columns.append(ColumnDT('no_urut'))
            columns.append(ColumnDT('tolok_ukur_%s' %ag_step_id))
            columns.append(ColumnDT('volume_%s' %ag_step_id))
            columns.append(ColumnDT('satuan_%s' %ag_step_id))
            #columns.append(ColumnDT("".join(['tolok_ukur_',str(self.status_apbd)])))
            #columns.append(ColumnDT("".join(['volume_',str(self.status_apbd)])))
            #columns.append(ColumnDT("".join(['satuan_',str(self.status_apbd)])))

            query = DBSession.query(KegiatanIndikator)\
                .join(KegiatanSub)\
                .filter(KegiatanSub.id==kegiatan_sub_id,
                        KegiatanSub.unit_id==ses['unit_id'])
            rowTable = DataTables(req, KegiatanIndikator, query, columns)
            return rowTable.output_result()
            
    ###############                    
    # Tambah  Data#
    ###############    
    @view_config(route_name='ag-indikator-add-fast', renderer='json',
                 permission='add')
    def ag_indikator_add_fast(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        kegiatan_sub_id  = 'kegiatan_sub_id'  in params and params['kegiatan_sub_id'] or None
        kegiatan_indikator_id = 'kegiatan_indikator_id' in params and params['kegiatan_indikator_id'] or None
        if not kegiatan_indikator_id:
            row = KegiatanIndikator()
            row_dict = {}
        else:
            row = DBSession.query(KegiatanIndikator).filter(KegiatanIndikator.id==kegiatan_indikator_id).first()
            if not row:
                return {'success':False, 'msg':'Data Tidak Ditemukan'}
            row_dict = row.to_dict()
            
        row_dict['no_urut']         = 'no_urut' in params and params['no_urut'] or \
                                      KegiatanIndikator.max_no_urut(kegiatan_sub_id)+1
        row_dict['kegiatan_sub_id'] = kegiatan_sub_id
        #row_dict['nama']            = 'nama' in params and params['nama'] or None
        #row_dict['kode']            = 'kode' in params and params['kode'] or None

        ag_step_id = ses['ag_step_id']
        tolok_ukur = 'tolok_ukur' in params and params['tolok_ukur'].replace('.', '') or 0
        volume     = 'volume'     in params and params['volume'].replace('.', '') or 0
        satuan     = 'satuan'     in params and params['satuan'].replace('.', '') or 0

        if ag_step_id<2:
            row_dict['tolok_ukur_1'] = tolok_ukur 
            row_dict['volume_1']     = volume 
            row_dict['satuan_1']     = satuan 
        if ag_step_id<3:
            row_dict['tolok_ukur_2'] = tolok_ukur 
            row_dict['volume_2']     = volume 
            row_dict['satuan_2']     = satuan 
        if ag_step_id<4:
            row_dict['tolok_ukur_3'] = tolok_ukur 
            row_dict['volume_3']     = volume 
            row_dict['satuan_3']     = satuan 
        if ag_step_id<5:
            row_dict['tolok_ukur_4'] = tolok_ukur 
            row_dict['volume_4']     = volume 
            row_dict['satuan_4']     = satuan 

        row.from_dict(row_dict)
        DBSession.add(row)
        DBSession.flush()
        return {"success": True, 'id': row.id, "msg":'Success Tambah Data'}
        
        try:
          pass
        except:
            return {'success':False, 'msg':'Gagal Tambah Data'}

#######    
# Add #
#######
def form_validator(form, value):
    def err_kegiatan():
        raise colander.Invalid(form,
            'Kegiatan dengan no urut tersebut sudah ada')
                
class AddSchema(colander.Schema):

    kegiatan_sub_id = colander.SchemaNode(
                          colander.String(),
                          )
    no_urut         = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="No.Urut",
                          )
    tipe            = colander.SchemaNode(
                        colander.String(),
                        widget=widget.SelectWidget(values=TIPE),
                        title="Tipe"
                        )
    header_id       = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          )
    tolok_ukur_1    = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          oid='tolok_ukur_1',
                          title='Tolok Ukur RKA'
                          )
    volume_1        = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          default=1,
                          oid='volume_1',
                          )
    satuan_1        = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          oid='satuan_1',
                          )
    tolok_ukur_2    = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          oid='tolok_ukur_2',
                          title='Tolok Ukur DPA'
                          )
    volume_2        = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          default=1,
                          oid='volume_2',
                          )
    satuan_2        = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          oid='satuan_2',
                          )
    tolok_ukur_3    = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          oid='tolok_ukur_3',
                          title='Tolok Ukur RPKA'
                          )
    volume_3        = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          default=1,
                          oid='volume_3',
                          )
    satuan_3        = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          oid='satuan_3',
                          )
    tolok_ukur_4    = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          oid='tolok_ukur_4',
                          title='Tolok Ukur DPPA'
                          )
    volume_4        = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          default=1,
                          oid='volume_4',
                          )
    satuan_4        = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          oid='satuan_4',
                          )
                          
class EditSchema(AddSchema):
    id             = colander.SchemaNode(
                          colander.Integer(),)

def get_form(request, class_form):
    schema = class_form(validator=form_validator)
    schema = schema.bind(tipe=TIPE)
    schema.request = request
    return Form(schema, buttons=('simpan','batal'))
    
def save(values, request, row=None):
    if not row:
        row = KegiatanIndikator()
    ag_step_id = request.session['ag_step_id']
    
    if not values['tolok_ukur_1']: 
        values['tolok_ukur_1']='-'
        values['satuan_1']='-'
    if not values['tolok_ukur_2']: 
        values['tolok_ukur_2']='-'
        values['satuan_2']='-'
    if not values['tolok_ukur_3']: 
        values['tolok_ukur_3']='-'
        values['satuan_3']='-'
    if not values['tolok_ukur_4']: 
        values['tolok_ukur_4']='-'
        values['satuan_4']='-'
        
    if ag_step_id<2:
        values['tolok_ukur_2'] = values['tolok_ukur_%s' % ag_step_id] 
        values['volume_2'] = values['volume_%s' % ag_step_id] 
        values['satuan_2'] = values['satuan_%s' % ag_step_id] 
    if ag_step_id<4:
        values['tolok_ukur_3'] = values['tolok_ukur_%s' % ag_step_id] 
        values['volume_3'] = values['volume_%s' % ag_step_id] 
        values['satuan_3'] = values['satuan_%s' % ag_step_id] 
    if ag_step_id<5:
        values['tolok_ukur_4'] = values['tolok_ukur_%s' % ag_step_id] 
        values['volume_4'] = values['volume_%s' % ag_step_id] 
        values['satuan_4'] = values['satuan_%s' % ag_step_id] 
        
    row.from_dict(values)
    if not row.no_urut:
          row.no_urut = KegiatanIndikator.max_no_urut(values['kegiatan_sub_id'])+1;
    
    DBSession.add(row)
    DBSession.flush()
    return row
                                      
def save_request(values, request, row=None):
    if 'id' in request.matchdict:
        values['id'] = request.matchdict['id']
    row = save(values, request, row)
    request.session.flash('Kegiatan sudah disimpan.')
        
def route_list(request,kegiatan_sub_id):
    return HTTPFound(location=request.route_url('ag-indikator',kegiatan_sub_id=kegiatan_sub_id))
    
def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r
    
@view_config(route_name='ag-indikator-add', renderer='templates/ag-indikator/add.pt',
             permission='add')
def view_add(request):
    form = get_form(request, AddSchema)
    kegiatan_sub_id = request.matchdict['kegiatan_sub_id']
    ses = request.session
    rows = KegiatanSub.query_id(kegiatan_sub_id).filter(KegiatanSub.unit_id == ses['unit_id']).first()
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items()
            controls_dicted = dict(controls)
            #return dict(form=form.render(appstruct=controls_dicted))
            try:
                c = form.validate(controls)
            except ValidationFailure, e:
                return dict(form=form, row=rows)#, rek_head=5)
                #request.session[SESS_ADD_FAILED] = e.render()               
                #return HTTPFound(location=request.route_url('ag-indikator-add'))
            save_request(controls_dicted, request)
        return route_list(request,kegiatan_sub_id)
    elif SESS_ADD_FAILED in request.session:
        del request.session[SESS_ADD_FAILED]
        #return session_failed(request, SESS_ADD_FAILED)
    return dict(form=form, row=rows)#, rek_head=5)

########
# Edit #
########
def query_id(request):
    return DBSession.query(KegiatanIndikator).filter(KegiatanIndikator.id==request.matchdict['id'])
    
def id_not_found(request,kegiatan_sub_id):    
    msg = 'ITEM ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request,kegiatan_sub_id)

@view_config(route_name='ag-indikator-edit', renderer='templates/ag-indikator/add.pt',
             permission='edit')
def view_edit(request):
    form = get_form(request, EditSchema)
    ses = request.session
    kegiatan_sub_id = request.matchdict['kegiatan_sub_id']
    row = query_id(request).first()
    if not row:
        return id_not_found(request,kegiatan_sub_id)
    rows = KegiatanSub.query_id(kegiatan_sub_id).filter(KegiatanSub.unit_id==ses['unit_id']).first()
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items()  
            #try:
            #    c = form.validate(controls)
            #except ValidationFailure, e:
            #    return dict(form=form, row=rows)
            save_request(dict(controls), request, row)
        return route_list(request,kegiatan_sub_id)
    elif SESS_EDIT_FAILED in request.session:
        del request.session[SESS_EDIT_FAILED]
        return dict(form=form)
    values = row.to_dict()
    form.set_appstruct(values) 
    return dict(form=form, row=rows)

##########
# Delete #
##########    
@view_config(route_name='ag-indikator-delete', renderer='templates/ag-indikator/delete.pt',
             permission='delete')
def view_delete(request):
    q = query_id(request)
    kegiatan_sub_id = request.matchdict['kegiatan_sub_id']
    row = q.first()
        
    if not row:
        return id_not_found(request,kegiatan_sub_id)
        
    form = Form(colander.Schema(), buttons=('hapus','cancel'))
    values= {}
    
    if request.POST:
        if 'hapus' in request.POST:
            msg = '%s berhasil.' % (request.title)
            DBSession.query(KegiatanIndikator).filter(KegiatanIndikator.id==request.matchdict['id']).delete()
            DBSession.flush()
            request.session.flash(msg)
        return route_list(request,kegiatan_sub_id)
    return dict(row=row, form=form.render())

            
                        