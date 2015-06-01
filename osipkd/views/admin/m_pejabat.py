import os
import uuid
from osipkd.tools import row2dict, xls_reader
from datetime import datetime
from sqlalchemy import not_, func, or_
from sqlalchemy.sql.expression import and_
from ziggurat_foundations.models import groupfinder
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
from osipkd.models import (
    DBSession,
    Group
    )
from osipkd.models.pemda_model import Unit
from osipkd.models.apbd_anggaran import Pejabat, Pegawai, Jabatan


from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah pejabat gagal'
SESS_EDIT_FAILED = 'Edit pejabat gagal'

class AddSchema(colander.Schema):
    unit_widget = widget.AutocompleteInputWidget(
            size=60,
            values = '/unit/act/headofnama',
            min_length=1)
                  
    pegawai_widget = widget.AutocompleteInputWidget(
            size=60,
            values = '/pegawai/act/headofnama1',
            min_length=1)
            
    jabatan_widget = widget.AutocompleteInputWidget(
            size=60,
            values = '/jabatan/act/headofnama1',
            min_length=1)

    unit_nm = colander.SchemaNode(
                    colander.String(),
                    widget=unit_widget,
                    oid = "unit_nm")
                    
    unit_id = colander.SchemaNode(
                    colander.Integer(),
                    widget=widget.HiddenWidget(),
                    oid = "unit_id")

    pegawai_nm = colander.SchemaNode(
                    colander.String(),
                    widget=pegawai_widget,
                    oid = "pegawai_nm")

    pegawai_id = colander.SchemaNode(
                    colander.Integer(),
                    widget=widget.HiddenWidget(),
                    titel="Pegawai",
                    oid = "pegawai_id")
                    
    jabatan_nm = colander.SchemaNode(
                    colander.String(),
                    widget=jabatan_widget,
                    oid = "jabatan_nm")

    jabatan_id = colander.SchemaNode(
                    colander.Integer(),
                    widget=widget.HiddenWidget(),
                    titel="Jabatan",
                    oid = "jabatan_id")
                    
    uraian = colander.SchemaNode(
                    colander.String())
                    
    mulai = colander.SchemaNode(
                    colander.Date())
    selesai = colander.SchemaNode(
                    colander.Date())
    disabled = colander.SchemaNode(
                    colander.Boolean())

class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))

class view_pejabat(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='pejabat', renderer='templates/pejabat/list.pt',
                 permission='read')
    def view_list(self):
        return dict(a={})
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='pejabat-act', renderer='json',
                 permission='view')
    def view_act(self):
        ses = self.request.session
        req = self.request
        params   = req.params
        url_dict = req.matchdict
        
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('pnama'))
            columns.append(ColumnDT('jnama'))
            columns.append(ColumnDT('unama'))
            query = DBSession.query(Pejabat.id,
                                    Pegawai.nama.label('pnama'),
                                    Jabatan.nama.label('jnama'),
                                    Unit.nama.label('unama'),
                            ).filter(Pejabat.pegawai_id==Pegawai.id,
                                     Pejabat.jabatan_id==Jabatan.id,
                                     Pejabat.unit_id==Unit.id,
                            )
            rowTable = DataTables(req, Pejabat, query, columns)
            return rowTable.output_result()

        elif url_dict['act']=='grid1':
            cari = 'cari' in params and params['cari'] or ''
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('pnama'))
            columns.append(ColumnDT('jnama'))
            columns.append(ColumnDT('unama'))
            query = DBSession.query(Pejabat.id,
                                    Pegawai.nama.label('pnama'),
                                    Jabatan.nama.label('jnama'),
                                    Unit.nama.label('unama'),
                            ).filter(Pejabat.pegawai_id==Pegawai.id,
                                     Pejabat.jabatan_id==Jabatan.id,
                                     Pejabat.unit_id==Unit.id,
                                     or_(Pegawai.nama.ilike('%%%s%%' % cari),
                                         Jabatan.nama.ilike('%%%s%%' % cari),
                                         Unit.nama.ilike('%%%s%%' % cari))
                                     
                            )
            rowTable = DataTables(req, Pejabat, query, columns)
            return rowTable.output_result()

            
        elif url_dict['act']=='headofnama':
            term = 'term' in params and params['term'] or '' 
            rows = DBSession.query(Pejabat.id, Pejabat.kode, Pejabat.nama
                      ).filter(
                      Pejabat.nama.ilike('%%%s%%' % term) ).all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[2]
                d['kode']        = k[1]
                d['nama']        = k[2]
                r.append(d)
            return r
            
        elif url_dict['act']=='headofkode':
            term = 'term' in params and params['term'] or '' 
            rows = DBSession.query(Pejabat.id, Pejabat.kode, Pejabat.nama
                      ).filter(
                      Pejabat.kode.ilike('%%%s%%' % term) ).all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[1]
                d['kode']        = k[1]
                d['nama']        = k[2]
                r.append(d)
            return r
   
        elif url_dict['act']=='headofkode1':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(Pejabat.id, Jabatan.kode, Pegawai.kode, Pegawai.nama
                      ).join(Pegawai,Jabatan).filter(Pejabat.unit_id == ses['unit_id'],
                           Jabatan.kode.ilike('23%'),
                           Pegawai.kode.ilike('%s%%' % term))   
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[1]
                d['kode']        = k[2]
                d['nama']        = k[3]
                r.append(d)    
            return r

        elif url_dict['act']=='headofnama1':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(Pejabat.id, Pegawai.kode, Pegawai.nama
                      ).join(Pegawai,Jabatan).filter(Pejabat.unit_id == ses['unit_id'],
                           Jabatan.kode.ilike('23%'),
                           Pegawai.nama.ilike('%%%s%%' % term))
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

        elif url_dict['act']=='headofkode2':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(Pejabat.id, Jabatan.kode, Pegawai.kode, Pegawai.nama,Jabatan.nama, 
                      ).join(Pegawai,Jabatan).filter(Pejabat.unit_id == ses['unit_id'],
                           Jabatan.kode.ilike('23%'),
                           Pegawai.kode.ilike('%s%%' % term))   
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[1]
                d['kode']        = k[1]
                d['nama']        = k[3]
                d['nip']         = k[2]
                d['jab']         = k[4]
                r.append(d)    
            return r

        elif url_dict['act']=='headofnip2':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(Pejabat.id, Jabatan.kode, Pegawai.kode, Pegawai.nama,Jabatan.nama,
                      ).join(Pegawai,Jabatan).filter(Pejabat.unit_id == ses['unit_id'],
                           Jabatan.kode.ilike('23%'),
                           Pegawai.nama.ilike('%s%%' % term))
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[2]
                d['kode']        = k[1]
                d['nama']        = k[3]
                d['nip']         = k[2]
                d['jab']         = k[4]
                r.append(d)    
            return r
            
        elif url_dict['act']=='headofnama2':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(Pejabat.id, Jabatan.kode, Pegawai.kode, Pegawai.nama,Jabatan.nama,
                      ).join(Pegawai,Jabatan).filter(Pejabat.unit_id == ses['unit_id'],
                           Jabatan.kode.ilike('23%'),
                           Pegawai.nama.ilike('%%%s%%' % term))
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[3]
                d['kode']        = k[1]
                d['nama']        = k[3]
                d['nip']         = k[2]
                d['jab']         = k[4]
                r.append(d)    
            return r

        elif url_dict['act']=='headofkode3':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(Pejabat.id, Jabatan.kode, Pegawai.kode, Pegawai.nama, 
                      ).join(Pegawai,Jabatan).filter(Pejabat.unit_id == ses['unit_id'],
                           Jabatan.kode.notlike('23%'),
                           Pegawai.kode.ilike('%s%%' % term))   
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[1]
                d['kode']        = k[1]
                d['nama']        = k[3]
                d['nip']         = k[2]
                r.append(d)    
            return r

        elif url_dict['act']=='headofnip3':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(Pejabat.id, Jabatan.kode, Pegawai.kode, Pegawai.nama
                      ).join(Pegawai,Jabatan).filter(Pejabat.unit_id == ses['unit_id'],
                           Jabatan.kode.notlike('23%'),
                           Pegawai.nama.ilike('%s%%' % term))
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[2]
                d['kode']        = k[1]
                d['nama']        = k[3]
                d['nip']         = k[2]
                r.append(d)    
            return r
            
        elif url_dict['act']=='headofnama3':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(Pejabat.id, Jabatan.kode, Pegawai.kode, Pegawai.nama
                      ).join(Pegawai,Jabatan).filter(Pejabat.unit_id == ses['unit_id'],
                           Jabatan.kode.notlike('23%'),
                           Pegawai.nama.ilike('%%%s%%' % term))
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[3]
                d['kode']        = k[1]
                d['nama']        = k[3]
                d['nip']         = k[2]
                r.append(d)    
            return r
            
        #Pejabat SPP

        elif url_dict['act']=='headofkode4':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(Pejabat.id, Jabatan.kode, Pegawai.kode, Pegawai.nama, Jabatan.nama,
                      ).join(Pegawai,Jabatan).filter(Pejabat.unit_id == ses['unit_id'],
                           Jabatan.kode.notlike('23%'),
                           Pegawai.kode.ilike('%s%%' % term))   
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[1]
                d['kode']        = k[1]
                d['nama']        = k[3]
                d['nip']         = k[2]
                d['jab']         = k[4]
                r.append(d)    
            return r

        elif url_dict['act']=='headofjab4':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(Pejabat.id, Jabatan.kode, Pegawai.kode, Pegawai.nama, Jabatan.nama,
                      ).join(Pegawai,Jabatan).filter(Pejabat.unit_id == ses['unit_id'],
                           Jabatan.kode.notlike('23%'),
                           Pegawai.nama.ilike('%s%%' % term))
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[4]
                d['kode']        = k[1]
                d['nama']        = k[3]
                d['nip']         = k[2]
                d['jab']         = k[4]
                r.append(d)    
            return r
            
        elif url_dict['act']=='headofnama4':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(Pejabat.id, Jabatan.kode, Pegawai.kode, Pegawai.nama, Jabatan.nama,
                      ).join(Pegawai,Jabatan).filter(Pejabat.unit_id == ses['unit_id'],
                           Jabatan.kode.notlike('23%'),
                           Pegawai.nama.ilike('%%%s%%' % term))
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[3]
                d['kode']        = k[1]
                d['nama']        = k[3]
                d['nip']         = k[2]
                d['jab']         = k[4]
                r.append(d)    
            return r

        elif url_dict['act']=='headofnip4':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(Pejabat.id, Jabatan.kode, Pegawai.kode, Pegawai.nama, Jabatan.nama,
                      ).join(Pegawai,Jabatan).filter(Pejabat.unit_id == ses['unit_id'],
                           Jabatan.kode.notlike('23%'),
                           Pegawai.nama.ilike('%%%s%%' % term))
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[2]
                d['kode']        = k[1]
                d['nama']        = k[3]
                d['nip']         = k[2]
                d['jab']         = k[4]
                r.append(d)    
            return r

        #Pejabat PPTK SPP

        elif url_dict['act']=='headofkode5':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(Pejabat.id, Jabatan.kode, Pegawai.kode, Pegawai.nama, 
                      ).join(Pegawai,Jabatan).filter(Pejabat.unit_id == ses['unit_id'],
                           Jabatan.kode.ilike('24%'),
                           Pegawai.kode.ilike('%s%%' % term))   
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[1]
                d['kode']        = k[1]
                d['nama']        = k[3]
                d['nip']         = k[2]
                r.append(d)    
            return r

        elif url_dict['act']=='headofnip5':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(Pejabat.id, Jabatan.kode, Pegawai.kode, Pegawai.nama
                      ).join(Pegawai,Jabatan).filter(Pejabat.unit_id == ses['unit_id'],
                           Jabatan.kode.ilike('24%'),
                           Pegawai.nama.ilike('%s%%' % term))
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[2]
                d['kode']        = k[1]
                d['nama']        = k[3]
                d['nip']         = k[2]
                r.append(d)    
            return r
            
        elif url_dict['act']=='headofnama5':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(Pejabat.id, Jabatan.kode, Pegawai.kode, Pegawai.nama
                      ).join(Pegawai,Jabatan).filter(Pejabat.unit_id == ses['unit_id'],
                           Jabatan.kode.ilike('24%'),
                           Pegawai.nama.ilike('%%%s%%' % term))
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[3]
                d['kode']        = k[1]
                d['nama']        = k[3]
                d['nip']         = k[2]
                r.append(d)    
            return r
            
        ## BUD SP2D
        elif url_dict['act']=='headofnama6':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(Pejabat.id, Jabatan.kode, Pegawai.kode, Pegawai.nama,Jabatan.nama,
                      ).join(Pegawai,Jabatan,Unit).filter(Pejabat.unit_id == Unit.id, Unit.kode=='1.20.09',
                           #Jabatan.kode.ilike('23%'),
                           Pegawai.nama.ilike('%%%s%%' % term))
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[3]
                d['kode']        = k[1]
                d['nama']        = k[3]
                d['nip']         = k[2]
                d['jab']         = k[4]
                r.append(d)    
            return r

        ## PA dan PPK SPM
        elif url_dict['act']=='headofnama7':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(Pejabat.id, Jabatan.kode, Pegawai.kode, Pegawai.nama,Jabatan.nama,
                      ).join(Pegawai,Jabatan).filter(Pejabat.unit_id == ses['unit_id'],
                           Jabatan.kode.notlike('23%'),
                           Pegawai.nama.ilike('%%%s%%' % term))
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[3]
                d['kode']        = k[1]
                d['nama']        = k[3]
                d['nip']         = k[2]
                d['jab']         = k[4]
                r.append(d)    
            return r

    #######    
    # Add #
    #######
    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(Pejabat).filter_by(id=uid)
            pejabat = q.first()
        else:
            pejabat = None
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind()
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
    def save(self, values, user, row=None):
        if not row:
            row = Pejabat()
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
        self.request.session.flash('pejabat sudah disimpan.')
    def route_list(self):
        return HTTPFound(location=self.request.route_url('pejabat'))
    def session_failed(self, session_name):
        r = dict(form=self.session[session_name])
        del self.session[session_name]
        return r
    @view_config(route_name='pejabat-add', renderer='templates/pejabat/add.pt',
                 permission='add')
    def view_add(self):
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
                    return HTTPFound(location=req.route_url('pejabat-add'))
                self.save_request(dict(controls))
            return self.route_list()
        elif SESS_ADD_FAILED in req.session:
            return self.session_failed(SESS_ADD_FAILED)
        return dict(form=form.render())
        
    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(Pejabat).filter_by(id=self.request.matchdict['id'])
    def id_not_found(self):    
        msg = 'pejabat ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()
    @view_config(route_name='pejabat-edit', renderer='templates/pejabat/edit.pt',
                 permission='edit')
    def view_edit(self):
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
                    return HTTPFound(location=request.route_url('pejabat-edit',
                                      id=row.id))
                self.save_request(dict(controls), row)
            return self.route_list()
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)
        values = row.to_dict()
        values['unit_nm'] = row.units.nama
        values['pegawai_nm'] = row.pegawais.nama
        values['jabatan_nm'] = row.jabatans.nama
        
        return dict(form=form.render(appstruct=values))
    ##########
    # Delete #
    ##########    
    @view_config(route_name='pejabat-delete', renderer='templates/pejabat/delete.pt',
                 permission='delete')
    def view_delete(self):
        request = self.request
        q = self.query_id()
        row = q.first()
        if not row:
            return self.id_not_found(request)
        form = Form(colander.Schema(), buttons=('hapus','batal'))
        if request.POST:
            if 'hapus' in request.POST:
                msg = 'Pejabat ID %d %s %s sudah dihapus.' % (row.id, row.pegawais.nama, row.jabatans.nama)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'Pejabat ID %d %s %s tidak dapat dihapus.' % (row.id, row.pegawais.nama, row.jabatans.nama)
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row,
                     form=form.render())