import os
import uuid
import colander

from datetime import datetime

from sqlalchemy import not_, func, or_
from sqlalchemy.sql.expression import and_

from ziggurat_foundations.models import groupfinder
from pyramid.view import (view_config,)
from pyramid.httpexceptions import (HTTPFound,)
from osipkd.views.base_view import BaseViews

from deform import (Form, widget,ValidationFailure,)
from datatables import ColumnDT, DataTables

from osipkd.tools import row2dict, xls_reader
from osipkd.models import (DBSession,)
from osipkd.models.pemda_model import Sap, Rekening, RekeningSap
from osipkd.models.apbd_anggaran import Kegiatan, KegiatanSub, KegiatanItem


SESS_ADD_FAILED = 'Tambah sap gagal'
SESS_EDIT_FAILED = 'Edit sap gagal'

rek_widget = widget.AutocompleteInputWidget(
        size=60,
        values = '/sap/act/headofnama',
        min_length=1)

            
class AddSchema(colander.Schema):
    parent_id  = colander.SchemaNode(
                    colander.String(),
                    widget = widget.HiddenWidget(),
                    missing = colander.drop,
                    oid = "parent_id"
                    )
    parent_nm = colander.SchemaNode(
                    colander.String(),
                    widget = rek_widget,
                    missing = colander.drop,
                    oid = "parent_nm",
                    title = "Header"
                    )
    tahun = colander.SchemaNode(
                    colander.Integer(),)
    kode = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=18)
                    )
    nama = colander.SchemaNode(
                    colander.String())
    disabled = colander.SchemaNode(
                    colander.Boolean())
                    
class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))
            
class view_rekening(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='sap', renderer='templates/sap/list.pt',
                 permission='read')
    def view_list(self):
        return dict(project="osipkd")
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='sap-act', renderer='json',
                 permission='view')
    def gaji_sap_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('kode'))
            columns.append(ColumnDT('nama'))
            columns.append(ColumnDT('level_id'))
            columns.append(ColumnDT('disabled'))
 
            query = DBSession.query(Sap.id,
                                    Sap.kode,
                                    Sap.nama,
                                    Sap.level_id,
                                    Sap.disabled)
            
            rowTable = DataTables(req, Sap, query, columns)
            return rowTable.output_result()
            
        elif url_dict['act']=='headofkode1':
            term = 'term' in params and params['term'] or ''            
            q = DBSession.query(Sap.id, 
                                Sap.kode, 
                                Sap.nama, 
                      ).filter(or_(Sap.kode.ilike('8%%%s%%' % term),
                                   Sap.kode.ilike('9%%%s%%' % term),
                                   Sap.kode.ilike('1%%%s%%' % term))
                      )
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[1]
                d['kode']        = k[1]
                d['nama']        = k[2]
                r.append(d)
            print '****----****',r                
            return r
            
        elif url_dict['act']=='headofnama1':
            term = 'term' in params and params['term'] or ''            
            q = DBSession.query(Sap.id, 
                                Sap.kode, 
                                Sap.nama, 
                      ).filter(Sap.nama.ilike('%%%s%%' % term),
                               or_(Sap.kode.ilike('8%%'),
                                   Sap.kode.ilike('9%%'),
                                   Sap.kode.ilike('1%%'))
                      )
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[2]
                d['kode']        = k[1]
                d['nama']        = k[2]
                r.append(d)
            print '****----****',r                
            return r
        
        elif url_dict['act']=='headofkode11':
            term = 'term' in params and params['term'] or ''            
            q = DBSession.query(Sap.id, 
                                Sap.kode, 
                                Sap.nama, 
                      ).filter(or_(Sap.kode.ilike('8%%%s%%' % term),
                                   Sap.kode.ilike('9%%%s%%' % term),
                                   Sap.kode.ilike('2%%%s%%' % term))
                      )
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[1]
                d['kode']        = k[1]
                d['nama']        = k[2]
                r.append(d)
            print '****----****',r                
            return r
            
        elif url_dict['act']=='headofnama11':
            term = 'term' in params and params['term'] or ''            
            q = DBSession.query(Sap.id, 
                                Sap.kode, 
                                Sap.nama, 
                      ).filter(Sap.nama.ilike('%%%s%%' % term),
                               or_(Sap.kode.ilike('8%%'),
                                   Sap.kode.ilike('9%%'),
                                   Sap.kode.ilike('2%%'))
                      )
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[2]
                d['kode']        = k[1]
                d['nama']        = k[2]
                r.append(d)
            print '****----****',r                
            return r
                
        elif url_dict['act']=='headofkode2':
            term = 'term' in params and params['term'] or ''            
            q = DBSession.query(Sap.id, 
                                Sap.kode, 
                                Sap.nama, 
                      ).filter(or_(Sap.kode.ilike('4%%%s%%' % term),
                                   Sap.kode.ilike('5%%%s%%' % term),
                                   Sap.kode.ilike('6%%%s%%' % term),
                                   Sap.kode.ilike('7%%%s%%' % term),
                                   Sap.kode.ilike('0%%%s%%' % term))
                      )
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[1]
                d['kode']        = k[1]
                d['nama']        = k[2]
                r.append(d)
            print '****----****',r                
            return r
            
        elif url_dict['act']=='headofnama2':
            term = 'term' in params and params['term'] or ''            
            q = DBSession.query(Sap.id, 
                                Sap.kode, 
                                Sap.nama, 
                      ).filter(Sap.nama.ilike('%%%s%%' % term),
                               or_(Sap.kode.ilike('4%%'),
                                   Sap.kode.ilike('5%%'),
                                   Sap.kode.ilike('6%%'),
                                   Sap.kode.ilike('7%%'),
                                   Sap.kode.ilike('0%%'))
                      )
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[2]
                d['kode']        = k[1]
                d['nama']        = k[2]
                r.append(d)
            print '****----****',r                
            return r
            
        elif url_dict['act']=='headofkode3':
            term = 'term' in params and params['term'] or ''            
            q = DBSession.query(Sap.id, 
                                Sap.kode, 
                                Sap.nama, 
                      ).filter(or_(Sap.kode.ilike('1%%%s%%' % term),
                                   Sap.kode.ilike('2%%%s%%' % term),
                                   Sap.kode.ilike('3%%%s%%' % term))
                      )
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[1]
                d['kode']        = k[1]
                d['nama']        = k[2]
                r.append(d)
            print '****----****',r                
            return r
            
        elif url_dict['act']=='headofnama3':
            term = 'term' in params and params['term'] or ''            
            q = DBSession.query(Sap.id, 
                                Sap.kode, 
                                Sap.nama, 
                      ).filter(Sap.nama.ilike('%%%s%%' % term),
                               or_(Sap.kode.ilike('1%%'),
                                   Sap.kode.ilike('2%%'),
                                   Sap.kode.ilike('3%%'))
                      )
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[2]
                d['kode']        = k[1]
                d['nama']        = k[2]
                r.append(d)
            print '****----****',r                
            return r
        
        elif url_dict['act']=='headofkode4':
            term = 'term' in params and params['term'] or ''
            rekening_id = 'rekening_id' in params and params['rekening_id'] or 0
                        
            q = DBSession.query(Sap.id, 
                                Sap.kode, 
                                Sap.nama, 
                      ).filter(RekeningSap.rekening_id   == rekening_id,
                               RekeningSap.rekening_id   == Rekening.id,
                               RekeningSap.db_lo_sap_id  == Sap.id,
                               RekeningSap.kr_lo_sap_id  == Sap.id,
                               RekeningSap.db_lra_sap_id == Sap.id,
                               RekeningSap.kr_lra_sap_id == Sap.id,
                               RekeningSap.neraca_sap_id == Sap.id,
                               Sap.kode.ilike('%%%s%%' % term))
            rows = q.all()
            
            if not rows:
                return {'success':False, 'msg':'SAP tidak ditemukan'}
                
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[1]
                d['kode']        = k[1]
                d['nama']        = k[2]
                r.append(d)
            print '****----****',r                
            return r
        
        elif url_dict['act']=='headofnama4':
            term = 'term' in params and params['term'] or ''
            rekening_id = 'rekening_id' in params and params['rekening_id'] or 0
                        
            q = DBSession.query(Sap.id, 
                                Sap.kode, 
                                Sap.nama, 
                      ).filter(RekeningSap.rekening_id   == rekening_id,
                               RekeningSap.rekening_id   == Rekening.id,
                               RekeningSap.db_lo_sap_id  == Sap.id,
                               RekeningSap.kr_lo_sap_id  == Sap.id,
                               RekeningSap.db_lra_sap_id == Sap.id,
                               RekeningSap.kr_lra_sap_id == Sap.id,
                               RekeningSap.neraca_sap_id == Sap.id,
                               Sap.nama.ilike('%%%s%%' % term))
            rows = q.all()
            
            if not rows:
                return {'success':False, 'msg':'SAP tidak ditemukan'}
                
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[1]
                d['kode']        = k[1]
                d['nama']        = k[2]
                r.append(d)
            print '****----****',r                
            return r
        
        elif url_dict['act']=='headofkode12':
            term = 'term' in params and params['term'] or ''            
            q = DBSession.query(Sap.id, 
                                Sap.kode, 
                                Sap.nama, 
                      ).filter(Sap.kode.ilike('%%%s%%' % term))
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[1]
                d['kode']        = k[1]
                d['nama']        = k[2]
                r.append(d)
            print '****----****',r                
            return r
        
        elif url_dict['act']=='headofnama12':
            term = 'term' in params and params['term'] or ''            
            q = DBSession.query(Sap.id, 
                                Sap.kode, 
                                Sap.nama, 
                      ).filter(Sap.nama.ilike('%%%s%%' % term))
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[2]
                d['kode']        = k[1]
                d['nama']        = k[2]
                r.append(d)
            print '****----****',r                
            return r
            
    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(Sap).filter_by(id=uid)
            sap = q.first()
        else:
            sap = None
            
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind()
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, user, row=None):
        if not row:
            row = Sap()
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
        if 'parent_id' in values and values['parent_id']:
            values['level_id'] = Sap.get_next_level(values['parent_id'])
        else:
            values['level_id'] = 1
            values['parent_id'] = None
        row = self.save(values, self.request.user, row)
        self.request.session.flash('sap sudah disimpan.')
        
    def route_list(self):
        return HTTPFound(location=self.request.route_url('sap'))
        
    def session_failed(self, session_name):
        r = dict(form=self.session[session_name])
        del self.session[session_name]
        return r
        
    @view_config(route_name='sap-add', renderer='templates/sap/add.pt',
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
                    req.session[SESS_ADD_FAILED] = e.render()               
                    return HTTPFound(location=req.route_url('sap-add'))
                self.save_request(dict(controls))
            return self.route_list()
        elif SESS_ADD_FAILED in req.session:
            return self.session_failed(SESS_ADD_FAILED)
        return dict(form=form.render())
        
    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(Sap).filter_by(id=self.request.matchdict['id'])
        
    def id_not_found(self):    
        msg = 'sap ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()
        
    @view_config(route_name='sap-edit', renderer='templates/sap/edit.pt',
                 permission='edit')
    def view_rekening_edit(self):
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
                    return HTTPFound(location=request.route_url('sap-edit',
                                      id=row.id))
                self.save_request(dict(controls), row)
            return self.route_list()
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)
        values = row.to_dict()
        values['parent_nm']= row.parent.nama if values['parent_id'] else ""
        return dict(form=form.render(appstruct=values))
        
    ##########
    # Delete #
    ##########    
    @view_config(route_name='sap-delete', renderer='templates/sap/delete.pt',
                 permission='delete')
    def view_sap_delete(self):
        request = self.request
        q = self.query_id()
        row = q.first()
        if not row:
            return self.id_not_found(request)
        form = Form(colander.Schema(), buttons=('hapus','batal'))
        if request.POST:
            if 'hapus' in request.POST:
                msg = 'sap ID %d %s sudah dihapus.' % (row.id, row.nama)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'sap ID %d %s tidak dapat dihapus.' % (row.id, row.nama)
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row,
                     form=form.render())