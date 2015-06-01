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
from osipkd.models.apbd import Jurnal, JurnalItem
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah ak-report-lkpj gagal'
SESS_EDIT_FAILED = 'Edit ak-report-lkpj gagal'
            
class view_ak_jurnal_item(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='ak-report-lkpj', renderer='templates/ak-report-lkpj/list.pt',
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
    @view_config(route_name='ak-report-lkpj-act', renderer='json',
                 permission='read')
    def view_act(self):
        pass
        
