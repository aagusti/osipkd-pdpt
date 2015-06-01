import os
import uuid
import colander

from datetime import datetime

from sqlalchemy import not_, func
from sqlalchemy.sql.expression import and_

from ziggurat_foundations.models import groupfinder
from pyramid.view import (view_config,)
from pyramid.httpexceptions import (HTTPFound,)
from osipkd.views.base_view import BaseViews

from deform import (Form, widget,ValidationFailure,)
from datatables import ColumnDT, DataTables

from osipkd.tools import row2dict, xls_reader
from osipkd.models import (DBSession,)
from osipkd.models.pemda_model import Rekening
from osipkd.models.apbd_anggaran import Kegiatan, KegiatanSub, KegiatanItem


SESS_ADD_FAILED = 'Tambah rekening gagal'
SESS_EDIT_FAILED = 'Edit rekening gagal'

rek_widget = widget.AutocompleteInputWidget(
        size=60,
        values = '/rekening/act/headofnama',
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
    @view_config(route_name='rekening', renderer='templates/rekening/list.pt',
                 permission='read')
    def view_list(self):
        return dict(project="osipkd")
    ##########                    
    # Action #
    ##########    
    def get_kode_dict(self, term, prefix=''):
        q = DBSession.query(Rekening.id, Rekening.kode, Rekening.nama
                  ).filter(Rekening.kode.ilike('%s%%' % prefix),
                           Rekening.kode.ilike('%%%s%%' % term))
        rows = q.all()
        r = []
        for k in rows:
            d={}
            d['id']          = k[0]
            d['value']       = k[1]
            d['kode']        = k[1]
            d['nama']        = k[2]
            r.append(d)    
        return r
        
    def get_nama_dict(self, term, prefix=''):
        q = DBSession.query(Rekening.id, Rekening.kode, Rekening.nama
                  ).filter(Rekening.kode.ilike('%s%%' % prefix),
                           Rekening.nama.ilike('%%%s%%' % term))
        rows = q.all()
        r = []
        for k in rows:
            d={}
            d['id']          = k[0]
            d['value']       = k[2]
            d['kode']        = k[1]
            d['nama']        = k[2]
            r.append(d)    
        return r

    @view_config(route_name='rekening-act', renderer='json',
                 permission='view')
    def gaji_rekening_act(self):
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
 
            query = DBSession.query(Rekening)
            
            rowTable = DataTables(req, Rekening, query, columns)
            return rowTable.output_result()
            
        elif url_dict['act']=='headofnama':
            term = 'term' in params and params['term'] or '' 
            return self.get_nama_dict(term)
            
        elif url_dict['act']=='headofkode':
            term = 'term' in params and params['term'] or '' 
            return self.get_kode_dict(term)
            
        #######################################################################
        # ASET 
        elif url_dict['act']=='headofnama2':
            term = 'term' in params and params['term'] or '' 
            return self.get_nama_dict(term,'2')
        elif url_dict['act']=='headofkode2':
            term = 'term' in params and params['term'] or '' 
            return self.get_kode_dict(term,'2')
			
        #######################################################################
        # PENDAPATAN 
        elif url_dict['act']=='headofnama4':
            term = 'term' in params and params['term'] or '' 
            return self.get_nama_dict(term,'4')
        elif url_dict['act']=='headofkode4':
            term = 'term' in params and params['term'] or '' 
            return self.get_kode_dict(term,'4')
        
        #######################################################################
        # BELANJA
        elif url_dict['act']=='headofnama5':
            term = 'term' in params and params['term'] or '' 
            return self.get_nama_dict(term,'5')
        elif url_dict['act']=='headofkode5':
            term = 'term' in params and params['term'] or '' 
            return self.get_kode_dict(term,'5')
        #######################################################################
        # BTL
        elif url_dict['act']=='headofnama51':
            term = 'term' in params and params['term'] or '' 
            return self.get_nama_dict(term,'5.1')
        elif url_dict['act']=='headofkode51':
            term = 'term' in params and params['term'] or '' 
            return self.get_kode_dict(term,'5.1')
        #######################################################################
        # BL
        elif url_dict['act']=='headofnama52':
            term = 'term' in params and params['term'] or '' 
            return self.get_nama_dict(term,'5.2')
        elif url_dict['act']=='headofkode52':
            term = 'term' in params and params['term'] or '' 
            return self.get_kode_dict(term,'5.2')
        #######################################################################
        # PENERIMAAN
        elif url_dict['act']=='headofnama61':
            term = 'term' in params and params['term'] or '' 
            return self.get_nama_dict(term,'6.1')
        elif url_dict['act']=='headofkode61':
            term = 'term' in params and params['term'] or '' 
            return self.get_kode_dict(term,'6.1')            
        #######################################################################
        # PENGELUARAN
        elif url_dict['act']=='headofnama62':
            term = 'term' in params and params['term'] or '' 
            return self.get_nama_dict(term,'6.2')
        elif url_dict['act']=='headofkode62':
            term = 'term' in params and params['term'] or '' 
            return self.get_kode_dict(term,'6.2')            
        
        #######################################################################
        # SPM POTONGAN 
        elif url_dict['act']=='headofkode7':
            term = 'term' in params and params['term'] or '' 
            return self.get_kode_dict(term,'7')

            
        #######################################################################
        # LO PENDAPATAN
        elif url_dict['act']=='headofnama8':
            term = 'term' in params and params['term'] or '' 
            return self.get_nama_dict(term,'8')
            
        #######################################################################
        # LO BELANJA
        elif url_dict['act']=='headofkode8':
            term = 'term' in params and params['term'] or '' 
            return self.get_kode_dict(term,'8')
        elif url_dict['act']=='headofnama9':
            term = 'term' in params and params['term'] or '' 
            return self.get_nama_dict(term,'9')
            
        elif url_dict['act']=='headofkode9':
            term = 'term' in params and params['term'] or '' 
            return self.get_kode_dict(term,'9')
        elif url_dict['act']=='import':
            pass
            
        elif url_dict['act']=='headofkode10':
            term = 'term' in params and params['term'] or ''
            kegiatan_sub_id = 'kegiatan_sub_id' in params and params['kegiatan_sub_id'] or 0
                        
            q = DBSession.query(Rekening.id, 
                                Rekening.kode, 
                                Rekening.nama, 
                      ).join(KegiatanItem, 
                             KegiatanSub,
                      ).filter(KegiatanSub.unit_id == ses['unit_id'],
                               KegiatanSub.tahun_id==ses['tahun'],
                               KegiatanItem.kegiatan_sub_id == KegiatanSub.id,
                               KegiatanItem.rekening_id == Rekening.id,
                               KegiatanItem.kegiatan_sub_id == kegiatan_sub_id,
                               Rekening.kode.ilike('%%%s%%' % term))
            rows = q.all()
            
            if not rows:
                return {'success':False, 'msg':'Rekening tidak ditemukan'}
                
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
            
        elif url_dict['act']=='headofkode11':
            term = 'term' in params and params['term'] or ''            
            q = DBSession.query(Rekening.id, 
                                Rekening.kode, 
                                Rekening.nama, 
                      ).filter(Rekening.kode.ilike('%%%s%%' % term))
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
            q = DBSession.query(Rekening.id, 
                                Rekening.kode, 
                                Rekening.nama, 
                      ).filter(Rekening.nama.ilike('%%%s%%' % term))
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
            q = DBSession.query(Rekening).filter_by(id=uid)
            rekening = q.first()
        else:
            rekening = None
            
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind()
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, user, row=None):
        if not row:
            row = Rekening()
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
            values['level_id'] = Rekening.get_next_level(values['parent_id'])
        else:
            values['level_id'] = 1
            values['parent_id'] = None
        row = self.save(values, self.request.user, row)
        self.request.session.flash('rekening sudah disimpan.')
        
    def route_list(self):
        return HTTPFound(location=self.request.route_url('rekening'))
        
    def session_failed(self, session_name):
        r = dict(form=self.session[session_name])
        del self.session[session_name]
        return r
        
    @view_config(route_name='rekening-add', renderer='templates/rekening/add.pt',
                 permission='add')
    def view_rekening_add(self):
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
                    return HTTPFound(location=req.route_url('rekening-add'))
                self.save_request(dict(controls))
            return self.route_list()
        elif SESS_ADD_FAILED in req.session:
            return self.session_failed(SESS_ADD_FAILED)
        return dict(form=form.render())
        
    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(Rekening).filter_by(id=self.request.matchdict['id'])
        
    def id_not_found(self):    
        msg = 'rekening ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()
        
    @view_config(route_name='rekening-edit', renderer='templates/rekening/edit.pt',
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
                    return HTTPFound(location=request.route_url('rekening-edit',
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
    @view_config(route_name='rekening-delete', renderer='templates/rekening/delete.pt',
                 permission='delete')
    def view_rekening_delete(self):
        request = self.request
        q = self.query_id()
        row = q.first()
        if not row:
            return self.id_not_found(request)
        form = Form(colander.Schema(), buttons=('hapus','batal'))
        if request.POST:
            if 'hapus' in request.POST:
                msg = 'rekening ID %d %s sudah dihapus.' % (row.id, row.nama)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'rekening ID %d %s tidak dapat dihapus.' % (row.id, row.nama)
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row,
                     form=form.render())