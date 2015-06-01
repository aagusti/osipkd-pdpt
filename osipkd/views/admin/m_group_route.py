import os
import uuid
from osipkd.tools import row2dict, xls_reader
from datetime import datetime
from sqlalchemy import not_, func
from pyramid.view import (
    view_config,
    )
from pyramid.httpexceptions import (
    HTTPFound,
    )
import colander
from deform import (
    Form,
    widget,
    ValidationFailure,
    )
from osipkd.models import (DBSession,)

from osipkd.models import GroupRoutePermission, Group, Route
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews
    

SESS_ADD_FAILED = 'Tambah routes gagal'
SESS_EDIT_FAILED = 'Edit routes gagal'
def deferred_source_type(node, kw):
    values = kw.get('perm_choice', [])
    return widget.SelectWidget(values=values)
               
class AddSchema(colander.Schema):
    group_widget = widget.AutocompleteInputWidget(
            size=60,
            values = '/group/act/headofnama',
            min_length=3)

    route_widget = widget.AutocompleteInputWidget(
            size=60,
            values = '/routes/act/headof',
            min_length=3)

    group_id  = colander.SchemaNode(
                    colander.Integer(),
                    widget = widget.HiddenWidget(),
                    oid = 'group_id')
    group_nm  = colander.SchemaNode(
                    colander.String(),
                    widget = group_widget,
                    oid = 'group_nm')
    route_id  = colander.SchemaNode(
                    colander.Integer(),
                    widget = widget.HiddenWidget(),
                    oid = 'route_id')
    route_nm  = colander.SchemaNode(
                    colander.String(),
                    widget = route_widget,
                    title ='Route',
                    oid = 'route_nm')

class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))
            
class view_routes(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='group-routes', renderer='templates/group-routes/list.pt',
                 permission='read')
    def view_list(self):
        return dict(a={})
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='group-routes-act', renderer='json',
                 permission='read')
    def gaji_routes_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('group_id'))
            columns.append(ColumnDT('route_id'))
            columns.append(ColumnDT('groups.group_name'))
            columns.append(ColumnDT('routes.nama'))
            columns.append(ColumnDT('routes.path'))
            query = DBSession.query(GroupRoutePermission).join(Group).join(Route)
            rowTable = DataTables(req, GroupRoutePermission, query, columns)
            return rowTable.output_result()
            
        elif url_dict['act']=='changeid':
            row = GroupRoutePermission.get_by_id('routes_id' in params and params['routes_id'] or 0)
            if row:
                ses['routes_id']=row.id
                ses['routes_kd']=row.kode
                ses['routes_nm']=row.nama
                return {'success':True}
                
            

    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(GroupRoutePermission).filter_by(id=uid)
            routes = q.first()
        else:
            routes = None
                
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind()
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, user, row=None):
        if not row:
            row = GroupRoutePermission()
            row.created = datetime.now()
            row.create_uid = user.id
        row.from_dict(values)
        row.updated = datetime.now()
        row.update_uid = user.id
        row.disabled = 'disabled' in values and values['disabled'] and 1 or 0
        DBSession.add(row)
        DBSession.flush()
        return row
        
    def save_request(self, values, row=None):
        if 'id' in self.request.matchdict:
            values['id'] = self.request.matchdict['id']
        row = self.save(values, self.request.user, row)
        self.request.session.flash('routes sudah disimpan.')
            
    def routes_list(self):
        return HTTPFound(location=self.request.route_url('group-routes'))
        
    def session_failed(self, session_name):
        r = dict(form=self.session[session_name])
        del self.session[session_name]
        return r
        
    @view_config(route_name='group-routes-add', renderer='templates/group-routes/add.pt',
                 permission='add')
    def view_routes_add(self):
        req = self.request
        ses = self.session
        form = self.get_form(AddSchema)
        if req.POST:
            if 'simpan' in req.POST:
                controls = req.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    req.session[SESS_ADD_FAILED] = e.render()               
                    return HTTPFound(location=req.route_url('group-routes-add'))
                self.save_request(dict(controls))
            return self.routes_list()
        elif SESS_ADD_FAILED in req.session:
            return self.session_failed(SESS_ADD_FAILED)
        return dict(form=form.render())

        
    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(GroupRoutePermission).filter_by(group_id=self.request.matchdict['id'],
                  route_id=self.request.matchdict['id2'])
        
    def id_not_found(self):    
        msg = 'group ID %s routes ID %s Tidak Ditemukan.' % (self.request.matchdict['id'], self.request.matchdict['id2'])
        request.session.flash(msg, 'error')
        return routes_list()

    ##########
    # Delete #
    ##########    
    @view_config(route_name='group-routes-delete', renderer='templates/group-routes/delete.pt',
                 permission='delete')
    def view_routes_delete(self):
        request = self.request
        q = self.query_id()
        row = q.first()
        
        if not row:
            return self.id_not_found(request)
        form = Form(colander.Schema(), buttons=('hapus','batal'))
        if request.POST:
            if 'hapus' in request.POST:
                msg = 'group ID %d routes  ID %d sudah dihapus.' % (row.group_id, row.route_id)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'group ID %d routes  ID %d  tidak dapat dihapus.' % (row.id, row.route_id)
                request.session.flash(msg)
            return self.routes_list()
        return dict(row=row,
                     form=form.render())

