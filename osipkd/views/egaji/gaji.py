import os
import uuid
import urllib
from osipkd.tools import row2dict, xls_reader
from datetime import datetime
from sqlalchemy import not_, func, text
from sqlalchemy import create_engine
from sqlalchemy.exc import DBAPIError
from sqlalchemy.sql.expression import text
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
    
from osipkd.models.gaji import GajiPegawai
from osipkd.models.pemda_model import UserUnit, Unit
from osipkd.models.base_model import EngineMssql

from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews
    

gajiSelect = text("""SELECT * FROM pegawai_gaji 
              WHERE tahun=:tahun AND bulan=:bulan AND jenis=:jenis""")

sqlinsert = text("""INSERT INTO gaji_pegawai(
   tahun, bulan, jenis, urut, nip, unitkd, sub, nama, tgl_lahir, 
   tmp_lahir, jns_kelamin, bank, rekening, npwp, no_pegawai, nojjp, 
   alamat, namasi, sts_pegawaikd, tmt_pegawai, sts_kwn, sts_sipil, 
   agama, jml_si, jml_anak, golongankd, tmt_golongan, masakerja, 
   jbt_fungsikd, jbt_strukturkd, tmt_jabatan, tunj_jab_fungsi, tunj_jab_struktur, 
   gaji_pokok, tmt_gaji_pokok, tunj_istri, tunj_anak, tunj_beras, 
   gurukd, operator, tgl_ubah, tunj_kerja, tdtkd, pend_terakhir, 
   pend_jurusan, v_jab_struktur, pot_iwp, pot_taperum, pot_sewa_rumah, 
   pot_pangan, pot_korpri, pot_gaji_lebih, pot_hutang, pembulatan, 
   pph, tunj_umum, tunj_umum_tamb, tunj_otsus, tunj_dt, tunj_askes, 
   tunj_penghasilan, biaya_jabatan, biaya_pensiun, persen_gaji, 
   isttu, aktif_kd, ptkp, aktif_tgl, tgl_gaji, tmt_fungsi, penerima_udwudt, 
   tglbyr_udwudt) 
   VALUES (:tahun, :bulan, :jenis, :urut, :nip, :unitkd, :sub, :nama, :tgl_lahir, 
   :tmp_lahir, :jns_kelamin, :bank, :rekening, :npwp, :no_pegawai, :nojjp, 
   :alamat, :namasi, :sts_pegawaikd, :tmt_pegawai, :sts_kwn, :sts_sipil, 
   :agama, :jml_si, :jml_anak, :golongankd, :tmt_golongan, :masakerja, 
   :jbt_fungsikd, :jbt_strukturkd, :tmt_jabatan, :tunj_jab_fungsi, :tunj_jab_struktur, 
   :gaji_pokok, :tmt_gaji_pokok, :tunj_istri, :tunj_anak, :tunj_beras, 
   :gurukd, :operator, :tgl_ubah, :tunj_kerja, :tdtkd, :pend_terakhir, 
   :pend_jurusan, :v_jab_struktur, :pot_iwp, :pot_taperum, :pot_sewa_rumah, 
   :pot_pangan, :pot_korpri, :pot_gaji_lebih, :pot_hutang, :pembulatan, 
   :pph, :tunj_umum, :tunj_umum_tamb, :tunj_otsus, :tunj_dt, :tunj_askes, 
   :tunj_penghasilan, :biaya_jabatan, :biaya_pensiun, :persen_gaji, 
   :isttu, :aktif_kd, :ptkp, :aktif_tgl, :tgl_gaji, :tmt_fungsi, :penerima_udwudt, 
   :tglbyr_udwudt)""")

   
SESS_ADD_FAILED = 'Tambah gaji gagal'
SESS_EDIT_FAILED = 'Edit gaji gagal'
       

class AddSchema(colander.Schema):
    nip = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=18),
                    title = "NIP" )
                    
    nama = colander.SchemaNode(
                    colander.String(),
                    readonly=True)

    gaji_kotor = colander.SchemaNode(
                    colander.Integer(),
                    readonly=True)
    potongan = colander.SchemaNode(
                    colander.Integer(),
                    readonly=True)
    gaji_bersih = colander.SchemaNode(
                    colander.Integer(),
                    readonly=True)
                    

class EditSchema(AddSchema):
    pass

class view_gajipegawai(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='gaji-peg', renderer='templates/gajipegawai/list.pt',
                 permission='read')
    def view_gaji(self):
        return dict(a={})
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='gaji-peg-act', renderer='json',
                 permission='read')
    def gaji_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('nip'))
            columns.append(ColumnDT('nama'))
            columns.append(ColumnDT('gaji_kotor',  filter=self._number_format))
            columns.append(ColumnDT('potongan',  filter=self._number_format))
            columns.append(ColumnDT('gaji_bersih',  filter=self._number_format))
            query = DBSession.query(GajiPegawai).filter(
                      GajiPegawai.tahun == ses['tahun'],
                      GajiPegawai.bulan == ses['bulan']
                    )

            rows = UserUnit.get_filtered(self.request)
            if rows and rows.sub_unit:
                query = query.filter(GajiPegawai.unitkd.like( '%s%%' % ses['unit_kd']))
            else:
                query = query.filter(GajiPegawai.unitkd== ses['unit_kd'])

            rowTable = DataTables(req, GajiPegawai, query, columns)
            return rowTable.output_result()
            
        elif url_dict['act']=='headofnip':
            nip = 'term' in params and params['term'] or '' 
            rows = DBSession.query(GajiPegawai.id, GajiPegawai.nip, 
                      GajiPegawai.nama, GajiPegawai.gaji_bersih
                      ).filter(
                      GajiPegawai.tahun == ses['tahun'],
                      GajiPegawai.bulan == ses['bulan'],
                      GajiPegawai.unitkd == ses['unit_kd'],
                      GajiPegawai.nip.ilike('%s%%' % nip) ).all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[1]
                d['nip']         = k[1]
                d['nama']        = k[2]
                d['gaji_bersih'] = k[3]
                r.append(d)
            return r
        elif url_dict['act']=='import':
            self.d['msg'] ='Gagal Import Gagal'
            engine_mssql = create_engine('mssql+pyodbc:///?odbc_connect={0}'.format( 
                              urllib.quote_plus(EngineMssql[0])))

            sqlselect = text("""SELECT *
                FROM pegawai_gaji
                WHERE tahun=:tahun AND bulan=:bulan AND jenis=:jenis
                ORDER by nip""")
            srcs = engine_mssql.execute(sqlselect, tahun=self.session['tahun'], 
                      bulan=self.session['bulan'], jenis=0).all()
            for src in srcs.fetchall():
                gajiPg = GajiPegawai()
                gajiPg.from_dict(src)
                DBSession.add(gajiPg)
                DBSession.flush()
            DBSession.commit()                  
                              
            return self.d
            
    ##########                    
    # CSV #
    ##########    
        
    @view_config(route_name='gaji-peg-csv', renderer='csv',
                 permission='read')
    def gaji_csv(self):
      q = DBSession.query(GajiPegawai.tahun,GajiPegawai.bulan, 
                    GajiPegawai.nip, GajiPegawai.nama, GajiPegawai.gaji_kotor,
                    GajiPegawai.potongan, GajiPegawai.gaji_bersih)
      rows = UserUnit.get_filtered(self.request)
      if rows and rows.sub_unit:
          q = q.filter(GajiPegawai.unitkd.like( '%s%%' % self.request.session['unit_kd']))
      else:
          q = q.filter(GajiPegawai.unitkd== self.request.session['unit_kd'])
         
      r = q.first()
      header = r.keys()
      query = q.all()
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
    