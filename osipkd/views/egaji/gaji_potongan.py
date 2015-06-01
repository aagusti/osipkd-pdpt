import os
import uuid
from osipkd.tools import row2dict, xls_reader
from datetime import datetime
from sqlalchemy import not_, func, text
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
from osipkd.models.gaji import GajiPotongan, GajiPegawai

from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews
from osipkd.models.pemda_model import (
    UserUnit, Unit)
    

SESS_ADD_FAILED = 'Tambah potongan gaji gagal'
SESS_EDIT_FAILED = 'Edit potongan gaji gagal'

class BankSchema(colander.Schema):
    mwidget = widget.TextInputWidget()
    amount_01 = colander.SchemaNode(
                    colander.Integer(),
                    widget = mwidget,
                    default = 0, 
                    missing=colander.drop, 
                    title='Bank',
                )                                
                
class BendaharaSchema(colander.Schema):
    mwidget = widget.TextInputWidget()
    amount_02 = colander.SchemaNode(
                    colander.Integer(),
                    widget = mwidget,
                    default = 0, 
                    missing=0, 
                    title='KPPK',                    
                )                                
    amount_03 = colander.SchemaNode(
                    colander.Integer(),
                    widget = mwidget,
                    default = 0, 
                    missing=0, 
                    title='PMI',                    
                )                                
    amount_04 = colander.SchemaNode(
                    colander.Integer(),
                    default = 0, 
                    widget = mwidget,
                    missing=0, 
                    title='KPRI',                    
                )                                
    amount_05 = colander.SchemaNode(
                    colander.Integer(),
                    widget = mwidget,
                    default = 0,
                    missing=0, 
                    title='KSP',                    
                )                                
    amount_06 = colander.SchemaNode(
                    colander.Integer(),
                    widget = mwidget,
                    default = 0,
                    missing=0, 
                    title='BPR',                    
                )                                

class BPSchema(colander.Schema):
    mwidget = widget.TextInputWidget()
    amount_07 = colander.SchemaNode(
                    colander.Integer(),
                    widget = mwidget,
                    default = 0,
                    missing=0, 
                    title='UPT 1',                    
                )                                
    amount_08 = colander.SchemaNode(
                    colander.Integer(),
                    widget = mwidget,
                    default = 0,
                    missing=0, 
                    title='UPT 2',                    
                )                                
    amount_09 = colander.SchemaNode(
                    colander.Integer(),
                    widget = mwidget,
                    default = 0, 
                    title = "PGRI",
                    missing=0,                     
                )                                
    amount_10 = colander.SchemaNode(
                    colander.Integer(),
                    widget = mwidget,
                    title = "K3S",
                    default = 0, 
                    missing=0,                     
                )                                
    amount_11 = colander.SchemaNode(
                    colander.Integer(),
                    widget = mwidget,
                    default = 0, 
                    title = "Koran",
                    missing=0,                     
                )                                
    amount_12 = colander.SchemaNode(
                    colander.Integer(),
                    widget = mwidget,
                    default = 0, 
                    missing=0, 
                    title='Umroh',                    
                )                                

                
class AddSchema(colander.Schema):
    nip_widget = widget.AutocompleteInputWidget(
            size=60,
            values = '/gaji/act/headofnip',
            min_length=1)

    id = colander.SchemaNode(colander.Integer(),
            widget=widget.HiddenWidget(readonly=True))
                    
    nip = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=18),
                    widget = nip_widget,
                    title = "NIP" )
                    
    nama = colander.SchemaNode(
                    colander.String(),
                    readonly=True)

    gaji_bersih = colander.SchemaNode(
                    colander.Integer(),
                    readonly=True)
                    
    bank = BankSchema()
    bendahara = BendaharaSchema()
    bp        = BPSchema(title="Bendahara Pengeluaran")    

class EditSchema(AddSchema):
    pass

def query_gaji_pegawai(tahun,bulan,nip):
    return DBSession.query(GajiPegawai).filter(
              GajiPegawai.tahun == tahun,
              GajiPegawai.bulan == bulan,
              GajiPegawai.jenis == 0,
              GajiPegawai.nip == nip).first()

def query_gaji_potongan(id):
    row = DBSession.query(GajiPotongan).filter(
              GajiPotongan.id == id
              ).first()
    if not row:
        row = GajiPotongan()
        row.id = id
        row.amount_01 = 0
        row.amount_02 = 0
        row.amount_03 = 0
        row.amount_04 = 0
        row.amount_05 = 0
        row.amount_06 = 0
        row.amount_07 = 0
        row.amount_08 = 0
        row.amount_09 = 0
        row.amount_10 = 0
        row.amount_11 = 0
        row.amount_12 = 0
        
    return row

def sum_of_potongan(potongan):
    n = 0
    for k in range(12):
        xfield=str(k+1).zfill(2)
        n += int(float(potongan['amount_%s' % xfield]))
    return n
    
def import_data(adata):
    for i in range(len(adata)):
        if i>0:
            j = adata[i]
            row = query_gaji_pegawai(j[0],j[1],j[2])
            id = row.id
            if row:
                potongan = query_gaji_potongan(id)
                potongan_dict = potongan.to_dict()
                if len(j)==10: #Pembantu Bendahara
                    for k in range(6):
                        xfield=str(k+7).zfill(2)
                        print xfield
                        potongan_dict['amount_%s' % xfield]= int(float(j[k+4]))
                        
                elif len(j)==9: #Bendahara
                    for k in range(5):
                        xfield=str(k+2).zfill(2)
                        potongan_dict['amount_%s' % xfield]= int(float(j[k+4]))

                elif len(j)==5 or len(j)==6: #Bank
                        potongan_dict['amount_01'] = int(float(j[4]))
            
            for k in range(11): 
                if (row.gaji_bersih-sum_of_potongan(potongan_dict))<15000:
                   xfield = str(12 - k).zfill(2)
                   potongan_dict['amount_%s' % xfield] = 0
            potongan.from_dict(potongan_dict)
            DBSession.add(potongan)
            DBSession.flush()
            
class view_gajipotongan(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='gaji-potongan', renderer='templates/gajipotongan/list.pt',
                 permission='read')
    def view_list(self):
        return dict(a={})
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='gaji-potongan-act', renderer='json',
                 permission='read')
    def gaji_potongan_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('nip'))
            columns.append(ColumnDT('nama'))
            columns.append(ColumnDT('gaji_bersih',  filter=self._number_format))
            columns.append(ColumnDT('amount_01',  filter=self._number_format))
            columns.append(ColumnDT('amount_02',  filter=self._number_format))
            columns.append(ColumnDT('amount_03',  filter=self._number_format))
            columns.append(ColumnDT('amount_04',  filter=self._number_format))
            columns.append(ColumnDT('amount_05',  filter=self._number_format))
            columns.append(ColumnDT('amount_06',  filter=self._number_format))
            columns.append(ColumnDT('amount_07',  filter=self._number_format))
            columns.append(ColumnDT('amount_08',  filter=self._number_format))
            columns.append(ColumnDT('amount_09',  filter=self._number_format))
            columns.append(ColumnDT('amount_10',  filter=self._number_format))
            columns.append(ColumnDT('amount_11',  filter=self._number_format))
            columns.append(ColumnDT('amount_12',  filter=self._number_format))
            query = DBSession.query(GajiPegawai.id, GajiPegawai.nip, GajiPegawai.nama, GajiPegawai.gaji_bersih,
                       GajiPotongan.amount_01, GajiPotongan.amount_02, GajiPotongan.amount_03,
                       GajiPotongan.amount_04, GajiPotongan.amount_05, GajiPotongan.amount_06,
                       GajiPotongan.amount_07, GajiPotongan.amount_08, GajiPotongan.amount_09,
                       GajiPotongan.amount_10, GajiPotongan.amount_11, GajiPotongan.amount_12,
                       ).join(GajiPotongan).filter(
                      GajiPegawai.tahun == ses['tahun'],
                      GajiPegawai.bulan == ses['bulan'],
                    )
            rows = UserUnit.get_filtered(self.request)
            if rows and rows.sub_unit:
                query = query.filter(GajiPegawai.unitkd.like( '%s%%' % self.request.session['unit_kd']))
            else:
                query = query.filter(GajiPegawai.unitkd== self.request.session['unit_kd'])
            rowTable = DataTables(req, GajiPegawai, query, columns)
            return rowTable.output_result()
        elif url_dict['act']=='upload':
            filename = self.request.POST['files'].filename
            input_file = self.request.POST['files'].file
            name, ext = os.path.splitext(filename)
            if ext not in ('.xls','.csv','.xlsx'):
                return dict(success=False, notes='File extension not allowed.')

            file_path = os.path.join('/tmp', '%s%s' % (uuid.uuid4(),ext))

            temp_file_path = file_path + '~'
            output_file = open(temp_file_path, 'wb')

            input_file.seek(0)
            while True:
                data = input_file.read(2<<16)
                if not data:
                    break
                output_file.write(data)

            output_file.close()
            os.rename(temp_file_path, file_path)
            if ext == '.xls':
                import_data(xls_reader(file_path))
                
                
            return dict(success=True, notes=file_path)

    #######    
    # Add #
    #######

    def form_validator(self, form, value):
        if 'id' in form.request.matchdict:
            uid = form.request.matchdict['id']
            q = DBSession.query(GajiPotongan).filter_by(id=uid)
            potongan = q.first()
        else:
            potongan = None
                
    def get_form(self, class_form, row=None):
        schema = class_form(validator=self.form_validator)
        schema = schema.bind()
        schema.request = self.request
        if row:
          schema.deserialize(row)
        return Form(schema, buttons=('simpan','batal'))
        
    def save(self, values, user, row=None):
        if not row:
            row = GajiPotongan()
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
        
        gaji = 'gaji_bersih' in values and int(float(values['gaji_bersih'])) or 0
        for k in range(12): 
            if (gaji-sum_of_potongan(values))<15000:
                   xfield = str(12 - k).zfill(2)
                   values['amount_%s' % xfield] = 0      
        
        row = self.save(values, self.request.user, row)
        self.request.session.flash('Potongan sudah disimpan.')
            
    def route_list(self):
        return HTTPFound(location=self.request.route_url('gaji-potongan'))
        
    def session_failed(self, session_name):
        r = dict(form=self.session[session_name])
        del self.session[session_name]
        return r
        
    @view_config(route_name='gaji-potongan-add', renderer='templates/gajipotongan/add.pt',
                 permission='add')
    def view_gaji_potongan_add(self):
        req = self.request
        ses = self.session
        form = self.get_form(AddSchema)
        if req.POST:
            if 'simpan' in req.POST:
                controls = req.POST.items()
                if 'id' in req.params and req.params['id']:
                    row = GajiPotongan.get_by_id(req.params['id'])
                    if row:
                        self.session.flash('Data Sudah Ada')
                        return dict(form=form)
                    
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form)
                    #req.session[SESS_ADD_FAILED] = e #.render()               
                    #return HTTPFound(location=req.route_url('gaji-potongan-add'))
                self.save_request(dict(controls))
            return self.route_list()
        elif SESS_ADD_FAILED in req.session:
            return self.session_failed(SESS_ADD_FAILED)
        return dict(form=form)

        
    ########
    # Edit #
    ########
    def query_id(self):
        return DBSession.query(GajiPotongan).filter_by(id=self.request.matchdict['id'])
        
    def id_not_found(self):    
        msg = 'Potongan ID %s Tidak Ditemukan.' % self.request.matchdict['id']
        request.session.flash(msg, 'error')
        return route_list()

    @view_config(route_name='gaji-potongan-edit', renderer='templates/gajipotongan/add.pt',
                 permission='edit')
    def view_gaji_potongan_edit(self):
        request = self.request
        row = self.query_id().first()
        if not row:
            return id_not_found(request)
        rowd={}
        rgp =DBSession.query(  GajiPegawai.nip,
                               GajiPegawai.nama,
                               GajiPegawai.gaji_bersih,
                             ).filter_by(id=self.request.matchdict['id']).first()
        rowd['id']          = row.id
        rowd['nip']         = rgp[0]
        rowd['nama']        = rgp[1]
        rowd['gaji_bersih'] = rgp[2]
        rowd['bank']        = {}
        rowd['bank']['amount_01'] = row.amount_01
        rowd['bendahara']    = {}
        rowd['bendahara']['amount_02'] = row.amount_02
        rowd['bendahara']['amount_03'] = row.amount_03
        rowd['bendahara']['amount_04'] = row.amount_04
        rowd['bendahara']['amount_05'] = row.amount_05
        rowd['bendahara']['amount_06'] = row.amount_06
        rowd['bp']    = {}
        rowd['bp']['amount_07'] = row.amount_07
        rowd['bp']['amount_08'] = row.amount_08
        rowd['bp']['amount_09'] = row.amount_09
        rowd['bp']['amount_10'] = row.amount_10
        rowd['bp']['amount_11'] = row.amount_11
        rowd['bp']['amount_12'] = row.amount_12
        """
        for k in row.keys():
            rowd.append((k,row[i]))
            i += 1
        """
        
        form = self.get_form(EditSchema)
        form.set_appstruct(rowd)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form)
                    #request.session[SESS_EDIT_FAILED] = e #.render()               
                    #return HTTPFound(location=request.route_url('gaji-potongan-edit',
                    #                  id=row.id))
                self.save_request(dict(controls), row)
            return self.route_list()
        elif SESS_EDIT_FAILED in request.session:
            return self.session_failed(SESS_EDIT_FAILED)
        return dict(form=form) #.render(appstruct=values))

    ##########
    # Delete #
    ##########    
    @view_config(route_name='gaji-potongan-delete', renderer='templates/gajipotongan/delete.pt',
                 permission='delete')
    def view_potongan_delete(self):
        request = self.request
        q = self.query_id()
        row = q.first()
        
        if not row:
            return self.id_not_found(request)
        form = Form(colander.Schema(), buttons=('hapus','batal'))
        if request.POST:
            if 'hapus' in request.POST:
                msg = 'Potongan ID %d %s sudah dihapus.' % (row.id, row.gajipegawais.nama)
                try:
                  q.delete()
                  DBSession.flush()
                except:
                  msg = 'Potongan ID %d %s tidak dapat dihapus.' % (row.id, row.gajipegawais.nama)
                request.session.flash(msg)
            return self.route_list()
        return dict(row=row,
                     form=form.render())

    ##########                    
    # CSV #
    ##########    
        
    @view_config(route_name='gaji-potongan-csv', renderer='csv',
                 permission='read')
    def gaji_potongan_csv(self):
        query = DBSession.query(GajiPegawai.id, GajiPegawai.nip, GajiPegawai.nama, GajiPegawai.gaji_bersih,
                   GajiPotongan.amount_01, GajiPotongan.amount_02, GajiPotongan.amount_03,
                   GajiPotongan.amount_04, GajiPotongan.amount_05, GajiPotongan.amount_06,
                   GajiPotongan.amount_07, GajiPotongan.amount_08, GajiPotongan.amount_09,
                   GajiPotongan.amount_10, GajiPotongan.amount_11, GajiPotongan.amount_12,
                   ).join(GajiPotongan).filter(
                  GajiPegawai.tahun == self.request.session['tahun'],
                  GajiPegawai.bulan == self.request.session['bulan'],
                )
        rows = UserUnit.get_filtered(self.request)
        if rows and rows.sub_unit:
            query = query.filter(GajiPegawai.unitkd.like( '%s%%' % self.request.session['unit_kd']))
        else:
            query = query.filter(GajiPegawai.unitkd== self.request.session['unit_kd'])

        r = query.first()
        header = r.keys()
        query = query.all()
        rows = []
        for item in query:
            rows.append(list(item))


        # override attributes of response
        filename = 'report.csv'
        self.request.response.content_disposition = 'attachment;filename=' + filename

        return {
          'header': header,
          'rows': rows,
        }
    