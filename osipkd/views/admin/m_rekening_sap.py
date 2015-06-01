import os
import uuid
import colander
from datetime import datetime

from sqlalchemy import not_, func, outerjoin, join, or_
from sqlalchemy.sql.expression import and_
from sqlalchemy.orm import aliased

from ziggurat_foundations.models import groupfinder
from pyramid.view import (view_config,)
from pyramid.httpexceptions import (HTTPFound,)
from osipkd.views.base_view import BaseViews

from deform import (Form, widget,ValidationFailure,)
from datatables import ColumnDT, DataTables

from osipkd.tools import row2dict, xls_reader
from osipkd.models import (DBSession,)
from osipkd.models.pemda_model import Sap, RekeningSap, Rekening
from osipkd.models.apbd_anggaran import Kegiatan, KegiatanSub, KegiatanItem


SESS_ADD_FAILED = 'Tambah rekening sap gagal'
SESS_EDIT_FAILED = 'Edit rekening sap gagal'

@colander.deferred
def deferred_pph(node, kw):
    values = kw.get('pph', [])
    return widget.SelectWidget(values=values)
    
PPH = (
    ('-', '-'),
    ('21', '21'),
    ('22', '22'),
    ('23', '23'),
    ('4.2', '4.2'),
    )
         
class AddSchema(colander.Schema):
    rek_widget  = widget.AutocompleteInputWidget(
                    size=60,
                    values = '/rekening/act/headofkode11',
                    min_length=1)
    rekn_widget = widget.AutocompleteInputWidget(
                    size=60,
                    values = '/rekening/act/headofnama11',
                    min_length=1)
    rekening_id = colander.SchemaNode(
                    colander.Integer(),
                    widget = widget.HiddenWidget(),
                    missing = colander.drop,
                    oid = "rekening_id")
    rekening_kd = colander.SchemaNode(
                    colander.String(),
                    widget = rek_widget,
                    missing = colander.drop,
                    oid = "rekening_kd",
                    title = "Rekening")
    rekening_nm = colander.SchemaNode(
                    colander.String(),
                    widget = rekn_widget,
                    missing = colander.drop,
                    oid = "rekening_nm",
                    title = "Uraian")
    ## HEADOF
    lo_widget   = widget.AutocompleteInputWidget(
                    size=60,
                    values = '/sap/act/headofkode1',
                    min_length=1)    
    lon_widget  = widget.AutocompleteInputWidget(
                    size=60,
                    values = '/sap/act/headofnama1',
                    min_length=1)
    ## LO DEBET
    db_lo_sap_id   = colander.SchemaNode(
                    colander.Integer(),
                    widget = widget.HiddenWidget(),
                    missing = colander.drop,
                    oid = "db_lo_sap_id")
    db_lo_sap_kd   = colander.SchemaNode(
                    colander.String(),
                    widget = lo_widget,
                    missing = colander.drop,
                    oid = "db_lo_sap_kd",
                    title = "LO Debet")
    db_lo_sap_nm   = colander.SchemaNode(
                    colander.String(),
                    widget = lon_widget,
                    missing = colander.drop,
                    oid = "db_lo_sap_nm",
                    title = "Uraian LO")
    
    ## HEADOF
    lok_widget   = widget.AutocompleteInputWidget(
                    size=60,
                    values = '/sap/act/headofkode11',
                    min_length=1)    
    lonk_widget  = widget.AutocompleteInputWidget(
                    size=60,
                    values = '/sap/act/headofnama11',
                    min_length=1)
    ## LO KREDIT
    kr_lo_sap_id   = colander.SchemaNode(
                    colander.Integer(),
                    widget = widget.HiddenWidget(),
                    missing = colander.drop,
                    oid = "kr_lo_sap_id")
    kr_lo_sap_kd   = colander.SchemaNode(
                    colander.String(),
                    widget = lok_widget,
                    missing = colander.drop,
                    oid = "kr_lo_sap_kd",
                    title = "LO Kredit")
    kr_lo_sap_nm   = colander.SchemaNode(
                    colander.String(),
                    widget = lonk_widget,
                    missing = colander.drop,
                    oid = "kr_lo_sap_nm",
                    title = "Uraian LO")

    ## HEADOF
    lra_widget  = widget.AutocompleteInputWidget(
                    size=60,
                    values = '/sap/act/headofkode2',
                    min_length=1) 
    lran_widget = widget.AutocompleteInputWidget(
                    size=60,
                    values = '/sap/act/headofnama2',
                    min_length=1)                    
    ## LRA DEBET
    db_lra_sap_id  = colander.SchemaNode(
                    colander.Integer(),
                    widget = widget.HiddenWidget(),
                    missing = colander.drop,
                    oid = "db_lra_sap_id")
    db_lra_sap_kd  = colander.SchemaNode(
                    colander.String(),
                    widget = lra_widget,
                    missing = colander.drop,
                    oid = "db_lra_sap_kd",
                    title = "LRA Debet")
    db_lra_sap_nm  = colander.SchemaNode(
                    colander.String(),
                    widget = lran_widget,
                    missing = colander.drop,
                    oid = "db_lra_sap_nm",
                    title = "Uraian LRA")
    ## LRA KERIDIT
    kr_lra_sap_id  = colander.SchemaNode(
                    colander.Integer(),
                    widget = widget.HiddenWidget(),
                    missing = colander.drop,
                    oid = "kr_lra_sap_id")
    kr_lra_sap_kd  = colander.SchemaNode(
                    colander.String(),
                    widget = lra_widget,
                    missing = colander.drop,
                    oid = "kr_lra_sap_kd",
                    title = "LRA Kredit")
    kr_lra_sap_nm  = colander.SchemaNode(
                    colander.String(),
                    widget = lran_widget,
                    missing = colander.drop,
                    oid = "kr_lra_sap_nm",
                    title = "Uraian LRA")

    ## HEADOF
    neraca_widget = widget.AutocompleteInputWidget(
                    size=60,
                    values = '/sap/act/headofkode3',
                    min_length=1)
    neracan_widget = widget.AutocompleteInputWidget(
                    size=60,
                    values = '/sap/act/headofnama3',
                    min_length=1)                    
    ## NERACA DEBET
    neraca_sap_id = colander.SchemaNode(
                    colander.Integer(),
                    widget = widget.HiddenWidget(),
                    missing = colander.drop,
                    oid = "neraca_sap_id")
    neraca_sap_kd = colander.SchemaNode(
                    colander.String(),
                    widget = neraca_widget,
                    missing = colander.drop,
                    oid = "neraca_sap_kd",
                    title = "Neraca")
    neraca_sap_nm = colander.SchemaNode(
                    colander.String(),
                    widget = neracan_widget,
                    missing = colander.drop,
                    oid = "neraca_sap_nm",
                    title = "Uraian Aset")
    pph_id      = colander.SchemaNode(
                    colander.String(),
                    widget=deferred_pph,
                    title = "PPh")

                    
class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))
            
class view_rekening_sap(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='rekening-sap', renderer='templates/rekening-sap/list.pt',
                 permission='read')
    def view_list(self):
        return dict(project="osipkd")
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='rekening-sap-act', renderer='json',
                 permission='view')
    def gaji_sap_act(self):
        ses = self.request.session
        req = self.request
        params   = req.params
        url_dict = req.matchdict
        
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('norek'))
            columns.append(ColumnDT('nmrek'))
            columns.append(ColumnDT('nosaplodb'))
            columns.append(ColumnDT('nosaplokr'))
            columns.append(ColumnDT('nosaplradb'))
            columns.append(ColumnDT('nosaplrakr'))
            columns.append(ColumnDT('nosapaset'))
            columns.append(ColumnDT('pph_id'))
            
            sap1db = aliased(Sap)
            sap1kr = aliased(Sap)
            sap2db = aliased(Sap)
            sap2kr = aliased(Sap)
            sap3   = aliased(Sap)
            
            query = DBSession.query(RekeningSap.id,
                                    Rekening.kode.label('norek'),
                                    Rekening.nama.label('nmrek'),
                                    sap1db.kode.label('nosaplodb'),
                                    sap1kr.kode.label('nosaplokr'),
                                    sap2db.kode.label('nosaplradb'),
                                    sap2kr.kode.label('nosaplrakr'),
                                    sap3.kode.label('nosapaset'),
                                    RekeningSap.pph_id,
                              ).outerjoin(Rekening, RekeningSap.rekening_id == Rekening.id
                              ).outerjoin(sap1db, RekeningSap.db_lo_sap_id  == sap1db.id
                              ).outerjoin(sap1kr, RekeningSap.kr_lo_sap_id  == sap1kr.id
                              ).outerjoin(sap2db, RekeningSap.db_lra_sap_id == sap2db.id
                              ).outerjoin(sap2kr, RekeningSap.kr_lra_sap_id == sap2kr.id
                              ).outerjoin(sap3, RekeningSap.neraca_sap_id   == sap3.id)
                              
            rowTable = DataTables(req, RekeningSap, query, columns)
            return rowTable.output_result()
            
        elif url_dict['act']=='grid1':
            cari = 'cari' in params and params['cari'] or ''
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('norek'))
            columns.append(ColumnDT('nmrek'))
            columns.append(ColumnDT('nosaplodb'))
            columns.append(ColumnDT('nosaplokr'))
            columns.append(ColumnDT('nosaplradb'))
            columns.append(ColumnDT('nosaplrakr'))
            columns.append(ColumnDT('nosapaset'))
            columns.append(ColumnDT('pph_id'))
            
            sap1db = aliased(Sap)
            sap1kr = aliased(Sap)
            sap2db = aliased(Sap)
            sap2kr = aliased(Sap)
            sap3   = aliased(Sap)
            
            query = DBSession.query(RekeningSap.id,
                                    Rekening.kode.label('norek'),
                                    Rekening.nama.label('nmrek'),
                                    sap1db.kode.label('nosaplodb'),
                                    sap1kr.kode.label('nosaplokr'),
                                    sap2db.kode.label('nosaplradb'),
                                    sap2kr.kode.label('nosaplrakr'),
                                    sap3.kode.label('nosapaset'),
                                    RekeningSap.pph_id,
                              ).outerjoin(Rekening, RekeningSap.rekening_id == Rekening.id
                              ).outerjoin(sap1db, RekeningSap.db_lo_sap_id  == sap1db.id
                              ).outerjoin(sap1kr, RekeningSap.kr_lo_sap_id  == sap1kr.id
                              ).outerjoin(sap2db, RekeningSap.db_lra_sap_id == sap2db.id
                              ).outerjoin(sap2kr, RekeningSap.kr_lra_sap_id == sap2kr.id
                              ).outerjoin(sap3, RekeningSap.neraca_sap_id   == sap3.id
                              ).filter(or_(Rekening.kode.ilike('%%%s%%' % cari),
                                           Rekening.nama.ilike('%%%s%%' % cari),
                                           RekeningSap.pph_id.ilike('%%%s%%' % cari)))
                              
            rowTable = DataTables(req, RekeningSap, query, columns)
            return rowTable.output_result()

    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(RekeningSap).filter_by(id=uid)
            rekeningsap = q.first()
        else:
            rekeningsap = None
            
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind(pph=PPH)
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, user, row=None):
        if not row:
            row = RekeningSap()
        row.from_dict(values)
        
        DBSession.add(row)
        DBSession.flush()
        return row
        
    def save_request(self, values, row=None):
        if 'id' in self.request.matchdict:
            values['id'] = self.request.matchdict['id']
        row = self.save(values, self.request.user, row)
        self.request.session.flash('Rekening SAP sudah disimpan.')
        
    def route_list(self):
        return HTTPFound(location=self.request.route_url('rekening-sap'))
        
    def session_failed(self, session_name):
        r = dict(form=self.session[session_name])
        del self.session[session_name]
        return r
        
    @view_config(route_name='rekening-sap-add', renderer='templates/rekening-sap/add.pt',
                 permission='add')
    def view_sap_add(self):
        req = self.request
        ses = self.session
        form = self.get_form(AddSchema)
        if req.POST:
            if 'simpan' in req.POST:
                controls = req.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form)
                    #req.session[SESS_ADD_FAILED] = e.render()               
                    #return HTTPFound(location=req.route_url('rekening-sap-add'))
                self.save_request(dict(controls))
            return self.route_list()
        elif SESS_ADD_FAILED in req.session:
            return dict(form=form)
            #return self.session_failed(SESS_ADD_FAILED)
        #return dict(form=form.render())
        rowd={}
        form.set_appstruct(rowd)                  
        return dict(form=form)
        
    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(RekeningSap).filter_by(id=self.request.matchdict['id'])
        
    def id_not_found(self):    
        msg = 'Rekening SAP ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()
        
    @view_config(route_name='rekening-sap-edit', renderer='templates/rekening-sap/add.pt',
                 permission='edit')
    def view_rekening_edit(self):
        request   = self.request
        row       = self.query_id().first()
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
                self.save_request(dict(controls), row)
            return self.route_list()
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)

        values = row.to_dict()
        r=DBSession.query(Rekening).filter(Rekening.id==row.rekening_id).first()
        if r:
            values['rekening_kd'] = r.kode
            values['rekening_nm'] = r.nama
        else:
            values['rekening_kd'] = ""
            values['rekening_nm'] = ""

        a=DBSession.query(Sap).filter(Sap.id==row.db_lo_sap_id).first()
        if a:
            values['db_lo_sap_kd'] = a.kode
            values['db_lo_sap_nm'] = a.nama
        else:
            values['db_lo_sap_id'] = 0
            values['db_lo_sap_kd'] = ""
            values['db_lo_sap_nm'] = ""

        aa=DBSession.query(Sap).filter(Sap.id==row.kr_lo_sap_id).first()
        if aa:
            values['kr_lo_sap_kd'] = aa.kode
            values['kr_lo_sap_nm'] = aa.nama
        else:
            values['kr_lo_sap_id'] = 0
            values['kr_lo_sap_kd'] = ""
            values['kr_lo_sap_nm'] = ""

        b=DBSession.query(Sap).filter(Sap.id==row.db_lra_sap_id).first()
        if b:
            values['db_lra_sap_kd'] = b.kode
            values['db_lra_sap_nm'] = b.nama
        else:
            values['db_lra_sap_id'] = 0
            values['db_lra_sap_kd'] = ""
            values['db_lra_sap_nm'] = ""

        bb=DBSession.query(Sap).filter(Sap.id==row.kr_lra_sap_id).first()
        if bb:
            values['kr_lra_sap_kd'] = bb.kode
            values['kr_lra_sap_nm'] = bb.nama
        else:
            values['kr_lra_sap_id'] = 0
            values['kr_lra_sap_kd'] = ""
            values['kr_lra_sap_nm'] = ""
        
        c=DBSession.query(Sap).filter(Sap.id==row.neraca_sap_id).first()
        if c:
            values['neraca_sap_kd'] = c.kode
            values['neraca_sap_nm'] = c.nama
        else:
            values['neraca_sap_id'] = 0
            values['neraca_sap_kd'] = ""
            values['neraca_sap_nm'] = ""
        
        form.set_appstruct(values)
        return dict(form=form)
        
    ##########
    # Delete #
    ##########    
    @view_config(route_name='rekening-sap-delete', renderer='templates/rekening-sap/delete.pt',
                 permission='delete')
    def view_sap_delete(self):
        request = self.request
        q       = self.query_id()
        row     = q.first()
        
        if not row:
            return self.id_not_found(request)
            
        form = Form(colander.Schema(), buttons=('hapus','batal'))
        if request.POST:
            if 'hapus' in request.POST:
                msg = 'Rekening SAP ID %d sudah dihapus.' % (row.id)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'Rekening SAP ID %d tidak dapat dihapus.' % (row.id)
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row, form=form.render())
        