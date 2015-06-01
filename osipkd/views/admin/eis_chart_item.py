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
from osipkd.models.eis import ChartItem, Chart
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews
    

SESS_ADD_FAILED = 'Tambah eis-chart-item gagal'
SESS_EDIT_FAILED = 'Edit eis-chart-item gagal'

def deferred_source_type(node, kw):
    values = kw.get('daftar_status', [])
    return widget.SelectWidget(values=values)
    
SOURCE_TYPE = (
    ('target', 'Target'),
    ('realisasi', 'Realisasi'),
    )
    
class Blok1(colander.Schema):
    value_1 = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    missing = 0)
                    
    value_2 = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    missing = 0)
                
    value_3 = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    missing = 0)
    value_4   = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    missing = 0)
    value_5   = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    missing = 0)
    value_6   = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    missing = 0)
                    
class Blok2(colander.Schema):
    value_7 = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    missing = 0)
                    
    value_8 = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    missing = 0)
                
    value_9 = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    missing = 0)
    value10   = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    missing = 0)
    value11   = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    missing = 0)
    value12   = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    missing = 0)            

                    
class AddSchema(colander.Schema):
    kode  = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=18),
                    oid='kode')
                    
    nama = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=128),
                    oid = 'nama')
    source_type = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=32),
                    widget=widget.SelectWidget(values=SOURCE_TYPE)) # deferred_source_type)
    is_sum = colander.SchemaNode(
                    colander.Boolean(),
                    title = 'Jumlah Kumulatif'
                    ) # deferred_source_type)
                    
    rekening_kd = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=128),
                    missing=colander.drop)
                    
    color       = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=6),
                    missing=colander.drop)
    highlight       = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=6),
                    missing=colander.drop)
                    
                    
                    
    values_1 = Blok1()
    values_2 = Blok2()
    

class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))
            
class view_eis_chart_item(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='eis-chart-item', renderer='templates/eis-chart-item/list.pt',
                 permission='read')
    def view_list(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        
        id = url_dict['chart_id']
        
        return dict(project='EIS', rows=Chart.query_id(id).first())
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='eis-chart-item-act', renderer='json',
                 permission='read')
    def eis_chart_item_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        chart_id = url_dict['chart_id']
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('kode'))
            columns.append(ColumnDT('nama'))
            columns.append(ColumnDT('source_type'))
            columns.append(ColumnDT('value_1',  filter=self._number_format))
            columns.append(ColumnDT('value_2',  filter=self._number_format))
            columns.append(ColumnDT('value_3',  filter=self._number_format))
            columns.append(ColumnDT('value_4',  filter=self._number_format))
            columns.append(ColumnDT('value_5',  filter=self._number_format))
            columns.append(ColumnDT('value_6',  filter=self._number_format))

            query = DBSession.query(ChartItem).filter(ChartItem.chart_id==chart_id)
            rowTable = DataTables(req, ChartItem, query, columns)
            return rowTable.output_result()
        
    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(ChartItem).filter_by(id=uid)
            row = q.first()
        else:
            row = None
                
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind(source_type=SOURCE_TYPE)
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, user, row=None):
        if not row:
            row = ChartItem()
            row.created = datetime.now()
            row.create_uid = user.id
        row.from_dict(values)
        row.updated = datetime.now()
        row.update_uid = user.id
        row.is_sum   = 'is_sum' in values and values['is_sum'] and 1 or 0
        DBSession.add(row)
        DBSession.flush()
        return row
        
    def save_request(self, values, row=None):
        if 'id' in self.request.matchdict:
            values['id'] = self.request.matchdict['id']
        row = self.save(values, self.request.user, row)
        self.request.session.flash('ChartItem sudah disimpan.')
            
    def route_list(self,chart_id):
        return HTTPFound(location=self.request.route_url('eis-chart-item',chart_id=chart_id) )
        
    def session_failed(self, session_name):
            
        #r = dict(form=self.session[session_name])
        del self.session[session_name]
        #return r
        
    @view_config(route_name='eis-chart-item-add', renderer='templates/eis-chart-item/add.pt',
                 permission='add')
    def view_eis_chart_item_add(self):
        req = self.request
        ses = self.session
        form = self.get_form(AddSchema)
        chart_id = req.matchdict['chart_id']
        if req.POST:
            if 'simpan' in req.POST:
                controls = req.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    #req.session[SESS_ADD_FAILED] = e.render()     
                    #form.set_appstruct(rowd)
                    return dict(form=form)
                    #return HTTPFound(location=req.route_url('eis-chart-item-add'))
                self.save_request(dict(controls, chart_id=chart_id))
            return self.route_list(chart_id)
        elif SESS_ADD_FAILED in req.session:
            return dict(form=form)
        
            #return self.session_failed(SESS_ADD_FAILED)
        return dict(form=form)

        
    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(ChartItem).filter_by(id=self.request.matchdict['id'])
        
    def id_not_found(self,chart_id):    
        msg = 'ChartItem ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list(chart_id)

    @view_config(route_name='eis-chart-item-edit', renderer='templates/eis-chart-item/add.pt',
                 permission='edit')
    def view_eis_chart_item_edit(self):
        request = self.request
        row = self.query_id().first()
        chart_id = request.matchdict['chart_id']
        if not row:
            return id_not_found(request)
        #values = row.to_dict()
        rowd={}
        rowd['id']          = row.id
        rowd['kode']        = row.kode
        rowd['nama']        = row.nama
        rowd['source_type'] = row.source_type
        rowd['rekening_kd'] = row.rekening_kd
        rowd['color']       = row.color
        rowd['highlight']       = row.highlight
        rowd['values_1']       = {}
        rowd['values_1']['value_1']  = row.value_1
        rowd['values_1']['value_2']  = row.value_2
        rowd['values_1']['value_3']  = row.value_3
        rowd['values_1']['value_4']  = row.value_4
        rowd['values_1']['value_5']  = row.value_5
        rowd['values_1']['value_6']  = row.value_6
        rowd['values_2']             = {}
        rowd['values_2']['value_7']  = row.value_7
        rowd['values_2']['value_8']  = row.value_8
        rowd['values_2']['value_9']  = row.value_9
        rowd['values_2']['value10']  = row.value10
        rowd['values_2']['value11']  = row.value11
        rowd['values_2']['value12']  = row.value12        
        form = self.get_form(EditSchema)
        form.set_appstruct(rowd)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                print controls
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form)
                    #request.session[SESS_EDIT_FAILED] = e.render()               
                    #return HTTPFound(location=request.route_url('eis-chart-item-edit',
                    #                  id=row.id))
                self.save_request(dict(controls, chart_id=chart_id), row)
            return self.route_list(chart_id)
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)
        return dict(form=form)

    ##########
    # Delete #
    ##########    
    @view_config(route_name='eis-chart-item-delete', renderer='templates/eis-chart-item/delete.pt',
                 permission='delete')
    def view_eis_chart_item_delete(self):
        request = self.request
        chart_id = request.matchdict['chart_id']
        q = self.query_id()
        row = q.first()
        
        if not row:
            return self.id_not_found(request)
        form = Form(colander.Schema(), buttons=('hapus','batal'))
        if request.POST:
            if 'hapus' in request.POST:
                msg = 'ChartItem ID %d %s sudah dihapus.' % (row.id, row.nama)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'ChartItem ID %d %s tidak dapat dihapus.' % (row.id, row.nama)
                request.session.flash(msg)
            return self.route_list(chart_id)
        return dict(row=row,
                     form=form.render())

