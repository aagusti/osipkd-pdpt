import os
import uuid
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from datetime import datetime
from sqlalchemy import not_, func, or_
from pyramid.httpexceptions import (
    HTTPFound,
    )
import colander
from deform import (
    Form,
    widget,
    ValidationFailure,
    )
from osipkd.models import (
    DBSession,
    )
from osipkd.models.efiling_models import Filing

from osipkd.views.base_view import BaseViews

class AddSchema(colander.Schema):
    cari = colander.SchemaNode(
                    colander.String(),
                    title='e-Filling',
                    oid="data") 
                    
class efiling(BaseViews):
  def get_form(self, class_form, row=None):
      schema = class_form()
      schema = schema.bind()
      schema.request = self.request
      if row:
        schema.deserialize(row)
      return Form(schema, buttons=('cari','batal'))
        
  @view_config(route_name="efiling", renderer="templates/home.pt")
  def view_filing(self):
      req = self.request
      ses = req.session
      form = self.get_form(AddSchema)
      page = {}
      rowpage = 1
      cpage = 'page' in req.POST and req.POST['page'] or 1
      if cpage<1:
         cpage = 1
      page['current']=int(cpage)
      offset = (page['current']-1) * rowpage
      if 'data' in req.POST:
          page['row'] = DBSession.query(func.count(Filing.id)).\
                        filter(or_(Filing.tag.like('%%%s%%' % req.POST['data']),
                           Filing.nama.like('%%%s%%' % req.POST['data'])),).scalar() or 0
                           
          rows = DBSession.query(Filing).\
                filter(or_(Filing.tag.like('%%%s%%' % req.POST['data']),
                           Filing.nama.like('%%%s%%' % req.POST['data'])),).\
                           limit(rowpage).offset(offset)
      else:
          rows = DBSession.query(Filing).\
                  limit(rowpage).offset(offset)
          page['row'] = DBSession.query(func.count(Filing.id)).scalar() or 0
                  
      count = page['row'] / int(rowpage)
      page['count'] = count
      if count < page['row']/float(rowpage):
          page['count']=count+1
                  
      return dict(form=form, rows=rows, page=page)
        