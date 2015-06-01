import os
import uuid
from osipkd.tools import row2dict, xls_reader
from datetime import datetime
from sqlalchemy import not_, func, cast, BigInteger, or_, join
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from osipkd.models import DBSession
from osipkd.models.apbd_anggaran import Program, Kegiatan, KegiatanSub, KegiatanItem
from osipkd.models.pemda_model import Urusan
from osipkd.models.apbd_tu import Spd, SpdItem
    
from datatables import ColumnDT, DataTables
from osipkd.views.base_view import BaseViews

SESS_ADD_FAILED = 'Tambah ag-kegiatan-sub gagal'
SESS_EDIT_FAILED = 'Edit ag-kegiatan-sub gagal'

def deferred_sdana(node, kw):
    values = kw.get('sdana', [])
    return widget.SelectWidget(values=values)
    
SDANA = (
    ('PAD', 'PAD'),
    ('DAU', 'DAU'),
    ('DAK', 'DAK'),
    ('APBD Provinsi', 'APBD Provinsi'),
    ('APBN', 'APBN'),
    ('LOAN', 'LOAN'),
    ('Bagi Hasil', 'Bagi Hasil'),
    )

class view_kegiatan_sub(BaseViews):

    @view_config(route_name="ag-bl", renderer="templates/ag-bl/list.pt")
    def view_list(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        #row = {}
        #row['rekening_kd'] = '0.00.00.21'
        #row['rekening_nm'] = 'BELANJA TIDAK LANGSUNG'
        #row['rekeninghead'] = 52
        return dict(project='EIS', #row = row
        )
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='ag-bl-act', renderer='json',
                 permission='read')
    def view_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        if url_dict['act']=='grid':
            pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if url_dict['act']=='grid':
                # defining columns
                columns = []
                columns.append(ColumnDT('id'))
                columns.append(ColumnDT('kode'))
                columns.append(ColumnDT('no_urut'))
                columns.append(ColumnDT('nama'))
                columns.append(ColumnDT('prg_nm'))
                columns.append(ColumnDT('rka'))
                columns.append(ColumnDT('dpa'))
                columns.append(ColumnDT('rpka'))
                columns.append(ColumnDT('dppa'))
                #columns.append(ColumnDT('pegawai_nama'))

                query = DBSession.query(KegiatanSub.id,
                          KegiatanSub.kode,
                          KegiatanSub.no_urut,
                        KegiatanSub.nama,
                        #PegawaiModel.nama.label('pegawai_nama'),
                        Program.nama.label('prg_nm'),
                    func.sum(KegiatanItem.vol_1_1*KegiatanItem.vol_1_2*
                             KegiatanItem.hsat_1).label('rka'),       
                    func.sum(KegiatanItem.vol_2_1*KegiatanItem.vol_2_2*
                             KegiatanItem.hsat_2).label('dpa'),                      
                    func.sum(KegiatanItem.vol_3_1*KegiatanItem.vol_3_2*
                             KegiatanItem.hsat_3).label('rpka'),                      
                    func.sum(KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*
                             KegiatanItem.hsat_4).label('dppa'))\
                    .join(Kegiatan)\
                    .join(Program)\
                    .join(Urusan)\
                    .outerjoin(KegiatanItem)\
                    .filter(
                            KegiatanSub.unit_id==self.unit_id,
                            KegiatanSub.tahun_id==self.tahun,
                            KegiatanSub.tahun_id==self.tahun,
                            #KegiatanSub.ttd1nip==PegawaiModel.kode,
                            Program.kode<>'0.00.00')\
                    .group_by(KegiatanSub.id,
                            KegiatanSub.no_urut,
                            KegiatanSub.nama,
                            Program.kode, Program.nama,
                            Kegiatan.kode, Urusan.kode, 
                            #PegawaiModel.kode, PegawaiModel.nama
                            )
                rowTable = DataTables(req, KegiatanSub, query, columns)
                # returns what is needed by DataTable
                #session.query(Table.column, func.count(Table.column)).group_by(Table.column).all()
                return rowTable.output_result()

        elif url_dict['act']=='reload':
            #if not kegiatan_kd:
            #    return {'success':False}
            query = DBSession.query(KegiatanSub).join(Kegiatan).join(Program).filter(
                       KegiatanSub.unit_id == ses['unit_id'],
                       KegiatanSub.tahun_id == ses['tahun'],
                       Program.kode<>'0.00.00'
                       ).first()
                       
            #if not query:
            #    return {'success':False, 'msg':'Data Kegiatan Tidak Ditemukan'}

            return {"success": True}
                
       
    @view_config(route_name='ag-kegiatan-sub-act', renderer='json',
                 permission='read')
    def view_act2(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        
        if url_dict['act']=='reload':
            kegiatan_kd = 'kegiatan_kd' in params and  params['kegiatan_kd'] or None
            if not kegiatan_kd:
                return {'success':False}
            query = DBSession.query(KegiatanSub).join(Kegiatan).filter(
                       KegiatanSub.unit_id == ses['unit_id'],
                       KegiatanSub.tahun_id == ses['tahun'],
                       Kegiatan.kode == kegiatan_kd
                       ).first()
                       
            if not query:
                return {'success':False, 'msg':'Data Sub Kegiatan Tidak Ditemukan'}
                       
            return {"success": True, 'kegiatan_sub_id': query.id, 'msg':''}
            
        elif url_dict['act']=='headofkode':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(KegiatanSub.id, Kegiatan.kode, KegiatanSub.no_urut,
                                KegiatanSub.nama
                      ).join(Kegiatan).filter(KegiatanSub.unit_id == ses['unit_id'],
                           KegiatanSub.tahun_id==ses['tahun'],
                           Kegiatan.kode.ilike('%%%s%%' % term))
                           
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = ''.join([k[1],'-',str(k[2])])
                d['kode']        = ''.join([k[1],'-',str(k[2])])
                d['nama']        = k[3]
                r.append(d)    
            return r
        elif url_dict['act']=='headofnama':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(KegiatanSub.id, Kegiatan.kode, KegiatanSub.no_urut,
                                KegiatanSub.nama).join(Kegiatan).filter(
                      KegiatanSub.unit_id == ses['unit_id'],
                      KegiatanSub.tahun_id==ses['tahun'],
                      Kegiatan.nama.ilike('%%%s%%' % term))
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[3]
                d['kode']        = ''.join([k[1],'-',str(k[2])])
                d['nama']        = k[3]
                r.append(d)    
            return r
            
        elif url_dict['act']=='headofkode1':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(KegiatanSub.id, Kegiatan.kode, KegiatanSub.no_urut,
                                KegiatanSub.nama
                        ).join(Kegiatan
                        ).filter(KegiatanSub.unit_id == ses['unit_id'],
                                 KegiatanSub.tahun_id==ses['tahun'],
                                 Kegiatan.kode!='0.00.00.10',
                                 Kegiatan.kode!='0.00.00.31',
                                 Kegiatan.kode!='0.00.00.32',
                                 Kegiatan.kode.ilike('%%%s%%' % term))
                           
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = ''.join([k[1],'-',str(k[2])])
                d['kode']        = k[1]
                d['nama']        = k[3]
                r.append(d)
            print '****----****',r                
            return r

        elif url_dict['act']=='headofnama1':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(KegiatanSub.id, Kegiatan.kode, KegiatanSub.no_urut,
                                KegiatanSub.nama
                        ).join(Kegiatan
                        ).filter(KegiatanSub.unit_id ==ses['unit_id'],
                                 KegiatanSub.tahun_id==ses['tahun'],
                                 Kegiatan.kode!='0.00.00.10',
                                 Kegiatan.kode!='0.00.00.31',
                                 Kegiatan.kode!='0.00.00.32',
                                 KegiatanSub.nama.ilike('%%%s%%' % term))
                           
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[3]
                d['kode']        = ''.join([k[1],'-',str(k[2])])
                d['nama']        = k[3]
                r.append(d)
            print '****----****',r                
            return r
            

        elif url_dict['act']=='headofkode2':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(KegiatanSub.id, Kegiatan.kode, KegiatanSub.no_urut,
                                KegiatanSub.nama
                      ).join(Kegiatan).filter(KegiatanSub.unit_id == ses['unit_id'],
                           KegiatanSub.tahun_id==ses['tahun'],
                           KegiatanSub.kegiatan_id==Kegiatan.id,
                           Kegiatan.kode.ilike('%%%s%%' % term))
                           
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[1]
                d['kode']        = k[1]
                d['nama']        = k[3]
                r.append(d)
            print '****----****',r                
            return r

        elif url_dict['act']=='headofnama2':
            term = 'term' in params and params['term'] or ''
            q = DBSession.query(KegiatanSub.id, Kegiatan.kode, KegiatanSub.no_urut,
                                KegiatanSub.nama).join(Kegiatan).filter(
                      KegiatanSub.unit_id == ses['unit_id'],
                      KegiatanSub.tahun_id==ses['tahun'],
                      Kegiatan.kode=='0.00.00.10', 
                      Kegiatan.nama.ilike('%%%s%%' % term))
            rows = q.all()
            r = []
            for k in rows:
                d={}
                d['id']          = k[0]
                d['value']       = k[3]
                d['kode']        = ''.join([k[1],'-',str(k[2])])
                d['nama']        = k[3]
                r.append(d)    
            return r

        elif url_dict['act']=='headofkode3':
            term         = 'term' in params and params['term'] or ''
            ap_spd_id    = 'ap_spd_id' in params and params['ap_spd_id'] or 0
            
            q = DBSession.query(KegiatanSub.id.label('kegiatan_sub_id'), Kegiatan.kode.label('kode'), KegiatanSub.nama.label('nama'),
                                func.sum(KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('anggaran'),
                                func.sum(KegiatanItem.bln01+KegiatanItem.bln02+KegiatanItem.bln03).label('trw1'),
                                func.sum(KegiatanItem.bln04+KegiatanItem.bln05+KegiatanItem.bln06).label('trw2'),
                                func.sum(KegiatanItem.bln07+KegiatanItem.bln08+KegiatanItem.bln09).label('trw3'),
                                func.sum(KegiatanItem.bln10+KegiatanItem.bln11+KegiatanItem.bln12).label('trw4')
                        ).join(Kegiatan).join(KegiatanItem
                        ).filter(KegiatanSub.unit_id == ses['unit_id'],
                               KegiatanSub.tahun_id==ses['tahun'],
                               Kegiatan.kode.ilike('%%%s%%' % term)
                        ).group_by(KegiatanSub.id, Kegiatan.kode, KegiatanSub.nama)
                    
            rows = q.all()

            r = []
            for k in rows:
                d={}
                d['id']       = k[0]
                d['kode']     = k[1]
                d['nama']     = k[2]
                d['anggaran'] = k[3]
                spds  = DBSession.query(Spd).filter(Spd.id==ap_spd_id).first()
                spd_tanggal = spds.tanggal
                rows2 =  DBSession.query(func.sum(SpdItem.nominal).label('lalu')
                            ).join(Spd
                            ).filter(SpdItem.kegiatan_sub_id==d['id'],
                            Spd.tanggal<=spd_tanggal).first()
                        
                d['lalu']     = rows2.lalu or 0
                        
                d['nominal'] = spds.triwulan_id==1 and k[4] or\
                               spds.triwulan_id==2 and k[5] or\
                               spds.triwulan_id==3 and k[6] or\
                               spds.triwulan_id==4 and k[7] 
                if d['nominal']==0:
                   d['nominal'] = d['anggaran'] // 4
            
                d['value']       = d['kode']
                d['kode']        = d['kode']
                d['nama']        = d['nama']
                d['anggaran']    = "%d" % d['anggaran']
                d['lalu']        = "%d" % d['lalu']
                d['nominal']     = "%d" % d['nominal']
                r.append(d)
            print '****----****',r                
            return r

        elif url_dict['act']=='headofnama3':
            term         = 'term' in params and params['term'] or ''
            ap_spd_id    = 'ap_spd_id' in params and params['ap_spd_id'] or 0
            
            q = DBSession.query(KegiatanSub.id.label('kegiatan_sub_id'), Kegiatan.kode.label('kode'), KegiatanSub.nama.label('nama'),
                                func.sum(KegiatanItem.vol_4_1*KegiatanItem.vol_4_2*KegiatanItem.hsat_4).label('anggaran'),
                                func.sum(KegiatanItem.bln01+KegiatanItem.bln02+KegiatanItem.bln03).label('trw1'),
                                func.sum(KegiatanItem.bln04+KegiatanItem.bln05+KegiatanItem.bln06).label('trw2'),
                                func.sum(KegiatanItem.bln07+KegiatanItem.bln08+KegiatanItem.bln09).label('trw3'),
                                func.sum(KegiatanItem.bln10+KegiatanItem.bln11+KegiatanItem.bln12).label('trw4')
                        ).join(Kegiatan).join(KegiatanItem
                        ).filter(KegiatanSub.unit_id == ses['unit_id'],
                               KegiatanSub.tahun_id==ses['tahun'],
                               KegiatanSub.nama.ilike('%%%s%%' % term)
                        ).group_by(KegiatanSub.id, Kegiatan.kode, KegiatanSub.nama)
                    
            rows = q.all()

            r = []
            for k in rows:
                d={}
                d['id']       = k[0]
                d['kode']     = k[1]
                d['nama']     = k[2]
                d['anggaran'] = k[3]
                spds  = DBSession.query(Spd).filter(Spd.id==ap_spd_id).first()
                spd_tanggal = spds.tanggal
                rows2 =  DBSession.query(func.sum(SpdItem.nominal).label('lalu')
                            ).join(Spd
                            ).filter(SpdItem.kegiatan_sub_id==d['id'],
                            Spd.tanggal<=spd_tanggal).first()
                        
                d['lalu']     = rows2.lalu or 0
                        
                d['nominal'] = spds.triwulan_id==1 and k[4] or\
                               spds.triwulan_id==2 and k[5] or\
                               spds.triwulan_id==3 and k[6] or\
                               spds.triwulan_id==4 and k[7] 
                if d['nominal']==0:
                   d['nominal'] = d['anggaran'] // 4
            
                d['value']       = d['nama']
                d['kode']        = d['kode']
                d['nama']        = d['nama']
                d['anggaran']    = "%d" % d['anggaran']
                d['lalu']        = "%d" % d['lalu']
                d['nominal']     = "%d" % d['nominal']
                r.append(d)
            print '****----****',r                
            return r
            
            
    ###############                    
    # Tambah  Data#
    ###############    
    @view_config(route_name='ag-kegiatan-sub-add-fast', renderer='json',
                 permission='add')
    def ak_kegiatan_sub_add_fast(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        kegiatan_kd = 'kegiatan_kd' in params and params['kegiatan_kd'] or None
        
        kegiatan = DBSession.query(Kegiatan).filter(Kegiatan.kode==kegiatan_kd).first()
        if not kegiatan:
            return {"success": False, 'msg':'Kegiatan tidak ditemukan'}
            
        row = KegiatanSub()
        row.kegiatan_id = kegiatan.id
        row.nama  = kegiatan.nama
        row.created = datetime.now()
        row.tahun_id = ses['tahun']
        row.unit_id = ses['unit_id']
        row.no_urut = 1
        try:
          DBSession.add(row)
          DBSession.flush()
          return {"success": True, 'id': row.id, "msg":'Success Tambah Kegiatan'}
        except:
            return {'success':False, 'msg':'Gagal Tambah Kegiatan'}
            
#######    
# Add #
#######
def form_validator(form, value):
    def err_kegiatan():
        raise colander.Invalid(form,
            'Kegiatan dengan no urut tersebut sudah ada')
                
class AddSchema(colander.Schema):
    kegiatan_widget = widget.AutocompleteInputWidget(
            size=60,
            values = '/kegiatan/act/headofkode',
            min_length=1)
    kegiatannm_widget = widget.AutocompleteInputWidget(
            size=60,
            values = '/kegiatan/act/headofnama',
            min_length=1)
            
    tahun_id         = colander.SchemaNode(
                          colander.String(),
                          oid = "tahun_id",
                          title="Tahun")
    unit_id          = colander.SchemaNode(
                          colander.String(),
                          oid = "unit_id")
    unit_kd          = colander.SchemaNode(
                          colander.String(),
                          title="SKPD",
                          oid = "unit_kd")
    unit_nm          = colander.SchemaNode(
                          colander.String(),
                          oid = "unit_nm")

                          
    kegiatan_id      = colander.SchemaNode(
                          colander.Integer(),
                          oid="kegiatan_id")
                          
    kode             = colander.SchemaNode(
                          colander.String(),
                          widget = kegiatan_widget,
                          oid="kode",
                          title="Kegiatan")
                          
    kegiatan_nm          = colander.SchemaNode(
                          colander.String(),
                          widget = kegiatannm_widget,
                          oid="kegiatan_nm",)

    no_urut          = colander.SchemaNode(
                          colander.Integer(),
                          missing=colander.drop)
                          
    nama             = colander.SchemaNode(
                          colander.String(),
                          title="Uraian",
                          oid = "nama")

    lokasi           = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop)
                          
    sifat            = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop)
    bagian           = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop)
    kondisi          = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop)
    waktu            = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title = 'Waktu Pelaks.')
    amt_lalu         = colander.SchemaNode(
                          colander.Integer(),
                          default = 0,
                          missing=colander.drop,
                          title = 'Anggaran Lalu')
    amt_yad          = colander.SchemaNode(
                          colander.Integer(),
                          default = 0,
                          missing=colander.drop,
                          title = 'Anggaran YAD')
    sdana            = colander.SchemaNode(
                          colander.String(),
                          widget=widget.SelectWidget(values=SDANA),
                          missing=colander.drop,
                          title = 'Sumber Dana')
    ttd1nip          = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="Pejabat 1")
    ttd2nip          = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="Pejabat 2")
    notes            = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="Catatan")
    target           = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,)
    sasaran          = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,)
    perubahan        = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="Alasan Perubahan")
    ppa              = colander.SchemaNode(
                          colander.Integer(),
                          default = 0,
                          missing=colander.drop,
                          title = 'PPA',)
    ppas             = colander.SchemaNode(
                          colander.Integer(),
                          default = 0,
                          missing=colander.drop,
                          title = 'PPAS',)
    ppa_rev          = colander.SchemaNode(
                          colander.Integer(),
                          default = 0,
                          missing=colander.drop,
                          title = 'Perubahan PPA',)
    ppas_rev         = colander.SchemaNode(
                          colander.Integer(),
                          default = 0,
                          missing=colander.drop,
                          title = 'Perubahan PPAS',)
    volume           = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,)
    tgl_bahas_1      = colander.SchemaNode(
                          colander.Date(),
                          missing=colander.drop,
                          title="Tanggal RKA")
    tgl_bahas_2      = colander.SchemaNode(
                          colander.Date(),
                          missing=colander.drop,
                          title="Tanggal DPA")
    tgl_bahas_3      = colander.SchemaNode(
                          colander.Date(),
                          missing=colander.drop,
                          title="Tanggal RPKA")
    tgl_bahas_4      = colander.SchemaNode(
                          colander.Date(),
                          missing=colander.drop,
                          title="Tanggal DPPA")
    catatan_1        = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="Catatan")
    catatan_2        = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="Catatan")
    catatan_3        = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="Catatan")
    catatan_4        = colander.SchemaNode(
                          colander.String(),
                          missing=colander.drop,
                          title="Catatan")
    pending          = colander.SchemaNode(
                          colander.Integer(),
                          default = 0,
                          missing=colander.drop,
                          )
    tahunke          = colander.SchemaNode(
                          colander.Integer(),
                          missing=colander.drop,
                          )
    h0yl             = colander.SchemaNode(
                          colander.Integer(),
                          default = 0,
                          missing=colander.drop,
                          title = "Anggaran 1"
                          )
    p0yl             = colander.SchemaNode(
                          colander.Integer(),
                          default = 0,
                          missing=colander.drop,
                          title = "Perubahan 1",)
    r0yl             = colander.SchemaNode(
                          colander.Integer(),
                          default = 0,
                          missing=colander.drop,
                          title = "Realisasi 1",)
    h1yl             = colander.SchemaNode(
                          colander.Integer(),
                          default = 0,
                          missing=colander.drop,
                          title = "Anggaran 1",)
    p1yl             = colander.SchemaNode(
                          colander.Integer(),
                          default = 0,
                          missing=colander.drop,
                          title = "Perubahan 2",)
    r1yl             = colander.SchemaNode(
                          colander.Integer(),
                          default = 0,
                          missing=colander.drop,
                          title = "Realisasi 2",)
    h2yl             = colander.SchemaNode(
                          colander.Integer(),
                          default = 0,
                          missing=colander.drop,
                          title = "Anggaran 3",)
    p2yl             = colander.SchemaNode(
                          colander.Integer(),
                          default = 0,
                          missing=colander.drop,
                          title = "Perubahan 3",)
    r2yl             = colander.SchemaNode(
                          colander.Integer(),
                          default = 0,
                          missing=colander.drop,
                          title = "Realisasi 3",)
    disabled         = colander.SchemaNode(
                          colander.Boolean(),
                          default = 0,
                          missing=colander.drop,)
                    
class EditSchema(AddSchema):
    id             = colander.SchemaNode(
                          colander.Integer(),)

def get_form(request, class_form):
    schema = class_form(validator=form_validator)
    schema = schema.bind(sdana=SDANA)
    schema.request = request
    return Form(schema, buttons=('simpan','batal'))
    
def save(values, row=None):
    if not row:
        row = KegiatanSub()
    row.from_dict(values)
    if not row.no_urut:
          row.no_urut = KegiatanSub.max_no_urut(row.tahun_id,row.unit_id,row.kegiatan_id)+1;
    DBSession.add(row)
    DBSession.flush()
    return row
                                      
def save_request(values, request, row=None):
    if 'id' in request.matchdict:
        values['id'] = request.matchdict['id']
    row = save(values, row)
    request.session.flash('Kegiatan sudah disimpan.')
        
def route_list(request):
    return HTTPFound(location=request.route_url('ag-bl'))
    
def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r
    
@view_config(route_name='ag-bl-add', renderer='templates/ag-bl/add.pt',
             permission='add')
def view_add(request):
    form = get_form(request, AddSchema)
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items()
            controls_dicted = dict(controls)
            #return dict(form=form.render(appstruct=controls_dicted))
            try:
                c = form.validate(controls)
            except ValidationFailure, e:
                return dict(form=form)
                #request.session[SESS_ADD_FAILED] = e.render()               
                #return HTTPFound(location=request.route_url('ag-bl-add'))
            save_request(controls_dicted, request)
        return route_list(request)
    elif SESS_ADD_FAILED in request.session:
        del request.session[SESS_ADD_FAILED]
        #return session_failed(request, SESS_ADD_FAILED)
    return dict(form=form)

########
# Edit #
########
def query_id(request):
    return DBSession.query(KegiatanSub).filter(KegiatanSub.id==request.matchdict['id'])
    
def id_not_found(request):    
    msg = 'User ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

@view_config(route_name='ag-bl-edit', renderer='templates/ag-bl/add.pt',
             permission='edit')
def view_edit(request):
    row = query_id(request).first()
    if not row:
        return id_not_found(request)
    form = get_form(request, EditSchema)
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items()
            
            try:
                c = form.validate(controls)
            except ValidationFailure, e:
                print e.render()
                return dict(form=form)
                #request.session[SESS_EDIT_FAILED] = e.render()               
                #return HTTPFound(location=request.route_url('ag-bl-edit',
                #                  id=row.id))
            save_request(dict(controls), request, row)
        return route_list(request)
    elif SESS_EDIT_FAILED in request.session:
        del request.session[SESS_EDIT_FAILED]
        return dict(form=form)
    values = row.to_dict() #dict(zip(row.keys(), row))
    values['kegiatan_nm']=row.kegiatans.nama
    form.set_appstruct(values) 
    return dict(form=form)

##########
# Delete #
##########    
@view_config(route_name='ag-bl-delete', renderer='templates/ag-bl/delete.pt',
             permission='delete')
def view_delete(request):
    q = query_id(request)
    row = q.first()
    if not row:
        return id_not_found(request)
    form = Form(colander.Schema(), buttons=('hapus','cancel'))
    values= {}
    if request.POST:
        if 'hapus' in request.POST:
            msg = '%s Kode %s  No. %s %s sudah dihapus.' % (request.title, row.kode, row.no_urut, row.nama)
            DBSession.query(KegiatanSub).filter(KegiatanSub.id==request.matchdict['id']).delete()
            DBSession.flush()
            request.session.flash(msg)
        return route_list(request)
    return dict(row=row,
                 form=form.render())

            
            