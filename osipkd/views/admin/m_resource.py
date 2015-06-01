"""import os
import uuid
from ..tools import row2dict, xls_reader
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
from ..models import (
    DBSession,
    Resource
    )
    
from datatables import ColumnDT, DataTables
from ..views.base_view import BaseViews
    

SESS_ADD_FAILED = 'Tambah resource gagal'
SESS_EDIT_FAILED = 'Edit resource gagal'


                
class AddSchema(colander.Schema):
    resource_name = colander.SchemaNode(
                    colander.String())
                    
    resource_type = colander.SchemaNode(
                    colander.String())
                    
class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))
            
class view_resource(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='resource', renderer='templates/resource/list.pt',
                 permission='read')
    def view_list(self):
        return dict(a={})
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='resource-act', renderer='json',
                 permission='read')
    def resource_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('resource_id'))
            columns.append(ColumnDT('resource_name'))
            columns.append(ColumnDT('resource_type'))
            columns.append(ColumnDT('ordering'))
            query = DBSession.query(Resource)
            rowTable = DataTables(req, Resource, query, columns)
            return rowTable.output_result()
            
        
    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(Resource).filter_by(id=uid)
            resource = q.first()
        else:
            resource = None
                
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind()
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, user, row=None):
        if not row:
            row = Resource()
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
        self.request.session.flash('resource sudah disimpan.')
            
    def route_list(self):
        return HTTPFound(location=self.request.route_url('resource'))
        
    def session_failed(self, session_name):
        r = dict(form=self.session[session_name])
        del self.session[session_name]
        return r
        
    @view_config(route_name='resource-add', renderer='templates/resource/add.pt',
                 permission='add')
    def view_resource_add(self):
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
                    return HTTPFound(location=req.route_url('resource-add'))
                self.save_request(dict(controls))
            return self.route_list()
        elif SESS_ADD_FAILED in req.session:
            return self.session_failed(SESS_ADD_FAILED)
        return dict(form=form.render())

        
    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(Resource).filter_by(id=self.request.matchdict['id'])
        
    def id_not_found(self):    
        msg = 'resource ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()

    @view_config(route_name='resource-edit', renderer='templates/resource/edit.pt',
                 permission='edit')
    def view_resource_edit(self):
        request = self.request
        row = self.query_id().first()
        if not row:
            return id_not_found(request)
        form = self.get_form(EditSchema)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                print controls
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    request.session[SESS_EDIT_FAILED] = e.render()               
                    return HTTPFound(location=request.route_url('resource-edit',
                                      id=row.id))
                self.save_request(dict(controls), row)
            return self.route_list()
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)
        values = row.to_dict()
        return dict(form=form.render(appstruct=values))

    ##########
    # Delete #
    ##########    
    @view_config(route_name='resource-delete', renderer='templates/resource/delete.pt',
                 permission='delete')
    def view_resource_delete(self):
        request = self.request
        q = self.query_id()
        row = q.first()
        
        if not row:
            return self.id_not_found(request)
        form = Form(colander.Schema(), buttons=('hapus','batal'))
        if request.POST:
            if 'hapus' in request.POST:
                msg = 'resource ID %d %s sudah dihapus.' % (row.id, row.description)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'resource ID %d %s tidak dapat dihapus.' % (row.id, row.description)
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row,
                     form=form.render())

"""